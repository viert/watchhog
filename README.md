Watchhog
========

What?
-----

Watchhog is a fast log watcher, parser and indexer written on Python/C++. It takes log file you ask it to handle, reads it every minute (that's for example, actually you can freely configure the period option), parse with fast token parser easily configured with **pattern** option, saves the result to python structure, actually a list of dicts, then builds indexes you configure for fast searching and makes it available by http in JSON format.

Why?
----

It's useful in my everyday tasks as system administrator. For example it solves the often task to answer the question "how much RPS do my server have just right now?" or to determine response timings.

Installation
------------

Watchhog is carefully debianized and can be freely built and installed on Ubuntu Trusty. It also have to install easily with usual *setup.py* mechanism.
You also have to install boost-python library to build the native parser. Anyway Watchhog has a pure-pythonic fallback parser though the python version of parser is dramatically slower.
*(Native parser is available on Linux systems. The installation script was hardcoded to check platform and would fail to build native extension on any other platform except Linux. The Mac OS X version will be soon available too)*

Configuration
-------------

By default Watchhog reads file `/etc/watchhog/watchhog.conf` as the main configuration. The following options are available:

```
collectors_directory  /etc/watchhog/collectors
```
Directory with collectors configurations. Will be described below

```
log                   /var/log/watchhog.log
```
Daemon's logfile

```
loglevel              debug
```
Daemon's log level. Standard python log levels are available, for example *info*, *error*, *warn*. Recommended production log level is *info*

```
pidfile               /var/run/watchhog.pid
```
That's it. The pidfile. I mean it.

```
bind                  0.0.0.0:5000
```
Host and port to bind. Host is optional, the default is 127.0.0.1. You should use 127.0.0.1 for security reasons but you have to bind on external (non-loopback) interfaces to use the Watchhog beautiful interface =)

```
plugins_directory     /usr/share/pyshared/hog/plugins
```
Directory for the daemon's plugins. By default watchhog arrives with a couple of it's own plugins (described below) stored in this directory

```
threads               10
```
Number of workers. Theese are python threads so you can't use more than one CPU core actually. Multithreading makes it real to process more than one log simultaneously.


Collector configuration
-----------------------
