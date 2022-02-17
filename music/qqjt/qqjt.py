# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-02-17 09:15:39
# @Last Modified by:   None
# @Last Modified time: 2022-02-17 11:40:29
import os
current_path, _ = os.path.split(os.path.realpath(__file__))
if __name__ == '__main__':
    import sys
    sys.path.append(os.path.join(current_path, '..'))
    sys.path.append(os.path.join(current_path, '../..'))

import asyncio

from hzy import fake_ua
try:
    from model import SongInfo
    from model import BaseMusicer
except ImportError:
    from ..model import SongInfo
    from ..model import BaseMusicer


ua = fake_ua.UserAgent()


class Musicer(BaseMusicer):
    """docstring for Musicer."""

    HEADERS = {}

    def __init__(self):
        super(Musicer, self).__init__(current_path=current_path, headers=self.HEADERS)
