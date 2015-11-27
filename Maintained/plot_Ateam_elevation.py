#!/usr/bin/python
# -*- coding: utf-8 -*-



#
# Written by Bas van der Tol (vdtol@strw.leidenuniv.nl), March 2011.
# Updated by Tammo Jan Dijkema (dijkema@astron.nl), November 2014

from pylab import *
import pyrap.quanta as qa
import pyrap.tables as pt
import pyrap.measures as pm
import sys
import numpy
from matplotlib import dates
from matplotlib.ticker import MaxNLocator
from matplotlib.transforms import nonsingular
import datetime

targets = [ {'name' : 'CasA', 'ra' : 6.123487680622104,  'dec' : 1.0265153995604648},
            {'name' : 'CygA', 'ra' : 5.233686575770755,  'dec' : 0.7109409582180791},
            {'name' : 'TauA', 'ra' : 1.4596748493730913, 'dec' : 0.38422502335921294},
            {'name' : 'HerA', 'ra' : 4.4119087330382163, 'dec' : 0.087135562905816893},
            {'name' : 'VirA', 'ra' : 3.276086511413598,  'dec' : 0.21626589533567378},
            {'name' : 'HydraA', 'ra' : 2.4352, 'dec' : -0.21099},
            #{'name' : 'JUPITER'},
            {'name' : 'SUN'}]


if len(sys.argv) == 2:
   msname = sys.argv[1]
else:
   print "Usage"
   print "   plot_Ateam_elevation.py <msname>"
   

# Create a measures object
me = pm.measures()

# Open the measurement set and the antenna and pointing table

ms = pt.table(msname, ack=False)  

# Get the position of the first antenna and set it as reference frame
ant_table = pt.table(msname + '/ANTENNA', ack=False)  
ant_no = 0
pos = ant_table.getcol('POSITION')
x = qa.quantity( pos[ant_no,0], 'm' )
y = qa.quantity( pos[ant_no,1], 'm' )
z = qa.quantity( pos[ant_no,2], 'm' )
position =  me.position( 'wgs84', x, y, z )
me.doframe( position )
ant_table.close()


# Get the first pointing of the first antenna
field_table = pt.table(msname + '/FIELD', ack=False)
field_no = 0
direction = field_table.getcol('PHASE_DIR')
ra = direction[ ant_no, field_no, 0 ]
dec = direction[ ant_no, field_no, 1 ]
targets.insert(0, {'name' : 'Pointing', 'ra' : ra, 'dec' : dec})
field_table.close()


# Get a ordered list of unique time stamps from the measurement set
time_table = pt.taql('select DISTINCT TIME from $1', tables = [ms])
time = time_table.getcol('TIME')

time1 = time/3600.0
time1 = (time1 - floor(time1[0]/24)*24)*3600

time2 = map(datetime.datetime.fromtimestamp, time1)
time2 = dates.date2num(time2)

clf()

ra_qa  = qa.quantity( targets[0]['ra'], 'rad' )
dec_qa = qa.quantity( targets[0]['dec'], 'rad' )
pointing =  me.direction('j2000', ra_qa, dec_qa)

for target in targets:
   t = qa.quantity(time[0], 's')
   t1 = me.epoch('utc', t)
   me.doframe(t1)

   if 'ra' in target.keys():
      ra_qa  = qa.quantity( target['ra'], 'rad' )
      dec_qa = qa.quantity( target['dec'], 'rad' )
      direction =  me.direction('j2000', ra_qa, dec_qa)
   else:
      direction =  me.direction(target['name'])
  
   target['separation']=me.separation(pointing, direction)   

   # Loop through all time stamps and calculate the elevation of the pointing
   el = []
   for t in time:
      t_qa = qa.quantity(t, 's')
      t1 = me.epoch('utc', t_qa)
      me.doframe(t1)
      a = me.measure(direction, 'azel')
      elevation = a['m1']
      el.append(elevation['value']/pi*180)
   el = numpy.array(el)

   plot(time2, el)
   if target['name']!='Pointing':
     # Include separation after sources
     target['label']=target['name']+' ('+target['separation'].to_string("%0.0f")+')'
   else:
     target['label']=target['name']
   target['endpoint']=el[-1]

# get close-by labels after each other
for target in targets:
   for target2 in targets:
       if target['label']!="" and target2['label']!="" and target!=target2:
           if abs(target2['endpoint']-target['endpoint'])<3:
               target['label']=target['label']+', '+target2['label']
               target2['label']=''


# draw labels
for target in targets:
   text(time2[-1], target['endpoint'],'  '+target['label'])
     

class TimeLocator(mpl.ticker.LinearLocator, object):
    """ Tick locator to place ticks at nice intervals on a time axis 
        (multiples of 10, 15, 30 mins)
    """
    def __init__(self):
        LinearLocator.__init__(self)

    def __call__(self):
        'Return the locations of the ticks'
        vmin, vmax = self.axis.get_view_interval()
        vmin, vmax = nonsingular(vmin, vmax, expander = 0.05)
        if vmax<vmin:
            vmin, vmax = vmax, vmin

        if self.presets.has_key((vmin, vmax)):
            return self.presets[(vmin, vmax)]

        if self.numticks is None:
            self._set_numticks()

        if self.numticks==0: return []
        ticklocs = np.linspace(vmin, vmax, self.numticks)

        minnticks=4
        eps = 0.5/(24*60*60) # half a second to avoid rounding problems

        if vmax-vmin>1: # Days, default of TimeLocator is fine
            exponent, remainder = divmod(math.log10(vmax - vmin), 1)

            if remainder < 0.5:
                exponent -= 1
            scale = 10**(-exponent)
        elif vmax-vmin>minnticks*1./24: #Hours
            scale=1./24
        else:
            scales=[30,15,10,5,2,1]
            for s in scales:
                if vmax-vmin>minnticks*float(s)/(24*60):
                    scale=float(s)/(24*60)
                    break
                scale=float(1)/(24*60)

        vmin = math.floor(vmin/scale)*scale
        vmax = math.ceil(vmax/scale)*scale
        ticklocs = arange(vmin, vmax, scale+eps)

        return ticklocs



# Format the plot   
title('Elevation')
ylabel('Elevation');
xlim(time2[0],time2[-1])
xlabel('Time');
ax=subplot(111)

# Make the plot smaller to make room on the right for labels
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.75, box.height])

# Format axes
ylim(-30,90)
yticks(range(-30,91,15))

hfmt = dates.DateFormatter('%H:%M')
ax.xaxis_date()
ax.xaxis.set_major_locator(TimeLocator())
ax.xaxis.set_major_formatter(hfmt)
degree_sign= u'\N{DEGREE SIGN}'
ax.yaxis.set_major_formatter(FormatStrFormatter('%d'+degree_sign))

#savefig('elevation.eps')
show()
