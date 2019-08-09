"""
Analyze MultiMatch data without clustering
"""

import pandas as pd
from copy import deepcopy


"""
Split the data between same/different gender comparisons.
"""


def split_by_gender_comparison(data_filepath, metadata_filepath):
    data, metadata = pd.read_csv(data_filepath), pd.read_csv(metadata_filepath)
    same_data, diff_data = [pd.DataFrame(columns=data.columns) for i in range(2)]

    for row_number, row_content in data.iterrows():
        pid_1, pid_2 = row_content.Part1_ID, row_content.Part2_ID

        meta_1, meta_2 = [metadata[metadata.participant == pid] for pid in [pid_1, pid_2]]

        gender_1, gender_2 = [meta.gender.values[0] for meta in [meta_1, meta_2]]

        if gender_1 == gender_2:
            same_data = same_data.append(deepcopy(row_content))
        else:
            diff_data = diff_data.append(deepcopy(row_content))

    return same_data, diff_data


"""
Get the mean and stdev of MultiMatch metrics for each bug / phase.

phase_comparisons: list of files containing similarity scores by phase
bug_comparisons: list of files containing similarity scores by bug
"""


def get_mean_stdev_of_comparisons(phase_comparisons, bug_comparisons, metadata_fpath):
    for phase_comp_file in phase_comparisons:
        bug_name = phase_comp_file.split("_")[-4][-1]
        phase_name = phase_comp_file.split("_")[-3][-1]

        same_data, diff_data = split_by_gender_comparison(phase_comp_file, metadata_fpath)
        print("Bug " + str(bug_name) + " Phase " + str(phase_name))
        report_mean_stdev(same_data, diff_data)

    for bug_comp_file in bug_comparisons:
        bug_name = bug_comp_file.split("_")[-3][-1]

        same_data, diff_data = split_by_gender_comparison(bug_comp_file, metadata_fpath)
        print("Bug " + str(bug_name) + " All Phases")
        report_mean_stdev(same_data, diff_data)


def report_mean_stdev(same_data, diff_data):
    same_data_measures, diff_data_measures = \
        [data[['Shape', 'Length', 'Direction', 'Position', 'Duration']]
         for data in [same_data, diff_data]]

    print("\tSame gender mean:")
    print(same_data_measures.mean())
    print("\tSame gender stdev:")
    print(same_data_measures.std())
    print("\tDifferent gender mean:")
    print(diff_data_measures.mean())
    print("\tDifferent gender stdev:")
    print(diff_data_measures.std())