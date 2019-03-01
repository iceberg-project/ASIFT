# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 16:29:47 2018

@author: mmacferrin

ASIFT_Output_generator.py -- describes the ASIFT_Output() function to display matching keypoints in two images.
Designed to be used with outputs from "fast_imas_IPOL" files and input GeoTIFF images.
"""

# Depends upon opencv library
import cv2
import gdal
import numpy
#import os
from matches_reader import ASIFT_Matches

## Some local variables to test this function, not needed otherwise.
#working_dir = r"C:\Users\mmacferrin\Dropbox\Research\IceBerg-Personal\ASIFT\PHASE_1_KEYPOINT_GENERATION\TEST_CASES\TEST_CASE_IMAGES"
#
#im1_gdal = os.path.join(working_dir, "WV01_20101207_102001000F043B00_102001001153AD00_seg1_2m_ortho.tif")
#im1_center_pixel = [7100,6100]
#im1_width = 2000
#im1_xoff = im1_center_pixel[0] - (im1_width / 2)
#im1_yoff = im1_center_pixel[1] - (im1_width / 2)
#
#im2_gdal = os.path.join(working_dir, "WV01_20161218_102001005C18BF00_1020010058E7BE00_seg1_2m_ortho.tif")
#im2_center_pixel = [14100,29200]
#im2_width = 2000
#im2_xoff = im2_center_pixel[0] - (im2_width / 2)
#im2_yoff = im2_center_pixel[1] - (im2_width / 2)
#
#matches_file = r'C:\Users\mmacferrin\Dropbox\Research\IceBerg-Personal\ASIFT\PHASE_1_KEYPOINT_GENERATION\TEST_CASES\perftest_2000_2000\data_matches.csv'

def drawMatches_from_file(im1_name, im2_name, matches_file, output_img_name, gap_pixels = 20,
                                                                           gap_color = 255,
                                                                           im1_XOff=None,
                                                                           im1_YOff=None,
                                                                           im1_XSize=None,
                                                                           im1_YSize=None,
                                                                           im2_XOff=None,
                                                                           im2_YOff=None,
                                                                           im2_XSize=None,
                                                                           im2_YSize=None,
                                                                           verbose=True):

    gtif1 = gdal.Open(im1_name, gdal.GA_ReadOnly)
    gtif1_band = gtif1.GetRasterBand(1)
    if (im1_XOff != None and im1_XSize != None and im1_YOff != None and im1_YSize != None):
        im1 = gtif1_band.ReadAsArray(xoff=im1_XOff, yoff=im1_YOff, win_xsize=im1_XSize, win_ysize=im1_YSize)
    else:
        im1 = gtif1_band.ReadAsArray()
#    print im1.shape

    gtif2 = gdal.Open(im2_name, gdal.GA_ReadOnly)
    gtif2_band = gtif2.GetRasterBand(1)
    if (im2_XOff != None and im2_XSize != None and im2_YOff != None and im2_YSize != None):
        im2 = gtif2_band.ReadAsArray(xoff=im2_XOff, yoff=im2_YOff, win_xsize=im2_XSize, win_ysize=im2_YSize)
    else:
        im2 = gtif2_band.ReadAsArray()

#    print im2.shape

    if gap_pixels is None or gap_pixels <= 0:
        gap_pixels = 0
    else:
        im2_with_gap = numpy.zeros((im2.shape[0], im2.shape[1]+gap_pixels), dtype=im2.dtype)
        if gap_color != None:
            im2_with_gap[:,:gap_pixels] = gap_color
            # If gap_color is not provided, it will default to black.

        im2_with_gap[:,gap_pixels:] = im2
        im2 = im2_with_gap
#        print im2.shape

    outimg = numpy.zeros(shape=(numpy.max([im1.shape[0], im2.shape[0]]), im1.shape[1] + im2.shape[1], 3),dtype=numpy.uint8) + gap_color

#    print outimg.shape
    for i in range(3):
        if im1.dtype == numpy.uint8:
            im1_divisor = 1
        elif im1.dtype in (numpy.int16, numpy.uint16):
            im1_divisor = 2**7
        else:
            raise ValueError("Unhandled dtype for numpy array in ASIFT_drawMatches::drawMatches_from_file(): {0}".format(str(im1.dtype)))

        outimg[:im1.shape[0],:im1.shape[1],i] = im1 / im1_divisor

        if im2.dtype == numpy.uint8:
            im2_divisor = 1
        elif im2.dtype in (numpy.int16, numpy.uint16):
            im2_divisor = 2**7
        else:
            raise ValueError("Unhandled dtype for numpy array in ASIFT_drawMatches::drawMatches_from_file(): {0}".format(str(im2.dtype)))

        outimg[:im2.shape[0],im1.shape[1]:,i] = im2 / im2_divisor

    keys1, keys2, matches = ASIFT_Matches(matches_file).return_cv2_keypoints()
    # Add gap_pixels to the x-dimension of the match on each keypoint in keys2
    for kp in keys2:
        kp.pt = (kp.pt[0] + gap_pixels, kp.pt[1])

    cv2.drawMatches(img1 = im1,
                    keypoints1 = keys1,
                    img2 = im2,
                    keypoints2 = keys2,
                    matches1to2 = matches,
                    outImg = outimg,
                    flags = cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS + cv2.DRAW_MATCHES_FLAGS_DRAW_OVER_OUTIMG)
#                    flags = cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS | cv2.DRAW_MATCHES_FLAGS_DRAW_OVER_OUTIMG)

    # Right now, lines_img is 0-255 (8-bit), even though it's being saved as a 16-bit array. This doesn't scale well with the outimg, which is actual 16-bit.
#    lines_img = lines_img * int(2**7)

#    print outimg.shape, outimg.dtype, numpy.min(outimg.flatten()), numpy.max(outimg.flatten())
#    print lines_img.shape, lines_img.dtype, numpy.min(lines_img.flatten()), numpy.max(lines_img.flatten())

#    combined_img = cv2.addWeighted(outimg, 0.01, lines_img, 1.0, 0)

    if verbose:
        print "Writing", output_img_name
#    cv2.imwrite(output_img_name, combined_img)
    cv2.imwrite(output_img_name, outimg, params=[int(cv2.IMWRITE_PNG_COMPRESSION), 8])


def drawMatches_from_keypoints(im1_name, im2_name, keys1, keys2, matches, output_img_name, gap_pixels = 15,
                                                                           gap_color = None,
                                                                           im1_XOff=None,
                                                                           im1_YOff=None,
                                                                           im1_XSize=None,
                                                                           im1_YSize=None,
                                                                           im2_XOff=None,
                                                                           im2_YOff=None,
                                                                           im2_XSize=None,
                                                                           im2_YSize=None,
                                                                           verbose=True):

    gtif1 = gdal.Open(im1_name, gdal.GA_ReadOnly)
    gtif1_band = gtif1.GetRasterBand(1)
    if (im1_XOff != None and im1_XSize != None and im1_YOff != None and im1_YSize != None):
        im1 = gtif1_band.ReadAsArray(xoff=im1_XOff, yoff=im1_YOff, win_xsize=im1_XSize, win_ysize=im1_YSize)
    else:
        im1 = gtif1_band.ReadAsArray()
#    print im1.shape

    gtif2 = gdal.Open(im2_name, gdal.GA_ReadOnly)
    gtif2_band = gtif2.GetRasterBand(1)
    if (im2_XOff != None and im2_XSize != None and im2_YOff != None and im2_YSize != None):
        im2 = gtif2_band.ReadAsArray(xoff=im2_XOff, yoff=im2_YOff, win_xsize=im2_XSize, win_ysize=im2_YSize)
    else:
        im2 = gtif2_band.ReadAsArray()
#    print im2.shape

    if gap_pixels is None or gap_pixels <= 0:
        gap_pixels = 0
    else:
        im2_with_gap = numpy.zeros((im2.shape[0], im2.shape[1]+gap_pixels), dtype=im2.dtype)
        if gap_color != None:
            im2_with_gap[:,:gap_pixels] = gap_color

        im2_with_gap[:,gap_pixels:] = im2
        im2 = im2_with_gap
#        print im2.shape

    outimg = numpy.zeros(shape=(numpy.max([im1.shape[0], im2.shape[0]]), im1.shape[1] + im2.shape[1], 3),dtype=numpy.uint8)
#    print outimg.shape
    for i in range(3):

        if im1.dtype == numpy.uint8:
            im1_divisor = 1
        elif im1.dtype in (numpy.int16, numpy.uint16):
            im1_divisor = 2**7
        else:
            raise ValueError("Unhandled dtype for numpy array in ASIFT_drawMatches::drawMatches_from_keypoints(): {0}".format(str(im1.dtype)))

        outimg[:im1.shape[0],:im1.shape[1],i] = im1 / im1_divisor

        if im2.dtype == numpy.uint8:
            im2_divisor = 1
        elif im2.dtype in (numpy.int16, numpy.uint16):
            im2_divisor = 2**7
        else:
            raise ValueError("Unhandled dtype for numpy array in ASIFT_drawMatches::drawMatches_from_keypoints(): {0}".format(str(im2.dtype)))

        outimg[:im2.shape[0],im1.shape[1]:,i] = im2 / im2_divisor

#    keys1, keys2, matches = ASIFT_Matches(matches_file).return_cv2_keypoints()
    # Add gap_pixels to the x-dimension of the match on each keypoint in keys2
    for kp in keys2:
        kp.pt = (kp.pt[0] + gap_pixels, kp.pt[1])

    cv2.drawMatches(img1 = im1,
                    keypoints1 = keys1,
                    img2 = im2,
                    keypoints2 = keys2,
                    matches1to2 = matches,
                    outImg = outimg,
                    flags = cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS + cv2.DRAW_MATCHES_FLAGS_DRAW_OVER_OUTIMG)
#                    flags = cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS | cv2.DRAW_MATCHES_FLAGS_DRAW_OVER_OUTIMG)

    # Right now, lines_img is 0-255 (8-bit), even though it's being saved as a 16-bit array. This doesn't scale well with the outimg, which is actual 16-bit.
#    lines_img = lines_img * int(2**7)

#    print outimg.shape, outimg.dtype, numpy.min(outimg.flatten()), numpy.max(outimg.flatten())
#    print lines_img.shape, lines_img.dtype, numpy.min(lines_img.flatten()), numpy.max(lines_img.flatten())

#    combined_img = cv2.addWeighted(outimg, 0.01, lines_img, 1.0, 0)
    if verbose:
        print "Writing", output_img_name
#    cv2.imwrite(output_img_name, combined_img)
    cv2.imwrite(output_img_name, outimg, params=[int(cv2.IMWRITE_PNG_COMPRESSION), 8])


if __name__ == "__main__":
    pass
#    drawMatches(im1_gdal, im2_gdal, matches_file, "TEST_draw_matches.png", gap_pixels = 20, gap_color = int((2**15)-1),
#                                                                           im1_XOff=im1_xoff,
#                                                                           im1_YOff=im1_yoff,
#                                                                           im1_XSize=im1_width,
#                                                                           im1_YSize=im1_width,
#                                                                           im2_XOff=im2_xoff,
#                                                                           im2_YOff=im2_yoff,
#                                                                           im2_XSize=im2_width,
#                                                                           im2_YSize=im2_width)