"""
Image parser utility for 4D gelocation use case
==========================================================
This script contains python script that reads a dataset (path) and produce a
JSON file with information about each image to be used in the EnTK Pipeline
script for the 4D Geolocation (ASIFT) Usecase.

Author: Aymen Alsaadi
Email : aymen.alsaadi@rutgers.edu
License: MIT
Copyright: 2018-2019
"""
from __future__ import print_function
import json
import os
import argparse
import cv2


def args_parser():
    """
    Argument Parsing Function for the script.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Path of the dataset')
    parser.add_argument('source_img', help='Name of the image to be matched with the dataset')
    return parser.parse_args()

def img_parser():
    """
    Traversing over all the files inside the target
    dataset path and extract each image information.
    """
    args = args_parser()
    # Reading the source image
    img1 = cv2.imread(args.source_img)
    json_dict = {}
    data = []
    for path, dirs, files in os.walk(args.path):
        for filename in files:
            if filename.endswith(".tif"):
                print ('found GEOTIFF Images ' + filename)
                img2 = cv2.imread(path + filename)
                tmp_dict = {}
                tmp_dict["img1"] = args.source_img
                tmp_dict["img2"] = path + filename
                tmp_dict["x1"] = img1.shape[0]
                tmp_dict["y1"] = img1.shape[1]
                tmp_dict["x2"] = img2.shape[0]
                tmp_dict["y2"] = img2.shape[0]
                data.append(tmp_dict)

    json_dict["Dataset"] = data

    # Writing information to JSON file
    with open("images.json", "w") as outfile:
        json.dump(json_dict, outfile, indent=4, sort_keys=True)


if __name__ == '__main__':

    img_parser()
