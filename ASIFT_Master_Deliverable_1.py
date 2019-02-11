# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 12:24:43 2018

ASIFT_Master_Deliverable_1.py -- Runs the master algorithm, using each phase code as needed.
for Deliverable 1, take two images, run ASIFT against each of them, and generate matching keypoints as a CSV file.
If the target image is geo-located, output the geo-location (lat/lon) of each keypoint as well.

@author: mmacferrin
"""
import argparse


# Import sub-directory phases
import PHASE_1_IMAGE_PREPROCESSING.ASIFT_Tile_Images as TILING
import PHASE_2_KEYPOINT_GENERATION.ASIFT_Scheduler as ASIFT
import PHASE_3_RANSAC_FILTERING.ASIFT_RANSAC_filter as RANSAC


def process_two_single_images_for_keypoints(source_image, target_image, output_CSV, verbose=True):
    '''Given two images, do all the tiling, contrast-enhancing, and ASIFTing necessary to generate a list of fairly confident keypoints.
    Spit this out and/or return them to the user function.'''

    # TODO 1: Generate the contrast-enhanced tiles and the ASIFT_run_cases.csv to run in the next step.

    # TODO 2: Run the ASIFT_Scheduler to run all the ASIFT_run_cases against each other.

    # TODO 3: Use the ASIFT_RANSAC_filter to filter out all the tiled results,
    # do a "second" filter on the combined results, and give us a "final" set of matching keypoints.

    # TODO 4: Output the set of matching keypoints to the user.
    return




def define_and_parse_arguments():
    parser = argparse.ArgumentParser(description = "Generate a list of matching keypoints between two large images. The source is a non-located image, the target is a (presumably-geolocated, but not necessarily) image against which you're trying to match the source.")
    parser.add_argument('source_image', type=str, help="Path to the source image (tif or png)")
    parser.add_argument('target_image', type=str, help="Path to the target image (tif or png)")
    parser.add_argument('output_csv', type=str, help="Path to a CSV file where you want to store results (will overwrite if the file exists)")
    parser.add_argument('--verbose', required=False, action='store_true', default=False, help="Increase the output verbosity")

    return parser.parse_args()

if __name__ == "__main__":
    args = define_and_parse_arguments()
    process_two_images_for_keypoints(args.source_image,
                                     args.target_image,
                                     args.output_csv,
                                     verbose = args.verbose)