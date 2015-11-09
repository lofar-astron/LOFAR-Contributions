#!/bin/tcsh -f

#
# Written by George Heald, heald@astron.nl, November 2010, Version 1.0 
#



# increase point size in a postscript file 
# assumes a pretty specific type of postscript file ....
# written by george heald 17/9/2009

alias MATH 'set \!:1 = `echo "\!:3-$" | bc -l`'

if ( $#argv == 1 ) then
  set multiply = 3
else if ( $#argv != 2 ) then
  echo "Two arguments required: input ps file and multiplication factor"
  echo "Second input defaults to 3 if not given."
  exit(1)
else
  set multiply = $2
endif

set outfile = emb_${1}
set ptsize = `cat ${1} | grep /MFAC | awk '{print $2}'`
echo $ptsize
set loopnumber = 0
cp $1 .tempfile.${loopnumber}.ps
foreach pts ( $ptsize )
        set oldnumber = $loopnumber
        @ loopnumber = $loopnumber + 1
        MATH newsize = $pts * $multiply
        echo ${loopnumber}: changing pointsize $pts to $newsize
        sed s/"${pts} def"/"${newsize} def"/ < .tempfile.${oldnumber}.ps  > .tempfile.${loopnumber}.ps
end
mv .tempfile.${loopnumber}.ps $outfile
\rm -f .tempfile.*
