#!/usr/bin/env python

import pyrap.tables as pt
import optparse

def main(inms='',beVerbose=False):
        didWarn = False
        whatSkipped = {}
        t = pt.table(inms, ack=False)
        th = pt.table(t.getkeyword('HISTORY'), ack=False)
        colnames = th.colnames()
        nrows = th.nrows()
        print 'The HISTORY table in %s has %d rows' % (inms, nrows)
        for row in th:
                if row['APPLICATION'] == 'imager' or row['APPLICATION'] == 'OLAP' or row['APPLICATION'] == 'ms':
                        if beVerbose:
                                print '%s was run at time %f with parameters:' % (row['APPLICATION'],row['TIME'])
                                for r in row['APP_PARAMS']:
                                        print '\t%s' % (r)
                        else:
                                if not didWarn:
                                        print '(Skipping OLAP, imager, and ms rows, use -v to print them)'
                                        didWarn = True
                                if row['APPLICATION'] in whatSkipped:
                                        whatSkipped[row['APPLICATION']] += 1
                                else:
                                        whatSkipped[row['APPLICATION']] = 1
                else:
                        print '%s was run at time %f with parameters:' % (row['APPLICATION'],row['TIME'])
                        for r in row['APP_PARAMS']:
                                print '\t%s' % (r)
        print 'Overview of skipped rows:'
        for key in whatSkipped:
                print '\t%s:\tskipped %d times' % (key,whatSkipped[key])

opt = optparse.OptionParser()
opt.add_option('-i','--inms',help='Input MS [no default]',default='')
opt.add_option('-v','--verbose',help='Verbose? [default False]',default=False,action='store_true')
options, args = opt.parse_args()
main(inms=options.inms,beVerbose=options.verbose)
