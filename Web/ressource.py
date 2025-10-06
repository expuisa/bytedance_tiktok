import re, execjs, random

b64 = execjs.compile("e=(a=>btoa(a));")


def shift_b64(s):
    return re.sub(
        r"[A-Za-z0-9+/=]",
        lambda m: "Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe="[
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".index(
                m.group(0)
            )
        ],
        s,
    )


def rc4_encrypt(rand, o):
    t = [0] * 256
    for f in range(256):
        t[f] = f

    e = 0
    for h in range(256):
        e = (e + t[h] + ord(rand[h % len(rand)])) % 256
        a = t[h]
        t[h] = t[e]
        t[e] = a

    c = 0
    e = 0
    n = ""
    for v in range(len(o)):
        c = (c + 1) % 256
        e = (e + t[c]) % 256
        a = t[c]
        t[c] = t[e]
        t[e] = a
        n += chr(ord(o[v]) ^ t[(t[c] + t[e]) % 256])

    return n


def enc_eq(input):
    rand = chr(random.randint(0, 255))
    rc4_enc = rc4_encrypt(rand, input)
    b64_enc = b64.call("e", (rand + rc4_enc))

    return shift_b64(b64_enc)
