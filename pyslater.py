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
    """Returns a tuple of list data from a csv file passed to it."""

    try:
        with open(filename, 'rU') as open_file: #remove the U. use newline=
            raw_rows = csv.reader(open_file)
            unicode_rows = []
            for utf8_row in raw_rows:
                unicode_row = [x.decode('utf8') for x in utf8_row]
                unicode_rows.append(unicode_row)
            return tuple(unicode_rows)
    except Exception as ex:
        raise ex

def read_ttg_file(filename):
    """Return contents of TTG file."""

    try:
        with open(filename, 'r') as open_file:
            contents = open_file.read().splitlines()
            return contents
    except Exception as ex:
        raise ex

def find_ttg_keywords(ttg_file_list):
    """Returns dictionary containing the line number and contents
    for the keywords that are wrapped in percent symbols."""

    return {line:text for line, text in enumerate(ttg_file_list, 1) if
            text.startswith('Text 37') and text.endswith('37')}

def convert_from_ttg_text(decimal_string):
    """Returns unicode standard string minus the "Text" at the beginning
   and the % / 37 keyword wrappers"""

    return "".join(unichr(int(character)) for character in decimal_string.split()[2:-1])

def convert_to_ttg_text(string):
    """Returns TTG style string"""

    return " ".join(str(ord(character)) for character in list(string))

def common_path(paths):
    """Returns common parent directory from list of paths.
    Not necessary in Python 3.5 because of os.path.commonpath()"""

    return os.path.dirname(os.path.commonprefix(paths))

def expand_path(path):
    """Expand shell variables and ~."""

    return os.path.expandvars(os.path.expanduser(path))

def filename_no_ext(filepath):
    """Return just filename without extension."""

    return os.path.splitext(os.path.basename(filepath))[0]

def tidy_text(text):
    """Returns string that is appropriate for filename usage."""

    # Delete first and last character if a symbol or space.
    chopped = re.sub(r"^[\W_]+|[\W_]+$", "", text)
    # Convert symbols & whitespace to underscores.
    sanitized = re.sub(r"\W+", "_", chopped)
    # Remove duplicate underscores.
    tidy = re.sub(r"(_)\1+", "_", sanitized)

    return tidy

def makedirs(filepath):
    """Make sure out the directories exist for given filepath
    Copied from https://stackoverflow.com/a/600612/119527"""

    dirpath = os.path.dirname(filepath)

    try:
        os.makedirs(dirpath)
    except OSError as ex:
        if ex.errno == errno.EEXIST:
            pass
        else:
            raise

#def generate_ttg_filepath(output_template, entries_list, entries_dict):
#    """ """
#
#    return result

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

def script_path():
    """Returns the path to this script file.
    Copied from https://stackoverflow.com/questions/918154/relative-paths-in-python"""

    return os.path.dirname(os.path.abspath(__file__))

def validate_output_template(string):
    """Ensure argparse output template argument has correct .ttg file extension."""

    if string.endswith(".ttg") is False:
        raise argparse.ArgumentTypeError("Output template must end in .ttg")
    return string

def validate_skip_rows(string):
    """Ensure argparse skip-rows argument is correct."""

    try:
        number = int(string)
    except:
        raise argparse.ArgumentTypeError("Must be a number")

    rows_skipped = range(number)
    return rows_skipped


def main():
    """Script that is run when called from the command line."""

    parser = argparse.ArgumentParser(description="""generates .ttg files using a
        template TTG file and CSV full of data to fill in fields""")
    parser.add_argument("csv_file", help="""path of the CSV file""")
    parser.add_argument("ttg_template",
                        nargs="?",
                        help="""path of the template TTG file""")

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

    parser.add_argument("-o", "--output",
                        default=os.path.join(os.getcwd(), "{5}_{6}_{4}"),
                        help="template for output file names""",
                        metavar="TEMPLATE",
                        type=validate_output_template)
    parser.add_argument("-n", "--dry-run",
                        action="store_true",
                        help="""perform trial run with no files written""")
    parser.add_argument("--no-html-output",
                        default=False,
                        action="store_true",
                        help="""skip output of html""")
    parser.add_argument("--skip-rows",
                        default=[0],
                        metavar="NUMBER",
                        type=validate_skip_rows,
                        help="""number of rows to skip in CSV""")

    args = parser.parse_args()
    print args

    if args.include == []:
        args.include.append("*")

    # Sort out CSV
    csv_rows = read_unicode_csv_file(args.csv_file)

    print "Found %s rows in the CSV file." % len(csv_rows)

    # Gather keywords in TTG file
    if args.ttg_template is not None:
        ttg_file_list = read_ttg_file(args.ttg_template)
        ttg_keywords = find_ttg_keywords(ttg_file_list)
        unicode_keywords = {index: convert_from_ttg_text(raw_string) for index,
                            raw_string in ttg_keywords.items()}

        print "Found %s keywords in the TTG template:" % len(unicode_keywords)
        print ", ".join([keyword for line_number, keyword in unicode_keywords.iteritems()])

    # Assemble output TTG filepaths
    ttg_results = []

    for row_number, row in enumerate(csv_rows):
        if row_number in args.skip_rows:
            print " ".join(["Skipping row", str(row_number + 1)])
            continue
        else:
            row_tidy = [tidy_text(item) for item in row]
            row_tidy_dict = {keyword: entry for keyword, entry
                             in zip(csv_rows[0], row_tidy)}

            filepath = expand_path(args.output).format(* row_tidy, ** row_tidy_dict)

            # Check output filename against exclude argument
            if True in [fnmatch.fnmatch(filepath, arg) for arg in args.exclude]:
                print " ".join(["Skipping", filename_no_ext(filepath)])
                continue

            # Check output filename against include argument
            if True in [fnmatch.fnmatch(filepath, arg) for arg in args.include]:
                print " ".join(["Proceeding with", filename_no_ext(filepath)])
            else:
                print " ".join(["Skipping", filename_no_ext(filepath)])
                continue

            ttg_results.append(filepath)

            # Start writing out TTGs
            if args.ttg_template is not None:
                print "".join(["Writing out ", filepath])

                # Assemble dict using header row for keys and row entries
                # for the replacements
                line_replacements = {keyword: entry for keyword, entry in
                                     zip(csv_rows[0], csv_rows[1:][row_number])}

                if args.dry_run is False:
                    #Make output path if necessary
                    makedirs(filepath)

                    with open(filepath, "w") as ttg:
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
        template_path = os.path.join(script_path(), "template.html")
        html_destination = os.path.join(common_path(ttg_results),
                                        "copy_paster.html")
        ttg_filenames = [filename_no_ext(i) for i in ttg_results]

        print " ".join(["Writing out", html_destination])

        if args.dry_run is False:
            makedirs(html_destination)
            generate_html_page(template_path, html_destination, 40,
                               ttg_filenames)

    print "Done!"

if __name__ == "__main__":
    main()
