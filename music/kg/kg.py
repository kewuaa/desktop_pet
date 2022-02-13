# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-02-04 16:17:25
# @Last Modified by:   None
# @Last Modified time: 2022-02-13 21:47:49
from urllib.parse import quote
import os
import re
import time
import json
import asyncio


from hzy import fake_ua
from ..model import SongInfo
from ..model import BaseMusicer
from .cookie import cookie
from .js_code import kg_js


current_path, _ = os.path.split(os.path.realpath(__file__))
ua = fake_ua.UserAgent()


class Musicer(BaseMusicer):
    """docstring for Musicer."""

    SEARCH_URL = 'https://complexsearch.kugou.com/v2/search/song?callback=callback123&keyword={song}&page=1&pagesize=30&bitrate=0&isfuzzy=0&tag=em&inputtype=0&platform=WebFilter&userid=943077582&clientver=2000&iscorrection=1&privilege_filter=0&token=1d8ad00b0dedb733bed729be875518669c98f5ab075e95cf334daffb9b39491b&srcappid=2919&clienttime={time}&mid={time}&uuid={time}&dfid=-&signature={signature}'
    SONG_URL = 'https://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback=jQuery19103812022462601341_1644030495674&hash={filehash}&dfid=1JdqSp27zyLa3wraVj18xXYA&appid=1014&mid=f5cc0826aa228ba869e92dc2f7501c9c&platid=4&album_id={album_id}&_=1644030495675'
    HEADERS = {
        'user-agent': '',
        'cookie': cookie,
        'referer': 'https://www.kugou.com/',
    }
    CMD = 'node {path} {encseckey}'
    STR = 'NVPh5oo715z5DIWAeQlhMDsWXXQV4hwtbitrate=0callback=callback123clienttime={time}clientver=2000dfid=-inputtype=0iscorrection=1isfuzzy=0keyword={song}mid={time}page=1pagesize=30platform=WebFilterprivilege_filter=0srcappid=2919tag=emtoken=1d8ad00b0dedb733bed729be875518669c98f5ab075e95cf334daffb9b39491buserid=943077582uuid={time}NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt'

    def __init__(self):
        super(Musicer, self).__init__(
            js=kg_js, current_path=current_path, name=__name__)
        self.match = re.compile('.*?\(([\\s\\S]*)\)')
        self._id_map = {}

    async def _get_song_info(self, song):
        self.HEADERS['user-agent'] = ua.get_ua()
        time_stamp = int(time.time() * 1000)
        signature = await self._get_params(
            self.STR.format(time=time_stamp, song=song))
        res = await self.session.get(
            self.SEARCH_URL.format(
                time=time_stamp, song=quote(song), signature=signature),
            headers=self.HEADERS)
        assert (status := res.status) == 200, f'response: {status}'
        result = await res.text()
        result_dict_str = self.match.match(result).group(1)
        result_dict = json.loads(result_dict_str)
        assert not (error := result_dict['error_msg']),\
            f'error during getting song hash: {error}'
        songs = result_dict['data']['lists']
        return [self._update_id_map(song['FileHash'], song['AlbumID'])
                for song in songs]

    async def _update_id_map(
            self, filehash: str, album_id: str) -> SongInfo:
        self.HEADERS['user-agent'] = ua.get_ua()
        res = await self.session.get(
            self.SONG_URL.format(filehash=filehash, album_id=album_id),
            headers=self.HEADERS)
        assert (status := res.status) == 200, f'response: {status}'
        result = await res.text()
        result_dict_str = self.match.match(result).group(1)
        result_dict = json.loads(result_dict_str)
        assert not (error := result_dict['err_code']),\
            f'error during getting song url: {error}'
        data = result_dict['data']
        # data['lyrics'] 歌词
        self._id_map[album_id] = data.get('play_url')
        return SongInfo(
            f'酷狗: {data["song_name"]}-->{data["author_name"]}-->《{data["album_name"]}》',
            (str(album_id), 'kg'),
            os.path.split(pic_url := data["img"])[1],
            pic_url)

    async def _get_song_url(self, _id):
        assert (url := self._id_map.get(str(_id))) is not None, 'VIP或无版权歌曲，无法播放与下载'
        return url

    async def _get_params(self, encseckey):
        proc = await asyncio.create_subprocess_shell(
            self.CMD.format(path=self.js_path, encseckey=encseckey),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        assert not stderr, f'subprocess error: {stderr.decode("gbk")}'
        result = stdout.decode('utf-8').strip()
        return result
