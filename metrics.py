"""
A set of calculations of AFD and other typical & extendable eye-tracking metrics
"""

import pandas as pd
import numpy as np
from math import sqrt

BUG1_TARGETS = \
    ["MineSweeperGui.updateCheat",
     "MineSweeperGui.updateCheat:Comment",
     "MineSweeperGui.resetButtons",
     "MineSweeperGui.resetButtons:Comment"]

BUG2_TARGETS = \
    ["MineSweeperBoard.generateMines(long Space)",
     "MineSweeperBoard.generateMines(long Space):Comment"]


"""
For each dataset in the processed_data directory, compute statistics for each phase.

The statistics are:
    1. 
"""

def compute_all_statistics():
    pass


"""
Return a subset of fixation_data that corresponds to the given phase.
Phases are 1-indexed.
    Phase 1: times before 1st 10 on-target fixations
    Phase 2: times after 1st 10 on-target fixations, but before the 1st edit
    Phase 3: times after 1st edit
"""


def query_phase_change_data(which_phase, which_participant, which_bug, phase_data_path, fixation_data_path):
    phase_data = pd.read_csv(phase_data_path)
    fixation_data = pd.read_csv(fixation_data_path)

    trial_info = phase_data[(phase_data["Participant"] == which_participant) &
                            (phase_data["Trial"] == which_bug)]

    if trial_info.empty:
        raise LookupError(
            "Did not find bug "+str(which_bug)+" for participant "+str(which_participant)
        )

    phase1_end = trial_info.loc["Time of first 10 consecutive on-target fixations (ms after epoch)", 0]

    phase2_end = trial_info.loc["Time of 1st significant edit (ms after epoch)"]

    if which_phase == 1:
        try:
            phase1_end_int = int(phase1_end)
        except ValueError:
            return fixation_data

        return fixation_data[fixation_data["fix_time"] < phase1_end_int]

    elif which_phase == 2:
        try:
            phase1_end_int = int(phase1_end)
        except ValueError:
            raise LookupError(
                "Phase 2 does not exist because phase 1 does not terminate"
            )

        try:
            phase2_end_int = int(phase2_end)
        except ValueError:
            return fixation_data[fixation_data["fix_time"] >= phase1_end_int]

        return fixation_data[(fixation_data["fix_time"] >= phase1_end_int) &
                             (fixation_data["fix_time"] < phase2_end_int)]

    elif which_phase == 3:
        try:
            phase2_end_int = int(phase2_end)
        except ValueError:
            raise LookupError(
                "Phase 3 does not exist because phase 2 does not terminate"
            )

        return fixation_data[fixation_data["fix_time"] >= phase2_end_int]

    raise ValueError(
        "Phase number must be 1, 2 or 3"
    )


"""
Compute AFD.
"""


def get_global_afd(data):
    return data["fix_dur"].mean()


"""
Get the AFD for a particular section.
"""


def get_subsection_afd(data, fieldname, area_name):
    return get_global_afd(
        data[data[fieldname] == area_name]
    )


"""
Get total fixation count
"""


def get_fixation_count(data):
    return len(data)


"""
Get total fixation count on a particular AOI
"""


def get_subsection_fx_count(data, fieldname, area_name):
    return len(data[data[fieldname] == area_name])


"""
Get average saccade length
"""


def get_avg_saccade_length(data):
    rows = list(data.iterrows())
    saccade_lengths = list()

    for i in range(len(rows) - 1):
        this_row, next_row = rows[i][1], rows[i+1][1]
        x_diff, y_diff = next_row.pixel_x - this_row.pixel_x, next_row.pixel_y - this_row.pixel_y
        saccade_lengths.append(sqrt(x_diff ** 2 + y_diff ** 2))

    return np.array(saccade_lengths).mean()


"""
Find the time at which some number of fixations on any target area have occurred.

Input: a DataFrame and a list of target functions that match a possible
    name in the DataFrame's 'function' field
"""


def detect_on_target_focus(data, target_functions, num_required):
    sequence = list(data['function'])
    times = list(data['fix_time'])
    found_loc = None

    for i in range(len(sequence) - num_required):
        if any(sequence[i: i+num_required] == [target] * num_required
               for target in target_functions):
            found_loc = i
            break

    if found_loc is not None:
        return times[found_loc]
    else:
        return "Pattern not found!"
