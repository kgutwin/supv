#!/usr/bin/python

import time
import logging

class Node:
    # defaults to updating immediately
    FREQ = 0.0
    def __init__(self, freq=None):
        if freq is not None:
            self.FREQ = float(freq)
        self.last_update = 0
        self.last_do = time.time()
        self.id = 'UNKNOWN'
        self.logger = logging.getLogger('log')

    def __repr__(self):
        return "<%s (id=%s)>" % (str(self.__class__), self.id)

    def update(self):
        n = time.time()
        if n >= (self.last_update + self.FREQ):
            self.logger.debug("running %s %f %f %f" % (repr(self), self.last_update, self.FREQ, n))
            self.last_update = n
            self.do()
            self.last_do = time.time()
            return True
        return False

    def bool(self, s):
        return s.lower() == "true"

    def secs_since_last_do(self):
        return time.time() - self.last_do
    def secs_until_next_update(self):
        return max(0, (self.last_update + self.FREQ) - time.time())

class Producer(Node):
    pass

class Consumer(Node):
    def __init__(self, **kwargs):
        Node.__init__(self, **kwargs)
        self.inputs = {}

    def update(self):
        # check if any input connection has changed
        if [1 for c in self.inputs.values() if c.changed]:
            return Node.update(self)
        return False

    def attach(self, conn):
        self.inputs[conn.source.id] = conn

