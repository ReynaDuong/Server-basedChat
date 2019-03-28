from base64 import b64encode, b64decode
from Crypto.Cipher import AES
import hashlib
from Crypto.Util.Padding import pad, unpad


def get_substring_between_parentheses(message):
    return message[message.find("(") + 1:message.find(")")]


def encrypt(message, key, iv):
    cipher = AES.new(hashlib.md5(key.encode('utf-8')).digest(),
                     AES.MODE_CBC,
                     hashlib.md5(iv.encode('utf-8')).digest())
    ct_bytes = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
    return b64encode(ct_bytes).decode('utf-8')


def decrypt(message, key, iv):
    ct = b64decode(message)
    cipher = AES.new(hashlib.md5(key.encode('utf-8')).digest(),
                     AES.MODE_CBC,
                     hashlib.md5(iv.encode('utf-8')).digest())
    return unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')

