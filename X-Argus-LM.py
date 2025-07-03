**THE ARGUS GIVEN IS TOO SHORT AND POSSIBLY WONt WORK**

import base64
import hashlib
import json
import random
import struct
import time
from copy import deepcopy
from random import choice
import argus_protobuf_pb2
from Crypto.Cipher import AES
from pysmx.SM3 import SM3

unpad = lambda s: s[: -ord(s[len(s) - 1 :])]
pad = lambda s: s + (chr((16 - (len(s) % 16))).encode() * (16 - (len(s) % 16)))

def calc_protobuf_value(d):
    # Important logic preserved
    return 0 ^ (d >> 31)  # XOR with high (which was always 0)

def calc_sm3(data):
    sm3 = SM3()
    sm3.update(data)
    return sm3.digest()

def rotate_right_64(num, k):
    while num < 0:
        num += 0x10000000000000000
    bits = bin(num)[2:].zfill(64)
    return int(bits[-k:] + bits[:-k], 2)

def encode_timestamp(ts):
    high = 0
    low = ((ts << 1) & 0xFFFFFFFF) ^ (high >> 31)
    r0 = (ts << 1) | (ts >> 31)
    t = r0 ^ (high >> 31)
    return low | (t << 32)

def reverse_bits(num):
    bits = bin(num)[2:].zfill(8)
    return int(bits[::-1], 2)

def to_hex_string(num):
    return hex(num)[2:].zfill(2)

def aes_encrypt(data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(data))

def aes_decrypt(ciphertext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext))

def bfi(rd, rn, lsb, width):
    mask = (1 << width) - 1
    inserted_bits = (rn & mask) << lsb
    cleared_rd = rd & ~(mask << lsb)
    return cleared_rd | inserted_bits

def get_x_argus_header(url, xkhronos, deviceid="", stub=""):
    data = url.split("?", 1)[1]
    xargus = Xargus(data, int(xkhronos), deviceid, stub)
    return xargus.main_encrypt()

