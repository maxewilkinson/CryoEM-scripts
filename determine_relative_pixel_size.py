#!/usr/bin/env python
# coding: utf-8

"""
determine_pixel_size
---------

Script to determine relative pixel size of map to map by FSC in RELION. 

Authors: Ana Casañal, Thomas G. Martin & Takanori Nakane
License:GPLv3

"""

import argparse
import numpy as np
import subprocess
from collections import OrderedDict

parser = argparse.ArgumentParser(description='')

parser.add_argument('--ref_map',nargs='?', help='filename of the reference map of which the pixel size is known',type=str)
parser.add_argument('--angpix_ref_map',nargs='?', help='pixel size in Å of the reference map. Will be used as fixed reference',type=float)
parser.add_argument('--map',nargs='?', help='filename of map of which the pixel size is not known',type=str)
parser.add_argument('--angpix_map_nominal',nargs='?', help='Starting pixel size in Å of the map that needs the pixel size to be determined. Will be used as a starting point to search for the relative pixel size.',type=float)
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

def load_mrc(filename, maxz=9999): 
	inmrc = open(filename, "rb") 
	header_int = np.fromfile(inmrc, dtype=np.uint32, count=256) 
	inmrc.seek(0, 0) 
	header_float = np.fromfile(inmrc, dtype=np.float32, count=256) 

	nx, ny, nz = header_int[0:3] 
	eheader = header_int[23] 
	mrc_type = None 
	if header_int[3] == 2: 
		mrc_type = np.float32 
	elif header_int[3] == 6: 
		mrc_type = np.uint16 
	nz = np.min([maxz, nz]) 

	inmrc.seek(1024 + eheader, 0) 
	map_slice = np.fromfile(inmrc, mrc_type, nx * ny * nz).reshape(nz, ny, 
	nx).astype(np.float32) 

	return nx, ny, nz, map_slice 


def determine_fsc_dropoff_point (ref_map, map2, angpix_ref_map, angpix_map_2, box_map):

	fsc_aims = [0.5,0.4,0.3,0.2]

	if (map2.find('.mrc') >= 0):
		tmp_output_name = map2.replace('.mrc','_tmp.mrc')
		tmp_fsc_output_name = map2.replace('.mrc','_tmp_fsc.star')
	else:
		tmp_output_name = map2 + '_tmp.mrc'
		tmp_fsc_output_name = map2  + '_tmp_fsc.star'
	subprocess.check_output(['relion_image_handler','--i', map2, '--o', tmp_output_name, '--angpix', str(angpix_map_2), '--rescale_angpix', str(angpix_ref_map), '--new_box', str(box_map), '--shift_com'])
	star = subprocess.check_output(['relion_image_handler', '--i', ref_map, '--angpix', str(angpix_ref_map), '--fsc', tmp_output_name])
	f = open(tmp_fsc_output_name, "w") 
	f.write(star) 
	f.close() 
	fsc_star = load_star(tmp_fsc_output_name)
	fsc_sum = 0
	for fsc_aim in fsc_aims:
		fsc_sum = fsc_sum + get_fsc_dropoff_point_in_star(fsc_star, fsc_aim)
	return fsc_sum/len(fsc_aims)


def get_fsc_dropoff_point_in_star (fsc_star, fsc_aim):
	fsc_list = fsc_star['fsc']['rlnFourierShellCorrelation']
	res_list = fsc_star['fsc']['rlnAngstromResolution']
	i_threshold = 0
	i = 0
	fsc_above_threshold = True
	for fsc in fsc_list:
		if fsc_above_threshold and (float(fsc) > fsc_aim):
			i_threshold = i
		elif (fsc_above_threshold) and (float(fsc) > -0.5):
			return interpolate(float(res_list[i_threshold]),float(res_list[i]),float(fsc_list[i_threshold]),float(fsc_list[i]),fsc_aim)
			fsc_above_threshold = False
		i = i + 1
	return float(res_list[-1])

def interpolate (x1, x2, y1, y2, y_goal):
	try:
		return x1+((x2-x1)*(y1-y_goal)/(y1-y2))
	except ZeroDivisionError:
		return 999

print("determine_relative_pixel_size.py GPL 2019")

ref_map = args.ref_map
angpix_ref_map = args.angpix_ref_map
map2 = args.map
angpix_map_nominal = args.angpix_map_nominal


nx, ny, nz, _ = load_mrc(ref_map) 
box_map = nx


if (map2.find('.mrc') >= 0):
	tmp_output_name = ref_map.replace('.mrc','_tmp.mrc')
else:
	tmp_output_name = ref_map + '_tmp.mrc'

subprocess.check_output(['relion_image_handler','--i', ref_map, '--o', tmp_output_name, '--shift_com'])
ref_map = tmp_output_name

initial_step_range = 3
step_sizes = [0.1, 0.05, 0.02, 0.01, 0.005, 0.002]

angpix_start = angpix_map_nominal - (initial_step_range * step_sizes[0]) - step_sizes[0]
angpix_end = angpix_map_nominal + (initial_step_range * step_sizes[0]) 


angpix_list = []
res_list = []
for step_size in step_sizes:
	print ("------------------")
	print("step: " + str(step_size) + " range: " + str(angpix_start) + " - " + str(angpix_end))
	print ("------------------")
	
	angpix = angpix_start
	while angpix <= angpix_end:
		res = determine_fsc_dropoff_point(ref_map, map2, angpix_ref_map, angpix, box_map)
		print("angpix: " + str(angpix) + " fsc: " + str(res))
		angpix_list.append(angpix)
		res_list.append(res)

		angpix = round(angpix + step_size,5)
	
	min_res = res_list[0]
	index_start = 0
	index_end = 0
	best_index_start = 0
	best_index_end = 0
	for k in range(len(res_list)-1):
		i = k + 1
		if (res_list[i] < min_res):
			min_res = res_list[i]
			index_start = i -1
			index_end = i + 1
			best_index_start = i
			best_index_end = i
		elif (res_list[i] == min_res):
			index_end = i + 1
			best_index_end = i

	estimate_pixel_size = angpix_list[best_index_start] + (angpix_list[best_index_end] - angpix_list[best_index_start])/2
	if (best_index_end == best_index_start):
		print ("------------------")
		print ("BEST:" + str(estimate_pixel_size))
	else:
		print ("------------------")
		print ("BEST:" + str(estimate_pixel_size) + " range: " + str(angpix_list[best_index_start]) + " - " + str(angpix_list[best_index_end]))

	if (index_end > len(res_list)-1):
		index_end = len(res_list)-1
	angpix_start = angpix_list[index_start]
	angpix_end = angpix_list[index_end]
	res_start = res_list[index_start]

	angpix_list = []
	res_list = []
	angpix_list.append(angpix_start)
	res_list.append(res_start)















