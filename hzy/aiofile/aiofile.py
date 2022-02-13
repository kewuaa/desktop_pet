# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-01-23 15:53:31
# @Last Modified by:   None
# @Last Modified time: 2022-02-05 19:32:18
import asyncio


class AsyncFuncWrapper(object):
    """docstring for AsyncFuncWrapper."""

    def __init__(self, block_func,
                 executor=None) -> None:
        super(AsyncFuncWrapper, self).__init__()
        self._block_func = block_func
        self._executor = executor

    def __call__(self, *args, **kwargs):
        return asyncio.get_running_loop().run_in_executor(
            self._executor, self._block_func, *args, **kwargs)


class AIOWrapper(object):
    """docstring for AIOWrapper."""

    def __init__(self, block_file_io):
        super(AIOWrapper, self).__init__()
        self._block_file_io = block_file_io

    def __getattribute__(self, name: str) -> AsyncFuncWrapper:
        io = super(AIOWrapper, self).__getattribute__('_block_file_io')
        block_func = getattr(io, name)
        return AsyncFuncWrapper(block_func)


# async def open_async(file, mode='r', buffering=-1, encoding=None, *args):
#     f = await asyncio.get_running_loop().run_in_executor(
#         None, open, file, mode, buffering, encoding, *args)
#     return AIOWrapper(block_file_io=f)


class open_async(object):
    """docstring for open_async."""

    def __init__(self, file, mode='r', buffering=-1, encoding=None, *args):
        super(open_async, self).__init__()
        self.file = file
        self.mode = mode
        self.buffering = buffering
        self.encoding = encoding
        self.args = args

    async def __aenter__(self):
        f = await asyncio.get_running_loop().run_in_executor(
            None, open, self.file, self.mode, self.buffering,
            self.encoding, *self.args)
        self.f = AIOWrapper(f)
        return self.f

    async def __aexit__(self, *args):
        await self.f.close()


if __name__ == '__main__':
    async def test():
        # f = await open_async('test.txt', mode='w', encoding='utf-8')
        # await f.write('this is one test')
        # await f.close()
        async with open_async('text.txt', mode='w', encoding='utf-8') as f:
            f.write('this is one test')
    asyncio.run(test())
