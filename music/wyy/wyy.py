# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-02-04 13:30:14
# @Last Modified by:   None
# @Last Modified time: 2022-02-17 12:43:32
import os
current_path, _ = os.path.split(os.path.realpath(__file__))
if __name__ == '__main__':
    import sys
    sys.path.append(os.path.join(current_path, '..'))
    sys.path.append(os.path.join(current_path, '../..'))

import json
import base64
import hashlib
import asyncio

from Crypto.Cipher import AES

from hzy import fake_ua
try:
    from model import SongInfo
    from model import BaseMusicer
except ImportError:
    from ..model import SongInfo
    from ..model import BaseMusicer


ua = fake_ua.UserAgent()
spare_cookie = '_ntes_nuid=c6b62f4920356fba00bb02b9ab8ffb6e; _ntes_nnid=4fb10a59e820fa78798fdffdfa1dcbcc,1640399690494; _iuqxldmzr_=32; NMTID=00OggMHqS2StC6LaUBPh-O98krfkUoAAAF-ex-VNw; WNMCID=jdtbkl.1642743174682.01.0; WEVNSM=1.0.0; WM_TID=uWRfK7Me84ZEFBBBRUJq6C7aA7%2BSeboU; playerid=16777386; _antanalysis_s_id=1643284866993; WM_NI=KJozOm5zeeV66Qn%2F95KzDs1S%2Fk52bBUXbEnwiu9H41P9bAloma0%2BZ3dFOyDS9Gs2eO%2FdCXglj0SOLggvutt6utgHlZ8RBx4ChNyzAnaky6phoNQNY15nZhtO1VIb0x9FRk8%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee86cb5b9496b78dd43c8def8ea7d15b938a9e84f87ba69faba4fc53ed96a9b6c72af0fea7c3b92a8996a19bce67f7a6ab86d53ef68fa2d0bc3f89a68c94b459edb5fbd3e14a9788aea6ed7dababf7a9b73b94e7aea2ef65afbf00ccd939a89a819ac759fb99bdd3e845edbc8db9e668aaf09db0cf6da5aabb95f73eb7aca9a9ef52fc8e8e99b749ac92b79bc466a3b5b7d7f364ad929fafdc3bf7b29689f745f38a8783b374fb9a9e8cbb37e2a3; JSESSIONID-WYYY=qsE2QFpkbjMDFpK6IfYNtgT%2BF5bj3WSqN1aGjCFaoOv2JQlrzq%2BAgv%2FvCisx%2FrU%5CmcnGblS7IYqnQgV2Ae9YWUARC2eUnqBkRx37Fq%2BfNo3%2Fht6bjsi5yvKwkmm%2FH0j7W8EQ4lEI8Q4Dxp6EnWmiMmx7r%2Bl1lGty%2FNSrdJq5%5C4%2Bm66f1%3A1643966110097'


def aes_encrypt(text, key):
    text = text.encode()
    pad = 16 - len(text) % 16
    text += chr(pad).encode() * pad
    aes = AES.new(key.encode(), AES.MODE_CBC, '0102030405060708'.encode())
    result = aes.encrypt(text)
    return base64.b64encode(result).decode()


