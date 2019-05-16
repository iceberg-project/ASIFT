#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 14:43:40 2019

Contrast_Enhancer.py -- different algorithms for enhancing contrast in a set of pixels

@author: mmacferrin
"""

import skimage.exposure as exposure
import numpy


def enhance_contrast(data, algorithm="equalize", output_min=None, output_max=None):
    '''Take an array of pixels and perform a contrast enhancement. Output the
    same number of pixels that have been contrast enhanced,
    in the same datatype as the input pixels. Nodata values are assumed to already
    have been masked out.
    
    Arrays are assumed to be integer values.
    
    If output_min or output_max are assigned, use those to assign the range of outputs.
    Otherwise, use the min() and max() of the integer datatype will be used.
    
    (For example, if 0 is a Nodata value, then output_min=1 should be used to not conflict
    with nodata values.)'''

    
    # Lower-case the algorithm name
    if algorithm != None:
        algorithm = algorithm.strip().lower()

    # Get the broadest range of integer values here.
    if output_min is None:
        output_min = numpy.iinfo(data.dtype).min
    if output_max is None:
        output_max = numpy.iinfo(data.dtype).max
    
    if algorithm == "equalize":
        return _enhance_contrast_EQUALIZE(data, output_min, output_max)
    
    # TODO: Fill in other algorithms here.
    
    else:
        return data

    
def _enhance_contrast_EQUALIZE(data_values, int_min, int_max):
    equalized_float_pixels = exposure.equalize_hist(data_values)

    # Fill in all the normalized pixels that aren't nodata values.
    return numpy.array(equalized_float_pixels*(int_max-int_min)+int_min, dtype=data_values.dtype)
