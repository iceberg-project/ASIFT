# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 17:56:20 2018

Image_Pyramid.py img dest_base levels --verbose --overwrite

@author: mmacferrin
"""

#from osgeo import gdal, gdalconst
import argparse
import os

def write_image_pyramid(src_img, num_levels, dest_dir=None, nodata=None, overwrite=False, verbose=True):
    '''Given a source image, create a set of destination images, each scaled by a factor of two.
    If the image already has a set of "overview" pyramids in it (may geotifs do), use those. Otherwise create them and write it out ourselves.'''
    assert num_levels > 0

    # If dest_dir isn't given, set it to the source dir.
    if dest_dir is None:
        dest_dir = os.path.split(src_img)[0]

    # Ingest the image.
    img_ds = gdal.Open(src_img, gdalconst.GA_ReadOnly)
    # NOTE: Only dealing with single-band, greyscale images here. NOT multi-spectral. This would need to be adjusted for any multi-spectral work.
    img_band = img_ds.GetRasterBand(1)
    img_meta = img_ds.GetMetadata()
    img_datatype = img_band.DataType

    # Get the driver.
    drv = img_ds.GetDriver()

    # Get the geoTranform for the image
    img_geoT = img_ds.GetGeoTransform()
    # Get the projection for the image
    img_proj = img_ds.GetProjection()

    NDV = img_band.GetNoDataValue() if (nodata is None) else nodata

    # Get the file extension
    file_base, file_ext = os.path.splitext(os.path.split(src_img)[-1])

    dest_fnames = [None] * num_levels

    for i in range(num_levels):

        size_level = 2**(i+1)

        dest_fname = os.path.join(dest_dir, file_base) + "_" + str(size_level) + file_ext
        dest_fnames[i] = dest_fname

        # If we don't want to overwrite and the file already exists, don't re-create it, just move along.
        if not overwrite and os.path.exists(dest_fname):
            if verbose:
                print os.path.split(dest_fname)[-1], "already exists."
            continue

        # Compute the new geotransform
        dest_geoT = list(img_geoT)
        # Multiply the resolutions in each direction by the appropriate factor of two
        dest_geoT[1] *= size_level
        dest_geoT[2] *= size_level
        dest_geoT[4] *= size_level
        dest_geoT[5] *= size_level
        dest_geoT = tuple(dest_geoT)

        dest_ds = drv.Create(dest_fname, img_band.XSize / size_level, img_band.YSize / size_level, 1, img_datatype)

        dest_ds.SetGeoTransform(dest_geoT)
        dest_ds.SetProjection(img_proj)
        dest_ds.SetMetadata(img_meta)

        dest_band = dest_ds.GetRasterBand(1)

        if NDV != None:
            dest_band.SetNoDataValue(NDV)

        # This is the easy way of rescaling in GDAL.
        gdal.RegenerateOverview(img_band, dest_band, 'average')

        # Write to disk
        dest_ds = None

        if verbose:
            print os.path.split(dest_fname)[-1], "written."

    return dest_fnames

def define_and_parse_arguments():
    parser = argparse.ArgumentParser(description = "Create N levels of pyramid images from a source image, save it to destination filenames beginning with 'dest_filebase'.")
    parser.add_argument('source_img', type=str, help="Path to the source image (tif or png)")
    parser.add_argument('N',  type=int, default=1, help="Number of factor-of-two levels to pyramid. 0 is only the original file. (default: 1)")
    parser.add_argument('-dest_dir', type=str, required=False, default='', help="Path to the directory of the destination image tiles (default: same directory as source image)")
    parser.add_argument('-nodata', type=int, default=-999, required=False, help="Nodata value in the image (default: use NoDataValue found in image)")
    parser.add_argument('--verbose', required=False, action='store_true', default=False, help="Increase the output verbosity")
    parser.add_argument('--overwrite', required=False, action='store_true', default=False, help="If present, overwrite the tiles created if image was already processed previously. (default: Keep tiles there if already used.)")

    return parser.parse_args()

if __name__ == "__main__":
    args = define_and_parse_arguments()
    write_image_pyramid(args.source_img,
                        args.N,
                        dest_dir = args.dest_dir if args.dest_dir != '' else None,
                        nodata = args.nodata if args.nodata != -999 else None,
                        overwrite=args.overwrite,
                        verbose=args.verbose)
