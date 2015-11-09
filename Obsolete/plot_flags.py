#! /usr/bin/env python
"""
Plots visibility amplitudes as channel vs. time slot with flags overlaid.

Usage: plot_flags.py [options] <measurement set>

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s station, --station=station
                        plot baselines to this station only (index or name)
  -c CORR, --corr=CORR  correlation to plot (xx, xy, yx, yy); default = xx
  -d                    plot CORRECTED_DATA instead of DATA
  -l                    plot using log scale
  -m                    scale plot using Min Max

Written by David Rafferty (rafferty@strw.leidenuniv.nl)
"""

import pyrap.tables as pt
import numpy
import sys
import pylab
import os
from matplotlib.colors import LogNorm


def plot_baseline_time(station2_selection, minmax=False, plot_cordata=False, logplot=False):
    """
    Loads data and plots baseline vs. time for single-channel data.
    """
    global ms
    global corr
    global im_flag
    global im_noflag
    global plot_array
    pylab.clf()
    gray_palette1 = pylab.cm.gray
    gray_palette2 = pylab.cm.gray
    gray_palette1.set_bad('r', alpha=alpha) # show flagged points in red
    gray_palette2.set_bad('r', alpha=alpha) # show flagged points in red

    print 'Plotting baseline vs. time for all baselines...'
    ms_filtered = ms.query("ANTENNA1 in " + str(station2_selection) + " && ANTENNA2 in " + str(station2_selection), sortlist="TIME,ANTENNA1,ANTENNA2")
    if plot_cordata:
        data = ms_filtered.getcol("CORRECTED_DATA")
    else:
        data = ms_filtered.getcol("DATA")
    if data == None or numpy.max(data) <= 0.0:
        print '  ERROR: no data found.'
        return False

    flags = ms_filtered.getcol("FLAG")
    plot_array = numpy.zeros((Nc,Nb,Nt),dtype=float)
    flags_array = numpy.zeros((Nc,Nb,Nt),dtype=float)
    for i in range(0,Nt): # step through each time slot
        for j in range(0,Nc): # step through each channel
            plot_array[j,:,i]= numpy.absolute(data[i*Nb:(i+1)*Nb,j,corr_indx])
            if flags != None:
                flags_array[j,:,i]= flags[i*Nb:(i+1)*Nb,j,0]
    masked_plot_array = numpy.ma.masked_where(flags_array == True, plot_array)

    # Estimate limits for the color stretch
    if minmax == True:
        min_estimate = numpy.min(plot_array[0,:,:])
        if min_estimate == 0.0:
            min_estimate = 1E-5
        max_estimate = numpy.max(plot_array[0,:,:])
    else:
        medamp = numpy.median(plot_array[0,:,:])
        min_estimate=medamp/3.0
        max_estimate=medamp*3.0

    if logplot:
        im_flag = pylab.imshow(masked_plot_array[0,:,:], cmap=gray_palette1, origin='lower', aspect='auto', norm=LogNorm(vmin=min_estimate, vmax=max_estimate), interpolation='nearest')
        im_noflag = pylab.imshow(plot_array[0,:,:], cmap=gray_palette2, origin='lower', aspect='auto', norm=LogNorm(vmin=min_estimate, vmax=max_estimate), interpolation='nearest', hold=True)
        im_noflag.set_visible(False)
    else:
        im_flag = pylab.imshow(masked_plot_array[0,:,:], cmap=gray_palette1, origin='lower', aspect='auto', vmin=min_estimate, vmax=max_estimate, interpolation='nearest')
        im_noflag = pylab.imshow(plot_array[0,:,:], cmap=gray_palette2, origin='lower', aspect='auto', vmin=min_estimate, vmax=max_estimate, interpolation='nearest', hold=True)
        im_noflag.set_visible(False)
    
    pylab.title('Visibility Amplitudes ('+corr+') for All Baselines')
    pylab.xlabel('Time Slot')
    pylab.ylabel('Baseline')
    pylab.colorbar()
    pylab.draw()
    return True

