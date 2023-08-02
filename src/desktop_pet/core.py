import asyncio
import random
import sys
from functools import partial

from PySide6.QtCore import QCoreApplication, Qt, QTimer
from PySide6.QtGui import QAction, QCursor, QGuiApplication, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMenu,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)
from qasync import QEventLoop

from . import image


class Pet(QWidget):
    def __init__(self, parent=None):
        super(Pet, self).__init__(parent)
        self.initUi()
        image.set_after_load(self.setSystemMenu)
        self.timer = QTimer()
        self.timer.timeout.connect(partial(image.set, self.image))
        self.timer.start(500)
        self.follow_mouse = False
        self.mouse_press_pos = None

    def initUi(self):
        screen = QGuiApplication.primaryScreen().size()
        self.x = screen.width() - self.width()
        self.y = screen.height() - self.height()
        # 加载配置
        # 依次为:子窗口化 去除界面边框 设置窗口置顶
        self.setWindowFlags(
            Qt.SubWindow | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint,
        )
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

    def setSystemMenu(self, all_actions):
        icon = all_actions[0][0]
        icon = QIcon(QPixmap.fromImage(icon))
        quit_action = QAction('退出', parent=self)
        quit_action.triggered.connect(lambda: asyncio.create_task(self.quit()))
        quit_action.setIcon(icon)
        menu = QMenu('exit', parent=self)
        menu.addAction(quit_action)
        self.tray_icon = QSystemTrayIcon(parent=self)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setIcon(icon)
        self.tray_icon.show()

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
        app = QCoreApplication.instance()
        if app is not None:
            app.quit()

    def show(self):
        self.move(self.x * random.random(), self.y * random.random())
        super().show()


def run():
    application = QApplication(sys.argv)
    loop = QEventLoop(application)
    asyncio.set_event_loop(loop)
    Pet()
    with loop:
        loop.run_forever()
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.run_until_complete(loop.shutdown_default_executor())
