# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-03-03 12:52:16
# @Last Modified by:   None
# @Last Modified time: 2022-03-04 15:50:45
import os
current_path, _ = os.path.split(os.path.realpath(__file__))
if __name__ == '__main__':
    import sys
    sys.path.append(os.path.join(current_path, '..'))
    sys.path.append(os.path.join(current_path, '../..'))

from urllib.parse import quote
from functools import partial
import re
import time
import json
import ctypes
import secrets
import asyncio

from hzy import fake_ua
try:
    from model import SongInfo
    from model import SongUrl
    from model import SongID
    from model import BaseMusicer
    from model import VerifyError
except ImportError:
    from ..model import SongInfo
    from ..model import SongUrl
    from ..model import SongID
    from ..model import BaseMusicer
    from ..model import VerifyError


ua = fake_ua.UserAgent()
spare_cookie = 'kw_token=U3AE5RVQKM'


def int_overflow(val: int) -> int:
    maxint = 2 ** 31
    if not -maxint <= val <= maxint - 1:
        val = (val + maxint) % (2 * maxint) - maxint
    return val


def unsigned_right_shitf(n, i):
    # 数字小于0，则转为32位无符号uint
    if n < 0:
        n = ctypes.c_uint32(n).value
    # 正常位移位数是为正数，但是为了兼容js之类的，负数就右移变成左移好了
    if i < 0:
        return -int_overflow(n << abs(i))
    # print(n)
    return int_overflow(n >> i)


n = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', '2b', '2c', '2d', '2e', '2f', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', '4c', '4d', '4e', '4f', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', '6d', '6e', '6f', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '7e', '7f', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9a', '9b', '9c', '9d', '9e', '9f', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 'db', 'dc', 'dd', 'de', 'df', 'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']


def reqid():
    r = None
    o = None
    d = 0

    def get_reqid():
        nonlocal r, o, d
        b = []
        f = r
        v = o
        if f is None or v is None:
            m = [secrets.randbelow(256) for _ in range(16)]
            r = f = f or [1 | m[0], m[1], m[2], m[3], m[4], m[5]]
            o = v = v or 16383 & (int_overflow(m[6] << 8) | 7)
        y = int(time.time() * 1000)
        w = d + 1
        d = w
        x = (10000 * (268435455 & (y := y + 12219292800000)) + w) % 4294967296
        b.append(unsigned_right_shitf(x, 24) & 255)
        b.append(unsigned_right_shitf(x, 16) & 255)
        b.append(unsigned_right_shitf(x, 8) & 255)
        b.append(255 & x)
        _x = int(y / 4294967296 * 10000) & 268435455
        b.append(unsigned_right_shitf(_x, 8) & 255)
        b.append(255 & _x)
        b.append(unsigned_right_shitf(_x, 24) & 15 | 16)
        b.append(unsigned_right_shitf(_x, 16) & 255)
        b.append(unsigned_right_shitf(v, 8) | 128)
        b.append(255 & v)
        b.extend(f)
        result = [n[i] for i in b]
        result.insert(10, '-')
        result.insert(8, '-')
        result.insert(6, '-')
        result.insert(4, '-')
        return ''.join(result)
    return get_reqid


get_reqid = reqid()


