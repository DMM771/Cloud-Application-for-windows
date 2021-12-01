import os
import sys

def getFolder(sock, dir):
    print("in getFolder")
    size = sock.recv(4)
    info = sock.recv(int.from_bytes(size, 'big'))
    while info:
        print("in info")
        if info != b'file':
            size = sock.recv(4)
            info = sock.recv(int.from_bytes(size, 'big'))
            info = info.strip().decode()
            path = os.path.join(dir, info)
            os.mkdir(path)
            size = sock.recv(4)
            info = sock.recv(int.from_bytes(size, 'big'))
            continue
        size = sock.recv(4)
        info = sock.recv(int.from_bytes(size, 'big'))
        info = info.strip().decode()
        path = os.path.join(dir, info)
        print(path)
        f = open(path, 'wb')
        size = sock.recv(4)
        size = int.from_bytes(size, 'big')
        while size > 0:
            info = sock.recv(min(1000000, size))
            f.write(info)
            size -= len(info)
        f.close()
        size = sock.recv(4)
        info = sock.recv(int.from_bytes(size, 'big'))

def sendFolder(sock,dir):
    for path, dirs, files in os.walk(dir):
        for di in dirs:
            pathD=os.path.join(path,di)
            relPath = os.path.relpath(pathD, dir)
            print(f'Sending {relPath}')
            sock.send((3).to_bytes(4, 'big'))
            sock.send(b'dir')
            sock.send(len(relPath).to_bytes(4, 'big'))
            sock.send(relPath.encode())

        for file in files:
            print("got here")
            fileName = os.path.join(path, file)
            relPath = os.path.relpath(fileName, dir)
            fileSize = os.path.getsize(fileName)
            print(fileSize)
            print(f'Sending {relPath}')
            sock.send((4).to_bytes(4, 'big'))
            sock.send(b'file')
            sock.send(len(relPath).to_bytes(4, 'big'))
            sock.send(relPath.encode())
            sock.send(fileSize.to_bytes(4, 'big'))
            f = open(fileName, 'rb')
            # Send the file in chunks so large files can be handled.
            while True:
                data = f.read(1_000_000)
                if not data:
                    break
                sock.send(data)
            f.close()