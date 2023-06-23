from pathlib import Path
import asyncio
import json
import os

import aiofiles
setting_path = Path(os.environ['Appdata'])
setting_file = setting_path / 'pet.json'


def load(callback):
    def cb(fut: asyncio.futures.Future):
        if fut.exception() is None:
            callback(fut.result())
        else:
            print('warning: loading setting file error')
            callback({})

    async def load():
        if not setting_file.exists():
            return {}
        async with aiofiles.open(setting_file, 'r') as f:
            json_str = await f.read()
        setting = json.loads(json_str)
        return setting
    asyncio.get_event_loop().create_task(load()).add_done_callback(cb)
