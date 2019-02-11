# -*- coding: utf-8 -*-
"""
Created on Thu Dec 06 03:26:07 2018

@author: mmacferrin
"""

'''We ran a bunch of test cases in Test_cases.py.  Let's cherry-pick the best ones and combine them here.'''


#######################################################################################
## Code for importing the parent directory in order to get the File_Locations object
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
## Also add the utility folder for the csv names
utilitydir = os.path.join(parentdir, "UTILITIES")
sys.path.insert(0,utilitydir)
#######################################################################################

img_dir = os.path.join(parentdir, "ASIFT_Images/temp_scratch")
img_src = os.path.join(img_dir, "CA228132V0108_CROPPED_8_curves.tif")
img_tar = os.path.join(img_dir, "W01_4_clipped.jpg")

import os
import numpy
import PHASE_3_RANSAC_FILTERING.ASIFT_drawMatches as DRAW_MATCHES
from CSV_auto_reader import read_simple_csv
from CSV_writer import write_csv

# Read in all the filtered CSV files.
csv_filtered_files = [os.path.join(img_dir,p) for p in os.listdir(img_dir) if ((p.find("data_matches_COMBINED_take") >= 0) and (os.path.splitext(p)[-1] == ".csv"))]

csv_data = []
# Combine it into a big master dataset.
for csv_filtered in csv_filtered_files:
    filtered_data = read_simple_csv(csv_filtered)
    csv_data.append(filtered_data)
    print filtered_data.dtype

csv_data_combined_temp = numpy.concatenate(csv_data)

# Filter out duplicate points
csv_data_combined = []
eps = 0.5
for kp2 in csv_data_combined_temp:
    include_flag = True
    for kp1 in csv_data_combined:
        if ((kp1["x1"] - eps) <= kp2["x1"] <= (kp1["x1"] + eps)) and \
           ((kp1["y1"] - eps) <= kp2["y1"] <= (kp1["y1"] + eps)) and \
           ((kp1["x2"] - eps) <= kp2["x2"] <= (kp1["x2"] + eps)) and \
           ((kp1["y2"] - eps) <= kp2["y2"] <= (kp1["y2"] + eps)):
            include_flag = False
            break

    if include_flag:
        csv_data_combined.append(kp2)

csv_data_combined = numpy.array(csv_data_combined, dtype=csv_data_combined[0].dtype)

csv_file_combined = os.path.join(img_dir, "data_matches_COMBINED_FINAL.csv")
csv_img_combined = os.path.splitext(csv_file_combined)[0] + ".png"
write_csv(csv_data_combined, csv_file_combined, verbose=True)

DRAW_MATCHES.drawMatches_from_file(img_src, img_tar,
                                   csv_file_combined,
                                   csv_img_combined,
                                   verbose=True)
