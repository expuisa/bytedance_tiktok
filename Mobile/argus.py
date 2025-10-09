from random import randint
from time import time
from struct import unpack
from base64 import b64encode
from hashlib import md5
from urllib.parse import parse_qs
from Crypto.Cipher.AES import new, MODE_CBC, block_size
from Crypto.Util.Padding import pad
from signer.lib.Sm3 import SM3
from signer.lib.Simon import simon_enc
from signer.lib.protobuf import ProtoBuf

# @srcxd @expuisa @comedien_de_merde
class Argus:
    SIGN_KEY = b'\xac\x1a\xda\xae\x95\xa7\xaf\x94\xa5\x11J\xb3\xb3\xa9}\xd8\x00P\xaa\n91L@R\x8c\xae\xc9RV\xc2\x8c'
    SM3_OUTPUT = b'\xfcx\xe0\xa9ez\x0ct\x8c\xe5\x15Y\x90<\xcf\x03Q\x0eQ\xd3\xcf\xf22\xd7\x13C\xe8\x8a2\x1cS\x04'

    @staticmethod
    def encrypt_enc_pb(data, length):
        data = list(data)
        xor_array = data[:8]

        for i in range(8, length):
            data[i] ^= xor_array[i % 8]

        return bytes(data[::-1])

    @staticmethod
    def get_bodyhash(stub=None):
        if stub is None or len(stub) == 0:
            return SM3().sm3_hash(bytes(16))[0:6]
        return SM3().sm3_hash(bytes.fromhex(stub))[0:6]

    @staticmethod
    def get_queryhash(query):
        if query is None or len(query) == 0:
            return SM3().sm3_hash(bytes(16))[0:6]
        return SM3().sm3_hash(query.encode())[0:6]

    @staticmethod
    def _prepare_key_list(key):
        key_list = []
        for i in range(2):
            key_list.extend(list(unpack("<QQ", key[i * 16:(i + 1) * 16])))
        return key_list

    @staticmethod
    def _encrypt_blocks(protobuf, key_list, new_len):
        enc_pb = bytearray(new_len)

        for block_idx in range(new_len // 16):
            offset = block_idx * 16
            pt = list(unpack("<QQ", protobuf[offset:offset + 16]))
            ct = simon_enc(pt, key_list)
            enc_pb[offset:offset + 8] = ct[0].to_bytes(8, byteorder="little")
            enc_pb[offset + 8:offset + 16] = ct[1].to_bytes(8, byteorder="little")

        return enc_pb

    @staticmethod
    def encrypt(xargus_bean):
        protobuf = pad(bytes.fromhex(ProtoBuf(xargus_bean).toBuf().hex()), block_size)
        new_len = len(protobuf)

        key = Argus.SM3_OUTPUT[:32]
        key_list = Argus._prepare_key_list(key)
        enc_pb = Argus._encrypt_blocks(protobuf, key_list, new_len)

        header = b"\xf2\xf7\xfc\xff\xf2\xf7\xfc\xff"
        b_buffer = Argus.encrypt_enc_pb(header + enc_pb, new_len + 8)
        b_buffer = b'\xa6n\xad\x9fw\x01\xd0\x0c\x18' + b_buffer + b'ao'

        cipher = new(
            md5(Argus.SIGN_KEY[:16]).digest(),
            MODE_CBC,
            md5(Argus.SIGN_KEY[16:]).digest()
        )

        return b64encode(b"\xf2\x81" + cipher.encrypt(pad(b_buffer, block_size))).decode()

    @staticmethod
    def _parse_app_version(version_name):
        parts = version_name.split('.')
        app_version_hash = bytes.fromhex(
            '{:x}{:x}{:x}00'.format(
                int(parts[2]) * 4,
                int(parts[1]) * 16,
                int(parts[0]) * 4
            ).zfill(8)
        )
        return int.from_bytes(app_version_hash, byteorder='big') << 1

    @staticmethod
    def _parse_os_version(os_version_str):
        os_parts = os_version_str.split(".")
        os_parts.extend([0] * (3 - len(os_parts)))
        return ((int(os_parts[0]) - 4) +
                int(os_parts[1]) * 256 +
                int(os_parts[2]) * 4096) * 2

    @staticmethod
    def get_sign(queryhash=None,
                 data=None,
                 timestamp=None,
                 aid=1233,
                 license_id=1611921764,
                 platform=0,
                 sec_device_id="",
                 sdk_version="v05.00.03-ov-android",
                 sdk_version_int=167773760):

        if timestamp is None:
            timestamp = int(time())

        params_dict = parse_qs(queryhash)

        app_version_constant = Argus._parse_app_version(params_dict['version_name'][0])
        # meta_sec_constant = Argus._parse_os_version(params_dict['os_version'][0])

        xargus_bean = {
            1: 0x20200929 << 1,
            2: 2,
            3: randint(0, 0x7FFFFFFF),
            4: str(aid),
            5: params_dict['device_id'][0],
            6: str(license_id),
            7: params_dict['version_name'][0],
            8: sdk_version,
            9: sdk_version_int,
            10: bytes(8),
            11: "android",
            12: timestamp << 1,
            13: Argus.get_bodyhash(data),
            14: Argus.get_queryhash(queryhash),
            15: {
                1: 85,
                2: 85,
                3: 85,
                5: 85,
                6: 170,
                7: (timestamp << 1) - 310
            },
            16: sec_device_id,
            20: "none",
            21: 738,
            23: {
                1: params_dict['device_type'][0],
                2: 0,
                3: 'googleplay',
                4: app_version_constant
            },
            25: 2
        }

        return Argus.encrypt(xargus_bean)
