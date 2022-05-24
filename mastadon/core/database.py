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
import datetime
import os
from typing import Any

import dotenv
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import columns, connection, management, models, usertype

dotenv.load_dotenv()

cloud = {'secure_connect_bundle': os.getcwd() + r'/mastadon/core/static/bundle.zip'}
auth_provider = PlainTextAuthProvider(
    os.getenv('client_id'), os.getenv('client_secret')
)


def connect():
    try:
        if os.getenv('safe', 'false') == 'true':
            connection.setup(
                None,
                'airbus',
                cloud=cloud,
                auth_provider=auth_provider,
                connect_timeout=100,
                retry_connect=True,
            )
        else:
            connection.setup(
                None,
                'airbus',
                connect_timeout=100,
                retry_connect=True,
                compression=False,
            )
    except:
        connect()


default_options = {
    # NOTE: Only let tombstones live for a day
    'gc_grace_seconds': 86400,
}

default_permissions = (
    1 << 0
    | 1 << 6
    | 1 << 10
    | 1 << 11
    | 1 << 12
    | 1 << 14
    | 1 << 15
    | 1 << 16
    | 1 << 18
    | 1 << 25
)

# this makes giving the current date just easier, as cassandra-driver accepts non-async functions
def _get_date():
    return datetime.datetime.now(datetime.timezone.utc)


class User(models.Model):
    __table_name__ = 'users'
    __options__ = default_options
    id = columns.BigInt(primary_key=True, partition_key=False)
    username = columns.Text(max_length=40)
    discriminator = columns.Integer(index=True)
    email = columns.Text(max_length=100)
    password = columns.Text()
    flags = columns.Integer()
    avatar = columns.Text(default='')
    banner = columns.Text(default='')
    locale = columns.Text(default='en-US')
    joined_at = columns.DateTime(default=_get_date)
    bio = columns.Text(max_length=4000)
    verified = columns.Boolean(default=False)
    system = columns.Boolean(default=False)
    bot = columns.Boolean(default=False)
    pronouns = columns.Text(default='')
    verification_code = columns.Integer()


# NOTE: Guilds
class Role(models.Model):
    __table_name__ = 'roles'
    __options__ = default_options
    id = columns.BigInt(primary_key=True, partition_key=False)
    guild_id = columns.BigInt(primary_key=True, partition_key=True)
    name = columns.Text(max_length=100)
    color = columns.Integer(default=0000)
    hoist = columns.Boolean(default=False)
    icon = columns.Text()
    position = columns.Integer()
    permissions = columns.BigInt(default=0)
    mentionable = columns.Boolean(default=False)


class Guild(models.Model):
    __table_name__ = 'guilds'
    __options__ = default_options
    id = columns.BigInt(primary_key=True, partition_key=True)
    name = columns.Text(max_length=40)
    description = columns.Text(max_length=4000)
    vanity_url = columns.Text(default='')
    icon = columns.Text(default='')
    banner = columns.Text(default='')
    owner_id = columns.BigInt(primary_key=True)
    nsfw = columns.Boolean(default=False)
    large = columns.Boolean(primary_key=True, default=False)
    perferred_locale = columns.Text(default='en-US')
    permissions = columns.BigInt(default=default_permissions)
    splash = columns.Text(default='')
    features = columns.Set(columns.Text)
    verified = columns.Boolean(default=False)


class GuildInvite(models.Model):
    __table_name__ = 'guild_invites'
    __options__ = default_options
    id = columns.Text(primary_key=True, partition_key=True)
    guild_id = columns.BigInt(primary_key=True)
    creator_id = columns.BigInt(primary_key=True)
    created_at = columns.DateTime(default=_get_date)
    channel_id = columns.BigInt(default=0)


class Member(models.Model):
    __table_name__ = 'members'
    __options__ = default_options
    id = columns.BigInt(primary_key=True, partition_key=True)
    guild_id = columns.BigInt(primary_key=True)
    avatar = columns.Text(default='')
    banner = columns.Text(default='')
    joined_at = columns.DateTime(default=_get_date)
    roles = columns.Set(columns.BigInt)
    nick = columns.Text(default='')
    owner = columns.Boolean(default=False)


## NOTE: Channels/Messages, etc


class PermissionOverWrites(models.Model):
    __table_name__ = 'permission_overwrites'
    __options__ = default_options
    channel_id = columns.BigInt(primary_key=True)
    user_id = columns.BigInt()
    type = columns.Integer(default=0)
    allow = columns.BigInt()
    deny = columns.BigInt()


