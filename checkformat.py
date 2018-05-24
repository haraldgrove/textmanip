#!/usr/bin/env python

# checkformat v1.0
# Checks if there is any problems with various file formats

import sys
from optparse import OptionParser
import gzip


def checkGeno(inputfile, reportfile, verbose=False):
    if inputfile[-3:] == ".gz":
        fin = gzip.open(inputfile, "r")
    else:
        fin = open(inputfile, "r")
    fout = open(reportfile, "w")
    firstline = True
    pedcols = True  # If the file contains two columns with father and mother
    markers = None
    irow = 0  # Which row being checked
    samples = 0
    alldist = []  # What alleles are being used
    sampledict = {}
    markerallele = {}
    for line in fin:
        irow += 1
        if firstline and line.startswith("#"):
            firstline = False
            if "\r\n" in line:
                fout.write("INFO: File has windows-formating\n")
            l = line.strip("#").strip().split()
            markers = len(l)
            if markers > 0:
                fout.write("INFO: %d markers\n" % markers)
                markerdict = {}
                countmark = 0
                for el in l:
                    if el not in markerdict:
                        markerdict[el] = 1
                    else:
                        fout.write("WARNING: Duplicate entries for marker %s\n" % (el))
                markers *= 2
            else:
                fout.write("WARNING: Marker row, but no markers listed\n")
                markers = None
        elif line.startswith("#"):
            fout.write("INFO: line %d, comment line\n" % (irow))
            continue
        else:
            if firstline:
                fout.write("WARNING: Missing marker line\n")
                firstline = False
            l = line.strip().split()
            if len(l) < 3:
                fout.write(
                    "ERROR, line %d: Too few columns (%d)\nAborting...\n"
                    % (irow, len(l))
                )
                fin.close()
                fout.close()
                sys.exit(0)
            samples += 1
            if not markers:
                markers = len(l[3:])
                fout.write("INFO: %d markers\n" % markers)
            elif (
                len(l[1:]) == markers and pedcols
            ):  # If pedcolumns are assumed, but not present, confounded with missing 2 allele columns
                fout.write("INFO: No pedigree information\n")
                pedcols = False
            elif len(l[3:]) != markers or (
                not pedcols and len(l[1:]) != markers
            ):  # if allelecols don't match markers, with or without pedcols
                fout.write(
                    "ERROR, line %d: Too many/few alleles (%d/%d)\n"
                    % (irow, len(l[3:]), markers)
                )
                continue
            alleles = list(set(l[3:]))
            alldist += alleles
            for i in xrange(0, markers / 2):
                markerallele[i] = (
                    markerallele.get(i, "") + l[3 + i * 2] + l[3 + i * 2 + 1]
                )
            if l[0] not in sampledict:
                sampledict[l[0]] = l[1], l[2]
            else:
                fout.write("WARNING: Multiple entries for sample %s\n" % (l[0]))
            pair = []
            for al in alleles:
                if al not in ["0", "1", "2", "3", "4", "A", "C", "G", "T"]:
                    if al in ["5", "9", "D"]:
                        fout.write(
                            "WARNING, line %d: Special allele used %s\n" % (irow, al)
                        )
                    else:
                        fout.write("ERROR, line %d: Unknown allele %s\n" % (irow, al))
            for al in l[3:]:
                if len(pair) == 0:
                    pair.append(al)
                elif len(pair) == 2:
                    pair = [al]
                else:
                    pair.append(al)
                    if "0" in pair and pair[0] != pair[1]:
                        fout.write(
                            "WARNING, line %d: Missing allele (%s/%s)\n"
                            % (irow, pair[0], pair[1])
                        )
    alld = list(set(alldist))
    for i in xrange(0, markers / 2):
        s = set(markerallele[i])
        if (len(s) > 2 and "0" not in s) or len(s) > 3:
            fout.write(
                "ERROR: Too many alleles for marker no. %d: %s\n" % (i, ",".join(s))
            )
    if samples > 0:
        fout.write("INFO: %d samples\n" % (samples))
        fout.write("INFO: alleles present %s\n" % (" ".join([s for s in alld])))
    else:
        fout.write("WARNING: No sample lines\n")
    fin.close()
    fout.close()


