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
from blacksheep.server.controllers import Controller, get, post

from ..checks import audit, get_member_permissions, validate_member
from ..database import Audit, to_dict
from ..errors import Forbidden, NotFound
from ..utils import AuthHeader, jsonify


class Audits(Controller):
    @get('/guilds/{int:guild_id}/audits')
    async def get_guild_audits(self, guild_id: int, auth: AuthHeader):
        member, _ = validate_member(token=auth.value, guild_id=guild_id)
        perms = get_member_permissions(member)

        if not perms.view_audit_log and not member.owner:
            raise Forbidden()

        audits_ = Audit.objects(Audit.guild_id == guild_id).all()

        audits = []

        for audit in audits_:
            audits.append(to_dict(audit))

        return jsonify(audits)

    @get('/guilds/{int:guild_id}/audits/{int:audit_id}')
    async def get_guild_audit(self, guild_id: int, audit_id: int, auth: AuthHeader):
        member, _ = validate_member(token=auth.value, guild_id=guild_id)
        perms = get_member_permissions(member)

        if not perms.view_audit_log and not member.owner:
            raise Forbidden()

        try:
            audit = Audit.objects(
                Audit.guild_id == guild_id, Audit.audit_id == audit_id
            ).get()
        except:
            raise NotFound()

        return jsonify(to_dict(audit))

    @post('/guilds/{int:guild_id}/audits')
    async def create_audit(self, guild_id: int, auth: AuthHeader, request: Request):
        me, _ = validate_member(token=auth.value, guild_id=guild_id)
        perms = get_member_permissions(me)

        if not perms.create_audits and not me.owner:
            raise Forbidden()

        data = await request.json(orjson.loads)

        ret = audit(
            str(data['type']),
            guild_id=guild_id,
            postmortem=str(data['postmortem']),
            audited=int(data.get('audited') or 0),
            object_id=int(data.get('object_id') or 0),
            user_id=me.id,
        )

        return jsonify(to_dict(ret), 201)
