#!/usr/bin/env python

# Author: Harald Grove
# Counts occurrences of each record in a given set of columns

import sys
import argparse

def countFile(opt):
    """
    Count number of occurrences
    """
    if ',' in opt.column:
        cols = [int(c)-1 for c in opt.column.split(',')]
    else:
        cols = [int(opt.column) - 1]
    with open(opt.infile,'r') as fin:
        hist = {}
        for line in fin:
            if line.startswith('#'):
                continue
            line_l = line.strip().split('\t')
            record = []
            for c in cols:
                record.append(line_l[c])
            record = tuple(record)
            hist[record] = hist.get(record,0) + 1
    if opt.outfile is not None:
        fout = open(opt.outfile,'w')
    else:
        fout = sys.stdout
    for key, value in hist.items():
        k = '\t'.join(key)
        fout.write('{}\t{}\n'.format(k,value))
    fout.close()

def main():
    parser = argparse.ArgumentParser(description='Counts occurrences')
    parser.add_argument("infile",help="input file")
    parser.add_argument("-o",dest="outfile",help="output file")
    parser.add_argument("-c",dest="column",help="column selection", default='1')
    parser.add_argument("-v",dest="verbose",action="store_true",help="Prints runtime info",default=False)
    args = parser.parse_args()
    countFile(args)

if __name__ == "__main__":
    main()
