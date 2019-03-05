# Import socket module
import socket

# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the port on which you want to connect
# host = socket.gethostbyname('localhost')
host = "127.0.0.1"
port = 9999

# connect to the server on local computer
s.connect((host, port))

# receive data from the server
print(s.recv(1024))

# close the connection
s.close()


