---
title: "4D Use Case: Phase 3: RANSAC Filtering"
---

Outputs from the ASIFT Executable have a large \# of “false positive” matching
keypoints. An implementation of the RANSAC algorithm filters these points to
generate a subset of keypoints with higher confidence.

(NOTE: Some RANSAC results, especially in poorly-fit images, generate
non-optimal homography matrices that require unrealistic distortions between
source & target images. These can be filtered out, but this is not yet
implemented).

RANSAC Filter
-------------

Starting with the “data_matches.csv” output from the ASIFT Executable in the
last phase, this runs a single RANSAC filter on the results, saving the outputs
in a “data_matches_FILTERED.csv” file.

Usage in Python:

```

def filter_ASIFT_matches(matching_keypoints_filename,
output_CSV=None,
output_good_points_only=True,
verbose=True,
ransac_reprojection_threshold=3,
eliminate_nodata_matches=True,
img1_filename=None,
img1_nodata=None,
img2_filename=None,
img2_nodata=None):

```

Usage standalone:

```

usage: RANSAC_filter.py [-h] [-ransac_threshold RANSAC_THRESHOLD]
[-img1_filename IMG1_FILENAME]
[-img1_nodata IMG1_NODATA]
[-img2_filename IMG2_FILENAME]
[-img2_nodata IMG2_NODATA] [--verbose]
[--filter_nodata_matches]
matches_filename output_filename
Filter keypoint matches using the RANSAC filter. Output a subset of keypoints
that pass RANSAC filtering.

positional arguments:
matches_filename Name of the CSV file from the ASIFT executable with
matching keypoints (typically 'data_matches.csv').
output_filename Name of the output CSV file to store the RANSAC-
filtered matches.

optional arguments:
\-h, --help show this help message and exit
\-ransac_threshold RANSAC_THRESHOLD
Pixel threshold for RANSAC filter (Default 3).
\-img1_filename IMG1_FILENAME
The name of the source image, for filtering out nodata
values.
\-img1_nodata IMG1_NODATA
The nodata value to use in the source image (default:
find in image metadata)
\-img2_filename IMG2_FILENAME
The name of the target image, for filtering out nodata
values.
\-img2_nodata IMG2_NODATA
The nodata value to use in the target image (default:
find in image metadata)
\--verbose Increase output verbosity
\--filter_nodata_matches
Filter out points adjacent to nodata values.

```

Matches Reader
--------------

A small utility for reading the “data_matches.csv” outputs from the ASIFT
Executable and creating OpenCV Keypoint objects for the RANSAC filter.

Usage in Python:

```

def read_matches_file(filename, include_keypoints=False):
'''Reads an ASIFT Executable match file.
Inputs:
\- filename: name of the "matches.csv" file
\- include_keypoints: (bool), If False, just return a numpy array of matches
from the file.
If True, return two lists of cv2.KeyPoint objects along with the numpy array of
matches from the file.

Return Values:
(If include_keypoints = False):
\- numpy array of data from the .csv file.
(If include_keypoints = True):
\- list of cv2.KeyPoint objects from source image
\- list of cv2.KeyPonit objects from target image
\- numpy array of data from the .csv file.

```

Usage standalone:

*(Standalone version not implemented)*

DrawMatches
-----------

A utility for drawing image pairs and writing them to disk, using filtered or
unfiltered results. Useful for visualization of results.

Contains two functions with slightly-different implementations

Usage in Python:

```

def drawMatches_from_file(im1_name, im2_name, matches_file, output_img_name,
gap_pixels = 20,

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

def drawMatches_from_keypoints(im1_name, im2_name, keys1, keys2, matches,
output_img_name, gap_pixels = 15,

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

```

KeyPoint Recombiner
-------------------

(not yet implemented) Takes RANSAC results between individual tiles of the
“source” and “target” images, recombines them, transforms the coordinates back
into whole-image-space. Performs another RANSAC filter to maintain internal
geometric consistency between the image matches. Outputs a final matches CSV to
output back to the user. (Optional: If the target image is geo-located, provides
image coordinates as well as geographic coordinates of keypoints in the source
image.)

Usage in Python:

*(Not yet implemented, coming soon)*

Usage standalone:

*(Not yet implemented, coming soon)*

Dependencies
------------

The code requires Python 2.7+ to execute.

Code within the phases depends upon the following external Python libraries:

-   GDAL v2.2+ : the GeoSpatial Data Abstraction Library
    ([www.gdal.org](http://www.gdal.org)), and associated Python “gdal” and
    “osgeo” bindings

-   OpenCV v3.2+ : Open Computer Vision libraries and associated Python “cv2”
    bindings

License
-------

(TODO: Fill in the open-source license to be used here.)

Acknowledgements
----------------

This project is funded by the NSF’s ICEBERG Cyber-Infrastructure grant.

Revisions:
----------

1.0 – 2019.02.10 – Draft document by Mike MacFerrin
