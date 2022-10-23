from pathlib import Path
import base64
import asyncio
import random
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot
from PySide6.QtCore import QTimer
from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QGuiApplication
from PySide6.QtGui import QAction
from PySide6.QtGui import QImage
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QIcon
from PySide6.QtGui import QCursor
# from PySide6.QtUiTools import QUiLoader
from qasync import QEventLoop

from .lib import aiofile
from .lib.talk import Talker
from .pictures import *


class Config:
    ACTION_DISTRIBUTION = [
        ['1', '2', '3'],
        ['4', '5', '6', '7', '8', '9', '10', '11'],
        ['12', '13', '14'],
        ['15', '16', '17'],
        ['18', '19'],
        ['20', '21'],
        ['22'],
        ['23', '24', '25'],
        ['26', '27', '28', '29'],
        ['30', '31', '32', '33'],
        ['34', '35', '36', '37'],
        ['38', '39', '40', '41'],
        ['42', '43', '44', '45', '46']
    ]
    PETS = {}
    for i in range(1, 5):
        PETS[f'pet_{i}'] = ACTION_DISTRIBUTION


class Pet(QWidget):
    def __init__(self, parent=None):
        super(Pet, self).__init__(parent)
        self.initUi()
        asyncio.get_event_loop().run_in_executor(
            None,
            self.initPet,
        ).add_done_callback(lambda fut: self.setSystemMenu())
        self.current_action = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.act)
        self.timer.start(500)
        self.follow_mouse = False
        self.mouse_press_pos = None

    def initUi(self):
        screen = QGuiApplication.primaryScreen().size()
        self.x = screen.width() - self.width()
        self.y = screen.height() - self.height()
        # 加载配置
        self.config = Config()
        # 依次为:子窗口化 去除界面边框 设置窗口置顶
        self.setWindowFlags(
            Qt.SubWindow | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # 自动填充背景，False则无背景，全白
        self.setAutoFillBackground(False)
        # 使背景透明
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 重新渲染
        self.repaint()
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        self.image = QLabel(parent=self)
        vbox.addWidget(self.image)
        self.show()


    def initPet(self):
        self.pet = random.choice(list(self.config.PETS.keys()))
        # img_file_path = os.path.join(self.config.PATH, self.pet)
        self.actions = []
        for action in self.config.PETS[self.pet]:
            self.actions.append(
                [self.loadImage(eval(self.pet)[int(index) - 1])
                 for index in action])
        self.icon = self.actions[0][0]
        self.setImage(self.icon)

    def setSystemMenu(self):
        self.talker = Talker()
        icon = QIcon(QPixmap.fromImage(self.icon))
        quit_action = QAction('退出', parent=self)
        quit_action.triggered.connect(lambda: asyncio.create_task(self.quit()))
        quit_action.setIcon(icon)
        menu = QMenu('exit', parent=self)
        menu.addAction(quit_action)
        self.tray_icon = QSystemTrayIcon(parent=self)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setIcon(icon)
        self.tray_icon.show()

    def setImage(self, img):
        self.image.setPixmap(QPixmap.fromImage(img))

    def act(self):
        if self.current_action:
            img = self.current_action.pop()
            self.setImage(img)
        else:
            self.current_action = random.choice(self.actions).copy()
            self.current_action.reverse()

    def mouseDoubleClickEvent(self, event):
        self.talker()
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        # print('press', event.globalPos(), self.pos())
        if event.button() == Qt.LeftButton:
            self.follow_mouse = True
            self.mouse_press_pos = self.pos() - event.globalPos()
            self.setCursor(QCursor(Qt.OpenHandCursor))
        super(Pet, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # print('move', event.globalPos(), self.pos())
        if Qt.LeftButton and self.follow_mouse:
            self.move(event.globalPos() + self.mouse_press_pos)
        super(Pet, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # print('release', event.globalPos(), self.pos())
        if self.follow_mouse:
            self.follow_mouse = False
            self.setCursor(QCursor(Qt.ArrowCursor))
        super(Pet, self).mouseReleaseEvent(event)

    async def quit(self):
        self.tray_icon = None
        await self.talker.close()
        QCoreApplication.instance().quit()

    def show(self):
        self.move(self.x * random.random(), self.y * random.random())
        super().show()

    @staticmethod
    def loadImage(b64str):
        b64content = b64str.encode()
        data = base64.b64decode(b64content)
        img = QImage()
        # img.load(img_path)
        img.loadFromData(data)
        return img


def run():
    application = QApplication(sys.argv)
    loop = QEventLoop(application)
    asyncio.set_event_loop(loop)
    with loop:
        pet = Pet()
        loop.run_forever()

