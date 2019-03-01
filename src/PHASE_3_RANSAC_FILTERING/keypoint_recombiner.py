#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 12:58:56 2019

KeyPoint_Recombiner.py -- takes all the outputs from post-RANSAC-filtered tile matches,
converts them back into larger image-coordiate space (rather than tile coordinates), filters
them again using another iteration of the RANSAC algorithm, and generates a geometrically-consistent set of
matching keypoints for the final image.

@author: mmacferrin
"""

# TODO: FINISH THIS