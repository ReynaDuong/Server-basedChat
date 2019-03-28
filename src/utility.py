from base64 import b64encode, b64decode
from Crypto.Cipher import AES
import hashlib
from Crypto.Util.Padding import pad, unpad


def get_substring_between_parentheses(message):
    return message[message.find("(") + 1:message.find(")")]


def encrypt(message, key, iv):
    print('Encrypting...')
    
    print('message = ' + message)
    print('key = ' + key)
    print('iv = ' + iv)

    cipher = AES.new(hashlib.md5(key.encode('utf-8')).digest(),
                     AES.MODE_CBC,
                     hashlib.md5(iv.encode('utf-8')).digest())

    p = pad(message.encode('utf-8'), AES.block_size)

    print('p = ' + str(p))

    ct_bytes = cipher.encrypt(p)

    print('ct_bytes = ' + str(ct_bytes))

    result = b64encode(ct_bytes).decode('utf-8')

    print('result = ' + result)

    return result


def decrypt(message, key, iv):
    print('Decrypting...')

    print('message = ' + message)
    print('key = ' + key)
    print('iv = ' + iv)

    cipher = AES.new(hashlib.md5(key.encode('utf-8')).digest(),
                     AES.MODE_CBC,
                     hashlib.md5(iv.encode('utf-8')).digest())

    ct = b64decode(message)

    print('ct = ' + str(ct))

    d = cipher.decrypt(ct)

    print('d = ' + str(d))

    p = unpad(d, AES.block_size)

    print('p = ' + str(p))

    return p.decode('utf-8')

