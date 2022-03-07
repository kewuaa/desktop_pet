# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-01-21 18:36:13
# @Last Modified by:   None
# @Last Modified time: 2022-03-05 08:20:06
from io import BytesIO
from collections.abc import Coroutine
import os
import sys
import json
import pickle
import base64
import asyncio

from aiohttp import request
from PIL import Image
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QDialog
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QMessageBox
from PySide2.QtWidgets import QFileDialog
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QToolButton
from PySide2.QtWidgets import QMenu
from PySide2.QtWidgets import QAction
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtMultimedia import QMediaContent
from PySide2.QtMultimedia import QMediaPlaylist
from PySide2.QtCore import Qt
from PySide2.QtCore import QUrl
from PySide2.QtCore import Slot
from PySide2.QtCore import Signal
from PySide2.QtCore import QStringListModel
from PySide2.QtGui import QIcon
from PySide2.QtGui import QPixmap
# from PySide2.QtUiTools import QUiLoader
from qasync import QEventLoop


from pet.hzy.aiofile import aiofile
from pet.music.musicer_model import CookieInvalidError
from pet.music.musicer_model import LackLoginArgsError
from pet.music.musicer_model import LoginIncompleteError
from pet.music.musicer_model import VerifyError
from pet.music.pictures import *
from pet.music.wyy import wyy
from pet.music.kg import kg
from pet.music.mg import mg
from pet.music.kw import kw
from pet.music.qq import qq
from pet.music.qqjt import qqjt
from pet.music.ui_login import Ui_Dialog
from pet.music.ui_music_player import Ui_MainWindow
current_path, _ = os.path.split(os.path.realpath(__file__))


async def download(url, path):
    async with request('GET', url) as res:
        async with aiofile.open_async(path, 'wb') as f:
            await f.write(await res.read())


async def download_img(url, path):
    async with request('GET', url) as res:
        fp = BytesIO(await res.read())
        img = aiofile.AIOWrapper(Image.open(fp))
        img = aiofile.AIOWrapper(await img.resize((300, 300), Image.ANTIALIAS))
        img = aiofile.AIOWrapper(await img.convert('RGB'))
        await img.save(path)


class MyDict(dict):
    """docstring for MyDict."""

    def __init__(self, slm):
        super(MyDict, self).__init__()
        self.slm = slm

    def __setitem__(self, k, v):
        super(MyDict, self).__setitem__(k, v)
        self.slm.setStringList(self.keys())

    def pop(self, k):
        v = super(MyDict, self).pop(k)
        self.slm.setStringList(self.keys())
        return v

    def clear(self):
        super(MyDict, self).clear()
        self.slm.setStringList([])

    def update(self, key_map: dict):
        super(MyDict, self).update(key_map)
        self.slm.setStringList(self.keys())


class SongLabel(QLabel):
    """docstring for SongLabel."""

    doubleclicked = Signal()

    def __init__(self, *args, **kwargs):
        super(SongLabel, self).__init__(*args, **kwargs)

    def mouseDoubleClickEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.doubleclicked.emit()


