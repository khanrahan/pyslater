#!/usr/bin/env python

"""
Generates .ttg files for Autodesk Flame using data from a CSV file.
"""

from __future__ import print_function # ready for upgrade to python3
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

    return "".join(chr(int(character)) for character in decimal_string.split()[2:-1])


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


def makedirs(filepath, dry_run):
    """Make sure out the directories exist for given filepath
    Copied from https://stackoverflow.com/a/600612/119527"""

    dirpath = os.path.dirname(filepath)

    if dry_run is not True:
        try:
            os.makedirs(dirpath)
        except OSError as ex:
            if ex.errno == errno.ENOENT: #empty filepath
                pass
            elif ex.errno == errno.EEXIST:
                pass
            else:
                raise


def overwrite_query():
    """Prompt user with decision to overwrite."""

    prompt = ("Overwrite? [y]es / [n]o / [Y]es to All / [N]o to All ")
    valid_responses = ["y", "n", "Y", "N"]

    while True:
        result = raw_input(prompt)

        if result in valid_responses:
            break

    return result


def generate_html_page(html_template, new_html_filename,
                       line_number_to_replace, list_of_replacements, dry_run):
    """Generates HTML page of filenames to copy paste."""

    html_line = """  <button
    data-clipboard-text=\"master_name_goes_here\">master_name_goes_here</button>"""

    if dry_run is not True:
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


def validate_exclude_rows(string):
    """Ensure argparse string is numbers listed in range notation
    and/or single numbers separated by commas.  Expand into a single list.
    Copied from https://gist.github.com/kgaughan/2491663"""

    single_frames = set()

    for element in string.split(','):
        parts = [int(x) for x in element.split('-')]
        if len(parts) == 1:
            single_frames.add(parts[0])
        else:
            for frame in range(min(parts), max(parts) + 1):
                single_frames.add(frame)

    return list(single_frames)


def validate_output_template(string):
    """Ensure argparse output template argument has correct .ttg file extension."""

    if string.endswith(".ttg") is False:
        raise argparse.ArgumentTypeError("Output template must end in .ttg")
    return string


def list_offset(list_of_integers, offset):
    """Offset each entry in a list of integers by a given offset value."""

    return [x + offset for x in list_of_integers]


def create_parser():
    """Assemble parser of command line args."""

    parser = argparse.ArgumentParser(description="""generates .ttg files using a
        template TTG file and CSV full of data to fill in fields""",
                                     formatter_class=lambda prog:
                                     argparse.HelpFormatter(prog, max_help_position=40))
    parser.add_argument("csv_file", help="""path of the CSV file""")
    parser.add_argument("ttg_template",
                        nargs="?",
                        help="""path of the template TTG file""")

    filtering = parser.add_argument_group("row filtering")

    filter_rows = filtering.add_mutually_exclusive_group()
    filter_rows.add_argument("--exclude",
                             action="append",
                             default=[],
                             metavar="PATTERN",
                             help="""exclude lines from CSV matching PATTERN""")
    filter_rows.add_argument("--include",
                             action="append",
                             default=[],
                             metavar="PATTERN",
                             help="""include lines from CSV matching PATTERN""")

    filter_row_numbers = filtering.add_mutually_exclusive_group()
    filter_row_numbers.add_argument("--exclude-rows",
                                    default=[1],
                                    metavar="NUMBERS",
                                    type=validate_exclude_rows,
                                    help="""row numbers to exclude in CSV""")
    filter_row_numbers.add_argument("--include-rows",
                                    default=[],
                                    metavar="NUMBERS",
                                    type=validate_exclude_rows,
                                    help="""row numbers to include in CSV""")

    existing_file = parser.add_argument_group("existing file")
    existing_exclusive = existing_file.add_mutually_exclusive_group()
    existing_exclusive.add_argument("--force-overwrite",
                                    default=False,
                                    action="store_true",
                                    help="""overwrite existing TTGs without
                                    confirmation.  same as Yes to All.""")
    existing_exclusive.add_argument("--skip-existing",
                                    default=False,
                                    action="store_true",
                                    help="""skip existing TTGs.  same as No to All.""")

    parser.add_argument("--header-row",
                        default=1,
                        metavar="NUMBER",
                        type=int,
                        help="row number of the column headers.  default is 1.")
    parser.add_argument("-n", "--dry-run",
                        default=False,
                        action="store_true",
                        help="""perform trial run with no files written""")
    parser.add_argument("--no-html",
                        default=False,
                        action="store_true",
                        help="""skip output of HTML""")
    parser.add_argument("-o", "--output",
                        default=os.path.join(os.getcwd(), "{5}_{6}_{4}"),
                        help="template for output file names""",
                        metavar="TEMPLATE",
                        type=validate_output_template)
    return parser


