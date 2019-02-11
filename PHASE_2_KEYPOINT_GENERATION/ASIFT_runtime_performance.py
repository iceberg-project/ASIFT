# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 16:51:46 2018

@author: mmacferrin

A quick routine for using the ASIFT_Test_Case class to perform testing on progressively larger images and plotting the output.
"""

from ASIFT_class_definitions import ASIFT_Executable

##################################################################################
#
## Test case 1
#case1 = ASIFT_Test_Case(im1="adam1.png",
#                        im2="adam2.png",
#                        output_dir='./TEST_CASES/CASE01_adam1_adam2')
#case1.execute(output_textfile="OUTPUT.txt")
#
## Test case 2
#case2 = ASIFT_Test_Case(im1="adam2.png",
#                        im2="adam1.png",
#                        output_dir="./TEST_CASES/CASE02_adam2_adam1")
#case2.execute(output_textfile="OUTPUT.txt")

##################################################################################

output_csv_filename = "./TEST_CASES/perf_monitoring.csv"

im1_gdal = "WV01_20101207_102001000F043B00_102001001153AD00_seg1_2m_ortho.tif"
im1_center_pixel = [7100,6100]
im2_gdal = "WV01_20161218_102001005C18BF00_1020010058E7BE00_seg1_2m_ortho.tif"
im2_center_pixel = [14100,29200]

##################################################################################

# pixel size in a single dimension (x,y), square tiles
im_case_sizes = [500,600,700,800,900,1000,1250,1500,1750,2000,2250,2500,2750,3000,3250,3500,3750,4000,4250,4500,4750,5000,5500,6000,6500,7000,7500]

# Create the CSV output file of all the performance results.
csv_header = "experiment_type,im1_gdal,im2_gdal,size1_px,size2_px,max_mem_kb,runtime_s,num_matches\n"
with open(output_csv_filename,'w') as csv_file:
    csv_file.write(csv_header)

for size in im_case_sizes:
    # Run each case 10 times to get a distribution.
    for i in range(10):

        # Run first with both images scaling up at the same time.
        test_case = ASIFT_Executable(im1_gdal=im1_gdal,
                                    im1_xoff=im1_center_pixel[0] - (size/2),
                                    im1_yoff=im1_center_pixel[1] - (size/2),
                                    im1_xsize=size,
                                    im1_ysize=size,

                                    im2_gdal=im2_gdal,
                                    im2_xoff=im2_center_pixel[0] - (size/2),
                                    im2_yoff=im2_center_pixel[1] - (size/2),
                                    im2_xsize=size,
                                    im2_ysize=size,

                                    output_dir="./TEST_CASES/perftest_{0}_{1}".format(size, size)
                                    )

        try:
            mem_kb, runtime, n_matches = test_case.execute(output_textfile="OUTPUT.txt",
                                                performance_monitoring=True,
                                                verbose=True)
        except TypeError:
            # If a TypeError occurs here, it could be the execution failed and returned None.
            # In that case, just move along.
            continue

        stats_line = "{0},{1},{2},{3:d},{4:d},{5:d},{6:f},{7:d}\n".format("im1_scale_im2_scale",
                                                                    im1_gdal,
                                                                    im2_gdal,
                                                                    size,
                                                                    size,
                                                                    mem_kb,
                                                                    runtime,
                                                                    n_matches)

        # Append the line to the file.
        with open(output_csv_filename,'a') as csv_file:
            csv_file.write(stats_line)

for size in im_case_sizes:
    for i in range(10):
        # Run second with one im1 scaling up, im2 set to 3000x3000
        test_case = ASIFT_Executable(im1_gdal=im1_gdal,
                                    im1_xoff=im1_center_pixel[0] - (size/2),
                                    im1_yoff=im1_center_pixel[1] - (size/2),
                                    im1_xsize=size,
                                    im1_ysize=size,

                                    im2_gdal=im2_gdal,
                                    im2_xoff=im2_center_pixel[0] - (3000/2),
                                    im2_yoff=im2_center_pixel[1] - (3000/2),
                                    im2_xsize=3000,
                                    im2_ysize=3000,

                                    output_dir="./TEST_CASES/perftest_{0}_{1}".format(size, 3000)
                                    )

        try:
            mem_kb, runtime, n_matches = test_case.execute(output_textfile="OUTPUT.txt",
                                                performance_monitoring=True,
                                                verbose=True)

        except TypeError:
            # If a TypeError occurs here, it could be the execution failed and returned None.
            # In that case, just move along.
            continue

        stats_line = "{0},{1},{2},{3:d},{4:d},{5:d},{6:f},{7:d}\n".format("im1_scale_im2_fixed",
                                                                    im1_gdal,
                                                                    im2_gdal,
                                                                    size,
                                                                    3000,
                                                                    mem_kb,
                                                                    runtime,
                                                                    n_matches)
        # Append the line to the file.
        with open(output_csv_filename,'a') as csv_file:
            csv_file.write(stats_line)

for size in im_case_sizes:
    for i in range(10):
        # Run third with one im2 scaling up, im1 set to 3000x3000
        test_case = ASIFT_Executable(im1_gdal=im1_gdal,
                                    im1_xoff=im1_center_pixel[0] - (3000/2),
                                    im1_yoff=im1_center_pixel[1] - (3000/2),
                                    im1_xsize=3000,
                                    im1_ysize=3000,

                                    im2_gdal=im2_gdal,
                                    im2_xoff=im2_center_pixel[0] - (size/2),
                                    im2_yoff=im2_center_pixel[1] - (size/2),
                                    im2_xsize=size,
                                    im2_ysize=size,

                                    output_dir="./TEST_CASES/perftest_{0}_{1}".format(3000, size)
                                    )
        try:
            mem_kb, runtime, n_matches = test_case.execute(output_textfile="OUTPUT.txt",
                                                performance_monitoring=True,
                                                verbose=True)
        except TypeError:
            # If a TypeError occurs here, it could be the execution failed and returned None.
            # In that case, just move along.
            continue

        stats_line = "{0},{1},{2},{3:d},{4:d},{5:d},{6:f},{7:d}\n".format("im1_fixed_im2_scale",
                                                                    im1_gdal,
                                                                    im2_gdal,
                                                                    3000,
                                                                    size,
                                                                    mem_kb,
                                                                    runtime,
                                                                    n_matches)

        # Append the line to the file.
        with open(output_csv_filename,'a') as csv_file:
            csv_file.write(stats_line)

# Save our csv text to the file.
print output_csv_filename, "written."

