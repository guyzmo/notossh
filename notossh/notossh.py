#!/usr/bin/env python

# Echo server program
import os
import sys
import socket
import base64
import signal
import os.path
import argparse
import tempfile
import subprocess
from data import _PNG, _ICON

# conditionally import freedesktop Notify
Notify = None
if sys.platform == 'linux2':
    from gi.repository import Notify

__author__ = 'Bernard `Guyzmo` Pratz'
__credits__ = ["Bernard `Guyzmo` Pratz", "Charles `doublerebel` Philips", "Rui Abreu Ferreira", "Cooper Ry Lees", "Kevin Mershon"]
__email__ = 'guyzmo AT m0g DOT net'
__status__ = "Production"

__NAME__ = 'irssi-notify-listener.py'
__version__ = "1.1"
__maintainer__ = "Bernard `Guyzmo` Pratz"
__description__ = 'Use libnotify over SSH to alert user for hilighted messages'
__license__ = 'WTF Public License <http://sam.zoy.org/wtfpl/>'
__url__ = 'http://github.com/guyzmo/irssi-over-ssh-notifications'
__updated__ = '''Last update: Wed Feb 20 15:43:38 CET 2013
'''

if (hasattr(os, "devnull")):
    REDIRECT_TO = os.devnull
else:
    REDIRECT_TO = "/dev/null"


def createDaemon():
    """Detach a process from the controlling terminal and run it in the
    background as a daemon.
    """
    try:
        pid = os.fork()
    except OSError, e:
        raise Exception("%s [%d]" % (e.strerror, e.errno))
    if (pid == 0):  # The first child.
        os.setsid()
        try:
            pid = os.fork()  # Fork a second child.
        except OSError, e:
            raise Exception("%s [%d]" % (e.strerror, e.errno))
        if (pid == 0):  # The second child.
            os.chdir(WORKDIR)
            os.umask(UMASK)
        else:
            os._exit(0)  # Exit parent (the first child) of the second child.
    else:
        os._exit(0)  # Exit parent of the first child.
    import resource  # Resource usage information.
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = MAXFD
    # Iterate through and close all file descriptors.
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:  # ERROR, fd wasn't open to begin with (ignored)
            pass
    # This call to open is guaranteed to return the lowest file descriptor,
    # which will be 0 (stdin), since it was closed above.
    os.open(REDIRECT_TO, os.O_RDWR)  # standard input (0)
    # Duplicate standard input to standard output and standard error.
    os.dup2(0, 1)  # standard output (1)
    os.dup2(0, 2)  # standard error (2)
    return(0)


def shutdownDaemon(signum, stack):
    """Remove the PID file and exit with return code 1"""
    os.unlink(PID_FILE)
    sys.exit(1)


# decode the icon put at begining of the script
def write_icon(file, data):
    f = open(file, "w")
    f.write(base64.b64decode(data))
    f.close()


# define the command used with growl on OSX
def notify_growl(opts, cmd_opts, args):
    args = args.split(':')

    growl_command = None
    if opts.sticky is True:
        growl_command = [opts.growl, '-s', '-n', 'Terminal', '--image', 'irssi.icns', '-m', ':'.join(args[1:]), args[0]]
    else:
        growl_command = [opts.growl, '-n', 'Terminal', '--image', 'irssi.icns', '-m', ':'.join(args[1:]), args[0]]

    return subprocess.Popen(growl_command)

# define the command used with OSX Mountain Lion
def notify_terminal(opts, cmd_opts, args):
    args = args.split(':')

    notifier_command = [opts.notifier, '-sender', 'net.m0g.notossh', '-activate', 'com.apple.Terminal', '-title', 'notossh', '-message', args[0], '-subtitle', ':'.join(args[1:])]
    return subprocess.Popen(notifier_command)


# define the command used with linux systems
def notify_dbus(opts, cmd_opts, args):
    args = args.split(':')
    n = Notify.Notification.new(':'.join(args[1:]), args[0], os.path.join(WORKDIR, 'irssi.png'))
    n.set_category("im.received")
    n.show()
    return 0


def notify_cli(opts, cmd_opts, args):
    args = args.split(':')
    return subprocess.Popen([opts.notify, '-i', os.path.join(WORKDIR, 'irssi.png'), '-t', '5000', ':'.join(args[1:]), args[0]])


def irssi_focused(titles):
    if not titles:
        return False
    title = None
    if sys.platform == 'windows':
        from win32gui import GetWindowText, GetForegroundWindow
        title = GetWindowText(GetForegroundWindow()).lower()
    elif sys.platform == "darwin":
        from AppKit import NSWorkspace
        title = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName'].lower()
    elif sys.platform == 'linux2':
        title = get_linux_active_window_title().lower()
    for t in titles:
        if t in title:
            return True
    return False


