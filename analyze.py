import os

log_filename = 'celery1-ucr_diff.log'
competely_different_indices = []
i_total_records_diff_indices = []
very_high_value_indices = []

very_high_value = 4

log_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log')
log_file = os.path.join(log_file_dir, log_filename)
with open (log_file, 'r') as file:
    log_file = file.readlines()
    for index, log_line in enumerate(log_file):
        full_diff = eval(log_line.split('\t')[-1])

        # If the [0][0] index is an empty list, then the inputs were completely different
        if not full_diff[0][0]:
            competely_different_indices.append(index)
        else:
            for diff_entry in full_diff:
                # If there was any difference in iTotalRecords
                if diff_entry[0][0] == 'iTotalRecords':
                    i_total_records_diff_indices.append(index)
                    break
                if float(diff_entry[1]) > very_high_value:
                    very_high_value_indices.append(index)

print("competely_different_indices: {}".format(competely_different_indices))
print("i_total_records_diff_indices: {}".format(i_total_records_diff_indices))
print("very_high_value_indices: {}".format(very_high_value_indices))


# Heuristics

# len(diff)
# another could be `iTotalRecords` being different,
# another could be there being a large difference between one of the columns, like the candidate has a value of 1 and the control has a value of 1000
