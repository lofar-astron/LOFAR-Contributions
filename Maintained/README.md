# A list of maintained scripts

* Ateamclipper.py (Jose Sabater)
* avgpbz.py (George Heald)
* closure.py: prints closure phase vs time/elevation for selected antennas (George Heald)
* embiggen.csh: increases the size of plotted points in postscript files. Useful when producing ps output from e.g. uvplot.py. (George Heald)
* lin2circ.py: given a Measurement Set with a DATA column given in XX,XY,YX,YY correlations, converts to circular correlations RR,RL,LR,LL and writes them to a column in the Measurement Set. (George Heald)
* modelclip.py: sorts a skymodel file with respect to Stokes I flux, and truncates the list of sources such that N\% of the total flux is kept in the model (where N is specified on the command line). Useful for clean component skymodels produced by 
e.g. casapy2bbs. (George Heald)
* msHistory.py: prints information from the HISTORY table of a Measurement Set. Useful for obtaining a quick listing of the parset values used in e.g. NDPPP. (George Heald)
* uvcov.py: plots uv coverage for one or more Measurement Sets. If all Measurement Sets are for the same source at the same time (in other words are different subbands of the same observation), then use the '-s' option to save a lot of time. Do NOT
 use that option if the input Measurement Sets are not coincident in time. (George Heald)
* uvplot.py: plots data from a Measurement Set in several combinations, in a per-baseline fashion. Not as flexible as casaplotms, but should be faster. (George Heald)
* plot_Ateam_elevation.py: it makes plots of the elevation and angular distance of the Ateam and other sources (Sun, Jupiter) given a Measurement Set. (Bas van der Tol)
* modskymodel.py: it can shift skymodels by a given angular amount. It can manipulate skymodels also in other ways, like masking them and updating their spectral index values. More info at http://usg.lofar.org/forum/index.php?topic=712.0 (Francesco de Gasperin)
* mos.py (George Heald)
* listr_v2.py: it is a clone of the old AIPS matrix listing of data files. For the data or corrected-data column, it lists amplitudes (or phases) averaged by baseline over a specified time interval. It does also cross-hands and identifies the antennas. (Neal Jackson)
* fromsky.py: it converts a BBS skymodel file into the MODEL\_DATA column of a visibility dataset. (Neal Jackson)
