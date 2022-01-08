import socket
import time
from threading import Thread

"""
this script runs separately to access the main process and run commands on it
"""

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connected = False
for i in range(1000, 99999):
    try:
        sock.connect(('192.168.1.140', i))
        connected = True
        break
    except:
        pass

if not connected:
    raise 'could not connect to the local server'

def send_commands():
    connected = False
    time.sleep(1)
    data = sock.recv(4096)
    if data:
        print("response: " + str(data.decode('utf-8')))
        connected = True
    if not connected:
        return
    while True:
        try:
            sock.send(str.encode(str(input('> '))))
            data = sock.recv(4096).decode('utf-8')
            print("response: " + str(data))
        except ConnectionError:
            print('a connection error occurred - probably the main process stopped working')
            break



Thread(target=send_commands, args=()).start()
