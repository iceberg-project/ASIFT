# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 17:04:32 2018

CSV_auto_writer.py: Takes a header and a list of numpy arrays, and writes out a simple CSV file.

@author: mmacferrin
"""
import numpy

def write_csv(data, csvname, header=None, verbose=False, print_help=False):
    help_msg = '''Takes data arrays and spits out a CSV file.

    data: the data, either as a numpy array of custom (named) "dtype" columned data, or a simple list of numpy ndarrays (in this case, use the "header" keyword for the names)
    csvname: the name of the CSV file to output
    header (optional): If the data is simply a list if ndarrays, this is an equal-length list of column names for the header.
    verbose (optional): Print an output message when the CSV is written.
    '''

    if print_help:
        print help_msg

    if header != None:
        header_line = ",".join(header) + "\n"
        # Check to see whether the arrays are all of equal length.
        assert numpy.count_nonzero([ len(row)-len(data[0]) for row in data ]) == 0
        data_lines = ''
        # Iterate over all the rows
        for i in range(len(data[0])):
            # Gather the values from all the columns
            row = ",".join([str(col[i]) for col in data]) + "\n"
            data_lines = data_lines + row

    else:
        colnames = data.dtype.names
        header_line = ",".join(colnames) + "\n"

        data_lines = ''
        for i in range(len(data)):
            row = ",".join([str(data[i][name]) for name in colnames]) + "\n"
            data_lines = data_lines + row

    f = open(csvname, 'w')
    f.write(header_line + data_lines)
    f.close()
    if verbose:
        print csvname, "written."

    return