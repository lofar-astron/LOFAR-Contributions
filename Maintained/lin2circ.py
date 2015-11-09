#!/usr/bin/env python

#
# Written by George Heald, heald@astron.nl, November 2010, Version 1.0
#




"""
lin2circ.py
Converts linear XX,XY,YX,YY correlations to circular RR,RL,LR,LL
assuming that the definitions follow the IAU ones, which are
described by Hamaker & Bregman (1996, A&AS, 117, 161).

In particular, I use the coordinate transformation given in Section 3,

          1     /  1   +i  \ 
C_A =  -------  |          |
       sqrt(2)  \  1   -i  /


The Hermitian conjugate of this is,

           1     /   1   1  \ 
C+_A =  -------  |          |
        sqrt(2)  \  -i  +i  /

So V_RL = C_A * V_XY * C+_A

where V_XY is the visibilities in linear coordinates,
      V_RL is the visibilities in circular coordinates.

This reduces to:

RR = XX - iXY + iYX + YY
RL = XX + iXY + iYX - YY
LR = XX - iXY - iYX - YY
LL = XX + iXY - iYX + YY

Version 1.0 written 15 April 2010 by George Heald
"""

import optparse
import pyrap.tables as pt
import numpy

def main(options):

        cI = numpy.complex(0.,1.)

        inms = options.inms
        if inms == '':
                print 'Error: you have to specify an input MS, use -h for help'
                return
        column = options.column
        outcol = options.outcol

        t = pt.table(inms, readonly=False, ack=True)
        if outcol not in t.colnames():
                print 'Adding output column',outcol,'to',inms
                coldmi = t.getdminfo(column)
                coldmi['NAME'] = outcol
                t.addcols(pt.maketabdesc(pt.makearrcoldesc(outcol, 0., valuetype='complex', shape=numpy.array(t.getcell(column,0)).shape)), coldmi)
        print 'Reading input column'
        data = t.getcol(column)
        print 'Computing output column'
        outdata = numpy.transpose(numpy.array([
                data[:,:,0]-cI*data[:,:,1]+cI*data[:,:,2]+data[:,:,3],
                data[:,:,0]+cI*data[:,:,1]+cI*data[:,:,2]-data[:,:,3],
                data[:,:,0]-cI*data[:,:,1]-cI*data[:,:,2]-data[:,:,3],
                data[:,:,0]+cI*data[:,:,1]-cI*data[:,:,2]+data[:,:,3]]),
                (1,2,0))
        print 'Finishing up'
        t.putcol(outcol, outdata)


opt = optparse.OptionParser()
opt.add_option('-i','--inms',help='Input MS [no default]',default='')
opt.add_option('-c','--column',help='Input column [default DATA]',default='DATA')
opt.add_option('-o','--outcol',help='Output column [default DATA_CIRC]',default='DATA_CIRC')
options, arguments = opt.parse_args()
main(options)

