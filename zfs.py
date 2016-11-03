#!/usr/bin/python

import os
import subprocess

import nodes

class Zpool(nodes.Producer):
    FREQ = 2.0
    def __init__(self, **kwargs):
        nodes.Producer.__init__(self, **kwargs)
        self.text = ""
        self.pools = {}
        self.state = {}
        self.devices = {}
        self.components = {}
        self.errors = {}
        self.pathmap = {}
        for p in os.listdir('/dev/disk/by-path'):
            b = os.path.basename(os.path.realpath(os.path.join('/dev/disk/by-path',p)))
            self.pathmap[b] = p

    def do(self):
        #self.logger.debug("getting zpool status")
        p = subprocess.Popen(["zpool","status"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # and parse
        self.text = ""
        self.devices = {}
        pool = None
        for line in p.stdout:
            l = line.split()
            self.text += line
            if len(l) == 0:
                continue
            if l[0] == "pool:":
                pool = l[1]
                self.pools[pool] = []
            elif l[0] == "state:":
                self.state[pool] = l[1]
            elif l[0] == "errors:":
                self.errors[pool] = line[8:].strip()
            elif l[0] == "config:":
                # skip two lines
                self.text += p.stdout.next()
                self.text += p.stdout.next()
                # and read until blank
                for line in p.stdout:
                    self.text += line
                    l = line.split()
                    if len(l) == 0:
                        break
                    else:
                        self.pools[pool].append(l[0])
                        self.components[l[0]] = tuple(l[1:])
                        # and try to track down the actual physical device
                        d = os.path.join('/dev', l[0])
                        if os.path.exists(d):
                            # normalize
                            d = os.path.realpath(d)
                            # get name
                            b = os.path.basename(d)
                            # look in sys
                            d = '/sys/block/' + b + "/slaves"
                            for phys in os.listdir(d):
                                self.devices.setdefault(phys,[]).append(l[1])
                                if phys in self.pathmap:
                                    self.devices[self.pathmap[phys]] = self.devices[phys]

