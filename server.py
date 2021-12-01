import os
import socket
import random
import string
import sys

import util


def created(numFolder, client_socket):
    size = client_socket.recv(4)
    type = client_socket.recv(int.from_bytes(size))
    if type == b'directory':
        size = client_socket.recv(4)
        dir_name = client_socket.recv(int.from_bytes(size))
        path = os.path.join(sys.argv[0], numFolder)
        os.mkdir(os.path.join(path, dir_name))
        print("copied folder")
    else:
        size = client_socket.recv(4)
        file_name = client_socket.recv(int.from_bytes(size))
        path = os.path.join(sys.argv[0], numFolder)
        file_size = client_socket.recv(4)
        f = open(os.path.join(path, file_name), 'wb')
        while file_size > 0:
            info = client_socket.recv(min(1000000, size))
            f.write(info)
            size -= len(info)
        f.close()






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
        elif data == b'new':
            id = ''.join(random.choices(string.ascii_letters + string.digits, k=128))
            numClient += 1
            dic[id] = numClient
            client_socket.send(bytes(id, encoding='utf8'))
            print('send id:', id)
            dirName = os.path.join(os.getcwd(), str(dic[id]))
            os.mkdir(dirName)
            print(dirName)
            util.getFolder(client_socket, dirName)
        elif data == b'upd':
            numFolder = client_socket.recv(128)
            size = client_socket.recv(4)
            upd_type = client_socket.recv(int.from_bytes(size))
            if upd_type == b'created':
                created(numFolder, client_socket)

        client_socket.close()
