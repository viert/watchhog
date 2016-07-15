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
Number of workers. These are python threads so you can't use more than one CPU core actually. Multithreading makes it real to process more than one log simultaneously.


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
This option tells watchhog which fields to index. Compound indexes can have only one multiplicity level. Indexes are described below.


```
postprocess postprocess.to_datetime(datetime, "%d/%b/%Y:%H:%M:%S")
```
**postprocess** directive describes how to modify record after every line is parsed. In this example *postprocess.to_datetime* is the name of module and function in watchhog plugin directory (postprocess module is distributed with watchhog itself). *postprocess.to_datetime* function actually converts field named 'datetime' to python datetime format using *"%d/%b/%Y:%H:%M:%S"* parsing configuration. Plugins mechanism is powerful and it's described in section **Plugins** below.

```
setvar rps = accesslog.rps_by(vhost)
```
**setvar** directive makes watchdog create a variable (called **rps** in example above) and assign the return value of function following.


How the heck does it work exactly?
==================================

Filekeeper
----------

Watchhog creates a so called Filekeeper that tracks the logfile, reopens it after logrotate and so on. Every *period* scheduler creates task to poll the new data from log. One of workers (number of workers are configured with *threads* option) takes the task and asks Filekeeper to read the new data from log file. Filekeeper reads the file from previous position up to the end, reopens the new file, if it was rotated within the period and reads it up to the end too.


Parser
------

The next step is parsing. Every line of logfile portion is being parsed to create a *record* - actually a simple python dict. Every record is a key/value, where keys are field names configured in *pattern* and values are strings. Often strings are not convinient type of data, especially when you know exactly what type of data the particular field holds. Here goes *postprocess* functions. This is where the magic begins.

Postprocess
-----------

When each record is created, Watchhog runs postprocess functions passing the record as the first argument and the other arguments configured right behind. For example we have http status code field called **status** and we sure it's always integer. Configuration says:
```
postprocess postprocess.to_int(status)
```

Which means exactly *Run the function **to_int** from the **postprocess** module and pass current **record** and string 'status' as arguments.*
*to_int()* is a built-in function and it looks just like this:
```python
def to_int(record, key, base=10, default=None):
    try:
        record[key] = int(record[key], base)
    except ValueError:
        if not default is None:
            record[key] = default
```
As you can see, the record['status'] will be a type of int after function running.


Indexes
-------

The next important step is indexing. Indexes help watchhog (and us finally) to search particular records in store table.
Indexes are python structures built the following way. Let's say you have some lines of log:
```
[2016-02-18 12:34:30] example.com "GET /ping HTTP/1.0" 200
[2016-02-18 12:34:30] example.com "GET /not_exist HTTP/1.0" 404
[2016-02-18 12:34:31] example2.com "GET /ping HTTP/1.0" 200
[2016-02-18 12:34:32] example2.com "GET /not_exist HTTP/1.0" 200
```

And you have the index configuration like that:
```
index               datetime
index               status.vhost
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

`status.vhost` is a compound index useful from time to time. Compound idexes are two-field indexes exactly. There's no way to build index more than of two fields yet.


Variables
---------

So we have now the table that consist of all parsed lines in the last portion of log (previous part was dropped to free memory, watchhog is a tool for just-right-now monitoring), some fields are converted to convinient type, everything is indexed. Now we can group and reduce with the mechanism of variables.
```
setvar rps = accesslog.rps_by(vhost)
```
This configuration will tell Watchhog to run function *rps_by* from module *accesslog* and pass the datastore as the first argument and the string 'vhost' as the second one.
`datastore` is the python object with properties: 

`table`, which holds the list of records

`indexes`, which holds indexes

`vars`, which holds the dict of store variables

You do not have to create the var in your own function, you have just to return the value. For example, function *rps_by* creates a key/value dict where keys are the unique field values (let's say you have access log with `example.com` and `example2.com` vhosts occuring in it, so the keys are `example.com` and `example2.com` exactly) and the values are request-per-second for the particular vhost. Finally it adds the key __total__ with the sum of all rps values.



HTTP
----

Finally Watchhog has a HTTP interface. Mostly you need the following handlers:

`/api/tables/<tablename>/data` - list of records in JSON
`/api/tables/<tablename>/variables/<varname>` - value of variable *varname* in particular *table* in JSON

You can get the data using curl or any other http client periodically and send the data to your favorite graph system (e.g. graphite or cacti), save statistics and write scripts for monitoring (e.g. nagios, zabbix and so forth)


uWSGI
=====

Since version 0.1.15 watchhog uses uwsgi by default though it does not require it (except debian packaged version that does). The common uWSGI config will look like

```
[uwsgi]
plugins = python,http
wsgi-file = /usr/sbin/watchhog.py
callable = server

master = false
need-app = true
processes = 1
enable-threads = true
single-interpreter = true


http = 0.0.0.0:4000
uid = root
```

This configuration allows you to run watchhog without frontend nginx or another webserver, uWSGI daemon will handle http interface for you.
The things you should remember when you configure uwsgi manually are:

- master option should be false. watchhog requires only one process to run at a moment, so you don't need master/multiworkers uwsgi mechanism.
- need-app must be set to true to prevent uwsgi from starting empty: remember that watchhog must start its worker threads no matter if you ask it for data via http or don't
- processes should be set to 1 (see the explanation of master option)
- enable-threads must be set to true to enable uwsgi python interpreter threads. watchhog uses at least 2 threads: one for frontend interface and one for data collection and processing.
- single-interpreter must be set to true for the same reason you set processes option to 1
- you can set uid to whatever you want but be sure watchhog can read your logs you want to parse
