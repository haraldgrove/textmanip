#!/usr/bin/env python

# summary.py

# from __future__ import division, print_function
import sys
import argparse
import time


def makeSummary(args):
    with open(args.infile, "r") as fin:
        lc = 0
        cc = {}
        firstline = None
        if args.separator == 'w':
            sep = None
        elif args.separator == 't':
            sep = '\t'
        else:
            sep = args.separator
        for index, line in enumerate(fin):
            # if args.comment and line.startswith(args.comment): continue
            l = line.strip().split(sep)
            if len(l) not in cc:
                cc[len(l)] = []
            cc[len(l)].append(index)
            if not firstline:
                firstline = l
                colInd = columnSelect(args.columns, len(l))
            if args.raw:
                if len(line) < 80:
                    sys.stdout.write(repr(line) + "\n")
                else:
                    sys.stdout.write(repr(line[0:40]))
                    sys.stdout.write("[...]")
                    sys.stdout.write(repr(line[len(line) - 40 :]))
                    sys.stdout.write("\n")
            elif args.info:
                try:
                    sys.stdout.write("%s\n" % "\t".join(l[e] for e in colInd))
                except IndexError:
                    sys.stdout.write("%s\n" % "\t".join(l))
            lc += 1
            if lc == args.lines and (args.raw or args.info):
                break
    if not (args.raw or args.info):
        sys.stdout.write("{} lines\n".format(lc))
        for key in cc:
            if len(cc[key]) < 10:
                seq = ','.join([str(i+1) for i in cc[key]])
            else:
                seq = ','.join([str(cc[key][i]+1) for i in range(0,5)]) + ' and {} more.'.format(len(cc[key]) - 5)
            sys.stdout.write("\t{}\t{}\n".format(key, seq))


def columnSelect(rawcol, l):
    temp = []
    c1 = rawcol.split(",")
    for e in c1:
        if "-" not in e:
            temp.append(int(e) - 1)
        else:
            e1 = e.split("-")
            try:
                a1 = int(e1[0])
            except ValueError:
                a1 = 1
            try:
                a2 = int(e1[1])
            except ValueError:
                a2 = l
            for f in range(a1, a2 + 1):
                temp.append(f - 1)
    return temp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile")
    parser.add_argument("-s", dest="separator", help="Columnseparator: (w)hitespace, (t)ab", default='t')
    parser.add_argument(
        "-r", dest="raw", action="store_true", help="Prints rawdata", default=False
    )
    parser.add_argument(
        "-l", dest="lines", type=int, help="Number of lines to print", default=10
    )
    parser.add_argument("-c", dest="columns", help="Columns to print", default="1-10")
    parser.add_argument(
        "-i",
        dest="info",
        action="store_true",
        help="Prints the first N lines&columns",
        default=False,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Prints runtime info",
        default=False,
    )
    args = parser.parse_args()
    makeSummary(args)


if __name__ == "__main__":
    # t = time.time()
    main()
    # sys.stdout.write('Time spent: %.3f\n' % (time.time()-t))
