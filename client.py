import os
import socket
import sys
import util
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

myId = b''
mySubId = b''
flag = False
updates = []


def is_upt(event):
    event_str = event.event_type + event.src_path
    global updates
    if event_str in updates:
        return True
    return False


def on_created(event):
    if is_upt(event):
        return
    print("a file has been created")
    print('the change happened in ' + event.src_path)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((sys.argv[1], int(sys.argv[2])))
    sock.send(b'upd')
    sock.send(myId)
    sock.send(len('created').to_bytes(4, 'big'))
    sock.send('created'.encode())
    sock.send(mySubId)
    updated_path = os.path.relpath(event.src_path, sys.argv[3])
    print(updated_path)
    if event.is_directory:
        sock.send(len('directory').to_bytes(4, 'big'))
        sock.send('directory'.encode())
        sock.send(len(updated_path).to_bytes(4, 'big'))
        sock.send(updated_path.encode())
    else:
        sock.send(len('file').to_bytes(4, 'big'))
        sock.send('file'.encode())
        sock.send(len(updated_path).to_bytes(4, 'big'))
        sock.send(updated_path.encode())
        file_size = os.path.getsize(event.src_path)
        sock.send(file_size.to_bytes(4, 'big'))
        f = open(event.src_path, 'rb')
        # Send the file in chunks so large files can be handled.
        while True:
            data = f.read(1_000_000)
            if not data:
                break
            sock.send(data)
        f.close()


def on_deleted(event):
    if is_upt(event):
        return
    print("a file has been deleted")
    print('the change happened in ' + event.src_path)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((sys.argv[1], int(sys.argv[2])))
    sock.send(b'upd')
    sock.send(myId)
    sock.send(len('deleted').to_bytes(4, 'big'))
    sock.send('deleted'.encode())
    sock.send(mySubId)
    updated_path = os.path.relpath(event.src_path, sys.argv[3])
    print(updated_path)
    sock.send(len(updated_path).to_bytes(4, 'big'))
    sock.send(updated_path.encode())


def on_modified(event):
    if not event.is_directory:
        on_created(event)
    elif not os.path.isdir(event.src_path):
        print("lest call delete")
        on_deleted(event)

    else:
        print("dir, do nothing")


def on_moved(event):
    if is_upt(event):
        return
    if event.is_directory:
        print("a dir has been renamed")
        print('the change happened in ' + event.src_path)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((sys.argv[1], int(sys.argv[2])))
        sock.send(b'upd')
        sock.send(myId)
        sock.send(len('renamed').to_bytes(4, 'big'))
        sock.send('renamed'.encode())
        sock.send(mySubId)
        updated_path = os.path.relpath(event.src_path, sys.argv[3])
        print(updated_path)
        sock.send(len(updated_path).to_bytes(4, 'big'))
        sock.send(updated_path.encode())
        updated_path = os.path.relpath(event.dest_path, sys.argv[3])
        print(updated_path)
        sock.send(len(updated_path).to_bytes(4, 'big'))
        sock.send(updated_path.encode())
    else:
        print("rename dir file dont change")


def receive_update():
    global flag
    flag = True
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((sys.argv[1], int(sys.argv[2])))
    soc.send(b'get')
    soc.send(myId)
    soc.send(mySubId)
    events_amount = int.from_bytes(soc.recv(4), 'big')
    for i in range(0, events_amount):
        event_type = soc.recv(4).decode()
        if event_type == 'move':
            size = int.from_bytes(soc.recv(4), 'big')
            src = os.path.join(sys.argv[3], soc.recv(size).decode())
            size = int.from_bytes(soc.recv(4), 'big')
            dst = os.path.join(sys.argv[3], soc.recv(size).decode())
            global updates
            updates.append('moved' + src)
            if os.path.isdir(src):
                os.renames(src, dst)

        elif event_type == 'crea':
            size = int.from_bytes(soc.recv(4), 'big')
            crea_type = soc.recv(size).decode()
            size = int.from_bytes(soc.recv(4), 'big')
            src = os.path.join(sys.argv[3], soc.recv(size).decode())
            global updates
            updates.append('created' + src)
            if crea_type == 'dir':
                os.mkdir(src)
            else:
                size = int.from_bytes(soc.recv(4), 'big')
                f = open(src, 'wb')
                while size > 0:
                    info = soc.recv(min(1000000, size))
                    f.write(info)
                    size -= len(info)
                f.close()

        elif event_type == 'dele':
            size = int.from_bytes(soc.recv(4), 'big')
            src = os.path.join(sys.argv[3], soc.recv(size).decode())
            global updates
            updates.append('deleted' + src)
            util.delete(src)
    flag = False


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((sys.argv[1], int(sys.argv[2])))
    if len(sys.argv) == 6:
        print("here")
        myId = sys.argv[5].encode()
        s.send(b'old')
        s.send(myId)
        mySubId = s.recv(4)
        util.getFolder(s, sys.argv[3])
    # get my id
    else:
        s.send(b'new')
        myId = s.recv(128)
        mySubId = s.recv(4)
        util.sendFolder(s, sys.argv[3])
    s.close()

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    path = sys.argv[3]
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    event_handler.on_created = on_created
    event_handler.on_modified = on_modified
    event_handler.on_deleted = on_deleted
    event_handler.on_moved = on_moved
    observer.start()

    try:
        while True:
            time.sleep(int(sys.argv[4]))
            receive_update()

    finally:
        observer.stop()
        observer.join()
