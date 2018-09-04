# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 16:49:57 2018

@author: mmacferrin

This file is to run ASIFT test cases using the fast_imas_IPOL executable.

THIS FILL WILL BE ITERATIVE, requiring some changes, until all the test cases we
want are running successfully and we are satisfied the algorithm is working robustly.
"""
################################################################################
# NOTE: BEFORE fast_imas_IPOL can be run, it must be compiled and built on the
# production machine, along with dependent libraries. Directions for doing this are
# in the 'fast_imas_IPOL/README.md file. It should be build with OpenCV ENABLED.
#
# The OpenCV library, v3.2 or higher, will need to be built and installed accordingly.
#
# To use and subset TIF images rather than PNG, the GDAL library and python bindings
#     must also be installed.
#
# Read "fast_imas_IPOL/README.md" for details of build instructions.
################################################################################

# subprocess is used to execute the ASIFT executable and
import subprocess
import os

# The location of the ASIFT executable after compiling.
ASIFT_EXEC = r"./fast_imas_IPOL/build/main"

# The directory where the test case images sit... THIS WILL CHANGE WHEN WE PUT IMAGES ON BRIDGES
TEST_IMAGES_DIR = r"./TEST_CASES/TEST_IMAGES"


# The ASIFT_Test_Case class handles the execution and output of an ASIFT test case.
class ASIFT_Test_Case:

    def __init__(self, im1, im2,
                       output_dir,
                       OPT_im3=None,
                       OPT_max_keys_im3=None,
                       OPT_applyfilter=None,
                       OPT_desc=None,
                       OPT_covering=None,
                       OPT_match_ratio=None,
                       OPT_filter_precision=None,
                       OPT_filter_radius=None,
                       OPT_fixed_area=None,
                       OPT_eigen_threshold=None):
        '''Defining the test case with each set of mandatory and optional parameters.
        All parameters descriptions can be found in './fast_imas_IPOL/README.md

        This method assumes all images to be tested are in the "TEST_IMAGES_DIR" directory.'''
        self.executable = os.path.abspath(ASIFT_EXEC)
        self.im1 = os.path.abspath(os.path.join(TEST_IMAGES_DIR, im1))
        self.im2 = os.path.abspath(os.path.join(TEST_IMAGES_DIR, im2))

        # The "output_dir" will actually be the WORKING DIRECTORY of the ASIFT program when it's run,
        # which means we need to specify absolute paths for the executables and the input images so they can
        # be found independently of the output directory location.
        self.output_dir = os.path.abspath(output_dir)

        if OPT_im3 != None:
            self.im3 = os.path.join(TEST_IMAGES_DIR, OPT_im3)
        else:
            self.im3 = None
        self.max_keys_im3 = OPT_max_keys_im3
        self.applyfilter = OPT_applyfilter
        self.desc = OPT_desc
        self.covering = OPT_covering
        self.match_ratio = OPT_match_ratio
        self.filter_precision = OPT_filter_precision
        self.filter_radius = OPT_filter_radius
        self.fixed_area = OPT_fixed_area
        self.eigen_threshold = OPT_eigen_threshold


    def test_source_files_exist(self, output_warning=False):
        '''A quick test as to whether each source images specified in __init__() actually exists.
        Returns True or False.  Optional parameter "output_warning" will/won't display a warning.'''

        im1_exists = os.path.exists(self.im1)
        im2_exists = os.path.exists(self.im2)

        if self.im3 != None:
            im3_exists = os.path.exists(self.im3)
        else:
            im3_exists = True # This is NOT true if im3 is not given, but this is just to keep the warning from breaking.

        if output_warning:
            if not im1_exists:
                raise Warning("WARNING: file '{0}' does not exist".format(self.im1))
            if not im2_exists:
                raise Warning("WARNING: file '{0}' does not exist".format(self.im2))
            if not im3_exists:
                raise Warning("WARNING: file '{0}' does not exist".format(self.im3))

        return im1_exists and im2_exists and im3_exists

    def execute(self, output_textfile=None):
        '''Execute the text case.
        output_textfile: if None, print the output to stdout.
                         if a string, contains the string to a textfile path where the output should be stored.
                         If this path already exists, it will be overwritten.'''

        # First make sure the input files exist
        assert self.test_source_files_exist(output_warning = True)

        # Build the path
        path_options = [self.executable]
        path_options.extend(["-im1", self.im1])
        path_options.extend(["-im2", self.im2])
        if self.im3 != None:
            path_options.extend(["-im3", self.im3])
        if self.max_keys_im3 != None:
            path_options.extend(["-max_keys_im3", str(self.max_keys_im3)])
        if self.applyfilter != None:
            path_options.extend(["-applyfilter", str(self.applyfilter)])
        if self.desc != None:
            path_options.extend(["-desc", str(self.desc)])
        # TODO: Add other command-line options here....

        # TESTING, remove in a bit
        print "EXECUTABLE OPTIONS:"
        for po in path_options:
            print po


        # Check to make sure our output directory exists. If not, make it.
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        # Execute the file.
        result = subprocess.check_output(path_options, cwd=self.output_dir)
        if output_textfile is None:
            print result

        else:
            output_textfile = os.path.abspath(os.path.join(self.output_dir, output_textfile))
            outfile = open(output_textfile, 'w')
            outfile.write(result)
            outfile.close()

        return


if __name__ == "__main__":

    # Test case 1
    case1 = ASIFT_Test_Case(im1="adam1.png",
                            im2="adam2.png",
                            output_dir='./TEST_CASES/CASE01_adam1_adam2')
    case1.execute(output_textfile="OUTPUT.txt")

    # Test case 2
    case2 = ASIFT_Test_Case(im1="adam2.png",
                            im2="adam1.png",
                            output_dir="./TEST_CASES/CASE02_adam2_adam1")
    case2.execute(output_textfile="OUTPUT.txt")

    APPLYFILTER_OPTIONS = [1,2,3,4]
    # FOr now, leaving out options 10 (LUCID), 13, 30,31,32
    DESC_OPTIONS = [1,2,11,21,22,3,4,5,6,7,8,9]

    # The rest of the test cases, run through ALL the basic command-line options, see if they work.
    test_id = 3
    for applyfilter in APPLYFILTER_OPTIONS:
        for desc in DESC_OPTIONS:
            test_case = ASIFT_Test_Case(im1="adam1.png",
                                        im2="adam2.png",
                                        output_dir="./TEST_CASES/CASE{0:02d}_adam1_adam2_{1:1d}_{2:02d}".format(test_id, applyfilter, desc),
                                        OPT_applyfilter=applyfilter,
                                        OPT_desc=desc)
            test_case.execute(output_textfile="OUTPUT.txt")

            # Iterate to the next test
            test_id += 1