def write_ttg(filepath, line_replacements, ttg_file_list, unicode_keywords,
              dry_run):
    """
    Writes out a ttg.
    filepath = full destination path and filename
    line_replacements = dictionary of replacements and their destination line
    numbers
    ttg_file_list = the template ttg stored a list of lines
    unicode_keywords = dictionary of the keywords in the template and their
    line number
    """

    if dry_run is not True:
        with open(filepath, "w") as ttg:
            for line_number, text in enumerate(ttg_file_list, 1):
                if line_number + 1 in list(unicode_keywords.keys()):
                    new_text = line_replacements[unicode_keywords[line_number
                                                                  + 1]]
                    ttg.write("TextLength " +
                              str(len(convert_to_ttg_text(new_text).split())) +
                              "\n")
                elif line_number in list(unicode_keywords.keys()):
                    new_text = line_replacements[unicode_keywords[line_number]]
                    ttg.write("Text " + convert_to_ttg_text(new_text) + "\n")
                else:
                    ttg.write(text + "\n")


def main():
    """Script that is run when called from the command line."""

    # Gather Args
    parser = create_parser()
    args = parser.parse_args()

    # Sort out CSV
    csv_rows = read_unicode_csv_file(args.csv_file)

    # Modify Args
    if args.include == []:
        args.include.append("*")
    if args.include_rows == []:
        args.include_rows = list_offset(list(range(len(csv_rows))), 1)

    # Gather keywords in TTG file
    if args.ttg_template is not None:
        ttg_file_list = read_ttg_file(args.ttg_template)
        ttg_keywords = find_ttg_keywords(ttg_file_list)
        unicode_keywords = {index: convert_from_ttg_text(raw_string) for index,
                            raw_string in list(ttg_keywords.items())}

        print("Found %s keywords in %s:" % (len(unicode_keywords),
                                            args.ttg_template))
        print(", ".join([keyword for _, keyword in list(unicode_keywords.items())]))

    print("Found %s rows in %s" % (len(csv_rows), args.csv_file))

    # Assemble output TTG filepaths
    ttg_results = []

    for row_number, row in enumerate(csv_rows):
        # Check against exclude-rows
        if row_number in list_offset(args.exclude_rows, -1):
            print(" ".join(["Skipping row", str(row_number + 1)]))
            continue

        # Check against include-rows arguments
        if not row_number in list_offset(args.include_rows, -1):
            print(" ".join(["Skipping row", str(row_number +1)]))
            continue

        row_tidy = [tidy_text(item) for item in row]
        row_tidy_dict = {keyword: entry for keyword, entry
                         in zip(csv_rows[0], row_tidy)}

        filepath = expand_path(args.output).format(* row_tidy, ** row_tidy_dict)

        # Check output filename against exclude argument
        if True in [fnmatch.fnmatch(filepath, arg) for arg in args.exclude]:
            print(" ".join(["Skipping", filename_no_ext(filepath)]))
            continue

        # Check output filename against include argument
        if False in [fnmatch.fnmatch(filepath, arg) for arg in args.include]:
            print(" ".join(["Skipping", filename_no_ext(filepath)]))
            continue

        print(" ".join(["Proceeding with", filename_no_ext(filepath)]))

        # Check for overwrite
        exists = os.path.isfile(filepath)

        if exists:
            print("%s already exists!" % filepath)

        if exists and args.force_overwrite is True:
            pass
        elif exists and args.skip_existing is True:
            print("Skipping %s" % filepath)
            continue
        else:
            reply = overwrite_query()
            if reply == "y":
                pass
            if reply == "n":
                print("Skipping %s" % filepath)
                continue
            if reply == "Y":
                args.force_overwrite = True
            if reply == "N":
                args.skip_existing = True
                continue

        ttg_results.append(filepath)

        # Start writing out TTGs
        if args.ttg_template is not None:
            print("".join(["Writing out ", filepath]))

            # Assemble dict using header row for keys and row entries
            # for the replacements
            line_replacements = {keyword: entry for keyword, entry in
                                 zip(csv_rows[args.header_row - 1], csv_rows[row_number])}

            makedirs(filepath, args.dry_run) #Make output path if necessary
            write_ttg(filepath, line_replacements, ttg_file_list,
                      unicode_keywords, args.dry_run)

    if args.no_html is False:
        template_path = os.path.join(script_path(), "template.html")
        html_destination = os.path.join(common_path(ttg_results),
                                        "copy_paster.html")
        ttg_filenames = [filename_no_ext(i) for i in ttg_results]

        print(" ".join(["Writing out", html_destination]))

        makedirs(html_destination, args.dry_run)
        generate_html_page(template_path, html_destination, 40, ttg_filenames,
                           args.dry_run)

    print("Done!")

if __name__ == "__main__":
    main()
