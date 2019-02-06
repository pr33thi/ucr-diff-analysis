import os
import argparse
import csv


def parse_args():
    parser = argparse.ArgumentParser(description='Analyze UCR diff results')
    parser.add_argument('--log', dest='log_filename', required=True,
                        help='Cloudant username')
    args = parser.parse_args()
    return args

def parse_diff_file(args):
    full_diff = []
    log_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log')
    log_file = os.path.join(log_file_dir, args.log_filename)
    with open(log_file, 'r') as file:
        log_file = file.readlines()
        for index, log_line in enumerate(log_file):
            full_diff.append(eval(log_line.split('\t')[-1].replace("null", "None")))
    return full_diff

def analyze_ucr_diff(full_diff):
    for diff_line in full_diff:
        completely_different = is_completely_different(diff_line)
        if not completely_different:
            i_total_records_diff = get_i_total_records_diff(diff_line)
            total_row_diff = get_total_row_diff(diff_line)
        dummy = 5

def is_completely_different(diff_line):
    if diff_line[0][0] == []:
        return True

def get_i_total_records_diff(diff_line):
    if diff_line[1][0][0] == 'iTotalRecords':
        return diff_line[1][0][1]

def get_total_row_diff(diff_line):
    if diff_line[-1][0][0] == 'total_row':
        return diff_line[-1]

if __name__=="__main__":
    args = parse_args()
    full_diff = parse_diff_file(args)

    only_some_diff = []
    for diff_line in full_diff:
        if not is_completely_different(diff_line):
            only_some_diff.append(diff_line)

    analyze_ucr_diff(full_diff)
