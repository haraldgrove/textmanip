#!/usr/bin/python

# Author: Harald Grove
# Counts occurrences of each record in a given column

import sys
import time
import os
from optparse import OptionParser

def countFile(opt):
    """ Removes lines not matching given criteria
    """
    col = int(opt.column) - 1
    fin = open(opt.infile,'r')
    hist = {}
    for line in fin:
        if line.startswith('#'):
            continue
        l = line.strip().split('\t')
        hist[l[col]] = hist.get(l[col],0) + 1
    fin.close()
    fout = open(opt.outfile,'w')
    for key in hist:
        fout.write('%s\t%s\n' % (key,hist[key]))
    fout.close()

def main():
    usage = "usage: %prog  [options]"
    parser = OptionParser(usage)
    parser.add_option("-i",dest="infile",help="input file", metavar="FILE")
    parser.add_option("-o",dest="outfile",help="output file", metavar="FILE")
    parser.add_option("-c",dest="column",help="column selection", default=1)
    parser.add_option("-v",dest="verbose",action="store_true",help="Prints runtime info",default=False)
    parser.add_option("-G",dest="galaxy",action="store_true",help="Script is being run from galaxy",default=False)
    (options,args) = parser.parse_args()
    if options.galaxy:
        if options.infile == 'None': options.infile = None
        if options.outfile == 'None': options.outfile = None
    countFile(options)

if __name__ == "__main__":
    #t = time.time()
    main()
    #print "Time spent: %.3f" % ( time.time()-t )
