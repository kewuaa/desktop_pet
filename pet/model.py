from random import sample
import os
import string
import base64
import asyncio

from aiohttp import ClientSession
from py_mini_racer import MiniRacer
from py_mini_racer.py_mini_racer import JSEvalException

from pet.hzy import fake_ua
from pet.hzy.aiofile import aiofile


random_string = string.ascii_letters + string.digits


class BaseModel(object):
    """base of all."""

    def __init__(self, current_path: str, js: str = None) -> None:
        self.headers = {}
        self.sess = ClientSession()
        self.current_path = current_path
        self._get_js_path = self._get_js_path()
        self.ua = fake_ua.UserAgent()
        self._js_code = js and self._load_js(js)

    def _set_random_ua(self):
        self.headers['user-agent'] = self.ua.get_ua()

    def _remove_browser(self, browser_type: str):
        self.ua.remove(browser_type)

    @property
    def session(self):
        if self.sess.closed:
            self.sess = ClientSession()
        return self.sess

    def _load_js(self, js: str):
        asyncio.create_task(self._judge_env())
        return base64.b64decode(js.encode())

    def _get_js_path(self):
        times = 0
        self._js_path = None

        async def func():
            nonlocal times
            times += 1
            if not times % 3:
                os.remove(self._js_path)
                self._js_path = None
            if self._js_path is None:
                self._js_path = os.path.join(
                    self.current_path, self._get_random_name() + '.js')
                async with aiofile.open_async(self._js_path, 'wb') as f:
                    await f.write(self._js_code)
            return self._js_path
        return func

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
            context = aiofile.AIOWrapper(MiniRacer())
            js_code = self._js_code.decode().split('/' * 33)[0]
            try:
                await context.eval(js_code)
            except JSEvalException:
                is_ok = False
            else:
                is_ok = True
            finally:
                async def run_js(data=None):
                    assert is_ok, 'js parse error'
                    if data is None:
                        return await context.call('main')
                    else:
                        return await context.call('main', data)
        else:
            async def run_js(data=None):
                path = await self._get_js_path()
                cmd = ' '.join(['node', path, data or ''])
                return await self._get_popen_result(cmd)
        self._run_js = run_js

    @staticmethod
    async def _get_popen_result(cmd: str) -> str:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        assert not stderr, stderr.decode('gbk')
        return stdout.decode().strip()

    async def close(self):
        await self.session.close()
        self._js_path and os.remove(self._js_path)


class Signal(object):
    """signal."""

    def __init__(self) -> None:
        super(Signal, self).__init__()
        self.func = None
        self.args = None

    def connect(self, func, *args):
        self.func = func
        self.args = args

    def emit(self):
        self.func and self.func(*self.args)
