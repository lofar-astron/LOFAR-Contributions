import os
import glob
import numpy
import lofar.parmdb
import numpy as numpy
import math
import lofar.expion.parmdbmain
from   scipy import *

def demix (infile, remove, target='target', timestep=10, freqstep=60):

#
#  wrapper routine to Bas vdTol's demixing scripts
#
#  problems/complaints: neal.jackson@manchester.ac.uk
#  further modified by R van Weeren, rvweeren@strw.leidenuniv.nl
# args: infile  MS to be demixed
#       remove  list of stuff to remove eg ['CygA','CasA'] 
#       target  name of target  (default 'target')
#
# invocation within python: import do_demix
#                           do_demix.demix('infile',['remove1','remove2'],'target_name')
#
#  *** NOTE: assumes that the MS to be demixed has a 'uv' in the middle of it!!!
#  *** NOTE: you need to "use LofIm" before starting (only tcsh working tested!!!)  
#  *** NOTE: do not run two demixing sessions in the same directory in parallel!!
# --------------------------------------------------------------------------
# edit the following two lines
#
    demixdir   = '/home/weeren/scripts/demixingfast/'
    clusterdesc= '/home/weeren/full.clusterdesc'
    skymodel   = '/home/weeren/scripts/Ateam_LBA_CC.skymodel'
    startchan  = '2'  # 2 usually ok
    half_window= 20  # integer window size of median filter, 20 is a good choice
    threshold  = 2.5  # solutions above/below threshold*rms are smoothed, 2.5 is a good choice
                      
# edit above 
# -----------------------------------------------------------

    key        = 'key_'+ infile     
    mixingtable= 'mixing_' + infile 
    basename   =  infile.replace('_uv.MS', '') + '_' 
    os.system ('cp -f ' + demixdir + '/smoothdemix.py .')
    os.system ('cp -f ' + demixdir + '/median_filter.py .')
    import smoothdemix
    import median_filter
    
#  run NDPPP to preflag input file out to demix.MS

    f=open(basename + 'NDPPP_dmx.parset','w')
    f.write('msin = %s\n' % infile)
    f.write('msin.autoweight = True\n')
    f.write('msin.startchan = ' + startchan + '\n')       # update if needed !!
    f.write('msin.nchan = %d\n' % freqstep)
    mstarget = infile.replace('uv',target)
    f.write('msout = %s\n' % mstarget)
    f.write('steps=[preflag]\n')
    f.write('preflag.type=preflagger\n')
    f.write('preflag.corrtype=auto\n')
    f.close()

    os.system ('use LofIm')  # update if needed
    os.system ('rm -f -r '+mstarget)
    os.system ('NDPPP ' + basename + 'NDPPP_dmx.parset')

# modify Bas's shiftphasecenter.py to cope with these data
# substitute appropriate things between the two lines with "edit" in them
# put in a dummy target and then use len(targets)-1 in case we only have one
#
    dowrite = 1
    f = open (demixdir+'shiftphasecenter.py','r')
    fo = open (basename + 'tmp_shiftphasecenter.py','w')
    
    for i in f:
        if dowrite:
            if 'for target in range' in i:
                fo.write('for target in range(len(targets)-1):')
            else:
                fo.write(i)
        if 'edit' in i:
            dowrite = 1-dowrite
            if not dowrite:
                fo.write('msname = \'%s\'\n' % mstarget)
                fo.write('targets = ( ')
                for j in range(len(remove)):
                    if remove[j]=='CasA':
                        fo.write('(\'CasA\',6.123487680622104,  1.0265153995604648),\n')
                    elif remove[j]=='CygA':
                        fo.write('(\'CygA\',5.233686575770755,  0.7109409582180791),\n')
                    elif remove[j]=='TauA':
                        fo.write('(\'TauA\',1.4596748493730913, 0.38422502335921294),\n')
                    elif remove[j]=='HerA':
                        fo.write('(\'HerA\',4.4119087330382163, 0.087135562905816893),\n')
                    elif remove[j]=='VirA':
                        fo.write('(\'VirA\',3.276086511413598,  0.21626589533567378),\n')
                    elif remove[j]=='HydA':
                        fo.write('(\'HydA\',2.4351466,         -0.21110706),\n')
                    elif remove[j]=='PerA':
                        fo.write('(\'PerA\',0.87180363,         0.72451580),\n')                        
                        
                fo.write ('(\'dummy\', 0.0, 0.00))\n')
                fo.write('N_channel_per_cell = %d\n' % freqstep)
                fo.write('N_time_per_cell = %d\n' % timestep)


    f.close()
    fo.close()

    print 'Removing targets '+str(remove)+' from '+mstarget
    #import tmp_shiftphasecenter
    os.system('python '+ basename + 'tmp_shiftphasecenter.py')
