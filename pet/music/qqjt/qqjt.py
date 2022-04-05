# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-02-17 09:15:39
# @Last Modified by:   None
# @Last Modified time: 2022-03-04 15:51:11
from urllib.parse import quote
import os
import time
import hashlib

from pet.music.musicer_model import SongInfo
from pet.music.musicer_model import SongUrl
from pet.music.musicer_model import SongID
from pet.music.musicer_model import BaseMusicer


current_path, _ = os.path.split(os.path.realpath(__file__))
spare_cookie = 'cuid=65bc7720-ecd3-a26b-eda1-719b8f34f2c9; Hm_lvt_d0ad46e4afeacf34cd12de4c9b553aa6=1645147447,1645147510,1645150160,1645150251; Hm_lpvt_d0ad46e4afeacf34cd12de4c9b553aa6=1645150251'


class Musicer(BaseMusicer):
    """docstring for Musicer."""

    SECRET = '0b50b02fd0d73a9c4c8c3a781c30845f'
    SEARCH_URL = 'https://music.taihe.com/v1/search?sign={sign}&word={keyword}&type=1&pageSize=20&appid=16073360&timestamp={time_stamp}'
    SEARCH_KEY = 'appid=16073360&pageSize=20&timestamp={time_stamp}&type=1&word={keyword}%s' % SECRET
    SONG_URL = 'https://music.taihe.com/v1/song/tracklink?sign={sign}&appid=16073360&TSID={TSID}&timestamp={time_stamp}'
    SONG_KEY = 'TSID={TSID}&appid=16073360&timestamp={time_stamp}%s' % SECRET

    def __init__(self):
        super(Musicer, self).__init__(current_path=current_path)
        self.headers['cookie'] = spare_cookie
        self.headers['referer'] = 'https://music.taihe.com/'
        self._login = self._update_cookie(self._login)

    async def _get_song_info(self, song):
        keyword = quote(song)
        time_stamp = int(time.time())
        sign = hashlib.md5(
            self.SEARCH_KEY.format(
                time_stamp=time_stamp, keyword=song).encode()).hexdigest()
        self._set_random_ua()
        res = await self.session.get(self.SEARCH_URL.format(
            sign=sign, keyword=keyword, time_stamp=time_stamp), headers=self.headers)
        assert (status := res.status) == 200, f'response: {status}'
        result_dict = await res.json(content_type=None)
        assert not (errmsg := result_dict['errmsg']), errmsg
        songs = result_dict['data']['typeTrack']
        return [SongInfo(f'千千静听: {song["title"]}-->{song["artist"][0]["name"]}-->《{song["albumTitle"]}》',
                         SongID((song['TSID'],), 'qqjt'),
                         os.path.split(pic_url := song['pic'])[1],
                         pic_url)
                for song in songs]

    async def _get_song_url(self, _id):
        time_stamp = int(time.time())
        sign = hashlib.md5(
            self.SONG_KEY.format(
                TSID=_id, time_stamp=time_stamp).encode()).hexdigest()
        self._set_random_ua()
        res = await self.session.get(
            self.SONG_URL.format(sign=sign, TSID=_id, time_stamp=time_stamp),
            headers=self.headers)
        assert (status := res.status) == 200, f'response: {status}'
        result_dict = await res.json(content_type=None)
        assert not (errmsg := result_dict['errmsg']), errmsg
        data = result_dict['data']
        url = (vip := data.get('path')) or data['trail_audio_info']['path']
        return SongUrl(url, not bool(vip))

    @staticmethod
    def sort_join(data: dict):
        return '&'.join(f'{key}={data[key]}' for key in sorted(data.keys()))

    async def _login(self, login_id, password, **kwargs):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'cookie': 'cuid=65bc7720-ecd3-a26b-eda1-719b8f34f2c9; Hm_lpvt_d0ad46e4afeacf34cd12de4c9b553aa6=1645226594; Hm_lvt_d0ad46e4afeacf34cd12de4c9b553aa6=1645177971,1645178536,1645178919,1645226594',
            'referer': 'https://music.taihe.com/player',
        }
        data = {
            'phone': login_id,
            'password': hashlib.md5(password.encode()).hexdigest(),
            'appid': '16073360',
            'timestamp': (time_stamp := int(time.time())),
        }
        sign = hashlib.md5((self.sort_join(data) + self.SECRET).encode()).hexdigest()
        url = f'https://music.taihe.com/v1/oauth/login/password?sign={sign}&timestamp={time_stamp}'
        res = await self.session.post(url, headers=headers, data=data)
        result = await res.json(content_type=None)
        assert not (errmsg := result['errmsg']), errmsg
        data = result['data']
        data.pop('expires_in')
        return data
