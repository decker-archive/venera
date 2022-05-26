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
import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, get, patch, put
from cassandra.cqlengine import query

from ..checks import (
    channels_valid,
    guilds_valid,
    validate_member,
    validate_meta_guilds,
    validate_user,
)
from ..database import GuildMeta
from ..database import Meta as db
from ..database import Note, User, to_dict
from ..errors import BadData
from ..utils import VALID_THEMES, AuthHeader, jsonify


class Meta(Controller):
    @get('/users/@me/meta')
    async def get_meta(self, auth: AuthHeader):
        me = validate_user(token=auth.value, stop_bots=True)

        meta = db.objects(
            db.user_id == me.id,
        ).get()

        return jsonify(to_dict(meta))

    @patch('/users/@me/meta')
    async def edit_meta(self, auth: AuthHeader, request: Request):
        me = validate_user(token=auth.value, stop_bots=True)

        meta: db = db.objects(db.user_id == me.id).get()

        data = await request.json(orjson.loads)

        if 'theme' in data:
            theme = str(data.pop('theme'))
            if theme not in VALID_THEMES:
                raise BadData()
            meta.theme = theme

        if 'guild_placements' in data:
            guild_placements = list(data.pop('guild_placements'))
            validate_meta_guilds(guild_ids=guild_placements, user_id=me.id)
            meta.guild_placements = guild_placements

        if 'direct_message_ignored_guilds' in data:
            dm_ignored_guilds = list(data.pop('direct_message_ignored_guilds'))
            guilds_valid(dm_ignored_guilds)

            meta.direct_message_ignored_guilds = dm_ignored_guilds

        meta = meta.save()

        return jsonify(to_dict(meta))

    @get('/users/@me/guilds/{int:guild_id}/meta')
    async def get_guild_meta(self, guild_id: int, auth: AuthHeader):
        _, me = validate_member(token=auth.value, guild_id=guild_id, stop_bots=True)

        meta = GuildMeta.objects(
            GuildMeta.user_id == me.id, GuildMeta.guild_id == guild_id
        ).get()

        return jsonify(to_dict(meta))

    @patch('/users/@me/guilds/{int:guild_id}/meta')
    async def edit_guild_meta(self, guild_id: int, auth: AuthHeader, request: Request):
        _, me = validate_member(token=auth.value, guild_id=guild_id, stop_bots=True)

        meta: GuildMeta = GuildMeta.objects(
            GuildMeta.user_id == me.id, GuildMeta.guild_id == guild_id
        ).get()

        data: dict = await request.json(orjson.loads)

        if 'muted_channels' in data:
            muted_channels = list(data.pop('muted_channels'))
            channels_valid(muted_channels, guild_id=guild_id)
            meta.muted_channels = set(muted_channels)

        meta = meta.save()

        return jsonify(to_dict(meta))

    @put('/users/@me/notes/{int:user_id}')
    async def create_note(self, user_id: int, auth: AuthHeader, request: Request):
        me = validate_user(token=auth.value, stop_bots=True)

        User.objects(User.id == user_id).get()

        data = await request.json(orjson.loads)

        content = str(data['content'])[:900]

        try:
            note: Note = Note.objects(
                Note.creator_id == me.id,
                Note.user_id == user_id,
            ).get()
            note.content = content
            note = note.save()
        except (query.DoesNotExist):
            note = Note.create(
                creator_id=me.id,
                user_id=user_id,
                content=content,
            )

        return jsonify(to_dict(note))

    @get('/users/@me/notes/{int:user_id}')
    async def get_note(self, user_id: int, auth: AuthHeader):
        me = validate_user(token=auth.value, stop_bots=True)

        try:
            note = Note.objects(Note.creator_id == me.id, Note.user_id == user_id).get()
        except (query.DoesNotExist):
            return jsonify('', 404)

        return jsonify(to_dict(note))
