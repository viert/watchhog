#!/usr/bin/env python
from hog.watcher.watcher import Watcher
from hog.configreader import parse_main_config
from hog.web.web import WatchFlask, server
from optparse import OptionParser
import sys
import os
import signal
import atexit

DEFAULT_CONFIG="/etc/watchhog/watchhog.conf"

watcher = None
host = None
port = None

def __default_term_handler(signalnum, frame):
    sys.exit(0)


def __remove_pid_file(pidfile):
    try:
        os.unlink(pidfile)
    except:
        pass


def start_daemon(mainfunc, pidfile, termfunc=__default_term_handler):
    if not pidfile is None:
        atexit.register(__remove_pid_file, pidfile)
    if not termfunc is None:
        signal.signal(signal.SIGTERM, termfunc)

    try:
        pid = os.fork()
    except OSError as e:
        raise Exception("%s [%d]" % (e.strerror, e.errno))

    if pid == 0:
        os.closerange(0,3)
        os.setsid()
        try:
            pid = os.fork()
        except OSError as e:
            raise Exception("%s [%d]" % (e.strerror, e.errno))

        if pid == 0:
            mainfunc()

        else:
            if not pidfile is None:
                with open(pidfile, "w") as pf:
                    pf.write(str(pid))
            os._exit(0)
    else:
        os._exit(0)


def start_debug():
    watcher.start()
    WatchFlask.setWatcher(watcher)
    server.run(host=host, port=port, debug=True)

def start():
    watcher.start()
    WatchFlask.setWatcher(watcher)
    server.run(host=host, port=port)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-c', '--config', dest="configfile", help="main watchhog configuration file", default=DEFAULT_CONFIG)
    parser.add_option('-f', '--foreground', dest="foreground", action="store_true", help="stay in foreground")
    (options, args) = parser.parse_args()
    if options.configfile is None:
        parser.print_help()
        sys.exit(1)

    config = parse_main_config(options.configfile)
    host, port = config['bind']
    watcher = Watcher(config['collectors_directory'], config['log'], config['plugins_directory'], config['threads'], config['loglevel'])

    if options.foreground:
        start_debug()
    else:
        start_daemon(start, config['pidfile'])
else:
    # uwsgi entry point. default config
    config = parse_main_config(DEFAULT_CONFIG)
    watcher = Watcher(config['collectors_directory'], config['log'], config['plugins_directory'], config['threads'], config['loglevel'])
    watcher.start()
    WatchFlask.setWatcher(watcher)
