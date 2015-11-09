#!/usr/bin/env python

#
# Written by George Heal, heald@astron.nl, November 2010, Version 1.0
#



import sys
import pylab
import numpy

if len(sys.argv) != 3:
        print 'Usage: provide 2 input arguments\n (1) catalog filename\n (2) clip percentage e.g. 90'
        print 'An output file will be produced, which is the input'
        print 'catalog filename with ".clipped" appended'
        exit()

outfilename = sys.argv[1]+'.clipped'
of = open(outfilename,'w')
cumflux = 0.0
percentage = float(sys.argv[2])
temp = []
nlines = 0
keptlines = 0

for line in open(sys.argv[1]):
        sline = line.split(',')
        if len(sline) < 2: continue
        if sline[-1].strip()[-6:] == 'format':
                print >>of, line.rstrip("\r\n")
                print >>of, ''
                for i in range(len(sline)):
                        if sline[i].strip() == 'I': break
        elif line[0] != '#':
                if len(sline) > i:
                        cumflux += float(sline[i].strip())
                        temp.append((numpy.abs(float(sline[i].strip())),float(sline[i].strip()),line.rstrip("\r\n")))
                        nlines += 1
                else:
                        print >>of, line.rstrip("\r\n")

temp = sorted(temp,reverse=True)
print 'Found cumulative flux %f' % (cumflux)
cliplevel = percentage/100.*cumflux
print 'Clipping at cumulative flux of %f percent = %f' % (percentage, cliplevel)

cumflux = 0.0
cumfluxlist = []
searching = True

for t in temp:
        cumflux += t[1]
        cumfluxlist.append(cumflux)
        if cumflux <= cliplevel and searching:
                print >>of, t[2]
                keptlines += 1
        else:
                searching = False

of.close()
if keptlines == 0:
        print 'WARNING!!! There were no compenents in the output file.'
        print 'Perhaps you need to set a higher percentage level.'
        print 'The results are in %s' % (outfilename)
else:
        print 'Done! Results are in %s' % (outfilename)
        print 'Kept %d / %d skymodel components' % (keptlines, nlines)

pylab.plot(range(len(cumfluxlist)),cumfluxlist,'b.')
pylab.plot([0,len(cumfluxlist)],[cliplevel,cliplevel],'k--')
pylab.xlabel('Number of CLEAN components [sorted by abs value of flux]')
pylab.ylabel('Cumulative flux')
pylab.legend(('Cumulative flux','Clip level'),loc='lower right')
pylab.show()

