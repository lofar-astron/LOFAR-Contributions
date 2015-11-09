#!/usr/bin/env python

import pyrap.tables as tables
import sys

def repair_ms(msname):
    tab=tables.table(msname, readonly=False)
    measinfo=tab.getcolkeyword('UVW', 'MEASINFO')
    measinfo['Ref']='J2000'
    tab.putcolkeyword('UVW', 'MEASINFO', measinfo)
    tab.close()
    pass




if __name__=='__main__':
    map(repair_ms, sys.argv[1:])
