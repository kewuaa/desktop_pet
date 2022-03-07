# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-01-15 08:58:38
# @Last Modified by:   None
# @Last Modified time: 2022-02-17 11:37:47
from collections import deque
import os
import re
import sys
import json
import base64
import asyncio

from lxml.html import fromstring
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QMessageBox
from PySide2.QtCore import Slot
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtGui import QIcon
from qasync import QEventLoop


from pet.model import BaseModel
from pet.model import Signal
from pet.hzy.aiofile import aiofile
from pet.translate.ui_translate import Ui_MainWindow


current_path, _ = os.path.split(os.path.realpath(__file__))
cookie = 'BIDUPSID=4B1B005B6F2DBD2D11C57555E80B2740; PSTM=1640399284; BDRCVFR[-HoWM-pHJEc]=mk3SLVN4HKm; BAIDUID=4B1B005B6F2DBD2DB1DC4B80C0B3ACF2:FG=1; delPer=0; BAIDUID_BFESS=AC31DE3EC7C0DB23CDFBD6FA2CE1673F:FG=1; BDUSS=I1UnNxc2J3NkgtTjJld3c4QTBUcX5nY35hWXR6R2lvZUt1RDlHTGpPNi1YTzVoRUFBQUFBJCQAAAAAAAAAAAEAAACEADmlt-fs4b2jAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL7PxmG-z8ZhSG; BDUSS_BFESS=I1UnNxc2J3NkgtTjJld3c4QTBUcX5nY35hWXR6R2lvZUt1RDlHTGpPNi1YTzVoRUFBQUFBJCQAAAAAAAAAAAEAAACEADmlt-fs4b2jAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL7PxmG-z8ZhSG; __yjs_duid=1_15aafb3ad0d7e3082c8ae6e3fe3107ba1640602511741; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; H_WISE_SIDS=107313_110085_127969_164870_174434_179345_184441_184716_185240_185268_186635_186841_187828_188125_189326_189732_189755_189971_190145_190248_190473_190622_191067_191256_191369_191503_191810_192206_192237_192390_193144_193283_193560_194085_194130_194509_194519_194583_194996_195173_195188_195346_195478_195552_195578_195679_196046_196049_196230_196427_196833_196881_196940_197083_197242_197287_197314_197337_197470_197582_197711_197782_197832_198031_198034_198067_198074_198089_198188_198259_198420_198510_198537_198648_198664_198750_198901_198998_199023_199041_199163_199177_199468_199578_199677_199876_199971; ZD_ENTRY=google; PSINO=6; H_PS_PSSID=31254_26350; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; APPGUIDE_10_0_2=1; BA_HECTOR=8lakagag0h8005a0521gu9bij0r; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1642311095,1642320813,1642376794,1642377546; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1642377546; __yjs_st=2_YzM5NTI0ODA3NjNlZTBhM2VlZjkyZjgyMTk4ZWY4YjJmMDJiNjBiNTI3NDI4N2RmYTY4ODA4Zjg2NGU2MTBmYWYyOTA4MjRmNGYwYjViZjg0NzAzNmY0ZWZhMzQ0MDE5NzYzNDEzYzJhZmIwZmNkMzQ4ZmM1ZDMzZjU5ZTE2YmQ1MjE2MmIwMWRkNzA0YjVlZjNkZDhmZmQzZTkxNzNkZDNiNmEyNzA5ODkzOTZlYjA2YjY0MzU2Y2VhMDlmNTZmNTgzZTRkOGUzYTNmYzE0ZjYwYWEyM2IwMTIwZTUzZjIwYjAyN2Q5ZjE2ZDc3YzliZjkzZmJkMGU3MDdjYzAxN183X2JiY2VlY2Vk; ab_sr=1.0.1_OWExZjY3OTMyN2QwYzBkYTY2ZjdjMzBhNTA3ZGQ3MTliOTZmZmFhZGQxZTY4NTEyMDUzZDE3OTI5YjBlMzhjY2ViNTMxMzIwYWEwMzYwZWJhZGI5ZGY3MTQ4YWE3ZDk3OTNlYzk4NjUxZjk3Y2RlOTcwYWU5NTUwODkyMDNiZTRjNjRjZDNjNGQwZThkNTYzNWQzY2EwN2I3ODk3YjM0ODFhNmExMmQwMzIxNGMwZDU3ZWE5N2Q3ZTUwZTcyNDli'
SIGN_JS = 'ZnVuY3Rpb24gbihyLCBvKSB7DQogICAgICAgIGZvciAodmFyIHQgPSAwOyB0IDwgby5sZW5ndGggLSAyOyB0ICs9IDMpIHsNCiAgICAgICAgICAgIHZhciBhID0gby5jaGFyQXQodCArIDIpOw0KICAgICAgICAgICAgYSA9IGEgPj0gImEiID8gYS5jaGFyQ29kZUF0KDApIC0gODcgOiBOdW1iZXIoYSksDQogICAgICAgICAgICBhID0gIisiID09PSBvLmNoYXJBdCh0ICsgMSkgPyByID4+PiBhIDogciA8PCBhLA0KICAgICAgICAgICAgciA9ICIrIiA9PT0gby5jaGFyQXQodCkgPyByICsgYSAmIDQyOTQ5NjcyOTUgOiByIF4gYQ0KICAgICAgICB9DQogICAgICAgIHJldHVybiByDQogICAgfQ0KZnVuY3Rpb24gbWFpbihyKSB7DQogICAgICAgIHZhciBpID0gJzMyMDMwNS4xMzEzMjEyMDEnDQogICAgICAgIHZhciBvID0gci5tYXRjaCgvW1x1RDgwMC1cdURCRkZdW1x1REMwMC1cdURGRkZdL2cpOw0KICAgICAgICBpZiAobnVsbCA9PT0gbykgew0KICAgICAgICAgICAgdmFyIHQgPSByLmxlbmd0aDsNCiAgICAgICAgICAgIHQgPiAzMCAmJiAociA9ICIiICsgci5zdWJzdHIoMCwgMTApICsgci5zdWJzdHIoTWF0aC5mbG9vcih0IC8gMikgLSA1LCAxMCkgKyByLnN1YnN0cigtMTAsIDEwKSkNCiAgICAgICAgfSBlbHNlIHsNCiAgICAgICAgICAgIGZvciAodmFyIGUgPSByLnNwbGl0KC9bXHVEODAwLVx1REJGRl1bXHVEQzAwLVx1REZGRl0vKSwgQyA9IDAsIGggPSBlLmxlbmd0aCwgZiA9IFtdOyBoID4gQzsgQysrKQ0KICAgICAgICAgICAgICAgICIiICE9PSBlW0NdICYmIGYucHVzaC5hcHBseShmLCBhKGVbQ10uc3BsaXQoIiIpKSksDQogICAgICAgICAgICAgICAgQyAhPT0gaCAtIDEgJiYgZi5wdXNoKG9bQ10pOw0KICAgICAgICAgICAgdmFyIGcgPSBmLmxlbmd0aDsNCiAgICAgICAgICAgIGcgPiAzMCAmJiAociA9IGYuc2xpY2UoMCwgMTApLmpvaW4oIiIpICsgZi5zbGljZShNYXRoLmZsb29yKGcgLyAyKSAtIDUsIE1hdGguZmxvb3IoZyAvIDIpICsgNSkuam9pbigiIikgKyBmLnNsaWNlKC0xMCkuam9pbigiIikpDQogICAgICAgIH0NCiAgICAgICAgdmFyIHUgPSB2b2lkIDANCiAgICAgICAgICAsIGwgPSAiIiArIFN0cmluZy5mcm9tQ2hhckNvZGUoMTAzKSArIFN0cmluZy5mcm9tQ2hhckNvZGUoMTE2KSArIFN0cmluZy5mcm9tQ2hhckNvZGUoMTA3KTsNCiAgICAgICAgdSA9IG51bGwgIT09IGkgPyBpIDogKGkgPSB3aW5kb3dbbF0gfHwgIiIpIHx8ICIiOw0KICAgICAgICBmb3IgKHZhciBkID0gdS5zcGxpdCgiLiIpLCBtID0gTnVtYmVyKGRbMF0pIHx8IDAsIHMgPSBOdW1iZXIoZFsxXSkgfHwgMCwgUyA9IFtdLCBjID0gMCwgdiA9IDA7IHYgPCByLmxlbmd0aDsgdisrKSB7DQogICAgICAgICAgICB2YXIgQSA9IHIuY2hhckNvZGVBdCh2KTsNCiAgICAgICAgICAgIDEyOCA+IEEgPyBTW2MrK10gPSBBIDogKDIwNDggPiBBID8gU1tjKytdID0gQSA+PiA2IHwgMTkyIDogKDU1Mjk2ID09PSAoNjQ1MTIgJiBBKSAmJiB2ICsgMSA8IHIubGVuZ3RoICYmIDU2MzIwID09PSAoNjQ1MTIgJiByLmNoYXJDb2RlQXQodiArIDEpKSA/IChBID0gNjU1MzYgKyAoKDEwMjMgJiBBKSA8PCAxMCkgKyAoMTAyMyAmIHIuY2hhckNvZGVBdCgrK3YpKSwNCiAgICAgICAgICAgIFNbYysrXSA9IEEgPj4gMTggfCAyNDAsDQogICAgICAgICAgICBTW2MrK10gPSBBID4+IDEyICYgNjMgfCAxMjgpIDogU1tjKytdID0gQSA+PiAxMiB8IDIyNCwNCiAgICAgICAgICAgIFNbYysrXSA9IEEgPj4gNiAmIDYzIHwgMTI4KSwNCiAgICAgICAgICAgIFNbYysrXSA9IDYzICYgQSB8IDEyOCkNCiAgICAgICAgfQ0KICAgICAgICBmb3IgKHZhciBwID0gbSwgRiA9ICIiICsgU3RyaW5nLmZyb21DaGFyQ29kZSg0MykgKyBTdHJpbmcuZnJvbUNoYXJDb2RlKDQ1KSArIFN0cmluZy5mcm9tQ2hhckNvZGUoOTcpICsgKCIiICsgU3RyaW5nLmZyb21DaGFyQ29kZSg5NCkgKyBTdHJpbmcuZnJvbUNoYXJDb2RlKDQzKSArIFN0cmluZy5mcm9tQ2hhckNvZGUoNTQpKSwgRCA9ICIiICsgU3RyaW5nLmZyb21DaGFyQ29kZSg0MykgKyBTdHJpbmcuZnJvbUNoYXJDb2RlKDQ1KSArIFN0cmluZy5mcm9tQ2hhckNvZGUoNTEpICsgKCIiICsgU3RyaW5nLmZyb21DaGFyQ29kZSg5NCkgKyBTdHJpbmcuZnJvbUNoYXJDb2RlKDQzKSArIFN0cmluZy5mcm9tQ2hhckNvZGUoOTgpKSArICgiIiArIFN0cmluZy5mcm9tQ2hhckNvZGUoNDMpICsgU3RyaW5nLmZyb21DaGFyQ29kZSg0NSkgKyBTdHJpbmcuZnJvbUNoYXJDb2RlKDEwMikpLCBiID0gMDsgYiA8IFMubGVuZ3RoOyBiKyspDQogICAgICAgICAgICBwICs9IFNbYl0sDQogICAgICAgICAgICBwID0gbihwLCBGKTsNCiAgICAgICAgcmV0dXJuIHAgPSBuKHAsIEQpLA0KICAgICAgICBwIF49IHMsDQogICAgICAgIDAgPiBwICYmIChwID0gKDIxNDc0ODM2NDcgJiBwKSArIDIxNDc0ODM2NDgpLA0KICAgICAgICBwICU9IDFlNiwNCiAgICAgICAgcC50b1N0cmluZygpICsgIi4iICsgKHAgXiBtKQ0KICAgIH0NCi8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLw0KY29uc3QgYXJncyA9IHByb2Nlc3MuYXJndi5zbGljZSgyKQ0KdmFyIGRhdGEgPSBhcmdzLmpvaW4oJyAnKQ0KY29uc29sZS5sb2cobWFpbihkYXRhKSkNCg=='