def plot_channel_time(station1, station2, minmax=False, plot_cordata=False, logplot=False):
    """
    Loads data and plots channel vs. time for a baseline.
    """
    global ms
    global im_flag
    global im_noflag
    global antList
    global corr
    global last_time_to_plot
    global plot_array
    pylab.clf()
    gray_palette1 = pylab.cm.gray
    gray_palette2 = pylab.cm.gray
    gray_palette1.set_bad('r', alpha=alpha) # show flagged points in red
    gray_palette2.set_bad('r', alpha=alpha) # show flagged points in red

    print 'Reading data...'
    if station2 > station1:
        if last_time_to_plot == None:
            ms_filtered = ms.query("ANTENNA1 in " + str(station1) + " && ANTENNA2 in " + str(station2), sortlist="TIME,ANTENNA1,ANTENNA2")
        else:
            ms_filtered = ms.query("ANTENNA1 in " + str(station1) + " && ANTENNA2 in " + str(station2) + " && TIME <= " +str(last_time_to_plot), sortlist="TIME,ANTENNA1,ANTENNA2")
    else:
        if last_time_to_plot == None:
            ms_filtered = ms.query("ANTENNA1 in " + str(station2) + " && ANTENNA2 in " + str(station1), sortlist="TIME,ANTENNA1,ANTENNA2")
        else:
            ms_filtered = ms.query("ANTENNA1 in " + str(station2) + " && ANTENNA2 in " + str(station1) + " && TIME <= " +str(last_time_to_plot), sortlist="TIME,ANTENNA1,ANTENNA2")

    flags = ms_filtered.getcol("FLAG")
    if flags == None:
        flags_array = numpy.zeros((Nt, Nc), dtype=bool)
    else:
        flags_array = numpy.transpose(flags[:,:,corr_indx])
    perc_flag = float(numpy.size(numpy.where(flags_array == True), 1)) / float(numpy.size(flags_array)) * 100.0
    if flags_array.all() == True:
        print '  Skipped '+antList[station1]+'-'+antList[station2]+' (100% of points flagged)'
        return False
    else:
        if plot_cordata:
            data = ms_filtered.getcol("CORRECTED_DATA")
        else:
            data = ms_filtered.getcol("DATA")

        if data == None or numpy.max(data) <= 0.0:
            print '  Skipped '+antList[station1]+'-'+antList[station2]+' (no data found)'
            return False
           
        plot_array = numpy.transpose(numpy.absolute(data[:,:,corr_indx]))
        masked_plot_array = numpy.ma.masked_where(flags_array == True, plot_array)

        # Estimate limits for the color stretch
        if Nt > 1000:
            maxNt = 500
        else:
            maxNt = int(Nt/2.0)

        if minmax == True:
            min_estimate = numpy.min(plot_array[0:maxNt,0:int(Nc/4.0)])
            max_estimate = numpy.max(plot_array[0:maxNt,0:int(Nc/4.0)])
            # If this quick estimate doesn't work, try to use the whole array
            if max_estimate == 0.0 or numpy.isfinite(min_estimate) or numpy.isfinite(max_estimate) == False:
                min_estimate = numpy.min(plot_array)
                max_estimate = numpy.max(plot_array)
            if min_estimate == 0.0:
                min_estimate = 1E-5
        else:
            medamp = numpy.median(plot_array[0:maxNt,0:int(Nc/4.0)])
            # If this quick median doesn't work, try to use the whole array
            if medamp == 0.0 or numpy.isfinite(medamp) == False:
                medamp = numpy.median(plot_array)
            min_estimate=medamp/3.0
            max_estimate=medamp*3.0

        if logplot:
            im_flag = pylab.imshow(masked_plot_array, cmap=gray_palette1, origin='lower', aspect='auto', norm=LogNorm(vmin=min_estimate, vmax=max_estimate), interpolation='nearest')
            im_noflag = pylab.imshow(plot_array, cmap=gray_palette2, origin='lower', aspect='auto', norm=LogNorm(vmin=min_estimate, vmax=max_estimate), interpolation='nearest', hold=True)
            im_noflag.set_visible(False)
        else:
            im_flag = pylab.imshow(masked_plot_array, cmap=gray_palette1, origin='lower', aspect='auto', vmin=min_estimate, vmax=max_estimate, interpolation='nearest')
            im_noflag = pylab.imshow(plot_array, cmap=gray_palette2, origin='lower', aspect='auto', vmin=min_estimate, vmax=max_estimate, interpolation='nearest', hold=True)
            im_noflag.set_visible(False)

        pylab.title('Visibility Amplitudes ('+corr+') for Baseline '+antList[station1]+'-'+antList[station2])
        pylab.xlabel('Time Slot')
        pylab.ylabel('Channel')                            
        pylab.colorbar()
        pylab.draw()
        print "  Plotted "+antList[station1]+'-'+antList[station2]+' (%4.2f%% of points flagged)' % (perc_flag,)
        return True

def on_click_one_channel(event):
    """
    Prints location and visibility amplitude
    """
    global ms
    global plot_array
    global antList
    tb = pylab.get_current_fig_manager().toolbar
    if event.button == 1 and event.inaxes and tb.mode == '':
        time_indx = int(round(event.xdata, 0))
        base_indx = int(round(event.ydata, 0))
        base_name = get_baseline_name(base_indx, antList)
        print '  Clicked point: time slot = %i, baseline = %s, amplitude = %f' % (time_indx+1, base_name, plot_array[0,base_indx, time_indx])

