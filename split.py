#!/usr/bin/env python3
"""
Split a text file into two by a given rule
"""

__author__ = "Harald Grove"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import time
import sys


def split_unique(args):
    """ Filter lines from input file into one of two output files """
    try:
        c = int(args.column) - 1
    except ValueError:
        sys.stderr.write("This option require a single column\n")
        sys.exit(1)
    db = {}
    with open(args.infile, "r") as fin:
        for line in fin:
            l = line.strip().split(args.delim)
            val = l[c]
            db[val] = db.get(val, 0) + 1
    temp = args.infile.rsplit(".", 1)
    outfile1 = "_unique.".join(temp)
    outfile2 = "_duplicate.".join(temp)
    with open(args.infile, "r") as fin, open(outfile1, "w") as fout1, open(
        outfile2, "w"
    ) as fout2:
        for line in fin:
            l = line.strip().split(args.delim)
            val = l[c]
            if db[val] > 1:
                fout2.write(line)
            else:
                fout1.write(line)


def split_highest(args):
    """ Given two columns, group by the first and select the highest from the second """
    try:
        c = [int(element) - 1 for element in args.column.split(",")]
    except ValueError:
        sys.stderr.write('ERROR: Columns should be numbers separated with ","\n')
        sys.exit(1)
    db = {}
    with open(args.infile, "r") as fin:
        for index, line in enumerate(fin):
            if line.startswith("#"):
                continue
            l = line.strip().split(args.delim)
            if len(l) == 0:
                continue
            group, val = l[c[0]], float(l[c[1]].strip("%"))
            if group not in db:
                db[group] = [val, index, line]
            elif db[group][0] < val:
                db[group] = [val, index, line]
    temp = args.infile.rsplit(".", 1)
    outfile1 = "_high.".join(temp)
    outfile2 = "_low.".join(temp)
    with open(args.infile, "r") as fin, open(outfile1, "w") as fout1, open(
        outfile2, "w"
    ) as fout2:
        for index, line in enumerate(fin):
            if line.startswith("#"):
                continue
            l = line.strip().split(args.delim)
            if len(l) == 0:
                continue
            group = l[c[0]]
            if db[group][1] == index:
                fout1.write(line)
            else:
                fout2.write(line)


def split_dist(args):
    """
    Splits the input file into a number of new files, each with a unique value for the given column
    :param args:
    :return:
    """
    try:
        c = int(args.column) - 1
    except ValueError:
        sys.stderr.write("This option require a single column\n")
        sys.exit(1)
    outfiles = {}
    temp = args.infile.rsplit(".", 1)
    outfile1 = "_unique.".join(temp)
    with open(args.infile, "r") as fin:
        for line in fin:
            l = line.strip().split(args.delim)
            val = l[c]
            if val not in outfiles:
                sep = ".{}.".format(val)
                outfiles[val] = open(sep.join(temp), "w")
            outfiles[val].write(line)
    for fout in outfiles.values():
        fout.close()


def split_limit(args):
    """
    Splits the file based on a given value in a given columns
    :param args:
    :return:
    """
    try:
        c = int(args.column) - 1
    except ValueError:
        sys.stderr.write("This option require a single column\n")
        sys.exit(1)
    temp = args.infile.rsplit(".", 1)
    outfile1 = "_above.".join(temp)
    outfile2 = "_below.".join(temp)
    with open(args.infile, "r") as fin, open(outfile1, "w") as fout1, open(
        outfile2, "w"
    ) as fout2:
        for index, line in enumerate(fin):
            if line.startswith("#"):
                continue
            l = line.strip().split(args.delim)
            if len(l) == 0:
                continue
            value = float(l[c])
            if value >= args.limit:
                fout1.write(line)
            else:
                fout2.write(line)


def split_bins(args):
    """
    Splits the file into a number given bins
    :param args:
    :return:
    """
    import math

    count = 0
    with open(args.infile, "r") as fin:
        for index, line in enumerate(fin):
            count += 1
    b = args.limit
    parts = math.floor(count / b)
    temp = args.infile.rsplit(".", 1)
    c = 0
    with open(args.infile, "r") as fin:
        for index, line in enumerate(fin):
            if (index) % parts == 0 and c < b:
                try:
                    fout.close()
                except:
                    pass
                fout = open("{}.part{}.{}".format(temp[0], c, temp[1]), "w")
                c += 1
            fout.write(line)
    fout.close()


def main(args):
    """ Main entry point of the app """
    if args.command == "unique":
        split_unique(args)
    elif args.command == "high":
        split_highest(args)
    elif args.command == "dist":
        split_dist(args)
    elif args.command == "limit":
        split_limit(args)
    elif args.command == "bins":
        if args.limit == 0:
            sys.stderr.write("This option requires --limit to also be set.\n")
            return
        split_bins(args)
    if args.log:
        with open("README.txt", "a") as fout:
            fout.write("[{}]\t[{}]\n".format(time.asctime(), " ".join(sys.argv)))


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("command", help="Command (unqiue/high/limit/bins)")
    parser.add_argument("infile", help="Input file")

    # Optional argument flag which defaults to False
    parser.add_argument("-f", "--flag", action="store_true", default=False)
    parser.add_argument(
        "-l",
        "--log",
        action="store_true",
        default=False,
        help="Save command to 'README.txt'",
    )

    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument("-c", "--column", help="Column(s) to evaluate", default="1")
    parser.add_argument("-d", "--delim", help="Delimiter", default="\t")
    parser.add_argument("-i", "--limit", type=float, help="Limit: Bins:", default=0)

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Verbosity (-v, -vv, etc)"
    )

    # Specify output of '--version'
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__),
    )

    args = parser.parse_args()
    main(args)
