#!/usr/bin/env python

"""
Docstring to come.
"""

import argparse
import csv

def read_csv_file(filename):
    """Returns a tuple of list data from a csv file passed to it.
    Prints any exceptions from reading the file."""

    try:
        with open(filename, 'rU') as open_file:
            rows = csv.reader(open_file)
            return tuple(rows)
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

def main():
    """Docstring to be."""

    parser = argparse.ArgumentParser(description="""generates .ttg files using a
        template TTG file and CSV full of data to fill in fields""")
    parser.add_argument("ttg_template", help="""path of the template TTG file""")
    parser.add_argument("csv_file", help="""path of the CSV file""")
    parser.add_argument("-u", "--underscores", action="store_true",
                        help="""replace spaces and illegal characters in output filenames""")
    args = parser.parse_args()

    print args.csv_file
    print args.ttg_template

    #gather keywords
    ttg_file_list = read_ttg_file(args.ttg_template)
    ttg_keywords = find_ttg_keywords(ttg_file_list)
    keywords = [(index, convert_from_ttg_text(raw_string)) for index, raw_string in ttg_keywords]

    #sort out csv
    rows = read_csv_file(args.csv_file)
    print '\n'.join(str(i) for i in rows)

    #start writing out ttgs
    for i, line in enumerate(rows):
        #skip header rowd
        if i == 0:
            pass
        else:
            #later add a filename formatting function
            filename = "_".join([spot_name, duration, tidy_text(title)])
            with open(filename, 'a') as the_file:
                the_file.write(line)

if __name__ == "__main__":
    main()
