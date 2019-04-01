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
import unittest
import os
import json
import filecmp
import cv2


class TestImgParser(unittest.TestCase):
    """
    Test JSON File content
    """
    def test_read_json(self):
        """
        This function will path for source image and target data sets
        and produce a JSON file for their coordinates and names .
        """
        img1 = cv2.imread('2000.tif')
        json_dict = {}
        data = []
        org_path = "/home/aymen/SummerRadical/tiles"
        for path, files in os.walk(org_path):
            for filename in files:
                if filename.endswith(".tif"):
                    print 'found GEOTIFF Images' + filename
                    img2 = cv2.imread(path + filename)
                    tmp_dict = {}
                    tmp_dict["img1"] = img1
                    tmp_dict["img2"] = path + filename
                    tmp_dict["x1"] = img1.shape[0]
                    tmp_dict["y1"] = img1.shape[1]
                    tmp_dict["x2"] = img2.shape[0]
                    tmp_dict["y2"] = img2.shape[0]
                    data.append(tmp_dict)

        json_dict["Dataset"] = data
        # Writing information to JSON file
        with open("original_images.json", "w") as outfile:
            json.dump(json_dict, outfile, indent=4, sort_keys=True)
        path = "original_images.json"
        path2 = "test_images.json"
        self.assertTrue(filecmp.cmp(path2, path), 'error')
        os.remove('original_images.json')

if __name__ == "__main__":
    unittest.main()
