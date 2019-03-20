#!/usr/bin/env python3

import socket
import sys

# define host and port number
port = 9999
# host = socket.gethostbyname(socket.gethostname())
host = "127.0.0.1"

# define message protocol


# create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket successfully created")


# bind the socket with address and port number
try:
    server_socket.bind((host, port))
    print("Socket is binded to %s" % port)
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

# put the socket into listening mode
server_socket.listen(5)
print("Socket is listening")

message = ''

# keep server online
while True:
    client, addr = server_socket.accept()
    print('Got connection from', addr)

    print('Client message top = ' + message)

    if message != '':
        client.send(message.encode())
        message = ''

    message = client.recv(4096).decode('utf-8')

    print('Client message bottom = ' + message)

    client.close()
