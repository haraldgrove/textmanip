#!/usr/bin/env python

# Copyright Harald Grove, CIGENE, 2012
# This is GNU GPL Software: http://www.gnu.org/

# Description:

import argparse
import gzip


def readUpdates(options):
    cNew, cOld, sep = options.colb, options.colc, options.sep
    cNew = int(cNew) - 1
    if sep == "t":
        sep = "\t"
    cOld = cOld.split(",")
    upd = {}
    with open(options.update, "r") as fin:
        for line in fin:
            if line.startswith("#"):
                continue
            l = line.strip().split("\t")
            try:
                newid = l[cNew]
            except IndexError:
                continue
            for ci in cOld:
                try:
                    alias = l[int(ci) - 1]
                except IndexError:
                    break
                al = alias.split(sep)
                for a in al:
                    upd[a] = newid
    if options.verbose:
        print("Read %d changes" % len(upd))
    return upd


def writeCorrected(options, upd):
    """ Changes all occurances of the targeted words """
    if options.infile[-3:] == ".gz":
        op = gzip.open
    else:
        op = open
    fin = op(options.infile, "r")
    fout = op(options.outfile, "w")
    for line in fin:
        first = True
        if line.startswith("#") and not options.comment:
            fout.write(line)
            continue
        l = line.strip().split()
        for ind, el in enumerate(l):
            if options.first and not first:
                continue
            if el in upd:
                l[ind] = upd[el]
                first = False
        else:
            fout.write("\t".join(l))
            fout.write("\n")
    fin.close()
    fout.close()


def main():
    parser = argparse.ArgumentParser(description="Replaces text in a file")
    parser.add_argument("infile", help="Input file")
    parser.add_argument("-o", dest="outfile", help="Output file")
    parser.add_argument("-u", dest="update", help="Update information")
    parser.add_argument(
        "-a",
        dest="comment",
        action="store_true",
        help="Replace in comment lines?",
        default=False,
    )
    parser.add_argument(
        "-b", dest="colb", help="Column in update file with new name", default="2"
    )
    parser.add_argument(
        "-c", dest="colc", help="Column(s) in input file with aliases", default="1"
    )
    parser.add_argument("-s", dest="sep", help="Separator for alias columns")
    parser.add_argument(
        "-g",
        dest="first",
        action="store_true",
        help="Only replace first occurence pr. line",
    )
    parser.add_argument(
        "-v",
        dest="verbose",
        action="store_true",
        help="Prints runtime info",
        default=False,
    )
    args = parser.parse_args()
    updict = readUpdates(args)
    writeCorrected(args, updict)


if __name__ == "__main__":
    # import time
    # t = time.time()
    main()
    # print("Time spent: %.3f" % ( time.time()-t ))