class GuildChannel(models.Model):
    __table_name__ = 'guild_channels'
    __options__ = default_options
    id = columns.BigInt(primary_key=True, partition_key=False)
    guild_id = columns.BigInt(primary_key=True, partition_key=True)
    type = columns.Integer(default=0)
    position = columns.Integer()
    name = columns.Text(max_length=45)
    topic = columns.Text(max_length=1024, default='')
    slowmode_timeout = columns.Integer(default=0)
    parent_id = columns.BigInt()


class ChannelSlowMode(models.Model):
    __table_name__ = 'channel_slowmode'
    __options__ = default_options
    id = columns.BigInt(primary_key=True, partition_key=True)
    channel_id = columns.BigInt(primary_key=True, partition_key=True)


class GuildChannelPin(models.Model):
    __table_name__ = 'guild_channel_pins'
    __options__ = default_options
    channel_id = columns.BigInt(primary_key=True, partition_key=True)
    message_id = columns.BigInt()


class Reaction(models.Model):
    __table_name__ = 'reactions'
    __options__ = default_options
    message_id = columns.BigInt(primary_key=True)
    user_id = columns.BigInt()
    emoji_id = columns.BigInt()


class Emoji(models.Model):
    __table_name__ = 'emojis'
    __options__ = default_options
    id = columns.BigInt(primary_key=True, partition_key=False)
    guild_id = columns.BigInt(primary_key=True, partition_key=True)
    asset = columns.Text()


# TODO: Embeds
class Message(models.Model):
    __table_name__ = 'messages'
    __options__ = default_options
    channel_id = columns.BigInt(primary_key=True, partition_key=True)
    bucket_id = columns.Integer(primary_key=True, partition_key=True)
    message_id = columns.BigInt(
        primary_key=True, partition_key=False, clustering_order='DESC'
    )
    guild_id = columns.BigInt()
    author_id = columns.BigInt()
    content = columns.Text(max_length=5000)
    created_at = columns.DateTime(default=_get_date)
    last_edited = columns.DateTime(default=_get_date)
    tts = columns.Boolean(default=False)
    mentions_everyone = columns.Boolean(default=False)
    mentioned_users = columns.Set(columns.BigInt)
    pinned = columns.Boolean(default=False)
    referenced_message_id = columns.BigInt()


class ReadState(models.Model):
    __table_name__ = 'readstates'
    id = columns.BigInt(primary_key=True, partition_key=True)
    channel_id = columns.BigInt(primary_key=True, partition_key=False)
    last_message_id = columns.BigInt()


class Meta(models.Model):
    __table_name__ = 'meta'
    __options__ = default_options
    user_id = columns.BigInt(primary_key=True)
    theme = columns.Text(default='dark')
    guild_placements = columns.List(columns.BigInt)
    direct_message_ignored_guilds = columns.Set(columns.BigInt)
    developer_mode = columns.Boolean(default=False)


class GuildMeta(models.Model):
    __table_name__ = 'guild_meta'
    __options__ = default_options
    user_id = columns.BigInt(primary_key=True, partition_key=True)
    guild_id = columns.BigInt(primary_key=True, partition_key=True)
    muted_channels = columns.Set(columns.BigInt)


class Note(models.Model):
    __table_name__ = 'notes'
    __options__ = default_options
    creator_id = columns.BigInt(primary_key=True, partition_key=True)
    user_id = columns.BigInt(primary_key=True)
    content = columns.Text(max_length=900, default='')


class Audit(models.Model):
    __table_name__ = 'audits'
    # let audits live for 4 months.
    __options__ = {'default_time_to_live': 10520000}
    # the guild this audit happened at.
    guild_id = columns.BigInt(primary_key=True, partition_key=True)
    # the user audited.
    audited = columns.BigInt(primary_key=True)
    # bot which audited this event, 0 means it was audited by the system.
    auditor = columns.BigInt(default=0)
    # the type of the audit.
    type = columns.Text()
    # the object id effected, i.e. message ids
    object_id = columns.BigInt(default=0)
    # the bot or systems postmortem.
    # this is set to 6000 mostly since I can't add a data field
    # so bots have to use the reason field instead, this should be large or
    # extendible on the client and should support markdown.
    postmortem = columns.Text(max_length=6000)
    # the snowflake id of this audit.
    audit_id = columns.BigInt()
    # when this was audited
    audited_at = columns.DateTime(default=_get_date)


