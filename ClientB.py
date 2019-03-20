#!/usr/bin/env python3

# Import socket module
import socket

# define protocol message
hello = "HELLO (Client-ID-B)"
response = "RESPONSE ()"
connect = ""
chat_request = ""
chat_started = ""
end_request = ""
chat = ""
history_req = ""

# Define the port on which you want to connect
# host = socket.gethostbyname('localhost')
host = "127.0.0.1"
port = 9999

new_connection = True
receivingMessage = ''
sendingMessage = ''

while True:

    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to the server on local computer
    s.connect((host, port))

    print('new_connection = ' + new_connection.__str__())

    if not new_connection:
        receivingMessage = s.recv(1024).decode('utf-8')
        print('Server: ' + receivingMessage)

    new_connection = False

    sendingMessage = input('You: ')
    s.send(sendingMessage.encode())

    # close the connection
    s.close()

    if sendingMessage == 'bye':
        break



