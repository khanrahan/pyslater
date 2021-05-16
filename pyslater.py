#!/usr/bin/env python

"""
Generates .ttg files for Autodesk Flame using data from a CSV file.
"""

import argparse
import csv
import errno
import fnmatch
import os
import re

def read_unicode_csv_file(filename):
    """Returns a tuple of list data from a csv file passed to it.
    Prints any exceptions from reading the file."""

    try:
        with open(filename, 'rU') as open_file: #remove the U. use newline=
            raw_rows = csv.reader(open_file)
            unicode_rows = []
            for utf8_row in raw_rows:
                unicode_row = [x.decode('utf8') for x in utf8_row]
                unicode_rows.append(unicode_row)
            return tuple(unicode_rows)
    except Exception as ex:
        print ex

def read_ttg_file(filename):
    """Return contents of TTG file."""

    try:
        with open(filename, 'r') as open_file:
            contents = open_file.read().splitlines()
            return contents
    except Exception as ex:
        print ex

def find_ttg_keywords(ttg_file_list):
    """Returns a list with tuples containing the line number and contents for
    the keywords that are wrapped in percent symbols."""

    return {line:text for line, text in enumerate(ttg_file_list, 1) if
            text.startswith('Text 37') and text.endswith('37')}

def convert_from_ttg_text(decimal_string):
    """Returns unicode standard string minus the "Text" at the beginning
    and the % / 37 keyword wrappers"""

    return "".join(unichr(int(character)) for character in decimal_string.split()[2:-1])

def convert_to_ttg_text(string):
    """Returns TTG style string"""

    return " ".join(str(ord(character)) for character in list(string))

def tidy_text(text):
    """Returns string that is appropriate for filename usage."""
    # Delete first and last character if a symbol or space.
    chopped = re.sub(r"^[\W_]+|[\W_]+$", "", text)
    # Convert symbols & whitespace to underscores.
    sanitized = re.sub(r"\W+", "_", chopped)
    # Remove duplicate underscores.
    tidy = re.sub(r"(_)\1+", "_", sanitized)

    return tidy

def generate_html_page(html_template, new_html_filename,
                       line_number_to_replace, list_of_replacements):
    """Generates HTML page of filenames to copy paste."""
    html_line = """  <button
    data-clipboard-text=\"master_name_goes_here\">master_name_goes_here</button>"""

    with open(html_template, 'rU') as source_file:
        with open(new_html_filename, 'w') as destination_file:
            for line_number, line in enumerate(source_file, 1):
                if line_number == line_number_to_replace:
                    for entry in list_of_replacements:
                        destination_file.write(html_line.replace("master_name_goes_here",
                                                                 entry) + "\n")
                else:
                    destination_file.write(line)

def main():
    """Script that is run when called from the command line."""

    parser = argparse.ArgumentParser(description="""generates .ttg files using a
        template TTG file and CSV full of data to fill in fields""")
    parser.add_argument("csv_file", help="""path of the CSV file""")
    parser.add_argument("ttg_template",
                        nargs="?",
                        help="""path of the template TTG file""")
    parser.add_argument("output_path",
                        default=os.getcwd(),
                        help="""path to a directory for output files""",
                        nargs="?",
                        type=os.path.abspath)

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--exclude",
                       action="append",
                       default=[],
                       metavar="PATTERN",
                       help="""exclude lines from csv matching PATTERN""")
    group.add_argument("--include",
                       action="append",
                       default=[],
                       metavar="PATTERN",
                       help="""include lines from csv matching PATTERN""")

    parser.add_argument("--output",
                        default="{5}_{6}_{4}",
                        help="template for output file names""",
                        metavar="TEMPLATE")
    parser.add_argument("-n", "--dry-run",
                        action="store_true",
                        help="""perform trial run with no files written""")
    parser.add_argument("--no-html-output",
                        default=False,
                        action="store_true",
                        help="""skip output of html""")

    args = parser.parse_args()
    if args.include == []:
        args.include.append("*")

    # Gather keywords in TTG file
    ttg_file_list = read_ttg_file(args.ttg_template)
    ttg_keywords = find_ttg_keywords(ttg_file_list)

    unicode_keywords = {index: convert_from_ttg_text(raw_string) for index,
                        raw_string in ttg_keywords.items()}
    print "Found %s keywords in the TTG template:" % len(unicode_keywords)
    print ", ".join([keyword for line_number, keyword in unicode_keywords.iteritems()])

    # Sort out csv
    csv_rows = read_unicode_csv_file(args.csv_file)

    # Make sure output path exists
    # Taken from https://stackoverflow.com/a/600612/119527
    try:
        os.makedirs(args.output_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(args.output_path):
            pass
        else:
            raise

    # Start writing out ttgs
    print "Found %s rows in the CSV file." % len(csv_rows)
    ttg_filenames = []
    for i, row in enumerate(csv_rows[1:]): #skip header row and start at 1

        row_tidy = [tidy_text(item) for item in row]
        row_tidy_dict = {keyword: entry for keyword, entry
                         in zip(csv_rows[0], row_tidy)}

        filename = args.output.format(* row_tidy, ** row_tidy_dict)

        # Check output filename against exclude argument
        if True in [fnmatch.fnmatch(filename, arg) for arg in args.exclude]:
            print " ".join(["Skipping", filename])
            continue

        # Check output filename against include argument
        if True in [fnmatch.fnmatch(filename, arg) for arg in args.include]:
            print " ".join(["Proceeding with", filename])
        else:
            print " ".join(["Skipping", filename])
            continue

        ttg_filenames.append(filename)

        filepath = os.path.join((args.output_path), filename)
        print "".join(["Writing out ", filepath, ".ttg"])

        # Assemble dict using header row for keys and row entries
        # for the replacements
        line_replacements = {keyword: entry for keyword, entry in
                             zip(csv_rows[0], csv_rows[1:][i])}

        if args.dry_run is False:
            with open(".".join([filepath, "ttg"]), "w") as ttg:
                for line_number, text in enumerate(ttg_file_list, 1):
                    if line_number + 1 in unicode_keywords.keys():
                        new_text = line_replacements[unicode_keywords[line_number
                                                                      + 1]]
                        ttg.write("TextLength " +
                                  str(len(convert_to_ttg_text(new_text).split())) +
                                  "\n")
                    elif line_number in unicode_keywords.keys():
                        new_text = line_replacements[unicode_keywords[line_number]]
                        ttg.write("Text " + convert_to_ttg_text(new_text) + "\n")
                    else:
                        ttg.write(text + "\n")

    if args.no_html_output is False:
        html_destination = os.path.join(args.output_path, "copy_paster.html")
        print " ".join(["Writing out", html_destination])
        generate_html_page("template.html", html_destination, 40,
                           ttg_filenames)

    print "Done!"

if __name__ == "__main__":
    main()
