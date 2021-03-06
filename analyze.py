import os
import argparse
import csv


def parse_args():
    parser = argparse.ArgumentParser(description='Analyze UCR diff results')
    parser.add_argument('--log', dest='log_filename', required=True,
                        help='File in the log/ directory to analyze')
    parser.add_argument('--o', dest='output_file', required=False,
                        help='output csv name', default='analysis_golden.csv')
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
            full_diff.append({"filters": log_line.split('\t')[3].replace("null", "None"),
                              "candidate_diff": eval(log_line.split('\t')[5].replace("null", "None")),
                              "control_values": eval(log_line.split('\t')[4].replace("null", "None")),
                              "report_config_id": log_line.split('\t')[2]})
    return full_diff


def initialize_csv(args):
    """
    Create the csv and add in the headers
    :param args: Command line args
    """
    with open(args.output_file, mode='w') as output_file:
        output_writer = csv.writer(output_file, delimiter=',')
        output_writer.writerow(["Log file: {}".format(args.log_filename)])
        output_writer.writerow(['index #', 'report_config_id',
                                'completely_different',
                                'i_total_records_diff',
                                'total_row_diff_indices',
                                'total_row_candidate_diff',
                                'total_row_control_values',
                                'candidate diff - control value',
                                'filters'])


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
    for index, diff in enumerate(full_diff):
        candidate_diff = diff['candidate_diff']
        control_values = diff['control_values']
        completely_different = _is_completely_different(candidate_diff)
        if not completely_different:
            total_row_diff = _get_total_row_diff(candidate_diff, control_values)
        _append_to_csv(args, csv_row=[index, diff['report_config_id'], completely_different,
                                      _get_i_total_records_diff(candidate_diff), total_row_diff['indices'],
                                      total_row_diff['candidate_diff'],
                                      total_row_diff['control_values'],
                                      total_row_diff['candidate_control_diff'],
                                      diff['filters']])


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


def _get_total_row_diff(candidate_diff, control_values):
    """
    Gets the diff in the row of 'Totals' at the bottom of the report
    :param candidate_diff: The line of the diff that is being analyzed
    :return: The difference in the 'Totals' row of the report (if no entry is found, returns 0 by default)
    """
    total_row_diff = {'candidate_diff': [], 'control_values': [], 'indices': [], 'candidate_control_diff': []}
    for candidate_diff_entry in candidate_diff:
        if candidate_diff_entry[0][0] == 'total_row':
            _extract_values_from_total_row(total_row_diff, candidate_diff_entry, control_values['total_row'])
    return total_row_diff


def _extract_values_from_total_row(total_row_diff, candidate_diff_entry, control_values_entry):
    try:
        diff_index = candidate_diff_entry[0]
        diff_value = candidate_diff_entry[1]
    except IndexError:
        _append_to_diff(total_row_diff,
                        "Malformed total_row: {}".format(candidate_diff_entry), "", "")
    if len(diff_index) == 1:
        # If the whole row is returned, append all nonzero entries
        for index, nonzero_candidate_diff in enumerate(diff_value[1:]):
            if nonzero_candidate_diff:
                _append_to_diff(total_row_diff, index, nonzero_candidate_diff, control_values_entry[1])

    else:  # only certain entries are returned
        _append_to_diff(total_row_diff, diff_index[1], diff_value, control_values_entry[diff_index[1]])
    return total_row_diff


def _append_to_diff(diff, index, candidate_diff, control_value):
    control_value = int(control_value)
    diff['indices'].append(index)
    diff['candidate_diff'].append(candidate_diff)
    diff['control_values'].append(control_value)
    diff['candidate_control_diff'].append(candidate_diff - control_value)


if __name__ == "__main__":
    args = parse_args()
    full_diff = parse_log_file(args)
    initialize_csv(args)
    analyze_ucr_diff(args, full_diff)
