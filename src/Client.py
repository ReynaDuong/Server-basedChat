import socket
import sys
import util
import hashlib


debug = False


def main():
    client_id = 'Client-ID-%s' % sys.argv[1]

    client_instances = {
        'Client-ID-A': {
            'LongTermKey': '123',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-B': {
            'LongTermKey': '456',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-C': {
            'LongTermKey': '789',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-D': {
            'LongTermKey': '000',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        },
        'Client-ID-E': {
            'LongTermKey': 'abc',
            'SessionKey': '',
            'SessionID': '',
            'Cookie': ''
        }
    }

    # Define the port on which you want to connect
    host = "127.0.0.1"
    udp_port = 7777
    tcp_port = 0
    is_authenticated = False

    new_connection = True
    connected = False

    if not is_authenticated:
        while True:
            # Authentication
            if not connected:
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
                        connected = True
                        continue

                    if debug:
                        print('Sending %s to %s' % (message, udp_addr))

                    udp_socket.sendto(message.encode(), udp_addr)
                    udp_socket.close()
                    is_authenticated = True

            else:
                if debug:
                    print('connected now on chat session')

                break

    # Chat session
    else:
        message = ''
        while True:
            tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("TCP Socket successfully created")
            tcp_client_socket.bind((host, tcp_port))

            raw_input = input(client_id + ': ')
            if raw_input.startswith('Chat '):
                chat_client = raw_input.split()[1]
                message = 'CHAT_REQUEST (%s)' % chat_client
            else:
                tcp_client_socket.send(message.encode('utf-8'))
                tcp_client_socket.close()


main()
