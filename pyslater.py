#!/usr/bin/env python

import argparse
import os
import csv

PARSER = argparse.ArgumentParser(description="""generates .ttg files using a
        template TTG file and CSV full of data to fill in fields""")
PARSER.add_argument("csv_file", help="""path of the CSV file.""")
ARGS = PARSER.parse_args()
print ARGS.csv_file

def read_csv_file(filename):
    """Returns a list of data from a csv file passed to it.
    Only reads files from 'C:\Users\User\Documents\' + filename
    Prints any exceptions from reading the file."""

    filepath = os.path.join(r'', filename)

    try:
        with open(filepath, 'rU') as c:
            rows = csv.reader(c)
            return list(rows)
    except Exception as ex:
        print(ex)

ROWS = read_csv_file(ARGS.csv_file)
print('\n'.join(map(str, ROWS)))
