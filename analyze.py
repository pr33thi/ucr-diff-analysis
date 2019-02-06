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
    full_diff = []
    log_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log')
    log_file = os.path.join(log_file_dir, args.log_filename)
    with open(log_file, 'r') as file:
        log_file = file.readlines()
        for index, log_line in enumerate(log_file):
            full_diff.append(eval(log_line.split('\t')[-1].replace("null", "None")))
    return full_diff

def create_csv(args):
    with open(args.output_file, mode='w') as output_file:
        output_writer = csv.writer(output_file, delimiter=',')
        output_writer.writerow(['index #', 'completely_different', 'i_total_records_diff', 'total_row_diff'])

def analyze_ucr_diff(args, full_diff):
    i_total_records_diff = 0
    total_row_diff = 0
    for index, diff_line in enumerate(full_diff):
        completely_different = is_completely_different(diff_line)
        if not completely_different:
            i_total_records_diff = get_i_total_records_diff(diff_line)
            total_row_diff = get_total_row_diff(diff_line)
        _append_to_csv(args, csv_row=[index, completely_different, i_total_records_diff, total_row_diff])

def _append_to_csv(args, csv_row):
    with open(args.output_file, mode='a') as fd:
        analysis_writer = csv.writer(fd, delimiter=',')
        analysis_writer.writerow(csv_row)

def is_completely_different(diff_line):
    if not diff_line[0][0]:
        return True
    return False

def get_i_total_records_diff(diff_line):
    if len(diff_line) >= 2:
        if diff_line[1][0][0] == 'iTotalRecords':
            return diff_line[1][1]
    return 0

def get_total_row_diff(diff_line):
    if diff_line[-1][0][0] == 'total_row':
        return diff_line[-1]
    return 0

if __name__ == "__main__":
    args = parse_args()
    full_diff = parse_log_file(args)
    create_csv(args)
    analyze_ucr_diff(args, full_diff)
