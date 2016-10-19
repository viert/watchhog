import re
import unittest
import logging

CommentPattern = re.compile(r'^#(.*)$')

COLLECTOR_DEFAULTS = {
    'period': '1m',
    'dispersion': '5s'
}

MAIN_DEFAULTS = {
    'threads': 10,
    'log': '/var/log/watchhog/watchhog.log',
    'loglevel': logging.ERROR,
    'pidfile': '/var/run/watchhog.pid',
    'bind': ':5000',
    'plugins_directory': '/usr/lib/watchhog/plugins',
    'collectors_directory': '/etc/watchhog/collectors'
}

NamePattern = re.compile(r'^name\s+(\w+)(?:\s+#.*)?$')
LogPattern = re.compile(r'^log\s+([^\s]+)(?:\s+#.*)?$')
PeriodPattern = re.compile(r'^period\s+(\d+[smh])(?:\s+#.*)?$')
DispersionPattern = re.compile(r'^dispersion\s+(\d+[smh])(?:\s+#.*)?$')
PatternPattern = re.compile(r'^pattern\s+(.+)$')
IndexPattern = re.compile(r'^index\s+([\w\.]+)(?:\s+#.*)?$')
PostProcessPattern = re.compile(r'^postprocess\s+([\w\.]+)\((.*)\)(?:\s+#.*)?$')
SetVarPattern = re.compile(r'^setvar\s+(\w+)\s*=\s*([\w\.]+)\((.*)\)(?:\s+#.*)?$')

COLLECTOR_FIELDS = [ 'name', 'log', 'pattern', 'index', 'period', 'dispersion', 'postprocess', 'vars' ]

class ConfigurationParseError(StandardError):
    def __init__(self, msg, filename, lineno):
        StandardError.__init__(self, "%s in file %s at line %d" % (msg, filename, lineno+1))
        self.msg = msg
        self.filename = filename
        self.lineno = lineno + 1


def parse_arguments_list(line, filename, index):

    # empty args optimisation
    if line == '':
        return []

    WAIT_ARG = 0
    READ_QUOTED_ARG = 1
    READ_APOSTROPHED_ARG = 2
    READ_PLAIN_ARG = 3
    WAIT_COMMA_OR_EOL = 4
    WHITE = re.compile(r'\s')

    args = []
    i = 0
    state = WAIT_ARG

    while i < len(line):
        sym = line[i]
        i += 1

        if state == WAIT_ARG:
            if sym == '"':
                state = READ_QUOTED_ARG
                arg = ""
            elif sym == "'":
                state = READ_APOSTROPHED_ARG
                arg = ""
            elif WHITE.match(sym):
                continue
            else:
                state = READ_PLAIN_ARG
                arg = sym
        elif state == READ_QUOTED_ARG:
            if sym == '"':
                args.append(arg)
                state = WAIT_COMMA_OR_EOL
            else:
                arg += sym
        elif state == READ_APOSTROPHED_ARG:
            if sym == "'":
                args.append(arg)
                state = WAIT_COMMA_OR_EOL
            else:
                arg += sym
        elif state == READ_PLAIN_ARG:
            if WHITE.match(sym):
                args.append(arg)
                state = WAIT_COMMA_OR_EOL
            elif sym == ',':
                args.append(arg)
                state = WAIT_ARG
            elif i == len(line):
                args.append(arg+sym)
                state = WAIT_COMMA_OR_EOL
            else:
                arg += sym
        elif state == WAIT_COMMA_OR_EOL:
            if WHITE.match(sym):
                continue
            elif sym == ",":
                state = WAIT_ARG
    if state != WAIT_COMMA_OR_EOL:
        raise ConfigurationParseError("Malformed arguments list", filename, index)
    return args


def parse_duration(dur, filename, index):
    m = re.match('^(\d+)([hms])$', dur)
    if m is None:
        raise ConfigurationParseError("Invalid duration: %s" % dur, filename, index)
    mult = 1
    if m.group(2) == "m":
        mult = 60
    elif m.group(2) == "h":
        mult = 3600
    return int(m.group(1))*mult

