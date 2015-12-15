#!/usr/bin/env python

"""
uvcov.py

This script is intended to provide a way to quickly plot uv coverage
for LOFAR datasets. It uses pyrap and ppgplot (numpy version).

If you use postscript device output, you may want to use 'embiggen.csh'
(located at /home/heald/bin/embiggen.csh) which makes the pointsizes bigger.

If you want square plots, you have to modify environment variables:
PGPLOT_PS_WIDTH
PGPLOT_PS_HEIGHT
Values of 7800 (equivalent to a physical size of 7.8 inches) work fine for me.

Written by George Heald
v1.0 completed 3/6/2010

10 June 2010  v1.1  Add choice to plot in kilolambda
 4 Aug  2010  v1.2  Add choice to assume same u,v in meters
10 Feb  2011  v1.3  Add option to specify title of plot
                    Add ability to plot broadband uv coverage from one MS
                    Allow antenna ranges instead of only lists (in -e)

To do:
- Fix antenna selection for plotting >1 MS

"""

import optparse
import glob
import signal
import sys
import ppgplot
# Note, for documentation on ppgplot, see
# http://www.astro.rug.nl/~breddels/python/ppgplot/ppgplot-doc.txt
import numpy
import pyrap.tables as pt

version_string = 'v1.3, 10 February 2011'
print 'uvcov.py',version_string
print ''

