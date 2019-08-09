"""
Cluster scanpaths with various algorithms from scikit-learn
"""

import csv
import numpy as np
import pandas as pd
from sklearn.cluster import AffinityPropagation, SpectralClustering


def sum_measure(row): return sum([float(row[name]) for name in
                                 ['Shape', 'Length', 'Direction', 'Position', 'Duration']])


def sum_of_squares_measure(row): return sum([float(row[name])**2 for name in
                                            ['Shape', 'Length', 'Direction', 'Position', 'Duration']])


def length_measure(row): return float(row['Length'])


def position_measure(row): return float(row['Position'])


def duration_measure(row): return float(row['Duration'])


"""
REQUIRES: path_to_file is the relative path to a CSV file
    containing fields for subject 1, subject 2 and the scores 
    from comparing the two with multi-match. 

EFFECT: Returns a dataframe representing the CSV.
"""


def ingest_data(path_to_file):
    return pd.read_csv(path_to_file)


"""
EFFECT: Processes the two participant columns and returns 
    a list of unique participants
"""


def get_unique_participants(data):
    participants = set(data['Part1_ID'])
    participants.update(set(data['Part2_ID']))

    return list(participants)


"""
Evaluate the given clustering method's predictive ability.

Note: clusters were done by phase/bug, so only clustering schemes with
matching phase/bug pairs should be evaluated as a unit.

Answer question:
    In general, when we run the clustering algorithm, how "good" is it at
    picking out two groups? The more groups are created, the worse
"""


def evaluate_clustering(cluster_data_file):
    data = pd.read_csv(cluster_data_file)
    data = data[data["Cluster Type"] == "Spectral Clustering"]

    for bug in [1, 2]:
        for phase in [1, 2, 3]:
            print("Bug " + str(bug) + " Phase " + str(phase))

            cluster_data = data[(data["Bug Number"] == bug) &
                                (data["Phase Number"] == phase)]

            cluster_nums = cluster_data["Cluster Category"].unique()

            for cluster_num in cluster_nums:
                category = cluster_data[cluster_data["Cluster Category"] == cluster_num]
                num_m = len(category[category["Gender"] == "M"])
                num_f = len(category[category["Gender"] == "F"])
                print("\t" + str(cluster_num) + " = M: " + str(num_m) + "/" + str(len(category)) + "\t" +
                      str(cluster_num) + " = F: " + str(num_f) + "/" + str(len(category)))


"""
Record metadata to the cluster information file
"""


def append_metadata(data_file, metadata_file, output_file):
    metadata = pd.read_csv(metadata_file)
    metadata_fields = ["Gender", "Group"]

    with open(data_file, "r") as infile:
        icsv = csv.DictReader(infile)

        with open(output_file, "w", newline='') as ofile:
            ocsv = csv.DictWriter(
                ofile,
                fieldnames=icsv.fieldnames+metadata_fields
            )
            ocsv.writeheader()

            for row in icsv:
                pid = row["PID"]
                metadata_row = metadata[metadata.PID == pid]
                gender = metadata_row.Gender.values[0]
                group = metadata_row.Group.values[0]

                out_row = dict(row)
                out_row["Gender"] = gender
                out_row["Group"] = group

                ocsv.writerow(out_row)


"""
Record cluster information to a file
"""


def record_clusters(data_file_list, output_file_path, n_clusters, which_measure):
    fields = [
        "PID",
        "Bug Number",
        "Phase Number",
        "Cluster Type",
        "Cluster Category"
    ]

    pid_clusters = dict()

    for data_file in data_file_list:
        bug_number = int(data_file.split("_")[0][1])
        phase_number = int(data_file.split("_")[1][1])

        data = ingest_data(data_file)

        for pid in get_unique_participants(data):
            if pid not in pid_clusters.keys():
                pid_clusters[pid] = dict()

        """
        ap_cluster = create_participant_cluster(
            "AffinityPropagation", data, default_measure
        )

        for pid, cluster in ap_cluster.items():
            if "AP" not in pid_clusters[pid].keys():
                pid_clusters[pid]["AP"] = dict()
            pid_clusters[pid]["AP"][bug_number, phase_number] = cluster
        """

        sc_cluster = create_participant_cluster(
            "SpectralClustering", data, which_measure, n_clusters
        )

        for pid, cluster in sc_cluster.items():
            if "SC" not in pid_clusters[pid].keys():
                pid_clusters[pid]["SC"] = dict()
            pid_clusters[pid]["SC"][bug_number, phase_number] = cluster

    with open(output_file_path, "w", newline='') as ofile:
        ocsv = csv.DictWriter(ofile, fieldnames=fields)
        ocsv.writeheader()

        for pid, clusters in pid_clusters.items():
            for cluster_type, trials in clusters.items():
                for bug_phase_pair, cluster_number in trials.items():
                    ocsv.writerow({
                        "PID": pid,
                        "Bug Number": bug_phase_pair[0],
                        "Phase Number": bug_phase_pair[1],
                        "Cluster Type": "Affinity Propagation" if cluster_type == "AP" else "Spectral Clustering",
                        "Cluster Category": cluster_number
                    })


"""
REQUIRES: 
    data = A pandas dataframe similar to one derived from ingest_data
    
    subject_order = a list of subjects to cluster from this data
        (this will be used to set the matrix ordering)

    measure = a lambda that computes a compounded similarity score given a
        dictionary-like object with any of the multi-match measures
        as keys.
        
        example: measure = lambda row: row["score1"]**2 + row["score2"]

EFFECT: Creates a clustering of scanpaths based on similarity.
"""


def create_participant_cluster(which_algorithm, data, measure, n_clusters):
    subject_order = get_unique_participants(data)
    affinity = create_affinity_matrix(data, subject_order, measure)

    if which_algorithm == "AffinityPropagation":
        cluster = AffinityPropagation(affinity='precomputed').fit(affinity)

    elif which_algorithm == "SpectralClustering":
        cluster = SpectralClustering(affinity='precomputed', n_clusters=n_clusters).fit(affinity)

    else:
        raise ValueError(
            "which_algorithm must be either 'AffinityPropagation' or "
            "'SpectralClustering'."
        )

    return dict(zip(subject_order, cluster.labels_))


def create_affinity_matrix(data, subject_order, measure):
    size = len(subject_order)
    affinity = np.ones((size, size))

    for i in range(size):
        for j in range(i+1, size):
            # Self-comparisons will all be 1
            if i == j:
                continue

            # Get the row that matches subjects i and j
            s_i, s_j = subject_order[i], subject_order[j]
            row = data[(data.Part1_ID == s_i) & (data.Part2_ID == s_j)]

            if len(row) == 0:
                row = data[(data.Part2_ID == s_i) & (data.Part1_ID == s_j)]

            if len(row) == 0:
                raise LookupError("Did not find comparison between "+s_i+" and "+s_j)

            affinity[i][j] = affinity[j][i] = measure(row)

    return affinity
