# TODO
# authentication before get connected
# hello is sent using UDP
# how does server keeps IP address and port number of clients?
# send according to the Client name

# Import socket module
import socket
import sys

client_id = sys.argv[0]

# define protocol message
hello = "HELLO Client-ID-" + client_id
response = "RESPONSE "
connect = "CONNECT "
chat_request = "CHAT_REQUEST "
end_request = "END_REQUEST "
chat = "CHAT "
history_req = "HISTORY_REQ "

# Define the port on which you want to connect
# host = socket.gethostbyname('localhost')
host = "127.0.0.1"
port = 9999

new_connection = True
is_in_chat_session = False
receivingMessage = ''
raw_sendingMessage = ''

# User wants to log on
# sendingMessage = input("Client A: ")
# if sendingMessage == "Log on":
#     # UDP transport
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
#     # send hello
#     sock.sendto(bytes(hello, "utf-8"), (host, port))
#
#     #
#

sendingMessage = ''

# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the server on local computer
s.connect((host, port))

# store session ID
sessionID = 0

# Authentication

# Keep connection
while True:

    # create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to the server on local computer
    s.connect((host, port))

    print('new_connection = ' + new_connection.__str__())

    if not new_connection:
        receivingMessage = s.recv(1024).decode('utf-8')
        print('Server: ' + receivingMessage)

    new_connection = False

    raw_sendingMessage = input('Client-A: ')

    # user enters
    command = (raw_sendingMessage.split())[0]
    if command == "Chat":
        sendingMessage = chat_request + command[1]
    elif raw_sendingMessage == "End chat":
        # send end_request
        sendingMessage = end_request + str(sessionID)
    elif raw_sendingMessage == "Log off":
        break
    else:  # in a chat session
        if is_in_chat_session:
            sendingMessage = raw_sendingMessage
        else:
            print("Command not recognizable")

    s.send(sendingMessage.encode())

    # close the connection
    s.close()