def main(options):

	debug = options.debug
        MSlist = []
        for inmspart in options.inms.split(','):
                for msname in glob.iglob(inmspart):
	                MSlist.append(msname)
	if len(MSlist) == 0:
		print 'Error: You must specify at least one MS name.'
		print '       Use "uvplot.py -h" to get help.'
		return
        if len(MSlist) > 1:
                print 'WARNING: Antenna selection (other than all) may not work well'
                print '         when plotting more than one MS. Carefully inspect the'
                print '         listings of antenna numbers/names!'
	device = options.device
	if device=='?':
		ppgplot.pgldev()
		return
        if options.title == '':
                plottitle = options.inms
        else:
                plottitle = options.title
	axlimits = options.axlimits.split(',')
	if len(axlimits) == 4:
		xmin,xmax,ymin,ymax = axlimits
	else:
		print 'Error: You must specify four axis limits'
		return
	timeslots = options.timeslots.split(',')
	if len(timeslots) != 3:
		print 'Error: Timeslots format is start,skip,end'
		return
	for i in range(len(timeslots)):
		timeslots[i] = int(timeslots[i])
		if timeslots[i] < 0:
			print 'Error: timeslots values must not be negative'
			return
        antToPlotSpl = options.antennas.split(',')
        antToPlot = []
        for i in range(len(antToPlotSpl)):
                tmpspl = antToPlotSpl[i].split('..')
                if len(tmpspl) == 1:
                        antToPlot.append(int(antToPlotSpl[i]))
                elif len(tmpspl) == 2:
                        for j in range(int(tmpspl[0]),int(tmpspl[1])+1):
                                antToPlot.append(j)
                else:
                        print 'Error: Could not understand antenna list.'
                        return
	queryMode = options.query
        plotLambda = options.kilolambda

        badval = 0.0
        xaxisvals = numpy.array([])
        yaxisvals = numpy.array([])
        savex = numpy.array([])
        savey = numpy.array([])
        numPlotted = 0
        for inputMS in MSlist:
	        # open the main table and print some info about the MS
                print 'Getting info for', inputMS
	        t = pt.table(inputMS, readonly=True, ack=False)
                tfreq = pt.table(t.getkeyword('SPECTRAL_WINDOW'),readonly=True,ack=False)
                ref_freq = tfreq.getcol('REF_FREQUENCY',nrow=1)[0]
                ch_freq = tfreq.getcol('CHAN_FREQ',nrow=1)[0]
                print 'Reference frequency:\t%f MHz' % (ref_freq/1.e6)
                if options.wideband:
                        ref_wavelength = 2.99792458e8/ch_freq
                else:
                        ref_wavelength = [2.99792458e8/ref_freq]
                print 'Reference wavelength:\t%f m' % (ref_wavelength[0])
                if options.sameuv and numPlotted > 0:
                        print 'Assuming same uvw as first MS!'
                        if plotLambda:
                                for w in ref_wavelength:
                                        xaxisvals = numpy.append(xaxisvals,[savex/w/1000.,-savex/w/1000.])
                                        yaxisvals = numpy.append(yaxisvals,[savey/w/1000.,-savey/w/1000.])
                        else:
                                print 'Plotting more than one MS with same uv, all in meters... do you want -k?'
                                xaxisvals = numpy.append(xaxisvals,[savex,-savex])
                                yaxisvals = numpy.append(yaxisvals,[savey,-savey])
                        continue
                        
	        firstTime = t.getcell("TIME", 0)
	        lastTime = t.getcell("TIME", t.nrows()-1)
	        intTime = t.getcell("INTERVAL", 0)
	        print 'Integration time:\t%f sec' % (intTime)
	        nTimeslots = (lastTime - firstTime) / intTime
	        print 'Number of timeslots:\t%d' % (nTimeslots)
                if timeslots[1] == 0:
                        if nTimeslots >= 100:
                                timeskip = int(nTimeslots/100)
                        else:
                                timeskip = 1
                else:
                        timeskip = int(timeslots[1])
                print 'For each baseline, plotting one point every %d samples' % (timeskip)
       	        if timeslots[2] == 0:
        		timeslots[2] = nTimeslots
        	# open the antenna subtable
        	tant = pt.table(t.getkeyword('ANTENNA'), readonly=True, ack=False)
        
        	# Station names
        	antList = tant.getcol('NAME')
                if len(antToPlot)==1 and antToPlot[0]==-1:
                        antToPlot = range(len(antList))
        	print 'Station list (only starred stations will be plotted):'
        	for i in range(len(antList)):
                        star = ' '
                        if i in antToPlot: star = '*'
        		print '%s %2d\t%s' % (star, i, antList[i])
        
        	# Bail if we're in query mode
        	if queryMode:
        		return
        
        	# select by time from the beginning, and only use specified antennas
        	tsel = t.query('TIME >= %f AND TIME <= %f AND ANTENNA1 IN %s AND ANTENNA2 IN %s' % (firstTime+timeslots[0]*intTime,firstTime+timeslots[2]*intTime,str(antToPlot),str(antToPlot)), columns='ANTENNA1,ANTENNA2,UVW')

        	# Now we loop through the baselines
                i = 0
                nb = (len(antToPlot)*(len(antToPlot)-1))/2
                sys.stdout.write('Reading uvw for %d baselines: %04d/%04d'%(nb,i,nb))
                sys.stdout.flush()
	        for tpart in tsel.iter(["ANTENNA1","ANTENNA2"]):
        		ant1 = tpart.getcell("ANTENNA1", 0)
        		ant2 = tpart.getcell("ANTENNA2", 0)
                        if ant1 not in antToPlot or ant2 not in antToPlot: continue
        		if ant1 == ant2: continue
                        i += 1
                        sys.stdout.write('\b\b\b\b\b\b\b\b\b%04d/%04d'%(i,nb))
                        sys.stdout.flush()
        		# Get the values to plot
                        uvw = tpart.getcol('UVW', rowincr=timeskip)
                        if numPlotted == 0:
                                savex = numpy.append(savex,[uvw[:,0],-uvw[:,0]])
                                savey = numpy.append(savey,[uvw[:,1],-uvw[:,1]])
                        if plotLambda:
                                for w in ref_wavelength:
                                        xaxisvals = numpy.append(xaxisvals,[uvw[:,0]/w/1000.,-uvw[:,0]/w/1000.])
                                        yaxisvals = numpy.append(yaxisvals,[uvw[:,1]/w/1000.,-uvw[:,1]/w/1000.])
                        else:
                                xaxisvals = numpy.append(xaxisvals,[uvw[:,0],-uvw[:,0]])
                                yaxisvals = numpy.append(yaxisvals,[uvw[:,1],-uvw[:,1]])
        		#if debug:
                        #        print uvw.shape
        		#	print xaxisvals.shape
        		#	print yaxisvals.shape
                        #else:
                        #        sys.stdout.write('.')
                        #        sys.stdout.flush()
                sys.stdout.write(' Done!\n')
                numPlotted += 1

        print 'Plotting uv points ...'
	# open the graphics device, using only one panel
	ppgplot.pgbeg(device, 1, 1)
	# set the font size
	ppgplot.pgsch(1)
	ppgplot.pgvstd()

	# Plot the data
        if debug:
                print xaxisvals
        xaxisvals = numpy.array(xaxisvals)
        yaxisvals = numpy.array(yaxisvals)
        tmpvals = numpy.sqrt(xaxisvals**2+yaxisvals**2)
	ppgplot.pgsci(1)
        uvmax = max(xaxisvals.max(),yaxisvals.max())
        uvmin = min(xaxisvals.min(),yaxisvals.min())
        uvuplim = 0.02*(uvmax-uvmin)+uvmax
        uvlolim = uvmin-0.02*(uvmax-uvmin)
	if xmin == '':
		minx = uvlolim
	else:
		minx = float(xmin)
	if xmax == '':
		maxx = uvuplim
	else:
		maxx = float(xmax)
	if ymin == '':
		miny = uvlolim
	else:
		miny = float(ymin)
	if ymax == '':
		maxy = uvuplim
	else:
		maxy = float(ymax)
	if minx == maxx:
		minx = -1.0
		maxx = 1.0
	if miny == maxy:
		miny = -1.0
		maxy = 1.0
        ppgplot.pgpage()
	ppgplot.pgswin(minx,maxx,miny,maxy)
        ppgplot.pgbox('BCNST',0.0,0,'BCNST',0.0,0)
        if plotLambda:
	        ppgplot.pglab('u [k\gl]', 'v [k\gl]', '%s'%(plottitle))
        else:
	        ppgplot.pglab('u [m]', 'v [m]', '%s'%(plottitle))
	ppgplot.pgpt(xaxisvals[tmpvals!=badval], yaxisvals[tmpvals!=badval], 1)

	# Close the PGPLOT device
	ppgplot.pgclos()
		