def get_baseline_name(indx, antList):
    """
    Returns the names of the stations that make up the baseline with the given index.
    """
    baseline_names = []
    for a in range(len(antList)):
        for b in range(a, len(antList)):
            baseline_names.append(antList[a]+'-'+antList[b])
    return baseline_names[indx]
    
def on_press_one_channel(event):
    """
    Toggles flags
    """
    global im_flag
    global im_noflag
    if event.key != 'f' and event.key != 'q': return
    if event.key == 'f':
        b1 = im_flag.get_visible()
        b2 = im_noflag.get_visible()
        im_flag.set_visible(not b1)
        im_noflag.set_visible(not b2)
        pylab.draw()
    if event.key == 'q':
        ms.close()
        print '...done.'
        sys.exit()
      
def on_click_multi_channel(event):
    """
    Toggles flags and advances to next baseline
    """
    global ms
    global plot_array
    global chan_freq
    tb = pylab.get_current_fig_manager().toolbar
    if event.button == 1 and event.inaxes and tb.mode == '':
        time_indx = int(round(event.xdata, 0))
        chan_indx = int(round(event.ydata, 0))
        print '  Clicked point: time slot = %i, channel = %i (%f MHz), amplitude = %f' % (time_indx+1, chan_indx+1, chan_freq[chan_indx]/1E6, plot_array[chan_indx, time_indx])

