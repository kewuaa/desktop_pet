# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-02-11 15:15:54
# @Last Modified by:   None
# @Last Modified time: 2022-03-05 09:37:01
from collections import namedtuple
from inspect import signature
from functools import wraps
from http.cookies import SimpleCookie
from random import sample
import os
import js2py
import string
import base64
import asyncio

from hzy.aiofile import aiofile
from aiohttp import ClientSession

SongInfo = namedtuple('SongInfo', ['text', 'id', 'pic', 'pic_url'])
SongUrl = namedtuple('SongUrl', ['url', 'vip'], defaults=(False,))
SongID = namedtuple('SongID', ['id', 'app'])
random_string = string.ascii_letters + string.digits


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


class BaseMusicer(object):
    """basic of all musicer."""

    def __init__(
            self, *, js: str = None, current_path: str, verify=False):
        super(BaseMusicer, self).__init__()
        self.headers = {}
        self.sess = ClientSession()
        self.current_path = current_path
        self._need_verify = verify
        self._add_cookie()
        if js is not None:
            self.load_js = self._load_js(js)

    @staticmethod
    def _get_cookie_dict(cookie_str: str) -> dict:
        return {i.key: i.value for i in SimpleCookie(cookie_str).values()}

    @staticmethod
    def _get_cookie_str(cookie_dict: dict) -> str:
        return '; '.join('='.join(str(i) for i in item) for item in cookie_dict.items())

    @property
    def session(self):
        if self.sess.closed:
            self.sess = ClientSession()
        return self.sess

    def verify(self):
        if self._need_verify:
            return asyncio.create_task(self._verify())

    async def _verify(self):
        pass

    def _load_js(self, js: str):
        async def load_js(name: str = None) -> str:
            if name is None:
                name = self._get_random_name()
            if not os.path.exists(
                    path := os.path.join(self.current_path, f'{name}.js')):
                async with aiofile.open_async(
                        path, 'wb') as f:
                    b64content = js.encode()
                    content = base64.b64decode(b64content)
                    await f.write(content)
            return path
        asyncio.create_task(self._judge_env())
        return load_js

    @staticmethod
    def _get_random_name() -> str:
        return ''.join(sample(random_string, 3 * 3))

    async def _judge_env(self):
        proc = await asyncio.create_subprocess_shell(
            'node -v',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        _, stderr = await proc.communicate()
        if stderr:
            async def run_js(path, data=None):
                context = aiofile.AIOWrapper(js2py.EvalJs())
                async with aiofile.open_async(path, 'r') as f:
                    js_code = await f.read()
                    await context.execute(js_code.split('/' * 33)[0])
                    if data is None:
                        return await context.main()
                    else:
                        return await context.main(data)
            self._run_js = run_js
        else:
            async def run_js(path, data=None):
                return await self._get_popen_result(
                    ' '.join(['node', path, data or '']))
            self._run_js = run_js

    async def _get_popen_result(self, cmd: str) -> str:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        assert not stderr, stderr.decode('gbk')
        return stdout.decode().strip()

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

    async def close(self):
        await self.session.close()
