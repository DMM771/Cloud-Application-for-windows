import os
import socket
import random
import string
import sys

import util

if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', int(sys.argv[1])))
    server.listen(5)
    numClient = 0
    dic = {}
    while True:
        client_socket, client_address = server.accept()
        print('connect')
        data = client_socket.recv(3)
        if data == b'old':
            data = client_socket.recv(128)
            numFolder = dic[data.decode()]
            print(numFolder)
            util.sendFolder(client_socket, os.path.join(os.getcwd(), str(numFolder)))
        else:
            id = ''.join(random.choices(string.ascii_letters + string.digits, k=128))
            numClient += 1
            dic[id] = numClient
            client_socket.send(bytes(id, encoding='utf8'))
            print('send id:', id)
            dirName = os.path.join(os.getcwd(), str(dic[id]))
            os.mkdir(dirName)
            print(dirName)
            util.getFolder(client_socket, dirName)
        client_socket.close()
