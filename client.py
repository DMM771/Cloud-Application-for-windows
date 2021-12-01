import os
import socket
import sys
import util
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler




if __name__ == "__main__":
    #print(sys.argv[5])
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

#     logging.basicConfig(level=logging.INFO,
#                         format='%(asctime)s - %(message)s',
#                         datefmt='%Y-%m-%d %H:%M:%S')
#
#     path = sys.argv[1] if len(sys.argv) > 1 else '.'
#     event_handler = LoggingEventHandler()
#     observer = Observer()
#     observer.schedule(event_handler, path, recursive=True)
#     observer.start()
#
#     try:
#         while True:
#             time.sleep(1)
#     finally:
#         observer.stop()
#         observer.join()
#
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect(('10.0.0.11', 12345))
# s.close()
