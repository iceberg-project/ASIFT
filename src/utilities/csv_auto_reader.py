# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 15:14:45 2018

CSV auto-reader: Reads in a simple comma-separated CSV file with a header line,
auto-detects the field types (string, int, or float) and returns the entire data set in that dtype.

@author: mmacferrin
"""

import numpy
import argparse
import pickle

def read_simple_csv(csv_file, picklefile=None, print_help=False, verbose=False, string_length_size=None):

    if print_help:
        print '''CSV_auto_reader::read_simple_csv(csv_file, print_help=False)
    Reads a simply-formatted, comma-separated CSV file with a single header line,
    custom-interprets the column data types and returns a numpy array with the contents.

    ASSUMPTIONS:
    1) All lines contain the same number of values, including the header line.
    2) All values are comma-separated. Quotation marks around values are not handled.
    3) Values are formatted as strings, integers, or floating-point values. 'NaN' or 'nan' strings are handled as floats.
    4) If any single value in a column cannot be converted to integers or floating-points, the column will default to strings.
    5) The first line is a header string with names of each column.
    6) All header strings are valid alphanumeric (or space or underscore '_') strings, unique from each other. Spaces on the

    If the above assumptions are violated, we cannot guarantee how the output will look, if it runs at all.

    The data-type of the output will be a custom numpy.dtype with named fields of
    type "numpy.str", "numpy.int" or "numpy.float".

    Arguments:
    csv_file CSV_FILE (required)      : the file path of the CSV file you want to read.
    picklefile PICKLE_FILE (optional) : Save the numpy array directly to a picklefile, if provided (default None)
    --print_help (optional)           : ignore the 'csv_file' parameter and just print this message
    --verbose (optional)              : Increase the verbosity'''
        return

    f = open(csv_file, 'r')
    lines = [line for line in f.readlines() if len(line.strip()) > 0]
    f.close()

    # The file must have at least two lines (a header and at least one row of values)
    # to parse here. Otherwise return None.
    if len(lines) <= 1:
        return None

    # Get the header line.
    header_keys = [item.strip() for item in lines[0].split(',')]
    header = dict([(name, i) for i,name in enumerate(header_keys)])
    lines = lines[1:]

    text_values_list = []
    # Each descriptor will have ['name', numpy.int], ['name', numpy.float], or ['name', numpy.str, LENGTH]

    # Read in all the items from all the lines.
    for line in lines:
        text_values_list.append([item.strip() for item in line.split(',')])

    str_len_list = [None] * len(header_keys)
    values_list = [None] * len(header_keys)

    # First, try to see if these are integers:
    for i in range(len(header_keys)):

        # Try to read in the row as integers first.
        try:
            values = numpy.array([numpy.int(text_row[i]) for text_row in text_values_list], dtype=numpy.int)
            values_list[i] = values
            continue
        except ValueError:
            pass

        # If integers don't work, try to read in the row as floating points
        try:
            values = numpy.array([numpy.float(text_row[i]) for text_row in text_values_list], dtype=numpy.float)
            values_list[i] = values
            continue
        except ValueError:
            pass

        # If floating points don't work, just default to reading in the row as strings.
        values = numpy.array([numpy.str(text_row[i]) for text_row in text_values_list], dtype=numpy.str)
        str_len_list[i] = numpy.max([val.dtype.itemsize for val in values])
        values_list[i] = values

    # Now, create the array of the datatype needed:
    dt_list = [None] * len(header_keys)

    for i in range(len(dt_list)):
        if str_len_list[i] != None:
            assert str_len_list[i] > 0
            dt_list[i] = (header_keys[i], numpy.str, str_len_list[i] if string_length_size is None else string_length_size)
        else:
            assert values_list[i].dtype in (numpy.int, numpy.float)
            dt_list[i] = (header_keys[i], values_list[i].dtype)

    # Create our datatype
    dt = numpy.dtype(dt_list)

    # Create an empty version of the final array
    final_array = numpy.empty([len(lines),], dtype=dt)

    # Fill in the values
    for key in header_keys:
        final_array[key] = values_list[header[key]]

    if picklefile != None:
        f = open(picklefile, 'wb')
        pickle.dump(final_array, f)
        f.close()

        if verbose:
            print picklefile, "created."

    # Return our custom array!
    return final_array


def define_and_parse_arguments():
    parser = argparse.ArgumentParser(description = "Read a simple CSV file (1 header line, consistent N columns, unique column names, no quoted fields, int/float/string values). Save the output to an optional python picklefile, if provided.")
    parser.add_argument('csv_file', type=str, help="Path to the CSV file to be read")
    parser.add_argument('picklefile',  type=str, default='', help="An optional picklefile, to save the output")
    parser.add_argument('--print_help', required=False, action='store_true', default=False, help="Print help message explaining usage (ignores other arguments)")
    parser.add_argument('--verbose', required=False, action='store_true', default=False, help="Increase output verbosity")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = define_and_parse_arguments()

    read_simple_csv(args.csv_file,
                    picklefile= (None if args.picklefile == '' else args.picklefile),
                    print_help=args.print_help,
                    verbose=args.verbose)