class BaiduTranslater(BaseModel):
    """docstring for BaiduTranslater."""

    BASE_URL = 'https://fanyi.baidu.com'
    POST_URL = 'https://fanyi.baidu.com/v2transapi?'
    FROM = '中文'
    TO = '英语'
    DOMAIN = '通用'

    def __init__(self):
        super(BaiduTranslater, self).__init__(current_path=current_path, js=SIGN_JS)
        asyncio.create_task(self.init())
        self.signal = Signal()
        self.headers['cookie'] = cookie
        self.js_name = self._get_random_name()

    async def init(self):
        self._set_random_ua()
        res = await self.session.get(self.BASE_URL, headers=self.headers)
        res_text = await res.text()
        token, self._lang_map = self._get_token_and_map(res_text)
        self._domain_map = self._get_domains_map(res_text)
        self._map_dict = {**self._lang_map, **self._domain_map}
        self.data = {
            'from': self._lang_map[self.FROM],
            'to': self._lang_map[self.TO],
            'domain': self._domain_map[self.DOMAIN],
            'token': token,
        }
        self.signal.emit()

    async def async_trans(self, query: str) -> str:
        """异步获取翻译结果."""
        sign = await self._run_js(await self.load_js(self.js_name), query)
        self._set_random_ua()
        self.data.update({'sign': sign, 'query': query})
        async with self.session.post(
                self.POST_URL, headers=self.headers, data=self.data) as response:
            result = await response.json()
            assert (trans_result := result.get('trans_result')) is not None, \
                '出现未知错误'
            trans_result = trans_result['data'][0]['dst']
            return trans_result

    def _get_token_and_map(self, res):
        """获得token参数."""
        token = re.search(r"token: '(.*)',", res).group(1)
        lang_map = re.search(r'langList: ({[\s\S]*?})', res).group(1)
        lang_map = lang_map.replace("'", '"')
        lang_map = json.loads(lang_map)
        lang_map = {lang: abbre for abbre, lang in lang_map.items()}
        return token, lang_map

    def _get_domains_map(self, res) -> dict:
        """获得domain."""
        tree = fromstring(res)
        domain_trans_iter_wrappers = tree.xpath(
            '//div[@class="domain-trans domain-trans-small"]/div[2]/div')
        domain_map = {
            '通用': 'common',
        }
        for domain_trans_iter_wrapper in domain_trans_iter_wrappers:
            value = domain_trans_iter_wrapper.xpath(
                './div[1]/@data-domain-value')[0]
            key = domain_trans_iter_wrapper.xpath(
                './div[1]/span[1]/text()')[0]
            domain_map[key] = value
        return domain_map

    async def close(self):
        await super(BaiduTranslater, self).close()
        os.remove(await self.load_js(self.js_name))


