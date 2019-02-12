# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 16:49:57 2018

@author: mmacferrin

This file is a wrapper to run ASIFT test cases using the fast_imas_IPOL executable.

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
# See "fast_imas_IPOL/README.md" for details of build instructions.
################################################################################

import subprocess # subprocess is used to execute the ASIFT executable and read output
import os
import re # Regular expressions used for text parsing
import argparse
from osgeo import gdal, gdalconst

################################################################################
# Global Module variables:
#   These should be set to match whatever machine upon which this is being run,
#   before the code is executed.
################################################################################

base_dir = r"/home/mmacferrin/Dropbox/Research/IceBerg-Personal/ASIFT/PHASE_2_KEYPOINT_GENERATION"

# The location of the ASIFT executable after compiling.
ASIFT_EXEC = os.path.join(base_dir, "fast_imas_IPOL/build/main")

# The directory where the test case images sit... THIS WILL CHANGE WHEN WE PUT IMAGES ON BRIDGES
#TEST_IMAGES_DIR = os.path.join(base_dir, r"TEST_CASES/TEST_CASE_IMAGES")

# The ASIFT_Executable class handles the execution and output of an ASIFT test case.
class ASIFT_Executable:

    def __init__(self, output_dir,
                       im1=None,
                       im2=None,
                       # THESE MUST BE PROVIDED TOGETHER
                       im1_gdal=None,
                       im1_xoff=None,
                       im1_yoff=None,
                       im1_xsize=None,
                       im1_ysize=None,
                       # THESE MUST BE PROVIDED TOGETHER
                       im2_gdal=None,
                       im2_xoff=None,
                       im2_yoff=None,
                       im2_xsize=None,
                       im2_ysize=None,

                       # The 'im3' option only applies to the 'XXX' algorithm.
                       im3=None,
                       max_keys_im3=None,

                       applyfilter=None,
                       desc=None,
                       covering=None,
                       match_ratio=None,
                       filter_precision=None,
                       filter_radius=None,
                       fixed_area=None,
                       eigen_threshold=None,
                       tensor_eigen_threshold=None):
        '''Defining the test case with each set of mandatory and optional parameters.
        All parameters descriptions can be found in './fast_imas_IPOL/README.md

        This method assumes all images to be tested are in the "TEST_IMAGES_DIR" directory.'''
        self.executable = os.path.abspath(ASIFT_EXEC)
#        if im1 != None:
#            self.im1 = os.path.abspath(os.path.join(TEST_IMAGES_DIR, im1))
#        else:
#            self.im1 = None

#        if im2 != None:
#            self.im2 = os.path.abspath(os.path.join(TEST_IMAGES_DIR, im2))
#        else:
#            self.im2 = None

#        if im3 != None:
#            self.im3 = os.path.abspath(os.path.join(TEST_IMAGES_DIR, im3))
#        else:
#            self.im3 = None

#        if im1_gdal != None:
#            self.im1_gdal = os.path.abspath(os.path.join(TEST_IMAGES_DIR, im1_gdal))
#        else:
#            self.im1_gdal = None

        self.im1 = im1
        self.im2 = im2
        self.im3 = im3
        self.im1_gdal = im1_gdal
        self.im2_gdal = im2_gdal

        self.im1_xoff = im1_xoff
        self.im1_yoff = im1_yoff
        self.im1_xsize = im1_xsize
        self.im1_ysize = im1_ysize

        self.im2_xoff = im2_xoff
        self.im2_yoff = im2_yoff
        self.im2_xsize = im2_xsize
        self.im2_ysize = im2_ysize

        # If window boundaries are undefined, define them here.
        if self.im1_gdal != None:
            if self.im1_xoff is None:
                self.im1_xoff = 0
            if self.im1_yoff is None:
                self.im1_yoff = 0
            if self.im1_xsize is None or self.im1_ysize is None:
                # If the sizes aren't provided, get them from the image itself.
                if not os.path.exists(self.im1_gdal):
                    raise IOError("File not found: " + self.im1_gdal)
                img_ds = gdal.Open(self.im1_gdal, gdalconst.GA_ReadOnly)
                band = img_ds.GetRasterBand(1)
                XSize = band.XSize
                YSize = band.YSize

                if self.im1_xsize is None:
                    self.im1_xsize = XSize - self.im1_xoff
                if self.im1_ysize is None:
                    self.im1_ysize = YSize - self.im1_yoff

        if self.im2_gdal != None:
            if self.im2_xoff is None:
                self.im2_xoff = 0
            if self.im2_yoff is None:
                self.im2_yoff = 0
            if self.im2_xsize is None or self.im2_ysize is None:
                # If the sizes aren't provided, get them from the image itself.
                if not os.path.exists(self.im2_gdal):
                    raise IOError("File not found: " + self.im2_gdal)
                img_ds = gdal.Open(self.im2_gdal, gdalconst.GA_ReadOnly)
                band = img_ds.GetRasterBand(1)
                XSize = band.XSize
                YSize = band.YSize

                if self.im2_xsize is None:
                    self.im2_xsize = XSize - self.im2_xoff
                if self.im2_ysize is None:
                    self.im2_ysize = YSize - self.im2_yoff

