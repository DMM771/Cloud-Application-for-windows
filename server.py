import os
import socket
import random
import string
import sys
import util


def addEvent(type, src, dst, sub_dict, num_sub):
    event = type + '###' + src
    if dst != '':
        event = event + '###' + dst
    for key in sub_dict.keys():
        if key == num_sub:
            continue
        sub_dict[key].append(event)


def created(numFolder, client_socket, dict):
    subid = client_socket.recv(4)
    size = client_socket.recv(4)
    type = client_socket.recv(int.from_bytes(size, 'big'))
    name = ''
    if type == b'directory':
        size = client_socket.recv(4)
        name = client_socket.recv(int.from_bytes(size, 'big'))
        path = os.path.join(os.getcwd(), str(numFolder))
        print(os.path.join(path, name.decode()))
        if not os.path.isdir(os.path.join(path, name.decode())):
            os.makedirs(os.path.join(path, name.decode()))
            print("copied folder")
    else:
        size = client_socket.recv(4)
        name = client_socket.recv(int.from_bytes(size, 'big'))
        path = os.path.join(os.getcwd(), str(numFolder))
        file_size = client_socket.recv(4)
        f = open(os.path.join(path, name.decode()), 'wb')
        file_size = int.from_bytes(file_size, 'big')
        while file_size > 0:
            info = client_socket.recv(min(1000000, file_size))
            f.write(info)
            file_size -= len(info)
        f.close()
    addEvent('created', name.decode(), '', dict, subid)


def deleted(num_folder, client_socket, dict):
    subid = client_socket.recv(4)
    size = client_socket.recv(4)
    name = client_socket.recv(int.from_bytes(size, 'big'))
    src_path = os.path.join(os.getcwd(), str(num_folder))
    util.delete(os.path.join(src_path, name.decode()))
    addEvent('deleted', name.decode(), '', dict, subid)


def moved(num_folder, client_socket, dict):
    subid = client_socket.recv(4)
    size = client_socket.recv(4)
    src_name = client_socket.recv(int.from_bytes(size, 'big'))
    src_path = os.path.join(os.getcwd(), str(num_folder))
    dst_path = src_path
    src_path = os.path.join(src_path, src_name.decode())
    size = client_socket.recv(4)
    dst_name = client_socket.recv(int.from_bytes(size, 'big'))
    dst_path = os.path.join(dst_path, dst_name.decode())
    if os.path.isdir(src_path):
        os.renames(src_path, dst_path)
    addEvent('moved', src_name.decode(), dst_name.decode(), dict, subid)


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', int(sys.argv[1])))
    server.listen(5)
    id_list = {}
    id_to_num = {}
    num_client = 0
    while True:
        print('wait')
        client_socket, client_address = server.accept()
        print('connect')
        data = client_socket.recv(3)
        if data == b'old':
            data = client_socket.recv(128)
            numFolder = id_to_num[data.decode()]
            print(numFolder)
            id_list[data.decode()][len(id_list[data.decode()]) + 1] = []
            client_socket.send((len(id_list[data.decode()])).to_bytes(4, 'big'))
            util.sendFolder(client_socket, os.path.join(os.getcwd(), str(numFolder)))
        elif data == b'new':
            id = ''.join(random.choices(string.ascii_letters + string.digits, k=128))
            id_list[id] = {}
            id_to_num[id] = num_client
            num_client += 1
            id_list[id][1] = []
            client_socket.send(id.encode())
            print('send id:', id)
            client_socket.send((1).to_bytes(4, 'big'))
            dirName = os.path.join(os.getcwd(), str(id_to_num[id]))
            os.mkdir(dirName)
            print(dirName)
            util.getFolder(client_socket, dirName)
        elif data == b'upd':
            data = client_socket.recv(128)
            numFolder = id_to_num[data.decode()]
            size = client_socket.recv(4)
            upd_type = client_socket.recv(int.from_bytes(size, 'big'))
            if upd_type == b'created':
                created(numFolder, client_socket, id_list[data.decode()])
            elif upd_type == b'renamed':
                moved(numFolder, client_socket, id_list[data.decode()])
            elif upd_type == b'deleted':
                deleted(numFolder, client_socket, id_list[data.decode()])
        client_socket.close()
