# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 15:54:17 2018

ASIFT_Scheduler.py -- Responsible for running all the image tiles against each other,
    compiling the results together, and creating a CSV file with final pixel and geo-locations.

@author: mmacferrin
"""

import argparse
import os
from ASIFT_Executable import ASIFT_Executable

# TODO: Write in a scheduler here: on a desktop workstation all the cases might be run in serial with a "for" loop.
# In an HPC environment, these cases would be farmed out to individual nodes, and their results gathered after execution is finished.

def schedule_and_run_all_ASIFT_tiles(ASIFT_run_cases_CSV_file, verbose=True):
    '''Takes the images output in the CSV file, runs them against each other, and compile all the outputs together.'''



# TODO: finish this code. -- read a "run cases" CSV file and send all the run cases to the scheduler.
#def read_ASIFT_run_cases_CSV_file(csv_file):
#    lines =


def define_and_parse_arguments():
    parser = argparse.ArgumentParser(description = "Execute the ASIFT algorithm on two image tiles and generate outputs.")
    # TODO: Add arguments here.
    parser.add_argument('ASIFT_csv_file', type=str, help="The ASIFT_run_cases_csv file spit out by PHASE_1_IMAGE_PREPROCESSING/ASIFT_Tile_Images.py::tile_both_images()")
    parser.add_argument('-nodes', type=int, required=False, default=1, help="Number of nodes to farm out jobs. (default: 1, running serially) [CURRENTLY UNUSED]")

    return parser.parse_args()


if __name__ == "__main__":

    args = define_and_parse_arguments()
    schedule_and_run_all_ASIFT_tiles(args.ASIFT_csv,
                                     verbose=args.verbose)