class Webhook(models.Model):
    __table_name__ = 'webhooks'
    __options__ = default_options
    id = columns.BigInt(primary_key=True, partition_key=True)
    channel_id = columns.BigInt(primary_key=True)
    guild_id = columns.BigInt(primary_key=True)
    creator_id = columns.BigInt()
    name = columns.Text(max_length=100)
    avatar = columns.Text()
    token = columns.Text()


class IgnoredBucket(models.Model):
    __table_name__ = 'ignored_buckets'
    channel_id = columns.BigInt(primary_key=True)
    bucket_id = columns.Integer()


def to_dict(model: models.Model, _keep_email=False) -> dict:
    # avoid import errors
    from .utils import run_migrations

    model = run_migrations(model)

    initial: dict[str, Any] = model.items()
    ret = dict(initial)

    if type(model).__name__ == 'Member':
        try:
            ret['user'] = to_dict(
                User.objects(
                    User.id == model.id,
                ).get()
            )
        except:
            # user was deleted
            ret['user'] = None

        try:
            ret['guild'] = to_dict(
                Guild.objects(
                    Guild.id == model.guild_id,
                ).get()
            )
        except:
            # user was deleted
            ret['guild'] = model.guild_id

    elif type(model).__name__ == 'Message':
        try:
            ret['author'] = to_dict(User.objects(User.id == model.author_id).get())
            ret.pop('author_id')
        except:
            # author was deleted
            ret['author'] = None

    elif type(model).__name__ == 'Webhook':
        ret.pop('token')

    elif type(model).__name__ == 'GuildChannel':
        ls = PermissionOverWrites.objects(
            PermissionOverWrites.channel_id == model.id
        ).all()
        overwrites = []

        for obj in ls:
            obj = to_dict(obj)
            obj.pop('channel_id')
            overwrites.append(obj)

        ret['permission_overwrites'] = overwrites

    for name, value in initial:
        if isinstance(value, (usertype.UserType, models.Model)):
            # things like member objects or embeds can have usertypes 3/4 times deep
            # there shouldnt be a recursion problem though
            value = dict(value.items())
            for k, v in value.items():
                if isinstance(v, usertype.UserType):
                    value[k] = to_dict(v)
            ret[name] = value

        # some values are lists of usertypes
        elif isinstance(value, (list, set)):
            if isinstance(value, set):
                value = list(value)

            set_values = []

            for v in value:
                if isinstance(v, usertype.UserType):
                    set_values.append(to_dict(v))
                elif isinstance(v, int):
                    set_values.append(str(v))
                else:
                    set_values.append(v)

            ret[name] = set_values

        if (
            name == 'id'
            or name.endswith('_id')
            and len(str(value)) > 14
            and name != 'message_id'
            and name != 'guild_id'
            and name != 'bucket_id'
            and name != 'channel_id'
            or name == 'parent_id'
        ):
            ret[name] = str(value)

        elif name == 'permissions':
            ret[name] = str(value)

        elif name == 'password':
            ret.pop(name)

        elif name == 'email' and not _keep_email:
            ret.pop(name)

        elif name == 'settings' and not _keep_email:
            ret.pop(name)

        elif name == 'message_id':
            ret.pop('message_id')
            ret['id'] = str(value)

        elif name == 'bucket_id':
            ret.pop('bucket_id')

        elif name == 'verification_code':
            ret.pop('verification_code')

        elif name == 'guild_id':
            id = ret.pop('guild_id')
            ret['guild'] = to_dict(Guild.objects(Guild.id == id).get())

        elif name == 'channel_id':
            try:
                id = ret.pop('channel_id')
                ret['channel'] = to_dict(
                    GuildChannel.get(GuildChannel.id == id).allow_filtering().get()
                )
            except:
                ret['channel'] = None

        elif name == 'ip':
            ret.pop('ip')

    del run_migrations

    return ret


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)
    connect()

    # migrate old data

    # NOTE: Tables
    management.sync_table(User)
    management.sync_table(Guild)
    management.sync_table(GuildInvite)
    management.sync_table(Member)
    management.sync_table(GuildChannel)
    management.sync_table(GuildChannelPin)
    management.sync_table(Message)
    management.sync_table(ReadState)
    management.sync_table(Role)
    management.sync_table(Emoji)
    management.sync_table(ChannelSlowMode)
    management.sync_table(Meta)
    management.sync_table(GuildMeta)
    management.sync_table(Note)
    management.sync_table(Reaction)
    management.sync_table(PermissionOverWrites)
    management.sync_table(Audit)
    management.sync_table(IgnoredBucket)