class Musicer(BaseMusicer):
    """docstring for Musicer."""

    URL = 'https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token='
    SEARCH_URL = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='
    HEADERS = {
        'referer': 'https://music.163.com/',
    }
    DATA = {
        'params': '',
        'encSecKey': 'ddb9e95ecba455a303a46b36f291368947d49531f824f5c4adbea2ff7ce22a2e0615a837d727ced55fdbfa85b3590466a39b85749ee5845d29786a7727fd8f154f953ca755d533fe84aa0f100c767f6dbc8441a5ad35711706cb9cf662018025a4519405aa738af496cd3d01594d62821ed0f39b4af97dee184b26e655dd4737',
    }
    i = "7qRdIQPyLJv6h2wV"
    g = "0CoJUm6Qyw8W8jud"
    INFO_REQUEST_DICT = {
        "hlpretag": "<span class=\"s-fc7\">",
        "hlposttag": "</span>",
        "s": '',
        "type": '1',
        "offset": '0',
        "total": "true",
        "limit": "30",
        "csrf_token": "",
    }
    URL_REQUEST_DICT = {
        'ids': '',
        'level': 'standard',
        'encodeType': 'aac',
        'csrf_token': '',
    }

    def __init__(self):
        super(Musicer, self).__init__(
            current_path=current_path, headers=self.HEADERS, cookie=spare_cookie)

    def encrypt(self, text):
        text = aes_encrypt(text, self.g)
        result = aes_encrypt(text, self.i)
        return result

    async def _get_song_info(self, song):
        self.HEADERS['user-agent'] = ua.get_ua()
        self.INFO_REQUEST_DICT['s'] = song
        self.DATA['params'] = self.encrypt(json.dumps(self.INFO_REQUEST_DICT))
        res = await self.session.post(
            self.SEARCH_URL, headers=self.HEADERS, data=self.DATA)
        assert (status := res.status) == 200, f'response: {status}'
        result_dict = await res.json(content_type=None)
        assert (results := result_dict.get('result')) is not None, '出现未知错误'
        songs = results['songs']
        return [SongInfo(
            f"网易云: {song['name']}-->{song['ar'][0]['name']}-->《{song['al']['name']}》",
            (str(song['id']), 'wyy'),
            os.path.split(pic_url := song['al']['picUrl'])[1],
            pic_url)
            for song in songs]

    async def _get_song_url(self, _id):
        self.HEADERS['user-agent'] = ua.get_ua()
        self.URL_REQUEST_DICT['ids'] = f'[{str(_id)}]'
        self.DATA['params'] = self.encrypt(json.dumps(self.URL_REQUEST_DICT))
        res = await self.session.post(self.URL, headers=self.HEADERS, data=self.DATA)
        assert (status := res.status) == 200, f'response: {status}'
        result_dict = await res.json(content_type=None)
        assert (url := result_dict['data'][0]['url']) is not None,\
            'VIP或无版权歌曲，无法播放与下载'
        return url

    # 存在问题待解决
    # 登录功能暂时不可使用
    async def _login(self, login_id, password):
        # try:
        url = 'https://music.163.com/weapi/w/register/cellphone?csrf_token='
        headers = {
            'accept': '*/*',
            'cookie': 'JSESSIONID-WYYY=bc%2FcFyviRmSn%2BezbnMZSyzfBvTu4%2B7mmk4%2BA5gscuJiRaVCPRXo%5CbnSOM%2BDHxDd8R62q5AJRo68DoE9xPrE0WFyrx4ihugPCt3lmm%2BMPyr%5CT6B%2FIBfYoajt2z%2Fuf313KDaZStgpy39ZaTra%5CdXp3uDUwl0ZzZolFZmgO0t6yq89WOWak%3A1644898552583; _iuqxldmzr_=32; _ntes_nnid=3fc405557aca62a5ce1c3f80f27d7f50,1644896752640; _ntes_nuid=3fc405557aca62a5ce1c3f80f27d7f50; NMTID=00OfUZQmXLVo9vEdk8eiakVghEnaYkAAAF--3yUWQ; WEVNSM=1.0.0; WNMCID=qvpqnt.1644896752879.01.0; WM_NI=yaQIRYimWYGqn0VrJdhYvxDHIBdWaVNbBSpn1RH9e57JdF5bPoiNlJ3YaFgkxNXkPoXJDV%2FbYvAbgkfyJ0duaWyKlyXPZ28tba%2FVKjpclArgp5AFwBtdi1IdBspOwG%2BDZGk%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee85d866ede7fdd0d0638be78ab2d85a868b9faaaa218df5ae82f5449cbb8a86dc2af0fea7c3b92abbbf9faad153abb399bac67baef09a93c970ac87ba99c7448b9eacb8e45e8ebe8eb4f366f38e88dae83ff596aca7b86a94b1a7afef42f187afa7e661bc92988cd3659c968cb7ae6a9baa8f83e661a6a786d1e77fa389b7acef739c9096d3bb80a2bfe1b7ca62b4bda4a2f16db4eb8fa7f64ab8bca7d2cc7082adc0b0f64de99c96a8ea37e2a3; WM_TID=8Mlx%2F8iOyAZBRRVUAFY%2BuP6KLrDDLFKJ; __snaker__id=4AXAnkFvY1B3zC4a; gdxidpyhxdE=AzNIHxaaPlR%2B3pT2BG%2BabQRlNhMsnEn7MiqH5Cd9DrWK%2B%2FPPtoi%5C%2BrMl%2BlsXS6AbSMHOtUPNSMsWd%2F8kSNcuPBzKH2ibyH8YMsX0l39TSSP71yOCOgM6DCBRugGirD3CeXJ%5C9VM14yX7W7XHfYYBNhwy3r%5CSxJa%2FokmEaeyf8s%2FGnbnj%3A1644897670778; _9755xjdesxxd_=32',
            'origin': 'https://music.163.com',
            'referer': 'https://music.163.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
        }
        login_dict = {
            'phone': login_id,
            'rememberLogin': 'true',
            'password': hashlib.md5(password.encode()).hexdigest(),
            'checkToken': await self.get_checktoken(),
            'csrf_token': '',
        }
        self.DATA['params'] = self.encrypt(json.dumps(login_dict))
        res = await self.session.post(url, headers=headers, data=self.DATA)
        result = await res.json(content_type=None)
        assert result['code'] == 200, result['msg']
        # finally:
        #     await self.close()
        # cookies = self._get_cookie_dict(cookie)
        # cookies.update({i.key: i.value for i in res.cookies.values()})
        # cookie_str = self.HEADERS['cookie'] = self._get_cookie_str(cookies)
        # asyncio.create_task(self._reset_cookie(cookie_str))

    async def get_checktoken(self):
        # self.load_js()
        proc = await asyncio.create_subprocess_shell(
            f'node {current_path}/checktoken.js',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        assert not stderr, stderr.decode('gbk')
        return stdout.decode().strip()
