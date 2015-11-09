#
#   fromsky (vis, model_file)
#
#   purpose: reads a BBS format sky model into the MODEL_DATA of a
#            visibility MS
#   version: 1, Neal Jackson, 2011.07.16, neal.jackson@manchester.ac.uk
#
#   use:   from fromsky import *; fromsky('vis-data','skymodel')
#   problems: the ft at the end takes a VERY long time (10 min per 100 comps)
#           currently no sanity checking - will crash if columns not found
#           I've only tested with point-component models so far
#
import sys
import os
import numpy as np
from numpy import ma
import casac
import inspect
import string
import ft

def fromsky (vis,model_file):
    a=inspect.stack()
    stacklevel=0
    for k in range (len(a)):
        if (string.find(a[k][1],'ipython console') >0):
            stacklevel=k
    myf=sys._getframe(stacklevel).f_globals
    myf['__last_task']='fromsky'
    myf['taskname']='fromsky'
    tb=myf['tb']
    cl=myf['cl']

    f=open(model_file)
    a='zzz'
    while not 'name' in a:    # assumes format string has '(Name' in it
        a=f.readline().lower().split('(')[1]
    a=a.split(')')[0].split(',')
    for i in range(len(a)):
        a[i]=a[i].strip()

    cra=cdec=cflux=ctype=cmaj=cmin=cpa=-1
    try:       # nb need essential four first
        cra=a.index('ra')
        cdec=a.index('dec')
        cflux=a.index('i')
        ctype=a.index('type')
        cmaj=a.index('majoraxis')
        cmin=a.index('minoraxis')
        cpa=a.index('orientation')
    except:
        pass

    while 1==1:
        a=f.readline().lower()
        if a=='':
            break
        if not 'point' in a and not 'gauss' in a:
            continue
        print a
        a=a.split(',')
        pos='J2000 '+a[cra].replace(':','h',1).replace(':','m',1)+' '+\
                   a[cdec].replace(':','d',1).replace(':','m',1)
        val=float(a[cflux])
        if 'point' in a[ctype]:
            cl.addcomponent(flux=val,fluxunit='Jy',dir=pos,shape='Point')
        if 'gauss' in a[ctype]:
            cl.addcomponent(flux=val,fluxunit='Jy',dir=pos,shape='Gaussian',\
                            majoraxis=a[cmaj]+'arcsec',minoraxis=a[cmin]+'arcsec',\
                            positionangle=a[cpa]+'deg')

    f.close()
    os.system('rm -f -r tmp_components.cl')
    cl.rename('tmp_components.cl')
    cl.close()
    ft.ft(vis=vis,complist='tmp_components.cl')
