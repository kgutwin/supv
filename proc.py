#!/usr/bin/python

import os
import os.path

import nodes

class Diskstats(nodes.Producer):
    FREQ = 0.1
    def __init__(self, **kwargs):
        nodes.Producer.__init__(self, **kwargs)

    def do(self):
        fp = open('/proc/diskstats','r')
        for line in fp:
            l = line.split()[2:]
            dev = l[0]
            fields = { 'r-num'     : int(l[1]),
                       'r-merged'  : int(l[2]),
                       'r-sects'   : int(l[3]),
                       'r-ms'      : int(l[4]),
                       'w-num'     : int(l[5]),
                       'w-merged'  : int(l[6]),
                       'w-sects'   : int(l[7]),
                       'w-ms'      : int(l[8]),
                       'inprogress': int(l[9]),
                       'io-ms'     : int(l[10]),
                       'io-ms-wt'  : int(l[11]),
                       }
                       
            setattr(self, dev, fields)
        # map entries in /dev/disk/by-path
        for p in os.listdir('/dev/disk/by-path'):
            f = os.readlink(os.path.join('/dev/disk/by-path', p))
            dev = os.path.basename(f)
            if hasattr(self, dev):
                setattr(self, p, getattr(self, dev, fields))

