from random import sample
import os
import js2py
import string
import base64
import asyncio

from aiohttp import ClientSession

from pet.hzy import fake_ua
from pet.hzy.aiofile import aiofile


random_string = string.ascii_letters + string.digits


class BaseModel(object):
    """base of all."""

    def __init__(self, current_path: str, js: str = None) -> None:
        self.headers = {}
        self.sess = ClientSession()
        self.current_path = current_path
        self.ua = fake_ua.UserAgent()
        if js is not None:
            self.load_js = self._load_js(js)

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
        if not stderr:
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
        if self.func is not None:
            self.func(*self.args)
