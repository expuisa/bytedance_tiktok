# coding:utf-8
import hashlib
import json
from time import time
from hashlib import md5
from copy import deepcopy
from random import choice
from urllib.parse import quote


def hex_string(num):
    return f'{num:02x}'


def RBIT(num):
    bin_str = f'{num:08b}'
    reversed_bin = bin_str[::-1]
    return int(reversed_bin, 2)


def reverse(num):
    tmp = f'{num:02x}'
    return int(tmp[1] + tmp[0], 16)


class XG:
    def __init__(self, debug):
        self.length = 0x14
        self.debug = debug
        self.hex_CE0 = [
            0x05,
            0x00,
            0x50,
            choice(range(0, 0xFF)),
            0x47,
            0x1e,
            0x00,
            choice(range(0, 0xFF)) & 0xf0,
        ]

    def addr_BA8(self):
        tmp = ''
        hex_BA8 = list(range(0x100))
        for i in range(0x100):
            A = 0 if i == 0 else (tmp if tmp else hex_BA8[i - 1])
            B = self.hex_CE0[i % 0x8]
            if A == 0x05 and i != 1 and tmp != 0x05:
                A = 0
            C = (A + i + B) % 0x100
            tmp = C if C < i else ''
            D = hex_BA8[C]
            hex_BA8[i] = D
        return hex_BA8

    def initial(self, debug, hex_BA8):
        tmp_add = []
        tmp_hex = deepcopy(hex_BA8)
        for i in range(self.length):
            A = debug[i]
            B = tmp_add[-1] if tmp_add else 0
            C = (hex_BA8[i + 1] + B) % 0x100
            tmp_add.append(C)
            D = tmp_hex[C]
            tmp_hex[i + 1] = D
            E = (D * 2) % 0x100
            F = tmp_hex[E]
            G = A ^ F
            debug[i] = G
        return debug

    def calculate(self, debug):
        for i in range(self.length):
            A = debug[i]
            B = reverse(A)
            C = debug[(i + 1) % self.length]
            D = B ^ C
            E = RBIT(D)
            F = E ^ self.length
            G = ~F + (1 << 32) if F < 0 else ~F
            H = int(hex(G)[-2:], 16)
            debug[i] = H
        return debug

    def main(self):
        result = ''.join(hex_string(i) for i in self.calculate(self.initial(self.debug, self.addr_BA8())))
        return f'8404{hex_string(self.hex_CE0[7])}{hex_string(self.hex_CE0[3])}{hex_string(self.hex_CE0[1])}{hex_string(self.hex_CE0[6])}{result}'


def generate_gorgon(param="", data=None, cookie=None):
    gorgon = []
    ttime = time()
    Khronos = hex(int(ttime))[2:]
    url_md5 = md5(param.encode('utf-8')).hexdigest()
    gorgon += [int(url_md5[i:i + 2], 16) for i in range(0, 8, 2)]

    if data:
        if isinstance(data, str):
            data = data.encode('utf-8')
        data_md5 = md5(data).hexdigest()
        gorgon += [int(data_md5[i:i + 2], 16) for i in range(0, 8, 2)]
    else:
        gorgon += [0x00] * 4

    if cookie:
        cookie_md5 = md5(cookie.encode('utf-8')).hexdigest()
        gorgon += [int(cookie_md5[i:i + 2], 16) for i in range(0, 8, 2)]
    else:
        gorgon += [0x00] * 4

    gorgon += [0x1, 0x1, 0x2, 0x4]
    gorgon += [int(Khronos[i:i + 2], 16) for i in range(0, 8, 2)]

    return {
        'X-Gorgon': XG(gorgon).main(),
        'X-Khronos': str(int(ttime))
    }


def main():
    print("=== X-Gorgon & X-Khronos Generator ===")
    param = input("Enter param string: ")
    data = input("Enter request body (leave empty if none): ")
    cookie = input("Enter cookie string (leave empty if none): ")

    headers = generate_gorgon(param, data or None, cookie or None)
    print("\nGenerated Headers:")
    print(f"X-Gorgon:  {headers['X-Gorgon']}")
    print(f"X-Khronos: {headers['X-Khronos']}")


if __name__ == "__main__":
    main()