def checkMarkers(inputfile, reportfile, verbose=False):
    if inputfile[-3:] == ".gz":
        fin = gzip.open(inputfile, "r")
    else:
        fin = open(inputfile, "r")
    fout = open(reportfile, "w")
    irow = 0
    markers = 0
    icol = None
    style = None
    markdict = {}
    for line in fin:
        irow += 1
        if line.startswith("#"):
            continue
        markers += 1
        l = line.strip().split()
        if not icol:
            icol = len(l)
            fout.write("INFO: %d columns\n" % icol)
            if "\r\n" in line:
                fout.write("INFO: File has windows-formating\n")
        if len(l) != icol:
            fout.write("ERROR, line %d: Too many/few columns (%d)\n" % (irow, len(l)))
        # if len(l) in [2,3] or len(l) > 5:
        #    fout.write('WARNING, line %d: Too many/few columns (%d)\n' % (irow,len(l)) )
        #    problems = True
        elif len(l) == 1:  # Format should be just marker names in one column
            if not style:
                style = "simple"
            if style != "simple":
                fout.write(
                    "WARNING, line %d: Too few columns (%d) for this format\n"
                    % (irow, len(l))
                )
            else:
                if l[0] not in markdict:
                    markdict[l[0]] = 1
                else:
                    fout.write("WARNING: Multiple entries for marker %s\n" % (l[0]))
        elif len(l) == 5:  # Format should be: Marker - Position - A1 - A2 - Chromosome
            if not style:
                style = "old"
            if style != "old":
                fout.write(
                    "WARNING, line %d: Too many columns (%d) for this format\n"
                    % (irow, len(l))
                )
            else:
                if len(l[2]) != 1 or len(l[3]) != 1:
                    fout.write(
                        "ERROR, line %d: Wrong format of alleles (%s,%s)\n"
                        % (irow, l[2], l[3])
                    )
                elif l[2] == l[3]:
                    fout.write(
                        "WARNING, line %d: Monomorphic marker (%s)\n" % (irow, l[0])
                    )
                if l[4] == "0":
                    fout.write(
                        "CAUTION, line %d: Setting chromosome to 0 will cause problems with BEAGLE\n"
                        % irow
                    )
                if l[0] not in markdict:
                    markdict[l[0]] = 1
                else:
                    fout.write("WARNING: Multiple entries for marker %s\n" % (l[0]))
        elif len(l) == 4:
            if not style:
                if len(l[2]) == len(l[3]) == 1:
                    style = "old"
                else:
                    style = "new"
            if style not in ["old", "new"]:
                fout.write(
                    "WARNING, line %d: Wrong number of columns (%d) for this format\n"
                    % (irow, len(l))
                )
            else:
                if style == "old" and l[0] not in markdict:
                    markdict[l[0]] = 1
                elif style == "new" and l[2] not in markdict:
                    markdict[l[2]] = 1
                else:
                    if style == "old":
                        fout.write("WARNING: Multiple entries for marker %s\n" % (l[0]))
                    elif style == "new":
                        fout.write("WARNING: Multiple entries for marker %s\n" % (l[2]))
                if style == "old" and (len(l[2]) != 1 or len(l[3]) != 1):
                    fout.write(
                        "Error, line %d: Wrong format of alleles (%s,%s)\n"
                        % (irow, l[2], l[3])
                    )
                elif style == "old" and l[2] == l[3]:
                    fout.write(
                        "WARNING, line %d: Monomorphic marker (%s)\n" % (irow, l[0])
                    )
        else:
            markers -= 1
    if markers > 1:
        fout.write("INFO: %d markers\n" % markers)
    else:
        fout.write("WARNING: No markers in file\n")
    if style:
        fout.write("Markerlist seems to match %s style\n" % style)
    else:
        fout.write("Markerlist does not match any of the known styles\n")
    fin.close()
    fout.close()


def checkPedigree(inputfile, reportfile, verbose=False):
    if inputfile[-3:] == ".gz":
        fin = gzip.open(inputfile, "r")
    else:
        fin = open(inputfile, "r")
    fout = open(reportfile, "w")
    fin.close()
    fout.close()


