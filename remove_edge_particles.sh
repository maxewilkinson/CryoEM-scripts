############################################################
# A script to remove particles from edges of micrographs   #
#         by Max Wilkinson, MRC-LMB Oct 2018               #
############################################################
#!/bin/bash

CLEAR='\033[0m'
RED='\033[0;31m'

function usage() {
    if [ -n "$1" ]; then
    echo -e "${RED}👉 $1${CLEAR}\n";
    fi
    echo "Usage: $0 [-x mic_x] [-y mic_y] [-box boxsize] [-tolerance tolerance level] [-i starfile] [-o starfile]"
    echo "  -x           Width of micrograph"
    echo "  -y           Height of micrograph"
    echo "  -box         Box size particles were extracted with"
    echo "  -tolerance   How much overlap in pixels is allowed between the box and edge of micrograph"
    echo "  -i           The star file to operate on"
    echo "  -o           Star file to write out"
    echo ""
    echo "Example: $0 -x 3838 -y 3710 -box 512 -tolerance 20 -i Extract/job413/particles.star -o particles_noedge.star"
    exit 1
} 


#defaults
mic_x=3838
mic_y=3710
box=512
tolerance=20
starfile=Extract/job413/particles.star
outstar=particles_test.star

# parse params
if [[ "$#" -eq 0 ]]; then
    usage
fi
while [[ "$#" > 1 ]]; do case $1 in
    -x|--x) mic_x="$2"; shift;shift;;
    -y|--y) mic_y="$2"; shift;shift;;
    -box|--box) box="$2"; shift;shift;;
    -tolerance|--tolerance) tolerance="$2"; shift;shift;;
    -i|--i) starfile="$2"; shift;shift;;
    -o|--o) outstar="$2"; shift;shift;;
    *) usage "Unknown parameter passed: $1"; shift;shift;;
esac; done


coord_x_idx=`awk '/_rlnCoordinateX/{split($2, a, "#"); print a[2]}' $starfile`
coord_y_idx=`awk '/_rlnCoordinateY/{split($2, a, "#"); print a[2]}' $starfile`


awk '{if (NF<= 2) {print} else \
{if ($'$coord_x_idx'>'$box'/2-'$tolerance' && \
     $'$coord_x_idx'<'$mic_x'-'$box'/2+'$tolerance' && \
     $'$coord_y_idx'>'$box'/2-'$tolerance' && \
     $'$coord_y_idx'<'$mic_y'-'$box'/2+'$tolerance' \
    ) {print}}}' $starfile > $outstar

