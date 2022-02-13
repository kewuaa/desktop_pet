# -*- coding: utf-8 -*-
# @Author: kewuaa
# @Date:   2022-02-13 09:33:52
# @Last Modified by:   None
# @Last Modified time: 2022-02-13 16:15:24
import binascii

import rsa


class RSA(object):
    """RSA."""

    def __init__(self, n, e):
        super(RSA, self).__init__()
        n = int(n, 16)
        e = int(e, 16)
        self.key = rsa.PublicKey(n, e)

    def encrypt(self, message):
        result = rsa.encrypt(message.encode(), self.key)
        result = binascii.b2a_hex(result)
        return result.decode()
