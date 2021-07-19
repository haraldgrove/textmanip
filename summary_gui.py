#!/usr/bin/env python3
"""
Module Docstring
Following this tutorial:
http://zetcode.com/gui/pyqt5/firstprograms/
"""

__author__ = "Harald Grove"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import time
import sys
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QApplication, QWidget

def small_window():
    app = QApplication(sys.argv)


def main(args):
    """ Main entry point of the app """
    small_window()
    now = QDate.currentDate()
    print(now.toString(Qt.ISODate))
    print(now.toString(Qt.DefaultLocaleLongDate))

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

    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument("-n", "--name", action="store", dest="name")

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
