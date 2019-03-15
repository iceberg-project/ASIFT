# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 11:51:24 2018

@author: mmacferrin

eprint() a quick utility function for printing to stderr instead of stdout.
"""

from __future__ import print_function
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
