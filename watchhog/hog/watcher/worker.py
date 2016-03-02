import logging
import time
import random
from Queue import Empty, Queue
from hog.filekeeper import filekeeper
from hog.store import Store
from hog.watcher.stoppable_thread import StoppableThread

class Worker(StoppableThread):
    def __init__(self, queue, metastore, functions, thread_id):
        StoppableThread.__init__(self)
        self.queue = queue
        self.functions = functions
        self.metastore = metastore
        self.current_task = None
        self.thread_id = thread_id
        logging.debug('[Worker #%d] worker created' % self.thread_id)

    def perform_task(self, task):
        task.on_start()
        self.current_task = task

        # creating new store
        store = Store(task.index)

        # reading data
        self.state = 'reading data from log %s' % task.log
        data = filekeeper.read(task.log)
        logging.debug('[Worker #%d] collector "%s" read %d bytes from %s' % (self.thread_id, task.name, len(data), task.log))

        if data == '':
            logging.info('[Worker #%d] collector "%s" has no data to parse' % (self.thread_id, task.name))
        else:
            # parsing and saving data
            self.state = 'parsing new data from %s' % task.log
            total = 0
            parsed = 0
            t1 = time.time()
            for line in data.split('\n'):
                if line == '': continue
                success = task.parser.parseLine(line+"\n")
                if success:
                    parsed += 1
                    record = task.parser.getResults()

                    # postprocess
                    for callback in task.postprocess:
                        func = callback['function']
                        args = [record] + callback['args']
                        try:
                            func(*args)
                        except Exception as e:
                            logging.error("[%s.%s] %s" % (func.__module__, func.__name__, repr(e)))

                    store.push(record, False)
                else:
                    if line == "":
                        logging.debug("Empty line parse")
                    else:
                        logging.debug("Line failed to parse: %s" % line)
                total += 1
            t2 = time.time()
            logging.info('[Worker #%d] collector "%s" parsed %d of %d lines of %s in %.06f seconds' % (self.thread_id,
                                                                                                       task.name,
                                                                                                       parsed,
                                                                                                       total,
                                                                                                       task.log,
                                                                                                       (t2 - t1)
                                                                                                       )
                         )
            store.reindex_all()
            t3 = time.time()
            logging.info('[Worker #%d] collector "%s" indexes built in %.06f seconds' % (self.thread_id, task.name, (t3-t2)))

            for varname, handler in task.vars.items():
                func = handler['function']
                args = [store] + handler['args']
                try:
                    result = func(*args)
                except Exception as e:
                    logging.error("[%s.%s] %s" % (func.__module__, func.__name__, repr(e)))
                    continue
                    raise
                store.set_var(varname, result)
            t4 = time.time()
            logging.info('[Worker #%d] collector "%s" variables calculated in %.06f seconds' % (self.thread_id, task.name, (t4-t3)))

            self.metastore[task.name] = store
        task.on_done()

    def run(self):
        logging.debug('[Worker #%d] worker started' % self.thread_id)
        try:
            while not self.stopped:
                self.state = 'sleeping'
                # cpu idle for up to 250ms
                time.sleep(random.random()/4)
                self.state = 'reading queue'
                try:
                    task = self.queue.get_nowait()
                except Empty:
                    continue

                logging.debug('[Worker #%d] got task %%"%s" from queue' % (self.thread_id, task.name))
                self.perform_task(task)
        except Exception as e:
            logging.error("[Worker #%d] Exception in thread: %s" % (self.thread_id, repr(e)))
            self.stop()

        self.state = 'stopped'
