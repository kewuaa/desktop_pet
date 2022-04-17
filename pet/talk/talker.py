# -*- coding: utf-8 -*-
#******************************************************************#
#
#          +-------------------------------------------+
#          |  __                                       |
#          | |  | __ ______  _  ____ _______  _____    |
#          | |  |/ // __ \ \/ \/ /  |  \__  \ \__  \   |
#          | |    <\  ___/\     /|  |  // __ \_/ __ \_ |
#          | |__|_ \\___  >\/\_/ |____/(____  (____  / |
#          |      \/    \/                  \/     \/  |
#          |                                           |
#          +-------------------------------------------+
#
#                     Filename: talker.py
#
#                       Author: kewuaa
#                      Created: 2022-04-15 19:19:16
#                last modified: 2022-04-17 15:47:58
#******************************************************************#
from urllib.parse import quote_plus
import os
import json
import base64
import asyncio
import winsound

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.nlp.v20190408 import nlp_client, models
import speech_recognition as sr

from pet.hzy.aiofile.aiofile import AIOWrapper
from pet.hzy.aiofile.aiofile import open_async
from pet.model import BaseModel


current_path, _ = os.path.split(os.path.realpath(__file__))


class Talker(BaseModel):
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
        super().__init__(current_path)
        self._recognizer = sr.Recognizer()
        asyncio.create_task(self._load_settings())
        self._to_delete = []

    async def _load_settings(self):
        if not os.path.exists(path := os.path.join(self.current_path, 'setting')):
            raise
        async with open_async(path, 'r') as f:
            settings = await f.read()
        print(settings)
        self._settings = {line.split('=')[0]: line.split('=')[1] for line in settings.split('\n')}
        print(self._settings)
        await self._fech_baidu_token()
        asyncio.current_task().add_done_callback(lambda _: self._init_tencent_app())

    def __call__(self):
        asyncio.create_task(
            asyncio.wait_for(self._run(), timeout=33)
            )

    def _init_tencent_app(self):
        cred = credential.Credential(
            self._settings['TENCENT_SECRET_ID'], self._settings['TENCENT_SECRET_KEY'])
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
        assert (resp := response_dict.get('Reply'))
        return resp

    async def _fech_baidu_token(self):
        params = {
                'grant_type': 'client_credentials',
                'client_id': self._settings['BAIDU_API_KEY'],
                'client_secret': self._settings['BAIDU_SECRET_KEY'],
                }
        resp = await self.session.get(self.TOKEN_URL, params=params)
        assert (status := resp.status) == 200, f'response: {status}'
        resp_dict = await resp.json(content_type=None)
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
        headers = {
                'Content-Type': 'application/json'
                }
        resp = await self.session.post(self.ASR_URL, headers=headers, data=json.dumps(self.ASR_DATA))
        assert (status := resp.status) == 200, f'response: {status}'
        resp_dict = await resp.json(content_type=None)
        assert (result := resp_dict.get('result')), resp_dict['err_msg']
        return result[0]

    def _record(self):
        with sr.Microphone(sample_rate=16000) as source:
            print('record start')
            audio = self._recognizer.listen(source)
        print('record ended')
        return audio.get_wav_data()

    async def _speak(self, text: str):
        text = quote_plus(text)
        self.TSS_PARAMS['tex'] = text
        resp = await self.session.get(self.TTS_URL, params=self.TSS_PARAMS)
        assert (status := resp.status) == 200, f'response: {status}'
        content = await resp.read()
        async with open_async((path := os.path.join(
                self.current_path, f'{self._get_random_name()}.wav'
                )), 'wb') as f:
            await f.write(content)
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        asyncio.get_running_loop().call_later(
            33, lambda :os.remove(path) or self._to_delete.remove(path))
        self._to_delete.append(path)

    async def _run(self):
        content = await asyncio.get_running_loop().run_in_executor(None, self._record)
        # async with open_async(f'{self.current_path}/result.wav', 'rb') as f:
        #     content = await f.read()
        msg = await self._get_speech_recognition(content)
        # print(f'我说：{msg}')
        resp = await self._get_response(msg)
        # print(f'回复：{resp}')
        asyncio.create_task(self._speak(resp))

    async def close(self):
        if self._to_delete:
            for path in self._to_delete:
                os.remove(path)
        return await super().close()