class MusicApp(object):
    """docstring for MusicApp."""

    DATA_PATH = f'{current_path}\\data'
    IMG_PATH = os.path.join(DATA_PATH, 'images')
    DOWNLOAD_PATH = os.path.join(DATA_PATH, 'musics')
    SAVE_PATH = os.path.join(DATA_PATH, 'listen')
    MAP = {
        '咪咕': 'mg',
        '网易云': 'wyy',
        'QQ': 'qq',
        '千千': 'qqjt',
        '酷我': 'kw',
        '酷狗': 'kg'
    }

    def __init__(self):
        super(MusicApp, self).__init__()
        if not os.path.exists(self.DATA_PATH):
            os.mkdir(self.DATA_PATH)
            os.mkdir(self.IMG_PATH)
        elif not os.path.exists(self.IMG_PATH):
            os.mkdir(self.IMG_PATH)
        if not os.path.exists(self.DOWNLOAD_PATH):
            os.mkdir(self.DOWNLOAD_PATH)
        self.song_length = 'oo'
        self.voice = 33
        self.is_mute = False
        self.mode_icon_list = []
        self.listen_slm = QStringListModel()
        self.download_slm = QStringListModel()
        self.initUi()
        self.musicer = {
            'wyy': wyy.Musicer(),
            'kg': kg.Musicer(),
            'mg': mg.Musicer(),
            'qq': qq.Musicer(),
            'qqjt': qqjt.Musicer(),
            'kw': kw.Musicer()
        }
        self.music_player = QMediaPlayer(parent=self.ui)
        self.music_play_list = QMediaPlaylist(parent=self.ui)
        self.music_play_list.setPlaybackMode(QMediaPlaylist.Loop)
        self.music_play_list.currentIndexChanged.connect(self.media_list_index_change)
        self.music_player.durationChanged.connect(self.get_duration_length)
        self.music_player.positionChanged.connect(self.position_change)
        self.music_player.setVolume(self.voice)
        self.current_search = None
        self.current_musicer = None
        self.to_listen = MyDict(self.listen_slm)
        asyncio.create_task(self.load_listen_list())
        self.to_download = MyDict(self.download_slm)

    async def load_listen_list(self):
        if os.path.exists(self.SAVE_PATH):
            with open(self.SAVE_PATH, 'rb') as f:
                if key_map := await aiofile.AsyncFuncWrapper(pickle.load)(f):
                    self.to_listen.update(key_map)
            for _id in self.to_listen.values():
                self.music_play_list.addMedia(await self._get_mediacontent(_id))

    def init_login_dialog(self):
        app = self

        class LoginUi(QDialog, Ui_Dialog):
            """docstring for LoginUi."""

            def __init__(self, title):
                super(LoginUi, self).__init__()
                self.setupUi(self)
                self.verifywidget.hide()
                self._login_args = None
                self.setWindowModality(Qt.ApplicationModal)
                self.setWindowTitle(f'登录{title}音乐')
                self.numbers = {str(i) for i in range(10)}
                self.messagelabel.setAlignment(Qt.AlignCenter)
                self.messagelabel.setStyleSheet("color:red")

            @property
            def login_args(self):
                return self._login_args

            def write(self, login_id, password):
                if login_id is not None:
                    self.loginidlineEdit.setText(login_id)
                if password is not None:
                    self.passwordlineEdit.setText(password)

            def accept(self):
                message = ''
                verify_code = ''
                if not (login_id := self.loginidlineEdit.text()):
                    message = '账号不能为空'
                elif not set(login_id) <= self.numbers:
                    message = '账号不能包含数字以外的元素'
                elif not (password := self.passwordlineEdit.text()):
                    message = '密码不能为空'
                elif not (self.verifywidget.isHidden() or
                        (verify_code := self.verifylineEdit.text())):
                    message = '请输入验证码'
                if message:
                    self.messagelabel.setText(message)
                else:
                    self._login_args = {
                        'login_id': login_id,
                        'password': password,
                        'verify_code': verify_code,
                    }
                    super(LoginUi, self).accept()
        self.login_dialog = LoginUi

    def login(self, app=None, **login_args):
        def call_back(*args):
            if (e := login_task.exception()) is None:
                self.ui.statusBar().showMessage('登录成功！！！')
                asyncio.get_running_loop().call_later(
                    3, self.ui.statusBar().showMessage,
                    f'当前下载路径: {self.DOWNLOAD_PATH}')
            else:
                init_args = {}
                if isinstance(e, LoginIncompleteError):
                    QMessageBox.information(self.ui, '提示', '暂未实现该平台的登录功能')
                else:
                    if isinstance(e, LackLoginArgsError):
                        QMessageBox.information(self.ui, '提示', '未存在登录信息,请登录')
                    elif isinstance(e, VerifyError):
                        init_args.update(json.loads(str(e)))
                    else:
                        QMessageBox.warning(
                            self.ui, '警告', '\n'.join([str(e), '请尝试重新登陆']))
                        init_args['login_id'] = login_args.get('login_id')
                    self.open_login_dialog(title, **init_args)
        title = self.ui.musicercomboBox.currentText()
        if app is None:
            app = self.MAP[title]
        (login_task := asyncio.create_task(
            self.musicer[app].login(**login_args))).add_done_callback(call_back)
        return login_task

    def open_login_dialog(self, title=None, *, login_id=None, password=None):
        def call_back(*args):
            if login_task.exception() is None:
                asyncio.create_task(
                    musicer.reset_setting(**login_args))
        if title is None:
            title = self.ui.musicercomboBox.currentText()
        musicer = self.musicer[self.MAP[title]]
        dialog = self.login_dialog(title)
        dialog.write(login_id, password)
        if (verify_task := musicer.verify()) is not None:
            def show_verify_widget(*args):
                if (e := verify_task.exception()) is None:
                    (img := QPixmap()).loadFromData(
                        base64.b64decode(verify_task.result().encode()))
                    dialog.verifywidget.show()
                    dialog.verifyimglabel.setPixmap(img)
                else:
                    QMessageBox.warning(self.ui, '警告', str(e))
            verify_task.add_done_callback(show_verify_widget)
        dialog.exec_()
        if (login_args := dialog.login_args) is not None:
            (login_task := self.login(**login_args)).add_done_callback(call_back)

    def initUi(self):
        self.init_login_dialog()
        app = self

        class PlayerUi(QMainWindow, Ui_MainWindow):
            """docstring for PlayerUi."""

            def __init__(self):
                super(PlayerUi, self).__init__()
                self.setupUi(self)
                self.window_icon = app._get_icon(window_icon_py)
                self.setWindowIcon(self.window_icon)

            def closeEvent(self, event):
                asyncio.create_task(app.close())
                result = QMessageBox.question(self, '请确认', '是否确认关闭',
                                              QMessageBox.Yes | QMessageBox.No)
                if result == QMessageBox.Yes:
                    self.save()
                    event.accept()
                else:
                    event.ignore()

            @staticmethod
            def save():
                with open(app.SAVE_PATH, 'wb') as f:
                    pickle.dump({**app.to_listen}, f)

        # self.ui = QUiLoader().load('ui_music_player.ui')
        self.ui = PlayerUi()
        self.ui.searchButton.clicked.connect(self.search)
        self.ui.musicercomboBox.addItems(self.MAP.keys())
        self.layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(self.layout)
        self.download_menu = QMenu()
        self.login_menu = QMenu()
        self.change_download_path_action = QAction(
            '更换下载路径', triggered=self.change_download_path)
        self.switch_account_action = QAction(
            '切换账号', triggered=self.open_login_dialog)
        self.download_menu.addAction(self.change_download_path_action)
        self.login_menu.addAction(self.switch_account_action)
        self.ui.resultscrollArea.setWidget(widget)
        self.ui.voicepushButton.clicked.connect(self.mute)
        self.ui.playpushButton.clicked.connect(self.play_pause)
        self.ui.playpushButton.setEnabled(False)
        self.ui.lastpushButton.clicked.connect(self.last_song)
        self.ui.lastpushButton.setEnabled(False)
        self.ui.nextpushButton.clicked.connect(self.next_song)
        self.ui.nextpushButton.setEnabled(False)
        self.ui.modepushButton.clicked.connect(self.change_mode())
        self.ui.modepushButton.setEnabled(False)
        self.ui.downloadtoolButton.clicked.connect(self.download)
        self.ui.downloadtoolButton.setMenu(self.download_menu)
        self.ui.logintoolButton.clicked.connect(lambda: self.login())
        self.ui.logintoolButton.setMenu(self.login_menu)
        self.ui.hideandshowpushButton.clicked.connect(self.hide_and_show)
        self.ui.listenlistView.setModel(self.listen_slm)
        self.ui.listenlistView.doubleClicked.connect(self.list_play)
        self.ui.listenlistView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.listenlistView.customContextMenuRequested.connect(
            self.listen_listview_contextmenu)
        self.ui.downloadlistView.setModel(self.download_slm)
        self.ui.downloadlistView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.downloadlistView.customContextMenuRequested.connect(
            self.download_listview_contextmenu)
        self.ui.voicehorizontalSlider.setRange(0, 100)
        self.ui.voicehorizontalSlider.setValue(self.voice)
        self.ui.voicehorizontalSlider.valueChanged.connect(self.voice_change)
        self.ui.processhorizontalSlider.sliderMoved.connect(self.process_change)
        self.ui.action_bat.triggered.connect(self.get_bat_file())
        self.ui.processhorizontalSlider.setEnabled(False)
        self.ui.downloadgroupBox.hide()
        self.ui.resize(967, 686)
        self.add_style_task = asyncio.create_task(self.add_style())

    @Slot()
    def get_bat_file(self):
        async def write():
            async with aiofile.open_async(
                    path := os.path.join(
                        os.path.expanduser('~'), 'Desktop', 'music_player.bat'), 'w') as f:
                pass
            async with aiofile.open_async(path, 'a') as f:
                await f.write('@echo off\nif "%1" == "233" goto begin\n')
                await f.write(r'mshta vbscript:createobject("wscript.shell").run("%~nx0 233",0)(window.close)&&exit')
                await f.write(f'\n:begin\npython {os.path.abspath(sys.argv[0])} music_player')

        def connect_func():
            asyncio.create_task(write())
        return connect_func

    async def add_style(self):
        def add_style_func():
            self.ui.statusBar().showMessage(
                f'当前下载路径: {self.DOWNLOAD_PATH}')
            self.ui.searchButton.setToolTip('<b>点击此按钮进行搜索</b>')
            self.ui.voicepushButton.setToolTip('<b>音量</b>')
            self.ui.playpushButton.setToolTip('<b>播放</b>')
            self.ui.nextpushButton.setToolTip('<b>下一曲</b>')
            self.ui.lastpushButton.setToolTip('<b>上一曲</b>')
            self.ui.modepushButton.setToolTip('<b>列表循环</b>')
            self.ui.downloadtoolButton.setToolTip('<b>下载</b>')
            self.ui.logintoolButton.setToolTip('<b>登录</b>')
            self.ui.hideandshowpushButton.setToolTip('<b>展开下载列表</b>')
            self.ui.voicehorizontalSlider.setToolTip(f'<b>{self.voice}</b>')
            self.add_icon = self._get_icon(add_py)
            self.add_music_icon = self._get_icon(add_music_py)
            self.play_icon = self._get_icon(play_py)
            self.pause_icon = self._get_icon(pause_py)
            self.sound_on_icon = self._get_icon(sound_on_py)
            self.sound_off_icon = self._get_icon(sound_off_py)
            self.mode_icon_list.extend([
                list_loop_icon := self._get_icon(list_loop_py),
                self._get_icon(random_py),
                self._get_icon(item_loop_py)])
            self.hide_icon = self._get_icon(hide_py)
            self.show_icon = self._get_icon(show_py)
            self.export_icon = self._get_icon(export_py)
            self.ui.playpushButton.setIcon(self.play_icon)
            self.ui.voicepushButton.setIcon(self.sound_on_icon)
            self.ui.hideandshowpushButton.setIcon(self.hide_icon)
            self.ui.searchButton.setIcon(self._get_icon(search_py))
            self.ui.nextpushButton.setIcon(self._get_icon(next_py))
            self.ui.lastpushButton.setIcon(self._get_icon(previous_py))
            self.ui.modepushButton.setIcon(list_loop_icon)
            self.ui.downloadtoolButton.setIcon(self._get_icon(download_py))
            self.ui.logintoolButton.setIcon(self._get_icon(login_py))
            self.ui.action_bat.setIcon(self.export_icon)
            self.change_download_path_action.setIcon(self._get_icon(download_path_setting_py))
            self.switch_account_action.setIcon(self._get_icon(switch_py))
        await asyncio.get_running_loop().run_in_executor(None, add_style_func)

    def listen_listview_contextmenu(self, pos):
        # pos = self.ui.listenlistView.viewport().mapFromGlobal(pos)
        popmenu = QMenu()
        remove_action = QAction('移出播放列表', triggered=self.remove_listen_item)
        add_to_download_action = QAction('添加至下载列表', triggered=self.listen_to_download)
        clear_action = QAction('清空播放列表', triggered=self.clear_listen_items)
        if self.ui.listenlistView.indexAt(pos).isValid():
            popmenu.addAction(remove_action)
            popmenu.addAction(add_to_download_action)
        popmenu.addAction(clear_action)
        popmenu.exec_(self.ui.listenlistView.mapToGlobal(pos))

    @Slot()
    def listen_to_download(self):
        index = self.ui.listenlistView.currentIndex()
        song_info = index.data()
        self.to_download[song_info] = self.to_listen[song_info]

    def download_listview_contextmenu(self, pos):
        popmenu = QMenu()
        remove_action = QAction('移出下载列表', triggered=self.remove_download_item)
        clear_action = QAction('清空下载列表', triggered=self.clear_download_items)
        if self.ui.downloadlistView.indexAt(pos).isValid():
            popmenu.addAction(remove_action)
        popmenu.addAction(clear_action)
        popmenu.exec_(self.ui.downloadlistView.mapToGlobal(pos))

    @Slot(int)
    def media_list_index_change(self, index):
        qmodel_index = self.listen_slm.index(index)
        self.ui.listenlistView.setCurrentIndex(qmodel_index)
        self.ui.processhorizontalSlider.setToolTip(f'<b>{qmodel_index.data()}</b>')

    @Slot()
    def remove_listen_item(self):
        index = self.ui.listenlistView.currentIndex()
        self.to_listen.pop(index.data())
        self.music_play_list.removeMedia(index.row())

    @Slot()
    def remove_download_item(self):
        index = self.ui.downloadlistView.currentIndex()
        self.to_download.pop(index.data())

    @Slot()
    def clear_listen_items(self):
        if self.to_listen:
            self.to_listen.clear()
            self.music_play_list.clear()
            self.ui.processhorizontalSlider.setEnabled(False)
            self.ui.lastpushButton.setEnabled(False)
            self.ui.nextpushButton.setEnabled(False)
            self.ui.modepushButton.setEnabled(False)
            self.ui.playpushButton.setEnabled(False)
            self.ui.playpushButton.setIcon(self.play_icon)

    @Slot()
    def clear_download_items(self):
        if self.to_download:
            self.to_download.clear()

    def change_mode(self):
        mode_list = [QMediaPlaylist.Loop,
                     QMediaPlaylist.Random,
                     QMediaPlaylist.CurrentItemInLoop]
        tips = ['<b>列表循环</b>', '<b>随机播放</b>', '<b>单曲循环</b>']
        push_times = 0

        @Slot()
        def connect_func():
            nonlocal push_times
            push_times += 1
            index = push_times % 3
            self.ui.modepushButton.setIcon(self.mode_icon_list[index])
            self.ui.modepushButton.setToolTip(tips[index])
            self.music_play_list.setPlaybackMode(mode_list[index])
        return connect_func

    @staticmethod
    def _get_icon(b64str: str) -> QIcon:
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(b64str.encode()))
        return QIcon(pixmap)

    @staticmethod
    def format_time(time: int) -> str:
        seconds = time / 1000
        return f'{int(seconds // 60)}:{int(seconds % 60)}'

    def clear_layout(self):
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            self.layout.removeItem(item)

    @Slot()
    def search(self):
        song = self.ui.inputlineEdit.text()
        if song.isspace():
            self.ui.inputlineEdit.clear()
        else:
            song = song.strip()
            musicer = self.ui.musicercomboBox.currentText()
            if song:
                if song != self.current_search or musicer != self.current_musicer:
                    self.clear_layout()
                    asyncio.create_task(self.search_song(song, self.MAP[musicer]))
                    self.current_search = song
                    self.current_musicer = musicer

    @Slot()
    def hide_and_show(self):
        if self.ui.downloadgroupBox.isHidden():
            self.ui.downloadgroupBox.show()
            self.ui.hideandshowpushButton.setIcon(self.show_icon)
            self.ui.hideandshowpushButton.setToolTip('<b>收起下载列表</b>')
        else:
            self.ui.downloadgroupBox.hide()
            self.ui.hideandshowpushButton.setIcon(self.hide_icon)
            self.ui.hideandshowpushButton.setToolTip('<b>展开下载列表</b>')
            asyncio.get_running_loop().call_later(0.1, self.ui.resize, 967, 686)

    @Slot(int)
    def get_duration_length(self, song_length):
        if song_length:
            self.ui.processhorizontalSlider.setRange(0, song_length)
            self.song_length = self.format_time(song_length)
        else:
            self.ui.timelabel.setText('--/--')

    @Slot()
    def position_change(self, pos):
        if (current_pos := self.format_time(pos)) != self.song_length:
            if not self.ui.processhorizontalSlider.isEnabled():
                self.ui.processhorizontalSlider.setEnabled(True)
                self.ui.playpushButton.setIcon(self.pause_icon)
                self.ui.playpushButton.setToolTip('<b>暂停</b>')
            if not self.ui.playpushButton.isEnabled():
                self.ui.playpushButton.setEnabled(True)
            self.ui.processhorizontalSlider.setValue(pos)
            self.ui.timelabel.setText(f'{current_pos}/{self.song_length}')
        else:
            self.ui.processhorizontalSlider.setValue(0)
            self.ui.processhorizontalSlider.setEnabled(False)
            self.ui.processhorizontalSlider.setToolTip('')
            self.ui.timelabel.setText('--/--')
            self.ui.playpushButton.setEnabled(False)
            self.ui.playpushButton.setIcon(self.play_icon)
            self.ui.playpushButton.setToolTip('<b>播放</b>')

    @Slot()
    def download(self):
        if self.to_download:
            for song_info in self.to_download.keys():
                _id = self.to_download[song_info]
                if not os.path.exists(
                        path := os.path.join(
                            self.DOWNLOAD_PATH, f'{"_".join([*_id.id, _id.app])}.m4a')):
                    asyncio.create_task(self.download_music(song_info, path))
                else:
                    asyncio.get_running_loop().call_later(
                        0.1, self.to_download.pop, song_info)
        else:
            QMessageBox.warning(self.ui, '警告', '没有可下载的歌曲')

    def add_listen(self, song_info, _id):
        async def add_func():
            if _id not in self.to_listen.values():
                self.music_play_list.addMedia(await self._get_mediacontent(_id))
                self.to_listen[song_info] = _id
            # print('listen:', self.to_listen)

        @Slot()
        def connect_func():
            asyncio.create_task(add_func())
        return connect_func

    def add_download(self, song_info, _id):
        @Slot()
        def connect_func():
            self.to_download[song_info] = _id
            # print('download:', self.to_download)
        return connect_func

    @Slot()
    def mute(self):
        if self.is_mute:
            self.is_mute = False
            self.ui.voicehorizontalSlider.setValue(self.voice)
            self.ui.voicepushButton.setIcon(self.sound_on_icon)
            self.music_player.setVolume(self.voice)
        else:
            self.is_mute = True
            self.ui.voicehorizontalSlider.setValue(0)
            self.ui.voicepushButton.setIcon(self.sound_off_icon)
            self.music_player.setVolume(0)

    @Slot(int)
    def voice_change(self, value):
        self.music_player.setVolume(value)
        self.ui.voicehorizontalSlider.setToolTip(f'<b>{value}</b>')
        if not self.is_mute:
            self.voice = value

    @Slot(int)
    def process_change(self, value):
        self.music_player.setPosition(value)

    @Slot()
    def change_download_path(self):
        file_open = QFileDialog()
        # file_open.setWindowFlags(Qt.Tool)
        file_open.setFileMode(QFileDialog.Directory)
        if file_open.exec_():
            path, *_ = file_open.selectedFiles()
            self.DOWNLOAD_PATH = path
            self.ui.statusBar().showMessage(
                f'current download path: {self.DOWNLOAD_PATH}')

    async def _get_mediacontent(self, _id):
        if os.path.exists(
                path := os.path.join(self.DOWNLOAD_PATH, f'{"_".join([*_id.id, _id.app])}.m4a')):
            mediacontent = QMediaContent(QUrl.fromLocalFile(path))
        else:
            url = await self._get_url(_id)
            mediacontent = QMediaContent(QUrl(url))
        return mediacontent

    def single_play(self, song_info, _id):
        async def play():
            self.music_player.setMedia(await self._get_mediacontent(_id))
            self.ui.playpushButton.setIcon(self.pause_icon)
            self.ui.playpushButton.setToolTip('<b>暂停</b>')
            self.ui.processhorizontalSlider.setToolTip(f'<b>{song_info}</b>')
            self.ui.lastpushButton.setEnabled(False)
            self.ui.nextpushButton.setEnabled(False)
            self.ui.modepushButton.setEnabled(False)
            self.music_player.play()

        @Slot()
        def connect_func():
            asyncio.create_task(play())
        return connect_func

    @Slot()
    def list_play(self, qmodel_list):
        index = qmodel_list.row()
        self.ui.playpushButton.setIcon(self.pause_icon)
        self.ui.playpushButton.setToolTip('<b>暂停</b>')
        self.music_player.setPlaylist(self.music_play_list)
        self.music_play_list.setCurrentIndex(index)
        self.music_player.play()
        self.ui.processhorizontalSlider.setToolTip(f'<b>{qmodel_list.data()}</b>')
        self.ui.lastpushButton.setEnabled(True)
        self.ui.nextpushButton.setEnabled(True)
        self.ui.modepushButton.setEnabled(True)

    @Slot()
    def last_song(self):
        self.music_play_list.previous()

    @Slot()
    def play_pause(self):
        if self.ui.processhorizontalSlider.isEnabled():
            if self.music_player.state() - 1:
                self.music_player.play()
                self.ui.playpushButton.setIcon(self.pause_icon)
                self.ui.playpushButton.setToolTip('<b>暂停</b>')
            else:
                self.music_player.pause()
                self.ui.playpushButton.setIcon(self.play_icon)
                self.ui.playpushButton.setToolTip('<b>播放</b>')

    @Slot()
    def next_song(self):
        self.music_play_list.next()

    async def search_song(self, song, musicer):
        try:
            songs_info = await self.musicer[musicer]._get_song_info(song)
        except AssertionError as e:
            QMessageBox.critical(self.ui, '错误', str(e))
            self.current_search = None
            self.current_musicer = None
            self.ui.inputlineEdit.clear()
        else:
            for song_info in songs_info:
                asyncio.create_task(self.show_label(song_info))

    async def show_label(self, song_info):
        if isinstance(song_info, Coroutine):
            song_info = await song_info
        item = QWidget()
        item.setLayout(hbox := QHBoxLayout())
        hbox.addWidget(add_music_button := QToolButton())
        hbox.addWidget(add_button := QToolButton())
        hbox.addWidget(song_label := SongLabel(song_info.text))
        add_music_button.clicked.connect(self.add_listen(song_info.text, song_info.id))
        add_button.clicked.connect(self.add_download(song_info.text, song_info.id))
        song_label.doubleclicked.connect(self.single_play(song_info.text, song_info.id))
        add_music_button.setIcon(self.add_music_icon)
        add_button.setIcon(self.add_icon)
        add_music_button.setAutoRaise(True)
        add_button.setAutoRaise(True)
        add_music_button.setToolTip('<b>添加至播放列表</b>')
        add_button.setToolTip('<b>添加至下载列表</b>')
        self.layout.addWidget(item)
        if song_info.pic is not None:
            if not os.path.exists(
                    path := os.path.join(
                        self.IMG_PATH, song_info.pic)):
                asyncio.create_task(
                    download_img(song_info.pic_url, path))
            song_label.setToolTip(f'<img src={path} >')

    async def download_music(self, song_info, path):
        try:
            url = await self._get_url(self.to_download[song_info])
            await download(url, path)
        finally:
            self.to_download.pop(song_info)

    async def _get_url(self, _id):
        try:
            url = await self.musicer[_id.app]._get_song_url(*_id.id)
        except AssertionError as e:
            song = ''
            if _id in self.to_download.values():
                song = [song_info
                        for song_info, id_ in self.to_download.items()
                        if id_ == _id][0]
            QMessageBox.critical(
                self.ui, '错误',
                f'{song}: {str(e)}' if song else str(e))
            asyncio.current_task().cancel()
            await asyncio.sleep(0)
        except CookieInvalidError as e:
            self.ui.statusBar().showMessage(
                f'当前cookie已失效,正在重新登录......')
            self.login(_id.app)
            asyncio.current_task().cancel()
            await asyncio.sleep(0)
        else:
            if url.vip:
                QMessageBox.information(self.ui, '提示', 'VIP歌曲,仅提供试听')
            return url.url

    def show(self):
        self.ui.show()

    async def close(self):
        for musicer in self.musicer.values():
            await musicer.close()

def run():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    with loop:
        music_app = MusicApp()
        music_app.show()
        loop.run_forever()


if __name__ == '__main__':
    run()
