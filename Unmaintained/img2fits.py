#!/usr/bin/env python

# Convert input CASA image to fits using pyrap.
#
# Written by Joris van Zwieten, zwieten@astron.nl, September 2010, Version 1.0
#

import pyrap.images as im
import os.path
import sys

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print "usage: img2fits.py <casa image> [output]"
    sys.exit(1)

inf = sys.argv[1]
if len(sys.argv) == 3:
    outf = sys.argv[2]
else:
    outf = os.path.splitext(sys.argv[1])[0] + '.fits'

print "converting %s -> %s" % (inf, outf)
image = im.image(inf)
image.tofits(outf)