def on_press_multi_channel(event):
    """
    Prints location and visibility amplitude
    """
    global ms
    global station1
    global station2
    global station1_indx
    global station2_indx
    global station1_selection
    global station2_selection
    global logplot
    global minmax
    if event.key != 'f' and event.key != 'q' and event.key != 'n':
        return
    if event.key == 'f':
        b1 = im_flag.get_visible()
        b2 = im_noflag.get_visible()
        im_flag.set_visible(not b1)
        im_noflag.set_visible(not b2)
        pylab.draw()
    if event.key == 'n':
        # load next baseline and plot
        Ns1 = len(station1_selection)
        Ns2 = len(station2_selection)
        pres = False
        while pres == False:
            station2_indx += 1 # increment station 2
            if station2_indx == Ns2:
                station1_indx += 1
                station2_indx = station1_indx + 1 # reset station 2
            if station1_indx == Ns1:
                break
            else:
                station1 = station1_selection[station1_indx]
                station2 = station2_selection[station2_indx]
                pres = plot_channel_time(station1, station2, minmax=minmax, logplot=logplot)       
    if event.key == 'q':
        ms.close()
        print '...done.'
        sys.exit()
        
    
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options] <measurement set>', version="%prog 1.0")
    parser.add_option('-s', '--station', dest='station1', help='plot baselines to this station only (index or name)', metavar='station', default=None)
    parser.add_option('-c', '--corr', dest='corr', help='correlation to plot (xx, xy, yx, yy); default = xx', type='choice',choices=['xx', 'yy', 'xy', 'yx'], default='xx')
    parser.add_option('-d', action='store_true', dest='cdata', help='plot CORRECTED_DATA instead of DATA', default=False)
    parser.add_option('-l', action='store_true', dest='logplot', help='plot using log scale', default=False)
    parser.add_option('-m', action='store_true', dest='minmax', help='scale plot using Min Max', default=False)
    parser.add_option('-f', action='store_true', dest='force_all', help='force display of large datasets', default=False)
    (options, args) = parser.parse_args()
    if len(args) == 1:
        MeasurementSet = args[0]
        if os.path.isdir(MeasurementSet) == False:
            sys.exit('ERROR: Input Measurement Set "'+MeasurementSet+'" not found.')
        s1 = options.station1
        corr = options.corr
        if corr == 'xx': corr_indx = 0
        if corr == 'xy': corr_indx = 1
        if corr == 'yx': corr_indx = 2
        if corr == 'yy': corr_indx = 3
        plot_cordata = options.cdata
        logplot = options.logplot
        minmax = options.minmax
        force_all = options.force_all
        alpha = 1.0

        ms = pt.table(MeasurementSet, readonly=True, ack=False)
        tant = pt.table(ms.getkeyword('ANTENNA'), readonly=True, ack=False)
        antList = tant.getcol('NAME')
        Ns = len(antList)
        print '\nThe following stations were found (index - name):'
        for i in range(int(Ns/3.0)):
            print '  %2i - %s    %2i - %s    %2i - %s' % (i*3, antList[i*3].ljust(10), i*3+1, antList[i*3+1].ljust(10), i*3+2, antList[i*3+2].ljust(10))
        if numpy.mod(Ns, 3) == 2:
            print '  %2i - %s    %2i - %s' % (Ns-2, antList[Ns-2].ljust(10), Ns-1, antList[Ns-1].ljust(10))
        if numpy.mod(Ns, 3) == 1:
            print '  %2i - %s' % (Ns-1, antList[Ns-1].ljust(10))
        print ' '

        station2_selection = range(Ns)
        if s1 == None:
            station1_selection = range(Ns)
        else:
            if s1.isdigit():
                s1_indx = int(s1)
                if s1_indx < 0 or s1_indx > Ns:
                    sys.exit('ERROR: Station "'+str(s1_indx)+'" not found.')
                s1_name = antList[s1_indx]
            else:
                s1_name = s1
                s1_indx_search = numpy.where(numpy.array(antList) == s1_name)
                if len(s1_indx_search[0]) > 0:
                    s1_indx = s1_indx_search[0][0]
                else:
                    sys.exit('ERROR: Station "'+s1_name+'" not found.')
            station1_selection = [s1_indx]
        pylab.ion()


        #
        # Read number of baselines, time slots, and channels
        #
        nrows = ms.nrows()
        Nstat = len(station2_selection)
        Nb = (Nstat * (Nstat-1) / 2) + Nstat # number of baselines (includes autocorrelations)
        Nt = nrows / Nb # number of time slots (i.e. total num of rows/num of baselines)
        Nrows_to_plot = nrows
        tsp = pt.table(ms.getkeyword('SPECTRAL_WINDOW'), readonly=True, ack=False)
        Nc = tsp.getcell('NUM_CHAN',0)
        chan_freq = tsp.getcell('CHAN_FREQ',0)
        tob = pt.table(ms.getkeyword('OBSERVATION'), readonly=True, ack=False)
        t_start = tob.getcell('TIME_RANGE',0)[0]
        t_end = tob.getcell('TIME_RANGE',0)[1]
        time_per_slot = ms.getcell('INTERVAL',0)
            
        
        #
        # Plot channel vs. time or baseline vs. time
        #
        if Nc == 1: # when only one channel is present, just plot baseline vs time
            print '  ***********************************************'
            print '    NOTE - With mouse in plot window:            '
            print '    "f" = toggle flags                           '
            print '    "q" = quit                                   '
            print '    left click = print time, baseline, and amp   '
            print '                 ("zoom rect" mode must be off)  '
            print '  ***********************************************'
            print ''
            pres = plot_baseline_time(station2_selection, minmax=minmax, plot_cordata=plot_cordata, logplot=logplot)
            if pres == True:
                pylab.connect('key_press_event', on_press_one_channel)
                pylab.connect('button_press_event', on_click_one_channel)
            else:
                ms.close()
                print '...done.'
                sys.exit()
        else: # when multiple channels are present, plot channel vs time and loop over baselines
            if Nc * nrows / Nb > 1E6 and force_all == False:
                Nt_to_plot = 2500 
                last_time_to_plot = t_start + time_per_slot * Nt_to_plot
                print 'WARNING: Large measurement set. Plotting only the first %3.1f hours.' % (Nt_to_plot*time_per_slot/3600.0,)
                print '         Use "-f" to plot the entire time range.'
                print ''
            else:
                last_time_to_plot = None
            print '  ***********************************************'
            print '    NOTE - With mouse in plot window:     '
            print '    "f" = toggle flags                           '
            print '    "n" = continue to next baseline              '
            print '    "q" = quit                                   '
            print '    left click = print time, channel, and amp    '
            print '                 ("zoom rect" mode must be off)  '
            print '  ***********************************************'
            print ''
            station1_indx = 0
            station2_indx = -1
            Ns1 = len(station1_selection)
            Ns2 = len(station2_selection)
            pres = False
            while pres == False:
                station2_indx += 1 # increment station 2
                if station2_indx == Ns2-1:
                    station1_indx += 1
                    station2_indx = station1_indx + 1 # reset station 2
                if station1_indx == Ns1:
                    sys.exit('No data found.')
                station1 = station1_selection[station1_indx]
                station2 = station2_selection[station2_indx]
                pres = plot_channel_time(station1, station2, minmax=minmax, plot_cordata=plot_cordata, logplot=logplot)
            pylab.connect('key_press_event', on_press_multi_channel)
            pylab.connect('button_press_event', on_click_multi_channel)
        pylab.show()

    else:
        parser.print_help()
