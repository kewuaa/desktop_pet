try:
    import tomllib
except ImportError:
    import tomli as tomllib
from pathlib import Path
from random import choice

from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel

ActionList = list[list[QImage]]

def random_init_action() -> ActionList:
    def to_img(ii: str) -> QImage:
        return QImage(f":img/images/{pet}/{ii}.jpg")

    with open(Path(__file__).parent / "actions.toml", "rb") as f:
        all_actions = tomllib.load(f)
    pet = choice(tuple(all_actions.keys()))
    __import__(f"desktop_pet.image.{pet}_rc")
    return [
        list(map(to_img, action))
        for action in all_actions[pet]
    ]

actions: ActionList = random_init_action()
current_action: list[QImage] = []


def set(label: QLabel) -> None:
    global current_action
    if not current_action:
        current_action = choice(actions).copy()
    img = current_action.pop()
    label.setPixmap(QPixmap.fromImage(img))
