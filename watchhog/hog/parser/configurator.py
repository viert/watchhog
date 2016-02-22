#
# Simple FSM parser configurator
# Analyzes log pattern to create parser directives (upTo and skip mostly)
#

from hog.parser import Parser
import re
import unittest

STATE_READ_SYM = 1
STATE_READ_ESCAPED_SYM = 2
STATE_READ_VARNAME = 3
STATE_READ_BRACED_VARNAME = 4

VARNAME_SYM_RE = re.compile("[\w-]")

def configure(line, parser=None):
    if parser is None:
        parser = Parser()

    if line[-1] != "\n": line += "\n"

    index = 0
    state = STATE_READ_SYM
    var_name = ""

    while index < len(line):
        sym = line[index]
        index += 1

        if state == STATE_READ_SYM:
            if sym == "$":
                state = STATE_READ_VARNAME
                var_name = ""
            elif sym == "\\":
                state = STATE_READ_ESCAPED_SYM
            else:
                parser.skip(sym)

        elif state == STATE_READ_VARNAME:
            if var_name == "" and sym == "{":
                state = STATE_READ_BRACED_VARNAME
            elif VARNAME_SYM_RE.match(sym):
                var_name += sym
            else:
                if var_name != "-":
                    parser.upTo(sym, var_name)
                    parser.skip(sym)
                else:
                    parser.skipTo(sym)
                    parser.skip(sym)
                state = STATE_READ_SYM

        elif state == STATE_READ_BRACED_VARNAME:
            if sym == "}":
                sym = line[index]
                index += 1
                if var_name != "-":
                    parser.upTo(sym, var_name)
                    parser.skip(sym)
                else:
                    parser.skipTo(sym)
                    parser.skip(sym)
                state = STATE_READ_SYM
            else:
                var_name += sym

        elif state == STATE_READ_ESCAPED_SYM:
            parser.skip(sym)

    if state != STATE_READ_SYM:
        raise ValueError("Invalid log pattern line")

    return parser

class TestConfigurator(unittest.TestCase):

    def test_configure(self):
        LOGLINE = '[18/Feb/2016:00:39:05 +0300] export.yandex.ru 178.68.203.196 "GET /for/counters.xml HTTP/1.1" 200 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 YaBrowser/16.2.0.3539 Safari/537.36" "yandex_gid=10945; yandexuid=158266091453834562;" 4237'
        PATTERN = '[$datetime $timezone] $vhost $ip "$method $url $http_version" $status "-" "$useragent" "$cookies" $reqtime'

        expectedResults = {
            'datetime': '18/Feb/2016:00:39:05',
            'timezone': '+0300',
            'vhost': 'export.yandex.ru',
            'ip': '178.68.203.196',
            'method': 'GET',
            'url': '/for/counters.xml',
            'http_version': 'HTTP/1.1',
            'status': '200',
            'useragent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 YaBrowser/16.2.0.3539 Safari/537.36',
            'cookies': 'yandex_gid=10945; yandexuid=158266091453834562;',
            'reqtime': '4237'
        }

        parser = configure(PATTERN)
        self.assertTrue(parser.parseLine(LOGLINE+"\n"))
        self.assertDictEqual(parser.getResults(), expectedResults)

    def test_configure_ignore_match(self):
        LOGLINE = '[18/Feb/2016:00:39:05 +0300] export.yandex.ru 178.68.203.196 "GET /for/counters.xml HTTP/1.1" 200 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 YaBrowser/16.2.0.3539 Safari/537.36" "yandex_gid=10945; yandexuid=158266091453834562;" 4237'
        PATTERN = '[$datetime $-] $vhost $ip "$method $url $-" $status "-" "$-" "$-" $reqtime'
        expectedResults = {
            'datetime': '18/Feb/2016:00:39:05',
            'vhost': 'export.yandex.ru',
            'ip': '178.68.203.196',
            'method': 'GET',
            'url': '/for/counters.xml',
            'status': '200',
            'reqtime': '4237'
        }

        parser = configure(PATTERN)
        self.assertTrue(parser.parseLine(LOGLINE+"\n"))
        self.assertDictEqual(parser.getResults(), expectedResults)

if __name__ == '__main__':
    unittest.main()