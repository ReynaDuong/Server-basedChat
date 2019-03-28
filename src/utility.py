import base64
from Crypto.Cipher import AES


def get_substring_between_parentheses(message):
    return message[message.find("(") + 1:message.find(")")]


def encrypt(message, key, iv):
    aes = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + aes.encrypt(message))


def decrypt(message, key, iv):
    b64_message = base64.b64decode(message)
    aes = AES.new(key, AES.MODE_CBC, iv)
    return aes.decrypt(b64_message)
