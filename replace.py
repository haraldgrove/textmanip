#!/usr/bin/env python

# Copyright Harald Grove, CIGENE, 2012
# This is GNU GPL Software: http://www.gnu.org/

# Description:

import sys
import time
from optparse import OptionParser

def readUpdates(options):
    cNew,cOld,sep = options.colb,options.colc,options.sep
    cNew = int(cNew)-1
    if sep == 't': sep = '\t'
    cOld = cOld.split(',')
    upd = {}
    with open(options.update,'r') as fin:
        for line in fin:
            if line.startswith('#'): continue
            l = line.strip().split('\t')
            try: newid = l[cNew]
            except IndexError: continue
            for ci in cOld:
                try: alias = l[int(ci)-1]
                except IndexError: break
                al = alias.split(sep)
                for a in al:
                    upd[a] = newid
    if options.verbose: print "Read %d changes" % len(upd)
    return upd

def writeCorrected(options,upd):
    """ Changes all occurances of the targeted words """
    fin = open(options.infile,'r')
    fout = open(options.outfile,'w')
    for line in fin:
        first = True
        if line.startswith('#') and not options.comment:
            fout.write(line)
            continue
        l = line.strip().split()
        for ind,el in enumerate(l):
            if options.first and not first: continue
            if el in upd:
                #print "%s\t%s" % (l[ind],upd[el])
                l[ind] = upd[el]
                #if upd[el] != 'DELETE': l[ind] = upd[el]
                #else: break
                first = False
        else:
            fout.write('\t'.join(l))
            fout.write('\n')
    fin.close()
    fout.close()

def main():
    usage = "usage: %prog [options]\n"
    parser = OptionParser(usage)
    parser.add_option("-i",dest="infile",help="Input file", metavar="FILE")
    parser.add_option("-o",dest="outfile",help="Output file", metavar="FILE")
    parser.add_option("-j",dest="infile2",help="Target markers", metavar="FILE")
    parser.add_option("-u",dest="update",help="Update information", metavar="FILE")
    parser.add_option("-a",dest="comment",action="store_true",help="Replace in comment lines?",default=False)
    parser.add_option("-b",dest="colb",help="Column in update file with new name", default='2')
    parser.add_option("-c",dest="colc",help="Column(s) in input file with aliases", default='1')
    parser.add_option("-s",dest="sep",help="Separator for alias columns")
    parser.add_option("-g",dest="first",action="store_true",help="Only replace first occurence pr. line")

    parser.add_option("-v",dest="verbose",action="store_true",help="Prints runtime info",default=False)
    parser.add_option("-G",dest="galaxy",action="store_true",help="Script is being run from galaxy",default=False)
    (options,args) = parser.parse_args()
    if options.galaxy:
        if options.infile2 == 'None': options.infile2 = None
        if options.sep == 'None': options.sep = None
    if not options.infile:
        sys.stderr.write('Missing inputfile\n')
        sys.exit(1)
    updict = readUpdates(options)
    writeCorrected(options,updict)

if __name__ == "__main__":
    #t = time.time()
    main()
    #print "Time spent: %.3f" % ( time.time()-t )
