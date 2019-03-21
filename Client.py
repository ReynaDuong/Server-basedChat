# TODO
# authentication before get connected
# hello is sent using UDP
# how does server keeps IP address and port number of clients?
# send according to the Client name

# Import socket module
import socket
import sys
import util
import hashlib


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
    tcp_port = 0

    new_connection = True
    authenticated = False
    connected = False
    message = ''

    while True:
        # Authentication
        if not connected:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip, udp_port = udp_socket.getsockname()

            if new_connection:
                message = 'HELLO(%s)' % client_id
                udp_socket.sendto(message.encode(), (host, 9999))
                print('Sending %s' % message)
                # udp_socket.close()
                new_connection = False
            else:
                print('line 72')
                udp_socket.connect((ip, udp_port))
                print('line 74')
                message, udp_addr = udp_socket.recvfrom(4096)
                print('line 76')
                message = message.decode('utf-8')

                print('Receiving %s' % message)

                if message.startswith('CHALLENGE'):
                    rand = util.get_substring_between_parentheses(message)
                    response = hashlib.sha1(client_instances[client_id]['LongTermKey'] + str(rand))
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

                print('Sending %s' % message)
                print(new_connection)

                # udp_socket.close()

        else:
            print('connected now on chat session')


main()
