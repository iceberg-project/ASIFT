# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 12:38:14 2018

@author: mmacferrin
"""

import os
import matplotlib.pyplot as plt
import numpy
import scipy.optimize as opt

results_filename = r"./TEST_CASES/perf_monitoring.csv"

results_file = open(results_filename, 'r')
results_lines = [line.strip() for line in results_file.readlines() if len(line.strip()) > 0]
results_file.close()

output_dir = r"./TEST_CASES/performance_outputs/"

header = dict([(n,i) for i,n in enumerate(results_lines[0].split(','))])

N = len(results_lines[1:])

experiment_types = numpy.zeros((N,),dtype=numpy.dtype('U19'))
im1_size_Mp = numpy.zeros((N,),dtype=numpy.float64)
im2_size_Mp = numpy.zeros((N,),dtype=numpy.float64)
max_memory_GB = numpy.zeros((N,),dtype=numpy.float64)
runtime_s = numpy.zeros((N,),dtype=numpy.float64)
num_matches = numpy.zeros((N,),dtype=numpy.uint32)

# ingest all the lines
for i,line in enumerate(results_lines[1:]):
    items = line.split(',')
    experiment_types[i] = items[header['experiment_type']]
    im1_size_Mp[i] = (float(items[header['size1_px']]) ** 2) / (10**6) # image is a square, NxN pixels
    im2_size_Mp[i] = (float(items[header['size2_px']]) ** 2) / (10**6) # image is a square, NxN pixels
    max_memory_GB[i] = float(items[header['max_mem_kb']]) / (2**20) # given in KB, convert to GB
    runtime_s[i] = float(items[header['runtime_s']])
    num_matches[i] = float(items[header['num_matches']])

# Get filters for each experiment type
ex1_mask = (experiment_types == 'im1_scale_im2_scale')
ex2_mask = (experiment_types == 'im1_scale_im2_fixed')
ex3_mask = (experiment_types == 'im1_fixed_im2_scale')

# Helper function for adding a polynomial curve.
def plot_curvefit(X,Y,ax,func,color=None,min_x=None,max_x=None,cutoff_zero_y=False):
    params, pcov = opt.curve_fit(func, X, Y)
    min_x_used = numpy.min(X) if (min_x is None) else min_x
    max_x_used = numpy.max(X) if (max_x is None) else max_x
    step = (max_x_used-min_x_used)/100.0
    x_curve = numpy.arange(min_x_used,
                           max_x_used + step,
                           step)

    y_curve = func(x_curve,*params)

    if cutoff_zero_y:
        x_curve = x_curve[y_curve >= 0]
        y_curve = y_curve[y_curve >= 0]

    if color is None:
        ax.plot(x_curve,y_curve)
    else:
        ax.plot(x_curve,y_curve,color=color)

    return params

def func_square(x,a,b,c):
    return a*(x**2) + b*x + c

def func_n_sqrt_n(x,a,b,c):
    return a*(x**0.5) + b*x + c

def func_sqrt_n_log_n(x,a):
    return a*(x**0.5)*numpy.log(x)

###############################################
## Plotting
###############################################
im, axes = plt.subplots(nrows=1, ncols=2, figsize=(10,4),dpi=150)

ex1_size = im1_size_Mp[ex1_mask] + im2_size_Mp[ex1_mask]
ex1_mem  = max_memory_GB[ex1_mask]
ex1_time = runtime_s[ex1_mask]

# The max memory seems to level off linearly AFTER gt 10 mpx. Let's reflect that.
#ex1_size_gt_8 = ex1_size[ex1_size >= 8.0]
#ex1_mem_gt_8 = ex1_mem[ex1_size >= 8.0]

ax1 = axes[0]
ax1.scatter(ex1_size,ex1_mem,s=4)
ax1.set_xlabel("Combined image size (Megapixels)")
ax1.set_ylabel("Max process memory (GB)")
plot_curvefit(ex1_size,ex1_mem,ax1,func_n_sqrt_n,color='darkred',min_x=0,cutoff_zero_y=True)
ax1.text(0.1,0.9,"Memory ~$O(n)$",horizontalalignment="left",verticalalignment="top",transform=ax1.transAxes)

# For a test, just plot the n^4 line using points up to 50 Mpx (same as last time), then see if it fits for 55 and 60 Mpx
#ex1_size_lte_50 = ex1_size[ex1_size <= 50.0]
#ex1_time_lte_50 = ex1_time[ex1_size <= 50.0]

ax2 = axes[1]
ax2.scatter(ex1_size,ex1_time,s=4)
ax2.set_xlabel("Combined image size (Megapixels)")
ax2.set_ylabel("Execution time (cpu-s)")
plot_curvefit(ex1_size,ex1_time,ax2,func_square,color='darkred',min_x=0)
ax2.text(0.1,0.9,"Time ~$O(n^2)$",horizontalalignment="left",verticalalignment="top",transform=ax2.transAxes)

figname = os.path.join(output_dir, "performance_plots_v2.png")

plt.tight_layout()
im.savefig(figname)
