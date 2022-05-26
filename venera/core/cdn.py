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

import boto3
import dotenv

dotenv.load_dotenv()


def upload(name: str, folder: str, obj: bytes, content_type: str):
    s3 = boto3.client(
        's3',
        region_name='ap-northeast-1',
        aws_access_key_id=os.getenv('ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('ACCESS_SECRET_KEY'),
    )

    s3.upload_fileobj(
        obj,
        'cdn.veneralab.com',
        folder + '/' + name,
        ExtraArgs={
            'ContentType': content_type or 'binary/octet-stream',
            'ACL': 'public-read',
        },
    )

    del s3