def signal_handler(signal, frame):
        sys.exit(0)

opt = optparse.OptionParser()
opt.add_option('-i','--inms',help='Input MS(s) to plot [no default]. Multiple MS names can be given together, separated by commas. Wildcards are also accepted in order to make it easier to plot more than one MS at a time.',default='')
opt.add_option('-d','--device',help='PGPLOT device to use for the plotting [default /xs], for options use the string "?"',default='/xs')
opt.add_option('-a','--axlimits',help='Axis limits (comma separated in order: xmin,xmax,ymin,ymax), leave any of them blank to use data min/max [default ",,,"]',default=',,,')
opt.add_option('-t','--timeslots',help='Timeslots to use (comma separated and zero-based: start,skip,end) [default 0,0,0 = full time range, skipping such that 100 points are plotted per baseline]',default='0,0,0')
opt.add_option('-e','--antennas',help='Antennas to use (comma separated list, zero-based) [default -1=all] Use -q to see a list of available antennas. Only antennas in this list are plotted. When plotting more than one MS this may not work well. To specify an inclusive range of antennas use .. format, e.g. -e 0..9 requests the first 10 antennas.',default='-1',type='string')
opt.add_option('-k','--kilolambda',help='Plot in kilolambda rather than meters? [default False]',default=False,action='store_true')
opt.add_option('-w','--wideband',help='Plot each channel separately? Only useful with -k. [default False]',default=False,action='store_true')
opt.add_option('-s','--sameuv',help='Assume same uv coordinates (in meters) for multiple MSs? This is useful if all input MSs are SBs of a single observation. It is NOT useful when combining MSs from different timeranges. [default False]',default=False,action='store_true')
opt.add_option('--title',help="Plot title [default ''=MS name] If you need no title at all, use --title=' '",default='')
opt.add_option('-b','--debug',help='Run in debug mode? [default False]',default=False,action='store_true')
opt.add_option('-q','--query',help='Query mode (quits after reading dimensions, use for unfamiliar MSs) [default False]',default=False,action='store_true')
options, arguments = opt.parse_args()

signal.signal(signal.SIGINT, signal_handler)

main(options)
