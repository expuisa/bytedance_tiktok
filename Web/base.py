from base64 import b64encode, b64decode

def node_b64(s):
    i = 0
    base64 = ending = ""
    base64chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    pad = 3 - len(s) % 3
    if pad != 3:
        s += "A" * pad
        ending += "=" * pad
    while i < len(s):
        b = 0
        for j in range(0, 3, 1):
            n = ord(s[i])
            i += 1
            b += n << 8 * (2 - j)
        base64 += base64chars[b >> 18 & 63]
        base64 += base64chars[b >> 12 & 63]
        base64 += base64chars[b >> 6 & 63]
        base64 += base64chars[b & 63]
    if pad != 3:
        base64 = base64[:-pad]
        base64 += ending
    return base64


def reverse_node_b64(base64):
    base64chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    s = ''
    for i in range(0, len(base64), 4):
        b = 0
        for j in range(4):
            if i+j < len(base64):
                n = base64chars.index(base64[i+j])
                b += n << 6*(3-j)
        s += chr(b >> 16 & 0xFF) + chr(b >> 8 & 0xFF) + chr(b & 0xFF)
    s = s.rstrip('A')
    s = s[:-len(s)%4]
    return s


# plain = "abc"
# encoded  = node_b64(plain)
# print(encoded)
# decoded = b64decode(encoded.encode())
# print(decoded)