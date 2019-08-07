#!/usr/bin/env python

"""
Generates .ttg files for Autodesk Flame using data from a CSV file.
"""

import argparse
import csv
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
    parser.add_argument("ttg_template", help="""path of the template TTG file""")
    parser.add_argument("csv_file", help="""path of the CSV file""")
    parser.add_argument("-u", "--underscores", action="store_true",
                        help="""replace spaces and illegal characters in output filenames""")
    args = parser.parse_args()

    # Gather keywords in TTG file
    ttg_file_list = read_ttg_file(args.ttg_template)
    ttg_keywords = find_ttg_keywords(ttg_file_list)

    unicode_keywords = {index: convert_from_ttg_text(raw_string) for index,
                        raw_string in ttg_keywords.items()}
    print "Found %s keywords in the TTG template:" % len(unicode_keywords)
    print ", ".join([keyword for line_number, keyword in unicode_keywords.iteritems()])

    # Sort out csv
    csv_rows = read_unicode_csv_file(args.csv_file)

    # Start writing out ttgs
    print "Found %s rows in the CSV file." % len(csv_rows)
    TTG_FILENAMES = []
    for i, row in enumerate(csv_rows[1:]): #skip header row and start at 1
        filename = "_".join([tidy_text(row[5]), tidy_text(row[6]),
                             tidy_text(row[4])])
        TTG_FILENAMES.append(filename)
        print "".join(["Writing out ", filename, ".ttg"])

        # Assemble dict of keywords and entries for the replacements
        line_replacements = {keyword: entry for keyword, entry in
                             zip(csv_rows[0], csv_rows[1:][i])}

        with open(".".join([filename, "ttg"]), "w") as f:
            for line_number, text in enumerate(ttg_file_list, 1):
                if line_number + 1 in unicode_keywords.keys():
                    new_text = line_replacements[unicode_keywords[line_number
                                                                  + 1]]
                    f.write("TextLength " +
                            str(len(convert_to_ttg_text(new_text).split())) +
                            "\n")
                elif line_number in unicode_keywords.keys():
                    new_text = line_replacements[unicode_keywords[line_number]]
                    f.write("Text " + convert_to_ttg_text(new_text) + "\n")
                else:
                    f.write(text + "\n")
        
    generate_html_page("template.html", "copy_paster.html", 40, TTG_FILENAMES) 
    print "".join(["Writing out ", "copy_paster.html"])

    print "Done!"

if __name__ == "__main__":
    main()
