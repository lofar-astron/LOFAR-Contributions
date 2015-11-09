
import numpy
import pylab as lb
import pyrap.tables as pt
import sys
import ctypes,math
import coordinates_mode as co
from numpy import *
from scipy import *

path = './inputs/'

#This script allows plotting of amplitude/phase vs time/uvdist/elevation with complete flagging.
#Can plot polarisations XX, YY, YX,XY.

# customizations
yaxis='a'     #Options 'a' or 'p'
xaxis='time'  #Options time,elevation,uvdist
data_name = "DATA"
pol=0
start_chan=0
end_chan=14
RAdeg=123.40025 #phase centre RA,DEC in degrees. Needed for elevation calculation
DECdeg=48.2179139

#Open table
t=pt.table(sys.argv[1])

def amp_phase(antenna1,antenna2):

        mampl=[]
        mphase=[]
        elevation=[]
        uvdist=[]
	time_hr=[]
	t2=t.query('ANTENNA1= '+str(antenna1) +' '+'AND ANTENNA2= '+str(antenna2))

	datapoint=0
	noflags=0
	flag=t2.getcolslice("FLAG", [start_chan,pol], [end_chan,pol])
	ampl = numpy.absolute (t2.getcolslice(data_name, [start_chan,pol], [end_chan,pol]))

	phase = t2.getcolslice(data_name, [start_chan,pol], [end_chan,pol])

	time=t2.getcol("TIME")
	timed = time/(24*3600) #Convert MJD in seconds to days
	timehr=(timed-timed[0])*24 #Hours since observation start
	uvw=t2.getcol("UVW")
	ant1=t2.getcell("ANTENNA1",0)
	ant2=t2.getcell("ANTENNA2",0)
	print 'Baseline = '+str(ant1)+' ' +str(ant2)
	print '***FLAG ANALYSIS***'
		   
	for x in range(len(time)):             
            atotal=0
	    ptotal=0+0j
	    count=0

	    altaz=co.altaz(time[x].item(),123.40025,48.2179139) #Calculate corresponding elevation
	    alt=altaz[0]
	    elevation.append(alt)

	    tmpuvw=uvw[x]                                    #Calculate uv distance
	    uvdist_1=sqrt((tmpuvw[0]**2)+(tmpuvw[1]**2))
	    uvdist.append(uvdist_1)
	    time_hr.append(timehr[x])
	    tmpflag=flag[x]  #Create temporary array for DATA and FLAG in each row, each 1x no of channels in dimension 
	    tmpamp=ampl[x]
	    tmpphase=phase[x]
			   
	    for i in range(0, end_chan):         #If tmpflag=true, set corresponding absolute amplitude data value to 0, and exclude from mean calculation.
                if tmpflag[i]:
                    noflags=noflags+1
		    datapoint=datapoint+1
		else:  
                    atest=tmpamp[i].item()
		    atotal=atest+atotal 
		    ptest=tmpphase[i].item()
		    ptotal=ptest+ptotal 
		    count=count+1
		    datapoint=datapoint+1
			  
	    if (count !=0):
                aspectral_mean=atotal/count
		pspectral_mean=ptotal/count
		mampl.append(aspectral_mean)
		phase_element=arctan2(pspectral_mean.imag,pspectral_mean.real)#%(2*pi)
		mphase.append(phase_element)

	    else: 
                mampl.append(nan)
		mphase.append(nan)
		
	print 'Total number of datapoints = '+str(datapoint)
	print 'Total number of flags = '+str(noflags)
	percentage=(float(noflags)/float(datapoint))*100
	print 'Percentage baseline flagged for correlation '+str(pol)+' = '+str(percentage)+'%'
	return mampl,mphase,time_hr,uvdist,elevation

		 
lb.figure(1)
lb.figure(2)
lb.figure(3)
lb.figure(4)
lb.figure(5)
lb.figure(6)
lb.clf()
       

for t2 in t.iter(["ANTENNA1","ANTENNA2"]):  
	ant1=t2.getcell("ANTENNA1",0)
	ant2=t2.getcell("ANTENNA2",0)
	mampl,mphase,time_hr,uvdist,elevation=amp_phase(ant1,ant2)
	if ant1!=ant2:            #Optional exclusion of autocorrelations
	#if yaxis=='a':
		titlestring = "Amplitude" 
		ylabelstring = "Amplitude"	
		lb.figure(1)
		xlabelstring="Elevation/degrees"
		lb.title("Amplitude vs Elevation for "+sys.argv[1]+" Correlation= "+str(pol))
		lb.xlabel(xlabelstring)
		lb.ylabel(ylabelstring)
		lb.plot(elevation,mampl,',')
		lb.figure(2)	
		xlabelstring="Time Since Obs Start/hours"
		lb.title("Amplitude vs Time Since Obs Start for "+sys.argv[1]+" Correlation= "+str(pol))
		lb.xlabel(xlabelstring)
		lb.ylabel(ylabelstring)
		lb.plot(time_hr,mampl,',')

		lb.figure(3)
		xlabelstring="UV distance"
		lb.title("Amplitude vs Elevation for "+sys.argv[1]+"Correlation= "+str(pol))
		lb.ylabel(ylabelstring)
		lb.xlabel(xlabelstring)
		lb.plot(uvdist,mampl,',')

#	elif yaxis=='p':
	        ylabelstring="Phase/radians"	
		lb.figure(4)
		xlabelstring="Elevation/degrees"
		lb.title("Phase vs Elevation for "+sys.argv[1]+" Correlation= "+str(pol))
		lb.xlabel(xlabelstring)
		lb.ylabel(ylabelstring)
		lb.plot(elevation,mphase,',')
		lb.figure(5)	
		xlabelstring="Time Since Obs Start/hours"
		lb.title("Phase vs Time Since Obs Start for "+sys.argv[1]+" Correlation= "+str(pol))
		lb.xlabel(xlabelstring)
		lb.ylabel(ylabelstring)
		lb.plot(time_hr,mphase,',')

		lb.figure(6)
		xlabelstring="UV distance"
		lb.title("Phase vs Elevation for "+sys.argv[1]+" Correlation= "+str(pol))
		lb.ylabel(ylabelstring)
		lb.xlabel(xlabelstring)
		lb.plot(uvdist,mphase,',')

		
	   	   
lb.show()
