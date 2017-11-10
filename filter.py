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

def filterFile(opt):
    """ Removes lines not matching given criteria
    """
    equal,skip = {},{}
    col = int(opt.column) - 1
    if opt.columnB:
        colB = int(opt.columnB) - 1
    else:
        colB = None
    if opt.infile[-3:] == '.gz':
        fin = gzip.open(opt.infile,'r')
    else:
        fin = open(opt.infile,'r')
    # Reads in and records filtervalues
    if opt.equal and os.path.isfile(opt.equal):
        if opt.equal[-3:] == '.gz':
            feq = gzip.open(opt.equal,'r')
        else:
            feq = open(opt.equal,'r')
        for line in feq:
            try:
                if opt.columnB: equal[line.strip().split()[colB]] = 1
                else: equal[line.strip()] = 1
            except IndexError:
                continue
    else:
        equal[opt.equal] = 1
    if opt.skip and os.path.isfile(opt.skip):
        for line in open(opt.skip,'r'):
            try:
                if opt.columnB:
                    skip[line.strip().split()[colB]] = 1
                else:
                    skip[line.strip()] = 1
            except IndexError:
                continue
    else:
        skip[opt.skip] = 1
    if opt.verbose:
        sys.stderr.write('Read %d filter criteria\n' % (len(equal)+len(skip)))
        for i,n in enumerate(equal):
            sys.stderr.write('%d, %s\n' % (i,n))
            if i > 5:
                break
    # Reads through target file and outputs according to template
    if not opt.outfile:
        fout = sys.stdout
    else:
        fout = open(opt.outfile,'w')
    if opt.unique:
        seen = {}
    firstline = True
    for line in fin:
        if line.startswith('#'):
            fout.write(line)
            continue
        if firstline and opt.header:
            fout.write(line)
            firstline = False
            continue
        if opt.tab:
            l = line.strip().split('\t')
        else: l = line.strip().split()
        if len(l) == 0:
            continue
        #print opt.equal,opt.skip,l[col]
        try:
            if opt.equal:
                if l[col] in equal:
                    fout.write(line)
            elif opt.skip:
                if l[col] not in skip:
                    fout.write(line)
            elif opt.less:
                if float(l[col].strip('%')) < float(opt.less):
                    fout.write(line)
            elif opt.more:
                if float(l[col].strip('%')) > float(opt.more):
                    fout.write(line)
            elif opt.unique:
                if l[col] not in seen:
                    fout.write(line)
                    seen[l[col]] = 1
        except (IndexError,ValueError):
            fout.write(line)
            continue
    fin.close()
    if opt.outfile:
        fout.close()

def main():
    parser = argparse.ArgumentParser(description='Processes genotypes.')
    parser.add_argument("infile",help="input file")
    parser.add_argument("-o",dest="outfile",help="output file")
    parser.add_argument('-v','--verbose',action="store_true",help='Prints runtime info')
    parser.add_argument("-c",dest="column",help="Column to filter on", default=1)
    parser.add_argument("-b",dest="columnB",help="Columen with filter values")
    parser.add_argument("-k",dest="header",action="store_true",help="Keep header line")
    parser.add_argument("-u",dest="unique",action="store_true",help="Remove lines with duplicated values in selected column")
    parser.add_argument("-e", dest="equal",help="Keep lines matching this")
    parser.add_argument("-l", dest="less",help="Keep lines with values less than this")
    parser.add_argument("-m", dest="more",help="Keep lines with value more than this")
    parser.add_argument("-s",dest="skip",help="Skip lines matching this")
    parser.add_argument("-t",dest="tab",action="store_true",help="Tab separated columns")
    args = parser.parse_args()
    if args.equal or args.skip or args.less or args.more or args.unique:
        filterFile(args)
    else:
        print("No filtering argument, aborting...")

if __name__ == "__main__":
    #t = time.time()
    main()
    #print "Time spent: %.3f" % ( time.time()-t )
