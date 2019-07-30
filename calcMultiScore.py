import os 
import numpy as np
import pandas as pd
import glob
import multimatch_gaze as mGaze
from tqdm import tqdm

def modPathName(pathName):
    return(pathName if pathName[len(pathName)-1] != "/" else pathName[0:len(pathName)-1])

def modCSVName(name):
    return(name if name.split(".")[-1]=="csv" else name+".csv")

#run a single comparison
def getSingleComparision(pathToFile1,pathToFile2,inSize = [1920,1080]):
    fix_vector1 = np.recfromcsv(pathToFile1,delimiter='\t'
        ,dtype={'names':('start_x','start_y','duration'),'formats':('f8','f8','f8')})
    fix_vector2 = np.recfromcsv(pathToFile2,delimiter='\t'
        ,dtype={'names':('start_x','start_y','duration'),'formats':('f8','f8','f8')})
    
    #Return them as a dictionary
    values = mGaze.docomparison(fix_vector1,fix_vector2,screensize=inSize)
    toReturn = {}
    toReturn["Shape"] = values[0]
    toReturn["Length"] = values[1]
    toReturn["Direction"]=values[2]
    toReturn["Position"]=values[3]
    toReturn["Duration"]=values[4]

    return(toReturn)
    

#ListFiles and listPartID are parell vectors. That is, the first file in listFiles is the one for the first entry in listPartID
#this would need to be called on each phase
#cacheDF is a dataframe of already computed multimatch scores
def pairWiseComparison(listFiles,listPartID,cacheDF):

    
    header = ["Part1_ID","Part2_ID","Shape","Length","Direction","Position","Duration"]
    toReturnDF = pd.DataFrame(columns = header)
    listAlreadyComp = []
    if(cacheDF.empty != True):
        toReturnDF = cacheDF.copy()

        #Get a list of tuples of all of the participants that have went already
        groups = cacheDF.groupby(["Part1_ID","Part2_ID"])
        for name,group in groups:
            pair1 = name[0],name[1]
            pair2 = name[1],name[0]
            listAlreadyComp.append(pair1)
            listAlreadyComp.append(pair2)



    #toReturnDF = cacheDF.copy()

    
    if(len(listFiles) != len(listPartID)):
        print("Error: The two list for pairWiseComparison are not the same length")
        return


    for i in tqdm(range(0,len(listPartID))):
        #check if multimatch file for part i is valie
        with open(listFiles[i],"r") as file1:
            if(len(file1.readlines()) == 1):
                print("Skipping participant " +str(listPartID[i]) +" because their multimatch.tsv is empty")
                continue

        for j in tqdm(range(i+1,len(listPartID))):
            #check if the multimatch file for part j  participants is valid
            with open(listFiles[j],"r") as file2:
                if(len(file2.readlines()) == 1):
                    print("Skipping participant " +str(listPartID[j]) +" because their multimatch.tsv is empty")
                    continue
            
            toAddDF = pd.DataFrame(columns = header)
            #Create a temp pair of the participants and see if it already exist in listAlready
            tempPair = listPartID[i],listPartID[j]
            if(tempPair in listAlreadyComp):
                print("Skipping comparision between " + tempPair[0] + " and " + tempPair[1] + " because we have already done it" )
                continue
            else:
                print("Doing comparison for participant " + str(listPartID[i]) + " and " + str(listPartID[j]))
                dictToAdd = getSingleComparision(listFiles[i],listFiles[j])
                dictToAdd["Part1_ID"] = listPartID[i]
                dictToAdd["Part2_ID"] = listPartID[j]
                toAddDF = toAddDF.append(dictToAdd,ignore_index=True)
                toReturnDF = pd.concat([toReturnDF,toAddDF],ignore_index=True)

    toReturnDF = toReturnDF.sort_values(by=["Part1_ID","Part2_ID"])
    return(toReturnDF)



