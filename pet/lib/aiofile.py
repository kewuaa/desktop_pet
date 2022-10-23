from concurrent.futures import ThreadPoolExecutor
from functools import partial
import asyncio


class AWrapper:
    """异步函数包装"""

    def __init__(self, block_func) -> None:
        self._block_func = block_func

    def __call__(self, *args, **kwargs) -> asyncio.futures.Future:
        return asyncio.get_event_loop().run_in_executor(
            None, partial(self._block_func, *args, **kwargs))


class AIOWrapper:
    """异步包装类"""

    def __init__(self, block_io) -> None:
        self._io = block_io

    def __getattribute__(self, name: str):
        io = super().__getattribute__('_io')
        return AWrapper(io.__getattribute__(name))


class async_open:
    """异步文件处理"""

    def __init__(self, file, mode, *, encoding=None, **kwargs):
        self._init_func = partial(
            open, file, mode, encoding=encoding, **kwargs)
        self._aio = None

    async def __aenter__(self):
        io = await asyncio.get_event_loop().run_in_executor(
            None, self._init_func)
        self._aio = AIOWrapper(io)
        return self._aio

    async def __aexit__(self, *args):
        await self._aio.close()


if __name__ == '__main__':
    from pathlib import Path

    async def main():
        async with async_open(
                Path(__file__).parent / './test.log', 'w',
                encoding='utf-8') as f:
            await f.write('test')
        print('done')
    asyncio.get_event_loop().run_until_complete(main())
