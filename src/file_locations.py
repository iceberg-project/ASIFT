# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 12:06:37 2018

File_Locations.py -- specifies where to find input/output files for the rest of the scripts.

@author: mmacferrin
"""
#######################################################################################
## Code for importing the parent directory in order to get the File_Locations object
import os,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#######################################################################################

# The location where the fast_imas_IPOL asift executable sits.
ASIFT_Executable_Path = os.path.join(currentdir, "fast_imas_IPOL/build/main")

# A folder for putting image tiles and CSV files during execution.
# Files can be cleared/emptied once execution has finished.
ASIFT_Scratch_Dir = os.path.join(currentdir, 'asift_scratch')

# The location where the scratch directory log sits.
ASIFT_Scratch_Logfile = os.path.join( ASIFT_Scratch_Dir, "scratch_directory_log.csv" )

# A blank copy of the logfile, to have on hand. Keep this copy at this location
# blank and static. The only code that should use it at all is
# ./phase_1_keypoint_generation/scratch_directory_manager.py::SCRATCH_Manager::setup_scratch_directory()
ASIFT_Scratch_Logfile_blank_copy = "./scratch_directory_log.csv"