#        if im2_gdal != None:
#            self.im2_gdal = os.path.abspath(os.path.join(TEST_IMAGES_DIR, im2_gdal))
#        else:
#            self.im2_gdal = None

        # The "output_dir" will actually be the WORKING DIRECTORY of the ASIFT program when it's run,
        # which means we need to specify absolute paths for the executables and the input images so they can
        # be found independently of the output directory location.
        self.output_dir = os.path.abspath(output_dir)

        self.max_keys_im3 = max_keys_im3
        self.applyfilter = applyfilter
        self.desc = desc
        self.covering = covering
        self.match_ratio = match_ratio
        self.filter_precision = filter_precision
        self.filter_radius = filter_radius
        self.fixed_area = fixed_area
        self.eigen_threshold = eigen_threshold
        self.tensor_eigen_threshold = tensor_eigen_threshold
        # Just a flag, whether this test case has executed correctly or not.
        self.has_executed_successfully = False

        self.results_array = None

    def test_source_files_exist(self, output_warning=False):
        '''A quick test as to whether each source images specified in __init__() actually exists.
        Returns True or False.  Optional parameter "output_warning" will/won't display a warning.'''

        if self.im1 != None:
            im1_exists = os.path.exists(self.im1)
        else:
            im1_exists = True

        if self.im2 != None:
            im2_exists = os.path.exists(self.im2)
        else:
            im2_exists = True

        # im3 is an optional parameter
        if self.im3 != None:
            im3_exists = os.path.exists(self.im3)
        else:
            im3_exists = True

        if self.im1_gdal != None:
            im1_gdal_exists = os.path.exists(self.im1_gdal)
        else:
            im1_gdal_exists = True

        if self.im2_gdal != None:
            im2_gdal_exists = os.path.exists(self.im2_gdal)
        else:
            im2_gdal_exists = True

        if output_warning:
            if not im1_exists:
                raise Warning("WARNING: file '{0}' does not exist".format(self.im1))
            if not im2_exists:
                raise Warning("WARNING: file '{0}' does not exist".format(self.im2))
            if not im3_exists:
                raise Warning("WARNING: file '{0}' does not exist".format(self.im3))
            if not im1_gdal_exists:
                raise Warning("WARNING: file '{0}' does not exist".format(self.im1_gdal))
            if not im2_gdal_exists:
                raise Warning("WARNING: file '{0}' does not exist".format(self.im2_gdal))

        return im1_exists and im2_exists and im3_exists and im1_gdal_exists and im2_gdal_exists

    def execute(self, output_textfile=None, performance_monitoring=False, verbose=True):
        '''Execute the text case.
        output_textfile: if None, print the output to stdout.
                         if a string, contains the string to a textfile path where the output should be stored.
                         If this path already exists, it will be overwritten.

        performance_monitoring: If True, monitor the performance using the "/usr/bin/time -v" command,
        which will output both time spent and total memory used, and the final number of matches found by ASIFT.

            * Relevant outputs from /usr/bin/time -v:
            *************************************************
            User time (seconds): xxx.xx
            System time (seconds): xxx.xx
            ...
            Maximum resident set size (kbytes): NNNNNN
            *************************************************


        verbose: if True, echo the process stdout & stderr text to the screen.
        '''

        # First make sure the input files exist
        assert self.test_source_files_exist(output_warning = verbose)

        # Build the path
        path_options = [self.executable]
        if self.im1 != None:
            path_options.extend(["-im1", self.im1])
        if self.im2 != None:
            path_options.extend(["-im2", self.im2])
        if self.im1_gdal != None:
            path_options.extend(["-im1_gdal", self.im1_gdal, str(self.im1_xoff), str(self.im1_yoff), str(self.im1_xsize), str(self.im1_ysize)])
        if self.im2_gdal != None:
            path_options.extend(["-im2_gdal", self.im2_gdal, str(self.im2_xoff), str(self.im2_yoff), str(self.im2_xsize), str(self.im2_ysize)])
        if self.im3 != None:
            path_options.extend(["-im3", self.im3])
        if self.max_keys_im3 != None:
            path_options.extend(["-max_keys_im3", str(self.max_keys_im3)])
        if self.applyfilter != None:
            path_options.extend(["-applyfilter", str(self.applyfilter)])
        if self.desc != None:
            path_options.extend(["-desc", str(self.desc)])
        if self.covering != None:
            path_options.extend(["-covering", str(self.covering)])
        if self.match_ratio != None:
            path_options.extend(["-match_ratio", str(self.match_ratio)])
        if self.filter_precision != None:
            path_options.extend(["-filter_precision", str(self.filter_precision)])
        if self.filter_radius != None:
            path_options.extend(["-filter_radius", str(self.filter_radius)])
        if self.eigen_threshold != None:
            path_options.extend(["-eigen_threshold", str(self.eigen_threshold)])
        if self.tensor_eigen_threshold != None:
            path_options.extend(["-tensor_eigen_threshold", str(self.tensor_eigen_threshold)])
        # Add other command-line options here if/as needed, see "fast_imas_IPOL/README.md" for details. It should be completely done now.

        # For performance_monitoring, add "/usr/bin/time" and "-v" to the command line options, at the start.
        # Then capture the output below.
        if performance_monitoring:
            path_options = ["/usr/bin/time","-v"] + path_options

        # Make sure all path options are just text (no integers, etc)
        path_options = [str(item) for item in path_options]

        if verbose:
            # TESTING, remove in a bit
            print "\n****************************************************************************"
            print "EXECUTABLE OPTIONS:"
            for po in path_options:
                print po,
            print

        # Check to make sure our output directory exists. If not, make it.
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        # Execute the file.
        # For this implementation, output stderr to the same as stdout, both of them
        # recorded to the "OUTPUT.txt" file along with the other ASIFT outputs.
        # This allows the stderr output from /usr/bin/time to be captured in "OUTPUT.txt" along with the ASIFT outputs
        try:
            result = subprocess.check_output(path_options, cwd=self.output_dir, stderr=subprocess.STDOUT)

            if verbose:
                print "\n============== RESULT =============="
                print result
        except subprocess.CalledProcessError:
            print "EXECUTION ERROR: No results"
            self.has_executed_successfully = False
            return None

        if (output_textfile != None) and (result != None):
            output_textfile = os.path.abspath(os.path.join(self.output_dir, output_textfile))
            outfile = open(output_textfile, 'w')
            outfile.write(result)
            outfile.close()

        if (performance_monitoring) and (result != None):

            # Get the maximum memory used, as well as the execution time (seconds)
            resident_set_size_match = re.search("(?<=Maximum resident set size \(kbytes\): )\d+", result)
            if resident_set_size_match == None:
                print 'ERROR: "Maximum resident set size (kbytes): " not found in result string.'
                return

            resident_set_size_kb = int(resident_set_size_match.group())

            system_time_match = re.search("(?<=System time \(seconds\): )\d*\.\d*", result)
            if system_time_match == None:
                print 'ERROR: "System time (seconds): " not found in result string.'
                return

            system_time_sec = float(system_time_match.group())

            user_time_match = re.search("(?<=User time \(seconds\): )\d*\.\d*", result)
            if user_time_match == None:
                print 'ERROR: "User time (seconds): " not found in result string.'
                return

            user_time_sec = float(user_time_match.group())

            # Get the number of matches found.
            num_matches_match = re.search("(?<=Final number of matches =) *\d*", result)
            if num_matches_match == None:
                print 'ERROR: "Final number of matches = " not found in result string.'
                return

            num_matches = int(num_matches_match.group().strip())

            self.has_executed_successfully = True
            return resident_set_size_kb, (system_time_sec + user_time_sec), num_matches

        else: # No performance monitoring
            self.has_executed_successfully = True
            return

