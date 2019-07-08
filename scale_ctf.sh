#!/bin/bash

#########################################################################################
#
# Description: Script to (approximately) correct defocus values for different angpix
# Max Wilkinson, MRC LMB
#
########################################################################################
# Approximately = +/- 20A or so ###
###################################

proc_name=$(echo $0 | gawk '{n=split($1,scr,"/");print scr[n];}')

if [ $# -eq 0 ]
    then
    echo "This program will scale defocus U, defocus V and magnification based on starting and new apix values."
    echo "Usage:           $proc_name <data file>"
    echo "User will then be prompted for apix values"
    exit 1
fi



echo -n "Starting apix: "
read apix1
echo -n "New apix: "
read apix2
#apix1=1.43
#apix2=1.38

rlnDefocusUIndex=$(gawk 'NF < 3 && /_rlnDefocusU/{print $2}' $1 | cut -c 2-)
rlnDefocusVIndex=$(gawk 'NF < 3 && /_rlnDefocusV/{print $2}' $1 | cut -c 2-)
rlnMagnificationIndex=$(gawk 'NF < 3 && /_rlnMagnification/{print $2}' $1 | cut -c 2-)
rlnSphericalAberrationIndex=$(gawk 'NF < 3 && /_rlnSphericalAberration/{print $2}' $1 | cut -c 2-)
rlnVoltageIndex=$(gawk 'NF < 3 && /_rlnVoltage/{print $2}' $1 | cut -c 2-)

output_file=$(echo $1 | sed 's/.star/_newapix.star/')



cs=$(head -200 $1 | gawk "/mrc/ {print \$$rlnSphericalAberrationIndex}" | sort | uniq | gawk '{printf "%.f",10000000 * $1}')
#echo $cs
#cs=27000000
echo "Read spherical aberration as" $cs "A from star-file header"

kv=$(head -200 $1 | gawk "/mrc/ {print \$$rlnVoltageIndex}" | sort | uniq | xargs printf %.f)
#kv=300
if [ $kv == "300" ]; then
    lambda=0.0197
elif [ $kv == "200" ]; then
    lambda=0.0251
else
    echo "Acceleration voltage not 200 or 300 keV, please modify script to allow use of correct electron wavelength"
    exit 1
fi
echo "Accelration voltage read as" $kv", will use electron wavelength of" $lambda "A"


#Fudge factor: average-ish spatial resolution (A) for applying constant correction. This value is a bit arbitrary, something like 5-7A works ok. The correction involved is only about 20A, i.e. about 0.1 percent of the defocus
avgS=5.68

varC=$(gawk "BEGIN {printf \"%.6f\",-0.5*${cs}*${lambda}**2}")
alpha=$(gawk "BEGIN {printf \"%.6f\",${apix1}/${apix2}}")
alpha2=$(gawk "BEGIN {printf \"%.6f\",${alpha}**2}")

const=$(gawk "BEGIN {printf \"%.6f\",${varC}*${alpha}**2 - ${varC}/${alpha}**2}")
correction=$(gawk "BEGIN {printf \"%.6f\",${const}/${avgS}**2}")

echo "Defocus rescaled  by" $alpha2 "plus a constant correction of" $correction 


gawk "BEGIN{OFS = \"\t\"} NF>3 {
       \$$rlnDefocusUIndex=sprintf(\"%.6f\",\$${rlnDefocusUIndex}/${alpha2} - ${correction})
       \$$rlnDefocusVIndex=sprintf(\"%.6f\",\$${rlnDefocusVIndex}/${alpha2} - ${correction})
       \$$rlnMagnificationIndex=sprintf(\"%.6f\",\$${rlnMagnificationIndex} * ${alpha})
}1" $1 > $output_file
echo "Wrote out" $output_file