def checkCrimap(inputfile, reportfile, verbose=False):
    if inputfile[-3:] == ".gz":
        fin = gzip.open(inputfile, "r")
    else:
        fin = open(inputfile, "r")
    fout = open(reportfile, "w")
    samples = 0
    try:
        line = fin.next()
        if "\r\n" in line:
            fout.write("INFO: File has windows-formating\n")
        numfam = int(line.strip())
    except:
        fout.write("ERROR: Missing or wrong format for familynumber\nAborting...\n")
        fin.close()
        fout.close()
        sys.exit(0)
    try:
        nummark = int(fin.next().strip())
    except:
        fout.write("ERROR: Missing or wrong format for markernumbers\nAborting...\n")
        fin.close()
        fout.close()
        sys.exit(0)
    markers = fin.next().strip().split()
    if len(markers) != nummark:
        fout.write(
            "ERROR: Too few/many markers in markerlist (%d/%d)\n"
            % (len(markers), nummark)
        )
    alldist = []
    duplicates = {}
    irow = 0
    sampledict = {}
    for fam in xrange(0, numfam):
        famID = fin.next().strip()
        irow += 1
        try:
            nummem = int(fin.next().strip())
        except:
            fout.write(
                "ERROR: Missing or wrong number of members for family %s \nAborting...\n"
                % famID
            )
            fin.close()
            fout.close()
            sys.exit(0)
        irow += 1
        for memb in xrange(0, nummem):
            l = fin.next().strip().split()
            irow += 1
            if len(l) < 4:
                fout.write("ERROR, line %d: Not enough columns\nAborting...\n" % irow)
                fin.close()
                fout.close()
                sys.exit(0)
            if len(l[4:]) != nummark * 2:
                fout.write(
                    "ERROR, line %d: Too many/few alleles (%d/%d)\n"
                    % (irow, len(l[4:]), nummark)
                )
            else:
                alleles = list(set(l[4:]))
                alldist += alleles
                if l[0] not in duplicates:
                    duplicates[l[0]] = l[1], l[2]
                else:
                    fout.write(
                        "CAUTION: Sample %s is appearing multiple times\n" % l[0]
                    )
                    dam, sire = duplicates[l[0]]
                    if (
                        dam != l[1]
                        and "0" not in [dam, l[1]]
                        or sire != l[2]
                        and "0" not in [sire, l[2]]
                    ):
                        fout.write(
                            "WARNING: Pedigree of sample %s does not match previous entry\n"
                            % (l[0])
                        )
                if (l[0], famID) not in sampledict:
                    sampledict[(l[0], famID)] = l[1], l[2]
                else:
                    fout.write(
                        "WARNING: Multiple entries for sample %s in family %s\n"
                        % (l[0], famID)
                    )
                pair = []
                for al in alleles:
                    if al not in ["0", "1", "2", "3", "4"]:
                        fout.write("ERROR, line %d: Unknown allele %s\n" % (irow, al))
                for al in l[4:]:
                    if len(pair) == 0:
                        pair.append(al)
                    elif len(pair) == 2:
                        pair = [al]
                    else:
                        pair.append(al)
                        if "0" in pair and pair[0] != pair[1]:
                            fout.write(
                                "WARNING, line %d: Missing allele (%s/%s)\n"
                                % (irow, pair[0], pair[1])
                            )
    try:
        fin.next()
        fout.write("WARNING: File contains more samples than indicated\n")
    except StopIteration:
        pass
    for key in sampledict:
        anim, fam = key
        dam, sire = sampledict[key]
        if (dam, fam) not in sampledict and dam != "0":
            fout.write("ERROR: Sample %s not present in family %s\n" % (dam, fam))
        if (sire, fam) not in sampledict and sire != "0":
            fout.write("ERROR: Sample %s not present in family %s\n" % (sire, fam))
    alld = list(set(alldist))
    fout.write("INFO: alleles present %s\n" % (" ".join([s for s in alld])))
    fin.close()
    fout.close()