def define_and_parse_arguments():
    parser = argparse.ArgumentParser(description = "Execute the ASIFT algorithm on two image tiles and generate outputs.")
    parser.add_argument('output_dir', type=str, help="Path to the directory to place outputs of this executable.")
    parser.add_argument('-im1', type=str, required=False, default='', help="Path to the source image (.png)")
    parser.add_argument('-im2', type=str, required=False, default='', help="Path to the target image (.png)")
    parser.add_argument('-im1_gdal', type=str, required=False, default='', help="Path to the source image (.tif)")
    parser.add_argument('-im1_xoff', type=int, required=False, default=-1, help="Tile x-offset in the source image (pixels)")
    parser.add_argument('-im1_yoff', type=int, required=False, default=-1, help="Tile y-offset in the source image (pixels)")
    parser.add_argument('-im1_xsize', type=int, required=False, default=-1, help="Tile x-size in the source image (pixels)")
    parser.add_argument('-im1_ysize', type=int, required=False, default=-1, help="Tile y-size in the source image (pixels)")
    parser.add_argument('-im2_gdal', type=str, required=False, default='', help="Path to the target image (.tif)")
    parser.add_argument('-im2_xoff', type=int, required=False, default=-1, help="Tile x-offset in the target image (pixels)")
    parser.add_argument('-im2_yoff', type=int, required=False, default=-1, help="Tile y-offset in the target image (pixels)")
    parser.add_argument('-im2_xsize', type=int, required=False, default=-1, help="Tile x-size in the target image (pixels)")
    parser.add_argument('-im2_ysize', type=int, required=False, default=-1, help="Tile y-size in the target image (pixels)")
    parser.add_argument('-im3', type=str, required=False, default='', help="The a-contraio input image and activates the a-contrario Matcher (default None, not used for now).")
    parser.add_argument('-max_keys_im3', type=int, required=False, default=-1, help="Sets the maximum number of keypoints to be used for the a-contrario Matcher to VALUE_N (default All, not used for now).")
    parser.add_argument('-applyfilter', type=int, required=False, default=-1, help="Selects the geometric filter to apply (default 2: ORSA Homography) See fast_imas_IPOL/README.md for details.")
    parser.add_argument('-desc', type=int, required=False, default=-1, help="Selects the SIIM method (default 11: Root-SIFT) See fast_imas_IPOL/README.md for details.")
    parser.add_argument('-covering', type=float, required=False, default=-1.0, help="Selects the near optimal covering to be used. Available choices are: 1.4, 1.5, 1.6, 1.7, 1.8, 1.9 and 2. (default 1.7)")
    parser.add_argument('-match_ratio', type=float, required=False, default=-1.0, help="Sets the Nearest Neighbour Distance Ratio. VALUE_M is a real number between 0 and 1. (default 0.6 for SURF and 0.8 for SIFT)")
    parser.add_argument('-filter_precision', type=int, required=False, default=-1, help="Sets the precision threshold for ORSA or USAC. VALUE_P is normally in terms of pixels. (default 3 pixels for Fundamental and 10 pixels for Homography)")
    parser.add_argument('-filter_radius', type=int, required=False, default=-1, help="It tells IMAS to use rho-hyperdescriptors (pixels, default 4)")
