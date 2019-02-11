# -*- coding: utf-8 -*-
"""
Created on Thu Dec 06 00:51:13 2018

@author: mmacferrin
"""

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

# Let's try this on our test images.

import os
import shutil
import ASIFT_Executable as ASIFT
import PHASE_3_RANSAC_FILTERING.ASIFT_RANSAC_filter as RANSAC
import PHASE_3_RANSAC_FILTERING.ASIFT_drawMatches as DRAW_MATCHES

for i in range(100):

    exe = ASIFT.ASIFT_Executable(img_dir, im1_gdal=img_src, im2_gdal=img_tar)
    exe.execute(verbose=True)

    keypoints_fname = os.path.join(img_dir, "data_matches.csv")
    output_csv_name = os.path.join(img_dir, "data_matches_FILTERED.csv")

    output_img_name = os.path.join(img_dir, "output_hori_FILTERED.png")

    RANSAC.filter_ASIFT_matches(keypoints_fname,
                                output_CSV=output_csv_name,
                                output_good_points_only=True,
                                verbose = True,
                                eliminate_nodata_matches = True,
                                img1_filename = img_src,
                                img2_filename = img_tar)


    DRAW_MATCHES.drawMatches_from_file(img_src,
                                       img_tar,
                                       output_csv_name,
                                       output_img_name,
                                       verbose=True)

    output_img_name_2 = os.path.join(img_dir, "output_hori_UNFILTERED.png")

    DRAW_MATCHES.drawMatches_from_file(img_src,
                                       img_tar,
                                       keypoints_fname,
                                       output_img_name_2,
                                       verbose=True)

    # Copy the file into a temp one so we can loop through this a bunch of times.
    cfbase, cfext = os.path.splitext(output_img_name)
    copyname = cfbase + "_" + str(i) + cfext
    shutil.copyfile(output_img_name, copyname)
    print os.path.split(copyname)[-1]

    cfbase, cfext = os.path.splitext(output_img_name_2)
    copyname = cfbase + "_" + str(i) + cfext
    shutil.copyfile(output_img_name_2, copyname)
    print os.path.split(copyname)[-1]

    cfbase, cfext = os.path.splitext(output_csv_name)
    copyname = cfbase + "_" + str(i) + cfext
    shutil.copyfile(output_csv_name, copyname)
    print os.path.split(copyname)[-1]
