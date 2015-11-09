#!/usr/bin/python
# script to automatically generate NDPPP script

import math, optparse

##----------------------input options----------------------------
parser = optparse.OptionParser()
parser.add_option("-f", "--file", dest="file",
                  help="name of skymodel file")
parser.add_option("-a", "--ra", dest="ra",
                  help="Right Ascention in h:m:s, example: 17:14:23.136")
parser.add_option("-d", "--dec", dest="dec",
                  help="Declination in degrees, example: +63.56.43.375 or -12.6.3")
parser.add_option("-r", "--radius", dest="radius",
                  help="Radius around RA/Dec in degrees")
parser.add_option("-o", "--overwrite", dest="overwrite", default=False,
                  help="Overwrite existing files if true, otherwise append")

(options, args) = parser.parse_args()
if not options.file:
  parser.error("SkyModel not set")
if not options.ra:
  parser.error("Right Ascention not set")
if not options.dec:
  parser.error("Declination not set")
if not options.radius:
  parser.error("Radius not set")
if options.overwrite:
  Mode = 'w'
else:
  Mode = 'a'

# Convert latitude and longitude to
# spherical coordinates in radians.
degrees_to_radians = math.pi/180.0

def distance_on_unit_sphere(lat1, long1, lat2, long2):
  try:
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
    
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
    
    # Compute spherical distance from spherical coordinates.
    
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc
  except Exception:
    print (lat1, long1, lat2, long2)
    raise

def convert_RA(RA):
  try:
    ra = RA.split(':')
    if len(ra) == 3:
      value = int(ra[0]) + int(ra[1])/60.0 + float(ra[2])/3600.0
      return value/24.0*360.0 - 180.0
    else:
      raise "RA conversion failed: " + RA
  except:
      raise "RA conversion failed: " + RA

def convert_Dec(Dec):
  try:
    dec = Dec.split('.')
    if len(dec) == 3:
      return int(dec[0]) + int(dec[1])/60.0 + float(dec[2])/3600.0
    elif len(dec) == 4:
      return int(dec[0]) + int(dec[1])/60.0 + float(dec[2]+ '.' + dec[3])/3600.0
    else:
      raise "Dec conversion failed: " + Dec
  except:
      raise "Dec conversion failed: " + Dec

def parse_input_file(filename, sources, comments):
  f     = open(filename)
  lines = f.readlines()
  f.close()
  for line in lines:
    if line[0] == '#' or line.isspace(): ##comments or whitespace
       if line[0] == '#': comments += line
    else:
      l = line.split(',')
      sources.append((l[2], l[3], line))
  return sources, comments

#-----main-----
print "Starting"
Sources,Comments = parse_input_file(options.file, [], "")
inside  = options.file + ".inside"
outside = options.file + ".outside"
infile  = open(inside, Mode)
outfile = open(outside, Mode)
infile.write(Comments)
outfile.write(Comments)

RA      = convert_RA(options.ra)
Dec     = convert_Dec(options.dec)
Radius  = float(options.radius) * degrees_to_radians
for s in Sources:
  if distance_on_unit_sphere(RA, Dec, convert_RA(s[0]), convert_Dec(s[1])) <= Radius:
    infile.write(s[2])
  else:
    outfile.write(s[2])
infile.close()
outfile.close()
print "Done"
