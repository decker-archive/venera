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
import base64
import binascii

import itsdangerous

from .database import User
from .errors import Forbidden, Unauthorized


def create_token(user_id: int, user_password: str) -> str:
    signer = itsdangerous.TimestampSigner(user_password)
    user_id = str(user_id)
    user_id = base64.b64encode(user_id.encode())

    return signer.sign(user_id).decode()


def verify_token(token: str):
    if token is None or not isinstance(token, str):
        raise Unauthorized()

    fragmented = token.split('.')
    user_id = fragmented[0]

    try:
        user_id = base64.b64decode(user_id.encode())
        user_id = int(user_id)
    except (ValueError, binascii.Error):
        raise Unauthorized()

    try:
        user: User = User.objects(User.id == user_id).get()
    except:
        raise Unauthorized()

    signer = itsdangerous.TimestampSigner(user.password)

    try:
        signer.unsign(token)

        return user
    except (itsdangerous.BadSignature):
        raise Forbidden()
