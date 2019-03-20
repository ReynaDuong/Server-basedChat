# TODO
# authentication before accepting messages

import socket
import sys

# Define host and port number
port = 9999
# host = socket.gethostbyname(socket.gethostname())
host = "127.0.0.1"

# Define message protocol
rand = 0
xres = 0
chat_session = 0
client_key = 0

challenge = "CHALLENGE %s" % rand
auth_success = "AUTH_SUCCESS "
auth_fail = "AUTH_FAIL"
connected = "CONNECTED"
chat_started = "CHAT_STARTED "
unreachable = "UNREACHABLE "
end_notif = "END-NOTIF "
history_resp = ""

# Define subscriber list
subscriber_list = {
    "Client-ID-A": "",
    "Client-ID-B": "",
    "Client-ID-C": ""
}

online_list = {
    "Client-ID-A": False,
    "Client-ID-B": False,
    "Client-ID-C": False
}

# create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket successfully created")


# bind the socket with address and port number
try:
    server_socket.bind((host, port))
    print("Socket is bind to %s" % port)
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

# put the socket into listening mode
server_socket.listen(5)
print("Socket is listening")

message = ''

# keep server online
while True:
    # accept and receive messages
    client, addr = server_socket.accept()
    print('Got connection from', addr)

    print('Client message top = ' + message)

    if message != '':
        client.send(message.encode())
        message = ''

    message = client.recv(4096).decode('utf-8')

    print('Client message bottom = ' + message)

    client.close()
