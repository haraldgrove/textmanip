#!/usr/bin/env python

# mycat.py, version 1.0
# A [] in the input file name can be used to indicate a numeric 
# Copyright Harald Grove, CIGENE, 2015
# This is GNU GPL Software: http://www.gnu.org/
# Changelog:

import sys
import time
import os
import argparse

def makeIndex(opt):
    if opt.chroms:
        chrom = []
        c = opt.chroms.split(',')
        for e in c:
            try:
                chrom.append(int(e))
            except:
                e1 = e.split('-')
                for i in xrange(int(e1[0]),int(e1[1])+1):
                    chrom.append(i)
    else: chrom = ''
    return chrom

def catBeagle(opt):
    if not opt.outfile:
        fout = sys.stdout
    else:
        fout = open(opt.outfile,'w')
    first = True
    for i in chrom:
        print(opt.infile)
        infile = opt.infile.replace('[]',str(i))
        print(infile)
        with open(infile,'r') as fin:
            for line in fin:
                l = line.strip().split()
                if l[0]== 'M' or first:
                    fout.write(line)
                    continue
        first = False

def catGenabel(opt):
    if not opt.outfile:
        fout = sys.stdout
    else:
        fout = open(opt.outfile,'w')
    firstLine = True
    infile = []
    for i in chrom:
        infile.append(open(opt.infile.replace('[]',str(i))))
    while 1:
        for i,fin in enumerate(infile):
            try: line = fin.next()
            except StopIteration: return
            l = line.strip().split()
            # i == 0 means first file, i.e. the one that will keep all information columns
            # firstLine is the first line for each file
            if i == 0 and firstLine: fout.write('%s' % ('\t'.join(l)))
            elif i == 0: fout.write('%s' % ('\t'.join(l)))
            elif firstLine: fout.write('\t%s' % ('\t'.join(l[3:])))
            else: fout.write('\t%s' % ('\t'.join(l[3:])))
        fout.write('\n')
        firstLine = False

def catGeno(opt):
    if not opt.outfile: fout = sys.stdout
    else: fout = open(opt.outfile,'w')
    firstLine = True
    infile = []
    for name in opt.infile:
        infile.append(open(name,'r'))
    while 1:
        for i, fin in enumerate(infile):
            try: line = fin.next()
            except StopIteration: return
            l = line.strip('#').strip().split()
            if i == 0 and firstLine: fout.write('#\t%s' % ('\t'.join(l)))
            elif i == 0: fout.write('%s' % ('\t'.join(l)))
            elif firstLine: fout.write('\t%s' % ('\t'.join(l)))
            else: fout.write('\t%s' % ('\t'.join(l[3:])))
        fout.write('\n')
        firstLine = False

def catFimpute(opt):
    if not opt.outfile: fout = sys.stdout
    else: fout = open(opt.outfile,'w')
    firstLine = True
    infile = []
    for i in chrom:
        infile.append(open(opt.infile.replace('[]',str(i))))
    while 1:
        for i, fin in enumerate(infile):
            try: line = fin.next()
            except StopIteration: return
            l = line.strip().split()
            if i == 0 and firstLine: fout.write('%s' % ('\t'.join(l)))
            elif i == 0: fout.write('%s' % ('\t'.join(l)))
            elif firstLine: continue
            else: fout.write('%s' % (l[2]))
        fout.write('\n')
        firstLine = False

def catPlink(opt):
    if not opt.outfile: fout = sys.stdout
    else: fout = open(opt.outfile,'w')
    infile = []
    for i in chrom:
        infile.append(open(opt.infile.replace('[]',str(i))))
    while 1:
        for i, fin in enumerate(infile):
            try: line = fin.next()
            except StopIteration: return
            if line.startswith('#'): continue
            l = line.strip().split()
            if i == 0: fout.write('%s' % ('\t'.join(l)))
            else: fout.write('\t%s' % ('\t'.join(l[6:])))
        fout.write('\n')

def main():
    parser = argparse.ArgumentParser(description='Concatenates text-files in horisontal direction.')
    parser.add_argument("infile",nargs='*',help="input file(s)")
    parser.add_argument("-o",dest="outfile",help="output file")
    parser.add_argument("-n",dest="informat",help="File type",required=True)
    parser.add_argument('-v','--verbose',action="store_true",help='Prints runtime info')
    args = parser.parse_args()
    if not args.informat:
        parser.error('Missing input file format')
    if args.informat == 'Beagle': catBeagle(args)
    elif args.informat == 'Geno': catGeno(args)
    elif args.informat == 'Plink': catPlink(args)
    elif args.informat == 'Fimpute': catFimpute(args)
    elif args.informat == 'Genabel': catGenabel(args)
    else: sys.stderr.write('Uknown input format: [%s]\n' % (args.informat))

if __name__ == "__main__":
    #t = time.time()
    main()
    #print "Time spent: %.3f" % ( time.time()-t )