def checkBeagle(inputfile, reportfile, verbose=False):
    if inputfile[-3:] == ".gz":
        fin = gzip.open(inputfile, "r")
    else:
        fin = open(inputfile, "r")
    fout = open(reportfile, "w")
    firstline = True
    columns = None
    irow = 0
    markers = 0
    alldist = []
    for line in fin:
        irow += 1
        if line.startswith("#"):
            continue
        l = line.strip().split()
        if not columns:
            columns = len(l)
            fout.write("INFO: %d samples\n" % (columns - 2))
            if (columns - 2) % 2 != 0:
                fout.write(
                    "ERROR: Sample columns should be divisible by 2 (%d)\n"
                    % (columns - 2)
                )
        if len(l) != columns:
            fout.write(
                "ERROR, line %d: Too few/many columns (%d/%d)\n"
                % (irow, len(l), columns)
            )
        if l[0] == "I" and not firstline:
            fout.write("WARNING: Identifyer line should be the first line\n")
        elif l[0] == "I" and firstline:
            pairs = []
            for el in l[2:]:
                if len(pairs) == 0:
                    pairs.append(el)
                elif len(pairs) == 2:
                    pairs = [el]
                else:
                    pairs.append(el)
                    if pairs[0] != pairs[1]:
                        fout.write(
                            "ERROR: Wrong identifier line, expected 2 columns pr. animal\nAborting...\n"
                        )
                        fin.close
                        fout.close
                        sys.exit(0)
        elif l[0] == "A":
            pass
        elif l[0] == "M":
            markers += 1
            alleles = list(set(l[2:]))
            if (len(alleles) > 2 and "0" not in alleles) or len(alleles) > 3:
                fout.write(
                    "ERROR, line %d: Too many alleles %s\n"
                    % " ".join([s for s in alleles])
                )
            alldist += alleles
        else:
            fout.write("WARNING: Unknown line designation %s\n" % l[0])
        if firstline:
            firstline = False
            if "\r\n" in line:
                fout.write("INFO: File has windows-formating\n")
    if len(alldist) > 0:
        fout.write(
            "INFO: Alleles used %s\n" % " ".join([s for s in list(set(alldist))])
        )
    fin.close()
    fout.close()


def checkBeaglePairs(inputfile, reportfile, verbose=False):
    if inputfile[-3:] == ".gz":
        fin = gzip.open(inputfile, "r")
    else:
        fin = open(inputfile, "r")
    fout = open(reportfile, "w")
    firstline = True
    columns = None
    irow = 0
    markers = 0
    alldist = []
    for line in fin:
        irow += 1
        if line.startswith("#"):
            continue
        l = line.strip().split()
        if not columns:
            columns = len(l)
            fout.write("INFO: %d parent-offspring pairs\n" % ((columns - 2) / 4))
            if (columns - 2) % 4 != 0:
                fout.write(
                    "ERROR: Sample columns should be divisible by 4 with pair data (%d)\n"
                    % (columns - 2)
                )
        if len(l) != columns:
            fout.write(
                "ERROR, line %d: Too few/many columns (%d/%d)\n"
                % (irow, len(l), columns)
            )
        if l[0] == "I" and not firstline:
            fout.write("WARNING: Identifyer line should be the first line\n")
        elif l[0] == "I" and firstline:
            pairs = []
            for el in l[2:]:
                if len(pairs) == 0:
                    pairs.append(el)
                elif len(pairs) == 2:
                    pairs = [el]
                else:
                    pairs.append(el)
                    if pairs[0] != pairs[1]:
                        fout.write(
                            "ERROR: Wrong identifier line, expected 2 columns pr. animal\nAborting...\n"
                        )
                        fin.close
                        fout.close
                        sys.exit(0)
        elif l[0] == "A":
            pass
        elif l[0] == "M":
            markers += 1
            alleles = list(set(l[2:]))
            if (len(alleles) > 2 and "0" not in alleles) or len(alleles) > 3:
                fout.write(
                    "ERROR, line %d: Too many alleles %s\n"
                    % " ".join([s for s in alleles])
                )
            alldist += alleles
        else:
            fout.write("WARNING: Unknown line designation %s\n" % l[0])
        if firstline:
            firstline = False
            if "\r\n" in line:
                fout.write("INFO: File has windows-formating\n")
    if len(alldist) > 0:
        fout.write(
            "INFO: Alleles used %s\n" % " ".join([s for s in list(set(alldist))])
        )
    fin.close()
    fout.close()


def checkBeagleTrios(inputfile, reportfile, verbose=False):
    if inputfile[-3:] == ".gz":
        fin = gzip.open(inputfile, "r")
    else:
        fin = open(inputfile, "r")
    fout = open(reportfile, "w")
    firstline = True
    columns = None
    irow = 0
    markers = 0
    alldist = []
    for line in fin:
        irow += 1
        if line.startswith("#"):
            continue
        l = line.strip().split()
        if not columns:
            columns = len(l)
            fout.write("INFO: %d parent-parent-offspring trios\n" % ((columns - 2) / 6))
            if (columns - 2) % 6 != 0:
                fout.write(
                    "ERROR: Sample columns should be divisible by 6 with trio data (%d)\n"
                    % (columns - 2)
                )
        if len(l) != columns:
            fout.write(
                "ERROR, line %d: Too few/many columns (%d/%d)\n"
                % (irow, len(l), columns)
            )
        if l[0] == "I" and not firstline:
            fout.write("WARNING: Identifyer line should be the first line\n")
        elif l[0] == "I" and firstline:
            pairs = []
            for el in l[2:]:
                if len(pairs) == 0:
                    pairs.append(el)
                elif len(pairs) == 2:
                    pairs = [el]
                else:
                    pairs.append(el)
                    if pairs[0] != pairs[1]:
                        fout.write(
                            "ERROR: Wrong identifier line, expected 2 columns pr. animal\nAborting...\n"
                        )
                        fin.close
                        fout.close
                        sys.exit(0)
        elif l[0] == "A":
            pass
        elif l[0] == "M":
            markers += 1
            alleles = list(set(l[2:]))
            if (len(alleles) > 2 and "0" not in alleles) or len(alleles) > 3:
                fout.write(
                    "ERROR, line %d: Too many alleles %s\n"
                    % " ".join([s for s in alleles])
                )
            alldist += alleles
        else:
            fout.write("WARNING: Unknown line designation %s\n" % l[0])
        if firstline:
            firstline = False
            if "\r\n" in line:
                fout.write("INFO: File has windows-formating\n")
    if len(alldist) > 0:
        fout.write(
            "INFO: Alleles used %s\n" % " ".join([s for s in list(set(alldist))])
        )
    fin.close()
    fout.close()


def checkTyper(options):
    if options.inputfile[-3:] == ".gz":
        fin = gzip.open(options.inputfile, "r")
    else:
        fin = open(options.inputfile, "r")
    frep = open(options.reportfile, "w")
    if options.outputfile:
        fout = open(options.outputfile, "w")
    markers = {}
    samples = {}
    irow = 0
    headerproblem = False
    starting = False
    for line in fin:
        l = line.strip().split(",")
        irow += 1
        if irow == 1 and l[0] != "Best Call Probability Report":
            headerproblem = True
        if irow == 2 and l[0] != "Customer":
            headerproblem = True
        if irow == 3 and l[0] != "Project":
            headerproblem = True
        if irow == 4 and l[0] != "Plate":
            headerproblem = True
        if irow == 5 and l[0] != "Experiment":
            headerproblem = True
        if irow == 7 and l[0] != "":
            headerproblem = True
        if irow == 6 and l[0] != "Chip":
            headerproblem = True
        if irow == 8 and l[0] != "Sample":
            headerproblem = True
        if irow < 9 and not headerproblem:
            if options.outputfile:
                fout.write(line)
            continue
        elif irow == 9 and not headerproblem:
            starting = True
        if "Sample" in line:
            starting = True
            frep.write("INFO: Header lines do not match expected formatting\n")
            if options.outputfile:
                fout.write(line)
            continue
        if not starting:
            if options.outputfile:
                fout.write(line)
            continue
        if " " in l[0] or " " in l[1]:
            frep.write(
                "WARNING, line %d: Unexpected whitespace in marker or sample name\n"
                % irow
            )
        if len(l) != 6:
            frep.write("ERROR, line %d: Wrong number of columns\n" % irow)
            if len(l) == 7 and l[4] == "" and options.outputfile:
                fout.write(
                    "%s,%s,%s,%s,0.%s,%s\n" % (l[0], l[1], l[2], l[3], l[5], l[6])
                )
        else:
            if options.outputfile:
                fout.write(line)
        try:
            gc = float(l[4])
        except:
            frep.write("ERROR, line %d: Missing gc-score in column 5\n" % irow)
        markers[l[1]] = markers.get(l[1], 0) + 1
        samples[l[0]] = samples.get(l[0], 0) + 1
        if len(l[2]) > 2 and ("DEL" not in l[2] or "INS" not in l[2]):
            frep.write("ERROR, line %d: Unknown allele %s in column 3\n" % (irow, l[2]))
    if not starting:
        frep.write('ERROR: Missing "Sample" in title line\n')
    if len(markers) > 0:
        frep.write("INFO: %d markers\n" % len(markers))
    else:
        frep.write("WARNING: No markers found\n")
    if len(samples) > 0:
        frep.write("INFO: %d samples\n" % len(samples))
    else:
        frep.write("WARNING: No samples found\n")
    fin.close()
    frep.close()
    try:
        fout.close()
    except:
        pass


def checkIllumina(inputfile, reportfile, verbose=False):
    if inputfile[-3:] == ".gz":
        fin = gzip.open(inputfile, "r")
    else:
        fin = open(inputfile, "r")
    fout = open(reportfile, "w")
    markers = {}
    samples = {}
    alleles = []
    irow = 0
    headerproblem = False
    starting = False
    nogccolumn = 0
    for line in fin:
        l = line.strip().split()
        irow += 1
        if irow == 1 and l[0] != "[Header]":
            headerproblem = True
        if irow == 2 and l[0] != "GSGT":
            headerproblem = True
        if irow == 3 and l[0] != "Processing":
            headerproblem = True
        if irow == 4 and l[0] != "Content":
            headerproblem = True
        if irow == 5 and l[0] != "Num":
            headerproblem = True
        if irow == 6 and l[0] != "Total":
            headerproblem = True
        if irow == 7 and l[0] != "Num":
            headerproblem = True
        if irow == 8 and l[0] != "Total":
            headerproblem = True
        if irow == 9 and l[0] != "[Data]":
            headerproblem = True
        if irow == 10 and l[0] != "SNP":
            headerproblem = True
        if irow < 10 and not headerproblem:
            continue
        if irow == 10 and not headerproblem:
            starting = True
            continue
        if "[Data]" in line:
            starting = True
            fin.next()
            irow += 1
            fout.write("INFO: Detected manually edited header lines\n")
            continue
        if not starting:
            continue
        # if ' ' in l[0] or ' ' in l[1]: fout.write('WARNING, line %d: Unexpected space found\n' % irow)
        if len(l) not in [4, 5]:
            fout.write("ERROR, line %d: Wrong number of columns\n" % irow)
            continue
        if len(l) == 4:
            if nogccolumn < 10:
                fout.write("WARNING, line %d: Missing gc-value\n" % irow)
            elif nogccolumn == 10:
                fout.write("WARNING: More than 10 lines with missing gc-value...\n")
            nogccolumn += 1
        else:
            try:
                gc = float(l[4])
            except:
                fout.write(
                    "WARNING, line %d: Missing or wrong gc-score in column 5\n" % irow
                )
        if len(l[2]) > 1 or len(l[3]) > 1:
            fout.write(
                "WARNING, line %d: Wrong format for alleles (%s,%s)\n"
                % (irow, l[2], l[3])
            )
        if l[2] not in alleles:
            alleles.append(l[2])
        if l[3] not in alleles:
            alleles.append(l[3])
        markers[l[0]] = markers.get(l[0], 0) + 1
        samples[l[1]] = samples.get(l[1], 0) + 1
    if not starting:
        fout.write('ERROR: Missing header lines, "[Data]" and "c1 c2 c3 c4 c5"\n')
    if len(markers) > 0:
        fout.write("INFO: %d markers\n" % len(markers))
    else:
        fout.write("WARNING: No markers found\n")
    if len(samples) > 0:
        fout.write("INFO: %d samples\n" % len(samples))
    else:
        fout.write("WARNING: No samples found\n")
    if len(alleles) > 0:
        fout.write("INFO: alleles found %s" % (" ".join([s for s in alleles])))
    fin.close()
    fout.close()


def checkFasta(inputfile, reportfile, verbose=False):
    if inputfile[-3:] == ".gz":
        fin = gzip.open(inputfile, "r")
    else:
        fin = open(inputfile, "r")
    fout = open(reportfile, "w")
    started = False
    sequence = ""
    header = False
    for line in fin:
        if line.startswith("#"):
            continue
        if line.startswith(">") and not header:
            started = True
            header = True
        elif line.startswith(">") and header:
            fout.write("WARNING: Empty sequence\n")
        elif not started and not line.startswith(">"):
            fout.write("WARNING: Missing title line (>Title) at beginning of file\n")
        else:
            sequence += line.strip()
            header = False
    summary = {}
    for e in sequence:
        summary[e] = summary.get(e, 0) + 1
    fout.write("INFO:")
    for e in summary:
        fout.write(" %s:%d" % (e, summary[e]))
    fout.write("\n")
    fin.close()
    fout.close()


# ************************************ FIX routines ****************************


def fixFasta(inputfile, reportfile, outfile, verbose=False):
    """ Changes:
            [A/G] -> A
            Removes empty sequences
    """
    if inputfile[-3:] == ".gz":
        fin = gzip.open(inputfile, "r")
    else:
        fin = open(inputfile, "r")
    fout = open(reportfile, "w")
    foutd = open(outfile, "w")
    started = False
    irow = 0
    for line in fin:
        if line.startswith("#"):
            foutd.write(line)
            continue
        if line.startswith(">"):
            header = line
            # foutd.write(line)
            continue
        if len(line.strip()) <= 0:
            continue
        ind = line.find("[")
        if ind == -1:
            if header:
                foutd.write(header)
                header = None
            foutd.write(line)
            continue
        if header:
            foutd.write(header)
            header = None
        newline = line.replace(line[ind : ind + 5], "N")
        irow += 1
        foutd.write(newline)
    fout.write("INFO: Changed %d occurences\n" % irow)
    fin.close()
    fout.close()
    foutd.close()


# ******************************************************************************


def main():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-i", dest="inputfile", help="Genotype file", metavar="FILE")
    parser.add_option("-r", dest="reportfile", help="Report file", metavar="FILE")
    parser.add_option("-n", dest="informat", help="Input format")
    parser.add_option(
        "-f", dest="fix", action="store_true", help="Fix problems", default=False
    )
    parser.add_option("-o", dest="outputfile", help="Fixed outputfile")
    parser.add_option(
        "-v",
        dest="verbose",
        action="store_true",
        help="prints runtime info",
        default=False,
    )
    parser.add_option(
        "-G",
        dest="galaxy",
        action="store_true",
        help="Script is being run from galaxy",
        default=False,
    )
    (options, args) = parser.parse_args()
    if options.galaxy:
        if options.outputfile == "None":
            options.outputfile = None
        elif options.outputfile[:4] == "None":
            options.outputfile = options.outputfile[4:]
        elif options.outputfile[-4:] == "None":
            options.outputfile = options.outputfile[:-4]
    nofix = False
    if options.fix and options.informat == "fasta":
        fixFasta(
            options.inputfile, options.reportfile, options.outputfile, options.verbose
        )
    else:
        nofix = True
    if nofix:
        if options.informat == "geno":
            checkGeno(options.inputfile, options.reportfile, options.verbose)
        elif options.informat == "marker":
            checkMarkers(options.inputfile, options.reportfile, options.verbose)
        elif options.informat == "pedigree":
            checkPedigree(options.inputfile, options.reportfile, options.verbose)
        elif options.informat == "cri":
            checkCrimap(options.inputfile, options.reportfile, options.verbose)
        elif options.informat == "bgl":
            checkBeagle(options.inputfile, options.reportfile, options.verbose)
        elif options.informat == "bglpairs":
            checkBeaglePairs(options.inputfile, options.reportfile, options.verbose)
        elif options.informat == "bgltrios":
            checkBeagleTrios(options.inputfile, options.reportfile, options.verbose)
        elif options.informat == "typer":
            checkTyper(options)
        elif options.informat == "illumina":
            checkIllumina(options.inputfile, options.reportfile, options.verbose)
        elif options.informat == "gest":
            checkGest(options.inputfile, options.reportfile, options.verbose)
        elif options.informat == "gestM":
            checkGestM(options.inputfile, options.reportfile, options.verbose)
        elif options.informat == "fasta":
            checkFasta(options.inputfile, options.reportfile, options.verbose)
        else:
            sys.stdout.write("Unknown file format\n")


if __name__ == "__main__":
    main()
