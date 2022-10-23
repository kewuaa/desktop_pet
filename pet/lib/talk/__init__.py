from urllib.parse import quote_plus
from itertools import count
from pathlib import Path
import json
import base64
import asyncio
import winsound

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.nlp.v20190408 import nlp_client, models
from aiohttp import ClientSession
import speech_recognition as sr

from ..aiofile import AIOWrapper
from ..aiofile import async_open


current_path = Path(__file__).parent


class Talker:
    "chat robot."

    TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'
    ASR_URL = 'http://vop.baidu.com/server_api'
    TTS_URL = 'http://tsn.baidu.com/text2audio'
    ASR_DATA = {
        'dev_pid': 1537,
        'rate': 16000,
        'cuid': '123456PYTHON',
        'channel': 1,
        'format': 'wav',
    }
    TSS_PARAMS = {
        'per': 103, # 发音人选择, 基础音库：0为度小美，1为度小宇，3为度逍遥，4为度丫丫
        # 精品音库：5为度小娇，103为度米朵，106为度博文，110为度小童，111为度小萌，默认为度小美
        'spd': 5,   # 语速，取值0-15，默认为5中语速
        'pil': 5,   # 音调，取值0-15，默认为5中语调
        'vol': 5,   # 音量，取值0-9，默认为5中音量
        'aue': 6,   # 下载的文件格式, 3：mp3(default) 4： pcm-16k 5： pcm-8k 6. wav
        'cuid': '123456PYTHON',
        'lan': 'zh',
        'ctp': 1,
    }

    def __init__(self) -> None:
        self.__loop = loop = asyncio.get_event_loop()
        self._recognizer = sr.Recognizer()
        self._to_delete = []
        self.__index = self.__increase_i()
        self.__sess = loop.create_future()

        def init_sess() -> None:
            task = loop.create_task(self.__init_sess())
            asyncio.futures._chain_future(task, self.__sess)

        self.__headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.47',
        }
        loop.call_soon_threadsafe(init_sess)
        loop.create_task(self.__load_settings())

    async def __init_sess(self) -> ClientSession:
        kwargs = {
            'headers': self.__headers,
            'loop': self.__loop,
        }
        return ClientSession(**kwargs)

    async def __load_settings(self):
        path = current_path / 'setting'
        if not path.exists():
            raise
        async with async_open(path, 'r') as f:
            settings = await f.read()
        self._settings = {
            line.split('=')[0]: line.split('=')[1]
            for line in settings.split('\n')
        }
        await self._fech_baidu_token()
        self._init_tencent_app()

    def __call__(self):
        self.__loop.create_task(
            asyncio.wait_for(self._run(), timeout=33)
        )

    def _init_tencent_app(self):
        cred = credential.Credential(
            self._settings['TENCENT_SECRET_ID'],
            self._settings['TENCENT_SECRET_KEY'],
        )
        httpProfile = HttpProfile()
        httpProfile.endpoint = 'nlp.tencentcloudapi.com'
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        self._tencent_client = AIOWrapper(nlp_client.NlpClient(cred, 'ap-guangzhou', clientProfile))

    async def _get_response(self, msg: str) -> str:
        req = models.ChatBotRequest()
        params = {
            'Query': msg,
        }
        req.from_json_string(json.dumps(params))
        resp = await self._tencent_client.ChatBot(req)
        response_dict = json.loads(resp.to_json_string())
        resp = response_dict.get('Reply')
        if resp is None:
            raise
        return resp

    async def _fech_baidu_token(self):
        params = {
            'grant_type': 'client_credentials',
            'client_id': self._settings['BAIDU_API_KEY'],
            'client_secret': self._settings['BAIDU_SECRET_KEY'],
        }
        sess: ClientSession = await self.__sess
        res = await sess.get(self.TOKEN_URL, params=params)
        if res.status != 200:
            raise
        resp_dict = await res.json(content_type=None)
        self.ASR_DATA['token'] = self.TSS_PARAMS['tok'] = resp_dict['access_token']

    async def _get_speech_recognition(self, content):
        length = len(content)
        assert length
        speech = base64.b64encode(content).decode()
        data = {
            'speech': speech,
            'len': length
        }
        self.ASR_DATA.update(data)
        sess: ClientSession = await self.__sess
        headers = {
            'Content-Type': 'application/json'
        }
        resp = await sess.post(
            self.ASR_URL,
            headers=headers,
            data=json.dumps(self.ASR_DATA),
        )
        if resp.status != 200:
            raise
        resp_dict = await resp.json(content_type=None)
        result = resp_dict.get('result')
        if not result:
            raise RuntimeError(resp_dict['err_msg'])
        return result[0]

    def _record(self):
        print('record start')
        with sr.Microphone(sample_rate=16000) as source:
            audio = self._recognizer.listen(source)
        print('record ended')
        return audio.get_wav_data()

    def __increase_i(self):
        c = count(0)
        yield from c

    async def _speak(self, text: str):
        text = quote_plus(text)
        self.TSS_PARAMS['tex'] = text
        sess: ClientSession = await self.__sess
        resp = await sess.get(
            self.TTS_URL,
            params=self.TSS_PARAMS,
        )
        if resp.status != 200:
            raise
        content = await resp.read()
        path = current_path / f'temp{next(self.__index)}.wav'
        async with async_open(path, 'wb') as f:
            await f.write(content)
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        self._to_delete.append(path)

        def callback() -> None:
            path.unlink()
            self._to_delete.remove(path)
        self.__loop.call_later(33, callback)

    async def _run(self):
        content = await self.__loop.run_in_executor(None, self._record)
        # async with async_open(f'{self.current_path}/result.wav', 'rb') as f:
        #     content = await f.read()
        msg = await self._get_speech_recognition(content)
        # print(f'我说：{msg}')
        resp = await self._get_response(msg)
        # print(f'回复：{resp}')
        self.__loop.create_task(self._speak(resp))

    async def close(self):
        if self._to_delete:
            for path in self._to_delete:
                path.unlink()
        sess: ClientSession = await self.__sess
        if not sess.closed:
            await sess.close()

