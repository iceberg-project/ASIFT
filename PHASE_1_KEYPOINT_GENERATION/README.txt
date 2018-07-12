Before running test cases, the fast_imas_IPOL executable must be compiled and linked, including the OpenCV library.
Instructions to do this are in the ./fast_imas_IPOL/README.md file.


To run the test cases, use Python v2.7.0+, only standard libraries required.

> python run_test_cases.py


Right now, the test cases simply run on the "adam1.png" and "adam2.png" test images within the ./TEST_CASES/TEST_IMAGES directory.
Outputs are stored in separate folders within the ./TEST_CASES directory.


Three issues must be resolved to test this algorithm on geographic images.

1) Have a location (on "Bridges" or elsewhere) to store the images, several GB worth so far.

2) Delve into the fast_imas_IPOL code to figure out how to ingest TIF images rather than just PNG.
The workaround so far is to auto-convert all images to .PNG format, but this is not ideal.

3) Tweak the algorithm parameters to optimize for geographic satellite & airborne images. So far
the results are very "hit and miss", but can and will be improved shortly.