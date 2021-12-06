import os
import socket
import random
import string
import sys
import util


def created(numFolder, client_socket):
    size = client_socket.recv(4)
    type = client_socket.recv(int.from_bytes(size, 'big'))
    if type == b'directory':
        size = client_socket.recv(4)
        dir_name = client_socket.recv(int.from_bytes(size, 'big'))
        path = os.path.join(os.getcwd(), str(numFolder))
        print(os.path.join(path, dir_name.decode()))
        if not os.path.isdir(os.path.join(path, dir_name.decode())):
            os.makedirs(os.path.join(path, dir_name.decode()))
            print("copied folder")
    else:
        size = client_socket.recv(4)
        file_name = client_socket.recv(int.from_bytes(size, 'big'))
        path = os.path.join(os.getcwd(), str(numFolder))
        file_size = client_socket.recv(4)
        f = open(os.path.join(path, file_name.decode()), 'wb')
        file_size = int.from_bytes(file_size, 'big')
        while file_size > 0:
            info = client_socket.recv(min(1000000, file_size))
            f.write(info)
            file_size -= len(info)
        f.close()


def deleted(num_folder, client_socket):
    size = client_socket.recv(4)
    dir_name = client_socket.recv(int.from_bytes(size, 'big'))
    src_path = os.path.join(os.getcwd(), str(num_folder))
    util.delete(os.path.join(src_path,dir_name.decode()))


def moved(num_folder, client_socket):
    size = client_socket.recv(4)
    dir_name = client_socket.recv(int.from_bytes(size, 'big'))
    src_path = os.path.join(os.getcwd(), str(num_folder))
    dst_path = src_path
    src_path = os.path.join(src_path, dir_name.decode())
    size = client_socket.recv(4)
    dir_name = client_socket.recv(int.from_bytes(size, 'big'))
    dst_path = os.path.join(dst_path, dir_name.decode())
    if os.path.isdir(src_path):
        os.renames(src_path, dst_path)


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
            data = client_socket.recv(128)
            numFolder = dic[data.decode()]
            size = client_socket.recv(4)
            upd_type = client_socket.recv(int.from_bytes(size, 'big'))
            if upd_type == b'created':
                created(numFolder, client_socket)
            elif upd_type == b'renamed':
                moved(numFolder, client_socket)
            elif upd_type == b'deleted':
                deleted(numFolder, client_socket)
        client_socket.close()
