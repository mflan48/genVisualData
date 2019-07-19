"""
Cluster scanpaths with various algorithms from scikit-learn
"""

import numpy as np
import pandas as pd
from sklearn.cluster import AffinityPropagation, SpectralClustering

"""
REQUIRES: path_to_file is the relative path to a CSV file
    containing fields for subject 1, subject 2 and the scores 
    from comparing the two with multi-match. 

EFFECT: Returns a dataframe representing the CSV.
"""
def ingest_data(path_to_file):
    return pd.DataFrame.from_csv(path_to_file)


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
def create_participant_cluster(which_algorithm, data, subject_order, measure):
    affinity = create_affinity_matrix(data, subject_order, measure)

    if which_algorithm == "AffinityPropagation":
        cluster = AffinityPropagation(affinity='precomputed').fit(affinity)

    elif which_algorithm == "SpectralClustering":
        cluster = SpectralClustering(affinity='precomputed').fit(affinity)

    else:
        raise ValueError(
            "which_algorithm must be either 'AffinityPropagation' or "
            "'SpectralClustering'."
        )

    return cluster.labels_

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
            row = data[data.s1 == s_i & data.s2 == s_j]
            if len(row) == 0:
                row = data[data.s2 == s_i & data.s1 == s_j]

            affinity[i][j] = affinity[j][i] = measure(row)

    return affinity
