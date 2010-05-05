# Echo server program
import socket
import shlex, subprocess
import sys
import os
import os.path

__AUTHOR__      = 'Bernard `Guyzmo` Pratz'
__CONTACT__     = 'guyzmo AT m0g DOT net'

__NAME__        = 'irssi-notify-listener.py'
__VERSION__     = 0.2
__DESCRIPTION__ = 'Use libnotify over SSH to alert user for hilighted messages'
__LICENSE__     = 'WTF Public License <http://sam.zoy.org/wtfpl/>'
__URL__         = 'http://github.com/guyzmo/irssi-over-ssh-notifications'
__UPDATED__     = '''Last update: Wed May 05 15:27:48 CEST 2010
                  '''

NOTIFIER_GROWL = '/usr/local/bin/growlnotify'
NOTIFIER_DBUS  = '/usr/bin/notify'
HOST = 'localhost'
PORT = 4222

# Daemonization
PID_FILE = "/tmp/irssi-notify-listener.pid"
UMASK = 766
WORKDIR='/tmp/'
MAXFD=1024

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
      raise Exception, "%s [%d]" % (e.strerror, e.errno)
   if (pid == 0):	# The first child.
      os.setsid()
      try:
         pid = os.fork()	# Fork a second child.
      except OSError, e:
         raise Exception, "%s [%d]" % (e.strerror, e.errno)
      if (pid == 0):	# The second child.
         os.chdir(WORKDIR)
         os.umask(UMASK)
      else:
         os._exit(0)	# Exit parent (the first child) of the second child.
   else:
      os._exit(0)	# Exit parent of the first child.
   import resource		# Resource usage information.
   maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
   if (maxfd == resource.RLIM_INFINITY):
      maxfd = MAXFD
   # Iterate through and close all file descriptors.
   for fd in range(0, maxfd):
      try:
         os.close(fd)
      except OSError:	# ERROR, fd wasn't open to begin with (ignored)
         pass
   # This call to open is guaranteed to return the lowest file descriptor,
   # which will be 0 (stdin), since it was closed above.
   os.open(REDIRECT_TO, os.O_RDWR)	# standard input (0)
   # Duplicate standard input to standard output and standard error.
   os.dup2(0, 1)			# standard output (1)
   os.dup2(0, 2)			# standard error (2)
   return(0)

def notify_growl(args):
    args = args.split(':')
    return [NOTIFIER_GROWL, '-s', '-n', 'Terminal', '--image', 'irssi.icns', '-m', ':'.join(args[1:]), args[0]]

def notify_dbus(args):
    args = args.split(':')
    return [NOTIFIER_DBUS, '-i', 'gtk-dialog-info', '-t', '5000', ':'.join(args[1:]), args[0]]

# define 'notify' function
if sys.platform == 'darwin':
    if not os.path.isfile(NOTIFIER_GROWL):
        print 'Please install Growl and check if growlnotify exists and is correctly set in source'
        sys.exit(1)
    notify = notify_growl
elif sys.platform == 'linux2':
    if not os.path.isfile(NOTIFIER_DBUS):
        print 'Please install libnotify and check if the notify command exists and is correctly set in source'
        sys.exit(1)
    notify = notify_dbus

if __name__ == '__main__':

    ### check arguments

    # check for help
    if len(sys.argv) == 2 and sys.argv[1] in ('-h', '--help') or len(sys.argv) > 2 :
        print '''Usage: %s [-s|-f|-h]
Usage: %s [--stop|--foreground|--help]

Running with no argument or one wrong argument, will still launch the daemon.
Only one argument is expected. More will give you that help message.

    -s|--stop           stop the running daemon
    -f|--foreground     executes in foreground (and outputs all notifications to stdout)
    -h|--help           this help message
''' % (sys.argv[0], sys.argv[0])
        sys.exit(0)

    # check for -stop
    if len(sys.argv) == 2 and sys.argv[1] in ('--stop', '-s'):
        if not os.path.isfile(PID_FILE):
            print 'nothing to stop. exiting...'
            sys.exit(1)
        try:
            os.kill(int(open(PID_FILE, 'r').read()), 9)
        except ValueError, ve:
            print 'Invalid PID file. exiting...'
            sys.exit(1)
        except OSError, oe:
            print 'Invalid PID: %s. Process has already exited. exiting...' % int(open(PID_FILE, 'r').read())
            sys.exit(1)
        os.unlink(PID_FILE)
        print 'notify daemon killed'
        sys.exit(0)

    if os.path.isfile(PID_FILE):
        print 'Daemon is already running... Exiting.'
        sys.exit(1)
    
    if not (len(sys.argv) == 2 and sys.argv[1] in ('-f', '--foreground')):
        print 'Starting server as daemon...'
        retCode = createDaemon()

        # create PID file
        f = open(PID_FILE, 'w').write(str(os.getpid()))
    else:
        print 'Starting server in foreground mode...'

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    
    while True:
        conn, addr = s.accept()
        while 1:
            data = conn.recv(1024)
            if not data: break
            p = subprocess.Popen(notify(data))
        conn.close()

    sys.exit(retCode)
