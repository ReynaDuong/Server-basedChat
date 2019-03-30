import base64
from Crypto.Cipher import AES
import platform


def get_substring_between_parentheses(message):
    return message[message.find("(") + 1:message.find(")")]


def encrypt(message, key, iv):
    aes = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + aes.encrypt(message))


def decrypt(message, key, iv):
    b64_message = base64.b64decode(message)
    aes = AES.new(key, AES.MODE_CBC, iv)
    return aes.decrypt(b64_message)


def detect_keyboard_hit():
    if platform.system().startswith('Win'):
        import msvcrt
        return msvcrt.kbhit()
    else:
        import tty, sys
        tty.setcbreak(sys.stdin)
        return sys.stdin.read(1)


# def get_char_console():
#     if platform.system().startswith('Win'):
#         import msvcrt
#         return msvcrt.getch()
#     else:
#         import sys, tty, termios
#         fd = sys.stdin.fileno()
#         old_settings = termios.tcgetattr(fd)
#         try:
#             tty.setraw(sys.stdin.fileno())
#             ch = sys.stdin.read(1)
#         finally:
#             termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
#         return ch
