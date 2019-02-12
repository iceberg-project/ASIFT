# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 14:21:57 2018

Tile_Generator.py -- used to export tiles with enhanced contrast into the scratch directory.

Arguments: Tile_Generator.py /path/to/image.tif /path/to/output_tile.tif -xoff XOFF -yoff YOFF -xsize XSIZE -ysize YSIZE -nodata NODATA
Path the source image (req'd)
Path to the contrast-enhanced tile (req'd)
-xoff: X-Offset of the tile within the source image, in pixels (opt'l)
-yoff: Y-Offset of the tile within the source image, in pixels (opt'l)
-xsize, -ysize: Size of the tile within the source image, in pixels (opt'l)
-nodata: The NODATA value in the image.

If one optional argument is used, they should all be used.

@author: mmacferrin
"""
import argparse
import os
from osgeo import gdal, gdalconst
import numpy

import Contrast_Enhancer

def write_tile(src_filename,
               dst_filename,
               data_array=None,
               contrast_enhance="equalize",
               nodata=None,
               xoff=None,
               yoff=None,
               xsize=None,
               ysize=None,
               overwrite=False,
               verbose=True):
    '''From the source image, create a tile image with contrast fit to a gaussian curve to enhance the contrast from other skewed images.
    (x,y) offset and sizes, when set to zero, just use the whole image.'''
    # Check if the data is already on disk. If so (and we don't want to overwrite), just return.
    if not overwrite and os.path.exists(dst_filename):
        return

    # 1: get the metadata from the source file. Including the projection info
    # to put metadata in the destination file as well. Also the XSize, YSize
    # Ingest the image.
    img_ds = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
    # NOTE: Only dealing with single-band, greyscale images here. NOT multi-spectral. This would need to be adjusted for any multi-spectral work.
    img_band = img_ds.GetRasterBand(1)
    img_meta = img_ds.GetMetadata()
    img_datatype = img_band.DataType

    img_xsize = int(img_band.XSize)
    img_ysize = int(img_band.YSize)

    # Get the driver.
    drv = img_ds.GetDriver()

    # Get the geoTranform for the image
    img_geoT = img_ds.GetGeoTransform()
    # Get the projection for the image
    img_proj = img_ds.GetProjection()

    NDV = img_band.GetNoDataValue() if (nodata is None) else nodata

    # Open the source image, get the tile data. (only if data array is not provided.)
    # All None values in data boudnaries get assigned to the edge of the image
    xoff = 0 if (xoff is None or xoff < 0) else xoff
    yoff = 0 if (yoff is None or yoff < 0) else yoff

    if data_array is None:
        # Make sure xsize stays within the bounds of the image
        xsize = (img_xsize - xoff) if (xsize is None) else int(xsize)
        if xsize+xoff > img_xsize:
            xsize = img_xsize - xoff
        # Make sure ysize stays within the bounds of the image
        ysize = (img_ysize - yoff) if (ysize is None) else int(ysize)
        if ysize+yoff > img_ysize:
            ysize = img_ysize - yoff

        data_array = img_band.ReadAsArray(xoff=xoff, yoff=yoff, win_xsize=xsize, win_ysize=ysize)
    else:
        xsize = data_array.shape[1] if (xsize is None) else xsize
        if xsize+xoff > data_array.shape[1]:
            xsize = data_array.shape[1] - xoff

        ysize = data_array.shape[0] if (ysize is None) else ysize
        if ysize+yoff > data_array.shape[0]:
            ysize = data_array.shape[0] - yoff

        # If we're using anything other than the boundaries of the data array, trim the data accordingly.
        if (xoff > 0) or (xsize < data_array.shape[1]) or (yoff > 0) or (ysize < data_array.shape[0]):
            data_array = data_array[yoff:(yoff+ysize), xoff:(xoff+xsize)]

    # 3: Run a histogram match against a gaussian curve (can do a flat curve, or whatever else)
    # Look to https://docs.opencv.org/3.1.0/d5/daf/tutorial_py_histogram_equalization.html for histogram ideas.
    # Or here: http://scikit-image.org/docs/0.9.x/auto_examples/plot_equalize.html
    # FLAT CURVE- HISTOGRAM EQUALIZER
    ndv_mask = (data_array == NDV)

    if contrast_enhance.strip().lower() == "equalize":
        # Fill in all the normalized pixels that aren't nodata values.
        data_normalized = numpy.copy(data_array)
        data_normalized[~ndv_mask] = Contrast_Enhancer.enhance_contrast(data_array[~ndv_mask], algorithm="equalize")

    elif contrast_enhance.strip().lower() == "none" or contrast_enhance is None:
        data_normalized = data_array

    else:
        raise NotImplementedError("Contrast enhancement not implemented: " + str(contrast_enhance))

    # If the file already exists and we don't want to overwrite, just spit back the normalized values here.
    if os.path.exists(dst_filename):
        if overwrite:
            if verbose:
                print "Removing old '{0}'".format(os.path.split(dst_filename)[-1])
            os.remove(dst_filename)
        else:
            return data_normalized

    # 4: Create the new file, dump the data into it.
    dest_ds = drv.Create(dst_filename, xsize=xsize, ysize=ysize, bands=1, eType=img_datatype)
    dest_band = dest_ds.GetRasterBand(1)

    # Write the data into the band.
    dest_band.WriteArray(data_normalized)

    # Use the GeoTranform info to calculate the new offset corner pixels.
    xcorner, xstep_x, xstep_y, ycorner, ystep_x, ystep_y = img_geoT
    dest_geoT = (xcorner + (xoff*xstep_x) + (yoff*xstep_y),
                 xstep_x,
                 ystep_x,
                 ycorner + (xoff*ystep_x) + (yoff*ystep_y),
                 ystep_x,
                 ystep_y)

    dest_ds.SetGeoTransform(dest_geoT)
    dest_ds.SetProjection(img_proj)
    dest_ds.SetMetadata(img_meta)

    if NDV != None:
        dest_band.SetNoDataValue(NDV)

    # Deallocate the objects, save the image.
    dest_ds = None
    dest_band = None

    if verbose:
        print os.path.split(dst_filename)[-1], "written."

    return data_normalized


def define_and_parse_arguments():
    parser = argparse.ArgumentParser(description = "Contrast-enhance a tile within an image, output to a new image.")
    parser.add_argument('source', type=str, help="Path to the source image (tif or png)")
    parser.add_argument('dest',   type=str, help="Path to the desination tile to be created (tif or png)")
    parser.add_argument('-nodata', type=int, default=-999, required=False, help="No-data value in the source image (default: -999, translates to None)")
    parser.add_argument('-xoff',  type=int, default=-1, required=False, help="X-offset for the upper-left corner of the tile, in pixels")
    parser.add_argument('-xsize', type=int, default=-1, required=False, help="Y-offset for the upper-left corner of the tile, in pixels")
    parser.add_argument('-yoff',  type=int, default=-1, required=False, help="X-size of the tile, in pixels")
    parser.add_argument('-ysize', type=int, default=-1, required=False, help="Y-size of the tile, in pixels")
    parser.add_argument('-contrast_enhance', type=str, default="none", required=False, help="Contrast enhancement, choices: none, equalize (default none)")
    parser.add_argument('--overwrite', required=False, action='store_true', default=False, help="Overwrite tile if already on disk")
    parser.add_argument('--verbose', required=False, action='store_true', default=False, help="Increase the output verbosity")

    return parser.parse_args()

if __name__ == "__main__":
    args = define_and_parse_arguments()
    write_tile(args.source,
               args.dest,
               nodata=None if args.nodata == -999 else args.nodata,
               contrast_enhance=args.contrast_enhance,
               xoff=args.xoff,
               yoff=args.yoff,
               xsize=args.xsize,
               ysize=args.ysize,
               overwrite=args.overwrite,
               verbose=args.verbose)
