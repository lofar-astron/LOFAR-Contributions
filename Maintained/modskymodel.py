#!/usr/bin/python

# Author: Francesco de Gasperin (fdg@mpa-garching.mpg.de)

import pyrap.images
import numpy as np
import optparse
import sys
import coordinates_mode as cm
import math

def isNaN(num):
  return num != num

def coordshift(ra, dec, rashift, decshift):
  # shift ra and dec by rashift and decshift
  # ra: string in the hh:mm:ss.ss format
  # dec: string in the dd.mm.ss.ss format
  # rashift: float in arcsec
  # dechift: float in arcsec
  (hh, mm, ss) = cm.ratohms(cm.hmstora(*ra.split(":")) + rashift/3600)
  ra = str(hh)+":"+str(mm)+":"+ '%.3f' % ss
  (dd, mm, ss) = cm.dectodms(cm.dmstodec(*dec.split(".",2)) + decshift/3600)
  dec = "+"+str(dd)+"."+str(mm)+"."+ '%.3f' % ss
  return ra, dec

opt = optparse.OptionParser(usage="%prog -o bbs.skymodel-new -i bbs.skymodel [and one or more of the following options]", version="%prog 0.1")
opt.add_option('-i', '--inbbs', help='Input bbs skymodel [default = bbs.skymodel]', default='bbs.skymodel')
opt.add_option('-o', '--outbbs', help='Output bbs skymodel [default = bbs.skymodel-new]', default='bbs.skymodel-new')
opt.add_option('-m', '--mask', help='Mask for valid clean components [Default: not applying any mask]')
opt.add_option('-p', '--spidximg', help='Spectral index image [Default: not changing spectral index]')
opt.add_option('-s', '--shift', help='Ra and Dec shift in arcsec [Format: +/-Ra shift, +/-Dec shift, Default: 0,0]')
opt.add_option('-v', '--verbose', help='Print some more output', action="store_true", default=False)
(options, foo) = opt.parse_args()
inbbs = options.inbbs
outbbs = options.outbbs
spidximg = options.spidximg
mask = options.mask
shift = options.shift
verbose = options.verbose

print "Input BBS file = "+inbbs
print "Output BBS file = "+outbbs

if mask != None: print "Mask = "+mask
if spidximg != None: print "Spectral index image = "+spidximg
if shift != None:
  try:
    (rashift, decshift) = shift.replace(' ', '').split(',')
    rashift = float(rashift)
    decshift = float(decshift)
    print "Ra shift: ", rashift, "arcsec"
    print "Dec shift: ", decshift, "arcsec"
  except:
    print "ERROR: bad formatted Ra,Dec shift. Should be something like \"-s 2,5\""

if spidximg == None and mask == None and shift == None:
  print "Nothing to do!"
  exit(0)
sys.stdout.flush()

# Open BBS Input files
names = ['Name', 'Type', 'Patch', 'Ra', 'Dec', 'I', 'Q', 'U', 'V', 'ReferenceFrequency', 'SpectralIndexDegree', 'SpectralIndex', 'MajorAxis', 'MinorAxis', 'Orientation']
formats = ['S30', 'S30', 'S30', 'S30', 'S30', float, float, float, float, float, int, float, float, float, float]
try:
  if verbose: print "WARNING: skipping first 5 rows, check that you are not loosing any CC"
  bbsdata = np.loadtxt(inbbs, skiprows=5, comments='#', delimiter=", ", dtype=np.dtype({'names':names, 'formats':formats}))
except IOError:
  print "ERROR: error opening BBS file (",inbbs,"), probably a wrong name/format"
  exit(1)

bbsnewdata = []

# Open mask
if mask != None:
  try:
    maskdata = pyrap.images.image(mask)
  except:
    print "ERROR: error opening MASK (",mask,"), probably a wrong name/format"
    exit(1)

# Open spidx image
if spidximg != None:
  try:
    spidxdata = pyrap.images.image(spidximg)
  except:
    print "ERROR: error opening SPIDX image (",spidximg,"), probably a wrong name/format"
    exit(1)

# for each component find the relative mask pix, spidx pix and do the shift
for cc in bbsdata:
  name = cc['Name']
  ra = cc['Ra']
  dec = cc['Dec']
  
  # first do the coordinate shift (assuming mask and spidx image have correct coordinates!)
  if shift != None:
    (ra, dec) = coordshift(ra, dec, rashift, decshift)
    cc['Ra'] = ra; cc['Dec'] = dec

  if mask != None:
    (a,b,_,_) = maskdata.toworld([0,0,0,0])
    (_, _, pixY, pixX) = maskdata.topixel([a, b, \
	  math.radians(cm.dmstodec(*dec.split(".",2))), math.radians(cm.hmstora(*ra.split(":")))])
    try:
      if not maskdata.getdata()[0][0][math.floor(pixY)][math.floor(pixX)]:
	if verbose: print "Removing component \"",name,"\" because is masked."
	continue
    except:
      print "WARNING: failed to find a good mask value for component \"", name, "\"."
      print "-> Removing this component"
      continue
   
  if spidximg != None:
    (a,b,_,_) = spidxdata.toworld([0,0,0,0])
    (_, _, pixY, pixX) = spidxdata.topixel([a, b, \
	  math.radians(cm.dmstodec(*dec.split(".",2))), math.radians(cm.hmstora(*ra.split(":")))])
    try:
      val = round(spidxdata.getdata()[0][0][math.floor(pixY)][math.floor(pixX)],2)
      cc['SpectralIndex'] = '%.2f' % val
      if isNaN(val): raise ValueError('Nan occurred')
    except:
      print "WARNING: failed to find a good spidx value for component \"", name, "\"."
      print "-> Set spectral index to 0.0"
      cc['SpectralIndex'] = '0.0'

  bbsnewdata.append([cc['Name'], cc['Type'], cc['Patch'], cc['Ra'], cc['Dec'], cc['I'], cc['Q'], cc['U'], cc['V'], cc['ReferenceFrequency'], cc['SpectralIndexDegree'], cc['SpectralIndex'], cc['MajorAxis'], cc['MinorAxis'], cc['Orientation']])

# write to new BBS file
f1 = open(inbbs, 'r')
f2 = open(outbbs,'w')
# write the headers back
for line in xrange(5):
  f2.write(f1.readline())
for cc in bbsnewdata:
  for ele in cc[:-1]:
    f2.write(str(ele))
    f2.write(', ')
  f2.write(str(cc[-1]))
  f2.write('\n')
f1.close()
f2.close()