class Xargus:
    def __init__(self, data, khronos, device="", stub=""):
        self._data = data
        self._stub = stub
        self._argus_version = 0x4020100
        self._app_version = "15.7.0"
        self._unknown8 = "v04.02.01-ml-android"
        self._device_id = device
        self._khronos = khronos
        self._unknown16 = "AbEP0QSeJStUszOoH-i5-Q7nE"

        # These should be real secret keys
        self._sign_key1 = [0xAA, 0xBB, 0xCC]
        self._sign_key2 = [0xDD, 0xEE, 0xFF]

        self._aes_key = hashlib.md5(bytes(self._sign_key1)).digest()
        self._aes_iv = hashlib.md5(bytes(self._sign_key2)).digest()

        self._random_val = random.randint(0x10000000, 0xFFFFFFFF)
        self._apd = []

    def _encrypt_random(self, key):
        A = 0
        T = 0
        for i in range(0, len(key), 2):
            B = key[i] ^ A
            C = (T >> 3) & 0xFFFFFFFF
            D = C ^ B
            E = D ^ T
            F = (E >> 5) & 0xFFFFFFFF
            G = (E << 11) & 0xFFFFFFFF
            H = key[i + 1] | G
            I = F ^ H
            J = I ^ E
            T = ~J & 0xFFFFFFFF
            return T

    def _generate_key(self):
        data = (
            self._sign_key1 + self._sign_key2 +
            list(struct.pack("<I", self._random_val)) +
            self._sign_key1 + self._sign_key2
        )
        sm3 = SM3()
        sm3.update(bytes(data))
        hex_digest = sm3.hexdigest()

        res_list = [int(hex_digest[i:i+2], 16) for i in range(0, len(hex_digest), 2)]
        sm3_list = [struct.unpack("<I", bytes(res_list[i:i+4]))[0] for i in range(0, len(res_list), 4)]

        res_list = res_list[:8]
        for i in range(0x47):
            t = i % 0x3E
            offset = (0x20 - t) & 0xFF
            offset_1 = t - 0x20
            B = 0x3DC94C3A >> offset_1 if offset_1 >= 0 else 0

            H = ((sm3_list[6] >> 3) | (sm3_list[7] << 29)) & 0xFFFFFFFF
            C = H ^ sm3_list[2]
            B = bfi(B, 0x7FFFFFFE, 1, 0x1F)

            H = ((sm3_list[7] >> 3) | (sm3_list[6] << 29)) & 0xFFFFFFFF
            E = H ^ sm3_list[3]
            B = ((C >> 1) | 0x80000000) if E & 1 else (C >> 1)
            F = (E >> 1) | H
            G = F ^ sm3_list[1] ^ E
            A = ~G & 0xFFFFFFFF
            D = A
            F = D ^ B
            sm3_list = sm3_list[2:] + [F, A]

            for j in range(2):
                res_list += list(struct.pack("<I", sm3_list[j]))
        return res_list

    def _generate_protobuf(self):
        argus = argus_protobuf_pb2.Argus()
        argus.header = 1077940818
        argus.version = 2
        argus.random = 422182720
        argus.stub = "1128"
        argus.deviceId = self._device_id
        argus.appVersion = self._app_version
        argus.unknown8 = self._unknown8
        argus.argusVersion = calc_protobuf_value(self._argus_version)
        argus.unknown10 = b"\x00\x01\x00\x00\x00\x00\x00\x00"
        argus.khronosOne = encode_timestamp(self._khronos)

        stub_sm3 = calc_sm3(self._stub.encode()) if self._stub else b"\x00" * 16
        url_sm3 = calc_sm3(self._data.encode())

        self._apd.append(stub_sm3[0])
        self._apd.append(url_sm3[0])
        argus.sm3One = stub_sm3[:6]
        argus.sm3Two = url_sm3[:6]

        unknown15 = argus_protobuf_pb2.UnknownStruct15()
        unknown15.unknown1 = 0
        unknown15.unknown2 = 0
        unknown15.unknown3 = 0
        argus.unknown15.CopyFrom(unknown15)

        argus.khronosTwo = encode_timestamp(self._khronos)
        argus.unknown20 = "none"
        argus.unknown21 = "738"

        return argus.SerializeToString()

    def encrypt(self, proto_block, key):
        key_parts = [struct.unpack("<I", bytes(key[i:i+4]))[0] for i in range(0, len(key), 4)]
        for i in range(len(key_parts)):
            t = i % 4
            # Placeholder for important but incomplete logic
            AA, BB, EE = 0, 0, 0  # Should be properly defined
            BB = ((proto_block[(2 + t) % 4] << 1) | (proto_block[3 - t] >> 31)) & 0xFFFFFFFF
            CC = AA & BB
            DD = proto_block[t] ^ CC
            proto_block[t] = key_parts[i] ^ DD ^ EE
        return [b for val in proto_block for b in struct.pack("<I", val)]

    def decrypt(self, proto_block, key):
        key_parts = [struct.unpack("<I", bytes(key[i:i+4]))[0] for i in range(0, len(key), 4)]
        for i in reversed(range(len(key_parts))):
            t = i % 4
            # Placeholder for important but incomplete logic
            AA, BB, EE = 0, 0, 0
            CC = AA & BB
            DD = proto_block[t] ^ CC
            proto_block[t] = key_parts[i] ^ DD ^ EE
        return [b for val in proto_block for b in struct.pack("<I", val)]

    def xor_with_random(self, key, data):
        rand = self._encrypt_random(key)
        rand_bytes = struct.pack(">I", rand)
        return [b ^ rand_bytes[i % 4] for i, b in enumerate(data)]

    def main_encrypt(self):
        key = self._generate_key()
        protobuf_data = pad(self._generate_protobuf())
        result = []

        for i in range(0, len(protobuf_data), 16):
            block = [struct.unpack("<I", protobuf_data[i + j:i + j + 4])[0] for j in range(0, 16, 4)]
            result.extend(self.encrypt(block, key))

        random_arr = list(struct.pack("<I", self._random_val))
        xor_key = random_arr[2:4]
        base64_header = random_arr[0:2]

        result = result[::-1]
        result += [0x0, 0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0][::-1]
        result = self.xor_with_random(xor_key, result)
        result += xor_key

        headers = [
            0x35,  # Constant prefix
            0x00,  # Placeholder for key marker
            0x00,  # Placeholder
            0x00,  # Placeholder
            random.randint(0x10, 0xFF),
            0x00,
            self._apd[0] & 0x3F,
            0x02,
            0x18,
        ] + result

        encrypted = aes_encrypt(bytes(headers), self._aes_key, self._aes_iv)
        return base64.b64encode(bytes(base64_header) + encrypted).decode()
