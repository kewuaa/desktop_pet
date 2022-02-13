# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-01-14 13:00:02
# @Last Modified by:   None
# @Last Modified time: 2022-02-09 12:30:55
import base64
import asyncio
import random
import sys
import os

from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QMenu
from PySide2.QtWidgets import QSystemTrayIcon
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QAction
from PySide2.QtCore import Qt
from PySide2.QtCore import Slot
from PySide2.QtCore import QTimer
from PySide2.QtCore import QThread
from PySide2.QtCore import QCoreApplication
from PySide2.QtGui import QImage
from PySide2.QtGui import QPixmap
from PySide2.QtGui import QIcon
from PySide2.QtGui import QCursor
from PySide2.QtUiTools import QUiLoader
from qasync import QEventLoop

from hzy.aiofile import aiofile
from translate.translate import TransApp
from music.music_player import MusicApp
from pictures import *


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
    def __init__(self, parent=None, **configs):
        super(Pet, self).__init__(parent)
        desktop = QApplication.desktop()
        self.x = desktop.width() - self.width()
        self.y = desktop.height() - self.height()
        # 加载配置
        self.config = Config()
        for name, value in configs.items():
            if hasattr(self.config, name):
                setattr(self.config, name, value)
        # 依次为:子窗口化 去除界面边框 设置窗口置顶
        self.setWindowFlags(
            Qt.SubWindow | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # 自动填充背景，False则无背景，全白
        self.setAutoFillBackground(False)
        # 使背景透明
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 重新渲染
        self.repaint()
        asyncio.get_running_loop().run_in_executor(None, self.initPet)
        # self.initPet()
        self.setSystemMenu()
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        self.image = QLabel(parent=self)
        vbox.addWidget(self.image)
        self.setImage(self.icon)
        self.show()
        self.current_action = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.act)
        self.timer.start(500)
        self.follow_mouse = False
        self.mouse_press_pos = None

    def initPet(self):
        self.pet = random.choice(list(self.config.PETS.keys()))
        # img_file_path = os.path.join(self.config.PATH, self.pet)
        self.actions = []
        for action in self.config.PETS[self.pet]:
            self.actions.append(
                [self.loadImage(eval(self.pet)[int(index) - 1])
                 for index in action])
        self.icon = self.actions[0][0]

    def setSystemMenu(self):
        self.trans_app = TransApp()
        self.trans_app.ui.setWindowFlags(Qt.Tool)
        self.music_app = MusicApp()
        self.music_app.ui.setWindowFlags(Qt.Tool)
        icon = QIcon(QPixmap.fromImage(self.icon))
        quit_action = QAction('退出', parent=self)
        quit_action.triggered.connect(self.quit)
        quit_action.setIcon(icon)
        trans_action = QAction(
            '百度翻译', parent=self, triggered=self.trans_app.show)
        music_action = QAction(
            '网易云', parent=self, triggered=self.music_app.show)
        music_action.setIcon(self.music_app.ui.window_icon)
        action_bat = QAction(
            '导出bat脚本文件', parent=self, triggered=self.get_bat_file())
        menu = QMenu('exit', parent=self)
        menu.addAction(action_bat)
        menu.addAction(music_action)
        menu.addAction(trans_action)
        menu.addAction(quit_action)
        self.tray_icon = QSystemTrayIcon(parent=self)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setIcon(icon)
        self.tray_icon.show()

    @Slot()
    def get_bat_file(self):
        async def write():
            async with aiofile.open_async(
                    path := os.path.join(
                        os.path.expanduser('~'), 'Desktop', 'pet.bat'), 'w') as f:
                pass
            async with aiofile.open_async(path, 'a') as f:
                await f.write('@echo off\nif "%1" == "233" goto begin\n')
                await f.write(r'mshta vbscript:createobject("wscript.shell").run("%~nx0 233",0)(window.close)&&exit')
                await f.write(f'\n:begin\npython {__file__}')

        def connect_func():
            asyncio.create_task(write())
        return connect_func

    def setImage(self, img):
        self.image.setPixmap(QPixmap.fromImage(img))

    def act(self):
        if self.current_action:
            img = self.current_action.pop()
            self.setImage(img)
        else:
            self.current_action = random.choice(self.actions).copy()
            self.current_action.reverse()

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

    def quit(self):
        self.tray_icon = None
        QCoreApplication.instance().quit()

    def show(self):
        self.move(self.x * random.random(), self.y * random.random())
        super(Pet, self).show()

    @staticmethod
    def loadImage(b64str):
        b64content = b64str.encode()
        data = base64.b64decode(b64content)
        img = QImage()
        # img.load(img_path)
        img.loadFromData(data)
        return img


if __name__ == '__main__':
    application = QApplication(sys.argv)
    loop = QEventLoop(application)
    asyncio.set_event_loop(loop)
    with loop:
        pet = Pet()
        loop.run_forever()
