"""
A set of calculations of AFD and other typical & extendable eye-tracking metrics
"""

import os
import csv
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


class PhaseQueryError(BaseException):
    pass


"""
For each dataset in the processed_data directory, compute statistics for each phase.

The statistics are:
    1. Fixation count
    2. Average fixation rate (count / s)
    3. Average fixation duration (ms)
    4. Fixation/saccade ratio (no units)
    5. Average saccade length (px)
    6. Average saccade velocity (px / s)

    Regression count is not included.
"""


def compute_all_statistics(output_path):
    phase_data_path = "phase_changes.csv"

    subject_fields = [
        "PID", "Bug Number", "Phase Number"
    ]

    stats_fields = [
        "FxCount",
        "FxRate_count_s",
        "AvgFxDuration_ms",
        "FxScRatio",
        "AvgScLength_px",
        "AvgScVelocity_px_s"
    ]

    data_dirs = os.listdir("processed_data")

    with open(output_path, "w", newline='') as ofile:
        ocsv = csv.DictWriter(ofile, fieldnames=subject_fields + stats_fields)
        ocsv.writeheader()

        for data_dir in data_dirs:
            pid = "P" + data_dir.split("_")[0][-3:]
            bug_number = int(data_dir.split("_")[1][-1])
            fixation_data_path = "processed_data/"+data_dir+"/merged_data.csv"

            for phase_number in [1, 2, 3]:
                try:
                    phase_data = query_phase_change_data(
                        phase_number, pid, bug_number, phase_data_path, fixation_data_path)
                except PhaseQueryError:
                    continue

                if phase_data.empty:
                    continue

                fixation_count = get_fixation_count(phase_data)
                fixation_rate = get_fixation_rate(phase_data)
                afd = get_afd(phase_data)
                fs_ratio = get_fixation_saccade_ratio(phase_data)
                avg_saccade_length = get_avg_saccade_length(phase_data)
                avg_saccade_velocity = get_avg_saccade_velocity(phase_data)

                ocsv.writerow({
                    "PID": pid,
                    "Bug Number": bug_number,
                    "Phase Number": phase_number,
                    "FxCount": fixation_count,
                    "FxRate_count_s": fixation_rate,
                    "AvgFxDuration_ms": afd,
                    "FxScRatio": fs_ratio,
                    "AvgScLength_px": avg_saccade_length,
                    "AvgScVelocity_px_s": avg_saccade_velocity
                })


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
        raise PhaseQueryError(
            "Did not find bug "+str(which_bug)+" for participant "+str(which_participant)
        )

    phase1_end = trial_info["Time of first 10 consecutive on-target fixations (ms after epoch)"].values[0]

    phase2_end = trial_info["Time of 1st significant edit (ms after epoch)"].values[0]

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
            raise PhaseQueryError(
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
            raise PhaseQueryError(
                "Phase 3 does not exist because phase 2 does not terminate"
            )

        return fixation_data[fixation_data["fix_time"] >= phase2_end_int]

    raise ValueError(
        "Phase number must be 1, 2 or 3"
    )


"""
Compute AFD.
"""


def get_afd(data):
    return data["fix_dur"].mean() / float(10 ** 6)  # Note: duration is in nanoseconds


"""
Compute fixation rate.
"""


def get_fixation_rate(data):
    first_time = data["fix_time"].values[0]
    last_time = data["fix_time"].values[-1]
    duration_seconds = (last_time - first_time) / 1000.0  # Note: time is in milliseconds
    return get_fixation_count(data) / float(duration_seconds)


"""
Compute the fixation : saccade time ratio.
"""


def get_fixation_saccade_ratio(data):
    fixation_ms, saccade_ms = 0, 0
    rows = list(data.iterrows())

    for i in range(len(rows) - 1):
        this_row, next_row = rows[i][1], rows[i+1][1]
        row_time_diff = next_row.fix_time - this_row.fix_time
        fx_duration = this_row.fix_dur / float(10 ** 6)   # Note: duration is in nanoseconds
        sc_duration = row_time_diff - fx_duration

        if sc_duration <= 0:
            continue

        fixation_ms += fx_duration
        saccade_ms += sc_duration

    fixation_ms += rows[-1][1].fix_dur

    return fixation_ms / float(saccade_ms)


"""
Return average saccade velocity, as euclidean distance divided by time.
"""
def get_avg_saccade_velocity(data):
    speeds = list()
    rows = list(data.iterrows())

    for i in range(len(rows) - 1):
        this_row, next_row = rows[i][1], rows[i + 1][1]
        row_time_diff = next_row.fix_time - this_row.fix_time
        fx_duration_ms = this_row.fix_dur / float(10 ** 6)  # Note: duration is in nanoseconds
        sc_duration_seconds = (row_time_diff - fx_duration_ms) / 1000.0

        if sc_duration_seconds < 0:
            continue

        x_diff, y_diff = abs(next_row.pixel_x - this_row.pixel_x), abs(next_row.pixel_y - this_row.pixel_y)
        saccade_length = sqrt((x_diff ** 2) + (y_diff ** 2))

        saccade_speed = saccade_length / sc_duration_seconds
        speeds.append(saccade_speed)

    return np.array(speeds).mean()

"""
Get the AFD for a particular section.
"""


def get_subsection_afd(data, fieldname, area_name):
    return get_afd(
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
Get average saccade length, as Euclidean distance.
"""


def get_avg_saccade_length(data):
    rows = list(data.iterrows())
    saccade_lengths = list()

    for i in range(len(rows) - 1):
        this_row, next_row = rows[i][1], rows[i+1][1]
        x_diff, y_diff = abs(next_row.pixel_x - this_row.pixel_x), abs(next_row.pixel_y - this_row.pixel_y)
        saccade_lengths.append(sqrt((x_diff ** 2) + (y_diff ** 2)))

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
