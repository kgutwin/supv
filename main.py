#!/usr/bin/python

import time
from xml.dom import minidom

import daemon

class Connection:
    def __init__(self, source, field, destination):
        self.source = source
        self.field = field
        self.destination = destination
        destination.attach(self)
        
        self.field_hash = None
        self.changed = True

    def __repr__(self):
        return "<Connection (%s, %s, %s)>" % (repr(self.source), repr(self.field), repr(self.destination))

    def get(self):
        return getattr(self.source, self.field)

    def update(self):
        if self.source.update():
            new_hash = hash(repr(self.get()))
            self.changed = (new_hash != self.field_hash)
            self.field_hash = new_hash


class Supv(daemon.Daemon):
    APPNAME = "supv"
    LOGDIR = "/var/log"
    CONFIGFILE = "config.xml"

    def __init__(self):
        daemon.Daemon.__init__(self)
        self.nodes = {}
        self.conns = []
        self.chain_ends = []
    
    def add_node(self, id, klass, kwargs):
        self.log_debug("creating node %s %s" % (id, repr(kwargs)))
        node = klass(**kwargs)
        node.id = id
        self.nodes[id] = node

    def add_connection(self, source, val, dest):
        self.log_debug("creating connection %s (%s) to %s" % (source, val, dest))
        c = Connection(self.nodes[source], val, self.nodes[dest])
        # find the highest index with dest node equal to this source node
        inds = [i for i in range(len(self.conns))
                if self.conns[i].destination is c.source]
        # and insert after that index
        insert_point = max(inds + [-1]) + 1
        self.conns.insert(insert_point, c)
        # finally, determine chain ends
        ce = {}
        for c in self.conns:
            ce[c.destination] = ce.get(c.destination, True) and True
            ce[c.source] = False
        self.chain_ends = [k for k, v in ce.items() if v == True]

    def initialize(self, configfn):
        # read config file
        cdom = minidom.parse(configfn)
        # parse import statements
        for dnode in cdom.getElementsByTagName("import"):
            mod = __import__(dnode.getAttribute('name'), globals(), locals(), [], -1)
            # create nodes
            for nnode in dnode.getElementsByTagName("node"):
                attrs = dict((k, v) for k, v in nnode.attributes.items() if not (k == 'id' or k == 'class'))
                klass = getattr(mod, nnode.getAttribute('class'))
                self.add_node(nnode.getAttribute("id"), klass, attrs)
        # create connections
        for dnode in cdom.getElementsByTagName("connection"):
            self.add_connection(dnode.getAttribute('source'), 
                                dnode.getAttribute('field'), 
                                dnode.getAttribute('destination'))
        # finished, unlink
        cdom.unlink()

    def run(self):
        # configure
        self.initialize(self.CONFIGFILE)
        # run
        while True:
            min_wait = 1.0
            el = None
            try:
                # process the connections
                for el in self.conns:
                    self.log_debug("process %s" % repr(el))
                    el.update()
                    nu = el.source.secs_until_next_update()
                    if nu != 0:
                        min_wait = min(min_wait, el.source.secs_until_next_update())
                        #self.log_debug("min_wait is %.4f from %s" % (min_wait, repr(el.source)))
                # process chain ends
                for el in self.chain_ends:
                    self.log_debug("process %s" % repr(el))
                    el.update()
            except:
                self.log_exc("node %s process exception" % repr(el))
            # snooze
            time.sleep(min_wait)



if __name__ == "__main__":
    s = Supv()
    #import cProfile
    #cProfile.run('s.main()', 'profile.out')
    s.main()
