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
# See "fast_imas_IPOL/README.md" for details of build instructions.
################################################################################

import subprocess # subprocess is used to execute the ASIFT executable and read output
import os
import re # Regular expressions used for text parsing

################################################################################
# Global Module variables:
#   These should be set to match whatever machine upon which this is being run,
#   before the code is executed.
################################################################################

# The location of the ASIFT executable after compiling.
ASIFT_EXEC = r"./fast_imas_IPOL/build/main"

# The directory where the test case images sit... THIS WILL CHANGE WHEN WE PUT IMAGES ON BRIDGES
TEST_IMAGES_DIR = r"./TEST_CASES/TEST_CASE_IMAGES"


# The ASIFT_Test_Case class handles the execution and output of an ASIFT test case.
class ASIFT_Test_Case:

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
        if im1 != None:
            self.im1 = os.path.abspath(os.path.join(TEST_IMAGES_DIR, im1))
        else:
            self.im1 = None

        if im2 != None:
            self.im2 = os.path.abspath(os.path.join(TEST_IMAGES_DIR, im2))
        else:
            self.im2 = None

        if im3 != None:
            self.im3 = os.path.abspath(os.path.join(TEST_IMAGES_DIR, im3))
        else:
            self.im3 = None

        if im1_gdal != None:
            self.im1_gdal = os.path.abspath(os.path.join(TEST_IMAGES_DIR, im1_gdal))
        else:
            self.im1_gdal = None

        self.im1_xoff = im1_xoff
        self.im1_yoff = im1_yoff
        self.im1_xsize = im1_xsize
        self.im1_ysize = im1_ysize

        if im2_gdal != None:
            self.im2_gdal = os.path.abspath(os.path.join(TEST_IMAGES_DIR, im2_gdal))
        else:
            self.im2_gdal = None

        self.im2_xoff = im2_xoff
        self.im2_yoff = im2_yoff
        self.im2_xsize = im2_xsize
        self.im2_ysize = im2_ysize

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
        assert self.test_source_files_exist(output_warning = True)

        # Build the path
        path_options = [self.executable]
        if self.im1 != None:
            path_options.extend(["-im1", self.im1])
        if self.im2 != None:
            path_options.extend(["-im2", self.im2])
        if self.im1_gdal != None:
            path_options.extend(["-im1_gdal", self.im1_gdal, self.im1_xoff, self.im1_yoff, self.im1_xsize, self.im1_ysize])
        if self.im2_gdal != None:
            path_options.extend(["-im2_gdal", self.im2_gdal, self.im2_xoff, self.im2_yoff, self.im2_xsize, self.im2_ysize])
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
        # Add other command-line options here if/as needed, see "fast_imas_IPOL/README.md" for details.

        # For performance_monitoring, add "/usr/bin/time" and "-v" to the command line options, at the start.
        # Then capture the output below.
        if performance_monitoring:
            path_options = ["/usr/bin/time","-v"] + path_options

        # Make sure all path options are just text (no integers, etc)
        path_options = [str(item) for item in path_options]

        if verbose:
            # TESTING, remove in a bit
            print "\n****************************************************************************\n"
            print "EXECUTABLE OPTIONS:"
            for po in path_options:
                print po

        # Check to make sure our output directory exists. If not, make it.
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        # Execute the file.  For this implementation, output stderr to the same as stdout
        try:
            result = subprocess.check_output(path_options, cwd=self.output_dir, stderr=subprocess.STDOUT)

            if verbose:
                print "\n============== RESULT =============="
                print result
        except subprocess.CalledProcessError:
            print "EXECUTION ERROR: No results"
            return None

        if output_textfile != None and result != None:
            output_textfile = os.path.abspath(os.path.join(self.output_dir, output_textfile))
            outfile = open(output_textfile, 'w')
            outfile.write(result)
            outfile.close()

        if performance_monitoring and result != None:

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

            return resident_set_size_kb, (system_time_sec + user_time_sec), num_matches

        else: # No performance monitoring
            return



if __name__ == "__main__":

    pass