#    parser.add_argument(['-eigen_threshold','-tensor_eigen_threshold'], type=int, required=False, default=-1, help="Controls thresholds for eliminating aberrant descriptors.(default 10)")
    parser.add_argument('--fixed_area', required=False, action='store_true', default=False, help="Resizes input images to have areas of about 800*600. *This affects the position of matches and all output images*")
    parser.add_argument('--verbose', required=False, action='store_true', default=False, help="Increase the output verbosity")

    return parser.parse_args()

if __name__ == "__main__":

    args = define_and_parse_arguments()

    ASIFT_exe = ASIFT_Executable(output_dir = args.output_dir,
                                 im1 =       None if args.im1 == ''       else args.im1,
                                 im2 =       None if args.im2 == ''       else args.im2,
                                 im1_gdal =  None if args.im1_gdal == ''  else args.im1_gdal,
                                 im1_xoff =  None if args.im1_xoff == -1  else args.im1_xoff,
                                 im1_yoff =  None if args.im1_yoff == -1  else args.im1_yoff,
                                 im1_xsize = None if args.im1_xsize == -1 else args.im1_xsize,
                                 im1_ysize = None if args.im1_ysize == -1 else args.im1_ysize,
                                 im2_gdal =  None if args.im2_gdal == ''  else args.im2_gdal,
                                 im2_xoff =  None if args.im2_xoff == -1  else args.im2_xoff,
                                 im2_yoff =  None if args.im2_yoff == -1  else args.im2_yoff,
                                 im2_xsize = None if args.im2_xsize == -1 else args.im2_xsize,
                                 im2_ysize = None if args.im2_ysize == -1 else args.im2_ysize,
                                 im3 =       None if args.im3 == ''       else args.im3,
                                 max_keys_im3 =     None if args.max_keys_im3 == -1     else args.max_keys_im3,
                                 applyfilter =      None if args.applyfilter == -1      else args.applyfilter,
                                 desc =             None if args.desc == -1             else args.desc,
                                 covering =         None if args.covering == -1.0       else args.covering,
                                 match_ratio =      None if args.match_ratio == -1.0    else args.match_ratio,
                                 filter_precision = None if args.filter_precision == -1 else args.filter_precision,
                                 filter_radius =    None if args.filter_radius == -1    else args.filter_precision,
#                                 eigen_threshold =  None if args.eigen_threshold == -1  else args.eigen_threshold,
                                 fixed_area =       None if args.fixed_area == False    else args.fixed_area
                                 )

    ASIFT_exe.execute(output_textfile = "OUTPUT.txt",
                      performance_monitoring = False,
                      verbose = args.verbose)

