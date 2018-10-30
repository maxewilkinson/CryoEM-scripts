#!/bin/bash

###############
# Make coordinate files from _data.star
# Max Wilkinson
# #############

if [ $# -eq 0 ]
    then
    echo "Usage:        $0 run_data.star <2dmatch>"
    exit 1
fi

if [ -z "$2" ]
    then
    match=2dmatch
    else
    match=$2
fi


Xidx=`gawk 'NF < 3 && /_rlnCoordinateX/{print $2}' $1 | cut -c 2-`
Yidx=`gawk 'NF < 3 && /_rlnCoordinateY/{print $2}' $1 | cut -c 2-`
Micidx=`gawk 'NF < 3 && /_rlnMicrographName/{print $2}' $1 | cut -c 2-`
Classidx=`gawk 'NF < 3 && /_rlnClassNumber/{print $2}' $1 | cut -c 2-`
FOMidx=`gawk 'NF < 3 && /_rlnAutopickFigureOfMerit/{print $2}' $1 | cut -c 2-`

Mics=$(gawk "NF > 3 {print \$$Micidx}" $1 | sort | uniq)

for mic in $Mics; do 
out=`echo $mic | sed "s/.mrc/_"$match".star/"`

echo '
data_

loop_
_rlnCoordinateX #1
_rlnCoordinateY #2
_rlnClassNumber #3
_rlnAutopickFigureOfMerit #4
' > $out

gawk -v m="$mic" "\$$Micidx == m {print \$$Xidx, \$$Yidx, \$$Classidx, \$$FOMidx}" $1 >> $out

echo "Wrote $out"
done

