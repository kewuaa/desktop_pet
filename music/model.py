# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-02-11 15:15:54
# @Last Modified by:   None
# @Last Modified time: 2022-02-13 21:01:40
from collections import namedtuple
from http.cookies import SimpleCookie
import os
import base64
import asyncio

from hzy.aiofile import aiofile
from aiohttp import ClientSession

SongInfo = namedtuple('SongInfo', ['text', 'id', 'pic', 'pic_url'])


class HZYErr(Exception):
    pass


class CookieInvalidError(HZYErr):
    pass


class BaseMusicer(object):
    """basic of all musicer."""

    def __init__(
            self, *, js=None, current_path: str, name: str = None):
        super(BaseMusicer, self).__init__()
        self.sess = ClientSession()
        self.current_path = current_path
        if js is not None and name is not None:
            asyncio.create_task(self._load_js(js, name))

    def load_login_args(self, *login_args):
        assert len(login_args) == 2, '登录参数格式不正确'
        self.login_id, self.password = login_args

    @staticmethod
    def _get_cookie_dict(cookie_str: str) -> dict:
        return {i.key: i.value for i in SimpleCookie(cookie_str).values()}

    @staticmethod
    def _get_cookie_str(cookie_dict: dict) -> str:
        return '; '.join('='.join(item) for item in cookie_dict.items())

    @property
    def session(self):
        if self.sess.closed:
            self.sess = ClientSession()
        return self.sess

    async def _load_js(self, js, name):
        if not os.path.exists(
                path := os.path.join(self.current_path, f'{name.split(".")[-1]}.js')):
            async with aiofile.open_async(
                    path, 'w') as f:
                b64content = js.encode()
                content = base64.b64decode(b64content)
                await f.write(content.decode())
        self.js_path = path

    async def _get_song_info(self, song):
        pass

    async def _get_song_url(self, _id):
        pass

    async def login(self, login_id, password):
        pass

    async def _reset_cookie(self, cookie: str) -> None:
        async with aiofile.open_async(
                os.path.join(self.current_path, 'cookie.py'), 'w') as f:
            await f.write(f'cookie = "{cookie}"\n')

    async def close(self):
        await self.session.close()
