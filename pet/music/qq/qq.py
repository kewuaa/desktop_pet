# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-02-22 22:10:35
# @Last Modified by:   None
# @Last Modified time: 2022-03-04 15:58:35
from re import compile
from datetime import datetime
from itertools import zip_longest
import os
import time
import json
import random

from playwright.async_api import async_playwright

from pet.music.musicer_model import SongInfo
from pet.music.musicer_model import SongUrl
from pet.music.musicer_model import SongID
from pet.music.musicer_model import BaseMusicer
from pet.music.musicer_model import CookieInvalidError


current_path, _ = os.path.split(os.path.realpath(__file__))
spare_cookie = '_qpsvr_localtk=0.4538522160856642; RK=g4zRPw2qGO; ptcz=b7a5f7280d89485721c5a14864bfc16b409647175102a691c7258f3c94ab1d4d; tvfe_boss_uuid=a6d9ec6d8f271197; pgv_pvid=6775997610; pgv_info=ssid=s4503669198; video_omgid=ddcf8ef1091f06fb; vversion_name=8.2.95; fqm_pvqid=1c9a74b8-b3c4-49c0-9256-828fb9d63049; fqm_sessionid=b13573dc-a886-44bc-a5ff-ff1853298284; ts_uid=3088992420; ptui_loginuin=1692525710; euin=oKCqow4A7KS5on**; tmeLoginType=2; pac_uid=1_692525710; iip=0; ts_refer=developer.aliyun.com/article/757367; ariaDefaultTheme=undefined; ts_last=y.qq.com/n/ryqq/search; login_type=1; psrf_musickey_createtime=1646552419; wxrefresh_token=; psrf_access_token_expiresAt=1654328419; psrf_qqrefresh_token=F2411FAA8F131C4BA3D358129EBC0196; psrf_qqaccess_token=42427D3B3BE26C71952C830186E8C9F6; qm_keyst=Q_H_L_54XXH1BpTa30Pj8UhDAyoBZm47E-FAOMModA4eDKFd0sZ49FKYVMdzA; wxopenid=; qqmusic_key=Q_H_L_54XXH1BpTa30Pj8UhDAyoBZm47E-FAOMModA4eDKFd0sZ49FKYVMdzA; wxunionid=; uin=1692525710; psrf_qqopenid=9F532E5A014BFC5DAADB28383F71273F; qm_keyst=Q_H_L_54XXH1BpTa30Pj8UhDAyoBZm47E-FAOMModA4eDKFd0sZ49FKYVMdzA; psrf_qqunionid=6E77AFE5B790D79310DFADC9A96A2C92'
SIGN_JS = 'd2luZG93ID0gZ2xvYmFsOw0KbmF2aWdhdG9yID0ge30NCmxvY2F0aW9uID0gew0KICAgICJob3N0IjogInkucXEuY29tIg0KfQ0KdmFyIG1haW4gPSBudWxsOw0KDQohZnVuY3Rpb24oZSkgew0KICAgIHZhciBuID0gInVuZGVmaW5lZCIgIT09IHR5cGVvZiBlID8gZSA6ICJ1bmRlZmluZWQiICE9PSB0eXBlb2Ygd2luZG93ID8gd2luZG93IDogInVuZGVmaW5lZCIgIT09IHR5cGVvZiBzZWxmID8gc2VsZiA6IHZvaWQgMDsNCiAgICB2YXIgciA9IGZ1bmN0aW9uKCkgew0KICAgICAgICBmdW5jdGlvbiBlKHQsIG4sIHIsIGksIG8sIGEsIHUsIGwpIHsNCiAgICAgICAgICAgIHZhciBjID0gIWk7DQogICAgICAgICAgICB0ID0gK3QsDQogICAgICAgICAgICBuID0gbiB8fCBbMF0sDQogICAgICAgICAgICBpID0gaSB8fCBbW3RoaXNdLCBbe31dXSwNCiAgICAgICAgICAgIG8gPSBvIHx8IHt9Ow0KICAgICAgICAgICAgdmFyIHMsIGYgPSBbXSwgcCA9IG51bGw7DQogICAgICAgICAgICBGdW5jdGlvbi5wcm90b3R5cGUuYmluZCB8fCAocyA9IFtdLnNsaWNlLA0KICAgICAgICAgICAgRnVuY3Rpb24ucHJvdG90eXBlLmJpbmQgPSBmdW5jdGlvbihlKSB7DQogICAgICAgICAgICAgICAgaWYgKCJmdW5jdGlvbiIgIT0gdHlwZW9mIHRoaXMpDQogICAgICAgICAgICAgICAgICAgIHRocm93IG5ldyBUeXBlRXJyb3IoImJpbmQxMDEiKTsNCiAgICAgICAgICAgICAgICB2YXIgdCA9IHMuY2FsbChhcmd1bWVudHMsIDEpDQogICAgICAgICAgICAgICAgICAsIG4gPSB0Lmxlbmd0aA0KICAgICAgICAgICAgICAgICAgLCByID0gdGhpcw0KICAgICAgICAgICAgICAgICAgLCBpID0gZnVuY3Rpb24oKSB7fQ0KICAgICAgICAgICAgICAgICAgLCBvID0gZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgICAgIHJldHVybiB0Lmxlbmd0aCA9IG4sDQogICAgICAgICAgICAgICAgICAgIHQucHVzaC5hcHBseSh0LCBhcmd1bWVudHMpLA0KICAgICAgICAgICAgICAgICAgICByLmFwcGx5KGkucHJvdG90eXBlLmlzUHJvdG90eXBlT2YodGhpcykgPyB0aGlzIDogZSwgdCkNCiAgICAgICAgICAgICAgICB9Ow0KICAgICAgICAgICAgICAgIHJldHVybiB0aGlzLnByb3RvdHlwZSAmJiAoaS5wcm90b3R5cGUgPSB0aGlzLnByb3RvdHlwZSksDQogICAgICAgICAgICAgICAgby5wcm90b3R5cGUgPSBuZXcgaSwNCiAgICAgICAgICAgICAgICBvDQogICAgICAgICAgICB9DQogICAgICAgICAgICApOw0KICAgICAgICAgICAgZm9yICh2YXIgZCA9IFtmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMl0gPSBpW2kubGVuZ3RoIC0gMl0gKyBpLnBvcCgpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGZvciAodmFyIGEgPSBuW3QrK10sIHUgPSBbXSwgbCA9IG5bdCsrXSwgYyA9IG5bdCsrXSwgcyA9IFtdLCBmID0gMDsgZiA8IGw7IGYrKykNCiAgICAgICAgICAgICAgICAgICAgdVtuW3QrK11dID0gaVtuW3QrK11dOw0KICAgICAgICAgICAgICAgIGZvciAoZiA9IDA7IGYgPCBjOyBmKyspDQogICAgICAgICAgICAgICAgICAgIHNbZl0gPSBuW3QrK107DQogICAgICAgICAgICAgICAgaS5wdXNoKChmdW5jdGlvbiB0KCkgew0KICAgICAgICAgICAgICAgICAgICB2YXIgaSA9IHUuc2xpY2UoMCk7DQogICAgICAgICAgICAgICAgICAgIGlbMF0gPSBbdGhpc10sDQogICAgICAgICAgICAgICAgICAgIGlbMV0gPSBbYXJndW1lbnRzXSwNCiAgICAgICAgICAgICAgICAgICAgaVsyXSA9IFt0XTsNCiAgICAgICAgICAgICAgICAgICAgZm9yICh2YXIgbCA9IDA7IGwgPCBzLmxlbmd0aCAmJiBsIDwgYXJndW1lbnRzLmxlbmd0aDsgbCsrKQ0KICAgICAgICAgICAgICAgICAgICAgICAgMCA8IHNbbF0gJiYgKGlbc1tsXV0gPSBbYXJndW1lbnRzW2xdXSk7DQogICAgICAgICAgICAgICAgICAgIHJldHVybiBlKGEsIG4sIHIsIGksIG8pDQogICAgICAgICAgICAgICAgfQ0KICAgICAgICAgICAgICAgICkpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGlbaS5sZW5ndGggLSAyXSA9IGlbaS5sZW5ndGggLSAyXSB8IGkucG9wKCkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaS5wdXNoKGlbblt0KytdXVswXSkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgdmFyIGUgPSBuW3QrK10NCiAgICAgICAgICAgICAgICAgICwgciA9IGlbaS5sZW5ndGggLSAyIC0gZV07DQogICAgICAgICAgICAgICAgaVtpLmxlbmd0aCAtIDIgLSBlXSA9IGkucG9wKCksDQogICAgICAgICAgICAgICAgaS5wdXNoKHIpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgdmFyIGUgPSBuW3QrK10NCiAgICAgICAgICAgICAgICAgICwgciA9IGUgPyBpLnNsaWNlKC1lKSA6IFtdOw0KICAgICAgICAgICAgICAgIGkubGVuZ3RoIC09IGUsDQogICAgICAgICAgICAgICAgZSA9IGkucG9wKCksDQogICAgICAgICAgICAgICAgaS5wdXNoKGVbMF1bZVsxXV0uYXBwbHkoZVswXSwgcikpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICB2YXIgZSA9IG5bdCsrXTsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMV0gJiYgKHQgPSBlKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICB2YXIgZSA9IG5bdCsrXQ0KICAgICAgICAgICAgICAgICAgLCByID0gZSA/IGkuc2xpY2UoLWUpIDogW107DQogICAgICAgICAgICAgICAgaS5sZW5ndGggLT0gZSwNCiAgICAgICAgICAgICAgICByLnVuc2hpZnQobnVsbCksDQogICAgICAgICAgICAgICAgaS5wdXNoKGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgICAgICByZXR1cm4gZnVuY3Rpb24oZSwgdCwgbikgew0KICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIG5ldyAoRnVuY3Rpb24uYmluZC5hcHBseShlLCB0KSkNCiAgICAgICAgICAgICAgICAgICAgfQ0KICAgICAgICAgICAgICAgICAgICAuYXBwbHkobnVsbCwgYXJndW1lbnRzKQ0KICAgICAgICAgICAgICAgIH0oaS5wb3AoKSwgcikpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGlbaS5sZW5ndGggLSAyXSA9IGlbaS5sZW5ndGggLSAyXSAtIGkucG9wKCkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgdmFyIGUgPSBpW2kubGVuZ3RoIC0gMl07DQogICAgICAgICAgICAgICAgZVswXVtlWzFdXSA9IGlbaS5sZW5ndGggLSAxXQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIHZhciBlID0gblt0KytdOw0KICAgICAgICAgICAgICAgIGlbZV0gPSB2b2lkIDAgPT09IGlbZV0gPyBbXSA6IGlbZV0NCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpLnB1c2goIWkucG9wKCkpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsICwgLCAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucHVzaChbblt0KytdXSkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaVtpLmxlbmd0aCAtIDFdID0gcltpW2kubGVuZ3RoIC0gMV1dDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaS5wdXNoKCIiKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGlbaS5sZW5ndGggLSAyXSA9IGlbaS5sZW5ndGggLSAyXSA8PCBpLnBvcCgpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgdmFyIGUgPSBpLnBvcCgpOw0KICAgICAgICAgICAgICAgIGkucHVzaChbaVtpLnBvcCgpXVswXSwgZV0pDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucHVzaChpW2kucG9wKClbMF1dWzBdKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGlbaS5sZW5ndGggLSAxXSA9IG5bdCsrXQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMl0gPSBpW2kubGVuZ3RoIC0gMl0gPj4gaS5wb3AoKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucHVzaCghMSkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaVtpLmxlbmd0aCAtIDJdID0gaVtpLmxlbmd0aCAtIDJdID4gaS5wb3AoKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGlbaS5sZW5ndGggLSAyXSA9IGlbaS5sZW5ndGggLSAyXSBeIGkucG9wKCkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaS5wdXNoKFtpLnBvcCgpLCBpLnBvcCgpXS5yZXZlcnNlKCkpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucG9wKCkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaVtpW2kubGVuZ3RoIC0gMl1bMF1dWzBdID0gaVtpLmxlbmd0aCAtIDFdDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsICwgLCAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucHVzaChpW2kubGVuZ3RoIC0gMV0pDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgcmV0dXJuICEwDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucHVzaChbciwgaS5wb3AoKV0pDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIHZhciBlID0gblt0KytdDQogICAgICAgICAgICAgICAgICAsIG8gPSBlID8gaS5zbGljZSgtZSkgOiBbXTsNCiAgICAgICAgICAgICAgICBpLmxlbmd0aCAtPSBlLA0KICAgICAgICAgICAgICAgIGkucHVzaChpLnBvcCgpLmFwcGx5KHIsIG8pKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMl0gPSBpW2kubGVuZ3RoIC0gMl0gPj0gaS5wb3AoKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCAsICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaS5sZW5ndGggPSBuW3QrK10NCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICB2YXIgZSA9IGkucG9wKCkNCiAgICAgICAgICAgICAgICAgICwgdCA9IGkucG9wKCk7DQogICAgICAgICAgICAgICAgaS5wdXNoKFt0WzBdW3RbMV1dLCBlXSkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMl0gPSBpW2kubGVuZ3RoIC0gMl0gJiBpLnBvcCgpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIHQgPSBuW3QrK10NCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMV0gKz0gU3RyaW5nLmZyb21DaGFyQ29kZShuW3QrK10pDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMl0gPSBpW2kubGVuZ3RoIC0gMl0gPT09IGkucG9wKCkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaS5wdXNoKHZvaWQgMCkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgdmFyIGUgPSBpLnBvcCgpOw0KICAgICAgICAgICAgICAgIGkucHVzaChlWzBdW2VbMV1dKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucHVzaCghMCkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMl0gPSBpW2kubGVuZ3RoIC0gMl0gKiBpLnBvcCgpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucHVzaChuW3QrK10pDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucHVzaCh0eXBlb2YgaS5wb3AoKSkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgIF07IDsgKQ0KICAgICAgICAgICAgICAgIHRyeSB7DQogICAgICAgICAgICAgICAgICAgIGZvciAodmFyIGggPSAhMTsgIWg7ICkNCiAgICAgICAgICAgICAgICAgICAgICAgIGggPSBkW25bdCsrXV0oKTsNCiAgICAgICAgICAgICAgICAgICAgaWYgKHApDQogICAgICAgICAgICAgICAgICAgICAgICB0aHJvdyBwOw0KICAgICAgICAgICAgICAgICAgICByZXR1cm4gYyA/IChpLnBvcCgpLA0KICAgICAgICAgICAgICAgICAgICBpLnNsaWNlKDMgKyBlLnYpKSA6IGkucG9wKCkNCiAgICAgICAgICAgICAgICB9IGNhdGNoIChtKSB7DQogICAgICAgICAgICAgICAgICAgIHZhciB2ID0gZi5wb3AoKTsNCiAgICAgICAgICAgICAgICAgICAgaWYgKHZvaWQgMCA9PT0gdikNCiAgICAgICAgICAgICAgICAgICAgICAgIHRocm93IG07DQogICAgICAgICAgICAgICAgICAgIHAgPSBtLA0KICAgICAgICAgICAgICAgICAgICB0ID0gdlswXSwNCiAgICAgICAgICAgICAgICAgICAgaS5sZW5ndGggPSB2WzFdLA0KICAgICAgICAgICAgICAgICAgICB2WzJdICYmIChpW3ZbMl1dWzBdID0gcCkNCiAgICAgICAgICAgICAgICB9DQogICAgICAgIH0NCiAgICAgICAgcmV0dXJuIGUudiA9IDUsDQogICAgICAgIGUoMCwgZnVuY3Rpb24oZSkgew0KICAgICAgICAgICAgdmFyIHQgPSBlWzFdDQogICAgICAgICAgICAgICwgbiA9IFtdDQogICAgICAgICAgICAgICwgciA9IGZ1bmN0aW9uKGUpIHsNCiAgICAgICAgICAgICAgICBmb3IgKHZhciB0LCBuLCByID0gIkFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXowMTIzNDU2Nzg5Ky89Ii5zcGxpdCgiIiksIGkgPSBTdHJpbmcoZSkucmVwbGFjZSgvWz1dKyQvLCAiIiksIG8gPSAwLCBhID0gMCwgdSA9ICIiOyBuID0gaS5jaGFyQXQoYSsrKTsgfm4gJiYgKHQgPSBvICUgNCA/IDY0ICogdCArIG4gOiBuLA0KICAgICAgICAgICAgICAgIG8rKyAlIDQpICYmICh1ICs9IFN0cmluZy5mcm9tQ2hhckNvZGUoMjU1ICYgdCA+PiAoLTIgKiBvICYgNikpKSkNCiAgICAgICAgICAgICAgICAgICAgbiA9IGZ1bmN0aW9uKGUsIHQsIG4pIHsNCiAgICAgICAgICAgICAgICAgICAgICAgIGlmICgiZnVuY3Rpb24iID09IHR5cGVvZiBBcnJheS5wcm90b3R5cGUuaW5kZXhPZikNCiAgICAgICAgICAgICAgICAgICAgICAgICAgICByZXR1cm4gQXJyYXkucHJvdG90eXBlLmluZGV4T2YuY2FsbChlLCB0LCBuKTsNCiAgICAgICAgICAgICAgICAgICAgICAgIHZhciByOw0KICAgICAgICAgICAgICAgICAgICAgICAgaWYgKG51bGwgPT0gZSkNCiAgICAgICAgICAgICAgICAgICAgICAgICAgICB0aHJvdyBuZXcgVHlwZUVycm9yKCciYXJyYXkiIGlzIG51bGwgb3Igbm90IGRlZmluZWQnKTsNCiAgICAgICAgICAgICAgICAgICAgICAgIHZhciBpID0gT2JqZWN0KGUpDQogICAgICAgICAgICAgICAgICAgICAgICAgICwgbyA9IGkubGVuZ3RoID4+PiAwOw0KICAgICAgICAgICAgICAgICAgICAgICAgaWYgKDAgPT0gbykNCiAgICAgICAgICAgICAgICAgICAgICAgICAgICByZXR1cm4gLTE7DQogICAgICAgICAgICAgICAgICAgICAgICBpZiAobyA8PSAobiB8PSAwKSkNCiAgICAgICAgICAgICAgICAgICAgICAgICAgICByZXR1cm4gLTE7DQogICAgICAgICAgICAgICAgICAgICAgICBmb3IgKHIgPSBNYXRoLm1heCgwIDw9IG4gPyBuIDogbyAtIE1hdGguYWJzKG4pLCAwKTsgciA8IG87IHIrKykNCiAgICAgICAgICAgICAgICAgICAgICAgICAgICBpZiAociBpbiBpICYmIGlbcl0gPT09IHQpDQogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiByOw0KICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIC0xDQogICAgICAgICAgICAgICAgICAgIH0ociwgbik7DQogICAgICAgICAgICAgICAgcmV0dXJuIHUNCiAgICAgICAgICAgIH0oZVswXSkNCiAgICAgICAgICAgICAgLCBpID0gdC5zaGlmdCgpDQogICAgICAgICAgICAgICwgbyA9IHQuc2hpZnQoKQ0KICAgICAgICAgICAgICAsIGEgPSAwOw0KICAgICAgICAgICAgZnVuY3Rpb24gdSgpIHsNCiAgICAgICAgICAgICAgICBmb3IgKDsgYSA9PT0gaTsgKQ0KICAgICAgICAgICAgICAgICAgICBuLnB1c2gobyksDQogICAgICAgICAgICAgICAgICAgIGErKywNCiAgICAgICAgICAgICAgICAgICAgaSA9IHQuc2hpZnQoKSwNCiAgICAgICAgICAgICAgICAgICAgbyA9IHQuc2hpZnQoKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgZm9yICh2YXIgbCA9IDA7IGwgPCByLmxlbmd0aDsgbCsrKSB7DQogICAgICAgICAgICAgICAgdmFyIGMgPSByLmNoYXJBdChsKS5jaGFyQ29kZUF0KDApOw0KICAgICAgICAgICAgICAgIHUoKSwNCiAgICAgICAgICAgICAgICBuLnB1c2goYyksDQogICAgICAgICAgICAgICAgYSsrDQogICAgICAgICAgICB9DQogICAgICAgICAgICByZXR1cm4gdSgpLA0KICAgICAgICAgICAgbg0KICAgICAgICB9KFsiTXdnT0FnNEREZ1FPQlE0R0RnYzRmem96Q1E0Q0RnTU9CQTRGRGdZT0J3NElGenBrT21VNlpqcHBPbTQ2WlJWRkZ6cG1PblU2Ympwak9uUTZhVHB2T200OUNVYzRYem9tRnpwa09tVTZaanBwT200NlpTNFhPbUU2YlRwa05UOEphU1lEQXk4QU9Id0pKaGM2WkRwbE9tWTZhVHB1T21VdUF3TUdBU1krTFFFUkFBRURPQU16Q2c0Q0RnTU9CQTRGRGdZT0J3NElEZ2tVQ0RnOE13Z09BZzRERGdRT0JRNEdEZ2NYT21jNmJEcHZPbUk2WVRwc0ZVVVhPblU2Ympwa09tVTZaanBwT200NlpUcGtQUkFKMWlZNDVnUW1GenBuT213NmJ6cGlPbUU2YkJVdEZ6cDNPbWs2Ympwa09tODZkeFZGRnpwMU9tNDZaRHBsT21ZNmFUcHVPbVU2WkQwUUNTWTRCaVlYT25jNmFUcHVPbVE2YnpwM0ZTMFhPbk02WlRwc09tWVZSUmM2ZFRwdU9tUTZaVHBtT21rNmJqcGxPbVE5RUFrbU9BRW1GenB6T21VNmJEcG1GUzArTFFHZUFBQXZBQ2NtSmhRSk9BMHpJZzRDRGdNT0JBNEZEZ1lPQnc0SURna09DZzRMRGd3T0RRNE9EZzhPRUE0UkRoSU9FdzRVRGhVT0ZnNFhEaGdPR1E0YURoc09IQTRkRGg0T0h3NGdGQWtYT2s4NllqcHFPbVU2WXpwMEZRb0FLeGM2TUNWRUFBd21KaXNYT2pFbFJBRU1KaVlyRnpveUpVUUNEQ1ltS3hjNk15VkVBd3dtSmlzWE9qUWxSQVFNSmlZckZ6bzFKVVFGRENZbUt4YzZOaVZFQmd3bUppc1hPamNsUkFjTUppWXJGem80SlVRSURDWW1LeGM2T1NWRUNRd21KaXNYT2tFbFJBb01KaVlyRnpwQ0pVUUxEQ1ltS3hjNlF5VkVEQXdtSmlzWE9rUWxSQTBNSmlZckZ6cEZKVVFPRENZbUt4YzZSaVZFSTBRVUN3d21KaWNtSmhRS0Z6cEJPa0k2UXpwRU9rVTZSanBIT2tnNlNUcEtPa3M2VERwTk9rNDZUenBRT2xFNlVqcFRPbFE2VlRwV09sYzZXRHBaT2xvNllUcGlPbU02WkRwbE9tWTZaenBvT21rNmFqcHJPbXc2YlRwdU9tODZjRHB4T25JNmN6cDBPblU2ZGpwM09uZzZlVHA2T2pBNk1Ub3lPak02TkRvMU9qWTZOem80T2prNkt6b3ZPajBuSmlZVUN4UWhGenBmT2w4NmN6cHBPbWM2YmpwZk9tZzZZVHB6T21nNlh6b3lPakE2TWpvd09qQTZNem93T2pVYlB3azRNeVloRkNFWE9sODZYenB6T21rNlp6cHVPbDg2YURwaE9uTTZhRHBmT2pJNk1Eb3lPakE2TURvek9qQTZOUnNEQXdZQkJBQW1GenAwT204NlZUcHdPbkE2WlRweU9rTTZZVHB6T21VbEJnQW5KaVlVREJjNmR6cHBPbTQ2WkRwdk9uY1ZSUmM2YnpwaU9tbzZaVHBqT25ROUNUZ0JKaGM2YmpwaE9uWTZhVHBuT21FNmREcHZPbklWUlJjNmJ6cGlPbW82WlRwak9uUTlDVGdESmhjNmJEcHZPbU02WVRwME9tazZienB1RlVVWE9tODZZanBxT21VNll6cDBQU2NtSmhRTkF3d0pPQW9tRnpwU09tVTZaenBGT25nNmNCVVhPa2c2WlRwaE9tUTZiRHBsT25NNmN4YzZhUzhDRnpwME9tVTZjenAwSlJjNmJqcGhPblk2YVRwbk9tRTZkRHB2T25JdUZ6cDFPbk02WlRweU9rRTZaenBsT200NmREVS9CZ0VuSmlZVURoUWhGenBmT2w4NmNUcHRPbVk2WlRwZk9uTTZhVHBuT200Nlh6cGpPbWc2WlRwak9tc2JQMFFCUFFrbUF3d0pPQWttQXcwUUNUZzRKaGM2YkRwdk9tTTZZVHAwT21rNmJ6cHVMaGM2YURwdk9uTTZkRFVYT21rNmJqcGtPbVU2ZURwUE9tWTFGenB4T25FNkxqcGpPbTg2YlFZQlJBQkVBUXNpSnlZbUZBOUJGenBCT25JNmNqcGhPbmtWQ2dBclJBQWxSQzVFR1FzTUppWXJSQUVsUkFRTUppWXJSQUlsUkFrTUppWXJSQU1sUkRWRUd3c01KaVlyUkFRbFJBTkVEUUFNSmlZclJBVWxSQUJFRkFBTUppWXJSQVlsUkM5RUZBc01KaVlyUkFjbFJDOUVFUXNNSmlZWE9tMDZZVHB3SlRnQk13c09BZzRERGdRT0JRNEdEZ2NPQ0JRSkF3b0pKZ01EUkFFQU9Bb21Bd01iUHkwQkFnRUpDd29PQXdZQkZ6cHFPbTg2YVRwdUpRUUFKaGNHQVNjbUpoUVFGenBCT25JNmNqcGhPbmtWQ2dBclJBQWxSQVpFREFBTUppWXJSQUVsUkFzTUppWXJSQUlsUkFNTUppWXJSQU1sUkFJTUppWXJSQVFsUkFFTUppWXJSQVVsUkFjTUppWXJSQVlsUkFZTUppWXJSQWNsUkRsRUlBc01KaVlYT20wNllUcHdKVGd4TXdzT0FnNEREZ1FPQlE0R0RnY09DQlFKQXdvSkpnTURSQUVBT0FFbUF3TWJQeTBCQWdFSkN3b09Bd1lCRnpwcU9tODZhVHB1SlJjR0FTY21KaFFSRnpwQk9uSTZjanBoT25rVkNnQXJSQUFsUkFoRUVVUU1Rd0FNSmlZclJBRWxSQXRFSWdBTUppWXJSQUlsUkRSRUhBQU1KaVlyUkFNbFJEeEVDQUFNSmlZclJBUWxSQTFFRGtRTlF3QU1KaVlyUkFVbFJBZEVERVFOUXdBTUppWXJSQVlsUkFkRURVUU1Rd0FNSmlZclJBY2xSQXRFRUVRTVF3QU1KaVlyUkFnbFJBVkVDRVFUUXdBTUppWXJSQWtsUkFwRURrUVBRd0FNSmlZclJBb2xSQkJFRVVRT1F3QU1KaVlyUkFzbFJCMUVQZ0FNSmlZclJBd2xSQXhFRVVNTUppWXJSQTBsUkFwRVJRQU1KaVlyUkE0bFJBZEVZUUFNSmlZclJEeEVMUXNsUkFZTUppWW5KaVlERGhBSkpqZ2VKaFFSRnpwQk9uSTZjanBoT25rVkNnQXJSQUFsUkJWRUJBQU1KaVlyUkFFbFJCdEVKd0FNSmlZclJBSWxSQUVNSmlZclJBTWxSRGhFQWdBTUppWXJSQVFsUkFORVZ3QU1KaVlyUkFVbFJEVkVHUUFNSmlZclJBWWxSRGxFUWdBTUppWXJSQWNsUkJwRUxRQU1KaVlyUkFnbFJDVkVCQXNNSmlZclJBa2xSQXdNSmlZclJBb2xSQWhFQ2tRUlF3QU1KaVlyUkFzbFJESkVLd0FNSmlZclJBd2xSQ0ZFQndBTUppWXJSQTBsUkFwRURFUU5Rd0FNSmlZclJBNGxSQzVFRUFBTUppWXJSQkZFQWdzbFJBaEVEMFFQUXdBTUppWW5KaVlVRWhjNlFUcHlPbkk2WVRwNUZRb0FKeVltRkJORUFDY21KaFFUSEVRVFJBTUxNQkFKSmpnVUpoUVVGQWtVQ3dNVFJBSkRHejhiUDBRMlJDWUxReFFKRkFzREUwUUNRMFFCQUJzL0d6OEFKeVltRkJVVUVRTVRHejhuSmlZVUVoYzZjRHAxT25NNmFCc0RGQU1WSkFZQkpoUVRLeHdyQkFFRUFFUUJBQ2NtSGdBRUFBSW1PRVFVRVJRTEZBa2hKd1FBSmljRUFDWW5KaVlVSFJjbkppWVVIa1FBSnlZbUZCNGNSQVV3RUFrbU9CUW1GQllVRWdNZVJBTkRHejhuSmlZVUZ4UVNBeDVFQTBORUFRQWJQeWNtSmhRWUZCSURIa1FEUTBRQ0FCcy9KeVltRkJrREZrUUNIeWNtSmhRYUF4WkVBemRFQkJrREYwUUVId0luSmlZVUd3TVhSQVZFQ2dBM1JBSVpBeGhFQmg4Q0p5WW1GQndER0VRMVJBb0FOeWNtSmhRZEF4MFVDZ01aR3o4QUZBb0RHaHMvQUJRS0F4c2JQd0FVQ2dNY0d6OEFKeVltRkI0ckhDc0VBUVFBUkFFQUp5WWVBQVFBQWlZNEx4UWRBeDBVQ2hRU1JBaEVCd0FiUDBRQ0h4cy9BQlFLRkJKRUMwUUVBQnMvUkFNM1JBUVpHejhBSnlZbUZCSWhKeVltRkI4VUhSYzZjanBsT25BNmJEcGhPbU02WlJzWE9sSTZaVHBuT2tVNmVEcHdGUmM2V3pwY09pODZLenBkRnpwbkx3SVhCZ0luSmlZVUlCYzZlanA2T21JRER3QURId0FERUFBbkppWVVEeFFRRkI4VUhSUUtJU2NFQUNZbkJBQW1Kd1FBSmljRUFDWW5KaVlVSUJjNmREcHZPa3c2YnpwM09tVTZjanBET21FNmN6cGxHd1lBTFFFQkFTRUlBeWNtSmhRSUZ6cGZPbWM2WlRwME9sTTZaVHBqT25VNmNqcHBPblE2ZVRwVE9tazZaenB1R3dNSkRDWW1QaTBCaHdBQUx3RW1QaTA9IiwgWzEzMywgMjYyOCwgMTU2LCAzNDAsIDI2NywgMjcyLCAyNzAsIDI4OCwgMzIxLCAzMjYsIDMyNCwgMzM4LCAzNTIsIDI1NzUsIDc4NiwgNzkwLCA3ODgsIDg2OSwgOTA0LCA5MDgsIDkwNiwgOTQ0LCA5NDUsIDk0OSwgOTQ3LCA5ODMsIDk5MSwgOTk1LCA5OTMsIDEwODUsIDExMzMsIDEyMTcsIDExMzgsIDExNDIsIDExNDAsIDExNDYsIDExNDcsIDExNTEsIDExNDksIDEyMTcsIDEzMzYsIDEzNzUsIDEzNTksIDEzNjksIDEzNjcsIDEzNzIsIDEzNzYsIDEzMzgsIDE1MDgsIDE1NDcsIDE1MzEsIDE1NDEsIDE1MzksIDE1NDQsIDE1NDgsIDE1MTAsIDE4MTMsIDE4MTgsIDE4MTYsIDIwMzYsIDIwNzMsIDIwNzgsIDIwNzYsIDIxNzQsIDIxNzIsIDIwNjIsIDIyMTMsIDIyMTgsIDIyMTYsIDIzODksIDIzODcsIDIyMDUsIDI1NzYsIDM1NF1dKSwgbikNCiAgICB9KCk7DQogICAgci5nID0gZnVuY3Rpb24oKSB7DQogICAgICAgIHJldHVybiByLnNoaWZ0KClbMF0NCiAgICB9DQogICAgLA0KICAgIG4uX19zaWduX2hhc2hfMjAyMDAzMDUgPSBmdW5jdGlvbihlKSB7DQogICAgICAgIGZ1bmN0aW9uIHQoZSwgdCkgew0KICAgICAgICAgICAgdmFyIG4gPSAoNjU1MzUgJiBlKSArICg2NTUzNSAmIHQpOw0KICAgICAgICAgICAgcmV0dXJuIChlID4+IDE2KSArICh0ID4+IDE2KSArIChuID4+IDE2KSA8PCAxNiB8IDY1NTM1ICYgbg0KICAgICAgICB9DQogICAgICAgIGZ1bmN0aW9uIG4oZSwgbiwgciwgaSwgbywgYSkgew0KICAgICAgICAgICAgcmV0dXJuIHQoKHUgPSB0KHQobiwgZSksIHQoaSwgYSkpKSA8PCAobCA9IG8pIHwgdSA+Pj4gMzIgLSBsLCByKTsNCiAgICAgICAgICAgIHZhciB1LCBsDQogICAgICAgIH0NCiAgICAgICAgZnVuY3Rpb24gcihlLCB0LCByLCBpLCBvLCBhLCB1KSB7DQogICAgICAgICAgICByZXR1cm4gbih0ICYgciB8IH50ICYgaSwgZSwgdCwgbywgYSwgdSkNCiAgICAgICAgfQ0KICAgICAgICBmdW5jdGlvbiBpKGUsIHQsIHIsIGksIG8sIGEsIHUpIHsNCiAgICAgICAgICAgIHJldHVybiBuKHQgJiBpIHwgciAmIH5pLCBlLCB0LCBvLCBhLCB1KQ0KICAgICAgICB9DQogICAgICAgIGZ1bmN0aW9uIG8oZSwgdCwgciwgaSwgbywgYSwgdSkgew0KICAgICAgICAgICAgcmV0dXJuIG4odCBeIHIgXiBpLCBlLCB0LCBvLCBhLCB1KQ0KICAgICAgICB9DQogICAgICAgIGZ1bmN0aW9uIGEoZSwgdCwgciwgaSwgbywgYSwgdSkgew0KICAgICAgICAgICAgcmV0dXJuIG4ociBeICh0IHwgfmkpLCBlLCB0LCBvLCBhLCB1KQ0KICAgICAgICB9DQogICAgICAgIGZ1bmN0aW9uIHUoZSkgew0KICAgICAgICAgICAgcmV0dXJuIGZ1bmN0aW9uKGUpIHsNCiAgICAgICAgICAgICAgICB2YXIgdCwgbiA9ICIiOw0KICAgICAgICAgICAgICAgIGZvciAodCA9IDA7IHQgPCAzMiAqIGUubGVuZ3RoOyB0ICs9IDgpDQogICAgICAgICAgICAgICAgICAgIG4gKz0gU3RyaW5nLmZyb21DaGFyQ29kZShlW3QgPj4gNV0gPj4+IHQgJSAzMiAmIDI1NSk7DQogICAgICAgICAgICAgICAgcmV0dXJuIG4NCiAgICAgICAgICAgIH0oZnVuY3Rpb24oZSwgbikgew0KICAgICAgICAgICAgICAgIGVbbiA+PiA1XSB8PSAxMjggPDwgbiAlIDMyLA0KICAgICAgICAgICAgICAgIGVbMTQgKyAobiArIDY0ID4+PiA5IDw8IDQpXSA9IG47DQogICAgICAgICAgICAgICAgdmFyIHUsIGwsIGMsIHMsIGYsIHAgPSAxNzMyNTg0MTkzLCBkID0gLTI3MTczMzg3OSwgaCA9IC0xNzMyNTg0MTk0LCB2ID0gMjcxNzMzODc4Ow0KICAgICAgICAgICAgICAgIGZvciAodSA9IDA7IHUgPCBlLmxlbmd0aDsgdSArPSAxNikNCiAgICAgICAgICAgICAgICAgICAgbCA9IHAsDQogICAgICAgICAgICAgICAgICAgIGMgPSBkLA0KICAgICAgICAgICAgICAgICAgICBzID0gaCwNCiAgICAgICAgICAgICAgICAgICAgZiA9IHYsDQogICAgICAgICAgICAgICAgICAgIHAgPSByKHAsIGQsIGgsIHYsIGVbdV0sIDcsIC02ODA4NzY5MzYpLA0KICAgICAgICAgICAgICAgICAgICB2ID0gcih2LCBwLCBkLCBoLCBlW3UgKyAxXSwgMTIsIC0zODk1NjQ1ODYpLA0KICAgICAgICAgICAgICAgICAgICBoID0gcihoLCB2LCBwLCBkLCBlW3UgKyAyXSwgMTcsIDYwNjEwNTgxOSksDQogICAgICAgICAgICAgICAgICAgIGQgPSByKGQsIGgsIHYsIHAsIGVbdSArIDNdLCAyMiwgLTEwNDQ1MjUzMzApLA0KICAgICAgICAgICAgICAgICAgICBwID0gcihwLCBkLCBoLCB2LCBlW3UgKyA0XSwgNywgLTE3NjQxODg5NyksDQogICAgICAgICAgICAgICAgICAgIHYgPSByKHYsIHAsIGQsIGgsIGVbdSArIDVdLCAxMiwgMTIwMDA4MDQyNiksDQogICAgICAgICAgICAgICAgICAgIGggPSByKGgsIHYsIHAsIGQsIGVbdSArIDZdLCAxNywgLTE0NzMyMzEzNDEpLA0KICAgICAgICAgICAgICAgICAgICBkID0gcihkLCBoLCB2LCBwLCBlW3UgKyA3XSwgMjIsIC00NTcwNTk4MyksDQogICAgICAgICAgICAgICAgICAgIHAgPSByKHAsIGQsIGgsIHYsIGVbdSArIDhdLCA3LCAxNzcwMDM1NDE2KSwNCiAgICAgICAgICAgICAgICAgICAgdiA9IHIodiwgcCwgZCwgaCwgZVt1ICsgOV0sIDEyLCAtMTk1ODQxNDQxNyksDQogICAgICAgICAgICAgICAgICAgIGggPSByKGgsIHYsIHAsIGQsIGVbdSArIDEwXSwgMTcsIC00MjA2MyksDQogICAgICAgICAgICAgICAgICAgIGQgPSByKGQsIGgsIHYsIHAsIGVbdSArIDExXSwgMjIsIC0xOTkwNDA0MTYyKSwNCiAgICAgICAgICAgICAgICAgICAgcCA9IHIocCwgZCwgaCwgdiwgZVt1ICsgMTJdLCA3LCAxODA0NjAzNjgyKSwNCiAgICAgICAgICAgICAgICAgICAgdiA9IHIodiwgcCwgZCwgaCwgZVt1ICsgMTNdLCAxMiwgLTQwMzQxMTAxKSwNCiAgICAgICAgICAgICAgICAgICAgaCA9IHIoaCwgdiwgcCwgZCwgZVt1ICsgMTRdLCAxNywgLTE1MDIwMDIyOTApLA0KICAgICAgICAgICAgICAgICAgICBwID0gaShwLCBkID0gcihkLCBoLCB2LCBwLCBlW3UgKyAxNV0sIDIyLCAxMjM2NTM1MzI5KSwgaCwgdiwgZVt1ICsgMV0sIDUsIC0xNjU3OTY1MTApLA0KICAgICAgICAgICAgICAgICAgICB2ID0gaSh2LCBwLCBkLCBoLCBlW3UgKyA2XSwgOSwgLTEwNjk1MDE2MzIpLA0KICAgICAgICAgICAgICAgICAgICBoID0gaShoLCB2LCBwLCBkLCBlW3UgKyAxMV0sIDE0LCA2NDM3MTc3MTMpLA0KICAgICAgICAgICAgICAgICAgICBkID0gaShkLCBoLCB2LCBwLCBlW3VdLCAyMCwgLTM3Mzg5NzMwMiksDQogICAgICAgICAgICAgICAgICAgIHAgPSBpKHAsIGQsIGgsIHYsIGVbdSArIDVdLCA1LCAtNzAxNTU4NjkxKSwNCiAgICAgICAgICAgICAgICAgICAgdiA9IGkodiwgcCwgZCwgaCwgZVt1ICsgMTBdLCA5LCAzODAxNjA4MyksDQogICAgICAgICAgICAgICAgICAgIGggPSBpKGgsIHYsIHAsIGQsIGVbdSArIDE1XSwgMTQsIC02NjA0NzgzMzUpLA0KICAgICAgICAgICAgICAgICAgICBkID0gaShkLCBoLCB2LCBwLCBlW3UgKyA0XSwgMjAsIC00MDU1Mzc4NDgpLA0KICAgICAgICAgICAgICAgICAgICBwID0gaShwLCBkLCBoLCB2LCBlW3UgKyA5XSwgNSwgNTY4NDQ2NDM4KSwNCiAgICAgICAgICAgICAgICAgICAgdiA9IGkodiwgcCwgZCwgaCwgZVt1ICsgMTRdLCA5LCAtMTAxOTgwMzY5MCksDQogICAgICAgICAgICAgICAgICAgIGggPSBpKGgsIHYsIHAsIGQsIGVbdSArIDNdLCAxNCwgLTE4NzM2Mzk2MSksDQogICAgICAgICAgICAgICAgICAgIGQgPSBpKGQsIGgsIHYsIHAsIGVbdSArIDhdLCAyMCwgMTE2MzUzMTUwMSksDQogICAgICAgICAgICAgICAgICAgIHAgPSBpKHAsIGQsIGgsIHYsIGVbdSArIDEzXSwgNSwgLTE0NDQ2ODE0NjcpLA0KICAgICAgICAgICAgICAgICAgICB2ID0gaSh2LCBwLCBkLCBoLCBlW3UgKyAyXSwgOSwgLTUxNDAzNzg0KSwNCiAgICAgICAgICAgICAgICAgICAgaCA9IGkoaCwgdiwgcCwgZCwgZVt1ICsgN10sIDE0LCAxNzM1MzI4NDczKSwNCiAgICAgICAgICAgICAgICAgICAgcCA9IG8ocCwgZCA9IGkoZCwgaCwgdiwgcCwgZVt1ICsgMTJdLCAyMCwgLTE5MjY2MDc3MzQpLCBoLCB2LCBlW3UgKyA1XSwgNCwgLTM3ODU1OCksDQogICAgICAgICAgICAgICAgICAgIHYgPSBvKHYsIHAsIGQsIGgsIGVbdSArIDhdLCAxMSwgLTIwMjI1NzQ0NjMpLA0KICAgICAgICAgICAgICAgICAgICBoID0gbyhoLCB2LCBwLCBkLCBlW3UgKyAxMV0sIDE2LCAxODM5MDMwNTYyKSwNCiAgICAgICAgICAgICAgICAgICAgZCA9IG8oZCwgaCwgdiwgcCwgZVt1ICsgMTRdLCAyMywgLTM1MzA5NTU2KSwNCiAgICAgICAgICAgICAgICAgICAgcCA9IG8ocCwgZCwgaCwgdiwgZVt1ICsgMV0sIDQsIC0xNTMwOTkyMDYwKSwNCiAgICAgICAgICAgICAgICAgICAgdiA9IG8odiwgcCwgZCwgaCwgZVt1ICsgNF0sIDExLCAxMjcyODkzMzUzKSwNCiAgICAgICAgICAgICAgICAgICAgaCA9IG8oaCwgdiwgcCwgZCwgZVt1ICsgN10sIDE2LCAtMTU1NDk3NjMyKSwNCiAgICAgICAgICAgICAgICAgICAgZCA9IG8oZCwgaCwgdiwgcCwgZVt1ICsgMTBdLCAyMywgLTEwOTQ3MzA2NDApLA0KICAgICAgICAgICAgICAgICAgICBwID0gbyhwLCBkLCBoLCB2LCBlW3UgKyAxM10sIDQsIDY4MTI3OTE3NCksDQogICAgICAgICAgICAgICAgICAgIHYgPSBvKHYsIHAsIGQsIGgsIGVbdV0sIDExLCAtMzU4NTM3MjIyKSwNCiAgICAgICAgICAgICAgICAgICAgaCA9IG8oaCwgdiwgcCwgZCwgZVt1ICsgM10sIDE2LCAtNzIyNTIxOTc5KSwNCiAgICAgICAgICAgICAgICAgICAgZCA9IG8oZCwgaCwgdiwgcCwgZVt1ICsgNl0sIDIzLCA3NjAyOTE4OSksDQogICAgICAgICAgICAgICAgICAgIHAgPSBvKHAsIGQsIGgsIHYsIGVbdSArIDldLCA0LCAtNjQwMzY0NDg3KSwNCiAgICAgICAgICAgICAgICAgICAgdiA9IG8odiwgcCwgZCwgaCwgZVt1ICsgMTJdLCAxMSwgLTQyMTgxNTgzNSksDQogICAgICAgICAgICAgICAgICAgIGggPSBvKGgsIHYsIHAsIGQsIGVbdSArIDE1XSwgMTYsIDUzMDc0MjUyMCksDQogICAgICAgICAgICAgICAgICAgIHAgPSBhKHAsIGQgPSBvKGQsIGgsIHYsIHAsIGVbdSArIDJdLCAyMywgLTk5NTMzODY1MSksIGgsIHYsIGVbdV0sIDYsIC0xOTg2MzA4NDQpLA0KICAgICAgICAgICAgICAgICAgICB2ID0gYSh2LCBwLCBkLCBoLCBlW3UgKyA3XSwgMTAsIDExMjY4OTE0MTUpLA0KICAgICAgICAgICAgICAgICAgICBoID0gYShoLCB2LCBwLCBkLCBlW3UgKyAxNF0sIDE1LCAtMTQxNjM1NDkwNSksDQogICAgICAgICAgICAgICAgICAgIGQgPSBhKGQsIGgsIHYsIHAsIGVbdSArIDVdLCAyMSwgLTU3NDM0MDU1KSwNCiAgICAgICAgICAgICAgICAgICAgcCA9IGEocCwgZCwgaCwgdiwgZVt1ICsgMTJdLCA2LCAxNzAwNDg1NTcxKSwNCiAgICAgICAgICAgICAgICAgICAgdiA9IGEodiwgcCwgZCwgaCwgZVt1ICsgM10sIDEwLCAtMTg5NDk4NjYwNiksDQogICAgICAgICAgICAgICAgICAgIGggPSBhKGgsIHYsIHAsIGQsIGVbdSArIDEwXSwgMTUsIC0xMDUxNTIzKSwNCiAgICAgICAgICAgICAgICAgICAgZCA9IGEoZCwgaCwgdiwgcCwgZVt1ICsgMV0sIDIxLCAtMjA1NDkyMjc5OSksDQogICAgICAgICAgICAgICAgICAgIHAgPSBhKHAsIGQsIGgsIHYsIGVbdSArIDhdLCA2LCAxODczMzEzMzU5KSwNCiAgICAgICAgICAgICAgICAgICAgdiA9IGEodiwgcCwgZCwgaCwgZVt1ICsgMTVdLCAxMCwgLTMwNjExNzQ0KSwNCiAgICAgICAgICAgICAgICAgICAgaCA9IGEoaCwgdiwgcCwgZCwgZVt1ICsgNl0sIDE1LCAtMTU2MDE5ODM4MCksDQogICAgICAgICAgICAgICAgICAgIGQgPSBhKGQsIGgsIHYsIHAsIGVbdSArIDEzXSwgMjEsIDEzMDkxNTE2NDkpLA0KICAgICAgICAgICAgICAgICAgICBwID0gYShwLCBkLCBoLCB2LCBlW3UgKyA0XSwgNiwgLTE0NTUyMzA3MCksDQogICAgICAgICAgICAgICAgICAgIHYgPSBhKHYsIHAsIGQsIGgsIGVbdSArIDExXSwgMTAsIC0xMTIwMjEwMzc5KSwNCiAgICAgICAgICAgICAgICAgICAgaCA9IGEoaCwgdiwgcCwgZCwgZVt1ICsgMl0sIDE1LCA3MTg3ODcyNTkpLA0KICAgICAgICAgICAgICAgICAgICBkID0gYShkLCBoLCB2LCBwLCBlW3UgKyA5XSwgMjEsIC0zNDM0ODU1NTEpLA0KICAgICAgICAgICAgICAgICAgICBwID0gdChwLCBsKSwNCiAgICAgICAgICAgICAgICAgICAgZCA9IHQoZCwgYyksDQogICAgICAgICAgICAgICAgICAgIGggPSB0KGgsIHMpLA0KICAgICAgICAgICAgICAgICAgICB2ID0gdCh2LCBmKTsNCiAgICAgICAgICAgICAgICByZXR1cm4gW3AsIGQsIGgsIHZdDQogICAgICAgICAgICB9KGZ1bmN0aW9uKGUpIHsNCiAgICAgICAgICAgICAgICB2YXIgdCwgbiA9IFtdOw0KICAgICAgICAgICAgICAgIGZvciAoblsoZS5sZW5ndGggPj4gMikgLSAxXSA9IHZvaWQgMCwNCiAgICAgICAgICAgICAgICB0ID0gMDsgdCA8IG4ubGVuZ3RoOyB0ICs9IDEpDQogICAgICAgICAgICAgICAgICAgIG5bdF0gPSAwOw0KICAgICAgICAgICAgICAgIGZvciAodCA9IDA7IHQgPCA4ICogZS5sZW5ndGg7IHQgKz0gOCkNCiAgICAgICAgICAgICAgICAgICAgblt0ID4+IDVdIHw9ICgyNTUgJiBlLmNoYXJDb2RlQXQodCAvIDgpKSA8PCB0ICUgMzI7DQogICAgICAgICAgICAgICAgcmV0dXJuIG4NCiAgICAgICAgICAgIH0oZSksIDggKiBlLmxlbmd0aCkpDQogICAgICAgIH0NCiAgICAgICAgZnVuY3Rpb24gbChlKSB7DQogICAgICAgICAgICByZXR1cm4gdSh1bmVzY2FwZShlbmNvZGVVUklDb21wb25lbnQoZSkpKQ0KICAgICAgICB9DQogICAgICAgIHJldHVybiBmdW5jdGlvbihlKSB7DQogICAgICAgICAgICB2YXIgdCwgbiwgciA9ICIiOw0KICAgICAgICAgICAgZm9yIChuID0gMDsgbiA8IGUubGVuZ3RoOyBuICs9IDEpDQogICAgICAgICAgICAgICAgdCA9IGUuY2hhckNvZGVBdChuKSwNCiAgICAgICAgICAgICAgICByICs9ICIwMTIzNDU2Nzg5YWJjZGVmIi5jaGFyQXQodCA+Pj4gNCAmIDE1KSArICIwMTIzNDU2Nzg5YWJjZGVmIi5jaGFyQXQoMTUgJiB0KTsNCiAgICAgICAgICAgIHJldHVybiByDQogICAgICAgIH0obChlKSkNCiAgICB9DQogICAgOw0KICAgIHZhciBpID0gbi5fZ2V0U2VjdXJpdHlTaWduOw0KICAgIGRlbGV0ZSBuLl9nZXRTZWN1cml0eVNpZ247DQogICAgbWFpbiA9IGkNCn0od2luZG93KQ0KLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vDQphcmdzID0gcHJvY2Vzcy5hcmd2LnNsaWNlKDIpDQpkYXRhID0gYXJncy5qb2luKCcgJykNCmNvbnNvbGUubG9nKG1haW4oZGF0YSkpDQo='


