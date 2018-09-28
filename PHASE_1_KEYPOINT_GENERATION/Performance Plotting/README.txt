Performance Plotting --- testing the ASIFT executable on a couple of 
Worldview-1 images to test both Memory and CPU usage as the images scale.

These scripts are all using Python 2.7.9, should be platform-independent.

FILES:

* ASIFT_class_definitions.py:
	A Python class wrapper defining "ASIFT_Test_Case", for executing the 
	ASIFT compiled executable and compiling results.

	Pre-requisites:
		- A compiled version of the "fast_imas_IPOL" ASIFT executable. The relative 
		  location of this executable should be defined in the "ASIFT_EXEC" variable 
		  at the top of the code.
		- By default, it grabs images from the local relative directory
		  "./TEST_CASES/TEST_CASE_IMAGES". This directory should be created and
		  images put in there for ease of use. (This is arbitrary and can be changed
		  to use absolute paths if desired, a quick code fix.)
		- For performance plotting, the executable "/usr/bin/time" (typical on most 
		  Linux distros) must be present. The exact formatting of the output from 
		  /usr/bin/time might differ between distributions, so the regular-expression 
		  text searches toward the bottom of the "ASIFT_Test_Case::execute()" method
		  may need to be modified depending upon your distribution. This will only
		  matter if the "performance_monitoring" flag is set to "True" in the 
		  execute() method.
		  
* ASIFT_runtime_performance.py: 
	Uses the "ASIFT_Test_Case" class and runs the executable on two tiles from 
	different worldview images, using tiles of various sizes to compare performance 
	results. Runs 10 iterations of each combination, and spits the outputs to a 
	CSV textfile called "perf_monitoring.csv"
	
	Pre-requisites:
		- Open the "WorldView_URLs.txt" file, download the associated WorldView images
		  and put them in the "TEST_CASES/TEST_CASE_IMAGES/" directory.
		
* ASIFT_performance_plotting.py:
	Opens the "perf_monitoring.csv" file output from ASIFT_runtime_performance.py
	and plots the results in a PNG image, titled "performance_plots_v2.py".
	
	Pre-requisites:
		- The "TEST_CASES" directory should be present to output the results of
		  each run.


To run the performance tests, put the WorldView images in the
"TEST_CASES/TEST_CASE_IMAGES/" directory and run "python ASIFT_runtime_performance.py"

To plot the results from the last step, run "python ASIFT_performance_plotting.py"
		  
The input/output directories listed above ("TEST_CASES" and "TEST_CASES/TEST_CASE_IMAGES")
are defined in the code and can be modified easily if you choose.

The URLs for the two worldview images defined in "ASIFT_runtime_performance.py" are located in
the "WorldView_URLs.txt" file. Links to two images and their associated XML metadata files 
are in that textfile.