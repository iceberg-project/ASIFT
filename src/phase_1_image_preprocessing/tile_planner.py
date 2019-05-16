# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 12:44:42 2018

Tile_Planner.py

Arguments: Tile_Planner.py /path/to/image.tif /path/to/out.csv tilesize -nodata NODATA -size_tolerance SIZE_TOLERANCE

Path to the image
Path to the csv file
Size
-size_tolerance: A pixel-tolerance (up to +N pixels) for the tile size, to avoid "slivers" and "small corners", if <N pixels wide it will append to the nearest tile.
-nodata: NODATA value in the source image

@author: mmacferrin
"""
import argparse
import os
import numpy
#from osgeo import gdal, gdalconst
from scratch_directory_manager import SCRATCH_Manager
from csv_writer import write_csv
import image_pyramid as PYRAMID
#from tile_generator import create_constrast_enhanced_tile

def create_tiles_from_image(img_filename,
                            csv_file=None,
                            tilesize=3000,
                            nodata=None,
                            minimum_size=1000,
                            pyramid_levels=0,
                            write_tiles_to_disk=True,
                            overwrite=False,
                            contrast_enhance=None, # (choices so far: None or 'equalize')
                            verbose=True):
    '''Given an image file name:
        1) Create a directory where the processing on this tile will take place.
        2) Create a set of pyramid images (if pyramid_levels > 0) to add to the tiles queue.
        3) For each pyramid image, tile it up into "tilesize" portions, no smaller than "minimum_size" on any one dimension (if smaller, will tack onto an adjacent tile).
        4) Check sizes and nodata values in each tile. If nodata isn't specified, get it from the image if it's there.
        5) Output all individual tiles to a CSV file, return the CSV file name to the calling function.

        csv_file can be a local filename without a path (if so, put it in the scratch directory), or a full path name, in which case it will stay where it was said.
        If csv_file is None, the file will be given a the same name as the scratch directory and put in there.
    '''
    # Get the hashed Scratch directory where we should place these pyramids and the tiles, also the same string that we will name the
    m = SCRATCH_Manager()
    scratch_basename = m.lookup(img_filename)
    # If a directory is not yet in place to do this, create one.
    if scratch_basename is None:
        scratch_subdir = m.add_directory(img_filename)
        scratch_basename = os.path.split(scratch_subdir)[-1]
    else:
        scratch_subdir = os.path.join(m.scratch_dir, scratch_basename)

    if csv_file is None:
        csv_file = scratch_basename + ".csv"

    # If only a local filename is entered, add the scratch directory to it.
    if os.path.split(csv_file)[-1] == os.path.join(*os.path.split(csv_file)):
        csv_file = os.path.join(scratch_subdir, csv_file)

    # If we want to use pyramids here, create them (overwrite only if flag set above)
    if pyramid_levels > 0:
        pyramid_paths = PYRAMID.write_image_pyramid(img_filename,
                                                    pyramid_levels,
                                                    dest_dir = scratch_subdir,
                                                    nodata = nodata,
                                                    overwrite = overwrite,
                                                    verbose = verbose)
        image_paths = numpy.append([img_filename], pyramid_paths)
    else:
        # Otherwise, just use the one file.
        image_paths = [img_filename]

    # Main image is 0, the rest will be 1...N (with zoom levels being 1 for main image, 2...2**(N) for the rest.)
    pyramid_levels += 1

    # All the tile info from all pyramid levels will go into this list, see very end of first loop.
    TOTAL_tile_list_flattened = []

    # Modify for various pyramid levels.
    for pyramid_i in range(pyramid_levels):

        img_path = image_paths[pyramid_i]
        zoom_level = 2**pyramid_i

        # Read in the image, get the data and metadata
        img_ds = gdal.Open(img_path, gdalconst.GA_ReadOnly)
        band = img_ds.GetRasterBand(1)
        img_data = band.ReadAsArray()
        XSize = band.XSize
        YSize = band.YSize
        file_ext = os.path.splitext(img_path)[-1]
        # Get the nodata value, if it's in the metadata or the function parameter
        if nodata is None:
            NDV = band.GetNoDataValue()
        else:
            NDV = nodata
        if NDV is None:
            NDV = -999

        # Get a mask for the nodata values, this will be important shortly.
        nodata_mask = (img_data == NDV)

        # 2: Divide the image boundaries into a default set of tiles.
        tile_xcoords = numpy.arange(0,XSize,tilesize)
        if tile_xcoords[-1] < XSize:
            tile_xcoords = numpy.append(tile_xcoords, XSize)

        tile_ycoords = numpy.arange(0,YSize,tilesize)
        if tile_ycoords[-1] < YSize:
            tile_ycoords = numpy.append(tile_ycoords, YSize)

        # Create a numpy datatype to store this data in an array.
        tile_data_dtype = numpy.dtype([('file_path', numpy.str, 4096),
                                       ('tile_path', numpy.str, 4096),
                                       ('pyramid_level', numpy.int),
                                       ('Xoff' , numpy.int),
                                       ('Xsize', numpy.int),
                                       ('Yoff' , numpy.int),
                                       ('Ysize', numpy.int),
                                       ('nodata', numpy.int)
                                       ])

        blank_tile_data = numpy.zeros((1,),dtype=tile_data_dtype)[0]

        # Create an empty 2d array to store tile info.
        tile_list = numpy.zeros(((len(tile_xcoords)-1), (len(tile_ycoords)-1)), dtype=tile_data_dtype)
        # A helper array that flags tiles that are slivers, and need to merge with adjacent tiles.
        # Filled with "left", "right", "top", "bottom" for direction it needs to merge. None if no need.
        tile_needs_to_merge = numpy.zeros((len(tile_xcoords)-1, len(tile_ycoords)-1), dtype="S10")

        # Loop over all the proposed tiles above.
        # In this loop, identify the boudaries of needed tiles to eliminate no-data spans within them.
        # If the resulting tile needs to merge with a neightbor, flag it with the direction is needs to merge.
        for tile_i,x in enumerate(tile_xcoords[:-1]):
            for tile_j,y in enumerate(tile_ycoords[:-1]):

                nodata_slice = nodata_mask[y:tile_ycoords[tile_j+1], x:tile_xcoords[tile_i+1]]
                # If this entire tile is Nodata, just skip this tile completely and move along.
                if numpy.all(nodata_slice):
                    continue

                tile_xsize = tile_xcoords[tile_i+1] - x
                tile_ysize = tile_ycoords[tile_j+1] - y

#                # All the data's there, zero NDV values. Just include the whole damned slice!
#                if not numpy.any(nodata_slice):
#                    tile_list[tile_i,tile_j] = numpy.array([(img_path, "", zoom_level, x, tile_xsize, y, tile_ysize, NDV)], dtype=tile_data_dtype)
#                    continue

                # Otherwise, there's some nodata values in there, so figure out if we should trim left/right/top/bottom at all for this tile.

                # Get the minimum and maximum rows with at least one good data point.
                # Remember y-values go downward in these images.
                rows_with_data = numpy.where(~numpy.all(nodata_slice, axis=1))[0]
                data_top_row = numpy.min(rows_with_data)
                data_bottom_row = numpy.max(rows_with_data)

                # Get the minimum and maximum cols with at least one good data point.
                cols_with_data = numpy.where(~numpy.all(nodata_slice, axis=0))[0]
                data_left_col = numpy.min(cols_with_data)
                data_right_col = numpy.max(cols_with_data)

                # Figure out the new image boundaries from this (maybe the same as before)
                tile_x     = x + data_left_col
                tile_xsize = data_right_col - data_left_col + 1
                tile_y     = y + data_top_row
                tile_ysize = data_bottom_row - data_top_row + 1

                # Do we need to merge this?  If so, flag it!
                tile_min_size = tile_xsize if (tile_xsize < tile_ysize) else tile_ysize
                # If it's smaller than allowed, figure out which side it's on.
                if tile_min_size < minimum_size:
                    # It's thin vertically (x-dimension is short)
                    if tile_xsize == tile_min_size:
                        if tile_x == x:
                            # The left side is flush, stick it over there.
                            tile_needs_to_merge[tile_i,tile_j] = "left"
                        elif (tile_x + tile_xsize) == tile_xcoords[tile_i+1]:
                            # It's flush on the right side, stick it over there.
                            tile_needs_to_merge[tile_i,tile_j] = "right"
                        else:
                            # If it's flush neither left nor right, then we need to just keep it there, don't merge with anything (just run the sliver)
                            pass
                    # Otherwise it's thin vertically (y-dimension is short)
                    elif tile_ysize == tile_min_size:
                        if tile_y == y:
                            # The top side is flush, stick it above.
                            tile_needs_to_merge[tile_i,tile_j] = "top"
                        elif (tile_y + tile_ysize) == tile_ycoords[tile_j+1]:
                            # It's flush on the bottom side, stick it below
                            tile_needs_to_merge[tile_i,tile_j] = "bottom"
                        else:
                            # If it's flush neither top nor bottom, then we need to just keep it there, don't merge with anything (just run the sliver)
                            pass
                    else:
                        raise ValueError("tile_min_size ({0}) doesn't match tile_xsize ({1}) or tile_ysize ({2}), logic error somewhere.".format(
                                            tile_min_size, tile_xsize, tile_ysize))


                # Put an entry in our table of tile information (will check later to merge if needed)
                tile_list[tile_i,tile_j] = numpy.array([(img_filename, "", zoom_level, tile_x, tile_xsize, tile_y, tile_ysize, NDV)], dtype=tile_data_dtype)

        # Tiles that are below "size_tolerance" pixels, combine with the tile next to it.
        for tile_i,x in enumerate(tile_xcoords[:-1]):
            for tile_j,y in enumerate(tile_ycoords[:-1]):
                this_tile_data = tile_list[tile_i,tile_j]

                tile_merge_flag = tile_needs_to_merge[tile_i,tile_j]

                # If we don't need to merge this, move along.
                if (tile_merge_flag == "") or (this_tile_data == blank_tile_data):
                    continue

                # We do need to merge it. Check with directino and make sure we're not out of bounds
                elif tile_merge_flag == "left":
                    if tile_i == 0:
                        # We're at the left-most tile, can't merge left, move along
                        continue
                    # Merge with left tile.
                    left_tile_data = tile_list[tile_i-1,tile_j]
                    # If there is no left tile to merge with, skip this, move along, UNLESS the tile to the left was already merged.
                    if left_tile_data == blank_tile_data:
                        # IF the tile to the left was already merged, and the 
                        # tile above was also merged, it means the new boundaries
                        # already encompass this "corner tile," and we can omit it.
                        if tile_needs_to_merge[tile_i-1, tile_j] != "" and (tile_j == 0 or tile_needs_to_merge[tile_i, tile_j-1] != ""):
                            tile_list[tile_i,tile_j] = blank_tile_data
                        continue

                    left_tile_data["Xsize"] = this_tile_data["Xoff"] + this_tile_data["Xsize"] - left_tile_data["Xoff"]
                    # Make sure the Yoffset and Ysize reflect the min and max dimensions of the combined data values.
                    Yoff = min(this_tile_data["Yoff"], left_tile_data["Yoff"])
                    left_tile_data["Ysize"] = max(left_tile_data["Yoff"] + left_tile_data["Ysize"], this_tile_data["Yoff"] + this_tile_data["Ysize"]) - Yoff
                    left_tile_data["Yoff"] = Yoff

                elif tile_merge_flag == "right":
                    if tile_i >= (len(tile_list)-1):
                        # We're at the right-most tile, can't merge right, move along
                        continue

                    # Merge with right tile.
                    right_tile_data = tile_list[tile_i+1,tile_j]
                    # If there is no right tile to merge with, skip this, move along
                    if right_tile_data == blank_tile_data:
                        continue

                    right_tile_data["Xsize"] = right_tile_data["Xsize"] + right_tile_data["Xoff"] - this_tile_data["Xoff"]
                    right_tile_data["Xoff"] = this_tile_data["Xoff"]
                    # Make sure the Yoffset and Ysize reflect the min and max dimensions of the combined data values.
                    Yoff = min(this_tile_data["Yoff"], right_tile_data["Yoff"])
                    right_tile_data["Ysize"] = max(right_tile_data["Yoff"] + right_tile_data["Ysize"], this_tile_data["Yoff"] + this_tile_data["Ysize"]) - Yoff
                    right_tile_data["Yoff"] = Yoff

                elif tile_merge_flag == "top":
                    if tile_j == 0:
                        # We're at the top-most tile, can't merge up, move along
                        continue

                    # Merge with upper tile.
                    above_tile_data = tile_list[tile_i,tile_j-1]
                    # If there is no upper tile to merge with, skip this, move along
                    if above_tile_data == blank_tile_data:
                        # IF the tile to the left was already merged, and the 
                        # tile above was also merged, it means the new boundaries
                        # already encompass this "corner tile," and we can omit it.
                        if tile_needs_to_merge[tile_i, tile_j-1] != "" and (tile_i == 0 or tile_needs_to_merge[tile_i-1, tile_j] != ""):
                            tile_list[tile_i,tile_j] = blank_tile_data
                        continue

                    above_tile_data["Ysize"] = this_tile_data["Yoff"] + this_tile_data["Ysize"] - above_tile_data["Yoff"]
                    # Make sure the Xoffset and Xsize reflect the min and max dimensions of the combined data values.
                    Xoff = min(this_tile_data["Xoff"], above_tile_data["Xoff"])
                    above_tile_data["Xsize"] = max(above_tile_data["Xoff"] + above_tile_data["Xsize"], this_tile_data["Xoff"] + this_tile_data["Xsize"]) - Xoff
                    above_tile_data["Xoff"] = Xoff

                elif tile_merge_flag == "bottom":
                    if tile_j >= (len(tile_list[tile_i])-1):
                        # We're at the bottom-most tile, can't merge right, move along
                        continue

                    # Merge with right tile.
                    below_tile_data = tile_list[tile_i,tile_j+1]
                    # If there is no right tile to merge with, skip this, move along
                    if below_tile_data == blank_tile_data:
                        continue

                    below_tile_data["Ysize"] = below_tile_data["Ysize"] + below_tile_data["Yoff"] - this_tile_data["Yoff"]
                    below_tile_data["Yoff"] = this_tile_data["Yoff"]
                    # Make sure the Xoffset and Xsize reflect the min and max dimensions of the combined data values.
                    Xoff = min(this_tile_data["Xoff"], below_tile_data["Xoff"])
                    below_tile_data["Xsize"] = max(below_tile_data["Xoff"] + below_tile_data["Xsize"], this_tile_data["Xoff"] + this_tile_data["Xsize"]) - Xoff
                    below_tile_data["Xoff"] = Xoff

                else:
                    raise ValueError("Unknown tile_needs_to_merge array flag: {0}".format(tile_merge_flag))

                # Now that we've merged, get rid of this sliver tile.
                tile_list[tile_i,tile_j] = blank_tile_data
#                tile_needs_to_merge[tile_i, tile_j] = ""


        # Add our little 2D array into the flattened array with all the other pyramid levels
        for i in range(tile_list.shape[0]):
            for j in range(tile_list.shape[1]):
                tile_record = tile_list[i,j]

                if tile_record != blank_tile_data:

                    xoff, yoff = tile_record["Xoff"], tile_record["Yoff"]
                    xsize, ysize = tile_record["Xsize"], tile_record["Ysize"]
                    zoom_level = tile_record["pyramid_level"]

                    # Update the tile path with the tile name, after arranging the boundaries.
                    tile_fname = "{0:s}_{1:d}_{2:d}_{3:d}_{4:d}_{5:d}{6:s}".format(scratch_basename,
                                                                                   zoom_level,
                                                                                   xoff,
                                                                                   xsize,
                                                                                   yoff,
                                                                                   ysize,
                                                                                   file_ext)
                    tile_path = os.path.join(scratch_subdir, tile_fname)
                    tile_record["tile_path"] = tile_path

                    # Add to our list of tiles.
                    TOTAL_tile_list_flattened.append(tile_record)

                    # While we're in here, go ahead and create the tile itself.
                    if write_tiles_to_disk:
                        tile_data = img_data[yoff : (yoff+ysize), xoff : (xoff+xsize)]

                        create_constrast_enhanced_tile(tile_record["file_path"],
                                                       tile_path,
                                                       data_array=tile_data,
                                                       nodata=NDV,
                                                       xoff=None,
                                                       yoff=None,
                                                       xsize=None,
                                                       ysize=None,
                                                       overwrite=overwrite,
                                                       contrast_enhance = contrast_enhance,
                                                       verbose=verbose)



    tile_ndarray = numpy.array(TOTAL_tile_list_flattened, dtype=tile_data_dtype)


    # If csv_file is set, spit out the data to a CSV file.
    if csv_file != None:
        write_csv(tile_ndarray, csv_file, verbose=verbose)


    # Return the data that would be stored within the CSV file back to the calling function.
    return tile_ndarray



def define_and_parse_arguments():
    parser = argparse.ArgumentParser(description = "Create a CSV defining tiles of an image and create a csv summary file.")
    parser.add_argument('image', type=str, help="Path to the source image (tif or png)")
    parser.add_argument('-tilesize',  type=int, default=3000, help="Size (pixels) of the tiles (default: 3000)")
    parser.add_argument('-csv_file', type=str, default='none', required=False, help="Path to the output CSV file of tile descriptors (default: put in same directory as the tiles.)")
    parser.add_argument('-nodata', type=int, default=-999, required=False, help="No-data value in the source image (default: -999, maps to None)")
    parser.add_argument('-contrast_enhance', type=str, default="", required=False, help="Method of contrast-enhancing output tiles. Only applied if tiles are written to disk. Choices so far: 'none' or 'equalize'. Default: 'none'")
    parser.add_argument('-minimum_size', type=int, default=1000, required=False, help="Minimum size tolerance (pixels) on any axis to avoid slivers (default: 1000). Slivers less than that size will be appended to neighboring tiles.")
    parser.add_argument('-pyramid_levels', type=int, default=0, required=False, help="Number of factor-of-two pyramid levels to create tiles (default 0, meaning original size only)")
    parser.add_argument('--dont_write_tiles', required=False, action='store_true', default=False, help="Skip writing tiles to disk. If set, just create the CSV with tile descriptions (does not delete tiles if they already exist). (Default: write the tiles.)")
    parser.add_argument('--overwrite', required=False, action='store_true', default=False, help="Overwrite pyramids and tiles if they already exist for this image. (default False)")
    parser.add_argument('--verbose', required=False, action='store_true', default=False, help="Increase output verbosity")

    return parser.parse_args()

if __name__ == "__main__":
    args = define_and_parse_arguments()

    data = create_tiles_from_image(args.image,
                                   csv_file = None if args.csv_file == '' else args.csv_file,
                                   tilesize = args.tilesize,
                                   nodata = None if args.nodata == -999 else args.nodata,
                                   minimum_size = args.minimum_size,
                                   pyramid_levels = args.pyramid_levels,
                                   write_tiles_to_disk = not args.dont_write_tiles,
                                   overwrite = args.overwrite,
                                   contrast_enhance = None if args.contrast_enhance.strip().lower() in ("none","") else args.contrast_enhance.strip().lower(),
                                   verbose = args.verbose)
