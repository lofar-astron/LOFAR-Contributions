# Unmaintained LOFAR analysis scripts

These scripts were written by the LOFAR community and are not actively maintained. They can be claimed for maintenance by an interested user.

* coordinates_mode.py: routines to work with astronomical coordinates
* plot.py: inspect gain solutions
* solfetch.py: modules required for solflag.py
* solflag.py: carries out solution-based flagging
* solplot.py: modules required for solflag.py
* uvcoverage.py: plots the uv coverage for a Measurement
* plot_flags.py: plots ``images'' of frequency versus time on a baseline-by-baseline basis, with the pixel values equal to the visibility amplitudes
* img2fits.py: converts CASA images to fits images
* compare_gaincal.py: plots CASA and BBS gain solutions against each other for comparison. It can also plot CASA vs CASA and BBS vs BBS. Only supports gain solutions, and only if a solution was computed for each integration time
* traces.py: plots L,M tracks for the zenith, azimuth and elevation of the NCP, CasA, CygA, and the target against time for a given MS or time range. Observer location is fixed to Dwingeloo. It is easy to add other sources of interest, or to modify
 the observer location, but it does require editing the Python code. The script is useful to check the elevation of possible interfering sources like CasA and CygA
* casapy2bbs: written by Joris van Zwieten. Converts a clean component image produced by casa into a skymodel file readable by BBS. See also modelclip.py.
* plotElevation.py: given a Measurement Set, plots the elevation of the target source as a function of time
* split_ms_by_time.py: extracts part of a Measurement Set (selected by timerange) and writes out to a new Measurement Set. Optionally excludes selected antennas.
* uvrms.py: performs RM Synthesis on the data in a Measurement Set. 
* fixlofaruvw.py: corrects the faulty UVW column header. Use this on all data sets recorded before 20/03/2011 to get the astrometry correct. This script changes the MEASINFO.Ref label in the UVW column to J2000.
* do_demixing.py: applies the demixing routine from Bas vdTol to the data to get rid of the A-team sources. The instructions are at the top of the file.
* CutBeamFromSkyModel.py: given a skymodel, it produces two sub-skymodels, the first containing all the components within a particular radius from a given coordinate, the second all the rest.
* flagnancorrected.py: it searches CORRECTED\_DATA column for NaN and flags them.
* flagnandata.py: it searches DATA column for NaN and flags them.
