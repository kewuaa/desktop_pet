# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-02-07 00:40:21
# @Last Modified by:   None
# @Last Modified time: 2022-02-13 21:48:34
from urllib.parse import quote
from yarl import URL
import os
import json
import time
import hashlib
import asyncio

from lxml.html import fromstring

from hzy import fake_ua
from hzy.aiofile.aiofile import AsyncFuncWrapper
from ..model import BaseMusicer
from ..model import SongInfo
from ..model import CookieInvalidError
from ..AES import encrypt
from ..RSA import RSA
from .cookie import cookie
from .setting import *


current_path, _ = os.path.split(os.path.realpath(__file__))
ua = fake_ua.UserAgent('internetexplorer')
fromstring = AsyncFuncWrapper(fromstring)


class Musicer(BaseMusicer):
    """docstring for Musicer."""

    SEARCH_URL = 'https://music.migu.cn/v3/search?page=1&type=song&i={i}&f=html&s={s}&c=001002A&keyword={keyword}&v=3.22.4'
    KEY_STR = 'c001002Afhtmlk3915f4a1-4229-4cf9-86a3-08d888cbf524-n41644147336766keyword{keyword}s{s}u{user_agent}/220001v3.22.4'
    SONG_URL = 'https://music.migu.cn/v3/api/music/audioPlayer/getPlayInfo?dataType=2&data={}&secKey=ElP1Za4xkAwkmEnBhaswmP%2FcK91dJQEYRVjJSVvQ9PKXL1CrvdcQVQ2MbjtSfy1JMU8o%2FzkTJY2ypU3NWk%2BXf7aYAv93IdJQAJZKmC%2Fe%2B48V2s52iOeCUcFYc9piXHT%2FMlawqSS4bwaqX%2BucR9J1A3XE21rQSkhjPKLXOAhRESc%3D'
    PERSONAL_KEY = '4ea5c508a6566e76240543f8feb06fd457777be39549c4016436afda65d2330e'
    TO_ENCRYP = '{"copyrightId":"%s","type":1,"auditionsFlag":11}'
    HEADERS = {
        'user-agent': '',
        'cookie': cookie,
        'referer': '',
    }

    def __init__(self):
        super(Musicer, self).__init__(current_path=current_path)
        self.load_login_args(login_id, password)
        self.encode = lambda string: quote(string).replace('/', '%2F').replace('%28', '(').replace('%29', ')')

    # async def init(self):
    #     async with self.session.get('https://music.migu.cn/') as res:
    #         assert res.status == 200
    #     headers = {
    #         'user-agent': ua.get_ua(),
    #         'referer': 'https://music.migu.cn/',
    #     }
    #     url = 'https://passport.migu.cn/popup/login?sourceid=220001&callbackURL=https%3A%2F%2Fmusic.migu.cn%2Fv3'
    #     async with self.session.get(URL(url, encoded=True), headers=headers) as res:
    #         assert res.status == 200
    #     await self.login()
        # print(dir(self.session.cookie_jar._cookies))
        # print(self.session.cookie_jar._cookies)
        # print(help(self.session.cookie_jar.update_cookies))

    async def _get_song_info(self, song):
        keyword = quote(song)
        time_stamp = int(time.time())
        self.HEADERS['referer'] = 'https://music.migu.cn/v3'
        user_agent = self.HEADERS['user-agent'] = ua.get_ua()
        sha1 = hashlib.sha1(self.encode(self.KEY_STR.format(
                                        keyword=keyword,
                                        s=time_stamp,
                                        user_agent=user_agent
                                        )).encode())
        res = await self.session.get(
            self.SEARCH_URL.format(i=sha1.hexdigest(),
                                   s=time_stamp,
                                   keyword=keyword),
            headers=self.HEADERS,
            allow_redirects=False)
        assert (status := res.status) == 200, f'response: {status}'
        text = await res.text()
        tree = await fromstring(text)
        song_list = tree.xpath('//div[@class="songlist-body"]/div')
        return [self._parse_info(song) for song in song_list]

    @staticmethod
    def _parse_info(lxml_tree):
        info = lxml_tree.xpath(
            './div[@class="song-actions single-column"]//@data-share')[0]
        info_dict = json.loads(info)
        return SongInfo(f'咪咕: {info_dict["title"]}-->{info_dict["singer"]}--><{info_dict["album"]}>',
                        (os.path.split(info_dict['linkUrl'])[1], 'mg'),
                        os.path.split(pic_url := info_dict['imgUrl'])[1],
                        ':'.join(['https', pic_url]))

    async def _get_song_url(self, _id):
        self.HEADERS['referer'] = 'https://music.migu.cn/v3/music/player/audio'
        self.HEADERS['user-agent'] = ua.get_ua()
        to_encryp = self.TO_ENCRYP % _id
        data = encrypt(to_encryp, self.PERSONAL_KEY).decode()
        data = self.encode(data)
        res = await self.session.get(URL(self.SONG_URL.format(data), encoded=True),
                                     headers=self.HEADERS,
                                     allow_redirects=False)
        assert (status := res.status) == 200, f'response: {status}'
        result = await res.json(content_type=None)
        if result['returnCode'] != '000000':
            raise CookieInvalidError(result['msg'])
        url = result['data']['playUrl']
        return ':'.join(['https', url])

    async def login(self):
        url = 'https://passport.migu.cn/authn'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
            'Cookie': 'player_stop_open=0; playlist_adding=1; addplaylist_has=1; audioplayer_new=1; add_play_now=1; audioplayer_exist=1; migu_cn_cookie_id=4ab2782f-7292-4771-b7b4-bdfa43b85de1; Hm_lvt_ec5a5474d9d871cb3d82b846d861979d=1644392873; Hm_lpvt_ec5a5474d9d871cb3d82b846d861979d=1644393538; playlist_change=0; audioplayer_open=0; mgpt_session_id=ADARPXRAQ2-7JWXHBT02OZIWD9R03N53-IPPTNKZK-0; mgpt_session_create=1644720004710; mgpt_session_last_access=1644720085065; mgnd_session_id=ADAR8DK7N2-LJWX4VWI4Q24181JHO2Y2-YBQDOKZK-0; mgnd_session_create=1644720938638; WT_FPC=id=295807d169ac3b44bf71644147339348:lv=1644720939787:ss=1644720095103; mgnd_session_last_access=1644721223674',
            'Referer': 'https://passport.migu.cn/login?sourceid=220001&apptype=0&forceAuthn=false&isPassive=false&authType=MiguPassport&passwordControl=0&display=web&referer=https://music.migu.cn/&logintype=1&qq=null&weibo=null&alipay=null&weixin=null&andPass=null&phoneNumber=&callbackURL=https%3A%2F%2Fmusic.migu.cn%2Fv3&relayState=&openPage=&hideRegister=&hideForgetPass=&sim=&needOneKey=0&hideps=0',
            'X-Requested-With': 'XMLHttpRequest',
        }
        data = {
            'sourceID': '220001',
            'appType': '0',
            'relayState': '',
            'loginID': '',
            'enpassword': '',
            'captcha': '',
            'imgcodeType': '1',
            'rememberMeBox': '1',
            'fingerPrint': '365f397d7a702e0ba61a0c81be7447500c0568561479bcb3da6ba896070cc336f6e8e3d5051a38a243ac8cfc57c642c897e04785ab7e2fbc9c674322cd697a3e70389cf3b5ae23e117294f895975aece81c93854dd97025f55cab44a5ef54a35cc0561354a8755a35d0ba0d625b8fab4c4cd8581009ae0c9570fb29ee715fed3',
            'fingerPrintDetail': '1f33883710fa9e30f6ecdb2324fcfea43a542590751fc54a08f094ceb440f5d680327edbf709f48390419d796628e32d5d8c44d4e79d6087d3963c71b260033023de27504d17d1e4c7fb925ee5ce4224569c5073e050462947781d2c57f551480ff194984fda31651a82c75d12cd72776f950a9aea82c8e5bc03744929f53864644ea8109ffdf2284db2a7799537ff50f8c0b9f160ddf45582a12c4fd500cd07c6d4eded3120f73ba57e5cb59986463c992d1ffe89df8307be6bd532a5842bedcaaf9138b905e28bc9f2e9a17e58a6e2f954e46f48cb5a86a77470c11c3520213879df9da08e243c5a1ab96d809b272d9c47682a5297eed2c6efff7dc4c042796909771a6baa300b7bb652901be5a399f6a5193ba54fcf1e9d227431539df077b1b97afe235007fd777b4e21b22bdfb231190747296d704d0070e5e818195f50f81734a7b34376fc314ec14a3530830354f1b261112c21ac9f53be126b6a5e68b9568e584fed59a71c7c859c7be6a4cf4464942bd9abf6efb8ca1922140204051621c2588c7a7824996401a2fc40a1416683e40874fa6172471146329c19db6ee497a0134d415189d8d67e9e41b8a0ab7d1de8547de01e824fb64e72acb13a4d954177bddac21ec5b0442c12e501cb42c50904aaec011e36b283b046a6d57576f9069940c4d6cfe51ddbd88e0e5628b25a954e2a57a3cdaedede781724b2f6d551ae34933c11033b1dffa5bc9cc5d52e6b1eb07ad85968298c0a87264c0d174dea088ae3cff2f79c9ab80e6b508d1bb25175195387715b9c87a2e5d0267ef85f2fdc5d845a21f800453da1b826ad588fb8eaa3927f8f9fde13f4994f8a4d83743ce2cbf766b3785cce8b7e33d75b77e4d54d1c0d1baeb3dcf342911d5224e60b2ee90423bd9b190fd458c875c7caae6a6a3111bea15800114d275bf3105551784a4d438ad57f8b2a5e4cf2ffb13420e5fa806df5c6b4ed8aab82fceabd5dc38e887ff327d2c0afa2d7847c2478a4c80b422ea6da5aef564046da772f24a943c7f171cdd56188b9bc7b105762a45a1fc5478a02a1d338bed5b084e7c72195a37c41aeb4b171437a464d94b5f099b3987aa91e5af685fe9605ea51d362b05596ca55243ff5884c75742f2a21d0b25234cc1dd08192569167d14a27af4634b51122722250d05d0010c00ca04c053959a3bf8327a3c21398ff4a54ab002ee83e4e4b010f12152c32136c1a093a16da2dba1fe4d45b3a634cf34a72a976635516bce37904cff9621c93a2e0641e5ef1c6d76c6c48c323732c32dfde0dcbc6abed4261d0d3e1072dc5468487711df62cc79bfcc08579c9e25d7fb0ce176d2ef8ad69f38c2a180cc5b5963c89be7c64732caf5e328a5705641033c7b3921d03da10f99e97b5b8ae7bb6f6a9f664fe67ec37207aba8167f170cdb8d4fe532160cf8e86ad21379ff701340bfe1025c996c67067572a1965e18811dfc305757441201f5f2324cff51c0da67cf767301fb3290a7f7fdaad1e0573ae5373bbb3ecaa5e11f825f984f46ffb2bcf315bb786aa44697ef4b48257402ac9a6422ecb461838dabaa2064d4bca296b98a75126eea5971120aa392c4e32bd9a8d3e4b8ca8989b11d0d1',
            'isAsync': 'true',
        }
        n = '00833c4af965ff7a8409f8b5d5a83d87f2f19d7c1eb40dc59a98d2346cbb145046b2c6facc25b5cc363443f0f7ebd9524b7c1e1917bf7d849212339f6c1d3711b115ecb20f0c89fc2182a985ea28cbb4adf6a321ff7e715ba9b8d7261d1c140485df3b705247a70c28c9068caabbedbf9510dada6d13d99e57642b853a73406817'
        e = '010001'
        rsa = RSA(n, e)
        data['loginID'] = rsa.encrypt(self.login_id)
        data['enpassword'] = rsa.encrypt(self.password)
        res = await self.session.post(url, headers=headers, data=data)
        # print(self.session.cookie_jar.filter_cookies('https://music.migu.cn'))
        result = await res.json(content_type=None)
        assert result['status'] == 2000, result['message']
        token = result['result']['token']
        async with self.session.get(URL(f'https://music.migu.cn/v3/user/login?callbackURL=https%3A%2F%2Fmusic.migu.cn%2Fv3&relayState=&token={token}',
                                        encoded=True),
                                    headers=headers) as res:
            assert res.status == 200
        cookies = self._get_cookie_dict(cookie)
        cookies.update({i.key: i.value for i in res.cookies.values()})
        cookie_str = self.HEADERS['cookie'] = self._get_cookie_str(cookies)
        asyncio.create_task(self._reset_cookie(cookie_str))
