import socket
import sys
import time
import utility
import hashlib
import msvcrt
import timeout


# Define the port on which you want to connect
host = "127.0.0.1"
udp_port = 7777
tcp_port = 0
debug = False
client_id = 'Client-ID-%s' % sys.argv[1]
keyboard_input = ''
default_keyboard_input_value = '33987748-6484-4a22-82f8-6bfb5838feba'


client_instances = {
    'Client-ID-A': {
        'LongTermKey': 'aaa',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': ''
    },
    'Client-ID-B': {
        'LongTermKey': 'bbb',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': ''
    },
    'Client-ID-C': {
        'LongTermKey': 'ccc',
        'AuthenticationKey': '',
        'SessionID': '',
        'Cookie': ''
    },
    'Client-ID-D': {
        'LongTermKey': 'ddd',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': ''
    },
    'Client-ID-E': {
        'LongTermKey': 'eee',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': ''
    },
    'Client-ID-F': {
        'LongTermKey': 'fff',
        'AuthenticationKey': '',
        'SessionID': '',
        'Cookie': ''
    },
    'Client-ID-G': {
        'LongTermKey': 'ggg',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': ''
    },
    'Client-ID-H': {
        'LongTermKey': 'hhh',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': ''
    },
    'Client-ID-I': {
        'LongTermKey': 'iii',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': ''
    },
    'Client-ID-J': {
        'LongTermKey': 'jjj',
        'AuthenticationKey': '',
        'EncryptionKey': '',
        'SessionID': '',
        'Cookie': ''
    }
}


def keyboard_listener():
    print(client_id + ': ', end='')
    sys.stdout.flush()
    time_started = time.time()
    global keyboard_input
    keyboard_input = ''

    while True:
        if time.time() > time_started + timeout.keyboard_wait_timeout:
            if debug:
                print('Timeout')
            else:
                print('\r', end='')
            keyboard_input = default_keyboard_input_value
            return

        if msvcrt.kbhit():
            break

    # print(client_id + ': ', end='')
    while True:
        c = msvcrt.getche()
        ordinal = ord(c)

        # enter
        if ordinal == 13:
            keyboard_input = keyboard_input.replace('\r', '')
            print(client_id + ': ')
            sys.stdout.flush()
            return
        elif ordinal == 8 or ordinal == 127:
            keyboard_input = keyboard_input[:-1]
        elif 32 <= ordinal <= 126:
            keyboard_input += c.decode('utf-8')
        else:
            pass


def authenticate():
    new_connection = True

    message = input(client_id + ': ')
    if message != 'Log on':
        sys.exit(-1)

    # Authentication
    while True:
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
                rand = utility.get_substring_between_parentheses(message)
                response = hashlib.sha1(client_instances[client_id]['LongTermKey'].encode('utf-8') +
                                        rand.encode()).hexdigest()
                client_instances[client_id]['AuthenticationKey'] = response

                session_key = hashlib.sha512(client_instances[client_id]['LongTermKey'].encode('utf-8') +
                                             rand.encode()).hexdigest()
                client_instances[client_id]['EncryptionKey'] = session_key

                message = 'RESPONSE(%s,%s)' % (client_id, response)

            elif message.startswith('AUTH_SUCCESS'):
                cookie, port = utility.get_substring_between_parentheses(message).split(',')
                global tcp_port
                tcp_port = int(port)
                client_instances[client_id]['Cookie'] = cookie
                message = 'CONNECT(%s)' % cookie

            elif message.startswith('AUTH_FAIL'):
                print('Server: Fail to authenticate :( meow')
                udp_socket.close()
                client_instances[client_id]['AuthenticationKey'] = ''
                client_instances[client_id]['EncryptionKey'] = ''
                client_instances[client_id]['SessionID'] = ''
                client_instances[client_id]['Cookie'] = ''
                sys.exit(-1)

            elif message.startswith('CONNECTED'):
                print('You are now connected :)')
                udp_socket.close()
                break

            if debug:
                print('Sending %s to %s' % (message, udp_addr))

            udp_socket.sendto(message.encode(), udp_addr)
            udp_socket.close()


