#!/bin/bash
#
# Irssi notifications over a SSH Tunnel
#
# description: Notifcations to growl
#	- Written in a init script style
#
# processname: irssi-notify-listener.py

BASE=/usr/local/sbin
PID_FILE=/tmp/irssi-notify-listener.pid
RETVAL=0
prog="irssi-notify-listener.py"
sprog="irssi-notify-listener.sh"

SSHHost="us.cooperlees.com"
NOTIFY_PORT=4222

installScripts()
{
	if [ -d $BASE ]; then
		if [ -e $prog ]; then
			echo -n "Installing $prog to $BASE ... "
			cp $prog $BASE
			if [ $? -ne 0 ]; then
				echo "FAILED!"
				exit 3
			fi
			echo "Done"

			echo -n "Installing $sprog to $BASE ... "
			cp $sprog $BASE
			if [ $? -ne 0 ]; then
				echo "FAILED!"
				exit 4
			fi
			echo "Done"

			chmod 775 $BASE/$prog $BASE/$sprog
		else
			echo "!-> $prog is not in $PWD"
			exit 2
		fi
	else
		echo "!-> No $BASE exists .."
		exit 1
	fi
}

SSHReverseTunnelStart()
{
	echo -n "Starting reverse ssh tunnel ... "

	ssh $SSHHost -f -N -R $NOTIFY_PORT:localhost:$NOTIFY_PORT

	echo "done"
}

SSHReverseTunnelStop()
{
	PID=$(ps -ef | grep "ssh $SSHHost.*-R $NOTIFY_PORT" | grep -v "grep" | cut -d " " -f 2 | head -1)
	if [ "$PID" != "" ]; then
		echo -n "Stopping reverse ssh tunnel ... "
		kill $PID
		echo "done"
	fi
}

start()
{
	echo -n $"Starting $prog:"

	${BASE}/${prog} > /dev/null
	RETVAL=$?

	echo " done"
}

stop()
{
	echo -n $"Stopping $prog:"
	
	${BASE}/${prog} --stop > /dev/null
	RETVAL=$?

	echo " done"
}

case "$1" in
	install)
		installScripts
		;;
	start)
		start
		;;
	startall)
		SSHReverseTunnelStart
		start
		;;
	stop)
		SSHReverseTunnelStop
		stop
		;;
	restart)
		stop
		start
		;;
	status)
		if [ ! -e $PID_FILE ]; then
			echo "--> $prog is not running ..."
		else
			PID=$(cat $PID_FILE)
			echo "--> $prog is running (PID = $PID)"	
		fi
		;;
	*)
		echo $"Usage: $0 {start|startall|stop|restart|status}"
		RETVAL=69
esac
exit $RETVAL
