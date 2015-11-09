#!/usr/bin/env python

# Plot two solution tables against each other. Supports comparison of 
# CASA v. CASA, CASA v. BBS, and BBS v. BBS. Only gain solutions 
# (gaincal task) are supported, and only if a solution was computed for 
# each integration time.
#
# Author: Joris van Zwieten (zwieten@astron.nl), September 2010, Version 1.0

import sys
import copy
import math
import numpy
import pylab
import pyrap.tables as tb
import lofar.parmdb as parmdb
import os.path as path

station_names = None

def fetch_bbs_parm(db, fqnames):
    result = None

    for fqname in fqnames:
        try:
            result = db.getValuesGrid(fqname)[fqname]
        except KeyError:
            pass

    if not (result is None):
        if type(result) is dict:
            result = result["values"]
        result = result.squeeze()

    return result

def read_bbs_gain(db, station, correlation, time, direction=None):
    global station_names

    if direction is None:
        fqnames = ["Gain:%d:%d:Real:%s" % (correlation, correlation, station_names[station]),
                    "Gain:%d%d:Real:%s" % (correlation + 1, correlation + 1, station_names[station])]
    else:
        fqnames = ["DirectionalGain:%d:%d:Real:%s:%s" % (correlation, correlation, station_names[station], direction),
                    "Gain:%d:%d:Real:%s:%s" % (correlation, correlation, station_names[station], direction),
                    "Gain:%d%d:Real:%s:%s" % (correlation + 1, correlation+ 1, station_names[station], direction)]
    re = fetch_bbs_parm(db, fqnames)

    if direction is None:
        fqnames = ["Gain:%d:%d:Imag:%s" % (correlation, correlation, station_names[station]),
                    "Gain:%d%d:Imag:%s" % (correlation + 1, correlation + 1, station_names[station])]
    else:
        fqnames = ["DirectionalGain:%d:%d:Imag:%s:%s" % (correlation, correlation, station_names[station], direction),
                    "Gain:%d:%d:Imag:%s:%s" % (correlation, correlation, station_names[station], direction),
                    "Gain:%d%d:Imag:%s:%s" % (correlation + 1, correlation+ 1, station_names[station], direction)]
    im = fetch_bbs_parm(db, fqnames)

    assert(not (re is None))
    assert(not (im is None))
    assert(len(re) == len(im))
    assert(len(time) == len(re))

    # Correct for the (in)famous factor 2.0 difference in source coherencies.
#    return (re + 1j * im) / numpy.sqrt(2.0)

    flag = numpy.zeros((len(re)), dtype=numpy.bool)
    return (flag, re + 1j * im)

def read_casa_gain(db, station, correlation, time, direction=None):
    sel = db.query("ANTENNA1 == %d" % station)
    sel = sel.sort("TIME")

    ctime = sel.getcol("TIME")
    cgain = sel.getcol("GAIN").squeeze()[:, correlation]

    flag = numpy.zeros((len(time)), dtype=numpy.bool)
    gain = numpy.zeros((len(time)), dtype=cgain.dtype)

    last = -1
    for i in range(len(ctime)):
        idx = time.index(ctime[i], last + 1)
        gain[idx] = cgain[i]

        flag[(last + 1):idx] = True
        last = idx

    return (flag, gain)

class GainTable:
    def __init__(self, name):
        self._reader = None
        self._table = None
        self._table_name = None

        idx = name.find(':')
        assert(idx > 0)

        package_name = name[:idx]
        self._table_name = name[idx+1:]

        if package_name == "bbs":
            self._table = parmdb.parmdb(self._table_name)
            self._reader = read_bbs_gain
        elif package_name == "casa":
            self._table = tb.table(self._table_name)
            self._reader = read_casa_gain
        else:
            assert(false)

    def read_gain(self, station, correlation, time, direction=None):
        return self._reader(self._table, station, correlation, time, direction)

    def read_reference_phase(self, time, direction=None):
        ref = [numpy.angle(self.read_gain(0, 0, time, direction)[1]), numpy.angle(self.read_gain(0, 1, time, direction)[1])]
        ref[0] = numpy.cos(-ref[0]) + numpy.sin(-ref[0]) * 1.0j
        ref[1] = numpy.cos(-ref[1]) + numpy.sin(-ref[1]) * 1.0j
        return ref

    def name(self):
        return self._table_name

