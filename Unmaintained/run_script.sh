#!/bin/bash 

# setup PYTHONPATH so it can find the pydal module

if [ -z "$PYTHONPATH" ]
then
  export PYTHONPATH=/app/usg/release/lib/python
else
  export PYTHONPATH=/app/usg/release/lib/python:${PYTHONPATH}

fi

echo ""
echo PYTHONPATH = ${PYTHONPATH}
echo ""

command='source /app/scripts/doPyrap'
# run the example
#command='python msinfo.py /lifs001/L2009_13427/SB0.MS'
#command='python closure.py SB27_FLG_7HR.MS 0 1 2 0 channel 0:14 0'
#command='python closure_rap.py   SB27_FLG_G.MS 0 0 0 channel 0:14 a 0'
#command='python closure_rap.py SB27_FLG_G_SECT1.MS'
command='python baseline_rap.py SB0_LBA_FLG_G.MS 0 0 0 channel 0:14 a 0'
#command='python autoflagger.py'
#command='python uvcoverage.py SB27_FLG.MS'
#command='python amp_diff.py SB0_FLG2.MS 1 2 2 3 0 channel  0'
#command='python data2ascii.py SB241.MS 1 2 0 50:55 test.txt'
echo ""
echo Running: ${command}
echo ""

$command
