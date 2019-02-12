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

# TODO: Change this if the folder containing images resides elsewhere.
# This might be on a remote drive, in which case more code may be needed here (with credentials) to access it.
ASIFT_Image_Dir = os.path.join(currentdir, 'ASIFT_Images')

# A folder for putting image tiles and CSV files during execution.
# Files can be cleared/emptied once execution has finished.
ASIFT_Scratch_Dir = os.path.join(currentdir, 'ASIFT_Scratch')

ASIFT_Scratch_Logfile = os.path.join( ASIFT_Scratch_Dir, "Scratch_Directory_Log.csv" )