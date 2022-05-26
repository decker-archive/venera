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
import os

import dotenv
import orjson
import redis.asyncio as redis

dotenv.load_dotenv()

pool = redis.ConnectionPool(
    host=os.getenv('redis_uri'),
    port=os.getenv('redis_port'),
    password=os.getenv('redis_password'),
    db=int(os.getenv('redis_db', 0)),
    retry_on_timeout=True,
)

manager = redis.Redis(connection_pool=pool)

# Possible Types
# 1: User(s)
# 2: Guild(s)
# 3: Channel(s)
# 4: ???
# 5: ???
# 6: Member(s)
# 7: Presence


async def user_event(name: str, user_id: int, data: dict):
    d = {'name': name, 'user_id': user_id, 'data': {'d': data}}

    await manager.publish('gateway', orjson.dumps(d))


async def guild_event(name: str, guild_id: int, data: dict, user_id: int = None):
    d = {
        'name': name,
        'guild_id': guild_id,
        'user_id': user_id,
        'data': {'d': data},
    }

    await manager.publish('gateway', orjson.dumps(d))


async def channel_event(
    name: str,
    channel: dict,
    data: dict,
    guild_id: int = None,
    is_message: bool = False,
):
    d = {
        'name': name,
        'channel': channel,
        'guild_id': guild_id,
        'data': {'d': data},
        'is_message': is_message,
    }

    await manager.publish('gateway', orjson.dumps(d))


async def member_event(name: str, member_id: int, guild_id: int, data: dict):
    d = {
        'name': name,
        'member_id': member_id,
        'guild_id': guild_id,
        'data': {'d': data},
    }

    await manager.publish('gateway', orjson.dumps(d))


async def presence_event(name: str, user_id: int, data: dict):
    d = {'name': name, 'user_id': user_id, 'data': {'d': data}}

    await manager.publish('gateway', orjson.dumps(d))
