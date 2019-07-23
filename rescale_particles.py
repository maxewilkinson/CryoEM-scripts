#!/usr/bin/env python
# coding: utf-8

"""
rescale_particles
---------

Script to rescale particles

Authors: Thomas G. Martin & Takanori Nakane
License: GPLv3

"""

import argparse
import numpy as np
import subprocess
from collections import OrderedDict

parser = argparse.ArgumentParser(description='')

parser.add_argument('--i',nargs='?', help='input filename',type=str)
parser.add_argument('--o',nargs='?', help='output filename',type=str)
parser.add_argument('--pix_nominal',nargs='?', help='Nominal pixel size. This is the pixel size that was used for the relion run of the original star file with the particle coordinates.',type=float)
parser.add_argument('--pix_relative',nargs='?', help='The ralative pixel size in comparison to the dataset that this data should be merged with. This can be determined e.g. by cross correlating 2 maps.',type=float)
parser.add_argument('--pix_target',nargs='?', help='Target pixel size. Pixel size you want it rescaled to.',type=float)
parser.add_argument('--mrc_name_path',nargs='?', help='Path to mrc files (including last /)',type=str)
parser.add_argument('--mrc_name_prefix',nargs='?', help='mrc prefix that is differnt to the original (including _).',type=str)
parser.add_argument('--mrc_name_suffix',nargs='?', help='mrc suffix that is differnt to the original (including _). If you need to use a - in the beginning use = and the string in \' instead of space (e.g. --mrc_name_suffix=\'-example\').',type=str)
parser.add_argument('--mrc_name_replacement_in',nargs='?', help='Part of the mrc name that is changed. If you need to use a - in the beginning use = and the string in \' instead of space (e.g. --mrc_name_replacement_in=\'-example\').',type=str)
parser.add_argument('--mrc_name_replacement_out',nargs='?', help='Replacement part for the changed part. If you need to use a - in the beginning use = and the string in \' instead of space (e.g. --mrc_name_replacement_out=\'-example\').',type=str)
args = parser.parse_args()

def load_star(filename):
    from collections import OrderedDict
    
    datasets = OrderedDict()
    current_data = None
    current_colnames = None
    
    in_loop = 0 # 0: outside 1: reading colnames 2: reading data

    for line in open(filename):
        line = line.strip()
        
        # remove comments
        comment_pos = line.find('#')
        if comment_pos > 0:
            line = line[:comment_pos]

        if line == "":
            continue

        if line.startswith("data_"):
            in_loop = 0

            data_name = line[5:]
            current_data = OrderedDict()
            datasets[data_name] = current_data

        elif line.startswith("loop_"):
            current_colnames = []
            in_loop = 1

        elif line.startswith("_"):
            if in_loop == 2:
                in_loop = 0

            elems = line[1:].split()
            if in_loop == 1:
                current_colnames.append(elems[0])
                current_data[elems[0]] = []
            else:
                current_data[elems[0]] = elems[1]

        elif in_loop > 0:
            in_loop = 2
            elems = line.split()
            assert len(elems) == len(current_colnames)
            for idx, e in enumerate(elems):
                current_data[current_colnames[idx]].append(e)        
        
    return datasets

def write_star(filename, datasets): 
	f = open(filename, "w") 

	for data_name, data in datasets.items(): 
		f.write( "\ndata_" + data_name + "\n\n") 

		col_names = list(data.keys())
		need_loop = isinstance(data[col_names[0]], list) 
		if need_loop: 
			f.write("loop_\n") 
			for idx, col_name in enumerate(col_names): 
				f.write("_%s #%d\n" % (col_name, idx + 1)) 

			nrow = len(data[col_names[0]]) 
			for row in range(nrow): 
				f.write("\t".join([data[x][row] for x in col_names])) 
				f.write("\n") 
		else: 
			for col_name, value in data.items(): 
				f.write("_%s\t%s\n" % (col_name, value)) 

		f.write("\n") 
	f.close() 


print("rescale_particles.py GPL 2019")

input_name = args.i
output_name = args.o
pix_a = args.pix_nominal
pix_o = args.pix_relative
pix_n = args.pix_target
starFile = load_star(input_name)

mrc_name_path = args.mrc_name_path
mrc_name_prefix = args.mrc_name_prefix
mrc_name_suffix = args.mrc_name_suffix
mrc_name_replacement_in = args.mrc_name_replacement_in
mrc_name_replacement_out = args.mrc_name_replacement_out


rlnMicrographName = starFile['']['rlnMicrographName']
corrected_rlnMicrographName = []
for name_with_path in rlnMicrographName:
	name = name_with_path
	while (name.find("/") >= 0):
		name = name[name.find("/")+1:]
	name = name.replace(".mrc","")
	if (mrc_name_replacement_in):
		if (mrc_name_replacement_out):
			name = name.replace(mrc_name_replacement_in,mrc_name_replacement_out)
		else :
			name = name.replace(mrc_name_replacement_in,"")
	new_name = ""
	if (mrc_name_path):
		new_name = new_name + mrc_name_path
	if (mrc_name_prefix):
		new_name = new_name + mrc_name_prefix
	new_name = new_name + name
	if (mrc_name_suffix):
		new_name = new_name + mrc_name_suffix
	new_name = new_name + ".mrc"

	corrected_rlnMicrographName.append(new_name)
rlnCoordinateX = starFile['']['rlnCoordinateX']
corrected_rlnCoordinateX = []
for x in rlnCoordinateX:
	corrected_rlnCoordinateX.append(str(round(float(x)*pix_o/pix_n,6)))
rlnCoordinateY = starFile['']['rlnCoordinateY']
corrected_rlnCoordinateY = []
for x in rlnCoordinateY:
	corrected_rlnCoordinateY.append(str(round(float(x)*pix_o/pix_n,6)))
rlnOriginX = starFile['']['rlnOriginX']
corrected_rlnOriginX = []
for x in rlnOriginX:
	corrected_rlnOriginX.append(str(round(float(x)*pix_o/pix_n,6)))
rlnOriginY = starFile['']['rlnOriginY']
corrected_rlnOriginY = []
for x in rlnOriginY:
	corrected_rlnOriginY.append(str(round(float(x)*pix_o/pix_n,6)))
rlnMagnification = starFile['']['rlnMagnification']
corrected_rlnMagnification = []
for x in rlnMagnification:
	corrected_rlnMagnification.append(str(int(round(float(x)*pix_a/pix_n,0))))
rlnDetectorPixelSize = starFile['']['rlnDetectorPixelSize']


outFile = OrderedDict()
outFile['rlnMicrographName'] = corrected_rlnMicrographName
outFile['rlnCoordinateX'] = corrected_rlnCoordinateX
outFile['rlnCoordinateY'] = corrected_rlnCoordinateY
outFile['rlnOriginX'] = corrected_rlnOriginX
outFile['rlnOriginY'] = corrected_rlnOriginY
outFile['rlnMagnification'] = corrected_rlnMagnification
outFile['rlnDetectorPixelSize'] = rlnDetectorPixelSize
outputFile = OrderedDict()
outputFile[''] = outFile
write_star(output_name,outputFile)