#ListFiles and listPartID are parell vectors. That is, the first file in listFiles is the one for the first entry in listPartID
#this would need to be called on each phase
#cacheDF is a dataframe of already computed multimatch scores
def pairWiseComparison2(listFiles,listPartID,cacheDF,outputPath):

    part1Col = "Part1_ID"
    part2Col = "Part2_ID"
    
    header = [part1Col,part2Col,"Shape","Length","Direction","Position","Duration"]
    toReturnDF = pd.DataFrame(columns = header)
    listAlreadyComp = []
    if(cacheDF.empty != True):
        toReturnDF = cacheDF.copy()

        #Get a list of tuples of all of the participants that have went already
        groups = cacheDF.groupby([part1Col,part2Col])
        for name,group in groups:
            pair1 = name[0],name[1]
            pair2 = name[1],name[0]
            listAlreadyComp.append(pair1)
            listAlreadyComp.append(pair2)

    
    if(len(listFiles) != len(listPartID)):
        print("Error: The two list for pairWiseComparison are not the same length")
        return


    for i in tqdm(range(0,len(listPartID))):
        #check if multimatch file for part i is valie
        with open(listFiles[i],"r") as file1:
            if(len(file1.readlines()) == 1):
                print("Skipping participant " +str(listPartID[i]) +" because their multimatch.tsv is empty")
                continue

        for j in tqdm(range(i+1,len(listPartID))):
            #check if the multimatch file for part j  participants is valid
            with open(listFiles[j],"r") as file2:
                if(len(file2.readlines()) == 1):
                    print("Skipping participant " +str(listPartID[j]) +" because their multimatch.tsv is empty")
                    continue
            
            toAddDF = pd.DataFrame(columns = header)
            #Create a temp pair of the participants and see if it already exist in listAlready
            tempPair = listPartID[i],listPartID[j]
            if(tempPair in listAlreadyComp):
                print("Skipping comparision between " + tempPair[0] + " and " + tempPair[1] + " because we have already done it" )
                continue
            else:
                print("Doing comparison for participant " + str(listPartID[i]) + " and " + str(listPartID[j]))
                #Run the comparison and add it to toReturnDF
                dictToAdd = getSingleComparision(listFiles[i],listFiles[j])
                dictToAdd[part1Col] = listPartID[i]
                dictToAdd[part2Col] = listPartID[j]
                toAddDF = toAddDF.append(dictToAdd,ignore_index=True)
                toReturnDF = pd.concat([toReturnDF,toAddDF],ignore_index=True,sort=False)
            
            #save the values of toReturnDF eito the output path
            toReturnDF = toReturnDF.sort_values(by=[part1Col,part2Col])
            toReturnDF.to_csv(outputPath,index=False)

    toReturnDF = toReturnDF.sort_values(by=[part1Col,part2Col])
    toReturnDF.to_csv(outputPath)
    return  


#The multimatch files need to have format Pid_ANYTHING IN BETWEEN_multiMatch.tsv
#these files must be in a directory that represents one of the phases we want to conduct the multimatch analysis on
#Directory to phase must not contain the final /
#this function will also extract the ID of the participants
def readInFiles(directoryToPhase):
    if(not os.path.exists(directoryToPhase)):
        print("Error: " + directoryToPhase + " does not exist")
        exit(1)
    
    fileList = sorted(glob.glob(directoryToPhase + "/P?*multiMatch.tsv"))
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

    cachedDF = None
    try:
        cachedDF = pd.read_csv("Bug1_Phase1_MultiComp_copy.csv")
    except FileNotFoundError:
        cachedDF = pd.DataFrame()

    #create the csv
    listFile, listID = readInFiles(directoryToPhase)
    finalDF = pairWiseComparison(listFile,listID,cacheDF=cachedDF)
    finalDF.to_csv(outputPath + "/" + outputName,index=False)
    return


def createMultiCSV2(pathToPhase,outputName,pathToCached):
    pathToPhase = modPathName(pathToPhase)
    outputName = modCSVName(outputName)

    cachedDF = None
    try:
        print("Found file " + pathToCached + " and will append to the contents of it")
        cachedDF = pd.read_csv(pathToCached)
    except FileNotFoundError:
        print("Creating empty dataframe and running pairWiseComparison2")
        cachedDF = pd.DataFrame()
    
    #create the csv
    listFile, listID = readInFiles(pathToPhase)
    pairWiseComparison2(listFile,listID,cacheDF=cachedDF,outputPath=outputName)





def main():
    createMultiCSV("./Bug1_Output/Phase1","Bug1_Phase1_MultiComp_Test")
    exit(1)
    #createMultiCSV("./Bug1_Output/Phase2","Bug1_Phase2_MultiComp")
    directoryToPhase = "testMultiMatch/"
    outputName = "testAdd.csv"

    cachedDF = None
    try:
        cachedDF = pd.read_csv("Bug1_Phase1_MultiComp_copy.csv")
    except FileNotFoundError:
        cachedDF = pd.DataFrame()
    
    listFile,listID = readInFiles(directoryToPhase)


    pairWiseComparison2(listFile,listID,cachedDF,outputName)




if __name__ == "__main__":
    main()
