#!/usr/bin/python

import re
import time

import nodes

class Grep(nodes.Producer,nodes.Consumer):
    """Filters text input for the specified regex, optionally inverting
    the search sense to include only nonmatching lines.
    """
    def __init__(self, regex, nonmatch="False", **kwargs):
        nodes.Producer.__init__(self, **kwargs)
        nodes.Consumer.__init__(self, **kwargs)
        self.re = re.compile(regex)
        self.nonmatch = self.bool(nonmatch)
        self.text = ""
        self.num_matches = 0

    def do(self):
        output = []
        self.num_matches = 0
        for inp in self.inputs:
            val = self.inputs[inp].get()
            if isinstance(val, list):
                lines = val
            elif isinstance(val, dict):
                lines = val.values()
            else:
                lines = val.split('\n')
            for line in lines:
                if (self.re.search(line) is not None) ^ self.nonmatch:
                    output.append(line)
                    self.num_matches += 1
        self.text = "\n".join(output)

class SearchReplace(nodes.Producer,nodes.Consumer):
    """Filters text input for the specified regex, optionally inverting
    the search sense to include only nonmatching lines.
    """
    def __init__(self, regex, replace, **kwargs):
        nodes.Producer.__init__(self, **kwargs)
        nodes.Consumer.__init__(self, **kwargs)
        self.re = re.compile(regex)
        self.replace = replace
        self.text = ""

    def do(self):
        output = []
        for inp in self.inputs:
            val = self.inputs[inp].get()
            if isinstance(val, list):
                lines = val
            elif isinstance(val, dict):
                lines = val.values()
            else:
                lines = val.split('\n')
            for line in lines:
                line = self.re.sub(self.replace,line)
                output.append(line)
        self.text = "\n".join(output)

class Parse(nodes.Producer,nodes.Consumer):
    """Parses input text and creates outputs with the specified formats.
    """
    pass

class RateOfChange(nodes.Producer,nodes.Consumer):
    """Applies the function (x_new - x_prev) / (time_elapsed) to the input.
    """
    def __init__(self, **kwargs):
        nodes.Producer.__init__(self, **kwargs)
        nodes.Consumer.__init__(self, **kwargs)
        self.prev_vals = {}
        self.last_do = time.time()

    def do(self):
        output = 0.0
        for inp in self.inputs:
            val = self.inputs[inp].get()
            val_prev = self.prev_vals.get(inp, 0.0)
            self.prev_vals[inp] = val
            delt = val - val_prev
            t = self.secs_since_last_do()
            rate = float(delt) / float(t)
            self.logger.debug("roc %f over %f is %f" % (delt, t, rate))
            output += rate
        self.output = output

class TruncLinear(nodes.Producer,nodes.Consumer):
    """Applies a linear transformation (slope, intercept) along with optional
    upper and lower truncations to the input.
    """
    def __init__(self, slope="1.0", intercept="0.0", maxout=None, minout=None, **kwargs):
        nodes.Producer.__init__(self, **kwargs)
        nodes.Consumer.__init__(self, **kwargs)
        self.slope = float(slope)
        self.intercept = float(intercept)
        self.maxout = maxout
        self.minout = minout
        if self.maxout is not None:
            self.maxout = float(self.maxout)
        if self.minout is not None:
            self.minout = float(self.minout)


    def do(self):
        # sum inputs
        inp = sum(self.inputs[i].get() for i in self.inputs)
        # apply linear function
        out = inp * self.slope + self.intercept
        # and max/min
        if self.maxout:
            out = min(out, self.maxout)
        if self.minout:
            out = max(out, self.minout)
        # output
        self.output = out
        self.logger.debug("transforming %f to %f" % (inp, out))
        
class Getitem(nodes.Producer,nodes.Consumer):
    """Retrieves the specified index or key from the input.
    """
    def __init__(self, item, **kwargs):
        nodes.Producer.__init__(self, **kwargs)
        nodes.Consumer.__init__(self, **kwargs)
        self.item = item

    def do(self):
        for inp in self.inputs:
            val = self.inputs[inp].get()
            try:
                try:
                    self.output = val[self.item]
                except IndexError:
                    self.output = val[int(self.item)]
            except KeyError:
                raise KeyError("could not find %s in %s" % (repr(self.item), repr(val.keys())))


