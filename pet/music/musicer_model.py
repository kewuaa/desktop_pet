# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-02-11 15:15:54
# @Last Modified by:   None
# @Last Modified time: 2022-03-05 09:39:43
from collections import namedtuple
from inspect import signature
from functools import wraps
from http.cookies import SimpleCookie
import os
import asyncio

from pet.hzy.aiofile import aiofile
from pet.model import BaseModel


SongInfo = namedtuple('SongInfo', ['text', 'id', 'pic', 'pic_url'], defaults=(None, None))
SongUrl = namedtuple('SongUrl', ['url', 'vip'], defaults=(False,))
SongID = namedtuple('SongID', ['id', 'app'])


class HZYErr(Exception):
    pass


class CookieInvalidError(HZYErr):
    pass


class LackLoginArgsError(HZYErr):
    pass


class LoginIncompleteError(HZYErr):
    pass


class VerifyError(HZYErr):
    pass


class BaseMusicer(BaseModel):
    """basic of all musicer."""

    def __init__(
            self, *, js: str = None, current_path: str, verify=False):
        super(BaseMusicer, self).__init__(
            current_path=current_path, js=js)
        self._need_verify = verify
        self._add_cookie()

    @staticmethod
    def _get_cookie_dict(cookie_str: str) -> dict:
        return {i.key: i.value for i in SimpleCookie(cookie_str).values()}

    @staticmethod
    def _get_cookie_str(cookie_dict: dict) -> str:
        return '; '.join('='.join(str(i) for i in item) for item in cookie_dict.items())

    def verify(self):
        if self._need_verify:
            return asyncio.create_task(self._verify())

    async def _verify(self):
        pass

    async def _load_cookie(self):
        if os.path.exists(path := os.path.join(self.current_path, 'cookie')):
            async with aiofile.open_async(path, 'r') as f:
                return await f.read()

    def _add_cookie(self):
        def update(*args):
            if (cookie := load_cookie_task.result()) is not None:
                self.headers.update(
                    {'cookie' if 'cookie' in self.headers else 'Cookie': cookie})
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

    async def login(self, **login_args):
        if signature(self._login).parameters.get('unprepare', False):
            raise LoginIncompleteError
        if not login_args:
            if (login_args := await self._load_setting()) is not None:
                assert 'login_id' in login_args and 'password' in login_args,\
                    'setting文件格式有误'
            else:
                raise LackLoginArgsError('尚未存在登录信息')
        await self._login(**login_args)
        return login_args

    async def _login(self, unprepare=None):
        raise RuntimeError('unprepare')

    async def reset_setting(self, **kwargs):
        if 'verify_code' in kwargs:
            kwargs.pop('verify_code')
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
            if (cookies := self.headers.get(key := 'cookie')) is None:
                cookies = self.headers[(key := 'Cookie')]
            cookies = self._get_cookie_dict(cookies)
            cookies.update(new_cookie)
            cookie_str = self.headers[key] = self._get_cookie_str(cookies)
            asyncio.create_task(self._reset_cookie(cookie_str))
        return _login
