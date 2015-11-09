#!/usr/bin/env python

# Plot LM tracks for the zenith, azimuth, and elevation at Dwingeloo of 
# a number of strong radio sources and the target source (when given an MS).
#
# Author: Joris van Zwieten (zwieten@astron.nl), September 2010

import sys
import pylab
import pyrap.tables
import os.path as path
import time
import calendar
import math

def deg2rad(angle):
    return (angle * math.pi) / 180.0

def rad2deg(angle):
    return (angle * 180.0) / math.pi

# Compute rad from hours, min, sec.
def ra2rad(ra):
        return (ra[0] + ra[1]/60.0 + ra[2]/3600.0) * math.pi / 12.0

# Compute rad from degrees, arcmin, arcsec.
def dec2rad(dec):
        return (dec[0] + dec[1]/60.0 + dec[2]/3600.0) * math.pi / 180.0

# Compute l,m,n from ra, dec of the source and the phase center.
def radec2lmn(ra, dec, phase_center):
    l = math.cos(dec) * math.sin(ra - phase_center[0])
    m = math.sin(dec) * math.cos(phase_center[1]) - math.cos(dec) * math.sin(phase_center[1]) * math.cos(ra - phase_center[0])
    n = math.sqrt(1.0 - l**2 - m**2)
    return (l, m, n)

# Compute the Julian date for the given date (valid from 1900/3/1 to 2100/2/28),
# according to Jean Meeus: Astronomical Algorithms.
# Adapted from http://www.jgiesen.de/elevaz/basics/meeus.htm
#
# Julian day: 86400 s, Julian year: 365.25 d, Julian century: 36525 d.
#
def julian_date(year, month, day, ut_hours):
    if month <= 2:
        year = year - 1
        month = month + 12

    return int(365.25 * year) + int(30.6001 * (month + 1)) - 15 + 1720996.5 + day + ut_hours / 24.0

# Convert from time in seconds since the Unix epoch (as returned by time.time())
# to Julian date.
def unix2jd(unix_time):
    (year, month, mday, hours, mins, sec,tmp0, tmp1, tmp2) = time.gmtime(unix_time)
    ut_hours = hours + (mins + sec / 60.0) / 60.0

    return julian_date(year, month, mday, ut_hours)

# Compute sidereal time at Greenwich for the given Julian date, according to
# Jean Meeus: Astronomical Algorithms.
# Adapted from http://www.jgiesen.de/elevaz/basics/meeus.htm
#
# Sidereal time is returned in hours.
#
def greenwich_sidereal_time(jd):
    t = (jd - 2451545.0 ) / 36525
    theta0 = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t * t - (t * t * t) / 38710000.0

    # The value of theta0 is sidereal time in degrees and is often >> 360 so
    # it should be wrapped to the range [0, 360) and then be converted to hours.
    return ((theta0 % 360.0) * 12.0) / 180.0

# Compute local sidereal time in hours for the given time in seconds since the
# Unix epoch (as returned by time.time()) and the given longitude in radians.
# Positive longitude is taken due East from the prime medidian.
def local_sidereal_time(jd, lon):
    return greenwich_sidereal_time(jd) + (lon * 12.0) / math.pi

# Compute local altitude (elevation) and azimuth from the given local hour
# angle, the declination of the source, and the local lattitude (all in
# radians).
def azel(ha, dec, lat):
    el = math.asin(math.sin(dec) * math.sin(lat) + math.cos(dec)
        * math.cos(lat) * math.cos(ha))

    az = math.acos((math.sin(dec) - math.sin(el) * math.sin(lat))
        / (math.cos(el) * math.cos(lat)))

    if math.sin(ha) >= 0.0:
        az = 2.0 * math.pi - az

    return (az, el)

# Plot source tracks for the given Julian date range.
def plot(observer, jd_range, source_list, sample_time = 900.0):
    # Convert location from degrees to radians.
    lat_observer = deg2rad(observer[0])
    lon_observer = deg2rad(observer[1])

    traces_l = []
    traces_m = []
    traces_az = []
    traces_el = []

#    print (jd_range[1] - jd_range[0]) * 24.0
    delta = sample_time / (24.0 * 3600.0)
#    print (jd_range[1] - jd_range[0]) / delta
    count = int(math.ceil((jd_range[1] - jd_range[0]) / delta))
    for i in range(0, count):
        jd = jd_range[0] + i * delta
        lst = local_sidereal_time(jd, lon_observer)

        raZenith = (lst * math.pi) / 12.0
        decZenith = lat_observer

        for j in range(0, len(source_list)):
            if i == 0:
                traces_l.append([])
                traces_m.append([])
                traces_az.append([])
                traces_el.append([])

            raSource = source_list[j][1]
            decSource = source_list[j][2]
            lmn = radec2lmn(raSource, decSource, (raZenith, decZenith))

            haSource = raZenith - raSource
            if haSource < 0.0:
                haSource = haSource + 2.0 * math.pi

            horz_coord = azel(haSource, decSource, lat_observer)

            traces_l[j].append(lmn[0])
            traces_m[j].append(lmn[1])
            traces_az[j].append(rad2deg(horz_coord[0]))
            traces_el[j].append(rad2deg(horz_coord[1]))

    legend = [src[0] for src in source_list]
    xaxis = [i * sample_time / 3600.0 for i in range(count)]

    pylab.figure(figsize=[7,9])
    pylab.subplots_adjust(top=0.95, bottom=0.07, hspace=0.4, wspace=0.2)
    pylab.subplot(311)
    pylab.title("LM-plane tracks")
    pylab.xlabel("L")
    pylab.ylabel("M")
    for j in range(0, len(source_list)):
    #    traces_l[j].append(traces_l[j][0])
    #    traces_m[j].append(traces_m[j][0])
        pylab.plot(traces_l[j], traces_m[j], '.-')
    pylab.xlim(-1.0, 1.0)
    pylab.ylim(-1.0, 1.0)
    pylab.legend(legend)

    pylab.subplot(312)
    pylab.title("Azimuth @ %.3f deg N, %.3f deg E" % observer)
    pylab.xlabel("Time (hour) (%d s/sample)" % sample_time)
    pylab.ylabel("Azimuth angle (deg)")
    for j in range(0, len(source_list)):
        pylab.plot(xaxis, traces_az[j])