def get_linux_active_window_title():
    from subprocess import Popen, PIPE
    import re
    root = Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=PIPE)
    for line in root.stdout:
        m = re.search('^_NET_ACTIVE_WINDOW.* ([\w]+)$', line)
        if m != None:
            id_ = m.group(1)
            id_w = Popen(['xprop', '-id', id_, 'WM_NAME'], stdout=PIPE)
            break
    if id_w != None:
        for line in id_w.stdout:
            match = re.match("WM_NAME\(\w+\) = (?P<name>.+)$", line)
            if match != None:
                return match.group("name")
    return "Active window not found"


def init(args):
    # define 'notify' function depending on running platform (whether it is darwin or linux)
    if sys.platform == 'darwin':
        if args.notifier:
            if not os.path.isfile(args.notifier):
                print 'terminal-notifier not found in given path, please install terminal-notifier'
                sys.exit(1)
            notify = notify_terminal
        else:
            if not os.path.isfile(args.growl):
                print 'Please install Growl and check if growlnotify exists and is correctly set in source'
                sys.exit(1)
            notify = notify_growl
            write_icon(os.path.join(WORKDIR, "irssi.icns"), _ICON)
    elif sys.platform == 'linux2':
        if Notify:
            if args.verbose:
                print "Initializing GTK Notify API"
            Notify.init("irssi")
            notify = notify_dbus
        else:
            if not os.path.isfile(args.notify):
                print 'Please install libnotify and check if the notify command exists or give its path. See --help.'
                sys.exit(1)
            notify = notify_cli

        write_icon(os.path.join(WORKDIR, "irssi.png"), _PNG)
    return notify


def service_start(args):
    args, left_args = args
    notify = init(args)
    if os.path.isfile(PID_FILE):
        print 'Daemon is already running... Exiting.'
        sys.exit(1)

    # Shutdown if the process is killed
    signal.signal(signal.SIGTERM, shutdownDaemon)

    if not args.foreground:
        if args.verbose:
            print 'Starting server as daemon...'
        retCode = createDaemon()

        # create PID file
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
    else:
        print 'Starting server in foreground mode...'

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((args.host, args.port))
    s.listen(1)
    if args.verbose:
        print 'Listening on %s:%s...' % (str(args.host), str(args.port))

    # daemon main loop
    while True:
        conn, addr = s.accept()
        while 1:
            data = conn.recv(1024)
            if not data:
                break
            if args.verbose:
                print 'RCPT: %s' % str(data)
                print 'Calling("%s")' % notify(args, left_args, data)
            if not irssi_focused(args.windowtitle):
                notify(args, left_args, data)
        conn.close()

    sys.exit(retCode)


def service_stop(args):
    args, left_args = args
    if not os.path.isfile(PID_FILE):
        print 'nothing to stop. exiting...'
        sys.exit(1)
    try:
        os.kill(int(open(PID_FILE, 'r').read()), 9)
    except ValueError:
        print 'Invalid PID file. exiting...'
        sys.exit(1)
    except OSError:
        print 'Invalid PID: %s. Process has already exited. exiting...' % int(open(PID_FILE, 'r').read())
        os.unlink(PID_FILE)
        sys.exit(1)
    os.unlink(PID_FILE)
    print 'notify daemon killed'
    sys.exit(0)

# Daemonization
WORKDIR = tempfile.mkdtemp()
PID_FILE = "/tmp/irssi-notify-listener.pid"
MAXFD = 1024
UMASK = 766


def start(notify_func=None):
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                description="IRSSI Notify Listener",
                epilog="By %s with patches from %s" % (__author__, ', '.join(__credits__[1:])))

    sp = parser.add_subparsers()

    sp.add_parser('start', help='Starts the service').set_defaults(func=service_start)
    sp.add_parser('stop', help='Stops the service').set_defaults(func=service_stop)

    parser.add_argument("-f",
                        "--foreground",
                        dest="foreground",
                        action="store_true",
                        help='Make the notifications stick')
    parser.add_argument("-S",
                        "--sticky",
                        dest="sticky",
                        action="store_true",
                        help='Make the notifications stick')
    parser.add_argument("-V",
                        "--verbose",
                        dest="verbose",
                        action="store_true",
                        help='Make the listener verbose')
    parser.add_argument('-H', '--host',
                        dest='host',
                        action='store',
                        default='localhost',
                        help='Host to listen on')
    parser.add_argument('-P', '--port',
                        dest='port',
                        action='store',
                        default=4222,
                        type=int,
                        help='Port to listen on')
    parser.add_argument('-G', '--with-growl',
                        dest='growl',
                        action='store',
                        default='/usr/local/bin/growlnotify',
                        help='Path to growl executable')
    parser.add_argument('-N', '--with-notify',
                        dest='notify',
                        action='store',
                        default='/usr/bin/notify-send',
                        help='Path to notify executable'),
    parser.add_argument('-T', '--with-terminal-notifier',
                        dest='notifier',
                        action='store',
                        help='Path to terminal-notifier executable')

    parser.add_argument('-W', '--window-title',
                        dest='windowtitle',
                        action='append',
                        default=[],
                        help='Do not send notify if this window title is in foreground, specify multiple times to look for multiple titles')

    args = parser.parse_known_args()
    args[0].func(args)

if __name__ == '__main__':
    start()
