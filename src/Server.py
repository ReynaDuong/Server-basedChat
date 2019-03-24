import socket
import sys
import hashlib
from random import randint
import util
from threading import Thread

udp_port = 9999
tcp_port = 12345
host = "127.0.0.1"
debug = True
global_session_count = randint(0, 1000)

clients = {
    'Client-ID-A': {
        'Online': False,
        'LongTermKey': 'aaa',
        'SessionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-B': {
        'Online': False,
        'LongTermKey': 'bbb',
        'SessionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-C': {
        'Online': False,
        'LongTermKey': 'ccc',
        'SessionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-D': {
        'Online': False,
        'LongTermKey': 'ddd',
        'SessionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-E': {
        'Online': False,
        'LongTermKey': 'eee',
        'SessionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-F': {
        'Online': False,
        'LongTermKey': 'fff',
        'SessionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-G': {
        'Online': False,
        'LongTermKey': 'ggg',
        'SessionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-H': {
        'Online': False,
        'LongTermKey': 'hhh',
        'SessionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-I': {
        'Online': False,
        'LongTermKey': 'iii',
        'SessionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-J': {
        'Online': False,
        'LongTermKey': 'jjj',
        'SessionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    }
}


def handle_tcp_connection(tcp_client):
    required_ack = True

    try:
        message = tcp_client.recv(4096)
        message = message.decode()

        if debug:
            print('Receiving %s' % message)

        data = util.get_substring_between_parentheses(message)

        if message.startswith('CHAT_REQUEST'):
            from_client_id, to_client_id = data.split(',')

            if clients[to_client_id]['Online']:
                global global_session_count
                global_session_count = global_session_count + 1

                clients[from_client_id]['SessionID'] = str(global_session_count)
                clients[to_client_id]['SessionID'] = str(global_session_count)

                # send to to_client
                message = 'CHAT_START(%d,%s)' % (global_session_count, from_client_id)
                clients[to_client_id]['QueuedMessages'].append(message)

                if debug:
                    print('%s queued messages = %s' %
                          (to_client_id,
                           ''.join(str(e) for e in clients[to_client_id]['QueuedMessages'])))

                # send to current client (from_client)
                message = 'CHAT_START(%d,%s)' % (global_session_count, to_client_id)
            else:
                message = 'UNREACHABLE(%s)' % to_client_id

        elif message.startswith('END_REQUEST'):
            client_id, session_id = data.split(',')

            for key, value in clients.items():

                if debug:
                    print(key)
                    print(value)

                if value['SessionID'] == session_id:

                    if debug:
                        print('%s to end chat: ' % key)

                    value['SessionKey'] = ''
                    value['SessionID'] = ''
                    value['Cookie'] = ''

                    if key != client_id:
                        value['QueuedMessages'].append('END_NOTIF(%s)' % session_id)

            required_ack = False

        elif message.startswith('PING'):
            from_client_id = data
            message = ''.join(str(e) for e in clients[from_client_id]['QueuedMessages'])
            clients[from_client_id]['QueuedMessages'] = []

        elif message.startswith('LOG_OFF'):
            client_id, cookie = util.get_substring_between_parentheses(message).split(',')
            required_ack = False

            if clients[client_id]['Cookie'] == cookie:
                clients[client_id]['Online'] = False
                clients[client_id]['SessionKey'] = ''
                clients[client_id]['SessionID'] = ''
                clients[client_id]['Cookie'] = ''

                if debug:
                    print('Reset all variables for %s' % client_id)
            else:
                if debug:
                    print('Receive LOG_OFF command for %s but wrong %s for cookie' %
                          (client_id, cookie))

        else:
            print('Unknown command')

        if required_ack:
            if message is None or len(message) == 0:
                message = 'NO_DATA'

            if debug:
                print('Sending %s' % message)

            tcp_client.send(message.encode('utf-8'))

    # except socket.timeout:
    #     print('Wait too long')

    finally:
        tcp_client.close()
        pass


def tcp_connection():
    if debug:
        print('Start handle_tcp_connection()')

    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("TCP Socket successfully created")

    try:
        tcp_server_socket.bind((host, tcp_port))
        print("TCP Socket is bind to %s" % tcp_port)
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    # put the socket into listening mode
    tcp_server_socket.listen(5)
    print("TCP Socket is listening")

    while True:
        # Chat session
        tcp_client, tcp_addr = tcp_server_socket.accept()

        if tcp_client:
            print('Got TCP connection from', tcp_addr)
            thread = Thread(target=handle_tcp_connection, args=(tcp_client,))
            thread.start()
            # thread.join()
            # tcp_client.close()


def udp_connection():
    if debug:
        print('Start handle_udp_connection()')

    udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("UDP Socket successfully created")

    try:
        udp_server_socket.bind((host, udp_port))
        print("UDP Socket is bind to %s" % udp_port)
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    while True:
        # Authenticate
        message, udp_addr = udp_server_socket.recvfrom(4096)

        if udp_addr:
            if debug:
                print('Got UDP connection from', udp_addr)
            message = message.decode()

            if debug:
                print('Receiving %s' % message)

            if message.startswith('HELLO'):
                client_id = util.get_substring_between_parentheses(message)
                clients[client_id]['Online'] = True
                challenge = randint(-1 * sys.maxsize - 1, sys.maxsize)
                xres = hashlib.sha1((clients[client_id]['LongTermKey'] +
                                     str(challenge)).encode()).hexdigest()
                clients[client_id]['SessionKey'] = xres

                if debug:
                    print('xres = %s' % xres)

                message = 'CHALLENGE(%d)' % challenge

            elif message.startswith('RESPONSE'):
                client_id, res = util.get_substring_between_parentheses(message).split(',')
                if clients[client_id]['SessionKey'] == res.strip():
                    cookie = randint(-1 * sys.maxsize - 1, sys.maxsize)
                    clients[client_id]['Cookie'] = str(cookie)
                    message = 'AUTH_SUCCESS(%d,%d)' % (cookie, tcp_port)
                else:
                    message = 'AUTH_FAIL'
                    clients[client_id]['Online'] = False
                    clients[client_id]['SessionKey'] = ''
                    clients[client_id]['Cookie'] = ''
                    clients[client_id]['SessionID'] = ''

            elif message.startswith('CONNECT'):
                message = 'CONNECTED'

            if debug:
                print('Sending %s' % message)

        udp_server_socket.sendto(message.encode(), udp_addr)

        # close here cause next connection not to be accepted?
        # udp_server_socket.close()


def main():
    udp_thread = Thread(target=udp_connection, args=())
    tcp_thread = Thread(target=tcp_connection, args=())

    udp_thread.start()
    tcp_thread.start()


main()
