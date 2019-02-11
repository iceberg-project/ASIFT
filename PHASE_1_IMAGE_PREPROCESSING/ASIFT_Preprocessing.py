# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 12:44:42 2018

ASIFT_Preprocessing.py

Arguments: ASIFT_Preprocessing.py /path/to/source/image.tif /path/to/target/image.tif -SOURCE_NODATA value -TARGET_NODATA value

Path to the source image (Required if run standalone.)
Path to the target image (Required if run standalone.)
-SOURCE_NODATA: NODATA value in the source image (Optional, if run standalone.)
-TARGET_NODATA: NODATA value in the target image (Optional, if run standalone.)

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

from Scratch_Directory_Manager import SCRATCH_Manager
#from File_Locations import ASIFT_Scratch_Dir
from Tile_Planner import create_tiles_from_image
from CSV_writer import write_csv

import argparse
import os
import numpy

'''This module will
    1) Determine whether NODATA values exist in either image.
    2) Assign a random-strong 10-digit subdirectory in SCRATCH for all the image tiles for both SRC and DEST images.
        SCRATCH -- [10-digit-code] -- CSV of all image tile pairs to run against each other, including nodata values.
                                   -- SRC_TILES -- [tiles]
                                   -- DST_TILES -- [tiles]
                                   -- [output_dirs will go here]
    3) Run the "Image_Tiling" on each image, getting a CSV of tile definitions. Hold onto the CSV data from each tiling scheme, also go ahead and save those.

    4) Run "Contrast_Enhancer" on each image, putting the tiles themselves in SRC_TILES and DST_TILES.

    5) Return to the calling function:
        a) the 10-digit scratch directory,
        b) The CSV files for tile coordinate mappings from each original image
        c) the CSV file name with all the tile pairs to run ASIFT on (which includes the mappings back to original corner coordinates), from step 3
'''

def tile_both_images(source_filename,
                     target_filename,
                     tilesize=3000,
                     minimum_size=1000,
                     source_nodata=None,
                     target_nodata=None,
                     source_pyramid_levels=0,
                     target_pyramid_levels=0,
                     contrast_enhance=None,
                     verbose=True,
                     overwrite=False):

    # Generate the directories for the source and target images.
    scratch = SCRATCH_Manager()

    scratch_source_dir = scratch.add_directory(source_filename, verbose=verbose, overwrite=overwrite)
    scratch_target_dir = scratch.add_directory(target_filename, verbose=verbose, overwrite=overwrite)
    scratch_source_subdir_name = os.path.split(scratch_source_dir)[-1]
    scratch_target_subdir_name = os.path.split(scratch_target_dir)[-1]

    # Create the path of the CSV files to create for each image, plus the combined ASIFT_run_cases_CSV file
    source_csv_name = os.path.join(scratch_source_dir, "tiles_{0}.csv".format(scratch_source_subdir_name))
    target_csv_name = os.path.join(scratch_target_dir, "tiles_{0}.csv".format(scratch_target_subdir_name))
    # Put the CSV file in the source directory. (could put anywhere, I guess.)
    ASIFT_run_cases_csv_name = os.path.join(scratch_source_dir, "ASIFT_run_cases_{0}_{1}.csv".format(scratch_source_subdir_name, scratch_target_subdir_name))

    source_and_target_files = [[source_filename, source_csv_name, source_pyramid_levels],
                               [target_filename, target_csv_name, target_pyramid_levels]]

    for i,(img_name, csv_name, pyramid_levels) in enumerate(source_and_target_files):
        # Run the Image_Tiling.py on each image separately, collect the data into each CSV_data object.
        img_csv_data = create_tiles_from_image(img_name,
                                               csv_file = csv_name,
                                               tilesize = tilesize,
                                               nodata = source_nodata if i==0 else target_nodata,
                                               pyramid_levels = pyramid_levels,
                                               minimum_size = minimum_size,
                                               write_tiles_to_disk = True,
                                               overwrite = overwrite,
                                               verbose = verbose)

        # Assign the output data to either the source or target image
        if i == 0:
            source_tile_CSV_data = img_csv_data
        else:
            target_tile_CSV_data = img_csv_data


    # Compile the list of ASIFT run cases
    # TODO: Change this to use Run_Case_Scheduler.py ---
    ASIFT_run_cases_CSV_data = create_asift_run_cases_csv_data(source_tile_CSV_data, target_tile_CSV_data)

    # Save ASIFT_run_cases_CSV_data to ASIFT_run_cases_csv_name.
    write_csv(ASIFT_run_cases_CSV_data, ASIFT_run_cases_csv_name)

    # Print message if verbose:
    if verbose:
        print os.path.split(ASIFT_run_cases_csv_name)[-1], "written."

    return source_csv_name, target_csv_name, ASIFT_run_cases_csv_name


