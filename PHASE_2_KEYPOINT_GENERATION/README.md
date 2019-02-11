---
title: "4D Use Case: Phase 2: Keypoint Generation"
---

Phase 2: Keypoint Generation
----------------------------

The execution of finding keypoints between image tiles. (It should be noted that
many of the terms here refer to the ASIFT algorithm, although other algorithms
are now also being used either in conjunction with or instead of ASIFT. Specific
references to ASIFT are legacy.) The following steps are included.

ASIFT Executable
----------------

A standalone set of functions for matching keypoints between two individual
tiles. This is the code that does the majority of the work. Results are saved in
the Scratch sub-Directory of the “source” image, including a “data_matches.csv”
file. This version of the code uses the “fast_imas_IPOL” executable, contained
in the “fast_imas_IPOL” directory; however, other implementations (such as CUDA
functions on a GPU node) can be swapped out here.

Usage in Python:

```
A = ASIFT_Executable(output_dir = “./”,
     im1_gdal = ‘source.tif’,
     im2_gdal = ‘target.tif’,
     im1_xoff = 0,
     im1_xsize = 3000,
     im1_yoff = 0,
     im1_ysize = 3000,
     im2_xoff = 1000,
     im2_xsize = 3500,
     im2_yoff = 1000,
     im2_ysize = 3500)
A.execute(output_textfile = “OUTPUT.txt”,
verbose = False)

```

Usage standalone:

```

usage: ASIFT_Executable.py [-h] [-im1 IM1] [-im2 IM2] [-im1_gdal IM1_GDAL]
[-im1_xoff IM1_XOFF] [-im1_yoff IM1_YOFF]
[-im1_xsize IM1_XSIZE] [-im1_ysize IM1_YSIZE]
[-im2_gdal IM2_GDAL] [-im2_xoff IM2_XOFF]
[-im2_yoff IM2_YOFF] [-im2_xsize IM2_XSIZE]
[-im2_ysize IM2_YSIZE] [-im3 IM3]
[-max_keys_im3 MAX_KEYS_IM3]
[-applyfilter APPLYFILTER] [-desc DESC]
[-covering COVERING] [-match_ratio MATCH_RATIO]
[-filter_precision FILTER_PRECISION]
[-filter_radius FILTER_RADIUS] [--fixed_area]
[--verbose] output_dir

Execute the ASIFT algorithm on two image tiles and generate outputs.
positional arguments:
output_dir Path to the directory to place outputs of this executable.

optional arguments:
\-h, --help show this help message and exit
\-im1 IM1 Path to the source image (.png)
\-im2 IM2 Path to the target image (.png)
\-im1_gdal IM1_GDAL Path to the source image (.tif)
\-im1_xoff IM1_XOFF Tile x-offset in the source image (pixels)
\-im1_yoff IM1_YOFF Tile y-offset in the source image (pixels)
\-im1_xsize IM1_XSIZE Tile x-size in the source image (pixels)
\-im1_ysize IM1_YSIZE Tile y-size in the source image (pixels)
\-im2_gdal IM2_GDAL Path to the target image (.tif)
\-im2_xoff IM2_XOFF Tile x-offset in the target image (pixels)
\-im2_yoff IM2_YOFF Tile y-offset in the target image (pixels)
\-im2_xsize IM2_XSIZE Tile x-size in the target image (pixels)
\-im2_ysize IM2_YSIZE Tile y-size in the target image (pixels)
\-im3 IM3 The a-contraio input image and activates the
a-contrario Matcher (default None, not used for now).
\-max_keys_im3 MAX_KEYS_IM3
Sets the maximum number of keypoints to be used for
the a-contrario Matcher to VALUE_N (default All, not
used for now).
\-applyfilter APPLYFILTER
Selects the geometric filter to apply (default 2: ORSA
Homography) See fast_imas_IPOL/README.md for details.
\-desc DESC Selects the SIIM method (default 11: Root-SIFT) See
fast_imas_IPOL/README.md for details.
\-covering COVERING Selects the near optimal covering to be used.
Available choices are: 1.4, 1.5, 1.6, 1.7, 1.8, 1.9
and 2. (default 1.7)
\-match_ratio MATCH_RATIO
Sets the Nearest Neighbour Distance Ratio. VALUE_M is
a real number between 0 and 1. (default 0.6 for SURF
and 0.8 for SIFT)
\-filter_precision FILTER_PRECISION
Sets the precision threshold for ORSA or USAC. VALUE_P
is normally in terms of pixels. (default 3 pixels for
Fundamental and 10 pixels for Homography)
\-filter_radius FILTER_RADIUS
It tells IMAS to use rho-hyperdescriptors (pixels,
default 4)
\--fixed_area Resizes input images to have areas of about 800\*600.
\*This affects the position of matches and all output
images\*
\--verbose Increase the output verbosity
```

ASIFT Scheduler
---------------

A set of functions to handle the execution of all the “run cases” output by the
“Run Case Planner” in the last phase. On a desktop workstation these could be
run in serial, for instance. In an HPC environment, individual cases would be
farmed out to individual nodes until execution is complete.

Usage in Python:

*(Not yet implemented.)*

Usage standalone:

*(Not yet implemented.)*

ASIFT Performance Monitor
-------------------------

Measures performance metrics of the ASIFT Executable (time, memory), useful for
internal optimization

Dependencies
------------

The code requires Python 2.7+ to execute. (A Python 3 version may be forthcoming
soon.)

Code within the phases depends upon the following external Python libraries:

-   GDAL v2.2+ : the GeoSpatial Data Abstraction Library
    ([www.gdal.org](http://www.gdal.org)), and associated Python “gdal” and
    “osgeo” bindings

-   OpenCV v3.4+ : Open Computer Vision libraries and associated Python “cv2”
    bindings

License
-------

(TODO: Fill in the open-source license to be used here.)

Acknowledgements
----------------

This project is funded by the NSF’s ICEBERG Cyber-Infrastructure grant.

Acknowledgements to Mariano Rodriguez for the “fast_imas_IPOL” executable
(<http://github.com/rdguez-mariano/fast_imas_IPOL>), which CPU-versions of this
code rely upon.

Revisions:
----------

1.0 – 2019.02.10 – Draft document by Mike MacFerrin
