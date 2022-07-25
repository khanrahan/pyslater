#!/usr/bin/env python

"""
PySlater

Description:
    Generates TTG files for Autodesk Flame using data from a CSV file.

    Will also export an HTML of the result TTG names.  The HTML will have buttons
    that when clicked, will copy the entry to the clipboard for easy pasting onto
    the sequences in Autodesk Flame.

    This module contains the class PySlater that does all of the actual work.
    This class could be imported into a Python environment and used on it's own.

    This module also contains the necessary argparse and __main__ details to be
    used from the command line.

URL:
    https://github.com/khanrahan/pyslater
"""

from __future__ import print_function

__version_info__ = (0, 0, 1)
__version__ = ".".join([str(num) for num in __version_info__])

import argparse
import csv
import errno
import fnmatch
import os
import re
import sys


class PySlater(object):
    """The main ttg and html generating class.

    Arguments:

    csv_file:        str   CSV file of slate data

    filter_include:  list  search string to match which lines to include.
                           example ["*foo*", "*bar*"]

    filter_exclude:  list  search string to match which lines to exclude.
                           example ["*foo*", "*bar*"]

    force_overwrite: bool  whether to overwrite existing TTGs

    output:          str   output path for the generated TTGs.  accepts tokens
                           wrapped in <> that match column names in the CSV.

    row_header:      int   location of the column titles in the CSV.  index of 1.

    row_exclude:     str   exclude rows by #. index of 1. single and/or a range.
                           example "1,3-17,87"

    row_include:     str   include rows by #. index of 1. single and/or a range.
                           example "1,3-17,87"

    skip_existing:   bool  skip overwriting existing files

    template_html:   str   HTML template file to populate with result TTG names

    template_ttg:    str   TTG template file to populate with data from the CSV
    """

    def __init__(self, csv_file, output, dry_run=False, html=True, filter_include=None,
                 filter_exclude=None, force_overwrite=False,
                 row_header=1, row_exclude=None, row_include=None,
                 skip_existing=False, template_html=None, template_ttg=None):

        self.script_path = self.get_script_path()

        # Default Args
        self.csv_file = csv_file
        self.output = self.expand_path(output)  # should this go to argparse?

        # Optional Args
        self.dry_run = dry_run
        self.filter_include = filter_include or []
        self.filter_exclude = filter_exclude or []
        self.force_overwrite = force_overwrite
        self.html = html
        self.row_header = row_header  # index based on 1
        self.row_include = self.expand_row_notation(row_include) if row_include else []
        self.row_exclude = self.expand_row_notation(row_exclude) if row_exclude else []
        self.skip_existing = skip_existing
        self.template_html = template_html or self.get_template_html()
        self.template_ttg = template_ttg

        # Generated Args at self.run()
        self.csv_rows = ()
        self.filepath_pattern = ""
        self.template_ttg_rows = []  # why is this not a tuple too?
        self.template_ttg_keywords = {}

        # Args for each Slate
        self.filepath = ""
        self.reply = ""
        self.ttg_replacements = {}

        # Remaining Args
        self.html_destination = ""

        self.results = []

    @staticmethod
    def common_path(paths):
        """Returns common parent directory from list of paths.
        Not necessary in Python 3.5 because of os.path.commonpath()"""

        return os.path.dirname(os.path.commonprefix(paths))

    @staticmethod
    def convert_from_ttg_text(decimal_string):
        """Returns unicode standard string minus the "Text" at the beginning
       and the <> keyword wrappers"""

        return "".join(chr(int(character)) for character in
                       decimal_string.split()[2:-1])

    @staticmethod
    def convert_to_ttg_text(string):
        """Returns TTG style string"""

        return " ".join(str(ord(character)) for character in list(string))

    @staticmethod
    def convert_output_tokens(path):
        """Convert <> to {}
        Flame convention for tokens is <>. Python uses {} for string formatting.
        """

        try:
            if not path:  # Catch empty string
                raise ValueError

            path = path.replace("<", "{").replace(">", "}")

        except ValueError:
            print("Output argument cannot be empty!")

        return path

    @staticmethod
    def expand_path(path):
        """Expand shell variables and ~"""

        try:
            return os.path.expandvars(os.path.expanduser(path))
        except AttributeError:
            print("Output missing!")

    @staticmethod
    def filename_no_ext(filepath):
        """Return just filename without extension."""

        return os.path.splitext(os.path.basename(filepath))[0]

    @staticmethod
    def find_ttg_keywords(ttg_file_list):
        """Returns dictionary containing the line number and contents
        for the keywords that are wrapped in greater/less than symbols aka
        angle brackets.  Angle brackets follow Flame convention for tokens.
        60 = <
        62 = >"""

        return {line: text for line, text in enumerate(ttg_file_list, 1) if
                text.startswith('Text 60') and text.endswith('62')}

    @staticmethod
    def write_html_page(html_template, new_html_filename,
                        line_number_to_replace, list_of_replacements):
        """Generates HTML page of filenames to copy paste."""

        html_line = """  <button
        data-clipboard-text=\"master_name_goes_here\">master_name_goes_here</button>"""

        if sys.version_info[0] >= 3:
            source_file = open(html_template, newline='')  # python3

        if sys.version_info[0] < 3:
            source_file = open(html_template, 'rU')  # python2.7

        destination_file = open(new_html_filename, 'w')

        with source_file:
            with destination_file:
                for line_number, line in enumerate(source_file, 1):
                    if line_number == line_number_to_replace:
                        for entry in list_of_replacements:
                            destination_file.write(html_line.replace("master_name_goes_here",
                                                                     entry) + "\n")
                    else:
                        destination_file.write(line)

    @staticmethod
    def expand_row_notation(string):
        """Expand numbers listed in range notation and/or single numbers
        separated by commas into a single list.
        Copied from https://gist.github.com/kgaughan/2491663
        """

        single_frames = set()

        for element in string.split(','):
            parts = [int(x) for x in element.split('-')]
            if len(parts) == 1:
                single_frames.add(parts[0])
            else:
                for frame in range(min(parts), max(parts) + 1):
                    single_frames.add(frame)

        return list(single_frames)

    @staticmethod
    def get_script_path():
        """Returns the path to this script file.
        Copied from https://stackoverflow.com/questions/918154/relative-paths-in-python"""

        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def list_offset(list_of_integers, offset):
        """Offset each entry in a list of integers by a given offset value."""

        return [x + offset for x in list_of_integers]

    @staticmethod
    def makedirs(filepath):
        """Make sure out the directories exist for given filepath
        Copied from https://stackoverflow.com/a/600612/119527
        """

        dirpath = os.path.dirname(filepath)

        try:
            os.makedirs(dirpath)
        except OSError as ex:
            if ex.errno == errno.ENOENT:  # empty filepath
                pass
            elif ex.errno == errno.EEXIST:
                pass
            else:
                raise

    @staticmethod
    def tidy_text(text):
        """Returns string that is appropriate for filename usage."""

        # Chop first and last character if a symbol or space.
        chopped = re.sub(r"^[\W_]+|[\W_]+$", "", text)
        # Swap aspect ratios using colons such as 1:1 to 1x1
        swapped = re.sub(r"([1-9]+):([1-9]+[0-9]*)", r"\1x\2", chopped)
        # Santize symbols & whitespace to underscores.
        sanitized = re.sub(r"\W+", "_", swapped)
        # Tidy up duplicate underscores.
        tidy = re.sub(r"(_)\1+", "_", sanitized)

        return tidy

    @staticmethod
    def overwrite_query():
        """Prompt user with decision to overwrite."""

        prompt = ("Overwrite? [y]es / [n]o / [Y]es to All / [N]o to All ")
        valid_responses = ["y", "n", "Y", "N"]

        while True:
            try:
                result = raw_input(prompt)  # python 2.7
            except NameError:
                result = input(prompt)

            if result in valid_responses:
                break

        return result

    def read_ttg_file(self):
        """Return contents of TTG file."""

        try:
            with open(self.template_ttg, 'r') as open_file:
                contents = open_file.read().splitlines()
                return contents

        except Exception as ex:
            raise ex

    def read_unicode_csv_file(self):
        """Returns a tuple of list data from a csv file passed to it."""

        try:
            if sys.version_info[0] >= 3:
                open_file = open(self.csv_file, newline='')  # python3

                with open_file:
                    raw_rows = csv.reader(open_file)
                    unicode_rows = [row for row in raw_rows]

            if sys.version_info[0] < 3:
                open_file = open(self.csv_file, 'rU')  # python2.7

                with open_file:
                    raw_rows = csv.reader(open_file)
                    unicode_rows = []

                    for utf8_row in raw_rows:
                        unicode_row = [x.decode('utf8') for x in utf8_row]
                        unicode_rows.append(unicode_row)

            return tuple(unicode_rows)

        except IOError:
            raise IOError("CSV file not found!")

        except TypeError:
            raise TypeError("CSV file not found!")


    def get_template_html(self):
        """return path to default template in default location."""

        return os.path.join(self.script_path, "templates", "template.html")

    def get_ttg_keywords(self):
        """return a dictionary with line numbers and keywords converted to unicode."""

        ttg_keywords = self.find_ttg_keywords(self.template_ttg_rows)
        ttg_keywords_unicode = {index: self.convert_from_ttg_text(raw_string) for
                                index, raw_string in list(ttg_keywords.items())}

        return ttg_keywords_unicode

    def write_ttg(self):
        """
        Writes out a ttg.  Relies on the below class parameters:

        self.filepath = full destination path and filename
        self.ttg_replacements = dictionary of replacements and their destination line
            numbers
        self.ttg_file_list = the template ttg stored a tuple of lines
        self.ttg_template_keywords = dictionary of the keywords in the template and their
            line number
        """

        try:
            with open(self.filepath, "w") as ttg:
                for line_number, text in enumerate(self.template_ttg_rows, 1):
                    if line_number + 1 in list(self.template_ttg_keywords.keys()):
                        new_text = self.ttg_replacements[self.template_ttg_keywords[line_number
                                                                                    + 1]]
                        ttg.write("TextLength " +
                                  str(len(self.convert_to_ttg_text(new_text).split())) +
                                  "\n")
                    elif line_number in list(self.template_ttg_keywords.keys()):
                        new_text = self.ttg_replacements[self.template_ttg_keywords[line_number]]
                        ttg.write("Text " + self.convert_to_ttg_text(new_text) + "\n")
                    else:
                        ttg.write(text + "\n")
        except IOError:
            print("Skipping! Cannot write to this path.")
            # raise

    def run(self):
        """Generate the slates!"""

        self.csv_rows = self.read_unicode_csv_file()
        self.filepath_pattern = self.convert_output_tokens(self.output)
        self.template_ttg_rows = self.read_ttg_file() if self.template_ttg else []
        self.template_ttg_keywords = self.get_ttg_keywords() if self.template_ttg else {}

        # Print info for TTG template keywords
        if self.template_ttg:
            print("Found %s keywords in %s:" % (len(self.template_ttg_keywords),
                                                self.template_ttg))
            print(", ".join([keyword for _, keyword in
                             list(self.template_ttg_keywords.items())]))

        # Print info for CSV file
        print("Found %s rows in %s" % (len(self.csv_rows), self.csv_file))

        for row_number, row in enumerate(self.csv_rows):

            # Check for empty row
            if all(i == u'' for i in row):
                print(" ".join(["Skipping row", str(row_number + 1),
                                "- Empty row"]))
                continue

            # Skip the header row
            if (self.row_header - 1) == row_number:
                print(" ".join(["Header Row - Skipping row", str(row_number + 1)]))
                continue

            # Check for excluded rows
            if self.row_exclude:
                if row_number in self.list_offset(self.row_exclude, -1):
                    print(" ".join(["Matches Exclude - Skipping row", str(row_number + 1)]))
                    continue

            # Check for included rows
            if self.row_include:
                if row_number not in self.list_offset(self.row_include, -1):
                    print(" ".join(["Not Included - Skipping row", str(row_number + 1)]))
                    continue

            # Assemble replacement entries for output path
            filepath_replacements = {"column": [], "keyword": {}}

            filepath_replacements["column"] = [None if item == u'' else
                                               self.tidy_text(item) for item in row]

            filepath_replacements["keyword"] = {keyword: self.tidy_text(entry) for
                                                keyword, entry in zip(self.csv_rows[0], row)
                                                if entry != u''}

            # Check output file path has all necessary entries
            try:
                self.filepath = self.filepath_pattern.format(* filepath_replacements["column"],
                                                             ** filepath_replacements['keyword'])

            except (IndexError, KeyError):
                print("Skipping row", str(row_number + 1),
                      "- Could not assemble output path")
                continue

            # Check output filename against filter exclude
            if self.filter_exclude:
                if True in [fnmatch.fnmatch(self.filepath, arg) for arg in self.filter_exclude]:
                    print(" ".join(["Skipping", self.filename_no_ext(self.filepath)]))
                    continue

            # Check output filename against include argument
            if self.filter_include:
                if not any([fnmatch.fnmatch(self.filepath, arg) for arg in self.filter_include]):
                    print(" ".join(["Skipping", self.filename_no_ext(self.filepath)]))
                    continue

            print(" ".join(["Proceeding with", self.filename_no_ext(self.filepath)]))

            # Check for overwrite
            if self.template_ttg:
                exists = os.path.isfile(self.filepath)

                if exists:
                    print("%s already exists!" % self.filepath)

                if exists and self.force_overwrite:
                    pass
                if exists and self.skip_existing:
                    print("Skipping %s" % self.filepath)
                    continue
                if exists and not self.force_overwrite and not self.skip_existing:
                    self.reply = self.overwrite_query()

                    # Overwrite responses
                    if self.reply and self.reply == "y":
                        pass
                    if self.reply and self.reply == "n":
                        print("Skipping %s" % self.filepath)
                        continue
                    if self.reply and self.reply == "Y":
                        self.force_overwrite = True
                    if self.reply and self.reply == "N":
                        self.skip_existing = True
                        continue

            # Start writing out TTGs
            if self.template_ttg:
                print("".join(["Writing out ", self.filepath]))

                # Assemble dict using header row for keys and row entries
                # for the replacements
                self.ttg_replacements = {keyword: entry for keyword, entry in
                                         zip(self.csv_rows[self.row_header - 1],
                                             self.csv_rows[row_number])}

            if self.template_ttg and not self.dry_run:
                self.makedirs(self.filepath)  # Make output path if necessary
                self.write_ttg()

            # Append to results
            self.results.append(self.filepath)

        if self.csv_file and self.html:
            self.html_destination = os.path.join(self.common_path(self.results),
                                                 "copy_paster.html")
            ttg_filenames = [self.filename_no_ext(i) for i in self.results]

            print(" ".join(["Writing out", self.html_destination]))

            if not self.dry_run:
                self.makedirs(self.html_destination)
                self.write_html_page(self.template_html, self.html_destination, 40, ttg_filenames)

        print("Done!")


