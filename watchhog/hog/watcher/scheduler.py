import time
import logging
from Queue import Queue
from hog.watcher.stoppable_thread import StoppableThread
from hog.watcher.worker import Worker

class Scheduler(StoppableThread):
    def __init__(self, tasks, metastore, functions, num_threads=10):
        StoppableThread.__init__(self)
        self.stopped = False
        self.tasks = tasks
        self.queue = Queue()
        self.pool = []
        for i in xrange(num_threads):
            worker = Worker(self.queue, metastore, functions, i+1)
            self.pool.append(worker)

    def stop(self):
        for worker in self.pool:
            worker.stop()
        StoppableThread.stop(self)

    def run(self):
        self.state = 'running'
        try:
            for worker in self.pool:
                worker.start()

            while not self.stopped:
                time.sleep(1.0)
                for task in self.tasks:
                    if task.ready():
                        task.on_queue()
                        self.queue.put(task)
                        logging.debug("[Scheduler] %s queued" % task)
        except Exception as e:
            logging.error("[Scheduler] Exception in scheduler thread: %s" % e.message)
            self.stop()

        self.state = 'stopped'