# for each source to remove, and the target, do a freq/timesquash NDPPP

    removeplustarget = numpy.append (remove, target)

    for i in removeplustarget:
        os.system ('rm -f ' + basename + 'dmx_avg.parset')
        f=open(basename + 'dmx_avg.parset','w')
        msin = infile.replace('uv',i)
        f.write('msin = %s\n' % msin)
        msout = msin.replace ('.MS','_avg.MS')
        f.write('msout = %s\n' % msout)
        f.write('steps=[avg]\n')
        f.write('avg.type = averager\n')
        f.write('avg.timestep = %d\n' % timestep)
        f.write('avg.freqstep = %d\n' % freqstep)
        f.close()
        print 'Squashing '+msin+' to '+msout
        os.system ('rm -f -r '+msout)
        os.system ('NDPPP '+ basename + 'dmx_avg.parset')
#
# edit Bas's demixing.py and run it on each of the avg files
# assume multiple hashes represent start and end of the bit to edit
#
    dowrite = 1
    f = open (demixdir+'demixing.py','r')
    fo = open (basename + 'tmp_demixing.py','w')
    for i in f:
        if dowrite:
            fo.write(i)
        if '#######' in i:
            dowrite = 1-dowrite
            if not dowrite:
                fo.write ('mixingname=\'' + mixingtable + '\'\n')
                fo.write ('msname = \''+mstarget+'\'\n')
                fo.write ('avg_msnames = [')
                for j in range(len(removeplustarget)):
                    msin = infile.replace('uv',removeplustarget[j])
                    msout = msin.replace ('.MS','_avg.MS')
                    msdem = msin.replace ('.MS','_avg_dem.MS')
                    os.system ('rm -f -r '+msdem)
                    fo.write('\''+msout+'\'')
                    if j == len(removeplustarget)-1:
                        fo.write(']\n')
                    else:
                        fo.write(',\n')
                fo.write('N_channel_per_cell = %d\n' % freqstep)
                fo.write('N_time_per_cell = %d\n' % timestep)
                fo.write('N_pol = 4\n')



    fo.close()
    f.close()

    print '****************************************************\n\n'
    print '     Running the demixing algorithm\n'
    print '\n\n****************************************************\n'

    #import tmp_demixing
    os.system('python ' + basename + 'tmp_demixing.py')

    print '****************************************************\n\n'
    print '     Finished the demixing algorithm, beginning BBS... \n'
    print '\n\n****************************************************\n'

#
#  run BBS on the demixed measurement sets
#
    for i in remove:
        print 'Doing: ', i
        msin = infile.replace('uv', i)
        msout = msin.replace ('.MS','_avg_dem.MS')  
#
# nb not _avg.MS as in instructions
#
        os.system ('rm -f -r '+ basename + i +'.vds')
        os.system ('rm -f -r '+ basename + i +'.gds')
        print 'Create vds & gds files....'
        os.system ('makevds '+clusterdesc+' '+msout+' '+ basename + i +'.vds')
        os.system ('combinevds '+ basename + i +'.gds '+ basename + i +'.vds')
        command='calibrate -f --key '+ key + ' --cluster-desc '+clusterdesc+' --db ldb001 --db-user postgres '+ basename + i+'.gds '+demixdir+'bbs_'+i+'.parset '+skymodel+' $PWD'
        print command
        os.system(command)

        input_parmdb = msout + '/instrument'
        output_parmdb= msout + '/instrument_smoothed'
        smoothdemix.smoothparmdb(input_parmdb,output_parmdb, half_window, threshold)
        command='calibrate --clean --skip-sky-db --skip-instrument-db --instrument-name instrument_smoothed --key '+ key + ' --cluster-desc '+clusterdesc+' --db ldb001 --db-user postgres '+ basename + i +'.gds '+demixdir+'bbs_'+i+'_smoothcal.parset '+skymodel+' $PWD'
        print command
        os.system(command)


#
#  edit Bas's subtract_from_averaged.py and run it
#  again put a dummy in mspredictnames to get the right dimensions
#  and then nadger the indices in the tmp_subtract.py file
#
    dowrite = 1
    f = open (demixdir+'subtract_from_averaged.py','r')
    fo = open (basename + 'tmp_subtract.py','w')
    for i in f:
        if dowrite:
            fo.write(i.replace('mspredictnames','mspredictnames[0:len(mspredictnames)-1]'))
        if '#######' in i:
            dowrite = 1-dowrite
            if not dowrite:
                fo.write ('msname = \''+mstarget.replace('.MS','_avg.MS')+'\'\n')
                fo.write ('mixingname=\'' + mixingtable + '\'\n')
                fo.write ('mspredictnames = (')    # BUG from (\'' --> ('
                for j in range(len(remove)):
                    fo.write("'"+infile.replace('uv',remove[j]+'_avg_dem')+'\'')  # BUG ADD +"'"
                    if j==len(remove)-1:
                        fo.write(')\n')
                        #fo.write(',\'dummy\')\n')
                    else:
                        fo.write(',')          
                fo.write ('msnameout = \''+mstarget.replace('.MS','_sub.MS')+'\'\n')
    fo.close()
    f.close()
    os.system('rm -f -r '+mstarget.replace('.MS','_sub.MS'))
    
    os.system('python ' + basename + 'tmp_subtract.py')
    #import tmp_subtract # does not work some table is still open apparently
