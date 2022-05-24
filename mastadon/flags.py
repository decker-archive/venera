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
import functools


def _has_flag(v: int, f: int) -> bool:
    return True if v & f else False


class UserFlags:
    def __init__(self, __v: int):
        has = functools.partial(_has_flag, __v)

        self.early_supporter = has(1 << 0)
        self.staff = has(1 << 1)
        self.verified = has(1 << 2)
        self.likely_scammer = has(1 << 3)
        self.donator = has(1 << 4)
        self.contributor = has(1 << 5)
        self.bug_hunter = has(1 << 6)


class GuildPermissions:
    @classmethod
    def default(self):
        return (
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

    def __init__(self, __v: int):
        has = functools.partial(_has_flag, __v)

        self.create_invites = has(1 << 0)
        self.kick_members = has(1 << 1)
        self.ban_members = has(1 << 2)
        self.administator = has(1 << 3)
        self.manage_channels = has(1 << 4)
        self.manage_guild = has(1 << 5)
        self.add_reactions = has(1 << 6)
        self.view_audit_log = has(1 << 7)

        # NOTE: Voice, although not out yet.
        # self.priority_speaker = has(1 << 8)
        # self.stream = has(1 << 9)
        self.view_channels = has(1 << 10)
        self.send_messages = has(1 << 11)
        self.send_tts_messages = has(1 << 12)
        self.manage_messages = has(1 << 13)
        self.embed_links = has(1 << 14)
        self.attach_files = has(1 << 15)
        self.read_message_history = has(1 << 16)
        self.mention_everyone = has(1 << 17)
        self.use_external_emojis = has(1 << 18)

        # TODO: Guild Insights
        # self.view_guild_insights = has(1 << 19)

        # NOTE: Voice, again
        # self.connect = has(1 << 20)
        # self.speak = has(1 << 21)
        # self.mute_members = has(1 << 22)
        # self.deafen_members = has(1 << 23)
        # self.move_members = has(1 << 24)

        self.change_nick = has(1 << 25)
        self.manage_nicks = has(1 << 26)
        self.manage_roles = has(1 << 27)
        self.manage_webhooks = has(1 << 28)
        self.manage_emojis = has(1 << 29)

        # NOTE: Is this feature actually possible?
        # self.manage_events = has(1 << 30)

        self.manage_channel_pins = has(1 << 31)
        self.create_audits = has(1 << 32)


if __name__ == '__main__':
    print(GuildPermissions.default())
