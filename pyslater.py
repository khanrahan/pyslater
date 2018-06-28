#!/usr/bin/env python

import argparse
import csv

def read_csv_file(filename):
    """Returns a list of data from a csv file passed to it.
    Prints any exceptions from reading the file."""

    try:
        with open(filename, 'rU') as open_file:
            rows = csv.reader(open_file)
            return list(rows)
    except Exception as ex:
        print ex

def read_ttg_file(filename):
    """Docstring to be."""

    try:
        with open(filename, 'r') as open_file:
            contents = open_file.read().splitlines()
            return contents
    except Exception as ex:
        print ex

def find_ttg_keywords(ttg_file_list):
    """Returns a list with tuples containing the line number and contents for
    the keywords that are wrapped in percent symbols."""

    return [(i, j) for (i, j) in enumerate(ttg_file_list) if
            j.startswith('Text 37') and j.endswith('37')]

def convert_from_ttg_text(decimal_string):
    """Returns unicode standard string minus the "Text" at the beginning
    and the % / 37 keyword wrappers"""

    return "".join(unichr(int(character)) for character in decimal_string.split()[2:-1])

def tidy_text():
    """docstring"""

    pass

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description="""generates .ttg files using a
        template TTG file and CSV full of data to fill in fields""")
    PARSER.add_argument("ttg_template", help="""path of the template TTG file""")
    PARSER.add_argument("csv_file", help="""path of the CSV file""")
    PARSER.add_argument("-u", "--underscores", action="store_true",
            help="""replace spaces and illegal characters in output filenames""")
    ARGS = PARSER.parse_args()

    print ARGS.csv_file
    print ARGS.ttg_template

    #gather keywords

    TTG_FILE_LIST = read_ttg_file(ARGS.ttg_template)
    TTG_KEYWORDS = find_ttg_keywords(TTG_FILE_LIST)
    KEYWORDS = [(a, convert_from_ttg_text(b)) for a, b in TTG_KEYWORDS]

    #start writing out ttgs

    ROWS = read_csv_file(ARGS.csv_file)
    print '\n'.join(str(i) for i in ROWS)
