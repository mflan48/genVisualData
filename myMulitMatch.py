import os 
import multimatch_gaze as m
import numpy as np
import datetime as dt


def main():
    fix_vector1 = np.recfromcsv('./Maddie/bug2/processed/4_1562840410646-1562840488700/output/P1_multiMatchData.tsv',
                delimiter='\t',dtype={'names':('start_x','start_y','duration'),'formats':('f8','f8','f8')})
    fix_vector2 = np.recfromcsv('./Nick/bug2/processed/4_1560947991475-1560948067094/output/P1_multiMatchData.tsv',
                delimiter='\t',dtype={'names':('start_x','start_y','duration'),'formats':('f8','f8','f8')})

    temp = m.docomparison(fix_vector1,fix_vector2,screensize=[1280,720])
    print(temp)

if __name__ == "__main__":
    main()