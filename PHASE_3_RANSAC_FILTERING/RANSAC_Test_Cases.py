# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 13:38:28 2018

@author: mmacferrin

RANSAC_Test_cases.py -- just running the algorithm against various test cases.
"""

import sys
import os
import cv2

# First, we need to get the Phase 1 code imported here. Attach the directory where the code exists to the Python system path.
PHASE_2_PATH = os.path.join(os.getcwd(), r"../PHASE_2_KEYPOINT_GENERATION")
sys.path.append(PHASE_2_PATH)

# Now import the ASIFT code to run from there.
from ASIFT_class_definitions import ASIFT_Test_Case, TEST_IMAGES_DIR

from ASIFT_Matches_Reader import ASIFT_Matches
from ASIFT_RANSAC_filter import filter_ASIFT_matches
from ASIFT_drawMatches import drawMatches_from_keypoints

# Worldview Image 1
im1_gdal = os.path.join(TEST_IMAGES_DIR, "WV01_20101207_102001000F043B00_102001001153AD00_seg1_2m_ortho.tif")
im1_center_pixel = [8200,5000]
im1_width = 3000
im1_xoff = im1_center_pixel[0] - (im1_width / 2)
im1_yoff = im1_center_pixel[1] - (im1_width / 2)

# Worldview Image 2
im2_gdal = os.path.join(TEST_IMAGES_DIR, "WV01_20161218_102001005C18BF00_1020010058E7BE00_seg1_2m_ortho.tif")
im2_center_pixel = [15300,28100]
im2_width = 3000
im2_xoff = im2_center_pixel[0] - (im2_width / 2)
im2_yoff = im2_center_pixel[1] - (im2_width / 2)

# TMA Image, cropped, valley/river
im3_gdal = os.path.join(TEST_IMAGES_DIR, "CA179332V0074_EDGE_TRIMMED.tif")
im3_center_pixel = [4500,4000]
im3_width = 3000
im3_xoff = im3_center_pixel[0] - (im3_width / 2)
im3_yoff = im3_center_pixel[1] - (im3_width / 2)

# TMA Image, cropped, glacier outlet 1
im4_gdal = im3_gdal
im4_center_pixel = [7000,7000]
im4_width = 3000
im4_xoff = im4_center_pixel[0] - (im4_width / 2)
im4_yoff = im4_center_pixel[1] - (im4_width / 2)

# TMA Image, cropped, glacier outlet 2
im5_gdal = im3_gdal
im5_center_pixel = [3500,7000]
im5_width = 3000
im5_xoff = im5_center_pixel[0] - (im5_width / 2)
im5_yoff = im5_center_pixel[1] - (im5_width / 2)

# Compile these 5 image subsets into lists.
img_names = [im1_gdal, im2_gdal, im3_gdal, im4_gdal, im5_gdal]
img_centers = [im1_center_pixel, im2_center_pixel, im3_center_pixel, im4_center_pixel, im5_center_pixel]
img_widths = [im1_width, im2_width, im3_width, im4_width, im5_width]
img_xoffs = [im1_xoff, im2_xoff, im3_xoff, im4_xoff, im5_xoff]
img_yoffs = [im1_yoff, im2_yoff, im3_yoff, im4_yoff, im5_yoff]

# The indices of the images above to pair off and try to match.
image_pairs = [(2,0),
               (3,0),
               (4,0),
               (2,1),
               (3,1),
               (4,1)]


for src_img_i, dst_img_i in image_pairs:
    im1_name = img_names[src_img_i]
    im1_xoff = img_xoffs[src_img_i]
    im1_yoff = img_yoffs[src_img_i]
    im1_size = img_widths[src_img_i]

    im2_name = img_names[dst_img_i]
    im2_xoff = img_xoffs[dst_img_i]
    im2_yoff = img_yoffs[dst_img_i]
    im2_size = img_widths[dst_img_i]

    output_dir = os.path.join(TEST_IMAGES_DIR, "test_output_{0}_{1}".format(src_img_i, dst_img_i))

    # Set up the ASIFT executable
    ASIFT = ASIFT_Test_Case(output_dir,
                            im1_gdal=im1_name,
                            im1_xoff=im1_xoff,
                            im1_yoff=im1_yoff,
                            im1_xsize=im1_size,
                            im1_ysize=im1_size,
                            im2_gdal=im2_name,
                            im2_xoff=im2_xoff,
                            im2_yoff=im2_yoff,
                            im2_xsize=im2_size,
                            im2_ysize=im2_size)

    # Run it.
    ASIFT.execute()


    # Check, make sure the mathes file was created.
    matches_file = os.path.join(output_dir, "data_matches.csv")
    assert os.path.exists(matches_file)
    output_img_ALL = os.path.join(output_dir, "PAIR_ALL.png")
    output_img_RANSAC = os.path.join(output_dir, "PAIR_RANSAC.png")

    keys1, keys2, matches = ASIFT_Matches(matches_file).return_cv2_keypoints()

    keys1_RANSAC, keys2_RANSAC = filter_ASIFT_matches(matches_file, output_good_points_only=True, verbose=True)
    assert len(keys1_RANSAC) == len(keys2_RANSAC)

    match_objects_RANSAC = [cv2.DMatch(i,i,i,0) for i in range(len(keys1_RANSAC))]

    drawMatches_from_keypoints(im1_name, im2_name, keys1, keys2, matches, output_img_ALL,
                                           im1_XOff=im1_xoff,
                                           im1_YOff=im1_yoff,
                                           im1_XSize=im1_width,
                                           im1_YSize=im1_width,
                                           im2_XOff=im2_xoff,
                                           im2_YOff=im2_yoff,
                                           im2_XSize=im2_width,
                                           im2_YSize=im2_width)

    drawMatches_from_keypoints(im1_name, im2_name, keys1_RANSAC, keys2_RANSAC, match_objects_RANSAC, output_img_RANSAC,
                                           im1_XOff=im1_xoff,
                                           im1_YOff=im1_yoff,
                                           im1_XSize=im1_width,
                                           im1_YSize=im1_width,
                                           im2_XOff=im2_xoff,
                                           im2_YOff=im2_yoff,
                                           im2_XSize=im2_width,
                                           im2_YSize=im2_width)

