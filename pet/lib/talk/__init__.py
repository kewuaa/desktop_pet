from urllib.parse import quote_plus
from itertools import count
from pathlib import Path
from re import compile
from time import time
import json
import base64
import asyncio
import winsound

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.nlp.v20190408 import nlp_client
from tencentcloud.nlp.v20190408 import models as nlp_models
from tencentcloud.asr.v20190614 import asr_client
from tencentcloud.asr.v20190614 import models as asr_models
from tencentcloud.tts.v20190823 import tts_client
from tencentcloud.tts.v20190823 import models as tts_models
from aiohttp import ClientSession
import speech_recognition as sr

from ..aiofile import AIOWrapper
from ..aiofile import async_open


current_path = Path(__file__).parent


class Talker:
    "chat robot."

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
            print(f'setting file: "{path}" not found')
            return
        async with async_open(path, 'r') as f:
            settings = await f.read()
        self._settings = {
            line.split('=')[0]: line.split('=')[1]
            for line in settings.split('\n')
        }
        self._init_tencent_app()

    def __call__(self):
        if not hasattr(self, '_settings'):
            print('no settings have been loaded')
            return
        self.__loop.create_task(self._run())

    def _init_tencent_app(self):
        cred = credential.Credential(
            self._settings['TENCENT_SECRET_ID'],
            self._settings['TENCENT_SECRET_KEY'],
        )
        self._tencent_nlp_client = AIOWrapper(nlp_client.NlpClient(cred, 'ap-guangzhou'))
        self._tencent_asr_client = AIOWrapper(asr_client.AsrClient(cred, 'ap-chengdu'))
        self._tencent_tts_client = AIOWrapper(tts_client.TtsClient(cred, "ap-chengdu"))

    async def _get_response(self, msg: str) -> str:
        req = nlp_models.ChatBotRequest()
        params = {
            'Query': msg,
        }
        req.from_json_string(json.dumps(params))
        resp = await self._tencent_nlp_client.ChatBot(req)
        response_dict = json.loads(resp.to_json_string())
        resp = response_dict.get('Reply')
        if resp is None:
            raise
        return resp

    result_compile = compile(r'\[.*\]([\s\S]*)')

    async def _get_speech_recognition(self, content):
        async def fetch_result(task_id):
            while 1:
                req = asr_models.DescribeTaskStatusRequest()
                params = {
                    "TaskId": task_id,
                }
                req.from_json_string(json.dumps(params))
                resp = await self._tencent_asr_client.DescribeTaskStatus(req)
                response_dict = json.loads(resp.to_json_string())
                data = response_dict['Data']
                status = data['Status']
                if status == 2:
                    result = data['Result']
                    result = self.result_compile.findall(result)[0]
                    return result.strip()
                elif status == 3:
                    raise RuntimeError(f'fetch result error: {data["ErrorMsg"]}')
                else:
                    await asyncio.sleep(0.3)

        length = len(content)
        assert length
        speech = base64.b64encode(content).decode()
        req = asr_models.CreateRecTaskRequest()
        params = {
            "ResTextFormat": 0,
            "EngineModelType": "16k_zh",
            "ChannelNum": 1,
            "SourceType": 1,
            "Data": speech,
            "DataLen": length,
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个CreateRecTaskResponse的实例，与请求对象对应
        resp = await self._tencent_asr_client.CreateRecTask(req)
        # 输出json格式的字符串回包
        response_dict = json.loads(resp.to_json_string())
        task_id = response_dict['Data']['TaskId']
        return await asyncio.wait_for(
            fetch_result(task_id),
            15,
        )

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
        req = tts_models.TextToVoiceRequest()
        params = {
            "Text": text,
            "SessionId": f"session-{int(time())}",
            "VoiceType": 1001,
            "Codec": "wav"
        }
        req.from_json_string(json.dumps(params))
        resp = await self._tencent_tts_client.TextToVoice(req)
        response_dict = json.loads(resp.to_json_string())
        content = response_dict['Audio'].encode()
        content = base64.b64decode(content)
        path = current_path / f'temp{next(self.__index)}.wav'
        async with async_open(path, 'wb') as f:
            await f.write(content)
        winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        self._to_delete.append(path)

        def callback(fut: asyncio.futures.Future) -> None:
            if fut.done():
                path.unlink()
                self._to_delete.remove(path)
        self.__loop.call_later(60, callback)

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

