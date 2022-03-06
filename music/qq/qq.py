# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-02-22 22:10:35
# @Last Modified by:   None
# @Last Modified time: 2022-03-04 15:58:35
import os
current_path, _ = os.path.split(os.path.realpath(__file__))
if __name__ == '__main__':
    import sys
    sys.path.append(os.path.join(current_path, '..'))
    sys.path.append(os.path.join(current_path, '../..'))

from datetime import datetime
from itertools import zip_longest
import time
import json
import random
import hashlib
import asyncio

from hzy import fake_ua
try:
    from model import SongInfo
    from model import SongUrl
    from model import SongID
    from model import BaseMusicer
    from model import CookieInvalidError
except ImportError:
    from ..model import SongInfo
    from ..model import SongUrl
    from ..model import SongID
    from ..model import BaseMusicer
    from ..model import CookieInvalidError


ua = fake_ua.UserAgent()
spare_cookie = '_qpsvr_localtk=0.4538522160856642; RK=g4zRPw2qGO; ptcz=b7a5f7280d89485721c5a14864bfc16b409647175102a691c7258f3c94ab1d4d; tvfe_boss_uuid=a6d9ec6d8f271197; pgv_pvid=6775997610; pgv_info=ssid=s4503669198; video_omgid=ddcf8ef1091f06fb; vversion_name=8.2.95; fqm_pvqid=1c9a74b8-b3c4-49c0-9256-828fb9d63049; fqm_sessionid=b13573dc-a886-44bc-a5ff-ff1853298284; ts_uid=3088992420; ptui_loginuin=1692525710; euin=oKCqow4A7KS5on**; tmeLoginType=2; pac_uid=1_692525710; iip=0; ts_refer=developer.aliyun.com/article/757367; ariaDefaultTheme=undefined; ts_last=y.qq.com/n/ryqq/search; login_type=1; psrf_musickey_createtime=1646552419; wxrefresh_token=; psrf_access_token_expiresAt=1654328419; psrf_qqrefresh_token=F2411FAA8F131C4BA3D358129EBC0196; psrf_qqaccess_token=42427D3B3BE26C71952C830186E8C9F6; qm_keyst=Q_H_L_54XXH1BpTa30Pj8UhDAyoBZm47E-FAOMModA4eDKFd0sZ49FKYVMdzA; wxopenid=; qqmusic_key=Q_H_L_54XXH1BpTa30Pj8UhDAyoBZm47E-FAOMModA4eDKFd0sZ49FKYVMdzA; wxunionid=; uin=1692525710; psrf_qqopenid=9F532E5A014BFC5DAADB28383F71273F; qm_keyst=Q_H_L_54XXH1BpTa30Pj8UhDAyoBZm47E-FAOMModA4eDKFd0sZ49FKYVMdzA; psrf_qqunionid=6E77AFE5B790D79310DFADC9A96A2C92'
SIGN_JS = 'LyoNCiogQEF1dGhvcjoga2V3dWFhDQoqIEBEYXRlOiAgIDIwMjItMDMtMDIgMDk6MzE6MDUNCiogQExhc3QgTW9kaWZpZWQgYnk6ICAgTm9uZQ0KKiBATGFzdCBNb2RpZmllZCB0aW1lOiAyMDIyLTAzLTA2IDE0OjUzOjAwDQoqLw0Kd2luZG93ID0gZ2xvYmFsOw0KbmF2aWdhdG9yID0gew0KICAgIC8vICdhcHBDb2RlTmFtZSc6ICJNb3ppbGxhIiwNCiAgICAvLyAnYXBwTmFtZSc6ICJOZXRzY2FwZSIsDQogICAgLy8gJ2FwcFZlcnNpb24nOiAiNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS85OC4wLjQ3NTguMTAyIFNhZmFyaS81MzcuMzYiLA0KICAgIC8vICd1c2VyQWdlbnQnOiAiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzk4LjAuNDc1OC4xMDIgU2FmYXJpLzUzNy4zNiINCn0NCmxvY2F0aW9uID0gew0KICAgIC8vICJhbmNlc3Rvck9yaWdpbnMiOiB7fSwNCiAgICAvLyAiaHJlZiI6ICJodHRwczovL3kucXEuY29tL24vcnlxcS9zZWFyY2g/dz0lRTUlODglOUElRTUlODglOUElRTUlQTUlQkQmdD1zb25nJnJlbW90ZXBsYWNlPXR4dC55cXEuY2VudGVyIiwNCiAgICAvLyAib3JpZ2luIjogImh0dHBzOi8veS5xcS5jb20iLA0KICAgIC8vICJwcm90b2NvbCI6ICJodHRwczoiLA0KICAgICJob3N0IjogInkucXEuY29tIiwNCiAgICAvLyAiaG9zdG5hbWUiOiAieS5xcS5jb20iLA0KICAgIC8vICJwb3J0IjogIiIsDQogICAgLy8gInBhdGhuYW1lIjogIi9uL3J5cXEvc2VhcmNoIiwNCiAgICAvLyAic2VhcmNoIjogIj93PSVFNSU4OCU5QSVFNSU4OCU5QSVFNSVBNSVCRCZ0PXNvbmcmcmVtb3RlcGxhY2U9dHh0LnlxcS5jZW50ZXIiLA0KICAgIC8vICJoYXNoIjogIiINCn0NCnZhciBtYWluID0gbnVsbDsNCg0KIWZ1bmN0aW9uKGUpIHsNCiAgICB2YXIgbiA9ICJ1bmRlZmluZWQiICE9PSB0eXBlb2YgZSA/IGUgOiAidW5kZWZpbmVkIiAhPT0gdHlwZW9mIHdpbmRvdyA/IHdpbmRvdyA6ICJ1bmRlZmluZWQiICE9PSB0eXBlb2Ygc2VsZiA/IHNlbGYgOiB2b2lkIDA7DQogICAgdmFyIHIgPSBmdW5jdGlvbigpIHsNCiAgICAgICAgZnVuY3Rpb24gZSh0LCBuLCByLCBpLCBvLCBhLCB1LCBsKSB7DQogICAgICAgICAgICB2YXIgYyA9ICFpOw0KICAgICAgICAgICAgdCA9ICt0LA0KICAgICAgICAgICAgbiA9IG4gfHwgWzBdLA0KICAgICAgICAgICAgaSA9IGkgfHwgW1t0aGlzXSwgW3t9XV0sDQogICAgICAgICAgICBvID0gbyB8fCB7fTsNCiAgICAgICAgICAgIHZhciBzLCBmID0gW10sIHAgPSBudWxsOw0KICAgICAgICAgICAgRnVuY3Rpb24ucHJvdG90eXBlLmJpbmQgfHwgKHMgPSBbXS5zbGljZSwNCiAgICAgICAgICAgIEZ1bmN0aW9uLnByb3RvdHlwZS5iaW5kID0gZnVuY3Rpb24oZSkgew0KICAgICAgICAgICAgICAgIGlmICgiZnVuY3Rpb24iICE9IHR5cGVvZiB0aGlzKQ0KICAgICAgICAgICAgICAgICAgICB0aHJvdyBuZXcgVHlwZUVycm9yKCJiaW5kMTAxIik7DQogICAgICAgICAgICAgICAgdmFyIHQgPSBzLmNhbGwoYXJndW1lbnRzLCAxKQ0KICAgICAgICAgICAgICAgICAgLCBuID0gdC5sZW5ndGgNCiAgICAgICAgICAgICAgICAgICwgciA9IHRoaXMNCiAgICAgICAgICAgICAgICAgICwgaSA9IGZ1bmN0aW9uKCkge30NCiAgICAgICAgICAgICAgICAgICwgbyA9IGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgICAgICByZXR1cm4gdC5sZW5ndGggPSBuLA0KICAgICAgICAgICAgICAgICAgICB0LnB1c2guYXBwbHkodCwgYXJndW1lbnRzKSwNCiAgICAgICAgICAgICAgICAgICAgci5hcHBseShpLnByb3RvdHlwZS5pc1Byb3RvdHlwZU9mKHRoaXMpID8gdGhpcyA6IGUsIHQpDQogICAgICAgICAgICAgICAgfTsNCiAgICAgICAgICAgICAgICByZXR1cm4gdGhpcy5wcm90b3R5cGUgJiYgKGkucHJvdG90eXBlID0gdGhpcy5wcm90b3R5cGUpLA0KICAgICAgICAgICAgICAgIG8ucHJvdG90eXBlID0gbmV3IGksDQogICAgICAgICAgICAgICAgbw0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgKTsNCiAgICAgICAgICAgIGZvciAodmFyIGQgPSBbZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaVtpLmxlbmd0aCAtIDJdID0gaVtpLmxlbmd0aCAtIDJdICsgaS5wb3AoKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBmb3IgKHZhciBhID0gblt0KytdLCB1ID0gW10sIGwgPSBuW3QrK10sIGMgPSBuW3QrK10sIHMgPSBbXSwgZiA9IDA7IGYgPCBsOyBmKyspDQogICAgICAgICAgICAgICAgICAgIHVbblt0KytdXSA9IGlbblt0KytdXTsNCiAgICAgICAgICAgICAgICBmb3IgKGYgPSAwOyBmIDwgYzsgZisrKQ0KICAgICAgICAgICAgICAgICAgICBzW2ZdID0gblt0KytdOw0KICAgICAgICAgICAgICAgIGkucHVzaCgoZnVuY3Rpb24gdCgpIHsNCiAgICAgICAgICAgICAgICAgICAgdmFyIGkgPSB1LnNsaWNlKDApOw0KICAgICAgICAgICAgICAgICAgICBpWzBdID0gW3RoaXNdLA0KICAgICAgICAgICAgICAgICAgICBpWzFdID0gW2FyZ3VtZW50c10sDQogICAgICAgICAgICAgICAgICAgIGlbMl0gPSBbdF07DQogICAgICAgICAgICAgICAgICAgIGZvciAodmFyIGwgPSAwOyBsIDwgcy5sZW5ndGggJiYgbCA8IGFyZ3VtZW50cy5sZW5ndGg7IGwrKykNCiAgICAgICAgICAgICAgICAgICAgICAgIDAgPCBzW2xdICYmIChpW3NbbF1dID0gW2FyZ3VtZW50c1tsXV0pOw0KICAgICAgICAgICAgICAgICAgICByZXR1cm4gZShhLCBuLCByLCBpLCBvKQ0KICAgICAgICAgICAgICAgIH0NCiAgICAgICAgICAgICAgICApKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMl0gPSBpW2kubGVuZ3RoIC0gMl0gfCBpLnBvcCgpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucHVzaChpW25bdCsrXV1bMF0pDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIHZhciBlID0gblt0KytdDQogICAgICAgICAgICAgICAgICAsIHIgPSBpW2kubGVuZ3RoIC0gMiAtIGVdOw0KICAgICAgICAgICAgICAgIGlbaS5sZW5ndGggLSAyIC0gZV0gPSBpLnBvcCgpLA0KICAgICAgICAgICAgICAgIGkucHVzaChyKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIHZhciBlID0gblt0KytdDQogICAgICAgICAgICAgICAgICAsIHIgPSBlID8gaS5zbGljZSgtZSkgOiBbXTsNCiAgICAgICAgICAgICAgICBpLmxlbmd0aCAtPSBlLA0KICAgICAgICAgICAgICAgIGUgPSBpLnBvcCgpLA0KICAgICAgICAgICAgICAgIC8vIGNvbnNvbGUubG9nKGUsIHIsICdcblxuJykNCiAgICAgICAgICAgICAgICBpLnB1c2goZVswXVtlWzFdXS5hcHBseShlWzBdLCByKSkNCiAgICAgICAgICAgICAgICAvLyBjb25zb2xlLmxvZyhlWzBdW2VbMV1dLmFwcGx5KGVbMF0sIHIpLCAnXG49PT09PT09PT09PT09PT09PT09PT09PT09PT1cbicpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICAvLyBjb25zb2xlLmxvZyh0KQ0KICAgICAgICAgICAgICAgIHZhciBlID0gblt0KytdOw0KICAgICAgICAgICAgICAgIC8vIGNvbnNvbGUubG9nKHQsIGUsIGlbaS5sZW5ndGgtMV0pDQogICAgICAgICAgICAgICAgaVtpLmxlbmd0aCAtIDFdICYmICh0ID0gZSkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgdmFyIGUgPSBuW3QrK10NCiAgICAgICAgICAgICAgICAgICwgciA9IGUgPyBpLnNsaWNlKC1lKSA6IFtdOw0KICAgICAgICAgICAgICAgIGkubGVuZ3RoIC09IGUsDQogICAgICAgICAgICAgICAgci51bnNoaWZ0KG51bGwpLA0KICAgICAgICAgICAgICAgIGkucHVzaChmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIGZ1bmN0aW9uKGUsIHQsIG4pIHsNCiAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiBuZXcgKEZ1bmN0aW9uLmJpbmQuYXBwbHkoZSwgdCkpDQogICAgICAgICAgICAgICAgICAgIH0NCiAgICAgICAgICAgICAgICAgICAgLmFwcGx5KG51bGwsIGFyZ3VtZW50cykNCiAgICAgICAgICAgICAgICB9KGkucG9wKCksIHIpKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMl0gPSBpW2kubGVuZ3RoIC0gMl0gLSBpLnBvcCgpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIHZhciBlID0gaVtpLmxlbmd0aCAtIDJdOw0KICAgICAgICAgICAgICAgIGVbMF1bZVsxXV0gPSBpW2kubGVuZ3RoIC0gMV0NCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICB2YXIgZSA9IG5bdCsrXTsNCiAgICAgICAgICAgICAgICBpW2VdID0gdm9pZCAwID09PSBpW2VdID8gW10gOiBpW2VdDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaS5wdXNoKCFpLnBvcCgpKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCAsICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpLnB1c2goW25bdCsrXV0pDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGlbaS5sZW5ndGggLSAxXSA9IHJbaVtpLmxlbmd0aCAtIDFdXQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucHVzaCgiIikNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMl0gPSBpW2kubGVuZ3RoIC0gMl0gPDwgaS5wb3AoKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIHZhciBlID0gaS5wb3AoKTsNCiAgICAgICAgICAgICAgICBpLnB1c2goW2lbaS5wb3AoKV1bMF0sIGVdKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpLnB1c2goaVtpLnBvcCgpWzBdXVswXSkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMV0gPSBuW3QrK10NCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaVtpLmxlbmd0aCAtIDJdID0gaVtpLmxlbmd0aCAtIDJdID4+IGkucG9wKCkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpLnB1c2goITEpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGlbaS5sZW5ndGggLSAyXSA9IGlbaS5sZW5ndGggLSAyXSA+IGkucG9wKCkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMl0gPSBpW2kubGVuZ3RoIC0gMl0gXiBpLnBvcCgpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucHVzaChbaS5wb3AoKSwgaS5wb3AoKV0ucmV2ZXJzZSgpKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpLnBvcCgpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGlbaVtpLmxlbmd0aCAtIDJdWzBdXVswXSA9IGlbaS5sZW5ndGggLSAxXQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCAsICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpLnB1c2goaVtpLmxlbmd0aCAtIDFdKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIHJldHVybiAhMA0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpLnB1c2goW3IsIGkucG9wKCldKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICB2YXIgZSA9IG5bdCsrXQ0KICAgICAgICAgICAgICAgICAgLCBvID0gZSA/IGkuc2xpY2UoLWUpIDogW107DQogICAgICAgICAgICAgICAgaS5sZW5ndGggLT0gZSwNCiAgICAgICAgICAgICAgICBpLnB1c2goaS5wb3AoKS5hcHBseShyLCBvKSkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaVtpLmxlbmd0aCAtIDJdID0gaVtpLmxlbmd0aCAtIDJdID49IGkucG9wKCkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgLCAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkubGVuZ3RoID0gblt0KytdDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgdmFyIGUgPSBpLnBvcCgpDQogICAgICAgICAgICAgICAgICAsIHQgPSBpLnBvcCgpOw0KICAgICAgICAgICAgICAgIGkucHVzaChbdFswXVt0WzFdXSwgZV0pDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaVtpLmxlbmd0aCAtIDJdID0gaVtpLmxlbmd0aCAtIDJdICYgaS5wb3AoKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICB0ID0gblt0KytdDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaVtpLmxlbmd0aCAtIDFdICs9IFN0cmluZy5mcm9tQ2hhckNvZGUoblt0KytdKQ0KICAgICAgICAgICAgICAgIC8vIGNvbnNvbGUubG9nKGlbaS5sZW5ndGgtMV0pDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMl0gPSBpW2kubGVuZ3RoIC0gMl0gPT09IGkucG9wKCkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgaS5wdXNoKHZvaWQgMCkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgZnVuY3Rpb24oKSB7DQogICAgICAgICAgICAgICAgdmFyIGUgPSBpLnBvcCgpOw0KICAgICAgICAgICAgICAgIGkucHVzaChlWzBdW2VbMV1dKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgLCAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucHVzaCghMCkNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgICwgLCBmdW5jdGlvbigpIHsNCiAgICAgICAgICAgICAgICBpW2kubGVuZ3RoIC0gMl0gPSBpW2kubGVuZ3RoIC0gMl0gKiBpLnBvcCgpDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucHVzaChuW3QrK10pDQogICAgICAgICAgICB9DQogICAgICAgICAgICAsIGZ1bmN0aW9uKCkgew0KICAgICAgICAgICAgICAgIGkucHVzaCh0eXBlb2YgaS5wb3AoKSkNCiAgICAgICAgICAgICAgICAvLyBjb25zb2xlLmxvZyhpW2kubGVuZ3RoLTFdKQ0KICAgICAgICAgICAgfQ0KICAgICAgICAgICAgXTsgOyApDQogICAgICAgICAgICAgICAgdHJ5IHsNCiAgICAgICAgICAgICAgICAgICAgZm9yICh2YXIgaCA9ICExOyAhaDsgKQ0KICAgICAgICAgICAgICAgICAgICAgICAgaCA9IGRbblt0KytdXSgpOw0KICAgICAgICAgICAgICAgICAgICBpZiAocCkNCiAgICAgICAgICAgICAgICAgICAgICAgIHRocm93IHA7DQogICAgICAgICAgICAgICAgICAgIHJldHVybiBjID8gKGkucG9wKCksDQogICAgICAgICAgICAgICAgICAgIGkuc2xpY2UoMyArIGUudikpIDogaS5wb3AoKQ0KICAgICAgICAgICAgICAgIH0gY2F0Y2ggKG0pIHsNCiAgICAgICAgICAgICAgICAgICAgdmFyIHYgPSBmLnBvcCgpOw0KICAgICAgICAgICAgICAgICAgICBpZiAodm9pZCAwID09PSB2KQ0KICAgICAgICAgICAgICAgICAgICAgICAgdGhyb3cgbTsNCiAgICAgICAgICAgICAgICAgICAgcCA9IG0sDQogICAgICAgICAgICAgICAgICAgIHQgPSB2WzBdLA0KICAgICAgICAgICAgICAgICAgICBpLmxlbmd0aCA9IHZbMV0sDQogICAgICAgICAgICAgICAgICAgIHZbMl0gJiYgKGlbdlsyXV1bMF0gPSBwKQ0KICAgICAgICAgICAgICAgIH0NCiAgICAgICAgfQ0KICAgICAgICByZXR1cm4gZS52ID0gNSwNCiAgICAgICAgZSgwLCBmdW5jdGlvbihlKSB7DQogICAgICAgICAgICB2YXIgdCA9IGVbMV0NCiAgICAgICAgICAgICAgLCBuID0gW10NCiAgICAgICAgICAgICAgLCByID0gZnVuY3Rpb24oZSkgew0KICAgICAgICAgICAgICAgIGZvciAodmFyIHQsIG4sIHIgPSAiQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVphYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ejAxMjM0NTY3ODkrLz0iLnNwbGl0KCIiKSwgaSA9IFN0cmluZyhlKS5yZXBsYWNlKC9bPV0rJC8sICIiKSwgbyA9IDAsIGEgPSAwLCB1ID0gIiI7IG4gPSBpLmNoYXJBdChhKyspOyB+biAmJiAodCA9IG8gJSA0ID8gNjQgKiB0ICsgbiA6IG4sDQogICAgICAgICAgICAgICAgbysrICUgNCkgJiYgKHUgKz0gU3RyaW5nLmZyb21DaGFyQ29kZSgyNTUgJiB0ID4+ICgtMiAqIG8gJiA2KSkpKQ0KICAgICAgICAgICAgICAgICAgICBuID0gZnVuY3Rpb24oZSwgdCwgbikgew0KICAgICAgICAgICAgICAgICAgICAgICAgaWYgKCJmdW5jdGlvbiIgPT0gdHlwZW9mIEFycmF5LnByb3RvdHlwZS5pbmRleE9mKQ0KICAgICAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiBBcnJheS5wcm90b3R5cGUuaW5kZXhPZi5jYWxsKGUsIHQsIG4pOw0KICAgICAgICAgICAgICAgICAgICAgICAgdmFyIHI7DQogICAgICAgICAgICAgICAgICAgICAgICBpZiAobnVsbCA9PSBlKQ0KICAgICAgICAgICAgICAgICAgICAgICAgICAgIHRocm93IG5ldyBUeXBlRXJyb3IoJyJhcnJheSIgaXMgbnVsbCBvciBub3QgZGVmaW5lZCcpOw0KICAgICAgICAgICAgICAgICAgICAgICAgdmFyIGkgPSBPYmplY3QoZSkNCiAgICAgICAgICAgICAgICAgICAgICAgICAgLCBvID0gaS5sZW5ndGggPj4+IDA7DQogICAgICAgICAgICAgICAgICAgICAgICBpZiAoMCA9PSBvKQ0KICAgICAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiAtMTsNCiAgICAgICAgICAgICAgICAgICAgICAgIGlmIChvIDw9IChuIHw9IDApKQ0KICAgICAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiAtMTsNCiAgICAgICAgICAgICAgICAgICAgICAgIGZvciAociA9IE1hdGgubWF4KDAgPD0gbiA/IG4gOiBvIC0gTWF0aC5hYnMobiksIDApOyByIDwgbzsgcisrKQ0KICAgICAgICAgICAgICAgICAgICAgICAgICAgIGlmIChyIGluIGkgJiYgaVtyXSA9PT0gdCkNCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIHI7DQogICAgICAgICAgICAgICAgICAgICAgICByZXR1cm4gLTENCiAgICAgICAgICAgICAgICAgICAgfShyLCBuKTsNCiAgICAgICAgICAgICAgICByZXR1cm4gdQ0KICAgICAgICAgICAgfShlWzBdKQ0KICAgICAgICAgICAgICAsIGkgPSB0LnNoaWZ0KCkNCiAgICAgICAgICAgICAgLCBvID0gdC5zaGlmdCgpDQogICAgICAgICAgICAgICwgYSA9IDA7DQogICAgICAgICAgICBmdW5jdGlvbiB1KCkgew0KICAgICAgICAgICAgICAgIGZvciAoOyBhID09PSBpOyApDQogICAgICAgICAgICAgICAgICAgIG4ucHVzaChvKSwNCiAgICAgICAgICAgICAgICAgICAgYSsrLA0KICAgICAgICAgICAgICAgICAgICBpID0gdC5zaGlmdCgpLA0KICAgICAgICAgICAgICAgICAgICBvID0gdC5zaGlmdCgpDQogICAgICAgICAgICB9DQogICAgICAgICAgICBmb3IgKHZhciBsID0gMDsgbCA8IHIubGVuZ3RoOyBsKyspIHsNCiAgICAgICAgICAgICAgICB2YXIgYyA9IHIuY2hhckF0KGwpLmNoYXJDb2RlQXQoMCk7DQogICAgICAgICAgICAgICAgdSgpLA0KICAgICAgICAgICAgICAgIG4ucHVzaChjKSwNCiAgICAgICAgICAgICAgICBhKysNCiAgICAgICAgICAgIH0NCiAgICAgICAgICAgIHJldHVybiB1KCksDQogICAgICAgICAgICBuDQogICAgICAgIH0oWyJNd2dPQWc0RERnUU9CUTRHRGdjNGZ6b3pDUTRDRGdNT0JBNEZEZ1lPQnc0SUZ6cGtPbVU2WmpwcE9tNDZaUlZGRnpwbU9uVTZianBqT25RNmFUcHZPbTQ5Q1VjNFh6b21GenBrT21VNlpqcHBPbTQ2WlM0WE9tRTZiVHBrTlQ4SmFTWURBeThBT0h3SkpoYzZaRHBsT21ZNmFUcHVPbVV1QXdNR0FTWStMUUVSQUFFRE9BTXpDZzRDRGdNT0JBNEZEZ1lPQnc0SURna1VDRGc4TXdnT0FnNEREZ1FPQlE0R0RnY1hPbWM2YkRwdk9tSTZZVHBzRlVVWE9uVTZianBrT21VNlpqcHBPbTQ2WlRwa1BSQUoxaVk0NWdRbUZ6cG5PbXc2YnpwaU9tRTZiQlV0RnpwM09tazZianBrT204NmR4VkZGenAxT200NlpEcGxPbVk2YVRwdU9tVTZaRDBRQ1NZNEJpWVhPbmM2YVRwdU9tUTZienAzRlMwWE9uTTZaVHBzT21ZVlJSYzZkVHB1T21RNlpUcG1PbWs2YmpwbE9tUTlFQWttT0FFbUZ6cHpPbVU2YkRwbUZTMCtMUUdlQUFBdkFDY21KaFFKT0EweklnNENEZ01PQkE0RkRnWU9CdzRJRGdrT0NnNExEZ3dPRFE0T0RnOE9FQTRSRGhJT0V3NFVEaFVPRmc0WERoZ09HUTRhRGhzT0hBNGREaDRPSHc0Z0ZBa1hPazg2WWpwcU9tVTZZenAwRlFvQUt4YzZNQ1ZFQUF3bUppc1hPakVsUkFFTUppWXJGem95SlVRQ0RDWW1LeGM2TXlWRUF3d21KaXNYT2pRbFJBUU1KaVlyRnpvMUpVUUZEQ1ltS3hjNk5pVkVCZ3dtSmlzWE9qY2xSQWNNSmlZckZ6bzRKVVFJRENZbUt4YzZPU1ZFQ1F3bUppc1hPa0VsUkFvTUppWXJGenBDSlVRTERDWW1LeGM2UXlWRURBd21KaXNYT2tRbFJBME1KaVlyRnpwRkpVUU9EQ1ltS3hjNlJpVkVJMFFVQ3d3bUppY21KaFFLRnpwQk9rSTZRenBFT2tVNlJqcEhPa2c2U1RwS09rczZURHBOT2s0NlR6cFFPbEU2VWpwVE9sUTZWVHBXT2xjNldEcFpPbG82WVRwaU9tTTZaRHBsT21ZNlp6cG9PbWs2YWpwck9tdzZiVHB1T204NmNEcHhPbkk2Y3pwME9uVTZkanAzT25nNmVUcDZPakE2TVRveU9qTTZORG8xT2pZNk56bzRPams2S3pvdk9qMG5KaVlVQ3hRaEZ6cGZPbDg2Y3pwcE9tYzZianBmT21nNllUcHpPbWc2WHpveU9qQTZNam93T2pBNk16b3dPalViUHdrNE15WWhGQ0VYT2w4Nlh6cHpPbWs2WnpwdU9sODZhRHBoT25NNmFEcGZPakk2TURveU9qQTZNRG96T2pBNk5Sc0RBd1lCQkFBbUZ6cDBPbTg2VlRwd09uQTZaVHB5T2tNNllUcHpPbVVsQmdBbkppWVVEQmM2ZHpwcE9tNDZaRHB2T25jVlJSYzZienBpT21vNlpUcGpPblE5Q1RnQkpoYzZianBoT25ZNmFUcG5PbUU2ZERwdk9uSVZSUmM2YnpwaU9tbzZaVHBqT25ROUNUZ0RKaGM2YkRwdk9tTTZZVHAwT21rNmJ6cHVGVVVYT204NllqcHFPbVU2WXpwMFBTY21KaFFOQXd3Sk9Bb21GenBTT21VNlp6cEZPbmc2Y0JVWE9rZzZaVHBoT21RNmJEcGxPbk02Y3hjNmFTOENGenAwT21VNmN6cDBKUmM2YmpwaE9uWTZhVHBuT21FNmREcHZPbkl1RnpwMU9uTTZaVHB5T2tFNlp6cGxPbTQ2ZERVL0JnRW5KaVlVRGhRaEZ6cGZPbDg2Y1RwdE9tWTZaVHBmT25NNmFUcG5PbTQ2WHpwak9tZzZaVHBqT21zYlAwUUJQUWttQXd3Sk9Ba21BdzBRQ1RnNEpoYzZiRHB2T21NNllUcDBPbWs2YnpwdUxoYzZhRHB2T25NNmREVVhPbWs2Ympwa09tVTZlRHBQT21ZMUZ6cHhPbkU2TGpwak9tODZiUVlCUkFCRUFRc2lKeVltRkE5QkZ6cEJPbkk2Y2pwaE9ua1ZDZ0FyUkFBbFJDNUVHUXNNSmlZclJBRWxSQVFNSmlZclJBSWxSQWtNSmlZclJBTWxSRFZFR3dzTUppWXJSQVFsUkFORURRQU1KaVlyUkFVbFJBQkVGQUFNSmlZclJBWWxSQzlFRkFzTUppWXJSQWNsUkM5RUVRc01KaVlYT20wNllUcHdKVGdCTXdzT0FnNEREZ1FPQlE0R0RnY09DQlFKQXdvSkpnTURSQUVBT0FvbUF3TWJQeTBCQWdFSkN3b09Bd1lCRnpwcU9tODZhVHB1SlFRQUpoY0dBU2NtSmhRUUZ6cEJPbkk2Y2pwaE9ua1ZDZ0FyUkFBbFJBWkVEQUFNSmlZclJBRWxSQXNNSmlZclJBSWxSQU1NSmlZclJBTWxSQUlNSmlZclJBUWxSQUVNSmlZclJBVWxSQWNNSmlZclJBWWxSQVlNSmlZclJBY2xSRGxFSUFzTUppWVhPbTA2WVRwd0pUZ3hNd3NPQWc0RERnUU9CUTRHRGdjT0NCUUpBd29KSmdNRFJBRUFPQUVtQXdNYlB5MEJBZ0VKQ3dvT0F3WUJGenBxT204NmFUcHVKUmNHQVNjbUpoUVJGenBCT25JNmNqcGhPbmtWQ2dBclJBQWxSQWhFRVVRTVF3QU1KaVlyUkFFbFJBdEVJZ0FNSmlZclJBSWxSRFJFSEFBTUppWXJSQU1sUkR4RUNBQU1KaVlyUkFRbFJBMUVEa1FOUXdBTUppWXJSQVVsUkFkRURFUU5Rd0FNSmlZclJBWWxSQWRFRFVRTVF3QU1KaVlyUkFjbFJBdEVFRVFNUXdBTUppWXJSQWdsUkFWRUNFUVRRd0FNSmlZclJBa2xSQXBFRGtRUFF3QU1KaVlyUkFvbFJCQkVFVVFPUXdBTUppWXJSQXNsUkIxRVBnQU1KaVlyUkF3bFJBeEVFVU1NSmlZclJBMGxSQXBFUlFBTUppWXJSQTRsUkFkRVlRQU1KaVlyUkR4RUxRc2xSQVlNSmlZbkppWUREaEFKSmpnZUpoUVJGenBCT25JNmNqcGhPbmtWQ2dBclJBQWxSQlZFQkFBTUppWXJSQUVsUkJ0RUp3QU1KaVlyUkFJbFJBRU1KaVlyUkFNbFJEaEVBZ0FNSmlZclJBUWxSQU5FVndBTUppWXJSQVVsUkRWRUdRQU1KaVlyUkFZbFJEbEVRZ0FNSmlZclJBY2xSQnBFTFFBTUppWXJSQWdsUkNWRUJBc01KaVlyUkFrbFJBd01KaVlyUkFvbFJBaEVDa1FSUXdBTUppWXJSQXNsUkRKRUt3QU1KaVlyUkF3bFJDRkVCd0FNSmlZclJBMGxSQXBFREVRTlF3QU1KaVlyUkE0bFJDNUVFQUFNSmlZclJCRkVBZ3NsUkFoRUQwUVBRd0FNSmlZbkppWVVFaGM2UVRweU9uSTZZVHA1RlFvQUp5WW1GQk5FQUNjbUpoUVRIRVFUUkFNTE1CQUpKamdVSmhRVUZBa1VDd01UUkFKREd6OGJQMFEyUkNZTFF4UUpGQXNERTBRQ1EwUUJBQnMvR3o4QUp5WW1GQlVVRVFNVEd6OG5KaVlVRWhjNmNEcDFPbk02YUJzREZBTVZKQVlCSmhRVEt4d3JCQUVFQUVRQkFDY21IZ0FFQUFJbU9FUVVFUlFMRkFraEp3UUFKaWNFQUNZbkppWVVIUmNuSmlZVUhrUUFKeVltRkI0Y1JBVXdFQWttT0JRbUZCWVVFZ01lUkFOREd6OG5KaVlVRnhRU0F4NUVBME5FQVFBYlB5Y21KaFFZRkJJREhrUURRMFFDQUJzL0p5WW1GQmtERmtRQ0h5Y21KaFFhQXhaRUF6ZEVCQmtERjBRRUh3SW5KaVlVR3dNWFJBVkVDZ0EzUkFJWkF4aEVCaDhDSnlZbUZCd0RHRVExUkFvQU55Y21KaFFkQXgwVUNnTVpHejhBRkFvREdocy9BQlFLQXhzYlB3QVVDZ01jR3o4QUp5WW1GQjRySENzRUFRUUFSQUVBSnlZZUFBUUFBaVk0THhRZEF4MFVDaFFTUkFoRUJ3QWJQMFFDSHhzL0FCUUtGQkpFQzBRRUFCcy9SQU0zUkFRWkd6OEFKeVltRkJJaEp5WW1GQjhVSFJjNmNqcGxPbkE2YkRwaE9tTTZaUnNYT2xJNlpUcG5Pa1U2ZURwd0ZSYzZXenBjT2k4Nkt6cGRGenBuTHdJWEJnSW5KaVlVSUJjNmVqcDZPbUlERHdBREh3QURFQUFuSmlZVUR4UVFGQjhVSFJRS0lTY0VBQ1luQkFBbUp3UUFKaWNFQUNZbkppWVVJQmM2ZERwdk9rdzZienAzT21VNmNqcERPbUU2Y3pwbEd3WUFMUUVCQVNFSUF5Y21KaFFJRnpwZk9tYzZaVHAwT2xNNlpUcGpPblU2Y2pwcE9uUTZlVHBUT21rNlp6cHVHd01KRENZbVBpMEJod0FBTHdFbVBpMD0iLCBbMTMzLCAyNjI4LCAxNTYsIDM0MCwgMjY3LCAyNzIsIDI3MCwgMjg4LCAzMjEsIDMyNiwgMzI0LCAzMzgsIDM1MiwgMjU3NSwgNzg2LCA3OTAsIDc4OCwgODY5LCA5MDQsIDkwOCwgOTA2LCA5NDQsIDk0NSwgOTQ5LCA5NDcsIDk4MywgOTkxLCA5OTUsIDk5MywgMTA4NSwgMTEzMywgMTIxNywgMTEzOCwgMTE0MiwgMTE0MCwgMTE0NiwgMTE0NywgMTE1MSwgMTE0OSwgMTIxNywgMTMzNiwgMTM3NSwgMTM1OSwgMTM2OSwgMTM2NywgMTM3MiwgMTM3NiwgMTMzOCwgMTUwOCwgMTU0NywgMTUzMSwgMTU0MSwgMTUzOSwgMTU0NCwgMTU0OCwgMTUxMCwgMTgxMywgMTgxOCwgMTgxNiwgMjAzNiwgMjA3MywgMjA3OCwgMjA3NiwgMjE3NCwgMjE3MiwgMjA2MiwgMjIxMywgMjIxOCwgMjIxNiwgMjM4OSwgMjM4NywgMjIwNSwgMjU3NiwgMzU0XV0pLCBuKQ0KICAgIH0oKTsNCiAgICByLmcgPSBmdW5jdGlvbigpIHsNCiAgICAgICAgcmV0dXJuIHIuc2hpZnQoKVswXQ0KICAgIH0NCiAgICAsDQogICAgbi5fX3NpZ25faGFzaF8yMDIwMDMwNSA9IGZ1bmN0aW9uKGUpIHsNCiAgICAgICAgZnVuY3Rpb24gdChlLCB0KSB7DQogICAgICAgICAgICB2YXIgbiA9ICg2NTUzNSAmIGUpICsgKDY1NTM1ICYgdCk7DQogICAgICAgICAgICByZXR1cm4gKGUgPj4gMTYpICsgKHQgPj4gMTYpICsgKG4gPj4gMTYpIDw8IDE2IHwgNjU1MzUgJiBuDQogICAgICAgIH0NCiAgICAgICAgZnVuY3Rpb24gbihlLCBuLCByLCBpLCBvLCBhKSB7DQogICAgICAgICAgICByZXR1cm4gdCgodSA9IHQodChuLCBlKSwgdChpLCBhKSkpIDw8IChsID0gbykgfCB1ID4+PiAzMiAtIGwsIHIpOw0KICAgICAgICAgICAgdmFyIHUsIGwNCiAgICAgICAgfQ0KICAgICAgICBmdW5jdGlvbiByKGUsIHQsIHIsIGksIG8sIGEsIHUpIHsNCiAgICAgICAgICAgIHJldHVybiBuKHQgJiByIHwgfnQgJiBpLCBlLCB0LCBvLCBhLCB1KQ0KICAgICAgICB9DQogICAgICAgIGZ1bmN0aW9uIGkoZSwgdCwgciwgaSwgbywgYSwgdSkgew0KICAgICAgICAgICAgcmV0dXJuIG4odCAmIGkgfCByICYgfmksIGUsIHQsIG8sIGEsIHUpDQogICAgICAgIH0NCiAgICAgICAgZnVuY3Rpb24gbyhlLCB0LCByLCBpLCBvLCBhLCB1KSB7DQogICAgICAgICAgICByZXR1cm4gbih0IF4gciBeIGksIGUsIHQsIG8sIGEsIHUpDQogICAgICAgIH0NCiAgICAgICAgZnVuY3Rpb24gYShlLCB0LCByLCBpLCBvLCBhLCB1KSB7DQogICAgICAgICAgICByZXR1cm4gbihyIF4gKHQgfCB+aSksIGUsIHQsIG8sIGEsIHUpDQogICAgICAgIH0NCiAgICAgICAgZnVuY3Rpb24gdShlKSB7DQogICAgICAgICAgICByZXR1cm4gZnVuY3Rpb24oZSkgew0KICAgICAgICAgICAgICAgIHZhciB0LCBuID0gIiI7DQogICAgICAgICAgICAgICAgZm9yICh0ID0gMDsgdCA8IDMyICogZS5sZW5ndGg7IHQgKz0gOCkNCiAgICAgICAgICAgICAgICAgICAgbiArPSBTdHJpbmcuZnJvbUNoYXJDb2RlKGVbdCA+PiA1XSA+Pj4gdCAlIDMyICYgMjU1KTsNCiAgICAgICAgICAgICAgICByZXR1cm4gbg0KICAgICAgICAgICAgfShmdW5jdGlvbihlLCBuKSB7DQogICAgICAgICAgICAgICAgZVtuID4+IDVdIHw9IDEyOCA8PCBuICUgMzIsDQogICAgICAgICAgICAgICAgZVsxNCArIChuICsgNjQgPj4+IDkgPDwgNCldID0gbjsNCiAgICAgICAgICAgICAgICB2YXIgdSwgbCwgYywgcywgZiwgcCA9IDE3MzI1ODQxOTMsIGQgPSAtMjcxNzMzODc5LCBoID0gLTE3MzI1ODQxOTQsIHYgPSAyNzE3MzM4Nzg7DQogICAgICAgICAgICAgICAgZm9yICh1ID0gMDsgdSA8IGUubGVuZ3RoOyB1ICs9IDE2KQ0KICAgICAgICAgICAgICAgICAgICBsID0gcCwNCiAgICAgICAgICAgICAgICAgICAgYyA9IGQsDQogICAgICAgICAgICAgICAgICAgIHMgPSBoLA0KICAgICAgICAgICAgICAgICAgICBmID0gdiwNCiAgICAgICAgICAgICAgICAgICAgcCA9IHIocCwgZCwgaCwgdiwgZVt1XSwgNywgLTY4MDg3NjkzNiksDQogICAgICAgICAgICAgICAgICAgIHYgPSByKHYsIHAsIGQsIGgsIGVbdSArIDFdLCAxMiwgLTM4OTU2NDU4NiksDQogICAgICAgICAgICAgICAgICAgIGggPSByKGgsIHYsIHAsIGQsIGVbdSArIDJdLCAxNywgNjA2MTA1ODE5KSwNCiAgICAgICAgICAgICAgICAgICAgZCA9IHIoZCwgaCwgdiwgcCwgZVt1ICsgM10sIDIyLCAtMTA0NDUyNTMzMCksDQogICAgICAgICAgICAgICAgICAgIHAgPSByKHAsIGQsIGgsIHYsIGVbdSArIDRdLCA3LCAtMTc2NDE4ODk3KSwNCiAgICAgICAgICAgICAgICAgICAgdiA9IHIodiwgcCwgZCwgaCwgZVt1ICsgNV0sIDEyLCAxMjAwMDgwNDI2KSwNCiAgICAgICAgICAgICAgICAgICAgaCA9IHIoaCwgdiwgcCwgZCwgZVt1ICsgNl0sIDE3LCAtMTQ3MzIzMTM0MSksDQogICAgICAgICAgICAgICAgICAgIGQgPSByKGQsIGgsIHYsIHAsIGVbdSArIDddLCAyMiwgLTQ1NzA1OTgzKSwNCiAgICAgICAgICAgICAgICAgICAgcCA9IHIocCwgZCwgaCwgdiwgZVt1ICsgOF0sIDcsIDE3NzAwMzU0MTYpLA0KICAgICAgICAgICAgICAgICAgICB2ID0gcih2LCBwLCBkLCBoLCBlW3UgKyA5XSwgMTIsIC0xOTU4NDE0NDE3KSwNCiAgICAgICAgICAgICAgICAgICAgaCA9IHIoaCwgdiwgcCwgZCwgZVt1ICsgMTBdLCAxNywgLTQyMDYzKSwNCiAgICAgICAgICAgICAgICAgICAgZCA9IHIoZCwgaCwgdiwgcCwgZVt1ICsgMTFdLCAyMiwgLTE5OTA0MDQxNjIpLA0KICAgICAgICAgICAgICAgICAgICBwID0gcihwLCBkLCBoLCB2LCBlW3UgKyAxMl0sIDcsIDE4MDQ2MDM2ODIpLA0KICAgICAgICAgICAgICAgICAgICB2ID0gcih2LCBwLCBkLCBoLCBlW3UgKyAxM10sIDEyLCAtNDAzNDExMDEpLA0KICAgICAgICAgICAgICAgICAgICBoID0gcihoLCB2LCBwLCBkLCBlW3UgKyAxNF0sIDE3LCAtMTUwMjAwMjI5MCksDQogICAgICAgICAgICAgICAgICAgIHAgPSBpKHAsIGQgPSByKGQsIGgsIHYsIHAsIGVbdSArIDE1XSwgMjIsIDEyMzY1MzUzMjkpLCBoLCB2LCBlW3UgKyAxXSwgNSwgLTE2NTc5NjUxMCksDQogICAgICAgICAgICAgICAgICAgIHYgPSBpKHYsIHAsIGQsIGgsIGVbdSArIDZdLCA5LCAtMTA2OTUwMTYzMiksDQogICAgICAgICAgICAgICAgICAgIGggPSBpKGgsIHYsIHAsIGQsIGVbdSArIDExXSwgMTQsIDY0MzcxNzcxMyksDQogICAgICAgICAgICAgICAgICAgIGQgPSBpKGQsIGgsIHYsIHAsIGVbdV0sIDIwLCAtMzczODk3MzAyKSwNCiAgICAgICAgICAgICAgICAgICAgcCA9IGkocCwgZCwgaCwgdiwgZVt1ICsgNV0sIDUsIC03MDE1NTg2OTEpLA0KICAgICAgICAgICAgICAgICAgICB2ID0gaSh2LCBwLCBkLCBoLCBlW3UgKyAxMF0sIDksIDM4MDE2MDgzKSwNCiAgICAgICAgICAgICAgICAgICAgaCA9IGkoaCwgdiwgcCwgZCwgZVt1ICsgMTVdLCAxNCwgLTY2MDQ3ODMzNSksDQogICAgICAgICAgICAgICAgICAgIGQgPSBpKGQsIGgsIHYsIHAsIGVbdSArIDRdLCAyMCwgLTQwNTUzNzg0OCksDQogICAgICAgICAgICAgICAgICAgIHAgPSBpKHAsIGQsIGgsIHYsIGVbdSArIDldLCA1LCA1Njg0NDY0MzgpLA0KICAgICAgICAgICAgICAgICAgICB2ID0gaSh2LCBwLCBkLCBoLCBlW3UgKyAxNF0sIDksIC0xMDE5ODAzNjkwKSwNCiAgICAgICAgICAgICAgICAgICAgaCA9IGkoaCwgdiwgcCwgZCwgZVt1ICsgM10sIDE0LCAtMTg3MzYzOTYxKSwNCiAgICAgICAgICAgICAgICAgICAgZCA9IGkoZCwgaCwgdiwgcCwgZVt1ICsgOF0sIDIwLCAxMTYzNTMxNTAxKSwNCiAgICAgICAgICAgICAgICAgICAgcCA9IGkocCwgZCwgaCwgdiwgZVt1ICsgMTNdLCA1LCAtMTQ0NDY4MTQ2NyksDQogICAgICAgICAgICAgICAgICAgIHYgPSBpKHYsIHAsIGQsIGgsIGVbdSArIDJdLCA5LCAtNTE0MDM3ODQpLA0KICAgICAgICAgICAgICAgICAgICBoID0gaShoLCB2LCBwLCBkLCBlW3UgKyA3XSwgMTQsIDE3MzUzMjg0NzMpLA0KICAgICAgICAgICAgICAgICAgICBwID0gbyhwLCBkID0gaShkLCBoLCB2LCBwLCBlW3UgKyAxMl0sIDIwLCAtMTkyNjYwNzczNCksIGgsIHYsIGVbdSArIDVdLCA0LCAtMzc4NTU4KSwNCiAgICAgICAgICAgICAgICAgICAgdiA9IG8odiwgcCwgZCwgaCwgZVt1ICsgOF0sIDExLCAtMjAyMjU3NDQ2MyksDQogICAgICAgICAgICAgICAgICAgIGggPSBvKGgsIHYsIHAsIGQsIGVbdSArIDExXSwgMTYsIDE4MzkwMzA1NjIpLA0KICAgICAgICAgICAgICAgICAgICBkID0gbyhkLCBoLCB2LCBwLCBlW3UgKyAxNF0sIDIzLCAtMzUzMDk1NTYpLA0KICAgICAgICAgICAgICAgICAgICBwID0gbyhwLCBkLCBoLCB2LCBlW3UgKyAxXSwgNCwgLTE1MzA5OTIwNjApLA0KICAgICAgICAgICAgICAgICAgICB2ID0gbyh2LCBwLCBkLCBoLCBlW3UgKyA0XSwgMTEsIDEyNzI4OTMzNTMpLA0KICAgICAgICAgICAgICAgICAgICBoID0gbyhoLCB2LCBwLCBkLCBlW3UgKyA3XSwgMTYsIC0xNTU0OTc2MzIpLA0KICAgICAgICAgICAgICAgICAgICBkID0gbyhkLCBoLCB2LCBwLCBlW3UgKyAxMF0sIDIzLCAtMTA5NDczMDY0MCksDQogICAgICAgICAgICAgICAgICAgIHAgPSBvKHAsIGQsIGgsIHYsIGVbdSArIDEzXSwgNCwgNjgxMjc5MTc0KSwNCiAgICAgICAgICAgICAgICAgICAgdiA9IG8odiwgcCwgZCwgaCwgZVt1XSwgMTEsIC0zNTg1MzcyMjIpLA0KICAgICAgICAgICAgICAgICAgICBoID0gbyhoLCB2LCBwLCBkLCBlW3UgKyAzXSwgMTYsIC03MjI1MjE5NzkpLA0KICAgICAgICAgICAgICAgICAgICBkID0gbyhkLCBoLCB2LCBwLCBlW3UgKyA2XSwgMjMsIDc2MDI5MTg5KSwNCiAgICAgICAgICAgICAgICAgICAgcCA9IG8ocCwgZCwgaCwgdiwgZVt1ICsgOV0sIDQsIC02NDAzNjQ0ODcpLA0KICAgICAgICAgICAgICAgICAgICB2ID0gbyh2LCBwLCBkLCBoLCBlW3UgKyAxMl0sIDExLCAtNDIxODE1ODM1KSwNCiAgICAgICAgICAgICAgICAgICAgaCA9IG8oaCwgdiwgcCwgZCwgZVt1ICsgMTVdLCAxNiwgNTMwNzQyNTIwKSwNCiAgICAgICAgICAgICAgICAgICAgcCA9IGEocCwgZCA9IG8oZCwgaCwgdiwgcCwgZVt1ICsgMl0sIDIzLCAtOTk1MzM4NjUxKSwgaCwgdiwgZVt1XSwgNiwgLTE5ODYzMDg0NCksDQogICAgICAgICAgICAgICAgICAgIHYgPSBhKHYsIHAsIGQsIGgsIGVbdSArIDddLCAxMCwgMTEyNjg5MTQxNSksDQogICAgICAgICAgICAgICAgICAgIGggPSBhKGgsIHYsIHAsIGQsIGVbdSArIDE0XSwgMTUsIC0xNDE2MzU0OTA1KSwNCiAgICAgICAgICAgICAgICAgICAgZCA9IGEoZCwgaCwgdiwgcCwgZVt1ICsgNV0sIDIxLCAtNTc0MzQwNTUpLA0KICAgICAgICAgICAgICAgICAgICBwID0gYShwLCBkLCBoLCB2LCBlW3UgKyAxMl0sIDYsIDE3MDA0ODU1NzEpLA0KICAgICAgICAgICAgICAgICAgICB2ID0gYSh2LCBwLCBkLCBoLCBlW3UgKyAzXSwgMTAsIC0xODk0OTg2NjA2KSwNCiAgICAgICAgICAgICAgICAgICAgaCA9IGEoaCwgdiwgcCwgZCwgZVt1ICsgMTBdLCAxNSwgLTEwNTE1MjMpLA0KICAgICAgICAgICAgICAgICAgICBkID0gYShkLCBoLCB2LCBwLCBlW3UgKyAxXSwgMjEsIC0yMDU0OTIyNzk5KSwNCiAgICAgICAgICAgICAgICAgICAgcCA9IGEocCwgZCwgaCwgdiwgZVt1ICsgOF0sIDYsIDE4NzMzMTMzNTkpLA0KICAgICAgICAgICAgICAgICAgICB2ID0gYSh2LCBwLCBkLCBoLCBlW3UgKyAxNV0sIDEwLCAtMzA2MTE3NDQpLA0KICAgICAgICAgICAgICAgICAgICBoID0gYShoLCB2LCBwLCBkLCBlW3UgKyA2XSwgMTUsIC0xNTYwMTk4MzgwKSwNCiAgICAgICAgICAgICAgICAgICAgZCA9IGEoZCwgaCwgdiwgcCwgZVt1ICsgMTNdLCAyMSwgMTMwOTE1MTY0OSksDQogICAgICAgICAgICAgICAgICAgIHAgPSBhKHAsIGQsIGgsIHYsIGVbdSArIDRdLCA2LCAtMTQ1NTIzMDcwKSwNCiAgICAgICAgICAgICAgICAgICAgdiA9IGEodiwgcCwgZCwgaCwgZVt1ICsgMTFdLCAxMCwgLTExMjAyMTAzNzkpLA0KICAgICAgICAgICAgICAgICAgICBoID0gYShoLCB2LCBwLCBkLCBlW3UgKyAyXSwgMTUsIDcxODc4NzI1OSksDQogICAgICAgICAgICAgICAgICAgIGQgPSBhKGQsIGgsIHYsIHAsIGVbdSArIDldLCAyMSwgLTM0MzQ4NTU1MSksDQogICAgICAgICAgICAgICAgICAgIHAgPSB0KHAsIGwpLA0KICAgICAgICAgICAgICAgICAgICBkID0gdChkLCBjKSwNCiAgICAgICAgICAgICAgICAgICAgaCA9IHQoaCwgcyksDQogICAgICAgICAgICAgICAgICAgIHYgPSB0KHYsIGYpOw0KICAgICAgICAgICAgICAgIHJldHVybiBbcCwgZCwgaCwgdl0NCiAgICAgICAgICAgIH0oZnVuY3Rpb24oZSkgew0KICAgICAgICAgICAgICAgIHZhciB0LCBuID0gW107DQogICAgICAgICAgICAgICAgZm9yIChuWyhlLmxlbmd0aCA+PiAyKSAtIDFdID0gdm9pZCAwLA0KICAgICAgICAgICAgICAgIHQgPSAwOyB0IDwgbi5sZW5ndGg7IHQgKz0gMSkNCiAgICAgICAgICAgICAgICAgICAgblt0XSA9IDA7DQogICAgICAgICAgICAgICAgZm9yICh0ID0gMDsgdCA8IDggKiBlLmxlbmd0aDsgdCArPSA4KQ0KICAgICAgICAgICAgICAgICAgICBuW3QgPj4gNV0gfD0gKDI1NSAmIGUuY2hhckNvZGVBdCh0IC8gOCkpIDw8IHQgJSAzMjsNCiAgICAgICAgICAgICAgICByZXR1cm4gbg0KICAgICAgICAgICAgfShlKSwgOCAqIGUubGVuZ3RoKSkNCiAgICAgICAgfQ0KICAgICAgICBmdW5jdGlvbiBsKGUpIHsNCiAgICAgICAgICAgIHJldHVybiB1KHVuZXNjYXBlKGVuY29kZVVSSUNvbXBvbmVudChlKSkpDQogICAgICAgIH0NCiAgICAgICAgcmV0dXJuIGZ1bmN0aW9uKGUpIHsNCiAgICAgICAgICAgIHZhciB0LCBuLCByID0gIiI7DQogICAgICAgICAgICBmb3IgKG4gPSAwOyBuIDwgZS5sZW5ndGg7IG4gKz0gMSkNCiAgICAgICAgICAgICAgICB0ID0gZS5jaGFyQ29kZUF0KG4pLA0KICAgICAgICAgICAgICAgIHIgKz0gIjAxMjM0NTY3ODlhYmNkZWYiLmNoYXJBdCh0ID4+PiA0ICYgMTUpICsgIjAxMjM0NTY3ODlhYmNkZWYiLmNoYXJBdCgxNSAmIHQpOw0KICAgICAgICAgICAgcmV0dXJuIHINCiAgICAgICAgfShsKGUpKQ0KICAgIH0NCiAgICA7DQogICAgdmFyIGkgPSBuLl9nZXRTZWN1cml0eVNpZ247DQogICAgZGVsZXRlIG4uX2dldFNlY3VyaXR5U2lnbjsNCiAgICBtYWluID0gaQ0KfSh3aW5kb3cpDQovLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8NCmFyZ3MgPSBwcm9jZXNzLmFyZ3Yuc2xpY2UoMikNCmRhdGEgPSBhcmdzLmpvaW4oJyAnKQ0KY29uc29sZS5sb2cobWFpbihkYXRhKSkNCg=='


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

    async def _get_song_info(self, song):
        time_stamp = int(time.time() * 1000)
        self.SEARCH_DATA['req_1']['param']['searchid'] = Ee(3)
        self.SEARCH_DATA['req_1']['param']['query'] = song
        self.headers['user-agent'] = ua.get_ua()
        _data = json.dumps(self.SEARCH_DATA, ensure_ascii=False)
        data = json.dumps(_data, ensure_ascii=False)
