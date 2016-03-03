import time
import random
from hog.utils import format_date
from hog.configreader import COLLECTOR_FIELDS
from datetime import datetime

class Task(object):
    def __init__(self, collector_config, parser, postprocess, variables):
        for field in COLLECTOR_FIELDS:
            self.__setattr__(field, collector_config[field])
        self.pattern = collector_config['pattern']
        self.parser = parser
        self.postprocess = postprocess
        self.vars = variables
        self.in_progress = False
        self.done_at = None
        self.started_at = None
        self.schedule()

    def schedule(self):
        if self.done_at is None:
            self.next_start = time.time() + random.randint(0, self.dispersion)
        else:
            deviation = random.randint(-self.dispersion, self.dispersion)
            self.next_start = self.done_at + self.period + deviation

    def on_queue(self):
        self.in_progress = True

    def on_start(self):
        self.started_at = time.time()

    def on_done(self):
        self.done_at = time.time()
        self.in_progress = False
        self.schedule()

    def to_dict(self):
        variables = {}
        for varname, x in self.vars.items():
            variables[varname] = { 'function': "%s.%s" % ( x['function'].__module__, x['function'].__name__ ), 'args': x['args'] }

        return {
            'collector': {
                'name': self.name,
                'pattern': self.pattern,
                'log': self.log,
                'index': self.index,
                'postprocess': [{ 'function': "%s.%s" % ( x['function'].__module__, x['function'].__name__ ), 'args': x['args'] } for x in self.postprocess],
                'period': self.period,
                'dispersion': self.dispersion,
                'vars': variables
            },
            'in_progress': self.in_progress,
            'started_at': datetime.utcfromtimestamp(self.started_at).isoformat(' ') if self.started_at is not None else None,
            'next_start': datetime.utcfromtimestamp(self.next_start).isoformat(' ') if self.next_start is not None else None,
            'done_at': datetime.utcfromtimestamp(self.done_at).isoformat(' ') if self.done_at is not None else None
        }

    def ready(self):
        return not self.in_progress and (time.time() >= self.next_start)

    def __repr__(self):
        return '[Task collector="%s" log="%s" in_progress="%s" last_started_at="%s" last_done_at="%s" next_start="%s"]' % ( self.name,
                                                                                                                            self.log,
                                                                                                                            self.in_progress,
                                                                                                                            format_date(self.started_at),
                                                                                                                            format_date(self.done_at),
                                                                                                                            format_date(self.next_start) )
