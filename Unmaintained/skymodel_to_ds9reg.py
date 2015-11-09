#THIS SCRIPT CONVERTS THE SOURCE CATALOG PRODUCED BY GSM.PY INTO A DS9
#REGION FILE. CREATED BY ALICIA BERCIANO ALBA, 14 FEB 2012 (V.1)

import os
import sys
from pylab import *
from scipy import *
from numpy import *



####################
# INPUT PARAMETERS #
####################

#file_path: directory where the skymodel file is located
#file_name: name of the skymodel_file
#file_extension: extension used to refer to a skymodel file 
#color: color of the regions

file_path = '/home/berciano/projects/voorwerp/catalogs/'
file_name = 'WENSS_0.9Jy'
file_extension = 'skymodel'
color     = 'red'

######################################################################

#Read the .skymodel file and extract the RA, DEC and source name information
file = open(file_name+'.'+file_extension, 'r')
lines = file.readlines()

RA  = []
DEC = []
SRC = []

for i in range(1,len(lines)):
    line = lines[i]
    line = line.split(',')
    ra   = line[2]
    dec  = line[3]
    src  = line[0]
    dec  = dec.replace(".",":",2)
    RA.append(ra)
    DEC.append(dec)
    SRC.append(src)


#Remove previously created region file (if exists) and make a new empy
#region file
reg=file_name+'.reg'
files = os.listdir(file_path)
if reg not in files:
    os.system('touch '+file_path+reg)
else:
    os.system('rm -f '+file_path+reg)
    os.system('touch '+file_path+reg)


#Create ds9 region file
regfile=open(file_path+reg,'a')
regfile.write('# Region file format: DS9 version 4.1 \n')
regfile.write('# Filename: '+file_path+file_name+' \n' )
regfile.write('global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1 \n')
regfile.write('fk5 \n')

for j in range(len(RA)):
    regfile.write('point('+RA[j]+','+DEC[j]+') # point=circle color='+color+' tag={'+SRC[j]+'} \n')