exchange_py = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAQAAAAAYLlVAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAAmJLR0QA/4ePzL8AAAAHdElNRQfjAQkDAC7C/BYgAAADZklEQVRo3u2Zy08TURTGf9QiKFarKKWlLgiaqNGYGOPCd0xcuMVFlwpxo27EBS78A2wNAWGlhsSFysOtEtwYFWWBYoIJLRtlg2gNIG+llHZcFIY7w7Sd6QxMonx3c+feufN959y555xOYR3r+N+RtwrPdFIMjLFgj0kegoSJEKLUDnonQaTF1orXDvvDsoAkbWsvQRQgIWWXsMFiATF2c0K4PoifbmbW0gcltJDQ7wVnxoc5KaKAfEOHNUkDXs4KIwGghh/GBLg4wDEOU04xboMbJeFSjQSAG0T1O7GKTkZIKhxptoWyeHsRBVTylpil1KkWxpN9C3zUUsVWQw63EPvoWAXLs2yBU6C/z5kV83+YJYZkyBAJF27VWDsN2slp6YD5aOaCYiZOP+/o5iujJAzQJ/ER4pxi7Bk1fM+0qJBG1Tvfx3XKcBjeRijhqSoQtePT8LwHz7L/K5kUFsRopiIH6tSDg6q916JPpewwd1IxchdvhAVx6lYEEv1QJyNt65dEJngAcElx7p+wPWd68BDJQq8UOQ5beS4s6WWPCXpwEhKSkE/zHj/fBEZOEpUv5qg2RZ+yL0SEAe6mzYF+hkQBt4nLFz2W1HGqNzyzACdHhVtf6c9YGbDAT/03O9gr93/zyQJ6g3BQJvdnGbRDwPKZn+eXHQKWqx3JUMzPHflCiE/kEu3Nwk2+3J+2Q0A5RXJ/2A4BR9gs97/oKhSx8hdvKeflfoJehKA4hD/tohARwgS1C0tDqGZOZoxySo8AL63yPUF9xXVaVPBRYHzBNhiXL/s17fPSKlRLYVM+cPNYUfhcBngoF1BadauSXqKfkpzpXdQJiU+iK/UsH0EiRAhp2Kam1/37RtP5zYrCZ5KLS1Pp0qeaPkFLTvbn4eMafapasYnC1GQ6eKknoJh/zS2GDVXKDnZSwXFOc0iIfgAvucJwJgGlNKjoYYJpg1/V8tjIFjatGO/iKpFMC8XKzvrWyf5sypW1rZVtiiahAiHbFxJrMU8PjXQwl/1Wq7cgyQidVGmdofQv4T0CqjHjL2GSCcYY5DMfGGBK21ZtRLkJKgl91Bo8hhJxYszmmkO9tCkcmWsgMgG1BDOh2CIJ5rKhBRJsEKCUYPkW6PkGOsN7JHYwyiPqmbZWgN5zbfPfMOtYx7+Mv5MNkqRw/i3AAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDE5LTAxLTA5VDAzOjAwOjQ2KzA4OjAwQW/saAAAACV0RVh0ZGF0ZTptb2RpZnkAMjAxOS0wMS0wOVQwMzowMDo0NiswODowMDAyVNQAAABDdEVYdHNvZnR3YXJlAC91c3IvbG9jYWwvaW1hZ2VtYWdpY2svc2hhcmUvZG9jL0ltYWdlTWFnaWNrLTcvL2luZGV4Lmh0bWy9tXkKAAAAGHRFWHRUaHVtYjo6RG9jdW1lbnQ6OlBhZ2VzADGn/7svAAAAGHRFWHRUaHVtYjo6SW1hZ2U6OkhlaWdodAAxMjhDfEGAAAAAF3RFWHRUaHVtYjo6SW1hZ2U6OldpZHRoADEyONCNEd0AAAAZdEVYdFRodW1iOjpNaW1ldHlwZQBpbWFnZS9wbmc/slZOAAAAF3RFWHRUaHVtYjo6TVRpbWUAMTU0Njk3NDA0NktaAtgAAAARdEVYdFRodW1iOjpTaXplADI5NjNCi8zW6wAAAGJ0RVh0VGh1bWI6OlVSSQBmaWxlOi8vL2hvbWUvd3d3cm9vdC9uZXdzaXRlL3d3dy5lYXN5aWNvbi5uZXQvY2RuLWltZy5lYXN5aWNvbi5jbi9maWxlcy8xMTMvMTEzNzk0Ny5wbmeufgkkAAAAAElFTkSuQmCC"


