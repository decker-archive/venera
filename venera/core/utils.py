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
import re

import dotenv
import orjson
from blacksheep import Content, FromHeader, Response
from imgproxy import ImgProxy

dotenv.load_dotenv()

NONMESSAGEABLE = [0]
MESSAGEABLE = [1]
CHANNEL_TYPES = [0, 1]
VALID_GUILD_FEATURES = [
    'THREAD_CHANNELS',
    'MESSAGE_ATTACHMENTS',
    'EMOJIS',
    'GUILD_ICONS',
    'GUILD_BANNERS',
    'GUILD_MEMBER_BANNERS',
    'GUILD_MEMBER_AVATARS',
    'CHANNEL_THREADS',
    'POLL_CHANNELS',
    'WEBHOOKS',
    'BOTS',
    'AUDIT_LOG',
    'VOICE_CHANNELS',
    'GUILD_DISCOVERY',
    'GUILD_EVENTS',
    'GUILD_SAFETY',
    'ANOUNCEMENT_CHANNELS',
    'ROLE_AVATARS',
    'TEXT_IN_VOICE_CHANNELS',
    'WELCOME_VERIFICATION',
    'FORM_CHANNELS',
]
VALID_THEMES = ['dark', 'light']
VALID_LOCALES = [
    'en-US',
    'en-GB',
]
DEPRECATED_LOCALES = ['en_US', 'en_UK', 'EN_US']
SCIENCE_TYPES = [
    'app-opened',
    'guild-opened',
    'channel-opened',
    'pane-opened',
    'changelog-viewed',
]

IMGPROXY_KEY = os.getenv('IMGPROXY_KEY')
IMGPROXY_SALT = os.getenv('IMGPROXY_SALT')
IMGPROXY_URL = os.getenv('IMGPROXY_URL', 'https://images-ext.veneralab.com')
VALID_WORDS = 'a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 1 2 3 4 5 6 7 8 9 0 -'.split(
    ' '
)


class AuthHeader(FromHeader[str]):
    name = 'Authorization'


def jsonify(data: dict, status: int = 200) -> Response:
    return Response(
        status=status,
        headers=None,
        content=Content(b'application/json', orjson.dumps(data)),
    )


def run_migrations(model):
    if type(model).__name__ == 'Guild':
        if model.perferred_locale in DEPRECATED_LOCALES:
            if 'US' in model.perferred_locale:
                model.perferred_locale = 'en-US'
            else:
                model.perferred_locale = 'en-GB'

            model.save()

    return model


NAME_FILTER = re.compile(r"^[^\u200BА-Яа-яΑ-Ωα-ω]+$")


def proxy_img(url: str, w: int = 0, h: int = 0):
    proxifier = ImgProxy(
        url, IMGPROXY_URL, key=IMGPROXY_KEY, salt=IMGPROXY_SALT, width=w, height=h
    )

    return proxifier()
