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

Watchhogs looks into `collectors directory` and tries to load every file with `.conf` extension. Other files would be ignored so distribution-arrived `nginx.conf.example` will never be used until you rename in to `nginx.conf`. Every collector are configured with the following options:

```
name                nginx
```
This is the collector name. It should be unique. Otherwise you'll have the only one collector, the last one watchhog had found in the directory.

```
log                 /var/log/nginx/access.log
```
The logfile collector handles

```
period              1m
dispersion          5s
```
Watchhog will read the new portion of log every `period` plus-minus `dispersion`. The dispersion option is used to minimize disk load (with two or more logs handled watchhog will not read them at once but with a random delay)

```
pattern             [$datetime $-] $vhost $ip "$method $url $-" $status "$referer" "$useragent" "$cookies" $time
```
Parser configuration. The most complex option. Will be described below.

```
index               datetime
index               status.vhost
```
This option tells watchhog which fields to index. Compound indexes can have only one multiplicity level. Indexes are python structures built the following way. Let's say you have some lines of log:
```
[2016-02-18 12:34:30] example.com "GET /ping HTTP/1.0" 200
[2016-02-18 12:34:30] example.com "GET /not_exist HTTP/1.0" 404
[2016-02-18 12:34:31] example2.com "GET /ping HTTP/1.0" 200
[2016-02-18 12:34:32] example2.com "GET /not_exist HTTP/1.0" 200
```
With the configuration above watchhog will build the following structures
```python
# datetime index
index['datetime']['index'] = {
  '2016-02-18 12:34:30' : [0, 1],
  '2016-02-18 12:34:31' : [2],
  '2016-02-18 12:34:32' : [3]
}
index['datetime']['counters'] = {
  '2016-02-18 12:34:30' : 2,
  '2016-02-18 12:34:31' : 1,
  '2016-02-18 12:34:32' : 1
}
index['datetime']['keys'] = [ '2016-02-18 12:34:30', '2016-02-18 12:34:31', '2016-02-18 12:34:32' ]

# status.vhost index
index['status.vhost']['index'] = {
  '200': {
    'example.com': [0],
    'example2.com': [2]
  },
  '404': {
    'example.com': [1],
    'example2.com': [3]
  }
}
index['status.vhost']['counters'] = {
  '200': { 'example.com': 1, 'example2.com': 1 },
  '404': { 'example.com': 1, 'example2.com': 1 }
}
```
