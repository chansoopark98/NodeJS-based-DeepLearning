from ast import While
import base64

from PIL import Image
import os, sys
import socket 

clientPort = 5000
clientSocket = socket.socket()
clientSocket.connect(('127.0.0.1', clientPort))

serverPort = 10000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('127.0.0.1', 10000))
serverSocket.listen(5)


while True:
    clientSocket.send('test'.encode("utf-8"))
# s.close()