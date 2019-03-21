# TODO
# authentication before accepting messages

import socket
import sys
import hashlib
from random import randint
import util


def main():
    # Define host and port number
    udp_port = 9999
    tcp_port = 12345
    host = "127.0.0.1"

    subscriber_list = {
        'Client-ID-A': {
            'Online': False,
            'LongTermKey': '123',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-B': {
            'Online': False,
            'LongTermKey': '456',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-C': {
            'Online': False,
            'LongTermKey': '789',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-D': {
            'Online': False,
            'LongTermKey': '000',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-E': {
            'Online': False,
            'LongTermKey': 'abc',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        }
    }

    udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("UDP Socket successfully created")

    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("TCP Socket successfully created")

    # bind the socket with address and port number
    try:
        udp_server_socket.bind((host, udp_port))
        print("UDP Socket is bind to %s" % udp_port)

        tcp_server_socket.bind((host, tcp_port))
        print("TCP Socket is bind to %s" % tcp_port)
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    # put the socket into listening mode
    tcp_server_socket.listen(5)
    print("Socket is listening")

    # keep server online
    while True:

        # Authenticate
        message, udp_addr = udp_server_socket.recvfrom(4096)

        if udp_addr:
            print('Got UDP connection from', udp_addr)
            message = message.decode()

            print('Receiving %s' % message)

            if message.startswith('HELLO'):
                client_id = util.get_substring_between_parentheses(message)
                subscriber_list[client_id]['Online'] = True
                challenge = randint(-1 * sys.maxsize - 1, sys.maxsize)
                xres = hashlib.sha1((subscriber_list[client_id]['LongTermKey'] +
                                     str(challenge)).encode()).hexdigest()
                subscriber_list[client_id]['SessionKey'] = xres
                print('xres = %s' % xres)
                message = 'CHALLENGE(%d)' % challenge

            elif message.startswith('RESPONSE'):
                client_id, res = util.get_substring_between_parentheses(message).split(',')
                if subscriber_list[client_id]['SessionKey'] == res.strip():
                    cookie = randint(-1 * sys.maxsize - 1, sys.maxsize)
                    subscriber_list[client_id]['Cookie'] = str(cookie)
                    message = 'AUTH_SUCCESS(%d,%d)' % (cookie, tcp_port)
                else:
                    message = 'AUTH_FAIL'
                    subscriber_list[client_id]['Online'] = False
                    subscriber_list[client_id]['SessionKey'] = ''
                    subscriber_list[client_id]['Cookie'] = ''
                    subscriber_list[client_id]['SessionID'] = ''

            elif message.startswith('CONNECT'):
                message = 'CONNECTED'

            print('Sending %s' % message)

        udp_server_socket.sendto(message.encode(), udp_addr)
        # udp_server_socket.close()

        # Chat session
        # tcp_client, tcp_addr = tcp_server_socket.accept()
        #
        # if tcp_client:
        #     print('Got TCP connection from', tcp_addr)


main()
