#
# Written by Joris van Zwieten,zwieten@astron.nl, November 2008
# Version 1.0
#

import pylab
import solplot
import lofar.parmdb
import numpy
import math

def phase_unwrap(phase, window_size=1):
    """
    Unwrap phase by restricting phase (n) to fall within a range [-pi, pi]
    around phase (n-1).
    
    Optionally low-pass filter using a running average.
    """

    last = 0.0
    window = []

    for i in range(0, len(phase)):
        delta = math.fmod(phase[i] - last, 2.0 * math.pi)

        if delta < -math.pi:
            delta += 2.0 * math.pi
        elif delta > math.pi:
            delta -= 2.0 * math.pi
        
        last += delta;
        
        if(len(window) < window_size):
            window.append(last)
        else:
            # shift window and insert new point
            window[:-1] = window[1:]
            window[-1] = last

        mean = 0.0
        for j in range(0, len(window)):
            mean += window[j]
        mean /= float(len(window))

        phase[i] = mean


def phase_normalize(phase):
    """
    Normalize phase to the range [-pi, pi].
    """

    # convert to range [-2*pi, 2*pi]
    numpy.fmod(phase, 2.0 * numpy.pi)

    # convert to range [-pi, pi]
    phase[phase < -numpy.pi] += 2.0 * numpy.pi
    phase[phase > numpy.pi] -= 2.0 * numpy.pi


def plot(pdb, stations, dir=None, parm="Gain:11", ref=0, unwrap=False, smooth=1, stack=None):
    """
    Plot gain amplitude and phase. If a direction is specified then directional
    gain will be plotted instead of directionless gain. The phase signal is
    plotted relative to the station with number 'ref' (default 0).

    Optionally the phase signal can be unwrapped and/or low-pass filtered.

    By default, the amplitude plots will be stacked and the phase plots will be
    stacked if 'unwrap' equals False. Through the 'stack' argument, this
    behaviour can be overridden. If 'stack' is set to True, both plots will be
    stacked. If set to False, both plots will not be stacked.
    """

    db = lofar.parmdb.parmdb(pdb)

#    stations = ["CS00%d_dipole%d" % (x,y) for x in [1,8] for y in [0,4,8,12]]
#    stations = stations + ["CS0%d_dipole%d" % (x,y) for x in [10,16] for y in [0,4,8,12]]

    (ampl, phase) = solplot.fetch(db, stations, direction=dir, parm=parm)

    refphase = numpy.array(phase)
    for i in range(0, len(stations)):
        if i != ref:
            refphase[i] = refphase[i] - refphase[ref]
            if unwrap:
                phase_unwrap(refphase[i], smooth)
            else:
                phase_normalize(refphase[i])
    refphase[ref] = 0.0

    solplot.plot(ampl, stack=(stack is None) or stack,show_legend=True)
    solplot.plot(refphase, stack=((not stack is None) and stack) or ((stack is None) and (not unwrap)))