##        print(data)
        path = await self.load_js(self.js_name)
        res = await self.session.post(
            self.SEARCH_URL % (
                time_stamp, await self._run_js(path, data)),
            headers=self.headers,
            data=_data)
        assert (status := res.status), f'response: {status}'
        result_dict = await res.json(content_type=None)
        if (result_dict := result_dict['req_1'])['code'] != 0:
            raise CookieInvalidError
        songs = result_dict['data']['body']['song']['list']
        return [SongInfo(f'QQ: {song["name"]}-->{song["singer"][0]["name"]}-->《{song["album"]["name"]}》',
                         SongID((str(song['mid']),), 'qq'))
                for song in songs]

    async def _get_song_url(self, _id):
        time_stamp = int(time.time() * 1000)
        self.URL_DATA['req_7']['param']['songmid'][0] = _id
        self.headers['user-agent'] = ua.get_ua()
        _data = json.dumps(self.URL_DATA, ensure_ascii=False)
        data = json.dumps(_data, ensure_ascii=False)
        path = await self.load_js(self.js_name)
        res = await self.session.post(
            self.SONG_URL % (time_stamp, await self._run_js(path, data)),
            headers=self.headers,
            data=_data)
        assert (status := res.status) == 200, f'response: {status}'
        result_dict = await res.json(content_type=None)
        if (result_dict := result_dict['req_7'])['code'] != 0:
            raise CookieInvalidError
        url = 'https://dl.stream.qqmusic.qq.com/' + result_dict['data']['midurlinfo'][0]['purl']
        return SongUrl(url)

    async def close(self):
        await super(Musicer, self).close()
        os.remove(await self.load_js(self.js_name))
