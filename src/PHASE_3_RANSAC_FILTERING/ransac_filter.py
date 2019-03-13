# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 14:46:18 2018

@author: mmacferrin

Code using OpenCV, from "Learn OpenCV" tutorial: https://www.learnopencv.com/image-alignment-feature-based-using-opencv-c-python/
"""

#######################################################################################
## Code for importing the Utilities directory
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
utilities_dir = os.path.join(parentdir, "utilities")
sys.path.insert(0,utilities_dir)
#######################################################################################=


from matches_reader import ASIFT_Matches
from csv_writer import write_csv

# External open CV v3 or higher
import argparse
import cv2
import numpy


def find_nodata_matches(keypoints_array, img_filename, img_nodata=None):
    '''Take the keypoints given for this image, find the nodata value, and search the image to find all points that are adjacent to nodata values.
    Return a boolean mask, same length as keypoints_array, with True for each value that is adjacent to a nodata value.'''
    img_ds = gdal.Open(img_filename, gdalconst.GA_ReadOnly)
    band = img_ds.GetRasterBand(1)
    xsize = band.XSize
    ysize = band.YSize

    NDV = band.GetNoDataValue() if (img_nodata is None) else img_nodata

    # If this image doesn't have a nodata value, just return an empty array.
    mask = numpy.zeros((keypoints_array.shape[0],), dtype=numpy.bool)
    if NDV is None:
        return mask

    # Read the data
    img_data = band.ReadAsArray()
    for i in range(keypoints_array.shape[0]):
        keyx, keyy = keypoints_array[i,:]

        # Encompass the 2x2 bounding box of pixels around each floating-point index match.
        index_xmin, index_ymin = numpy.floor([keyx, keyy])
        index_xmin = int(index_xmin)
        index_ymin = int(index_ymin)
        index_xmax, index_ymax = numpy.ceil([keyx, keyy])
        index_xmax = int(index_xmax)
        index_ymax = int(index_ymax)

        # Make sure we don't go out-of-bounds of the image.
        if index_xmax == xsize:
            index_xmax -= 1
        if index_ymax == ysize:
            index_ymax -= 1

        # If any of the values in the 2x2 slice are NDV, mark this as a bad point.
        mask[i] = numpy.any(img_data[index_ymin:(index_ymax+1), index_xmin:(index_xmax+1)] == NDV)

    return mask

def filter_ASIFT_matches(matching_keypoints_filename,
                         output_CSV=None,
                         output_good_points_only=True,
                         verbose=True,
                         ransac_threshold=3,
                         eliminate_nodata_matches=True,
                         img1_filename=None,
                         img1_nodata=None,
                         img2_filename=None,
                         img2_nodata=None):
    '''ASIFT_RANSAC_filter::filter_ASIFT_matches(matching_keypoints_filename,
                                                 output_good_points_only = True,
                                                 verbose = False,
                                                 ransac_reprojection_threshold=3)
        Parameters:
            * matching_keypoints_filename (req'd): the file path of the "data_matches.csv" file produced by the ASIFT executable.
            * output_good_points_only (opt'l): boolean, default True
                                               if True: return a 2 lists of matching cv2::KeyPoint matches, bad points omitted.
                                               if False: return the Homography transformatio matrix, keypoints1 (all), keypoints2 (all), and a boolean mask of the selected keypoints in each array.
            * verbose (opt'l): boolean, default False
                               if True: print a status statement when the function completes.
                               if False: stay silent, just return the damned matches.
            * ransac_reprojection_threshold (opt'l): number 1-10, default 3. The allowed cutoff threshold for accepting/rejecting transformed matching keypoints as "good" matches.
    '''

    # 1. Open the "data_matches.csv" file, digest the points into matches and keypoints manually.
    keys1, keys2, matches = ASIFT_Matches(matching_keypoints_filename).return_cv2_keypoints()

    keys1_ndarray = numpy.asarray([keys1[i].pt for i in range(len(keys1))])
    keys2_ndarray = numpy.asarray([keys2[i].pt for i in range(len(keys2))])

    # 1.5 -- eliminate values that are on or adjacent to nodata values.
    if eliminate_nodata_matches:
        if img1_filename != None:
            img1_nodata_mask = find_nodata_matches(keys1_ndarray, img1_filename, img1_nodata)
        else:
            img1_nodata_mask = numpy.zeros((keys1_ndarray.shape[0],),dtype=numpy.bool)

        if img2_filename != None:
            img2_nodata_mask = find_nodata_matches(keys2_ndarray, img2_filename, img2_nodata)
        else:
            img2_nodata_mask = numpy.zeros((keys2_ndarray.shape[0],),dtype=numpy.bool)

        bad_matches_mask = img1_nodata_mask | img2_nodata_mask
        assert len(bad_matches_mask) == len(keys1) == len(keys2)

    else:
        bad_matches_mask = numpy.zeros((keys1_ndarray.shape[0],),dtype=numpy.bool)


    # 2. Use the cv2.findHomography call, and tweak the parameters to get a good filter.
    # See reference info: https://docs.opencv.org/3.0-beta/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html?highlight=findhomography#findhomography
   
   
    #This is a function from opencv doc @aymenalsaadi M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    H, mask = cv2.findHomography(keys1_ndarray, keys2_ndarray, cv2.RANSAC, ransac_threshold, 2000)
    if len(mask.shape) > 1:
        mask.shape = (mask.shape[0],)

    mask = mask & ~bad_matches_mask

    if verbose:
        print numpy.count_nonzero(mask), "of", len(mask), "matches selected."

    mask_list = list(mask)

    good_kp1 = [kp1 for kp1, flag in zip(keys1, mask_list) if flag]
    good_kp2 = [kp2 for kp2, flag in zip(keys2, mask_list) if flag]

    # Output to CSV file if requested.
    if output_CSV != None:
        x1 = numpy.array([key.pt[0] for key in good_kp1], dtype=numpy.float)
        y1 = numpy.array([key.pt[1] for key in good_kp1], dtype=numpy.float)
        sigma1 = numpy.array([key.size for key in good_kp1], dtype=numpy.float)

        x2 = numpy.array([key.pt[0] for key in good_kp2], dtype=numpy.float)
        y2 = numpy.array([key.pt[1] for key in good_kp2], dtype=numpy.float)
        sigma2 = numpy.array([key.size for key in good_kp2], dtype=numpy.float)

        write_csv([x1, y1, sigma1, x2, y2, sigma2],
                  output_CSV,
                  header=["x1", "y1", "sigma1", "x2", "y2", "sigma2"],
                  verbose=verbose,
                  print_help=False)

    # 3. Return good matches
    if output_good_points_only:
        return good_kp1, good_kp2
    else:
        return H, keys1, keys2, mask



def define_and_parse_arguments():
    parser = argparse.ArgumentParser(description = "Filter keypoint matches using the RANSAC filter. Output a subset of keypoints that pass RANSAC filtering.")
    parser.add_argument('matches_filename', type=str, help="Name of the CSV file from the ASIFT executable with matching keypoints (typically 'data_matches.csv').")
    parser.add_argument('output_filename', type=str, help="Name of the output CSV file to store the RANSAC-filtered matches.")
    parser.add_argument('-ransac_threshold', type=int, default=3, required=False, help="Pixel threshold for RANSAC filter (Default 3).")
    parser.add_argument('-img1_filename', type=str, required=False, default="", help="The name of the source image, for filtering out nodata values.")
    parser.add_argument('-img1_nodata', type=int, required=False, default=-999, help="The nodata value to use in the source image (default: find in image metadata)")
    parser.add_argument('-img2_filename', type=str, required=False, default="", help="The name of the target image, for filtering out nodata values.")
    parser.add_argument('-img2_nodata', type=int, required=False, default=-999, help="The nodata value to use in the target image (default: find in image metadata)")
    parser.add_argument('--verbose', required=False, action='store_true', default=False, help="Increase output verbosity")
    parser.add_argument('--filter_nodata_matches', required=False, action='store_true', default=False, help="Filter out points adjacent to nodata values.")

    return parser.parse_args()

if __name__ == "__main__":
    args = define_and_parse_arguments()

    keys1, keys2 = filter_ASIFT_matches(args.matches_filename,
                                        output_CSV = args.output_filename,
                                        output_good_points_only = True,
                                        ransac_threshold = args.ransac_threshold,
                                        verbose=args.verbose,
                                        eliminate_nodata_matches = args.filter_nodata_matches,
                                        img1_filename = None if (args.img1_filename == "") else args.img1_filename,
                                        img1_nodata = None if (args.img1_nodata == -999) else args.img1_nodata,
                                        img2_filename = None if (args.img2_filename == "") else args.img2_filename,
                                        img2_nodata = None if (args.img2_nodata == -999) else args.img2_nodata)


    if args.verbose:
        print repr(keys1)
        print repr(keys2)
