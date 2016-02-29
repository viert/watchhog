from hog.watcher.scheduler import Scheduler
from hog.watcher.task import Task
from hog.store import Store
from hog.configreader import parse_collector_config, ConfigurationParseError
from hog.parser.configurator import configure as configure_parser
import logging
import os
import sys


class Watcher(object):
    def __init__(self, config_dir, log_filename, plugin_dir, num_threads, loglevel):
        self.config_dir = config_dir
        self.plugin_dir = plugin_dir
        logging.basicConfig(filename=log_filename, level=loglevel, format="%(asctime)s %(levelname)s: %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")
        self.functions = {}
        self.tables = {}
        self.import_plugins()
        self.reconfigure_tasks()
        self.scheduler = Scheduler(self.tasks, self.tables, self.functions, num_threads)

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.stop()

    def reconfigure_tasks(self):
        self.tasks = []
        for f in os.listdir(self.config_dir):
            fullname = os.path.join(self.config_dir, f)
            if os.path.isdir(fullname):
                continue
            if f.endswith(".conf"):
                try:
                    c = parse_collector_config(fullname)
                except ConfigurationParseError as e:
                    logging.error("[Watcher] " + str(e))
                    logging.error("[Watcher] collector skipped")
                    continue
                collector_name = c['name']
                index_fields = c['index']

                postprocess = []
                for item in c['postprocess']:
                    try:
                        func_declaration = {
                            'function': self.functions[item['function']],
                            'args': item['args']
                        }
                    except KeyError:
                        logging.error('No function %s found for postprocess in config file %s' % (item['function'], f))
                        continue
                    postprocess.append(func_declaration)

                variables = {}
                for varname, item in c['vars'].items():
                    try:
                        func_declaration = {
                            'function': self.functions[item['function']],
                            'args': item['args']
                        }
                    except KeyError:
                        logging.error('No function %s found for variable "%s" in config file %s' % (item['function'], varname, f))
                        continue
                    variables[varname] = func_declaration

                self.tables[collector_name] = Store(index_fields)

                try:
                    parser = configure_parser(c['pattern'])
                except ValueError as e:
                    logging.error("[Watcher] %s. collector skipped" % str(e))
                    continue
                task = Task(c, parser, postprocess, variables)
                self.tasks.append(task)

    def import_plugins(self):
        sys.path.append(self.plugin_dir)
        for python_file in os.listdir(self.plugin_dir):
            if not python_file.endswith('.py'): continue
            module_name = os.path.splitext(os.path.basename(python_file))[0]
            try:
                i = __import__(module_name)
                exports = i.exports
            except ImportError as e:
                logging.error('[Watcher] Error importing module "%s": %s' % ( module_name, str(e) ))
                continue
            except AttributeError as e:
                logging.error('[Watcher] Error importing module "%s": %s' % ( module_name, str(e) ))
                continue
            names = []
            for func_name in exports:
                if hasattr(func_name, '__call__'):
                    func = func_name
                    func_name = func.__name__
                else:
                    try:
                        func = i.__dict__[func_name]
                    except KeyError as e:
                        logging.error('[Watcher] Error importing function "%s" from module "%s"' % (func_name, module_name))
                        continue
                key = "%s.%s" % (module_name, func_name)
                self.functions[key] = func
                names.append(func_name)
            logging.debug("[Watcher] module %s imported successfully. Functions: %s" % (module_name, str(names)))