#def create_asift_run_cases_csv_data(source_tile_CSV_data, target_tile_CSV_data):
#    '''Running through the list of tiles for the source and target images, create an MxN-length list of
#    run cases to be run by the "PHASE_2_KEYPOINT_GENERATION" code.  Return the CSV data to the calling function.'''
#    # TODO 1: Create a numpy data type to store this data.
#    return None
#    numpy.dtype
#
#    ASIFT_run_cases_CSV_data = None
#
#    # Double-for loop to get all the data compiled together
#    for i,source_record in enumerate(source_tile_CSV_data):
#        for j,target_record in enumerate(target_tile_CSV_data):
#            # TODO 3: Fill in data here.
#            ASIFT_run_cases_CSV_data[i*len(target_tile_CSV_data) + j] = None
#
#    # Return data to calling function.
#    return ASIFT_run_cases_CSV_data

def output_asift_csv_file(ASIFT_run_cases_CSV_data, ASIFT_run_cases_csv_name):
    '''Take the data generated by "created_asift_run_cases_csv_data()" and spit it out to the CSV file specified.'''
    # TODO 1: Spit out the data to the file.


def define_and_parse_arguments():
    parser = argparse.ArgumentParser(description = "Contrast-enhance a tile within an image, output to a new image.")
    parser.add_argument('source', type=str, required=True, help="Path to the source image (tif or png)")
    parser.add_argument('target', type=str, required=True, help="Path to the target image (tif or png)")
    parser.add_argument('-tilesize',  type=int, default=3000, help="Size of the tiles, in pixels (default: 3000)")
    parser.add_argument('-size_tolerance', type=int, default=1000, required=False, help="Tile size tolerance to avoid slivers, in pixels (default: 1000)")
    parser.add_argument('-source_pyramid_levels', type=int, default=0, required=False, help="Number of factor-of-two pyramid levels to create tiles (default 0, original size only)")
    parser.add_argument('-target_pyramid_levels', type=int, default=0, required=False, help="Number of factor-of-two pyramid levels to create tiles (default 0, original size only)")
    parser.add_argument('-source_nodata_value', type=int, default=-999, required=False, help="No-data value in the source image. If not provided, will look in image metadata. (default: -999... translates to None)")
    parser.add_argument('-target_nodata_value', type=int, default=-999, required=False, help="No-data value in the target image. If not provided, will look in image metadata. (default: -999... translates to None)")
    parser.add_argument('--verbose', required=False, action='store_true', default=False, help="Increase the output verbosity")
    parser.add_argument('--overwrite', required=False, action='store_true', default=False, help="If present, overwrite the tiles created if image was already processed previously. (default: Keep tiles there if already used.)")

    return parser.parse_args()

if __name__ == "__main__":
    args = define_and_parse_arguments()
    # Given two images, create CSV files that desribe the tiles in each image,
    # as well as the matchings between both sets of image tiles to run ASIFT upon.
    tile_both_images(args.source,
                     args.target,
                     tilesize = args.tilesize,
                     size_tolerance = args.size_tolerance,
                     source_nodata = None if (args.source_nodata_value == -999) else args.source_nodata_value,
                     target_nodata = None if (args.target_nodata_value == -999) else args.target_nodata_value,
                     source_pyramid_levels = args.source_pyramid_levels,
                     target_pyramid_levels = args.target_pyramid_levels,
                     verbose = args.verbose,
                     overwrite = args.overwrite)