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


def triple_split_by_gender_comparison(data_filepath, metadata_filepath):
    data, metadata = pd.read_csv(data_filepath), pd.read_csv(metadata_filepath)
    male_data, female_data, diff_data = [pd.DataFrame(columns=data.columns) for i in range(3)]

    for row_number, row_content in data.iterrows():
        pid_1, pid_2 = row_content.Part1_ID, row_content.Part2_ID

        meta_1, meta_2 = [metadata[metadata.participant == pid] for pid in [pid_1, pid_2]]

        gender_1, gender_2 = [meta.gender.values[0] for meta in [meta_1, meta_2]]

        if gender_1 == gender_2 and gender_1 == "Male":
            male_data = male_data.append(deepcopy(row_content))
        elif gender_1 == gender_2 and gender_1 == "Female":
            female_data = female_data.append(deepcopy(row_content))
        else:
            diff_data = diff_data.append(deepcopy(row_content))

    return male_data, female_data, diff_data


"""
Get the mean and stdev of MultiMatch metrics for each bug / phase.

phase_comparisons: list of files containing similarity scores by phase
bug_comparisons: list of files containing similarity scores by bug
"""


def get_mean_stdev_of_comparisons(phase_comparisons, bug_comparisons, metadata_fpath, three_groups=False):
    for phase_comp_file in phase_comparisons:
        bug_name = phase_comp_file.split("_")[-4][-1]
        phase_name = phase_comp_file.split("_")[-3][-1]

        print("Bug " + str(bug_name) + " Phase " + str(phase_name))

        if three_groups:
            m_data, f_data, diff_data = triple_split_by_gender_comparison(phase_comp_file, metadata_fpath)
            report_triple_maen_stdev(m_data, f_data, diff_data)

        else:
            same_data, diff_data = split_by_gender_comparison(phase_comp_file, metadata_fpath)
            report_mean_stdev(same_data, diff_data)

    for bug_comp_file in bug_comparisons:
        bug_name = bug_comp_file.split("_")[-3][-1]

        print("Bug " + str(bug_name) + " All Phases")

        if three_groups:
            m_data, f_data, diff_data = triple_split_by_gender_comparison(bug_comp_file, metadata_fpath)
            report_triple_maen_stdev(m_data, f_data, diff_data)

        else:
            same_data, diff_data = split_by_gender_comparison(bug_comp_file, metadata_fpath)
            report_mean_stdev(same_data, diff_data)


def report_mean_stdev(same_data, diff_data):
    same_data_measures, diff_data_measures = \
        [data[['Shape', 'Length', 'Direction', 'Position', 'Duration']]
         for data in [same_data, diff_data]]

    print("\tSame gender mean:")
    print(same_data_measures.mean())
    print("\tSame gender median:")
    print(same_data_measures.median())
    print("\tSame gender stdev:")
    print(same_data_measures.std())

    print("\tDifferent gender mean:")
    print(diff_data_measures.mean())
    print("\tDifferent gender median:")
    print(diff_data_measures.median())
    print("\tDifferent gender stdev:")
    print(diff_data_measures.std())


def report_triple_maen_stdev(male_data, female_data, diff_data):
    male_data_measures, female_data_measures, diff_data_measures = \
        [data[['Shape', 'Length', 'Direction', 'Position', 'Duration']]
         for data in [male_data, female_data, diff_data]]

    print("\tM-M mean:")
    print(male_data_measures.mean())
    print("\tM-M median:")
    print(male_data_measures.median())
    print("\tM-M stdev:")
    print(male_data_measures.std())

    print("\tF-F mean:")
    print(female_data_measures.mean())
    print("\tF-F median:")
    print(female_data_measures.median())
    print("\tF-F stdev:")
    print(female_data_measures.std())

    print("\tDifferent gender mean:")
    print(diff_data_measures.mean())
    print("\tDifferent gender median:")
    print(diff_data_measures.median())
    print("\tDifferent gender stdev:")
    print(diff_data_measures.std())
