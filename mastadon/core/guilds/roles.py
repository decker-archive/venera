# The contents of this file are subject to the Common Public Attribution
# License Version 1.0. (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://code.mastadonapp.com/LICENSE. The License is based on the Mozilla Public
# License Version 1.1, but Sections 14 and 15 have been added to cover use of
# software over a computer network and provide for limited attribution for the
# Original Developer. In addition, Exhibit A has been modified to be consistent
# with Exhibit B.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for
# the specific language governing rights and limitations under the License.
#
# The Original Code is mastadon.
#
# the Original Developer is the Initial Developer. The Initial Developer of 
# the Original Code is mastadon Inc.
# 
# All portions of the code written by mastadon are Copyright (c) 2022 mastadon
# Inc. All Rights Reserved.
import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, get, patch, post

from ..checks import validate_member
from ..database import Role, to_dict
from ..errors import NotFound
from ..randoms import factory
from ..utils import AuthHeader, jsonify


class Roles(Controller):
    # @post('/guilds/{int:guild_id}/roles')
    async def create_role(self, guild_id: int, auth: AuthHeader, request: Request):
        validate_member(token=auth.value, guild_id=guild_id)

        imp = {}
        imp['id'] = factory().formulate()
        imp['guild_id'] = guild_id

        data = await request.json(orjson.loads)

        if 'name' in data:
            imp['name'] = str(data['name'])

        Role.create()

        return jsonify('')

    @patch('/guilds/{int:guild_id}/roles/{int:role_id}')
    async def edit_role(self, guild_id: int, role_id: int, auth: AuthHeader):
        return jsonify('')

    @get('/guilds/{int:guild_id}/roles/{int:role_id}')
    async def get_role(self, guild_id: int, role_id: int, auth: AuthHeader):
        validate_member(token=auth.value, guild_id=guild_id)

        try:
            roles = Role.objects(Role.guild_id == guild_id, Role.id == role_id).get()
        except:
            raise NotFound()

        return jsonify(to_dict(roles))

    @get('/guilds/{int:guild_id}/roles')
    async def get_roles(self, guild_id: int, auth: AuthHeader):
        validate_member(token=auth.value, guild_id=guild_id)

        _rs = Role.objects(Role.guild_id == guild_id).all()
        roles = []

        for role in _rs:
            roles.append(to_dict(role))

        return jsonify(roles)
