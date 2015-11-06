#!/usr/bin/python

import numpy
import pyrap.tables as pt
import sys

msname = str(sys.argv[1])

cliplevelhba = 5.0
cliplevellba = 50.0

t = pt.table(msname, readonly=False)
data = t.getcol('MODEL_DATA')
flag = t.getcol('FLAG')
freq_tab= pt.table(msname + '/SPECTRAL_WINDOW')
freq    = freq_tab.getcol('REF_FREQUENCY')

if freq[0] > 100e6:
 cliplevel = cliplevelhba
if freq[0] < 100e6:
 cliplevel = cliplevellba

idx1 = numpy.where(flag[:,:,0] == True)
idx2 = numpy.where(flag[:,:,3] == True)

print '------------------------------'
print 'SB Frequency [MHz]', freq[0]/1e6
print '% input XX flagged', 1e2*numpy.float(len(idx1[1]))/numpy.float(len(numpy.array(flag[:,:,0]).flat))
print '% input YY flagged', 1e2*numpy.float(len(idx2[1]))/numpy.float(len(numpy.array(flag[:,:,3]).flat))
print ''
print 'Cliplevel used [Jy]', cliplevel
print '\n\n'

for pol in range(0,len(data[0,0,:])):
 for chan in range(0,len(data[0,:,0])):
  print 'Doing polarization,chan', pol, chan
  idx = numpy.where(abs(data[:,chan,pol]) > cliplevel)
  flag[idx,chan,0] = True
  flag[idx,chan,1] = True
  flag[idx,chan,2] = True
  flag[idx,chan,3] = True 

idx1 = numpy.where(flag[:,:,0] == True)
idx2 = numpy.where(flag[:,:,3] == True)
print ''
print '% output XX flagged', 1e2*numpy.float(len(idx1[1]))/numpy.float(len(numpy.array(flag[:,:,0]).flat))
print '% output YY flagged', 1e2*numpy.float(len(idx2[1]))/numpy.float(len(numpy.array(flag[:,:,3]).flat))
print ''
t.putcol('FLAG', flag)
t.close()
freq_tab.close()
