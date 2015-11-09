#!/bin/tcsh
# -*- coding: utf-8 -*-

# Created by R van Weeren and further modified by A Shulevski.
#
# Run as: Solution_Plotter.py <MS> <antenna_1 ( ex. CS002LBA)> <antenna_2 (ex. RS021LBA)> <plot_item (one of: amp, phase, TEC)> [other_solution_database (ex. instrument_one__db)]
#

import sys
import pyrap.tables as pt
import os
import lofar.parmdb
import numpy as numpy
import math
import lofar.expion.parmdbmain
from   scipy import *
import pylab
import matplotlib.pyplot as plt

args = sys.argv[1:]

assert(len(args) == 4 or len(args) == 5), "Usage: Run as: Solution_Plotter.py <MS> <antenna_1 ( ex. CS002LBA)> <antenna_2 (ex. RS021LBA)> <plot_item (one of: amp, phase, TEC)> [other_solution_database (ex. instrument_one__db)]"

antenna1 = args[1]
antenna2 = args[2]

#antenna1 = 'CS021LBA'
#antenna1 = 'RS208LBA'

msname = args[0]

#msname = 'SB000_split.MS'
instrument_name =  msname + '/' + 'instrument'

if len(args) == 5:
	#instrument_name = msname +'/' +'instrument_amp_corr'
	instrument_name = msname +'/' + args[4]


freq_tab= pt.table(msname + '/SPECTRAL_WINDOW')
freq    = freq_tab.getcol('REF_FREQUENCY')
freq_tab.close()

print 'Observing frequency', freq/[1e6], ' MHz'

pdb = lofar.parmdb.parmdb(instrument_name)
parms = pdb.getValuesGrid("*")
print parms.keys()
key_names = parms.keys()
antenna_list = numpy.copy(key_names)
pol_list = numpy.copy(key_names)
sol_par  = numpy.copy(key_names)
print len(key_names)
print len(antenna_list)

# clean lists, hack
for ii in range(len(key_names)):
      #print ii
      antenna_list[ii] = "CS001LBA"
      pol_list[ii]     = "0:0"
      sol_par[ii]      = "Ampl"
      gain             = "Gain"

# create the antenna+polarizations list
for ii in range(len(key_names)):
    print 'ii', ii
    print str(key_names[ii])
    string_a = str(key_names[ii])

    split_a  = string_a.split( ":" )
    if split_a[0] != 'TEC' :
      antenna_list[ii] = split_a[4]
      pol_list[ii]     = split_a[1] + ':' + split_a[2]
      sol_par[ii]      = split_a[3]
      gain             = split_a[0]
    #print antenna_list[ii]

antenna_list = numpy.unique(antenna_list)
pol_list     = numpy.unique(pol_list)
sol_par      =  numpy.unique(sol_par)
print 'Stations available:', antenna_list
print 'Polarizations:', pol_list, sol_par, gain

if args[3] == "amp":
	amp = parms['Gain:0:0:Ampl:'+ antenna1]['values'][::]
	plt.plot(amp, 'o')
	plt.xlabel("Time slot")
	plt.ylabel("Solution amplitude")
	plt.title("Solution Amplitudes")
	print 'Plotting amplitude solutions for :', antenna1

elif args[3] == "phase":
	phase = parms['Gain:0:0:Phase:'+ antenna1]['values'][::]
	plt.plot(phase, 'o')
	plt.xlabel("Time slot")
	plt.ylabel("Solution phase")
	plt.title("Solution Phases")
	print 'Plotting phase solutions for :', antenna1

elif args[3] == "TEC":

	a1_TEC        = -8.44797245e9*(parms['TEC:'+ antenna1]['values'][::])/freq

	a2_TEC        = -8.44797245e9*(parms['TEC:'+ antenna2]['values'][::])/freq

	del_TEC         = (a1_TEC) - (a2_TEC)

	del_TEC = numpy.fmod(del_TEC, 2.0 * numpy.pi)
	del_TEC[del_TEC < -numpy.pi] += 2.0 * numpy.pi
	del_TEC[del_TEC > numpy.pi] -= 2.0 * numpy.pi
	plt.plot(del_TEC, 'o')
	plt.xlabel("Time slot")
	plt.ylabel("Diff. TEC Solution")
	plt.title("Diff. TEC")
	print 'Plotting diff. TEC solutions for :', antenna1, antenna2

#show()
plt.show()