class TransApp(object):
    """docstring for TransApp."""

    def __init__(self):
        super(TransApp, self).__init__()
        self.task_queue = deque(maxlen=3)
        self.clipboard = QApplication.clipboard()
        self.translater = BaiduTranslater()
        self.init_Ui()

    def init_Ui(self):
        app = self

        class TransUi(QMainWindow, Ui_MainWindow):
            """docstring for TransUi."""

            def __init__(self):
                super(TransUi, self).__init__()
                self.setupUi(self)

            def closeEvent(self, event):
                asyncio.create_task(app.close())
                result = QMessageBox.question(self, '请确认', '是否确认关闭',
                                              QMessageBox.Yes | QMessageBox.No)
                if result == QMessageBox.Yes:
                    event.accept()
                else:
                    event.ignore()

        # self.ui = QUiLoader().load('ui_translate.ui')
        self.ui = TransUi()

        def init():
            init_from_lang = self.translater.FROM
            init_to_lang = self.translater.TO
            init_domain = self.translater.DOMAIN
            langs = self.translater._lang_map.keys()
            domains = self.translater._domain_map.keys()
            self.ui.from_comboBox.addItems(langs)
            self.ui.to_comboBox.addItems(langs)
            self.ui.domain_comboBox.addItems(domains)
            self.ui.from_comboBox.currentIndexChanged[str].connect(
                self.reset_data('from'))
            self.ui.to_comboBox.currentIndexChanged[str].connect(
                self.reset_data('to'))
            self.ui.domain_comboBox.currentIndexChanged[str].connect(
                self.reset_data('domain'))
            self.ui.from_comboBox.activated.connect(lambda x: self.send_query())
            self.ui.to_comboBox.activated.connect(lambda x: self.send_query())
            self.ui.domain_comboBox.activated.connect(lambda x: self.send_query())
            self.ui.from_comboBox.setCurrentText(init_from_lang)
            self.ui.to_comboBox.setCurrentText(init_to_lang)
            self.ui.domain_comboBox.setCurrentText(init_domain)
            self.ui.from_textEdit.textChanged.connect(self.send_query)
            exchange_pixmap = QPixmap()
            exchange_pixmap.loadFromData(base64.b64decode(exchange_py.encode()))
            self.ui.exchangeButton.setIcon(exchange_pixmap)
            self.ui.exchangeButton.clicked.connect(self.exchange)
            self.ui.action.triggered.connect(self.copy)
            self.ui.action_bat.triggered.connect(self.get_bat_file())
        self.translater.signal.connect(init)

    @Slot()
    def get_bat_file(self):
        async def write():
            async with aiofile.open_async(
                    path := os.path.join(
                        os.path.expanduser('~'), 'Desktop', 'translater.bat'), 'w') as f:
                pass
            async with aiofile.open_async(path, 'a') as f:
                await f.write('@echo off\nif "%1" == "233" goto begin\n')
                await f.write(r'mshta vbscript:createobject("wscript.shell").run("%~nx0 233",0)(window.close)&&exit')
                await f.write(f'\n:begin\npython {__file__}')

        def connect_func():
            asyncio.create_task(write())
        return connect_func

    def reset_data(self, key: str) -> 'callable':
        map_dict = self.translater._map_dict

        @Slot(str)
        def reset(current_text: str):
            self.translater.data[key] = map_dict[current_text]
            # print(f'reset -> {current_text}')
            # print(self.translater.data)
        return reset

    def clear_edit(self):
        if not self.ui.from_textEdit.toPlainText():
            self.ui.to_textEdit.clear()

    @Slot()
    def send_query(self):
        query = self.ui.from_textEdit.toPlainText()
        asyncio.create_task(self.show_result(query))

    @Slot()
    def exchange(self):
        _from = self.ui.from_comboBox.currentText()
        to = self.ui.to_comboBox.currentText()
        self.ui.from_comboBox.setCurrentText(to)
        self.ui.to_comboBox.setCurrentText(_from)
        self.send_query()

    @Slot()
    def copy(self):
        text = self.ui.to_textEdit.toPlainText()
        self.clipboard.setText(text)

    async def show_result(self, query: str) -> None:
        self.task_queue.append(query)
        await asyncio.sleep(0.1)
        if self.task_queue:
            # print(self.task_queue)
            query = self.task_queue.popleft()
            if query:
                try:
                    result = await self.translater.async_trans(query)
                except AssertionError as e:
                    result = str(e)
                self.ui.to_textEdit.setPlainText(result)
            else:
                loop = asyncio.get_running_loop()
                loop.call_later(1, self.clear_edit)

    def show(self):
        self.ui.show()

    async def close(self):
        await self.translater.close()


def run():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    with loop:
        translater = TransApp()
        translater.show()
        loop.run_forever()
