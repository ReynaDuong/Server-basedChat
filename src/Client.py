import socket
import sys
import util
import hashlib
from random import randint


debug = True


def main():
    client_id = 'Client-ID-%s' % sys.argv[1]

    client_instances = {
        'Client-ID-A': {
            'LongTermKey': 'aaa',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-B': {
            'LongTermKey': 'bbb',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-C': {
            'LongTermKey': 'ccc',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-D': {
            'LongTermKey': 'ddd',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-E': {
            'LongTermKey': 'eee',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-F': {
            'LongTermKey': 'fff',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-G': {
            'LongTermKey': 'ggg',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-H': {
            'LongTermKey': 'hhh',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-I': {
            'LongTermKey': 'iii',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-J': {
            'LongTermKey': 'jjj',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        }
    }

    # Define the port on which you want to connect
    host = "127.0.0.1"
    udp_port = 7777
    tcp_port = 0

    new_connection = True
    is_authenticated = False

    message = input(client_id + ': ')
    if message != 'Log on':
        return

    # new_connection = False
    # is_authenticated = True

    while True:
        # Authentication
        if not is_authenticated:

            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.bind((host, udp_port))

            if new_connection:
                message = 'HELLO(%s)' % client_id
                udp_socket.sendto(message.encode(), (host, 9999))

                if debug:
                    print('Sending %s' % message)

                udp_socket.close()
                new_connection = False

            else:
                message, udp_addr = udp_socket.recvfrom(4096)
                message = message.decode('utf-8')

                if debug:
                    print('Receiving %s from %s' % (message, udp_addr))

                if message.startswith('CHALLENGE'):
                    rand = util.get_substring_between_parentheses(message)
                    response = hashlib.sha1(client_instances[client_id]['LongTermKey'].encode('utf-8') +
                                            rand.encode()).hexdigest()
                    message = 'RESPONSE(%s,%s)' % (client_id, response)

                elif message.startswith('AUTH_SUCCESS'):
                    rand_cookie, tcp_port = util.get_substring_between_parentheses(message).split(',')
                    client_instances[client_id]['Cookie'] = rand_cookie
                    message = 'CONNECT(%s)' % rand_cookie

                elif message.startswith('AUTH_FAIL'):
                    print('Server: Fail to authenticate :( meow')
                    udp_socket.close()
                    break

                elif message.startswith('CONNECTED'):
                    print('You are now connected :)')
                    udp_socket.close()
                    is_authenticated = True
                    continue

                if debug:
                    print('Sending %s to %s' % (message, udp_addr))

                udp_socket.sendto(message.encode(), udp_addr)
                udp_socket.close()

        # Chat phase
        else:
            print('connected now on chat session')
            message = ''

            while True:
                tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                print("TCP Socket successfully created")
                tcp_client_socket.connect((host, 12345))
                raw_input = input(client_id + ': ')

                if raw_input.startswith('Chat '):
                    chat_client = raw_input.split(' ')[1]
                    message = 'CHAT_REQUEST(%s,%s)' % (client_id, chat_client)

                elif message.startswith('End chat'):
                    # message = 'END_REQUEST(session-ID)'
                    pass

                elif raw_input == 'Log off':
                    message = 'LOG_OFF(%s,%s)' % (client_id, rand_cookie)

                    if debug:
                        print('Sending %s' % message)

                    tcp_client_socket.send(message.encode('utf-8'))
                    tcp_client_socket.close()
                    return

                else:
                    message = raw_input

                tcp_client_socket.send(message.encode('utf-8'))
                tcp_client_socket.close()


main()
