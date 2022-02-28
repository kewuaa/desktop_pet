# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-02-11 15:15:54
# @Last Modified by:   None
# @Last Modified time: 2022-02-28 15:47:30
from collections import namedtuple
from inspect import signature
from functools import wraps
from http.cookies import SimpleCookie
import os
import base64
import asyncio

from hzy.aiofile import aiofile
from aiohttp import ClientSession

SongInfo = namedtuple('SongInfo', ['text', 'id', 'pic', 'pic_url'])
SongUrl = namedtuple('SongUrl', ['url', 'vip'], defaults=(False,))
SongID = namedtuple('SongID', ['id', 'app'])


class HZYErr(Exception):
    pass


class CookieInvalidError(HZYErr):
    pass


class LackLoginArgsError(HZYErr):
    pass


class LackCookieError(HZYErr):
    pass


class LoginIncompleteError(HZYErr):
    pass


class BaseMusicer(object):
    """basic of all musicer."""

    def __init__(
            self, *, js: str = None, current_path: str, cookie: str):
        super(BaseMusicer, self).__init__()
        self.headers = {}
        self.sess = ClientSession()
        self.current_path = current_path
        self.spare_cookie = cookie
        self._add_cookie()
        if js is not None:
            self.load_js = self._load_js(js)

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

    def _load_js(self, js: str):
        async def load_js(name: str):
            if not os.path.exists(
                    path := os.path.join(self.current_path, f'{name}.js')):
                async with aiofile.open_async(
                        path, 'wb') as f:
                    b64content = js.encode()
                    content = base64.b64decode(b64content)
                    await f.write(content)
        return load_js

    async def _get_popen_result(self, name: str) -> str:
        proc = await asyncio.create_subprocess_shell(
            f'node {self.current_path}/{name}.js',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        assert not stderr, stderr.decode('gbk')
        return stdout.decode().strip()

    async def _load_cookie(self):
        if os.path.exists(path := os.path.join(self.current_path, 'cookie')):
            async with aiofile.open_async(path, 'r') as f:
                return await f.read()
        else:
            raise LackCookieError

    def _add_cookie(self):
        def update(*args):
            if (e := load_cookie_task.exception()) is None:
                cookie = load_cookie_task.result()
            else:
                cookie = self.spare_cookie
            self.headers.update({'cookie': cookie})
        load_cookie_task = asyncio.create_task(self._load_cookie())
        load_cookie_task.add_done_callback(update)

    async def _get_song_info(self, song):
        pass

    async def _get_song_url(self, *_id):
        pass

    async def _load_setting(self):
        if os.path.exists(path := os.path.join(self.current_path, 'setting')):
            async with aiofile.open_async(path, 'r') as f:
                return {item[0]: item[1]
                        for line in await f.readlines()
                        if len(item := line.strip().split('=', 1)) > 1}

    async def login(self):
        if signature(self._login).parameters.get('unprepare', False):
            raise LoginIncompleteError
        if (login_args := await self._load_setting()) is not None:
            assert 'login_id' in login_args and 'password' in login_args,\
                'setting文件格式有误'
        else:
            raise LackLoginArgsError('尚未存在登录信息')
        await self._login(**login_args)

    async def _login(self, unprepare=None, **kwargs):
        pass

    async def reset_setting(self, **kwargs):
        assert 'login_id' in kwargs and 'password' in kwargs
        async with aiofile.open_async(
                os.path.join(self.current_path, 'setting'), 'w') as f:
            for k, v in kwargs.items():
                await f.write(f'{k}={v}\n')

    async def _reset_cookie(self, cookie: str) -> None:
        async with aiofile.open_async(
                os.path.join(self.current_path, 'cookie'), 'w') as f:
            await f.write(cookie)

    def _update_cookie(self, login_func):
        @wraps(login_func)
        async def _login(*args, **kwargs):
            new_cookie = await login_func(*args, **kwargs)
            cookies = self._get_cookie_dict(self.headers['cookie'])
            cookies.update(new_cookie)
            cookie_str = self.headers['cookie'] = self._get_cookie_str(cookies)
            asyncio.create_task(self._reset_cookie(cookie_str))
        return _login

    async def close(self):
        await self.session.close()
