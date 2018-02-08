#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "Harald Grove"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import time
import sys
import random


def match(m, l):
    for m1 in m:
        if m1 not in l:
            return False
    return True

def extractlines(args):
    db = []
    with open(args.equal, 'r') as fin:
        for line in fin:
            l = line.strip().split()
            db.append(l)
    with open(args.infile, 'r') as fin, open(args.outfile, 'w') as fout:
        if args.header:
            fout.write(next(fin))
        for line in fin:
            l = line.strip().split()
            for el in db:
                if match(el,l):
                    #print(el,l)
                    fout.write(line)
                    break

def filterlines(args):
    db = []
    with open(args.skip, 'r') as fin:
        for line in fin:
            l = line.strip().split()
            db.append(l)
    with open(args.infile, 'r') as fin, open(args.outfile, 'w') as fout:
        if args.header:
            fout.write(next(fin))
        for line in fin:
            l = line.strip().split()
            try:
                if int(l[0][3:]) < 15:
                    continue
            except ValueError:
                pass
            for el in db:
                if match(el,l):
                    break
            else:
                fout.write(line)

def randselect(args):
    db = []
    with open(args.infile, 'r') as fin, open(args.outfile, 'w') as fout:
        if args.header:
            fout.write(next(fin))
        for line in fin:
            if random.random() < args.rand:
                fout.write(line)

def main(args):
    """ Main entry point of the app """
    if args.equal is not None:
        extractlines(args)
    elif args.skip is not None:
        filterlines(args)
    elif args.rand is not None:
        randselect(args)
    if args.log:
        with open('README.txt', 'a') as fout:
            fout.write('[{}]\t[{}]\n'.format(time.asctime(), ' '.join(sys.argv)))


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("infile", help="Input file")

    # Optional argument flag which defaults to False
    parser.add_argument('-l', '--log', action="store_true", default=False, help="Save command to 'README.txt'")
    parser.add_argument('-k', '--header', action="store_true", default=False, help="Preserve first line as header")

    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument("-e", "--equal", help="Values to keep")
    parser.add_argument("-f", "--skip", help="Values to filter")
    parser.add_argument("-o", "--outfile", help="Outfile")
    parser.add_argument("-r", "--rand", type=float, help="Proportion of lines to randomly keep [0 - 1]")

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help="Verbosity (-v, -vv, etc)")

    # Specify output of '--version'
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s (version {version})'.format(version=__version__))

    args = parser.parse_args()
    main(args)
