# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-01-21 18:36:13
# @Last Modified by:   None
# @Last Modified time: 2022-02-13 21:51:10
from io import BytesIO
from collections.abc import Coroutine
import os
import sys
if __name__ == '__main__':
    sys.path.append('..')
import json
import base64
import asyncio

from hzy.aiofile import aiofile
from aiohttp import request
from PIL import Image
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QMessageBox
from PySide2.QtWidgets import QFileDialog
from PySide2.QtWidgets import QToolTip
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QToolButton
from PySide2.QtWidgets import QMenu
from PySide2.QtWidgets import QAction
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtMultimedia import QMediaContent
from PySide2.QtMultimedia import QMediaPlaylist
from PySide2.QtCore import QModelIndex
from PySide2.QtCore import Qt
from PySide2.QtCore import QUrl
from PySide2.QtCore import Slot
from PySide2.QtCore import Signal
from PySide2.QtCore import QStringListModel
from PySide2.QtGui import QIcon
from PySide2.QtGui import QPixmap
from PySide2.QtUiTools import QUiLoader
from qasync import QEventLoop

from .model import CookieInvalidError
from .pictures import *
from .wyy import wyy
from .kg import kg
from .mg import mg
from .ui_music_player import Ui_MainWindow


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
    SAVE_PATH = os.path.join(DATA_PATH, 'listen.dump')
    MAP = {'网易云': 'wyy', '酷狗': 'kg', '咪咕': 'mg'}

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
        self.musicer = {'wyy': wyy.Musicer(), 'kg': kg.Musicer(), 'mg': mg.Musicer()}
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
            async with aiofile.open_async(self.SAVE_PATH, 'r') as f:
                dump = await f.read()
                kg_id_map_dump, to_listen_dump = dump.split('>^<')
                if to_listen_dump:
                    self.musicer['kg']._id_map.update(
                        await aiofile.AsyncFuncWrapper(json.loads)(kg_id_map_dump))
                    for line in to_listen_dump.split('\n'):
                        song_info, _id = line.split('^3^')
                        _id = tuple(_id.split('^_^'))
                        self.music_play_list.addMedia(await self._get_mediacontent(_id))
                        self.to_listen[song_info] = _id

    def initUi(self):
        app = self

        class PlayerUi(QMainWindow, Ui_MainWindow):
            """docstring for PlayerUi."""

            def __init__(self):
                super(PlayerUi, self).__init__()
                self.setupUi(self)
                self.window_icon = app._get_icon(window_icon_py)
                self.setWindowIcon(self.window_icon)

            def closeEvent(self, event):
                result = QMessageBox.question(self, '请确认', '是否确认关闭',
                                              QMessageBox.Yes | QMessageBox.No)
                if result == QMessageBox.Yes:
                    asyncio.create_task(app.close())
                    self.save()
                    event.accept()
                else:
                    event.ignore()

            @staticmethod
            def save():
                to_listen_dump = '\n'.join(
                    [f'{k}^3^{"^_^".join(v)}'
                     for k, v in app.to_listen.items()])
                kg_id_map_dump = json.dumps({v[0]: app.musicer['kg']._id_map[v[0]]
                                             for _, v in app.to_listen.items()
                                             if v[1] == 'kg'})
                with open(app.SAVE_PATH, 'w') as f:
                    f.write('>^<'.join([kg_id_map_dump, to_listen_dump]))

        # self.ui = QUiLoader().load('ui_music_player.ui')
        self.ui = PlayerUi()
        self.ui.searchButton.clicked.connect(self.search)
        self.layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(self.layout)
        self.menu = QMenu()
        self.change_download_path_action = QAction(
            '改变下载路径', triggered=self.change_download_path)
        self.menu.addAction(self.change_download_path_action)
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
        self.ui.downloadtoolButton.setMenu(self.menu)
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
        asyncio.create_task(self.add_style())

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
                await f.write(f'\n:begin\npython {__file__}')

        def connect_func():
            asyncio.create_task(write())
        return connect_func

    async def add_style(self):
        def add_style_func():
            self.ui.statusBar().showMessage(
                f'current download path: {self.DOWNLOAD_PATH}')
            self.ui.searchButton.setToolTip('<b>点击此按钮进行搜索</b>')
            self.ui.voicepushButton.setToolTip('<b>音量</b>')
            self.ui.playpushButton.setToolTip('<b>播放</b>')
            self.ui.nextpushButton.setToolTip('<b>下一曲</b>')
            self.ui.lastpushButton.setToolTip('<b>上一曲</b>')
            self.ui.modepushButton.setToolTip('<b>列表循环</b>')
            self.ui.downloadtoolButton.setToolTip('<b>下载</b>')
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
            self.ui.playpushButton.setIcon(self.play_icon)
            self.ui.voicepushButton.setIcon(self.sound_on_icon)
            self.ui.hideandshowpushButton.setIcon(self.hide_icon)
            self.ui.searchButton.setIcon(self._get_icon(search_py))
            self.ui.nextpushButton.setIcon(self._get_icon(next_py))
            self.ui.lastpushButton.setIcon(self._get_icon(previous_py))
            self.ui.modepushButton.setIcon(list_loop_icon)
            self.ui.downloadtoolButton.setIcon(self._get_icon(download_py))
            self.change_download_path_action.setIcon(self._get_icon(download_path_setting_py))
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
                if not os.path.exists(
                        path := os.path.join(
                            self.DOWNLOAD_PATH, f'{"_".join(self.to_download[song_info])}.m4a')):
                    asyncio.create_task(self.download_music(song_info, path))
                else:
                    asyncio.get_running_loop().call_later(
                        0.1, self.to_download.pop, song_info)
        else:
            QMessageBox.warning(self.ui, 'warning', 'no song could be downloaded')

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
                path := os.path.join(self.DOWNLOAD_PATH, f'{_id}.m4a')):
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
        # if not self.music_play_list.currentIndex():
        #     self.music_play_list.setCurrentIndex(
        #         self.music_play_list.mediaCount() - 1)
        # else:
        #     self.music_play_list.previous()
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
        # if self.music_play_list.currentIndex() == self.music_play_list.mediaCount() - 1:
        #     self.music_play_list.setCurrentIndex(0)
        # else:
        #     self.music_play_list.next()
        self.music_play_list.next()

    async def search_song(self, song, musicer):
        try:
            songs_info = await self.musicer[musicer]._get_song_info(song)
        except AssertionError as e:
            QMessageBox.critical(self.ui, 'error', str(e))
            self.ui.inputlineEdit.clear()
        else:
            for song_info in songs_info:
                asyncio.create_task(self.show_label(song_info))
                # item = QWidget()
                # item.setLayout(hbox := QHBoxLayout())
                # hbox.addWidget(add_music_button := QToolButton())
                # hbox.addWidget(add_button := QToolButton())
                # hbox.addWidget(song_label := SongLabel(song_info.text))
                # add_music_button.clicked.connect(self.add_listen(song_info.text, song_info.id))
                # add_button.clicked.connect(self.add_download(song_info.text, song_info.id))
                # song_label.doubleclicked.connect(self.single_play(song_info.text, song_info.id))
                # add_music_button.setIcon(self.add_music_icon)
                # add_button.setIcon(self.add_icon)
                # add_music_button.setAutoRaise(True)
                # add_button.setAutoRaise(True)
                # add_music_button.setToolTip('<b>添加至播放列表</b>')
                # add_button.setToolTip('<b>添加至下载列表</b>')
                # self.layout.addWidget(item)
                # if not os.path.exists(
                #         path := os.path.join(
                #             self.IMG_PATH, song_info.pic)):
                #     asyncio.create_task(
                #         download_img(song_info.pic_url, path))
                # song_label.setToolTip(f'<img src={path} >')
                # await asyncio.sleep(0)

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
            url = await self.musicer[_id[1]]._get_song_url(_id[0])
        except AssertionError as e:
            asyncio.current_task().cancel()
            try:
                await asyncio.sleep(0)
            except asyncio.CancelledError:
                song = ''
                if _id in self.to_download.values():
                    song = [song_info
                            for song_info, id_ in self.to_download.items()
                            if id_ == _id][0]
                QMessageBox.critical(
                    self.ui, 'error',
                    f'{song}: {str(e)}' if song else str(e))
                raise
        except CookieInvalidError as e:
            self.ui.statusBar().showMessage(
                f'当前cookie已失效,正在重新登录......')
            task = asyncio.create_task(self.musicer[_id[1]].login())
            task.add_done_callback(lambda x: self.ui.statusBar().showMessage('登录成功！！！'))
            asyncio.get_running_loop().call_later(
                3, self.ui.statusBar().showMessage, f'current download path: {self.DOWNLOAD_PATH}')
            asyncio.current_task().cancel()
            await asyncio.sleep(0)
        else:
            return url

    def show(self):
        self.ui.show()

    async def close(self):
        for musicer in self.musicer.values():
            await musicer.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    with loop:
        music_app = MusicApp()
        music_app.show()
        loop.run_forever()
