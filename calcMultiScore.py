import os 
import numpy as np
import pandas as pd
import glob
import multimatch_gaze as mGaze

def modPathName(pathName):
    return(pathName if pathName[len(pathName)-1] != "/" else pathName[0:len(pathName)-1])

def modCSVName(name):
    return(name if name.split(".")[-1]==".csv" else name+".csv")

#run a single comparison
def getSingleComparision(pathToFile1,pathToFile2,inSize = [1920,1080]):
    fix_vector1 = np.recfromcsv(pathToFile1,delimiter='\t'
        ,dtype={'names':('start_x','start_y','duration'),'formats':('f8','f8','f8')})
    fix_vector2 = np.recfromcsv(pathToFile2,delimiter='\t'
        ,dtype={'names':('start_x','start_y','duration'),'formats':('f8','f8','f8')})
    
    #Return them as a list
    return(mGaze.docomparison(fix_vector1,fix_vector2,screensize=inSize))
    

#ListFiles and listPartID are parell vectors. That is, the first file in listFiles is the one for the first entry in listPartID
#this would need to be called on each phase
def pairWiseComparison(listFiles,listPartID):
    if(len(listFiles) != len(listPartID)):
        print("Error: The two list for pairWiseComparison are not the same length")
        return
    header = ["Part1_ID","Part2_ID","Shape","Length","Direction","Position","Duration"]
    arr2d = []
    for i in range(0,len(listPartID)):
        for j in range(i+1,len(listPartID)):
            print("Doing comparison for participant " + str(listPartID[i]) + " and " + str(listPartID[j]))
            toAddList = [listPartID[i],listPartID[j]] + getSingleComparision(listFiles[i],listFiles[j])
            arr2d.append(toAddList)
    return(pd.DataFrame(arr2d,columns=header))
    
#The multimatch files need to have format Pid_ANYTHING IN BETWEEN_multiMatch.tsv
#these files must be in a directory that represents one of the phases we want to conduct the multimatch analysis on
#Directory to phase must not contain the final /
#this function will also extract the ID of the participants
def readInFiles(directoryToPhase):
    fileList = sorted(glob.glob(directoryToPhase + "/P?_*multiMatch.tsv"))
    idList = list()
    for curPath in fileList:
        curName = os.path.basename(curPath)
        idList.append(curName.split("_")[0])
    return(fileList,idList)



#Create the csv file
def createMultiCSV(directoryToPhase, outputName,outputPath="."):
    #Fix the names if needed
    directoryToPhase = modPathName(directoryToPhase)
    outputName = modCSVName(outputName)
    outputPath = modPathName(outputPath)

    #create the csv
    listFile, listID = readInFiles(directoryToPhase)
    finalDF = pairWiseComparison(listFile,listID)
    finalDF.to_csv(outputPath + "/" + outputName,index=False)
    return



    



def main():
    createMultiCSV(".","Com_line_not_implemented")



if __name__ == "__main__":
    main()