def chat():
    refresh_timeout = timeout.default_refresh_timeout
    last_activity_time = time.time()
    end_session = False
    is_session_expired = False

    tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_client_socket.settimeout(2)  # wait to receive data from server
    tcp_client_socket.connect((host, tcp_port))

    print("TCP Socket successfully created")

    while True:
        # messages from server
        try:
            message = tcp_client_socket.recv(4096)
            tcp_client_socket.close()

            if message is None:
                continue

            message = message.decode()
            if debug:
                print('Server: %s' % message)

            messages = message.split('<;>')

            for msg in messages:
                if msg.startswith('CHAT_START'):
                    data = utility.get_substring_between_parentheses(msg)
                    client_instances[client_id]['SessionID'] = data.split(',')[0]

                    if debug:
                        print('%s SessionID = %s' % (client_id, client_instances[client_id]['SessionID']))

                    print('Chat started' + ' ' * 10)

                elif message.startswith('UNREACHABLE'):
                    print('Correspondent is unreachable')

                elif msg.startswith('END_NOTIF'):
                    client_instances[client_id]['SessionID'] = ''
                    client_instances[client_id]['Cookie'] = ''
                    print('Chat ended' + ' ' * 10)

                elif msg.startswith('CHAT'):
                    data = utility.get_substring_between_parentheses(msg).split(',')
                    print('%s: %s' % (data[0], data[2]))

                elif msg.startswith('NO_DATA'):
                    if debug:
                        print('No message from server')
                    else:
                        print('\r', end='')

                elif msg.startswith('HISTORY_RESP'):
                    data = utility.get_substring_between_parentheses(msg).split(',')
                    session = data[0]
                    sender = data[1]
                    past_message = data[2]
                    print('Session: {:10}Sender: {:20}Message: {}'.format(session, sender, past_message))

        except socket.timeout:
            if debug:
                print('No message from server. Timeout.')

        # user input to send
        keyboard_listener()
        sys.stdout.flush()

        if keyboard_input == default_keyboard_input_value:
            raw_input = 'Ping'
        else:
            raw_input = keyboard_input
            last_activity_time = time.time()

        if time.time() - last_activity_time > timeout.inactivity_timeout:
            raw_input = 'Log off'
            is_session_expired = True

        # reset refresh_timeout as needed
        if refresh_timeout == timeout.history_refresh_timeout and raw_input != 'Ping':
            refresh_timeout = timeout.default_refresh_timeout

        if raw_input.startswith('Chat ') and raw_input != 'Chat end':
            chat_client = raw_input.split(' ')[1]
            if chat_client == client_id:
                print('Error: trying to chat to yourself')
                message = ''
            else:
                message = 'CHAT_REQUEST(%s,%s)' % (client_id, chat_client)

        elif raw_input == 'End chat':
            message = 'END_REQUEST(%s,%s)' % (client_id, client_instances[client_id]['SessionID'])
            client_instances[client_id]['SessionID'] = ''
            client_instances[client_id]['AuthenticationKey'] = ''
            client_instances[client_id]['Cookie'] = ''
            print('Chat ended' + ' ' * (len(client_id) - len('Chat ended') + 1))

        elif raw_input == 'Log off':
            message = 'LOG_OFF(%s,%s)' % (client_id, client_instances[client_id]['Cookie'])
            client_instances[client_id]['AuthenticationKey'] = ''
            client_instances[client_id]['EncryptionKey'] = ''
            client_instances[client_id]['SessionID'] = ''
            client_instances[client_id]['Cookie'] = ''

            if is_session_expired:
                print('Log off due to long inactivity time')

            end_session = True

        elif raw_input.startswith('History'):
            chat_client = raw_input.split(' ')[1]
            message = 'HISTORY_REQ(%s,%s)' % (client_id, chat_client)
            refresh_timeout = timeout.history_refresh_timeout

        elif raw_input == 'Ping':
            message = 'PING(%s)' % client_id

        else:
            if client_instances[client_id]['SessionID'] == '':
                message = 'PING(%s)' % client_id
                print('Unknown command. Not connected to chat session yet.')
            else:
                message = 'CHAT(%s,%s,%s)' % (client_id, client_instances[client_id]['SessionID'], raw_input)

        if debug:
            print('Sending %s' % message)

        try:
            tcp_client_socket.send(message.encode('utf-8'))
        except OSError:
            if debug and not end_session:
                print('Catch OSError, try to connect TCP socket again')

            tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_client_socket.settimeout(2)  # wait to receive data from server
            tcp_client_socket.connect((host, tcp_port))
            tcp_client_socket.send(message.encode('utf-8'))

        if end_session:
            tcp_client_socket.close()
            return


def main():
    authenticate()
    chat()


main()
