# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 16:43:47 2018

@author: mmacferrin

ASIFT_Matches_reader.py -- A simple utility for opening and reading ASIFT data_matches.csv files
"""

import numpy
import cv2

def read_matches_file(filename, include_keypoints=False):
    '''Reads an ASIFT Executable match file.
    Inputs:
        - filename: name of the "matches.csv" file
        - include_keypoints: (bool), If False, just return a numpy array of matches from the file.
                                     If True, return two lists of cv2.KeyPoint objects along with the numpy array of matches from the file.
    Return Values:
        (If include_keypoints = False):
        - numpy array of data from the .csv file.
        (If include_keypoints = True):
        - list of cv2.KeyPoint objects from source image
        - list of cv2.KeyPonit objects from target image
        - numpy array of data from the .csv file.
    '''
    m = ASIFT_Matches(filename)

    if include_keypoints:
        return m.read()
    else:
        return m.return_cv2_keypoints()



class ASIFT_Matches:

    # A custom numpy datatype for asift matches from "fast_imas_IPOL"
    match_dtype = numpy.dtype([('x1',    numpy.float),
                               ('y1',    numpy.float),
                               ('sigma1',numpy.float),
                               ('angle1',numpy.float),
                               ('t1_x',  numpy.float),
                               ('t1_y',  numpy.float),
                               ('theta1',numpy.float),
                               ('x2',    numpy.float),
                               ('y2',    numpy.float),
                               ('sigma2',numpy.float),
                               ('angle2',numpy.float),
                               ('t2_x',  numpy.float),
                               ('t2_y',  numpy.float),
                               ('theta2',numpy.float)
                               ])

    def __init__(self, filename=None):

        self.filename = filename
        self.matches = None

    def read(self, filename=None):
        '''Reads the input file, saves the data, returns an array of matching points'''
        if filename is None:
            filename = self.filename
        if self.filename is None:
            self.filename = filename

        f = open(filename, 'r')
        lines = [line.strip() for line in f.readlines() if len(line.strip()) > 0]
        f.close()

        # Read the header line, and all the data lines.
        header = dict([(item.strip(),i) for i,item in enumerate(lines[0].split(','))])
#        print header
        lines = lines[1:]

        # Create an empty array of matches.
        self.matches = numpy.zeros((len(lines),), dtype=ASIFT_Matches.match_dtype)

        # Fill the array, line by line from the CSV file. All values are floating-point in this case, making the conversions easy.
        for i,line in enumerate(lines):
            items = [float(item) for item in line.split(',')]
            for key in header.keys():
                self.matches[i][key] = items[header[key]]

        # Return the array
        return self.matches

    def return_cv2_keypoints(self, filename=None):
        '''From the matching keypoints, return a list of cv2 keypoints from each image that correspond with each other as 1:1 matches.'''
        if self.matches is None:
            self.read()

        keys1 = [cv2.KeyPoint(x=self.matches[i]['x1'], y=self.matches[i]['y1'], _size=self.matches[i]['sigma1']) for i in range(len(self.matches))]
        keys2 = [cv2.KeyPoint(x=self.matches[i]['x2'], y=self.matches[i]['y2'], _size=self.matches[i]['sigma2']) for i in range(len(self.matches))]
        match_objects = [cv2.DMatch(i,i,i,0) for i in range(len(self.matches))]

        return keys1, keys2, match_objects


if __name__ == "__main__":
    matches_file = r'C:\Users\mmacferrin\Dropbox\Research\IceBerg-Personal\ASIFT\PHASE_1_KEYPOINT_GENERATION\TEST_CASES\perftest_2000_2000\data_matches.csv'
    matches_object = ASIFT_Matches(matches_file)
    matches = matches_object.read()
    print matches