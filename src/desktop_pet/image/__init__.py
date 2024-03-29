import asyncio
import json
from pathlib import Path
from random import choice

import aiofiles
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel

path = Path(__file__).parent
actions = None
current_action = None
after_load = None


async def load_pet(file: Path) -> dict:
    async with aiofiles.open(file, 'r') as f:
        json_str = await f.read()
    return json.loads(json_str)


async def load_image(image: Path) -> QImage:
    async with aiofiles.open(image, 'rb') as f:
        data = await f.read()
        img = QImage()
        img.loadFromData(data)
        return img


def set_after_load(callback):
    global after_load
    after_load = callback


async def load():
    pets = tuple(path.glob('*/pet.json'))
    if not pets:
        raise RuntimeError('pet file not found')
    pet = choice(pets)
    img_dir = pet.parent
    pet = await load_pet(pet)
    format = pet.get('img_format', 'jpg')
    actions = pet.get('actions')
    if actions is None:
        raise RuntimeError('pet file error, key "actions" is needed')
    all_actions = []
    for action in actions:
        all_actions.append([
            await load_image(img_dir / f'{i}.{format}')
            for i in action
        ])
    # return [
    #     [await load_image(img_dir / f'{i}.{format}') for i in action]
    #     for action in actions
    # ]
    return all_actions


def set(label: QLabel) -> None:
    async def aset():
        global current_action
        if not current_action:
            assert actions is not None
            current_action = choice(await actions).copy()
        image = current_action.pop()
        label.setPixmap(QPixmap.fromImage(image))
    global actions
    loop = asyncio.get_event_loop()
    if actions is None:
        def callback(fut: asyncio.futures.Future):
            if fut.exception() is not None:
                return
            if callable(after_load):
                after_load(fut.result())
        actions = loop.create_task(load())
        actions.add_done_callback(callback)
    loop.create_task(aset())