def ve(e, t):
    (n := list(str(e))).reverse()
    (a := list(str(t))).reverse()
    r = [0] * (len(n) + len(a))
    for l, al in enumerate(a):
        for u, nu in enumerate(n):
            r[l + u] += int(al) * int(nu)
            r[l + u + 1] += int(r[l + u] / 10)
            r[l + u] %= 10
    r.reverse()
    r[0] or r.pop(0)
    return ''.join(str(i) for i in r)


def ye(e, t):
    nn = []
    (n := list(str(e))).reverse()
    (a := list(str(t))).reverse()
    i = 0
    for nu, au in zip_longest(n, a, fillvalue=0):
        l = round(int(nu)) + round(int(au)) + i
        nn.append(str(l % 10))
        i = 1 if l >= 10 else 0
    i == 1 and nn.append('1')
    nn.reverse()
    return ''.join(nn)


def get_time():
    t = datetime.now()
    return (
        (t.hour * 60 + t.minute) * 60 + t.second) * 1000 + t.microsecond // 1000


def Ee(e):
    t = ve(e, '18014398509481984')  # '54043195528445952'
    n = ve(round(random.random() * 4194304), '4294967296')
    r = get_time()
    return ye(ye(t, n), r)


class Musicer(BaseMusicer):
    """docstring for Musicer."""

    SEARCH_URL = 'https://u.y.qq.com/cgi-bin/musics.fcg?_=%s&sign=%s'
    SEARCH_DATA = {
##        "comm": {
##            "cv": 4747474,
##            "ct": 24,
##            "format": "json",
##            "inCharset": "utf-8",
##            "outCharset": "utf-8",
##            "notice": 0,
##            "platform": "yqq.json",
##            "needNewCode": 1,
##            "uin": 1692525710,
##            "g_tk_new_20200303": 1252795051,
##            "g_tk": 1252795051
##        },
        "req_1": {
            "method": "DoSearchForQQMusicDesktop",
            "module": "music.search.SearchCgiService",
            "param": {
                "remoteplace": "txt.yqq.center",
                "searchid": "",
                "search_type": 0,
                "query": "",
                "page_num": 1,
                "num_per_page": 10,
            },
        },
    }
    SONG_URL = 'https://u.y.qq.com/cgi-bin/musics.fcg?_=%s&sign=%s'
    URL_DATA = {
        "req_7":{
            "module":"vkey.GetVkeyServer",
            "method":"CgiGetVkey",
            "param":{
                "guid":"9000858194",
                "songmid":[
                    ""
                ],
                "songtype":[
                    0
                ],
                "uin":"1692525710",
                "loginflag":1,
                "platform":"20"
            }
        }
    }

    def __init__(self):
        super(Musicer, self).__init__(
            current_path=current_path, js=SIGN_JS)
        self.headers['cookie'] = spare_cookie
        self.headers['referer'] = 'https://y.qq.com/'
        self.js_name = self._get_random_name()
        self._route_compile = compile(r'(\.png$)|(\.jpe?g$)')
        self._match_compile = compile(r'ssl.+login\?')

    async def _get_song_info(self, song):
        time_stamp = int(time.time() * 1000)
        self.SEARCH_DATA['req_1']['param']['searchid'] = Ee(3)
        self.SEARCH_DATA['req_1']['param']['query'] = song
        self._set_random_ua()
        _data = json.dumps(self.SEARCH_DATA, ensure_ascii=False)
        data = json.dumps(_data, ensure_ascii=False)
        res = await self.session.post(
            self.SEARCH_URL % (
                time_stamp, await self._run_js(data)),
            headers=self.headers,
            data=_data)
        assert (status := res.status), f'response: {status}'
        result_dict = await res.json(content_type=None)
        if not (songs := result_dict['req_1']['data']['body']['song']['list']):
            raise CookieInvalidError
        return [SongInfo(f'QQ: {song["name"]}-->{song["singer"][0]["name"]}-->《{song["album"]["name"]}》',
                         SongID((str(song['mid']),), 'qq'))
                for song in songs]

    async def _get_song_url(self, _id):
        time_stamp = int(time.time() * 1000)
        self.URL_DATA['req_7']['param']['songmid'][0] = _id
        self._set_random_ua()
        _data = json.dumps(self.URL_DATA, ensure_ascii=False)
        data = json.dumps(_data, ensure_ascii=False)
        res = await self.session.post(
            self.SONG_URL % (time_stamp, await self._run_js(data)),
            headers=self.headers,
            data=_data)
        assert (status := res.status) == 200, f'response: {status}'
        result_dict = await res.json(content_type=None)
        if (result_dict := result_dict['req_7'])['code'] != 0:
            raise CookieInvalidError
        url = 'https://dl.stream.qqmusic.qq.com/' + result_dict['data']['midurlinfo'][0]['purl']
        return SongUrl(url)

    # async def _login(self, login_id, password, **kwargs):
    #     async with async_playwright() as p:
    #         browser = await p.chromium.launch(headless=False)
    #         context = await browser.new_context()
    #         await context.route(self._route_compile, lambda route: route.abort())
    #         page = await context.new_page()
    #         page.on('request', self._get_response)
    #         await page.goto('https://y.qq.com/')
    #         await page.click('//*[@id="app"]//a[@class="top_login__link"]')
    #         login_frame = page.frame_locator('//iframe[@name="login_frame"]')
    #         await login_frame.frame_locator('//iframe[@name="ptlogin_iframe"]').locator(
    #             '//a[@id="switcher_plogin"]').click()
    #         login_frame = login_frame.frame_locator('//iframe[@name="ptlogin_iframe"]')
    #         await (id_frame := login_frame.locator('//input[@name="u"]')).click()
    #         await id_frame.fill(login_id)
    #         await id_frame.press("Tab")
    #         await (password_frame := login_frame.locator('//input[@name="p"]')).fill(password)
    #         async with page.expect_navigation():
    #             await password_frame.press('Enter')
    #         import asyncio
    #         await asyncio.sleep(3)
    #         await page.close()
    #         await context.close()
    #         await browser.close()
    #         assert False, 'test'

    # def _get_response(self, request):
    #     url = request.url
    #     if self._match_compile.search(url) is None:
    #         return
    #     else:
    #         res = request.response
    #         print(res)
        