#
#    # Test case 1
#    case1 = ASIFT_Test_Case(im1="adam1.png",
#                            im2="adam2.png",
#                            output_dir='./TEST_CASES/CASE01_adam1_adam2')
#    case1.execute(output_textfile="OUTPUT.txt")
#
#    # Test case 2
#    case2 = ASIFT_Test_Case(im1="adam2.png",
#                            im2="adam1.png",
#                            output_dir="./TEST_CASES/CASE02_adam2_adam1")
#    case2.execute(output_textfile="OUTPUT.txt")


#    APPLYFILTER_OPTIONS = [1,2,3,4]
#    # FOr now, leaving out options 10 (LUCID), 13, 30,31,32
#    DESC_OPTIONS = [1,2,11,21,22,3,4,5,6,7,8,9]
#
#    # The rest of the test cases, run through ALL the basic command-line options, see if they work.
#    test_id = 3
#    for applyfilter in APPLYFILTER_OPTIONS:
#        for desc in DESC_OPTIONS:
#            test_case = ASIFT_Test_Case(im1="adam1.png",
#                                        im2="adam2.png",
#                                        output_dir="./TEST_CASES/CASE{0:02d}_adam1_adam2_{1:1d}_{2:02d}".format(test_id, applyfilter, desc),
#                                        OPT_applyfilter=applyfilter,
#                                        OPT_desc=desc)
#            test_case.execute(output_textfile="OUTPUT.txt")
#
#            # Iterate to the next test
#            test_id += 1