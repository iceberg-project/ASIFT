# ASIFT
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/ae1c0eb2ae3d440eb9a7a5625cb75cc2)](https://app.codacy.com/app/iparask/ASIFT?utm_source=github.com&utm_medium=referral&utm_content=iceberg-project/ASIFT&utm_campaign=Badge_Grade_Dashboard)

# Inroduction
The ASIFT Workflow is a set of combined algorithms made available through the IceBerg project to automatically geo-locate old aerial or satellite imagery using a database of well-know, geo-located and ortho-rectified current imagery. 

# The goal of the ASIFT workflow
Workflow is for a user to take an airborne or satellite image anywhere that we have WorldView Ortho-rectified imagery available, and where the user knows the approximate location of the photo (within ~100 km) but does not have geo-location information on it. The ASIFT Workflow be able to pin down where that photo was taken, automatically determine a likely set of geo-located ground control points for the image, and ortho-rectify the image if needed.

# Pre-conditions to run the ASIFT Use case 
   ## Geographically-distinct and permanent features:
There must be distinct, relatively-high contrast features within the image that would create good “key points” for the ASIFT algorithm. Mountainous regions are good, for instance. The flat-white featureless interior of an ice sheet is not.
  - The key points must be invariant through time (seasons to decades): i.e. a stable mountain ridge is a good key point. A drifting sand dune, an eroding riverbank, or flat white fields of snow or grass are not good key points.
  - The user must have a general idea where the image is located (the ASIFT algorithm cannot search the entire world, at least not yet).     - The user can provide one of the two following pieces of data to fulfill this requirement:
  1. A center Latitude/longtitude location and a search radius (within 50km of 45.8 N 142.3 W, e.g.)
  2. A shapefile in WGS84 (Latitude/longtitude) coordinates, containing a single polygon within which to search.

# Software Dependencies

- Opencv2
- gdal
- pandas
- numpy
- cmake
