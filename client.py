import os
import socket
import sys
import util
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

myId = b''


def on_created(event):
    print("a file has been created")
    print('the change happened in ' + event.src_path)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((sys.argv[1], int(sys.argv[2])))
    sock.send(b'upd')
    sock.send(myId)
    sock.send(len('created').to_bytes(4, 'big'))
    sock.send('created'.encode())
    updated_path = os.path.relpath(event.src_path,sys.argv[3])
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
    print("a file has been deleted")


def on_modified(event):
    print("i detect a modification, dont do anything")


def on_moved(event):
    print("a file has been moved")


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((sys.argv[1], int(sys.argv[2])))
    if len(sys.argv) == 6:
        print("here")
        myId = sys.argv[5]
        s.send(b'old')
        s.send(myId.encode())
        util.getFolder(s, sys.argv[3])
    # get my id
    else:
        s.send(b'new')
        myId = s.recv(128)
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
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
