#!/bin/bash
### BEGIN INIT INFO
# Provides:          watchhog
# Required-Start:    $network $local_fs
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: <Enter a short description of the software>
# Description:       <Enter a long description of the software>
#                    <...>
#                    <...>
### END INIT INFO

# Author: Pavel Vorobyov <aquavitale@yandex.ru>

PATH=/sbin:/usr/sbin:/bin:/usr/bin
DESC=watchhog                  # Introduce a short description here
NAME=watchhog                  # Introduce the short server's name here
DAEMON=/usr/sbin/watchhog.py   # Introduce the server's location here
DAEMON_ARGS=""                 # Arguments to run the daemon with
PIDFILE=/var/run/$NAME.pid
SCRIPTNAME=/etc/init.d/$NAME

# Exit if the package is not installed
[ -x $DAEMON ] || exit 0

# Read configuration variable file if it is present
[ -r /etc/default/$NAME ] && . /etc/default/$NAME

# Load the VERBOSE setting and other rcS variables
. /lib/init/vars.sh

# Define LSB log_* functions.
# Depend on lsb-base (>= 3.0-6) to ensure that this file is present.
. /lib/lsb/init-functions

#
# Function that starts the daemon/service
#

get_pid() {
  if [ -e $PIDFILE ]; then
    pid=`cat $PIDFILE`
  else
    pid=`ps ax | grep $DAEMON | grep -v grep | awk '{ print $1 }'`
  fi
}

do_start()
{
  get_pid
  if [ "x$pid" != "x" ]; then
    echo $DAEMON is already running
    return 1
  fi

  $DAEMON
  sleep 0.1

  get_pid
  if [ "x$pid" == "x" ]; then
    echo $DAEMON failed to start
    return 2
  fi

  echo $DAEMON started.
  return 0
}

#
# Function that stops the daemon/service
#
do_stop()
{
  get_pid
  if [ "x$pid" == "x" ]; then
    echo $DAEMON is already stopped
    return 1
  fi

  kill $pid
  sleep 0.1

  get_pid
  if [ "x$pid" != "x" ]; then
    echo $DAEMON failed to stop
    return 2
  fi

  echo $DAEMON stopped
    rm -f $PIDFILE
  return 0
}

#
# Function that sends a SIGHUP to the daemon/service
#
do_reload() {
    return 0
}

case "$1" in
  start)
    [ "$VERBOSE" != no ] && log_daemon_msg "Starting $DESC " "$NAME"
    do_start
    case "$?" in
        0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
        2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
    esac
  ;;
  stop)
    [ "$VERBOSE" != no ] && log_daemon_msg "Stopping $DESC" "$NAME"
    do_stop
    case "$?" in
        0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
        2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
    esac
    ;;
  status)
    echo $DAEMON status is not implemented in initscript

  ;;
  restart|force-reload)
    #
    # If the "reload" option is implemented then remove the
    # 'force-reload' alias
    #
    log_daemon_msg "Restarting $DESC" "$NAME"
    do_stop
    case "$?" in
      0|1)
        do_start
        case "$?" in
            0) log_end_msg 0 ;;
            1) log_end_msg 1 ;; # Old process is still running
            *) log_end_msg 1 ;; # Failed to start
        esac
        ;;
      *)
        # Failed to stop
        log_end_msg 1
        ;;
    esac
    ;;
  *)
    #echo "Usage: $SCRIPTNAME {start|stop|restart|reload|force-reload}" >&2
    echo "Usage: $SCRIPTNAME {start|stop|restart|force-reload}" >&2
    exit 3
    ;;
esac

:
