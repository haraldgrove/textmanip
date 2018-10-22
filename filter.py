#!/usr/bin/env python

# filter.py, version 1.2
# Filter whitespace separated files on one column
# Copyright Harald Grove, CIGENE, 2013
# This is GNU GPL Software: http://www.gnu.org/
# Changelog:
# 2013-08-06: harag, changed input to accept filenames
# 2013-08-08: harag, added options for higher/lower filtering on numeric columns

import sys
import time
import os
import argparse
import gzip

def read_filters(filename, col):
    db = {}
    if os.path.isfile(filename):
        if filename[-3:] == ".gz":
            feq = gzip.open(filename, "r")
        else:
            feq = open(filename, "r")
        for line in feq:
            word = line.strip().split()
            try:
                db[word[col]] = 1
            except IndexError:
                continue
    else:
        db[filename] = 1
    return db

def filterFile(args):
    """ Removes lines not matching given criteria
    """
    # Reads in and records filtervalues
    if args.skip is not None:
        db = read_filters(args.skip, args.columnB-1)
    elif args.equal is not None:
        db = read_filters(args.equal, args.columnB-1)
    # Reads through target file and outputs according to template
    if args.infile is None:
        fin = sys.stdin
    else:
        fin = open(args.infile, "r")
    if args.outfile is None:
        fout = sys.stdout
    else:
        fout = open(args.outfile, "w")
    col = args.column - 1
    if args.unique:
        db = {}
    firstline = True
    for line in fin:
        if line.startswith("#"):
            fout.write(line)
            continue
        if firstline and args.header:
            fout.write(line)
            firstline = False
            continue
        l = line.strip().split(args.sep)
        if len(l) == 0:
            continue
        try:
            if args.equal:
                if l[col] in db:
                    fout.write(line)
            elif args.skip:
                if l[col] not in db:
                    fout.write(line)
            elif args.less:
                if float(l[col].strip("%")) < float(args.less):
                    fout.write(line)
            elif args.more:
                if float(l[col].strip("%")) > float(args.more):
                    fout.write(line)
            elif args.unique:
                if l[col] not in db:
                    fout.write(line)
                    db[l[col]] = 1
        except (IndexError, ValueError):
            fout.write(line)
            continue
    fin.close()
    if args.outfile:
        fout.close()


def main():
    parser = argparse.ArgumentParser(description="Keep or exclude lines.")
    parser.add_argument("-i", "--infile", help="input file")
    parser.add_argument("-o", "--outfile", help="output file")
    parser.add_argument("-c", "--column", help="Column to filter on", default=1)
    parser.add_argument("-b", "--columnB", help="Columen with filter values", default=1)
    parser.add_argument("-k", "--header", action="store_true", help="Keep header line")
    parser.add_argument("-u", "--unique", action="store_true", 
                        help="Remove lines with duplicated values in selected column")
    parser.add_argument("-e", "--equal", help="Keep lines matching this")
    parser.add_argument("-l", "--less", help="Keep lines with value less than this")
    parser.add_argument("-m", "--more", help="Keep lines with value more or equal to this")
    parser.add_argument("-s", "--skip", help="Skip lines matching this")
    parser.add_argument("-t", "--sep", help="Column separator")
    args = parser.parse_args()
    if args.equal or args.skip or args.less or args.more or args.unique:
        filterFile(args)
    else:
        print("No filtering argument, aborting...")


if __name__ == "__main__":
    # t = time.time()
    main()
    # print "Time spent: %.3f" % ( time.time()-t )
