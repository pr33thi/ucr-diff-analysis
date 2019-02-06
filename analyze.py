import os
import argparse
import csv


def parse_args():
    parser = argparse.ArgumentParser(description='Analyze UCR diff results')
    parser.add_argument('--log', dest='log_filename', required=True,
                        help='File in the log/ directory to analyze')
    parser.add_argument('--o', dest='output_file', required=False,
                        help='output csv name', default='analysis.csv')
    args = parser.parse_args()
    return args

def parse_log_file(args):
    """
    Parse each row of the log file into a list, and add it to a list containing all entries
    :param args: Command line args
    :return: The list of lists of parsed rows
    """
    full_diff = []
    log_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log')
    log_file = os.path.join(log_file_dir, args.log_filename)
    with open(log_file, 'r') as file:
        log_file = file.readlines()
        for index, log_line in enumerate(log_file):
            full_diff.append(eval(log_line.split('\t')[-1].replace("null", "None")))
    return full_diff

def initialize_csv(args):
    """
    Create the csv and add in the headers
    :param args: Command line args
    """
    with open(args.output_file, mode='w') as output_file:
        output_writer = csv.writer(output_file, delimiter=',')
        output_writer.writerow(['index #', 'completely_different', 'i_total_records_diff', 'total_row_diff'])

def analyze_ucr_diff(args, full_diff):
    """
    Definitions of info in the diff (to see the report, go to this icds report:
    https://india.commcarehq.org/a/icds-dashboard-qa/reports/configurable/static-icds-dashboard-qa-static-mpr_5_child_health_cases_v2/
    and click apply):
    - `aaData`: Each header that is different, and the # it is off by
    - `total_row`: How much each total is off by (has the same #s as aaData)
    - `iTotalRecords`: The difference in total # of records (in this case, # of AWCs the query matched)
    -----
    Analyze the diff and write it as an entry to the csv file
    :param args: Command line args
    :param full_diff: The list of lists of parsed rows
    """
    i_total_records_diff = 0
    total_row_diff = 0
    for index, diff_line in enumerate(full_diff):
        completely_different = _is_completely_different(diff_line)
        if not completely_different:
            i_total_records_diff = _get_i_total_records_diff(diff_line)
            total_row_diff = _get_total_row_diff(diff_line)
        _append_to_csv(args, csv_row=[index, completely_different, i_total_records_diff, total_row_diff])

def _append_to_csv(args, csv_row):
    """
    Append a row to the csv
    :param args: Command line args
    :param csv_row: The row of data to be appended
    """
    with open(args.output_file, mode='a') as fd:
        analysis_writer = csv.writer(fd, delimiter=',')
        analysis_writer.writerow(csv_row)

def _is_completely_different(diff_line):
    """
    Calculate whether the diff is completely different
    :param diff_line: The line of the diff that is being analyzed
    :return: Boolean that says whether it is completely different or not
    """
    if not diff_line[0][0]:
        return True
    return False

def _get_i_total_records_diff(diff_line):
    """
    Gets the diff in total records (ie number of AWC's)
    :param diff_line: The line of the diff that is being analyzed
    :return: The difference in total records (if no entry is found, returns 0 by default)
    """
    if len(diff_line) >= 2:
        if diff_line[1][0][0] == 'iTotalRecords':
            return diff_line[1][1]
    return 0

def _get_total_row_diff(diff_line):
    """
    Gets the diff in the row of 'Totals' at the bottom of the report
    :param diff_line: The line of the diff that is being analyzed
    :return: The difference in the 'Totals' row of the report (if no entry is found, returns 0 by default)
    """
    if diff_line[-1][0][0] == 'total_row':
        return diff_line[-1]
    return 0

if __name__ == "__main__":
    args = parse_args()
    full_diff = parse_log_file(args)
    initialize_csv(args)
    analyze_ucr_diff(args, full_diff)
