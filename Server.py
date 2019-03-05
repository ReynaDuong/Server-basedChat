import socket
import sys

port = 9999
# host = socket.gethostbyname(socket.gethostname())
host = "127.0.0.1"

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket successfully created")


# bind the socket with address and port number
try:
    s.bind((host, port))
    print("Socket is binded to %s" % port)
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

# put the socket into listening mode
s.listen(5)
print("Socket is listening")


# a forever loop until we interrupt it or an error occurs
while True:
    # Establish connection with client.
    c, addr = s.accept()
    print('Got connection from', addr)

    # send a thank you message to the client.
    message = "Thank you for connecting"
    c.send(message.encode())

    # Close the connection with the client
    c.close()


