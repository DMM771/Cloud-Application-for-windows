import os


def delete(path):
    if os.path.isdir(path):
        for path, dirs, files in os.walk(path, topdown=False):
            for file in files:
                os.remove(os.path.join(path, file))
            for dir in dirs:
                os.rmdir(os.path.join(path, dir))
        os.rmdir(path)
    else:
        os.remove(path)


def getFolder(sock, dir):
    size = sock.recv(4)
    info = sock.recv(int.from_bytes(size, 'big'))
    while info:
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


def sendFolder(sock, dir):
    for path, dirs, files in os.walk(dir):
        for di in dirs:
            pathD = os.path.join(path, di)
            relPath = os.path.relpath(pathD, dir)
            sock.send((3).to_bytes(4, 'big'))
            sock.send(b'dir')
            sock.send(len(relPath).to_bytes(4, 'big'))
            sock.send(relPath.encode())

        for file in files:
            fileName = os.path.join(path, file)
            relPath = os.path.relpath(fileName, dir)
            fileSize = os.path.getsize(fileName)
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
