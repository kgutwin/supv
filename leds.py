#!/usr/bin/python

import nodes

class Led(nodes.Consumer):
    def __init__(self, name, **kwargs):
        nodes.Consumer.__init__(self, **kwargs)
        self.path = "/sys/class/leds/" + name + "/brightness"
    
    def do(self):
        # sum inputs
        brightness = 0
        for inp in self.inputs:
            brightness += int(self.inputs[inp].get())
        # output
        self.logger.debug("setting led %s to '%s'" % (self.path, str(brightness)))
        ofp = open(self.path, 'w')
        ofp.write(str(brightness))
        ofp.close()

