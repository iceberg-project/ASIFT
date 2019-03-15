# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 12:38:14 2018

@author: mmacferrin
"""

import os
import matplotlib.pyplot as plt
import numpy
import scipy.optimize as opt

#results_filename = r"./TEST_CASES/perf_monitoring_DONEv1.csv"
results_filename_2 = r"./TEST_CASES/perf_monitoring_SNAPSHOTv2.1.csv"

#for i,fname in enumerate([results_filename,results_filename_2]):
#    results_file = open(fname, 'r')
results_file = open(results_filename_2, 'r')
#if i==0:
results_lines = [line.strip() for line in results_file.readlines() if len(line.strip()) > 0]
#else:
#    results_lines = results_lines + [line.strip() for line in results_file.readlines() if len(line.strip()) > 0][1:]
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

def func_n(x,a,b):
    return a*x + b

def func_single_poly(x,a,b,c):
    return a * (x**b) + c

###############################################
## Plotting
###############################################

ex1_size_combined = im1_size_Mp[ex1_mask] + im2_size_Mp[ex1_mask]
ex1_size_mult = im1_size_Mp[ex1_mask] * im2_size_Mp[ex1_mask]
ex1_size_max = numpy.maximum(im1_size_Mp[ex1_mask], im2_size_Mp[ex1_mask])
ex1_mem  = max_memory_GB[ex1_mask]
ex1_time = runtime_s[ex1_mask] / 1000.
ex1_label = "img1 varies, img2 varies"

ex2_size_combined = im1_size_Mp[ex2_mask] + im2_size_Mp[ex2_mask]
ex2_size_mult = im1_size_Mp[ex2_mask] * im2_size_Mp[ex2_mask]
ex2_size_max = numpy.maximum(im1_size_Mp[ex2_mask], im2_size_Mp[ex2_mask])
ex2_mem  = max_memory_GB[ex2_mask]
ex2_time = runtime_s[ex2_mask] / 1000.
ex2_label = "img1 varies, img2 fixed"

ex3_size_combined = im1_size_Mp[ex3_mask] + im2_size_Mp[ex3_mask]
ex3_size_mult = im1_size_Mp[ex3_mask] * im2_size_Mp[ex3_mask]
ex3_size_max = numpy.maximum(im1_size_Mp[ex3_mask], im2_size_Mp[ex3_mask])
ex3_mem  = max_memory_GB[ex3_mask]
ex3_time = runtime_s[ex3_mask] / 1000.
ex3_label = "img1 fixed, img2 varies"

# The max memory seems to level off linearly AFTER gt 10 mpx. Let's reflect that.
#ex1_size_gt_8 = ex1_size[ex1_size >= 8.0]
#ex1_mem_gt_8 = ex1_mem[ex1_size >= 8.0]

im, axes = plt.subplots(nrows=1, ncols=2, figsize=(10,4),dpi=150)

ax1 = axes[0]
ax1.scatter(ex1_size_max,ex1_mem,s=4, label=ex1_label)
ax1.scatter(ex2_size_max,ex2_mem,s=4, label=ex2_label)
ax1.scatter(ex3_size_max,ex3_mem,s=4, label=ex3_label)
ax1.set_xlabel("Largest image size (Megapixels)")
ax1.set_ylabel("Max process memory (GB)")
params = plot_curvefit(ex1_size_max,ex1_mem,ax1,func_single_poly,color='darkred',min_x=0,cutoff_zero_y=False)
#plot_curvefit(ex1_size_max,ex1_mem,ax1,func_n_sqrt_n,color='darkred',min_x=0,cutoff_zero_y=True)
ax1.text(0.05,0.95,"Memory: ~$O(max(m,n)^{" + "{0:0.02f}".format(params[1]) +"})$",horizontalalignment="left",verticalalignment="top",transform=ax1.transAxes)
ax1.legend(fontsize="x-small",loc=(0.05,0.72),bbox_transform=ax1.transAxes)
ax1.text(0.80,0.08,"m = size(img1)\nn = size(img2)",horizontalalignment="left",verticalalignment="top",transform=ax1.transAxes, fontsize="x-small")

# For a test, just plot the n^4 line using points up to 50 Mpx (same as last time), then see if it fits for 55 and 60 Mpx
#ex1_size_lte_50 = ex1_size[ex1_size <= 50.0]
#ex1_time_lte_50 = ex1_time[ex1_size <= 50.0]

ax2 = axes[1]
ax2.scatter(ex1_size_mult**0.5,ex1_time,s=4, label=ex1_label)
ax2.scatter(ex2_size_mult**0.5,ex2_time,s=4, label=ex2_label)
ax2.scatter(ex3_size_mult**0.5,ex3_time,s=4, label=ex3_label)
ax2.set_xlabel(r"Geometric-mean Image Size (Megapixels)")
ax2.set_ylabel(r"Execution time ($\times 10^3$ cpu-s)")
plot_curvefit(ex1_size_mult**0.5,ex1_time,ax2,func_square,color='darkred',min_x=0)
ax2.text(0.05,0.95,r"Time: ~$O(m \times n)$",horizontalalignment="left",verticalalignment="top",transform=ax2.transAxes)
#ax2.legend(fontsize="x-small",loc=(0.05,0.78),bbox_transform=ax2.transAxes)

#ax2 = axes[1]
#ax2.scatter(ex1_size_combined,ex1_time,s=4, label=ex1_label)
#ax2.scatter(ex2_size_combined,ex2_time,s=4, label=ex2_label)
#ax2.scatter(ex3_size_combined,ex3_time,s=4, label=ex3_label)
#ax2.set_xlabel(r"Combined image size (Megapixels)")
#ax2.set_ylabel(r"Execution time ($\times 10^3$ cpu-s)")
#plot_curvefit(ex1_size_combined,ex1_time,ax2,func_square,color='darkred',min_x=0)
#ax2.text(0.05,0.95,"Time: ~$O((m+n)^2)$",horizontalalignment="left",verticalalignment="top",transform=ax2.transAxes)
##ax2.legend(fontsize="x-small",loc=(0.05,0.78),bbox_transform=ax2.transAxes)

plt.suptitle("ASIFT Image Scaling", fontsize="xx-large")

plt.tight_layout(rect=[0, 0, 1, 0.96])
figname = os.path.join(output_dir, "performance_plots_v2.png")

im.savefig(figname)
