import sys
import os
import numpy as np
from numpy import ma
import casac
import inspect
import string

def xarray (a):
    b = np.zeros(a.max()+1,dtype='i4')
    for i in range (len(a)):
        b[a[i]]=i
    return b

def printarray (a,ndig,uant=['0','0'],ants=[]):

    delant = []
    for i in range(len(uant)):
        if a[i].min()==a[i].max()==a[:,i].min()==a[:,i].max()==0:
            delant=np.append(delant,int(i))
    if len(delant):
        print 'Removing ',len(delant),' antennas with no data '
        a=np.delete(a,delant,0)
        a=np.delete(a,delant,1)
    uant=np.delete(uant,delant)    # ! not good if antennas nonsequential
    for i in range(ndig+2):
        sys.stdout.write(' ')
    for i in uant:
        sys.stdout.write(str(i).rjust(ndig+1))
    sys.stdout.write('\n')
    for i in range((ndig+1)*len(uant)+5):
        sys.stdout.write('-')
    sys.stdout.write('\n')
    for i in range(a.shape[0]):
        sys.stdout.write(str(uant[i]).rjust(ndig+1))
        sys.stdout.write('|')
        for j in range(a.shape[1]):
            sys.stdout.write(str(a[i][j]).rjust(ndig+1))
        try:
            sys.stdout.write('  '+ants[uant[i]])
        except:
            pass
        print ' '

# main routine: listr     v.2 Neal Jackson 2011.06.01
#                             neal.jackson@manchester.ac.uk
# Purpose: does old-style AIPS MATX listings
# Invocation:   from listr_v2 import * ; listr('MS')
# optional arguments:
#     utstart, utend - units are seconds of MS file /(24.0*3600.0)
#     datacolumn='DATA' or 'CORRECTED_DATA'
#     whichtype='amp' or 'phase' - only any point doing phase on corrected data
#     ndig - number of digits in output tables, default is 3
#     docross - if true, do the cross-polarization as well as total intensity
#     channel - NB only does one channel! (default=0)
# timing - about 10s-1min on one reasonably compressed subband
# (I have tried several different algorithms e.g. masked data arrays,
# and all others take longer)


def listr (ms,utstart=0.0,utend=1.0E+11,datacolumn='DATA',\
           ndig=3,whichtype='amp',docross=False,c=0):

    a=inspect.stack()
    stacklevel=0
    for k in range (len(a)):
        if (string.find(a[k][1],'ipython console') >0):
            stacklevel=k
    myf=sys._getframe(stacklevel).f_globals
    myf['__last_task']='listr'
    myf['taskname']='listr'
    tb=myf['tb']

    try:
        tb.open(ms+'/ANTENNA')
        ants=tb.getcol('NAME')
        tb.close()
    except:
        ants=[]

    tb.open(ms,nomodify=True)
    ant1,ant2=tb.getcol('ANTENNA1'),tb.getcol('ANTENNA2')
    dat=tb.getcol(datacolumn)
    scan=tb.getcol('SCAN_NUMBER')
    flag=tb.getcol('FLAG')
    ifno=tb.getcol('DATA_DESC_ID')
    t=tb.getcol('TIME')/(24.0*3600.0)
    tb.close()

    uant = np.unique (np.append (ant1, ant2))
    uscan = np.unique (scan)
    uifno = np.unique (ifno)
    xant,xscan,xifno = xarray (uant),xarray (uscan),xarray (uifno)

    if whichtype[0]=='a':
        LL,RR=abs(dat[0][c]),abs(dat[3][c])
        if docross:
            LR,RL=abs(dat[1][c]),abs(dat[2][c])
    elif whichtype[0]=='p':
        LL=np.arctan2(dat[0][c].imag,dat[0][c].real)
        RR=np.arctan2(dat[3][c].imag,dat[3][c].real)
        if docross:
            LR=np.arctan2(dat[1][c].imag,dat[1][c].real)
            RL=np.arctan2(dat[2][c].imag,dat[2][c].real)
    else:
        print 'unknown datatype, allowed types are amp and phase'
        return
    
    ll = np.zeros ((len(uscan),len(uifno),len(uant),len(uant)))
    lli = np.zeros ((len(uscan),len(uifno),len(uant),len(uant)))
    cc = np.zeros ((len(uscan),len(uifno),len(uant),len(uant)))
    cci = np.zeros ((len(uscan),len(uifno),len(uant),len(uant)))

    for i in xrange (dat.shape[2]):
        if 10*i/dat.shape[2] != 10*(i-1)/dat.shape[2]:
            sys.stdout.write('.')
            sys.stdout.flush()
        if t[i]<utstart or t[i]>utend:
            continue
        zant1,zant2 = xant[ant1[i]],xant[ant2[i]]
        zscan = xscan[scan[i]]
        zifno = xifno[ifno[i]]
        if not flag[0][c][i]:
            if lli[zscan,zifno,zant1,zant2]:
                f = lli[zscan,zifno,zant1,zant2]
                ll[zscan,zifno,zant1,zant2] = (ll[zscan,zifno,zant1,zant2]*f+LL[i])/(f+1.)
            else:
                ll[zscan,zifno,zant1,zant2] = LL[i]
            lli[zscan,zifno,zant1,zant2] += 1.0
        if not flag[3][c][i]:
            if lli[zscan,zifno,zant2,zant1]:
                f = lli[zscan,zifno,zant2,zant1]
                ll[zscan,zifno,zant2,zant1] = (ll[zscan,zifno,zant2,zant1]*f+RR[i])/(f+1.)
            else:
                ll[zscan,zifno,zant2,zant1] = RR[i]
            lli[zscan,zifno,zant2,zant1] += 1.0
        if docross:
            if not flag[1][c][i]:
                if cci[zscan,zifno,zant1,zant2]:
                    f = cci[zscan,zifno,zant1,zant2]
                    cc[zscan,zifno,zant1,zant2] = (cc[zscan,zifno,zant1,zant2]*f+LR[i])/(f+1.)
                else:
                    cc[zscan,zifno,zant1,zant2] = LR[i]
                cci[zscan,zifno,zant1,zant2] += 1.0
            if not flag[2][c][i]:
                if cci[zscan,zifno,zant2,zant1]:
                    f = lli[zscan,zifno,zant2,zant1]
                    cc[zscan,zifno,zant2,zant1] = (cc[zscan,zifno,zant2,zant1]*f+RL[i])/(f+1.)
                else:
                    cc[zscan,zifno,zant2,zant1] = RL[i]
                cci[zscan,zifno,zant2,zant1] += 1.0

    for i in range(len(uscan)):
        for j in range(len(uifno)):
            if ll[i][j].max()==0:
                print 'No data'
                break
            fac=10.0**(float(ndig)-np.ceil(np.nanmax(np.log10(ll[i][j]))))
            print 'scan %d: IF %d: fluxes *%d = Jy\n' % (i,j,fac)
            ill= np.asarray(ll*fac,dtype='i4')
            printarray (ill[i][j],ndig,uant,ants)


    if docross:
        print '\nCross-hands:\n'
        for i in range(len(uscan)):
            for j in range(len(uifno)):
                if cc[i][j].max()==0:
                    print 'No data'
                    break
                fac=10.0**(float(ndig)-np.ceil(np.nanmax(np.log10(cc[i][j]))))
                print 'scan %d: IF %d: fluxes *%d = Jy\n' % (i,j,fac)
                icc= np.asarray(cc*fac,dtype='i4')
                printarray (icc[i][j],ndig,uant,ants)
#    return ill
                
