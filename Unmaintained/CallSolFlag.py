#! /usr/bin/env python

"""
Flag all the data in the CORRECTED_DATA column above a certain limit

"""

__version__ = '0.1'

from optparse import OptionParser
from pyrap.tables import table
import sys
import numpy

def parse_options(args=None, nargs=[], usage_message=''):
    parser = OptionParser(usage="%prog [options] <MS in file>  <MS out file> -i # -e #", version="%prog " + __version__)
    parser.set_defaults(usage=False, limit=0)
    parser.add_option("--usage", action='store_true',
                      help="show extended usage message")
    parser.add_option("-l", "--limit", type='int',
                      help="Start keeping data from this timeslot")
    (options, args) = parser.parse_args(args=args)
    optdict = {}
    for key in parser.defaults.keys():
        optdict[key] = eval("options.%s" % key)
    if len(nargs) > 0:
        if len(args) not in nargs:
            parser.error('Incorrect number of arguments')
    return args, optdict

# flag everything above the limit
def solflag(input, limit):	
    try:
        t = table(input,readonly=False)
    except Exception, e:
        print str(e)
        raise
    try:
        for i, data in enumerate(t.getcol('CORRECTED_DATA')):
            if max([abs(val) for val in data[0]]) > limit:
                t.putcell('FLAG', i, numpy.array([[True, True, True,True]]))
                t.putcell('FLAG_ROW', i, True)
        t.close()
    except Exception, e:
        print str(e)
        raise

def run(args, options):
    solflag(args[0], options['limit'])

def main():
    return run(*parse_options(nargs=[1]))

if __name__ == '__main__':
    sys.exit(main())
