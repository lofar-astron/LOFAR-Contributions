#!/usr/bin/env python

import sys
import numpy
import pyrap.measures as pm
import pyrap.tables as pt
import pyrap.quanta as qa
import pylab

if len(sys.argv) != 2:
        print 'Error: I need an MS name'
        exit(1)

me = pm.measures()
t = pt.table(sys.argv[1])
timevals = t.getcol('TIME')
tb = pt.table(t.getkeyword('ANTENNA'))
pos = tb.getcol('POSITION')
x = qa.quantity(pos[0,0],'m')
y = qa.quantity(pos[0,1],'m')
z = qa.quantity(pos[0,2],'m')
tb.close()
position = me.position('wgs84',x,y,z)
tb = pt.table(t.getkeyword('FIELD'))
direction = numpy.squeeze(tb.getcol('PHASE_DIR'))
tb.close()
t.close()
RA = qa.quantity(direction[0],'rad')
dec = qa.quantity(direction[1],'rad')
pointing = me.direction('j2000',RA,dec)
me.doframe(position)
el = numpy.zeros(len(timevals))
az = numpy.zeros(len(timevals))
for i in range(len(timevals)):
        tt = qa.quantity(timevals[i],'s')
        tt1 = me.epoch('utc',tt)
        me.doframe(tt1)
        a=me.measure(pointing,'azel')
        el[i]=a['m1']['value']
        az[i]=a['m0']['value']

pylab.plot(timevals-timevals.min(),el,'b',timevals-timevals.min(),az,'r')
pylab.legend(('elevation','azimuth'))
pylab.show()
