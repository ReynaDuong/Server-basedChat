import socket
import sys
import hashlib
from random import randint
import utility
from threading import Thread
import constant


udp_port = 9999
tcp_port = 12345
host = "127.0.0.1"
debug = True
global_session_count = randint(0, 1000)


clients = {
    'Client-ID-A': {
        'Online': False,
        'LongTermKey': 'aaa',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-B': {
        'Online': False,
        'LongTermKey': 'bbb',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-C': {
        'Online': False,
        'LongTermKey': 'ccc',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-D': {
        'Online': False,
        'LongTermKey': 'ddd',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-E': {
        'Online': False,
        'LongTermKey': 'eee',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-F': {
        'Online': False,
        'LongTermKey': 'fff',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-G': {
        'Online': False,
        'LongTermKey': 'ggg',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-H': {
        'Online': False,
        'LongTermKey': 'hhh',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-I': {
        'Online': False,
        'LongTermKey': 'iii',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    },
    'Client-ID-J': {
        'Online': False,
        'LongTermKey': 'jjj',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': '',
        'QueuedMessages': []
    }
}

histories = []


def handle_tcp_connection(tcp_client):
    required_ack = True
    global global_session_count

    try:
        message = tcp_client.recv(4096)
        message = message.decode()

        if debug:
            print('Receiving %s' % message)

        data = utility.get_substring_between_parentheses(message)

        if message.startswith('CHAT_REQUEST'):
            from_client_id, to_client_id = data.split(',')

            if clients[to_client_id]['Online'] is True and \
                    len(clients[to_client_id]['SessionID']) == 0:
                global_session_count = global_session_count + 1

                if debug:
                    print('Current global_session_count = %d' % global_session_count)

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
                if debug:
                    print('Unreachable')
                message = 'UNREACHABLE(%s)' % to_client_id

        elif message.startswith('END_REQUEST'):
            client_id, session_id = data.split(',')

            for key, value in clients.items():
                if value['SessionID'] == session_id:

                    if debug:
                        print('%s to end chat: ' % key)

                    value['SessionID'] = ''
                    value['Cookie'] = ''

                    if key != client_id:
                        value['QueuedMessages'].append('END_NOTIF(%s)' % session_id)

            required_ack = False

        elif message.startswith('PING'):
            from_client_id = data
            message = '<;>'.join(str(e) for e in clients[from_client_id]['QueuedMessages'])
            clients[from_client_id]['QueuedMessages'] = []

        elif message.startswith('LOG_OFF'):
            client_id, cookie = utility.get_substring_between_parentheses(message).split(',')
            required_ack = False

            if clients[client_id]['Cookie'] == cookie:
                clients[client_id]['Online'] = False
                clients[client_id]['AuthenticationKey'] = ''
                clients[client_id]['EncryptionKey'] = ''
                clients[client_id]['SessionID'] = ''
                clients[client_id]['Cookie'] = ''

                if debug:
                    print('Reset all variables for %s' % client_id)
            else:
                if debug:
                    print('Receive LOG_OFF command for %s but wrong %s for cookie' %
                          (client_id, cookie))

        elif message.startswith('CHAT'):
            client_id, session_id, data = data.split(',')

            if clients[client_id]['SessionID'] == session_id:
                history = {
                    'SessionID': session_id,
                    'Sender': client_id,
                    'Message': data
                }
                histories.append(history)

            for key, value in clients.items():
                if value['SessionID'] == session_id and key != client_id:
                    value['QueuedMessages'].append(message)
                    break

            required_ack = False

        elif message.startswith('HISTORY_REQ'):
            client_id = data.split(',')[0]
            chat_with = data.split(',')[1]

            if debug:
                print(histories)
                print('Requestor: %s - For: %s' % (client_id, chat_with))

            '''
            NOTE: this logic down here only works if both client send something
            in the session. If either of them does not send anything and just
            receiving, then this logic will miss that session
            '''

            is_populated_first_history_record = False

            # find all distinct sessions of the current client
            sessions_of_current_client = []
            for history in histories:
                if history['Sender'] == client_id and \
                        history['SessionID'] not in sessions_of_current_client:
                    sessions_of_current_client.append(history['SessionID'])

            if debug:
                print(sessions_of_current_client)

            # find all messages in the previously found sessions
            for history in histories:
                if history['SessionID'] in sessions_of_current_client:
                    temp_message = 'HISTORY_RESP(%s,%s,%s)' % \
                                   (history['SessionID'], history['Sender'], history['Message'])

                    if is_populated_first_history_record:
                        clients[client_id]['QueuedMessages'].append(temp_message)
                    else:
                        message = temp_message
                        is_populated_first_history_record = True

            required_ack = True

        else:
            print('Unknown command')

        if required_ack:
            if message is None or len(message) == 0:
                message = 'NO_DATA'

            if debug:
                print('Sending %s' % message)

            tcp_client.send(message.encode('utf-8'))

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


def udp_connection():
    if debug:
        print('Start handle_udp_connection()')

    is_encrypted_message = False
    client_id = ''
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
                print('Receiving (encrypted) %s' % message)

            if is_encrypted_message:
                message = utility.decrypt(message, clients[client_id]['EncryptionKey'], constant.default_iv)

                if debug:
                    print('Receiving (decrypted) %s' % message)

            if message.startswith('HELLO'):
                client_id = utility.get_substring_between_parentheses(message)
                clients[client_id]['Online'] = True
                challenge = randint(-1 * sys.maxsize - 1, sys.maxsize)

                xres = hashlib.sha1((clients[client_id]['LongTermKey'] +
                                     str(challenge)).encode()).hexdigest()
                clients[client_id]['AuthenticationKey'] = xres

                session_key = hashlib.sha256((clients[client_id]['EncryptionKey'] +
                                              str(challenge)).encode()).hexdigest()
                clients[client_id]['EncryptionKey'] = session_key

                message = 'CHALLENGE(%d)' % challenge

            elif message.startswith('RESPONSE'):
                client_id, res = utility.get_substring_between_parentheses(message).split(',')
                if clients[client_id]['AuthenticationKey'] == res.strip():
                    cookie = randint(-1 * sys.maxsize - 1, sys.maxsize)
                    clients[client_id]['Cookie'] = str(cookie)
                    message = 'AUTH_SUCCESS(%d,%d)' % (cookie, tcp_port)
                    is_encrypted_message = True
                else:
                    message = 'AUTH_FAIL'
                    clients[client_id]['Online'] = False
                    clients[client_id]['AuthenticationKey'] = ''
                    clients[client_id]['EncryptionKey'] = ''
                    clients[client_id]['Cookie'] = ''
                    clients[client_id]['SessionID'] = ''

            elif message.startswith('CONNECT'):
                message = 'CONNECTED'

            if debug:
                print('Sending %s' % message)

            if is_encrypted_message:
                message = utility.encrypt(message, clients[client_id]['EncryptionKey'], constant.default_iv)
                if debug:
                    print('Sending %s' % message)

        udp_server_socket.sendto(message.encode(), udp_addr)

        # close here cause next connection not to be accepted?
        # udp_server_socket.close()


def main():
    udp_thread = Thread(target=udp_connection, args=())
    # tcp_thread = Thread(target=tcp_connection, args=())

    udp_thread.start()
    # tcp_thread.start()


main()
