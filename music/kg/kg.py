# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-02-04 16:17:25
# @Last Modified by:   None
# @Last Modified time: 2022-02-19 20:29:46
import os
current_path, _ = os.path.split(os.path.realpath(__file__))
if __name__ == '__main__':
    import sys
    sys.path.append(os.path.join(current_path, '..'))
    sys.path.append(os.path.join(current_path, '../..'))

from urllib.parse import quote
import os
import re
import time
import json
import hashlib
import asyncio

from hzy import fake_ua
try:
    from model import SongInfo
    from model import SongUrl
    from model import SongID
    from model import BaseMusicer
except ImportError:
    from ..model import SongInfo
    from ..model import SongUrl
    from ..model import SongID
    from ..model import BaseMusicer


ua = fake_ua.UserAgent()
spare_cookie = 'kg_mid=f5cc0826aa228ba869e92dc2f7501c9c; kg_dfid=1JdqSp27zyLa3wraVj18xXYA; Hm_lvt_aedee6983d4cfc62f509129360d6bb3d=1642742193,1642742812,1643949951; kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e; kg_mid_temp=f5cc0826aa228ba869e92dc2f7501c9c; KuGoo=KugooID=943077582&KugooPwd=61698FFE640EB1FAB166F74963062A4E&NickName=%u0033%u0033%u662f%u0073%u0074%u0075%u0070%u0069%u0064%u7684%u5973%u670b%u53cb&Pic=http://imge.kugou.com/kugouicon/165/20211207/20211207190111627338.jpg&RegState=1&RegFrom=&t=1d8ad00b0dedb733bed729be875518669c98f5ab075e95cf334daffb9b39491b&t_ts=1643964933&t_key=&a_id=1014&ct=1643964933&UserName=%u006b%u0067%u006f%u0070%u0065%u006e%u0039%u0034%u0033%u0030%u0037%u0037%u0035%u0038%u0032; KugooID=943077582; t=1d8ad00b0dedb733bed729be875518669c98f5ab075e95cf334daffb9b39491b; a_id=1014; UserName=%u006b%u0067%u006f%u0070%u0065%u006e%u0039%u0034%u0033%u0030%u0037%u0037%u0035%u0038%u0032; mid=f5cc0826aa228ba869e92dc2f7501c9c; dfid=1JdqSp27zyLa3wraVj18xXYA; Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d=1643964943'


class Musicer(BaseMusicer):
    """docstring for Musicer."""

    SEARCH_URL = 'https://complexsearch.kugou.com/v2/search/song?callback=callback123&keyword={song}&page=1&pagesize=20&bitrate=0&isfuzzy=0&tag=em&inputtype=0&platform=WebFilter&userid=943077582&clientver=2000&iscorrection=1&privilege_filter=0&token=1d8ad00b0dedb733bed729be875518669c98f5ab075e95cf334daffb9b39491b&srcappid=2919&clienttime={time}&mid={time}&uuid={time}&dfid=-&signature={signature}'
    SONG_URL = 'https://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback=jQuery19103812022462601341_1644030495674&hash={filehash}&dfid=1JdqSp27zyLa3wraVj18xXYA&appid=1014&mid=f5cc0826aa228ba869e92dc2f7501c9c&platid=4&album_id={album_id}&_=1644030495675'
    STR = 'NVPh5oo715z5DIWAeQlhMDsWXXQV4hwtbitrate=0callback=callback123clienttime={time}clientver=2000dfid=-inputtype=0iscorrection=1isfuzzy=0keyword={song}mid={time}page=1pagesize=20platform=WebFilterprivilege_filter=0srcappid=2919tag=emtoken=1d8ad00b0dedb733bed729be875518669c98f5ab075e95cf334daffb9b39491buserid=943077582uuid={time}NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt'

    def __init__(self):
        super(Musicer, self).__init__(
            current_path=current_path, cookie=spare_cookie)
        self.headers['referer'] = 'https://www.kugou.com/'
        self.match = re.compile('.*?\(([\\s\\S]*)\)')
        self._id_map = {}

    async def _get_song_info(self, song):
        self.headers['user-agent'] = ua.get_ua()
        time_stamp = int(time.time() * 1000)
        signature = hashlib.md5(
            self.STR.format(time=time_stamp, song=song).encode()).hexdigest().upper()
        res = await self.session.get(
            self.SEARCH_URL.format(
                time=time_stamp, song=quote(song), signature=signature),
            headers=self.headers)
        assert (status := res.status) == 200, f'response: {status}'
        result = await res.text()
        result_dict_str = self.match.match(result).group(1)
        result_dict = json.loads(result_dict_str)
        assert not (error_msg := result_dict['error_msg']), error_msg
        songs = result_dict['data']['lists']
        return [self._info_request(song['AlbumID'], song['FileHash'])
                for song in songs]

    async def _info_request(
            self, album_id: str, filehash: str) -> SongInfo:
        data = await self._request(album_id, filehash)
        # data['lyrics'] 歌词
        self._id_map[album_id] = SongUrl(data['play_url'], bool(data.get('trans_param')))
        return SongInfo(
            f'酷狗: {data["song_name"]}-->{data["author_name"]}-->《{data["album_name"]}》',
            SongID((str(album_id), filehash), 'kg'),
            os.path.split(pic_url := data["img"])[1],
            pic_url)

    async def _request(
            self, album_id: str, filehash: str) -> dict:
        self.headers['user-agent'] = ua.get_ua()
        res = await self.session.get(
            self.SONG_URL.format(filehash=filehash, album_id=album_id),
            headers=self.headers)
        assert (status := res.status) == 200, f'response: {status}'
        result = await res.text()
        result_dict_str = self.match.match(result).group(1)
        result_dict = json.loads(result_dict_str)
        assert not result_dict['err_code'], f'error during getting song url'
        data = result_dict['data']
        return data

    async def _get_song_url(self, album_id: str, filehash: str):
        if  (url := self._id_map.get(str(album_id))) is None:
            data = await self._request(album_id, filehash)
            url = SongUrl(data['play_url'], bool(data.get('trans_param')))
        return url
