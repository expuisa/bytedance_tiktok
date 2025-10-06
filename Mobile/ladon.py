import base64
import hashlib
import ctypes
from os import urandom
from signer.lib.pkcs7_padding import pkcs7_padding_pad_buffer, padding_size

class Ladon:
    ROUNDS = 0x22
    ROTATION_RIGHT = 8
    ROTATION_LEFT = 0x3D
    UINT64_MASK = 0xFFFFFFFFFFFFFFFF

    @staticmethod
    def encrypt(x_khronos, lc_id, aid):
        return ladon_encrypt(x_khronos, lc_id, aid)

def md5bytes(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()

def get_type_data(ptr, index, data_type):
    if data_type == "uint64_t":
        return int.from_bytes(ptr[index * 8:(index + 1) * 8], "little")
    raise ValueError("Invalid data type")

def set_type_data(ptr, index, data, data_type):
    if data_type == "uint64_t":
        ptr[index * 8:(index + 1) * 8] = data.to_bytes(8, "little")
    else:
        raise ValueError("Invalid data type")

def validate(num):
    return num & Ladon.UINT64_MASK

def rotate_right(value, count):
    nbits = ctypes.sizeof(ctypes.c_ulonglong) * 8
    count %= nbits
    low = ctypes.c_ulonglong(value.value << (nbits - count)).value
    value = ctypes.c_ulonglong(value.value >> count).value
    return value | low

def build_hash_table(md5hex):
    hash_table = bytearray(272 + 16)
    hash_table[:32] = md5hex

    temp = []
    for i in range(4):
        temp.append(int.from_bytes(hash_table[i * 8:(i + 1) * 8], byteorder="little"))

    buffer_b0 = temp[0]
    buffer_b8 = temp[1]
    temp = temp[2:]

    for i in range(Ladon.ROUNDS):
        x9 = buffer_b0
        x8 = buffer_b8
        x8 = validate(rotate_right(ctypes.c_ulonglong(x8), 8))
        x8 = validate(x8 + x9)
        x8 = validate(x8 ^ i)
        temp.append(x8)
        x8 = validate(x8 ^ rotate_right(ctypes.c_ulonglong(x9), 61))
        set_type_data(hash_table, i + 1, x8, "uint64_t")
        buffer_b0 = x8
        buffer_b8 = temp.pop(0)

    return hash_table

def encrypt_ladon_input(hash_table, input_data):
    data0 = int.from_bytes(input_data[:8], byteorder="little")
    data1 = int.from_bytes(input_data[8:], byteorder="little")

    for i in range(Ladon.ROUNDS):
        hash_val = int.from_bytes(hash_table[i * 8:(i + 1) * 8], byteorder="little")
        data1 = validate(hash_val ^ (data0 + ((data1 >> 8) | (data1 << 56))))
        data0 = validate(data1 ^ ((data0 >> 0x3D) | (data0 << 3)))

    output_data = bytearray(26)
    output_data[:8] = data0.to_bytes(8, byteorder="little")
    output_data[8:] = data1.to_bytes(8, byteorder="little")

    return bytes(output_data)

def decrypt_ladon_input(hash_table, encrypted_data):
    data0 = int.from_bytes(encrypted_data[:8], byteorder="little")
    data1 = int.from_bytes(encrypted_data[8:], byteorder="little")

    for i in range(Ladon.ROUNDS - 1, -1, -1):
        hash_val = int.from_bytes(hash_table[i * 8:(i + 1) * 8], byteorder="little")
        data0 = validate(((data1 >> 0x3D) | (data1 << 3)) ^ data0)
        data1 = validate(((data0 - hash_val) << 8 | (data0 - hash_val) >> 56) ^ data1)

    decrypted_data = bytearray(16)
    decrypted_data[:8] = data0.to_bytes(8, byteorder="little")
    decrypted_data[8:] = data1.to_bytes(8, byteorder="little")

    return bytes(decrypted_data)

def encrypt_ladon(md5hex, data, size):
    hash_table = build_hash_table(md5hex)
    new_size = padding_size(size)

    input_buffer = bytearray(new_size)
    input_buffer[:size] = data
    pkcs7_padding_pad_buffer(input_buffer, size, new_size, 16)

    output = bytearray(new_size)
    for i in range(new_size // 16):
        block_start = i * 16
        block_end = (i + 1) * 16
        output[block_start:block_end] = encrypt_ladon_input(
            hash_table,
            input_buffer[block_start:block_end]
        )

    return output

def decrypt_ladon(md5hex, encrypted_data, size):
    hash_table = build_hash_table(md5hex)

    decrypted_output = bytearray(size)
    for i in range(size // 16):
        block_start = i * 16
        block_end = (i + 1) * 16
        decrypted_output[block_start:block_end] = decrypt_ladon_input(
            hash_table,
            encrypted_data[block_start:block_end]
        )

    return decrypted_output.rstrip(b"\x00")

def ladon_encrypt(khronos, lc_id=1611921764, aid=1233, random_bytes=None):
    if random_bytes is None:
        random_bytes = urandom(4)

    data = f"{khronos}-{lc_id}-{aid}"
    keygen = random_bytes + str(aid).encode()
    md5hex = md5bytes(keygen)

    size = len(data)
    new_size = padding_size(size)

    output = bytearray(new_size + 4)
    output[:4] = random_bytes
    output[4:] = encrypt_ladon(md5hex.encode(), data.encode(), size)

    return base64.b64encode(bytes(output)).decode()
