#! /usr/bin/env python

from __future__ import with_statement
from __future__ import division

"""

Doc string

"""

__version__ = '0.2'

import sys
import os
import warnings
import logging
import numpy
from argparse import ArgumentParser
#import imgstats
#import matplotlib as mpl
#from matplotlib.backends.backend_agg import FigureCanvasAgg
import pyrap.tables as pt


SPEED_OF_LIGHT = 299792458.0


def setup_logger(conffile=None, verboseness=4):
    # some extra debug levels
    TRACE = 5
    XINFO = 15
    SEVERE = 35
    levels = [logging.CRITICAL, logging.ERROR, SEVERE,
              logging.WARNING, logging.INFO, XINFO, logging.DEBUG, TRACE]    
    logprop_filename = "msinfo.log_prop"
    if logconffile:
        logging.config.fileConfig(logconffile)
    elif os.path.exists(logprop_filename):
        logging.config.fileConfig(logprop_filename)
    elif os.path.exists(os.path.join(
            os.environ['HOME'], logprop_filename)):
        logging.config.fileConfig(os.path.join(
                os.environ['HOME'], logprop_filename))
    else:
        logger = logging.getLogger("msinfo")
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)


class Info(object):

    def __init__(self, **kwargs):
        self.parse_options(nargs=[])
        
    def run(self):
        for self.filename in self.filenames:
            try:
                self.ms = pt.table(self.filename, ack=False)
                self.get_summary()
                self.print_summary(verbosity=1)
                # print self.ms.keywordnames()
                # print self.ms.colnames()
                # print 
                # print self.ms.summary()
                # print self.ms.name()
                # print self.ms.info()
                #summary = get_summary()  # ms, options['verbose'])
                #summary['filename'] = filename
                #if summary:
                #    print_summary(summary, options['verbose'])
                #antennas = get_antenntas(ms, options['verbose'])
                #print_antennas(antennas, options['verbose'])
            except IOError, msg:
                sys.stderr.write("%s\n" % msg)
            else:
                pass
                self.ms.close()
        return 0

    def parse_options(self, args=None, nargs=[], usage_message=''):
        parser = ArgumentParser(description="Show information about one or "
                                "more measurenent sets", prog="msinfo",
                                version="%(prog)s " + __version__)
        parser.add_argument("filename", nargs='+')
        parser.add_argument("-V", "--verbose", type=int, default=3,
                            help="Verboseness: the level of detailed output")
        args = parser.parse_args()
        self.filenames = args.filename


    def get_antenntas(self):
        self.antennas = {}
        ant_table = pt.table(os.path.join(self.filename, "ANTENNA", ack=False))
        self.antennas['position'] = ant_table.getcol("POSITION")
        self.antennas['name'] = ant_table.getcol("NAME")
    
    def get_frequencies(self):
        table = pt.table(os.path.join(self.filename, 'SPECTRAL_WINDOW'), ack=False)
        frequencies = table.getcol('CHAN_FREQ')[0]
        nchannels = table.getcol('NUM_CHAN')[0]
        channel_width = table.getcol('CHAN_WIDTH')[0][0]
        return {'frequencies': frequencies, 'nchannels': nchannels,
                'width': channel_width}

    def get_summary(self):
        subtables = self.ms.keywordnames()
        for subtable in ('POLARIZATION', 'OBSERVATION', 'FIELD', 
                         'SPECTRAL_WINDOW'):
            if subtable not in subtables:
                sys.stderr.write("Subtable %s missing from MS\n" % subtable)
                sys.exit()
        frequencies = self.get_frequencies()
        self.get_antenntas()
        polarization = {'count': pt.table(
                os.path.join(self.filename, 'POLARIZATION'), ack=False).getcol(
                'NUM_CORR')[0]}
        times = {'time': pt.table(
                os.path.join(self.filename, 'OBSERVATION'), ack=False).getcol(
                'TIME_RANGE')[0]}
        fieldnames = {'fieldnames': pt.table(
                os.path.join(self.filename, 'FIELD'), ack=False).getcol('NAME')}
        phases = {'direction': pt.table(
                os.path.join(self.filename, 'FIELD'), ack=False).getcol('PHASE_DIR')}
        self.summary = {
            'frequencies': frequencies,
            'polarization': polarization,
            'fieldnames': fieldnames,
            'times': times,
            'phases': phases
            }


    def get_antenntas(self):
        self.antennas = {}
        self.antennas['position'] = pt.table(os.path.join(self.filename, "ANTENNA"), 
                                             ack=False).getcol("POSITION")
        self.antennas['name'] = pt.table(os.path.join(self.filename, "ANTENNA"), 
                                         ack=False).getcol("NAME")

    
    def print_summary(self, verbosity, output=sys.stdout):
        output.write("""
        
    \tSummary of UV data for %s
    
      Phase center:            %s
      Frequency range (MHz):   %.2f  --  %.2f
      Wavelength range (m):    %.2f  --  %.2f
      Time range (MJs):        %.2f  --  %.2f
      Duration (hrs):          %.2f
      # of integrations:       %d
      time bin / integration:  %.1f
      # of channels:           %d
      channel width (KHz):     %.1f
      # of polarizations:      %d
      
    """ % (self.filename, str(self.summary['phases']['direction']),
           min(self.summary['frequencies']['frequencies']/1e6),
           (max(self.summary['frequencies']['frequencies']) +
            self.summary['frequencies']['width'])/1e6,
           min(SPEED_OF_LIGHT/self.summary['frequencies']['frequencies']),
           max(SPEED_OF_LIGHT/self.summary['frequencies']['frequencies']),
           self.summary['times']['time'][0], self.summary['times']['time'][1],
           self.summary['times']['time'][1]/3600.0 - self.summary['times']['time'][0]/3600.0,
           1, 1,
           self.summary['frequencies']['nchannels'],
           self.summary['frequencies']['width']/1e3,
           self.summary['polarization']['count']))

        # CENTER = (3.82682E6, 4.60987E5, 5.06472E6)
        r = numpy.sqrt(self.antennas['position'][:,0]**2 + 
                       self.antennas['position'][:,1]**2 + 
                       self.antennas['position'][:,2]**2)
        latitude = 180*numpy.arctan2(self.antennas['position'][:,1], 
                                     self.antennas['position'][:,0])/numpy.pi
        longitude = 90 - 180*numpy.arccos(self.antennas['position'][:,2]/r)/numpy.pi
        output.write("Antennas & their GPS positions (longitude, latitude):\n")
        for name, rr, pphi, ttheta in zip(self.antennas['name'], r, 
                                          latitude, longitude):
            sys.stdout.write("  %s:  %10.6f  %10.6f\n" % (name, pphi, ttheta))

    

def main():
    info = Info()
    info.run()


if __name__ == '__main__':
    sys.exit(main())
