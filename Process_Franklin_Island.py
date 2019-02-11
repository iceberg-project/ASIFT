# -*- coding: utf-8 -*-
"""
Created on Wed Dec 05 11:12:41 2018

@author: mmacferrin
"""
# Import sub-directory phases
import PHASE_1_IMAGE_PREPROCESSING.Tile_Planner as TILING
import PHASE_1_IMAGE_PREPROCESSING.Scratch_Directory_Manager as SCRATCH
import PHASE_2_KEYPOINT_GENERATION.ASIFT_Executable as ASIFT
import PHASE_3_RANSAC_FILTERING.ASIFT_RANSAC_filter as RANSAC
import PHASE_3_RANSAC_FILTERING.ASIFT_drawMatches as DRAW_MATCHES
from UTILITIES.CSV_auto_reader import read_simple_csv
from UTILITIES.CSV_writer import write_csv

import os
import numpy

scratch = SCRATCH.SCRATCH_Manager()

STEP = 3

def modify_directory_to_local_machine(fname):
    '''Change paths from local paths to the one on this machine.'''
    scratch.scratch_dir

    ASIFT_Image_Match = fname.find("ASIFT_Images")
    ASIFT_Scratch_Match = fname.find("ASIFT_Scratch")

    # THis file is located in the ASIFT_Images directory.
    if ASIFT_Image_Match >= 0:
        new_path = os.path.join(os.path.split(scratch.scratch_dir)[0], fname[ASIFT_Image_Match:])

    elif ASIFT_Scratch_Match >= 0:
        new_path = os.path.join(os.path.split(scratch.scratch_dir)[0], fname[ASIFT_Scratch_Match:])

    else:
        raise ValueError( "Unknown folder match: " + fname)

    # If we're going from a Windows box to a linux box, it helps to replace the directory delimiters.
    # If directory delimiters are forward slashes, turn them all into forward slash (Linux)
    if scratch.scratch_dir[0] == '/':
        return new_path.replace("\\","/")
    # If directory delimiter is backslash, turn them all into back slash (Windows)
    elif scratch.scratch_dir[0:4].find(":\\") > 0:
        return new_path.replace("/", "\\")
    else:
        return new_path



if STEP == 1:
    # Tile the images.
    image_csv = modify_directory_to_local_machine(r'C:\Users\mmacferrin\Dropbox\Research\IceBerg-Personal\ASIFT\ASIFT_Images\Franklin\Franklin_Image_List.csv')
    image_list = read_simple_csv(image_csv)['IMG_FILENAME']

    for img_fname in image_list:
        img_fname = modify_directory_to_local_machine(img_fname)

        print "========== {0} ===========".format(os.path.split(img_fname)[-1])
        scratch_img_dir = scratch.add_directory(img_fname, verbose=True, overwrite=False)
        scratch_subdir_name = os.path.split(scratch_img_dir)[-1]

        # Create the path of the CSV files to create for each image, plus the combined ASIFT_run_cases_CSV file
        tile_csv_name = os.path.join(scratch_img_dir, "tiles_{0}.csv".format(scratch_subdir_name))

        TILING.create_tiles_from_image(img_fname,
                                       csv_file=tile_csv_name,
                                       pyramid_levels=5,
                                       tilesize=1100,
                                       minimum_size=500,
                                       overwrite=False,
                                       verbose=True)

elif STEP in (2,3):
    # run ASIFT on these images
    source_csv = r'C:\Users\mmacferrin\Dropbox\Research\IceBerg-Personal\ASIFT\ASIFT_Images\Franklin\Franklin_Tile_Source_TMA_List.csv'
    source_csv = modify_directory_to_local_machine(source_csv)
    target_csv = r'C:\Users\mmacferrin\Dropbox\Research\IceBerg-Personal\ASIFT\ASIFT_Images\Franklin\Franklin_Tile_Target_WV01_List.csv'
    target_csv = modify_directory_to_local_machine(target_csv)
    sources_list = read_simple_csv(source_csv)['SOURCE']
    sources_list = [modify_directory_to_local_machine(path) for path in sources_list]
    targets_list = read_simple_csv(target_csv)['TARGET']
    targets_list = [modify_directory_to_local_machine(path) for path in targets_list]

    output_info_dtype = numpy.dtype([("source_file", numpy.str, 4096),
                                     ("target_file", numpy.str, 4096),
                                     ("output_dir", numpy.str, 4096)])

    output_info_csv = modify_directory_to_local_machine(r'C:\Users\mmacferrin\Dropbox\Research\IceBerg-Personal\ASIFT\ASIFT_Images\Franklin\ASIFT_runs.csv')

if STEP == 2:

    output_info_list = []

    count = 0
    for source_fname in sources_list:
        for target_fname in targets_list:
            count += 1
            # 1: Create a subdirectory (in the source image dir) for this run case output
            source_dir = os.path.split(source_fname)[0]
            source_dirname = os.path.split(source_dir)[-1]
            target_dirname = os.path.split(os.path.split(target_fname)[0])[-1]
            output_dirname = source_dirname[0:15] + "_" + target_dirname[0:15] + "_" + str(count)
            output_dir = os.path.join(source_dir, output_dirname)
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)

            # 2: Run ASIFT in that subdirectory
            Aexe = ASIFT.ASIFT_Executable(output_dir, im1_gdal=source_fname, im2_gdal=target_fname)
            Aexe.execute(verbose=True)

            # 3: Save it to our output list
            output_info_list.append(numpy.array((source_fname, target_fname, output_dir), dtype=output_info_dtype))

    write_csv(numpy.array(output_info_list, dtype=output_info_dtype), output_info_csv)

elif STEP == 3:
    # run RANSAC on the ASIFT outputs.
    # Need the keypoints filename, all the rest.
    output_info = read_simple_csv(output_info_csv)

    for source_file, target_file, output_dir in output_info:
        keypoints_fname = os.path.join(output_dir, "data_matches.csv")
        if not os.path.exists(keypoints_fname):
            raise IOError("Keypoints file not found: " + keypoints_fname)

        output_csv_name = os.path.join(output_dir, "data_matches_FILTERED.csv")

        RANSAC.filter_ASIFT_matches(keypoints_fname,
                                    output_CSV=output_csv_name,
                                    output_good_points_only=True,
                                    verbose = True,
                                    eliminate_nodata_matches = True,
                                    img1_filename = source_file,
                                    img2_filename = target_file)

        # For testing purposes here, output after filtering...
        output_img_name = os.path.join(output_dir, "output_hori_FILTERED.png")

        DRAW_MATCHES.drawMatches_from_file(source_file,
                                           target_file,
                                           output_csv_name,
                                           output_img_name,
                                           verbose=True)

        # AND before filtering...
        output_img_name_2 = os.path.join(output_dir, "output_hori_UNFILTERED.png")

        DRAW_MATCHES.drawMatches_from_file(source_file,
                                           target_file,
                                           keypoints_fname,
                                           output_img_name_2,
                                           verbose=True)
