# The contents of this file are subject to the Common Public Attribution
# License Version 1.0. (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://code.veneralab.com/LICENSE. The License is based on the Mozilla Public
# License Version 1.1, but Sections 14 and 15 have been added to cover use of
# software over a computer network and provide for limited attribution for the
# Original Developer. In addition, Exhibit A has been modified to be consistent
# with Exhibit B.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for
# the specific language governing rights and limitations under the License.
#
# The Original Code is venera.
#
# the Original Developer is the Initial Developer. The Initial Developer of 
# the Original Code is Venera.
# 
# All portions of the code written by Venera are Copyright (c) 2022 Venera.
# All Rights Reserved.
import random

import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, get, patch, post
from cassandra.cqlengine import query
from email_validator import validate_email

from ..checks import send_verification, upload_image, validate_user, verify_email
from ..database import Guild, Member, Meta, User, to_dict
from ..errors import BadData, Conflict, Forbidden, NotFound
from ..randoms import factory, get_hash, verify_hash
from ..tokens import create_token
from ..utils import VALID_LOCALES, AuthHeader, jsonify


class Users(Controller):
    @get('/users/@me')
    async def get_me(self, auth: AuthHeader):
        me = validate_user(auth.value)

        if me.locale == 'EN_US' or me.locale == 'en_US':
            me.locale = 'en-US'
            me = me.save()

        elif me.locale == 'en_UK':
            me.locale = 'en-GB'
            me = me.save()

        me = to_dict(me, True)

        return jsonify(me)

    @get('/users/{int:user_id}')
    async def get_user(self, user_id: int, auth: AuthHeader):
        validate_user(auth.value)

        try:
            user: User = User.objects(User.id == user_id).get()
        except query.DoesNotExist:
            raise NotFound()

        if user.locale == 'EN_US' or user.locale == 'en_US':
            user.locale = 'en-US'
            user = user.save()

        elif user.locale == 'en_UK':
            user.locale = 'en-GB'
            user = user.save()

        ret = to_dict(user)

        if user.bot:
            ret['pronouns'] = 'Attack Helicopter/AttkHeli'

        return jsonify(ret)

    @post('/users')
    async def register_user(self, request: Request):
        data: dict = await request.json(orjson.loads)

        username = data['username'][:40]
        discrim = random.randint(1000, 9999)
        email = validate_email(
            verify_email(str(data['email'])), check_deliverability=True
        ).email
        password = await get_hash(str(data.pop('password')))
        flags = 1 << 0
        bio = str(data.get('bio') or '')
        locale = str(data.get('locale') or 'en-US')
        pronouns = str(data.get('pronouns') or '')
        pfp_id = ''
        banner_id = ''
        verification_code = random.randint(10000, 90000)

        if locale not in VALID_LOCALES:
            raise BadData()

        if data.get('avatar'):
            pfp_id = upload_image(str(data['avatar']), 'users')

        if data.get('banner'):
            banner_id = upload_image(str(data['banner']), 'users')

        user_id = factory().formulate()

        user: User = User.create(
            id=user_id,
            username=username,
            discriminator=discrim,
            email=email[:100],
            password=password,
            flags=flags,
            bio=bio[:4000],
            locale=locale,
            pronouns=pronouns,
            avatar=pfp_id,
            banner=banner_id,
            verification_code=verification_code,
        )
        Meta.create(user_id=user_id)

        resp = to_dict(user, True)
        resp['token'] = create_token(user_id=user.id, user_password=user.password)

        send_verification(email=email, username=username, code=verification_code)

        return jsonify(resp, 201)

    @patch('/users/@me')
    async def edit_me(self, auth: AuthHeader, request: Request):
        me = validate_user(auth.value, stop_bots=True)

        data: dict = await request.json(orjson.loads)
        SEND_NEW_CODE = False

        if data.get('username'):
            me.username = str(data['username'])

        if data.get('pronouns'):
            me.pronouns = str(data['pronouns'])

        if data.get('email'):
            me.email = validate_email(
                verify_email(str(data['email'])), check_deliverability=True
            ).email
            me.verified = False
            me.verification_code = random.randint(10000, 90000)
            SEND_NEW_CODE = True

        if data.get('password'):
            me.password = await get_hash(str(data['password']))

        if data.get('discriminator'):
            d = int(str(data['discriminator'])[:4])
            if len(str(d)) != 4:
                raise BadData()
            me.discriminator = d

        if data.get('avatar'):
            me.avatar = (
                upload_image(str(data['avatar']), 'users')
                if data['avatar'] != ''
                else ''
            )

        if data.get('banner'):
            me.banner = (
                upload_image(str(data['banner']), 'users')
                if data['banner'] != ''
                else ''
            )

        me = me.save()

        ret = to_dict(me, True)

        if SEND_NEW_CODE:
            send_verification(
                email=me.email, username=me.username, code=me.verification_code
            )

        return jsonify(ret)

    @get('/users/@me/tokens')
    async def make_token(self, request: Request):
        data = await request.json(orjson.loads)
        email, password = data['email'], data['password']

        me = User.objects(User.email == str(email)).allow_filtering().get()

        ok = await verify_hash(me.password, str(password))

        if not ok:
            raise Forbidden()

        token = create_token(me.id, me.password)

        return jsonify([token], 201)

    @post('/users/@me/verify')
    async def verify(self, auth: AuthHeader, request: Request):
        me = validate_user(token=auth.value, stop_bots=True)

        if me.verified:
            raise Conflict()

        code = int(request.query.get('utm_verification')[0])

        if code != me.verification_code:
            raise BadData()

        me.verified = True
        me = me.save()

        return jsonify(to_dict(me))

    @get('/users/@me/guilds')
    async def get_guilds(self, auth: AuthHeader):
        me = validate_user(token=auth.value, stop_bots=True)

        objs = Member.objects(Member.id == me.id).all()
        guilds = []

        for obj in objs:
            guilds.append(to_dict(Guild.objects(Guild.id == obj.guild_id).get()))

        return jsonify(guilds)