#    pylab.legend(legend)

    pylab.subplot(313)
    pylab.title("Elevation @ %.3f deg N, %.3f deg E" % observer)
    pylab.xlabel("Time (hour) (%d s/sample)" % sample_time)
    pylab.ylabel("Elevation angle (deg)")
    for j in range(0, len(source_list)):
        pylab.plot(xaxis, traces_el[j])
#    pylab.legend(legend)

    pylab.show()

def main(args):
    # Position of the observer (lat, lon) in degrees.
    observer = (52.81200794146114, 6.39618316773478)

    source_list = []
    source_list.append(("NCP", ra2rad((0.0, 0.0, 0.0)), dec2rad((90.0, 0.0, 0.0))))
    source_list.append(("CasA", ra2rad((23.0, 27.0, 25.4)), dec2rad((58.0, 52.0, 38.0))))
    source_list.append(("CygA", ra2rad((19.0, 59.0, 28.3)), dec2rad((40.0, 44.0, 2.0))))
#    source_list.append(("3C196", ra2rad((8.0, 14.0, 36.06)), dec2rad((48.0, 13.0, 2.25))))

    if len(args) == 1:
#        Information in the OBSERVATION subtable seems to be inconsistent
#
#        ms = pyrap.tables.table(path.join(args[0], "OBSERVATION"))
#        time_range = ms.getcell("TIME_RANGE", 0)
#        ms.close()
#        del ms

        ms = pyrap.tables.table(args[0])
        time_col = ms.getcol("TIME")
        time_range = [min(time_col), max(time_col)]

        field = pyrap.tables.table(path.join(args[0], "FIELD"))
        phase_dir = field.getcell("PHASE_DIR", 0)[0]
        source_list.append(("TARGET", phase_dir[0], phase_dir[1]))

        # Convert time range from seconds modified Julian data to Julian date.
        time_range = [t / (24.0 * 3600.0) + 2400000.5 for t in time_range]
    else:
        # Convert time range to seconds since the Unix epoch.
        t_start = calendar.timegm(time.strptime(args[0], "%Y/%m/%d/%H:%M:%S"))
        t_end = calendar.timegm(time.strptime(args[1], "%Y/%m/%d/%H:%M:%S"))

        # Convert time range to Julian date.
        time_range = [unix2jd(t_start), unix2jd(t_end)]

    plot(observer, time_range, source_list)

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print "usage: traces.py <ms>"
        print "    Plot source traces @ Dwingeloo for the given MS."
        print
        print "usage: traces.py <start> <stop>"
        print "    Times are assumed to be in UTC; format example:"
        print "    traces.py 2009/01/01/00:00:00 2009/01/02/00:00:00"
        sys.exit(1)

    main(sys.argv[1:])

################################################################################

# Compute local sidereal time in hours for the given time in seconds since the
# Unix epoch (as returned by time.time()) and the given longitude in radians.
# Positive longitude is taken due East from the prime medidian.
#def find_lst(unix_time, lon):
#    lst = find_gst(unix_time) + (lon * 12.0) / math.pi
#    if lst > 24.0:
#        lst = lst - 24.0
#    elif lst < 0.0:
#        lst = lst + 24.0

## Compute sidereal time at Greenwich for the given time in seconds since the
## Unix epoch (as returned by time.time()).
## LST functions taken from http://www.dur.ac.uk/john.lucey/users/lst.html
#def find_gst(unix_time):
#    #
#    # formula from Duffett-Smith's ``Practical Astronomy'', see Page 16-20.
#    #
#
#    (year, month, mday, hours, mins, sec,tmp0, tmp1, tmp2) = time.gmtime(unix_time)
#
#    ut_hours = hours + (mins + sec / 60.0) / 60.0
#    mday = mday + ut_hours / 24.0
#
#    if month <= 2:
#        year = year - 1
#        month = month + 12
#
#    a = int(year / 100.0)
#    b = 2.0 - a + int(a / 4.0)
#
#    if year < 0:
#        c = int((365.2500 * year) - 0.7500)
#    else:
#        c = int(365.2500 * year)
#
#    d = int(30.600100 * (month + 1.0))
#    jd = b + c + d + int(mday) + 1720994.500
#
#
#    s = jd - 2451545.000
#    t = s / 36525.000
#    t0 = 6.697374558 + (2400.051336 * t) + (0.000025862 * (t * t));
#    t0 = (t0 - int(t0 / 24.0) * 24)
#    if t0 < 0.0:
#        t0 = t0 + 24.0
#
#    ut = 1.002737909 * ut_hours
#    tmp = int((ut + t0) / 24.0)
#    gst = ut + t0 - tmp * 24.0
#    return gst