def main(args):
    global station_names

    if len(args) < 3:
        print "usage: compare.py <ms> <solution table> <solution table> [direction]"
        print "examples:"
        print "    compare.py test.MS bbs:test.MS/instrument casa:~/test.cal"
        print "    compare.py test.MS bbs:test.MS/instrument bbs:instrument-old CasA"
        sys.exit(1)

    print "Observation            :", args[0]
    print "Gain solution table LHS:", args[1]
    print "Gain solution table RHS:", args[2]

    direction = None
    if len(args) > 3:
        print "Direction              :", args[3]
        direction = args[3]

    ms = args[0]
    obs = tb.table(path.join(ms, "ANTENNA"))
    station_names = obs.getcol("NAME")
    print "Stations               :", station_names
    print

    obs = tb.tablecommand("SELECT UNIQUE TIME FROM %s" % ms)
    time = list(obs.getcol("TIME"))
    print "No. of unique times    :", len(time)

    lhs = GainTable(args[1])
    ref_lhs = lhs.read_reference_phase(time, direction)

    rhs = GainTable(args[2])
    ref_rhs = rhs.read_reference_phase(time, direction)

    for i in range(len(station_names)):
        for j in range(2):
            try:
                (flag_lhs, g_lhs) = lhs.read_gain(i, j, time, direction)
                (flag_rhs, g_rhs) = rhs.read_gain(i, j, time, direction)
            except:
                print "error: failed to read solutions for station %s polarization %d" % (station_names[i], j)
                continue

            assert(len(g_lhs.shape) == 1 and g_lhs.shape[0] == len(time))
            assert(len(g_rhs.shape) == 1 and g_rhs.shape[0] == len(time))

            flags = flag_lhs | flag_rhs
            g_lhs = g_lhs * ref_lhs[j]
            g_rhs = g_rhs * ref_rhs[j]

            g_lhs = g_lhs[~flags]
            g_rhs = g_rhs[~flags]

            gdiff = g_lhs / g_rhs

            y0 = numpy.mean(numpy.abs(g_lhs))
            dy = numpy.std(numpy.abs(g_lhs))

            # Make time relative to the start in minutes.
            xaxis = ((time - time[0]) / 60.0)[~flags]

            fig = pylab.figure()
            fig.text(.5, .95, station_names[i], horizontalalignment='center', fontsize=14)

            pylab.subplot(231)
#            pylab.scatter(xaxis, numpy.abs(gb))
            pylab.plot(xaxis, numpy.abs(g_lhs))
            pylab.xlabel("Time (min)")
            pylab.ylabel("Amplitude")
            pylab.title("GAIN LHS %s" % (["XX", "YY"][j]))
            pylab.gca().set_ylim((y0 - 3.0 * dy, y0 + 3.0 * dy))

            pylab.subplot(232)
#            pylab.scatter(xaxis, numpy.abs(gc))
            pylab.plot(xaxis, numpy.abs(g_rhs))
            pylab.xlabel("Time (min)")
            pylab.ylabel("Amplitude")
            pylab.title("GAIN RHS %s" % (["XX", "YY"][j]))
            pylab.gca().set_ylim((y0 - 3.0 * dy, y0 + 3.0 * dy))

            pylab.subplot(233)
            pylab.scatter(numpy.abs(g_lhs), numpy.abs(g_rhs))
            pylab.xlabel("LHS")
            pylab.ylabel("RHS")
            pylab.title("GAIN %s RHS vs. LHS" % (["XX", "YY"][j]))
#            pylab.plot(numpy.abs(gdiff))
#            pylab.title("RATIO")
#            pylab.gca().set_ylim((0.5, 1.5))

            pylab.subplot(234)
            pylab.scatter(xaxis, numpy.angle(g_lhs))
            pylab.xlabel("Time (min)")
            pylab.ylabel("Phase (rad)")
            pylab.title("PHASE LHS %s" % (["XX", "YY"][j]))
            pylab.gca().set_ylim((-numpy.pi, numpy.pi))

            pylab.subplot(235)
            pylab.scatter(xaxis, numpy.angle(g_rhs))
            pylab.xlabel("Time (min)")
            pylab.ylabel("Phase (rad)")
            pylab.title("PHASE RHS %s" % (["XX", "YY"][j]))
            pylab.gca().set_ylim((-numpy.pi, numpy.pi))

            pylab.subplot(236)
            pylab.scatter(numpy.angle(g_lhs), numpy.angle(g_rhs))
            pylab.xlabel("LHS")
            pylab.ylabel("RHS")
            pylab.title("PHASE %s RHS vs. LHS" % (["XX", "YY"][j]))
#            pylab.plot(numpy.angle(gdiff))
#            pylab.title("DIFFERENCE")
#            pylab.gca().set_ylim((-numpy.pi, numpy.pi))

    pylab.show()

if __name__ == "__main__":
    main(sys.argv[1:])
