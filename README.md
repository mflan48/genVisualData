# Description of Repo
This repo contains scripts to compute various data files/analysis for our experiment. It contains scripts that do the following
1) Generates visual/multimatch data for all the participants. 
2) Calculates distribution and transition matrices for each of the phases for all of the participants
3) #TODO, add descriptions of what the clustering.py and metrics.py files do

## **genAllPhases Script***
### _Description_

For our experiment, we are splitting the merged_data into three _phases_. These phases are 
1) Finding initial points 
2) Building on initial points 
3) Fixing the bug. 

This script will create data for each bug and for each phase in each bug. For each of those, it will create files for the following: [alpscarf tool](https://github.com/Chia-KaiYang/alpscarf), [radial transition graph tool](http://www.rtgct.fbeck.com/), scatter plots, and [multimatch tool](https://multimatch.readthedocs.io/en/latest/index.html).
It creates these csv files from the `merged_data.csv` file that is created in the [iTracePost Module](https://github.com/ianbtr/iTrace-post).

This script will also create Distribution and Transition csv files for each of the bugs for all of the participants

### _Requirements_

This program requires a path to a **_processed_data_** directory that contains all of the merged_data files
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
* Note: If a certain participant does not have any data for a specific bug, the subdirectory for that bug is not required

In order to split the data up by phases, two epoch times are needed to distinguish the three stages. These times should be located in a **_CSV file_** with the following header

`Participant,Trial,endPhase1,endPhase2`

The program also requires **_two output directories_**, one for each bug. These directories can be specified with the `-o` and `-t` command line option.
Each of these directories must have the following structure:

```
Bug1_Output/
├── Phase1
├── Phase2
└── Phase3
```

### _Usage_

Below is the command line interface:
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
    - _isStimulus_: a string that indicates the radial data should be generated with the stimulus column as the passed in argument\n
   
### _Example usage_
- `python3 genAllPhases.py -p ./processed_data -c ./PhaseChanges.csv -o ./Bug1_Output -t ./Bug2_Output`

*Note this script requires the genVisualPhases.py script since it uses the `createMergeDF()`, `parseMergeCSV()` `createSinglePhase()`, `createTransMatrix()`, and `createDistMatrix()` functions.

## calcMultiScore Script

### _Description_
This script will compute pairwise scanpath comparisons of all participants **_for a single phase for a single bug_** using the [MultiMatch](https://multimatch.readthedocs.io/en/latest/index.html) tool.
It will create a **_CSV file_** with the following header:

`Part1_ID,Part2_ID,Shape,Length,Direction,Position,Duration`

Because MultiMatch has the potential to have a long runtime, caching has been implemented to save time. This means that after every successful comparision of MultiMatch, the script will write out the results to the passed in csv file. This means that next time the script is called, it will ignore all of the comparisions already done and pick up where it left of. 


### _Requirements_
This script requires that the files used for the comparison are generated from the genAllPhases.py script.

### _Usage_
- `python3 calcMultiScore.py <directoryToTSVFiles> <outputName> <pathToCachedCSV>`
