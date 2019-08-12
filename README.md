# Description
This project contains scripts to create various data files/analyses for our experiment:
1) Write the files need to create graphics and run the MultiMatch tool for all the participants. 
2) Calculate distribution and transition matrices for each of the phases for all of the participants
3) Calculate conventional eye-tracking metrics based on fixations and saccades.
4) Given similarity scores from MultiMatch, separate participants into clusters.

## **genAllPhases.py**
### _Description_

For our experiment, we split the fixation data into three _phases_:
1) Finding initial focus points 
2) Building on those points 
3) Fixing the bug. 

This script will separate the data into groups for each bug and for each phase in each bug. For each of those, it will create files to generate the following graphics and computations: [alpscarf tool](https://github.com/Chia-KaiYang/alpscarf), [radial transition graph tool](http://www.rtgct.fbeck.com/), scatter plots, and [MultiMatch tool](https://multimatch.readthedocs.io/en/latest/index.html).
It creates these csv files from the `merged_data.csv` file that is created by the [iTrace-post project](https://github.com/ianbtr/iTrace-post).

This script will also create Distribution and Transition csv files for each of the bugs for all of the participants. The Distribution csv file contains the percentage of time the participant spent on each of the software entities listed below for each of the three phases. The Transition csv file contains a transition matrix between each of the entities for each phase for all of the participants.

1) Comments
2) Method_Body
3) Member_Variable
4) Bug_Report
5) Class_Signature
6) Method_Signature

### _Requirements_

This program requires a path to a **_processed_data_** directory that contains all of the output files from iTrace-post.
This directory must have the following structure:

```bash
processed_data/
├── P100
│   ├── bug1
│   │   └── merged_data.csv
│   └── bug2
│       └── merged_data.csv
├── P101
│   ├── bug1
│   │   └── merged_data.csv
│   └── bug2
│       └── merged_data.csv
├── Rest of Participants...
```
* Note: If a certain participant does not have any data for a specific bug, the subdirectory for that bug is not required.

In order to split the data up by phases, two epoch times (ms) are needed to distinguish the three stages. These times should be located in a **_CSV file_** with the following header

`Participant,Trial,endPhase1,endPhase2`

The program also creates **_two output directories_**, one for each bug. These directories can be specified with the `-o` and `-t` command line option.
Each of these directories must have the following structure:

```
Bug1_Output/
├── Phase1
├── Phase2
└── Phase3
```

### _Usage_

Below is the command line interface for genAllPhases.py:
- **Required Arguments**
    - _-p, --processed_ : a path to the processed directory that has the structure described above
    - _-c, --changes_ : a path to a csv file that contains the times of the phases changes
    - _-o, --one_ : a path to a directory to store the bug1 output
    - _-t, --two_ : a path to a directory to store the bug2 output

- **Optional Arguments**
    - _-d, --dictPhaseFile_ : This file represents the options that the output files can be created with. By default, the program will have the following options selected 
        - _isRadial_:entity
        - _isAlpScarf_:entity
        - _isStimulus_:Phase
        - _isColors_:[mapEntityColor.txt](./mapEntityColor.txt)

        The file must have the following format. 

        `OptionForPhaseDict:Value`

- **Arguments for PhaseDict Text File**
    - _isColors_: a text file that contains a mapping of functions to hex colors. This file must have the following format
        - `ColUsedForIsAlpScarf-Color`
    - _isAlpScarf_: a string that indicates that the alpscarf plot data should be generated with the AOI column as the passed in argument
    - _isRadial_: a string that indicates the radial data should be generated with the AOIName column as the passed in argument
    - _isStimulus_: a string that indicates the radial data should be generated with the stimulus column as the passed in argument
   
### _Example usage_
- `python3 genAllPhases.py -p ./processed_data -c ./PhaseChanges.csv -o ./Bug1_Output -t ./Bug2_Output`

*Note this script requires the genVisualPhases.py script since it uses the `createMergeDF()`, `parseMergeCSV()` `createSinglePhase()`, `createTransMatrix()`, and `createDistMatrix()` functions.

## calcMultiScore.py

### _Description_
This script will compute pairwise scanpath comparisons of all participants **_for a single phase for a single bug_** using the [MultiMatch](https://multimatch.readthedocs.io/en/latest/index.html) tool.
It will create a **_CSV file_** with the following header:

`Part1_ID,Part2_ID,Shape,Length,Direction,Position,Duration`

Because MultiMatch has the potential to have a long runtime, caching has been implemented to save time. This means that on every successful comparison, the script will write out the results to the passed in csv file. The next time the script is called, it will ignore all of the already-completed comparisions and pick up where it left of. 


### _Requirements_
This script requires that the files used for the comparison are generated from the genAllPhases.py script.

### _Usage_
- `python3 calcMultiScore.py <directoryToTSVFiles> <outputName> <pathToCachedCSV>`
