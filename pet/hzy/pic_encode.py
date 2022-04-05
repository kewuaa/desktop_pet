# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-02-17 10:17:08
# @Last Modified by:   None
# @Last Modified time: 2022-03-01 20:09:29
import sys
import base64


def encode(path: str) -> str:
    with open(path, 'rb') as f:
        content = f.read()
        b64content = base64.b64encode(content)
        b64str = b64content.decode()
    return b64str


if __name__ == '__main__':
    assert len(argv := sys.argv) > 1, '请正确输入路径'
    print('\n'.join(encode(path) for path in argv[1:]))