def parse_main_config(filename):
    index = 0
    config = {}
    f = open(filename)
    for index, line in enumerate(f):
        line = line.strip()
        if line == "" or CommentPattern.match(line):
            continue
        try:
            directive, value = line.split()
        except ValueError:
            raise ConfigurationParseError("Malformed configuration line", filename, index)

        if directive not in MAIN_DEFAULTS:
            raise ConfigurationParseError("Invalid directive: %s" % directive, filename, index)

        if directive == "threads":
            try:
                value = int(value)
            except:
                raise ConfigurationParseError("Invalid thread number", filename, index)
        if directive == "loglevel":
            try:
                value = logging.__getattribute__(value.upper())
            except AttributeError:
                raise ConfigurationParseError("Invalid log level", filename, index)

        config[directive] = value

    try:
        host, port = config['bind'].split(':')
    except ValueError:
        raise ConfigurationParseError("Invalid bind option: %s" % config['bind'], filename, index)
    if host == '':
        host = '127.0.0.1'
    try:
        port = int(port)
    except:
        raise ConfigurationParseError("Invalid port: %s" % port, filename, index)
    config['bind'] = (host, port)

    for key in MAIN_DEFAULTS:
        if not key in config:
            config[key] = MAIN_DEFAULTS[key]

    return config


def parse_pattern(line):
    pattern = PatternPattern.match(line).group(1)
    pattern = pattern\
        .replace('\\t', '\t')\
        .replace('\\n', '\n')
    return pattern


def parse_collector_config(filename):

    config = {
        'index': [],
        'postprocess': [],
        'vars': {}
    }

    f = open(filename)
    for index, line in enumerate(f):
        line = line.strip()
        if line == "" or CommentPattern.match(line):
            continue
        elif NamePattern.match(line):
            if 'name' in config:
                raise ConfigurationParseError('Duplicate name directive', filename, index)
            config['name'] = NamePattern.match(line).group(1)
        elif LogPattern.match(line):
            if 'log' in config:
                raise ConfigurationParseError('Duplicate log directive', filename, index)
            config['log'] = LogPattern.match(line).group(1)
        elif PeriodPattern.match(line):
            if 'period' in config:
                raise ConfigurationParseError('Duplicate period directive, index', filename, index)
            config['period'] = parse_duration(PeriodPattern.match(line).group(1), filename, index)
        elif DispersionPattern.match(line):
            if 'dispersion' in config:
                raise ConfigurationParseError('Duplicate dispersion directive', filename, index)
            config['dispersion'] = parse_duration(DispersionPattern.match(line).group(1), filename, index)
        elif PatternPattern.match(line):
            if 'pattern' in config:
                raise ConfigurationParseError('Duplicate pattern directive', filename, index)
            config['pattern'] = parse_pattern(line)

        elif IndexPattern.match(line):
            config['index'].append(IndexPattern.match(line).group(1))
        elif PostProcessPattern.match(line):
            m = PostProcessPattern.match(line)
            function = m.group(1)
            if m.group(2) is None:
                args = []
            else:
                args = parse_arguments_list(m.group(2), filename, index)
            config['postprocess'].append({ 'function': function, 'args': args })
        elif SetVarPattern.match(line):
            m = SetVarPattern.match(line)
            varname = m.group(1)
            if varname in config['vars']:
                raise ConfigurationParseError("Duplicate variable '%s'" % varname, filename, index)
            function = m.group(2)
            if m.group(3) is None:
                args = []
            else:
                args = parse_arguments_list(m.group(3), filename, index)
            config['vars'][varname] = { 'function': function, 'args': [x.strip().strip('"').strip("'") for x in args] }
        else:
            raise ConfigurationParseError("Parse error", filename, index)

    for key in COLLECTOR_DEFAULTS:
        if key not in config:
            config[key] = COLLECTOR_DEFAULTS[key]
    return config


class TestConfigReader(unittest.TestCase):
    def test_argument_parser(self):
        args = parse_arguments_list('"abc",\'def\' ,19, "some spaced arg\'" ', "filename", 0)
        self.assertEqual(['abc', 'def', '19', 'some spaced arg\''], args)
        args = parse_arguments_list('status', 'filename', 0)
        self.assertEqual(['status'], args)
        args = parse_arguments_list('datetime, " ", date, time', "filename", 0)
        self.assertEqual(['datetime', ' ', 'date', 'time'], args)
        args = parse_arguments_list('', "filename", 0)
        self.assertEqual([], args)

    def test_pattern_parser(self):
        line = r"pattern [$datetime]\t$vhost"
        self.assertEqual(parse_pattern(line), '[$datetime]\t$vhost')


if __name__ == '__main__':
    unittest.main()