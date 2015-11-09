import numpy
import pylab
import pyrap.tables as pt
import sys
import coordinates_mode as co
from numpy import *
from scipy import *



#This script flags all autocorrelations in a measurement set. ** Be sure to copy original MS first, as the flagging of the autocorrelations cannot be undone!


#Open table
t=pt.table('SB27_FLG_7HR_CC.MS',readonly=False)
start_chan=0
end_chan=14

pylab.figure(None)
pylab.clf()

#For all the times with each antenna pair (baseline) do this: 
for t2 in t.iter(["ANTENNA1","ANTENNA2"]):

       flag=t2.getcol("FLAG")
       test=t2.getcolshapestring("FLAG",0,-1,1)
       print test[1]
       
       ant1=t2.getcell("ANTENNA1",0)
       ant2=t2.getcell("ANTENNA2",0)
       print 'Baseline = '+str(ant1)+' ' +str(ant2)
       count=0
       flagarray=ones([15,4],dtype='bool')
       #print flagarray
       print flag[1].shape
#For all rows with antenna pair t2.
		   
       for x in range(len(flag)):
           if ant1==ant2:
               t2.putcell(columnname="FLAG",rownr=x,value=flagarray)
               count=count+1

		
print 'Flagging of Autocorrelations Complete'