class Musicer(BaseMusicer):
    """docstring for Musicer."""

    SEARCH_URL = 'https://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key={keyword}&pn=1&rn=20&httpsStatus=1&reqId={reqid}'
    SONG_URL = 'https://www.kuwo.cn/api/v1/www/music/playUrl?mid={rid}&type=music&httpsStatus=1&reqId={reqid}'

    def __init__(self):
        super(Musicer, self).__init__(
            current_path=current_path, verify=True)
        self.headers['Cookie'] = spare_cookie
        self.headers['Referer'] = 'https://www.kuwo.cn/search/list'
        self._login = self._update_cookie(self._login)
        self._verify_img = None
        self._verify_token = None
        self.sub = re.compile(r'(?<=kw_token=)\w{10}')

    async def _get_song_info(self, song, retry_num=3):
        keyword = quote(song)
        self.headers['user-agent'] = ua.get_ua()
        self.headers['csrf'] = self.sub.search(self.headers['Cookie']).group()
        res = await self.session.get(
            self.SEARCH_URL.format(keyword=keyword,
                                   reqid=(reqid := get_reqid())),
            headers=self.headers)
        if (status := res.status) > 400 and retry_num:
            print('retry')
            return await self._get_song_info(song, retry_num=retry_num - 1)
        assert status == 200, f'response: {status}'
        asyncio.current_task().add_done_callback(
            partial(self._change_token, res.cookies))
        result_dict = await res.json(content_type=None)
        assert result_dict.get('success') is None, result_dict['message']
        songs = result_dict['data']['list']
        return [SongInfo(f'酷我: {song["name"]}-->{song["artist"]}-->《{song["album"]}》',
                         SongID((str(song['rid']),), 'kw'),
                         os.path.split(pic_url := song['pic'])[1],
                         pic_url)
                for song in songs]

    async def _get_song_url(self, _id, retry_num=3):
        self.headers['user-agent'] = ua.get_ua()
        res = await self.session.get(
            self.SONG_URL.format(rid=_id, reqid=get_reqid()),
            headers=self.headers)
        if (status := res.status) > 400 and retry_num:
            print('retry')
            return await self._get_song_url(_id, retry_num=retry_num - 1)
        assert status == 200, f'response: {status}'
        asyncio.current_task().add_done_callback(
            partial(self._change_token, res.cookies))
        result_dict = await res.json(content_type=None)
        assert result_dict['code'] == 200, result_dict['msg']
        return SongUrl(result_dict['data']['url'])

    def _change_token(self, res_cookie, *args):
        kw_token = [i.value
                    for i in res_cookie.values()
                    if i.key == 'kw_token']
        self.headers['Cookie'] = self.sub.sub(kw_token, self.headers['Cookie'])

    async def _verify(self):
        url = f'https://www.kuwo.cn/api/common/captcha/getcode?reqId={get_reqid()}&httpsStatus=1'
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Cookie': 'kw_token=4BIODCKIP9L',
            'csrf': '4BIODCKIP9L',
            'Host': 'www.kuwo.cn',
            'Origin': 'https://www.kuwo.cn',
            'Referer': 'https://www.kuwo.cn/',
        }
        res = await self.session.get(url, headers=headers)
        assert (status := res.status) == 200, f'response: {status}'
        result_dict = await res.json(content_type=None)
        data = result_dict['data']
        self._verify_img = img = data['img']
        self._verify_token = data['token']
        return img.split(',')[-1]

    async def _login(self, login_id, password, verify_code=None, **kwargs):
        if verify_code is None:
            raise VerifyError(json.dumps({'login_id': login_id, 'password': password}))
        url = f'https://www.kuwo.cn/api/www/login/loginByKw?reqId={get_reqid()}&httpsStatus=1'
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Cookie': 'kw_token=G17DD57NYT5',
            'csrf': 'G17DD57NYT5',
            'Host': 'www.kuwo.cn',
            'Origin': 'https://www.kuwo.cn',
            'Referer': 'https://www.kuwo.cn/',
            'Content-Type': 'application/json;charset=UTF-8',
        }
        data = {
            "userIp": "www.kuwo.cn",
            "uname": login_id,
            "password": password,
            "verifyCode": verify_code,
            "img": self._verify_img or '',
            "verifyCodeToken": self._verify_token or '',
        }
        res = await self.session.post(url, headers=headers, data=json.dumps(data))
        result_dict = await res.json(content_type=None)
        # print(result_dict)
        assert result_dict['code'] == 200, result_dict['msg']
        return result_dict['data']['cookies']
