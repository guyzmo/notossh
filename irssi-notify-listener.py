# Echo server program
import socket
import shlex, subprocess
import os

NOTIFIER_GROWL = '/usr/local/bin/growlnotify'
NOTIFIER_DBUS  = '/usr/bin/notify'
HOST = 'localhost'
PORT = 4222

def notify_growl(args):
    args = args.split(':')
    return [NOTIFIER_GROWL, '-s', '-n', 'Terminal', '--image', 'irssi.icns', '-m', ':'.join(args[1:]), args[0]]

def notify_dbus(args):
    args = args.split(':')
    return [NOTIFIER_DBUS, '-i', 'gtk-dialog-info', '-t', '5000', ':'.join(args[1:]), args[0]]

if os.uname()[0] == 'Darwin':
    notify = notify_growl
elif os.uname()[0] == 'Linux':
    notify = notify_dbus

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
while True:
    conn, addr = s.accept()
    #print 'Connected by', addr
    while 1:
        data = conn.recv(1024)
        if not data: break
        #conn.send(data)
        p = subprocess.Popen(notify(data))
    conn.close()