def create_parser():
    """Assemble parser of command line args."""

    parser = argparse.ArgumentParser(description="""generates TTG files using a
        template TTG file and CSV full of data to fill in fields.""",
                                     formatter_class=lambda prog:
                                     argparse.HelpFormatter(prog, max_help_position=40))

    parser.add_argument("csv_file",
                        help="""path of the CSV file""")
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
                                    metavar="NUMBERS",
                                    help="""row numbers to exclude in CSV""")
    filter_row_numbers.add_argument("--include-rows",
                                    metavar="NUMBERS",
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
                        default=os.path.join(os.getcwd(), "<5>_<6>_<4>.ttg"),
                        help="template for output file names""",
                        metavar="TEMPLATE",
                        type=validate_output_template)
    parser.add_argument("--version",
                        action="version",
                        help="print program version and exit",
                        version="%(prog)s " + __version__)

    return parser


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


def main():
    """Script that is run when called from the command line."""

    # Gather Args
    parser = create_parser()
    args = parser.parse_args()

    # Run the PySlater class
    pys = PySlater(
        csv_file=args.csv_file,
        dry_run=args.dry_run,
        filter_include=args.include,
        filter_exclude=args.exclude,
        force_overwrite=args.force_overwrite,
        html=not args.no_html,  # not inverts the bool of no_html
        output=args.output,
        row_header=args.header_row,
        row_include=args.include_rows,
        row_exclude=args.exclude_rows,
        skip_existing=args.skip_existing,
        template_ttg=args.ttg_template)

    pys.run()


if __name__ == "__main__":
    main()
