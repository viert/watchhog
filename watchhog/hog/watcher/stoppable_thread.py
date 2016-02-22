from threading import Thread

class StoppableThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.stopped = False
        self.state = 'initializing'
        self.daemon = True

    def stop(self):
        self.state = 'stopping'
        self.stopped = True