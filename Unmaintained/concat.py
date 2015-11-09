#!/usr/bin/env python

import sys
from pyrap.tables import table

if __name__ == "__main__":
    print "Concatenate MeasurementSets\n"
    try:
        t = table(sys.argv[2:])
        t.sort('TIME').copy(sys.argv[1], deep = True)
    except:
        print "Usage: concat.py <output.MS> <input.MS> [input.MS] ..."
