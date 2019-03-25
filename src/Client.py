import socket
import sys
import time
import util
import hashlib
import msvcrt


# Define the port on which you want to connect
host = "127.0.0.1"
udp_port = 7777
tcp_port = 0
debug = False
client_id = 'Client-ID-%s' % sys.argv[1]
keyboard_input = ''
refresh_timeout = 10    # seconds

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


def keyboard_listener():
    print(client_id + ': ', end='')
    sys.stdout.flush()
    time_started = time.time()
    global keyboard_input
    keyboard_input = ''
    # keyboard_input = 'Ping'
    # time.sleep(timeout)

    while True:
        if time.time() > time_started + refresh_timeout:
            print('Time out.')
            keyboard_input = 'Ping'
            return

        if msvcrt.kbhit():
            break

    # print(client_id + ': ', end='')
    while True:
        c = msvcrt.getche()
        ordinal = ord(c)

        # enter
        if ordinal == 13:
            return
        elif ordinal == 8:
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
                rand = util.get_substring_between_parentheses(message)
                response = hashlib.sha1(client_instances[client_id]['LongTermKey'].encode('utf-8') +
                                        rand.encode()).hexdigest()
                message = 'RESPONSE(%s,%s)' % (client_id, response)

            elif message.startswith('AUTH_SUCCESS'):
                cookie, port = util.get_substring_between_parentheses(message).split(',')
                global tcp_port
                tcp_port = int(port)
                client_instances[client_id]['Cookie'] = cookie
                message = 'CONNECT(%s)' % cookie

            elif message.startswith('AUTH_FAIL'):
                print('Server: Fail to authenticate :( meow')
                udp_socket.close()
                break

            elif message.startswith('CONNECTED'):
                print('You are now connected :)')
                udp_socket.close()
                break

            if debug:
                print('Sending %s to %s' % (message, udp_addr))

            udp_socket.sendto(message.encode(), udp_addr)
            udp_socket.close()


def chat():
    print('connected now on chat session')
    end_session = False

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

            if message.startswith('CHAT_START'):
                data = util.get_substring_between_parentheses(message)
                client_instances[client_id]['SessionID'] = data.split(',')[0]

                if debug:
                    print('%s SessionID = %s' % (client_id, client_instances[client_id]['SessionID']))

                print('Chat started')

            elif message.startswith('UNREACHABLE'):
                print('Correspondent is unreachable')

            elif message.startswith('END_NOTIF'):
                client_instances[client_id]['SessionID'] = ''
                client_instances[client_id]['SessionKey'] = ''
                client_instances[client_id]['Cookie'] = ''
                print('Chat ended')

            elif message.startswith('CHAT'):
                data = util.get_substring_between_parentheses(message).split(',')[2]
                print('Server: %s' % data)

            elif message.startswith('NO_DATA'):
                print('No message from server')

        except socket.timeout:
            if debug:
                print('No message from server. Timeout.')

        # user input to send
        keyboard_listener()
        raw_input = keyboard_input

        if raw_input.startswith('Chat ') and raw_input != 'Chat end':
            chat_client = raw_input.split(' ')[1]
            message = 'CHAT_REQUEST(%s,%s)' % (client_id, chat_client)

        elif raw_input == 'End chat':
            message = 'END_REQUEST(%s,%s)' % (client_id, client_instances[client_id]['SessionID'])
            client_instances[client_id]['SessionID'] = ''
            client_instances[client_id]['SessionKey'] = ''
            client_instances[client_id]['Cookie'] = ''
            print('Chat ended')

        elif raw_input == 'Log off':
            message = 'LOG_OFF(%s,%s)' % (client_id, client_instances[client_id]['Cookie'])
            end_session = True

        elif raw_input == 'Ping':
            message = 'PING(%s)' % client_id

        else:
            # chat message
            message = 'CHAT(%s,%s,%s)' % (client_id,client_instances[client_id]['SessionID'], raw_input)

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
