#!/usr/bin/env python

# join.py, version 1.2
# Join two tab files by matching columns
# Copyright Harald Grove, 2017
# This is GNU GPL Software: http://www.gnu.org/

import sys
import argparse


def joinfiles(opt):
    """
    Matches lines and writes output
    """
    with open(opt.infile2, "r") as fin2:
        f2 = fin2.readlines()
    db = {}
    for ind, line in enumerate(f2):
        l = line.strip().split()
        db[l[opt.column2 - 1]] = ind
    if opt.outfile is not None:
        fout = open(opt.outfile, "w")
    else:
        fout = sys.stdout
    with open(opt.infile1, "r") as fin1:
        for line in fin1:
            l = line.strip().split()
            try:
                if l[opt.column1 - 1] in db:
                    fout.write(
                        "{}\t{}\n".format(
                            line.strip(), f2[db[l[opt.column1 - 1]]].strip()
                        )
                    )
                else:
                    fout.write("{}\n".format(line.strip()))
            except IndexError:
                continue
    if opt.outfile is not None:
        fout.close()


def main(args):
    joinfiles(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Join files.")
    parser.add_argument("infile1", help="first input file")
    parser.add_argument("infile2", help="second input file")
    parser.add_argument("-o", dest="outfile", help="output file")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Prints runtime info"
    )
    parser.add_argument(
        "-c", dest="column1", type=int, help="Column in first file ", default=1
    )
    parser.add_argument(
        "-b", dest="column2", type=int, help="Column in second file", default=1
    )
    parser.add_argument(
        "-k",
        dest="keep",
        action="store_true",
        help="Keep non-matching lines from first file",
    )
    parser.add_argument(
        "-t", dest="sep", action="store_true", help="Tab separated columns"
    )
    args = parser.parse_args()
    main(args)
