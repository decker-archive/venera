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
import os
import threading
import time


class SnowflakeFactory:
    def __init__(self) -> None:
        self._epoch: int = 1649325271415
        self._incrementation = 0

    def formulate(self) -> int:
        current_ms = int(time.time() * 1000)
        epoch = current_ms - self._epoch << 22

        epoch |= (threading.current_thread().ident % 32) << 17
        epoch |= (os.getpid() % 32) << 12

        epoch |= self._incrementation % 4096

        self._incrementation += 1

        return epoch


if __name__ == '__main__':
    l = []
    f = SnowflakeFactory()
    while True:
        sf = f.formulate()
        if sf in l:
            print(sf, ' was duplicated')
            break
        l.append(sf)
        print(sf)
