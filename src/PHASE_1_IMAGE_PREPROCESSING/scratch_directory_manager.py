# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 11:55:15 2018

Scratch_Directory_Manager.py -add fname -remove fname -lookup fname --remove_all --verbose

@author: mmacferrin
"""

#######################################################################################
## Code for importing the parent directory in order to get the File_Locations object
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
## Also add the utility folder for the csv names
utilitydir = os.path.join(parentdir, "UTILITIES")
sys.path.insert(0,utilitydir)
#######################################################################################

from File_Locations import ASIFT_Scratch_Dir, ASIFT_Scratch_Logfile
from CSV_auto_reader import read_simple_csv
from CSV_writer import write_csv

import hashlib
import os
import shutil
import numpy
import argparse

class SCRATCH_Manager:

    def __init__(self, scratch_dir=ASIFT_Scratch_Dir, scratch_logfile=ASIFT_Scratch_Logfile):
        self.scratch_dir = scratch_dir
        self.logfile = scratch_logfile
        self.logfile_data = None
        self.logfile_numpy_dt = None
        return

    def hash_filename(self, fname, remove_path=True):
        '''Take a filename, generate a hash string. Right now using the md5 algorithm.
        For this purpose we are not worried about security vulnerabilities of md5,
        it works to create unique strings for our purposes.

        If 'remove_path' set, it will get only the file name, not the entire path to the file if it's included.

        Returns a 32-character hexadecimal string hash value, with the first four letters of filename and an underscore pre-pended.'''
        if remove_path:
            fname = os.path.split(fname)[-1]

        m = hashlib.md5()
        m.update(fname)
        hashstr = m.hexdigest()

        fname_base = os.path.splitext(fname)[0]
        hash_name = (fname_base[0:4] if len(fname_base) >= 4 else fname_base) + '_' + hashstr
        return hash_name

    def read_logfile(self):
        '''Read the logfile and return a numpy data array from 'read_simple_csv'''
        # We artificially make the string length longer in the numpy data type,
        # so we don't accidentally concatenate long filenames added to the database.
        # Max filename size here, 2048 characters.
        self.logfile_data = read_simple_csv(self.logfile, string_length_size=2048)
        self.logfile_numpy_dt = self.logfile_data.dtype
        return self.logfile_data

    def lookup(self, fname):
        '''Simply look up a file name in the logfile and return its full scratch directory path. If it doesn't yet exist, return None.'''
        if self.logfile_data is None:
            self.read_logfile()

        # Get just the file name, not the whole path.
        fname = os.path.split(fname)[-1]

        fname_indices_mask = self.logfile_data['image_name'] == fname
        if numpy.any(fname_indices_mask):
            # If the directory already exists, remove it if we want to overwrite it.
            return self.logfile_data[fname_indices_mask]['md5_hashdir'][0]
        else:
            # If it's not in our logfile, return None
            return None

    def add_directory(self, fname, overwrite=False, verbose=False):
        '''Add a scratch directory for processing the file if it doesn't already exist.
        Also adds an entry into the logfile.
        If overwrite is True and the directory already exists, it will clear it and create an empty directory in its place.'''
        if self.logfile_data is None:
            self.read_logfile()

        # Get just the file name, not the whole path.
        fname = os.path.split(fname)[-1]

        fname_indices_mask = self.logfile_data['image_name'] == fname
        if numpy.any(fname_indices_mask):
            # If the directory already exists, remove it if we want to overwrite it.
            if overwrite:
                self.remove_directory(fname, verbose=verbose)

            # If we don't want to overwrite it, check that the directory exists on disk (create it if it doesn't), and return it.
            else:
                hashdir = self.logfile_data[fname_indices_mask]['md5_hashdir'][0]
                hash_path = os.path.join(self.scratch_dir, hashdir)
                if not os.path.exists(hash_path):
                    os.mkdir(hash_path)

                return hash_path

        # Add it to the logfile.
        hashdir = self.hash_filename(fname)

        new_data = numpy.empty((1,), dtype=self.logfile_numpy_dt)
        new_data[0]['image_name'] = fname
        new_data[0]['md5_hashdir'] = hashdir

        self.logfile_data = numpy.append(self.logfile_data, new_data)
        write_csv(self.logfile_data, self.logfile, verbose=verbose)

        hash_path = os.path.join(self.scratch_dir, hashdir)

        if os.path.exists(hash_path):
            if overwrite:
                shutil.rmtree(hash_path)
                os.mkdir(hash_path)
        else:
            os.mkdir(hash_path)

        return hash_path


    def remove_directory(self, fname, warn_if_not_present=False, verbose=False):
        '''Removes a directory if it's present in the scratch folder. Also removes the
        entry from the logfile.'''
        if self.logfile_data is None:
            self.read_logfile()

        # Get just the file name, not the whole path.
        fname = os.path.split(fname)[-1]

        fname_indices_mask = self.logfile_data['image_name'] == fname

        if not numpy.any(fname_indices_mask):
            if warn_if_not_present:
                raise Warning("SCRATCH_Manager::remove_directory() -- directory entry for file '{0}' not present in logfile.".format(fname))
            return

        # There shouldn't be more then one entry for any given filename, that's
        # the whole point of the hash. But if there is, go ahead and delete them all.
        for hashdir in self.logfile_data['md5_hashdir'][fname_indices_mask]:
            hashdir_path = os.path.join(self.scratch_dir, hashdir)
            if os.path.exists(hashdir_path):
                shutil.rmtree(hashdir_path)
                if verbose:
                    print "Scratch directory {0} removed.".format(hashdir)
            else:
                if warn_if_not_present:
                    raise Warning("SCRATCH_Manager::remove_directory() -- directory name '{0}' not present to remove.".format(hashdir))

        # Set the logfile data to all the entries *except* the ones we just removed.
        self.logfile_data = self.logfile_data[~fname_indices_mask]
        # Overwrite the logfile.
        write_csv(self.logfile_data, self.logfile, verbose=verbose)

        return

    def remove_all_directories(self, verbose=False):
        '''Basically run down all directories and clear the logfile. Replace the
        logfile with a blank one with only a "blank sample" entry, which helps the read_simple_csv() function later.'''
        if self.logfile_data is None:
            self.read_logfile()

        # For each directory present in the working scratch directory, remove it.
        # Note: this ONLY removes directories that are stored in the logfile, not manually-added directories.
        for hashdir in self.logfile_data['md5_hashdir']:
            hashdir_path = os.path.join(self.scratch_dir, hashdir)
            if os.path.exists(hashdir_path):
                shutil.rmtree(hashdir_path)
                if verbose:
                    print "Scratch directory {0} removed.".format(hashdir)

        new_data = numpy.empty((1,), dtype=self.logfile_numpy_dt)
        new_data[0]['image_name'] = 'blank_sample'
        new_data[0]['md5_hashdir'] = self.hash_filename('blank_sample')
        self.logfile_data = new_data

        write_csv(self.logfile_data, self.logfile, verbose=verbose)



def define_and_parse_arguments():
    parser = argparse.ArgumentParser(description = "Add, remove, or look up the temporary working directory, which stores intermediate results for a given image file.")
    parser.add_argument('-add',  type=str, default='', required=False, help="A filename. Adds a directory to store tiles and/or temporary results for the given file.")
    parser.add_argument('-remove', type=str, default='', required=False, help="An image filename. Remove a directory for the given filename, typically after processing is done.")
    parser.add_argument('-lookup', type=str, default='', required=False, help="Look up the directory for the given filename and print it to the screen.")
    parser.add_argument('--remove_all', required=False, action='store_true', default=False, help="Clean up the scratch directory and remove all files & subfolders.")
    parser.add_argument('--verbose', required=False, action='store_true', default=False, help="Increase the output verbosity")

    return parser.parse_args()

if __name__ == "__main__":
    args = define_and_parse_arguments()
    # Given two images, create CSV files that desribe the tiles in each image,
    # as well as the matchings between both sets of image tiles to run ASIFT upon.


    if args.remove == '' and args.add == '' and args.lookup == '' and args.remove_all == False:
        ## No actions were selected. Just print usage and return.
        args.print_help()

    else:
        m = SCRATCH_Manager()

        # Technically you can do more than one action in a single run, although
        # it'd be a little convoluted. For instance you can "remove_all" previous
        # temp folders and "add" another with a new file. Actions will be executed in the order listed here.
        if args.remove != '':
            m.remove_directory(args.remove, verbose=args.verbose)

        if args.remove_all:
            m.remove_all_directories(verbose=args.verbose)

        if args.add != '':
            dirpath = m.add_directory(args.add, verbose=args.verbose)
            if args.verbose:
                print dirpath

        if args.lookup != '':
            dirname = m.lookup(args.lookup)
            if dirname != None:
                print dirname
