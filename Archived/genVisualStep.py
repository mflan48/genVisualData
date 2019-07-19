import pandas as pd
import numpy as np
import datetime
import json
import os
import glob
import sys
import getopt

"""
    Convert a timestamp into the amount of milliseconds passed since a certain starting value

    Parameters:
    timeStamp: epoch timestamp :timestamp of the form Year-Month-dayThour:Minute:seconds-UTC difference Ex: 2019-06-11T12:12:12.881-05:00 correspnods to june 11th 2019 
    startValue: float :the starting value in millisecons

    Return:
    A float of the amont of milliseconds the timestamp is from the starting value
"""
def convertTimeStamp(timeStamp,startValue = 0):
    return (datetime.datetime.strptime(timeStamp, "%Y-%m-%dT%H:%M:%S.%f-05:00")).timestamp() - startValue

"""
    Convert the number AOI to the format AOI_

    Parameters:
    myStrX: int or string :the number to be converted to AOI_

    Return:
    AOI_
"""
def convertAOI(myStrX):
    return ("AOI_" + str(myStrX))

"""
    Convert a hex color to the hex color format for alpscarf

    Parameters:
    myColor: str :a string of the hex color

    Return:
    The hex color in the right format
"""
def convertColor(myColor):
    return ( ("\"" + "#"+str(myColor) + "\"" ) if myColor[0] != '#' else ("\"" + str(myColor) + "\"") )

#jsonFilePath is the full path to the jsonFile
def getAmountAOI(jsonFilePath):
    with open(jsonFilePath,"r") as jsonFile:
        return(len(json.load(jsonFile)))

#THE pathToPost MUST NOT CONTAIN THE FINAL /. FILTER THIS OUT IN MAIN
#globQuery is what we want to search for in the directory. for csv use /*.csv and for json use /*.json
def getFilePaths(pathToPost,globQuery):
    
    #Check if that phase/post2aoi path exist
    if(not os.path.exists(pathToPost)):
        print("Error: Could not find path " + pathToPost)
        print("Make sure to define the path to the current phase with the -p command line option")
        exit(1)

    pathFiles = pathToPost + globQuery
    files = glob.glob(pathFiles)

    return(sorted(files))


#JUST GET THE ORIGNAL MINESWEEPER FILE NAME AND ADD .java
#how we store the 
def getFileNameFromPath(filePath):
    #split path to just get the file then just get the file.java
    return(os.path.split(filePath)[1].split(".")[0] + ".java")
        #fileName.split(".")[0] + ".java")


"""
    Searches a given directory for all json files and returns a dictionary with following key value pair
    {minesweeperFileName : amount of AOI's}

    Return:
    A dictionary of {minesweeperFileName : amountAOI's in file}
"""
def getAllAOISize(listJSONPath):

    #If there are no files, throw error
    if(len(listJSONPath) == 0):
        print("Error: No Json files exist")
        exit(1)
    
    toReturn = {}
    #Go thru each of the files and get the length of the AOI's in them 
    for curPath in listJSONPath:
        #get the file name without the .json extension and just the original file.java
        #toReturn[getCodeFile(curFile)] = getAmountAOI(pathToPost, curFile)
        toReturn[getFileNameFromPath(curPath)] = getAmountAOI(curPath)
    return toReturn        

"""
    Creates a dictionary of how much each file's AOI needs to get offset by

    Parameters:
    jsonPath: string :path to directory with all of the json files
    csvPath: string :path to directory with all of the csv files

    Return:
    A dictionary with key value pair {fileName: numberOffSet for AOI}
    Also prints the numbering of AOI's for each file 
"""
def getNumToAdjustAOI(listJSONPath,listCSVPath):

    #Create the dictionary of AOI sizes
    jsonDict = getAllAOISize(listJSONPath)


    #keeps track of the offset AOI number
    curOffSet = 0

    toReturn = {}

    for i in listCSVPath:
        #get the the .csv fileName
        curCSVName = getFileNameFromPath(i)

        #Check to see if it exist in the jsonDict. If it does then print the numbers for which it AOIS will be globally
        # If its not, that means either the .csv doesnt exist or their was not a jsonFile for it 
        if(curCSVName in jsonDict.keys()):
            print(curCSVName + " AOI's will be number " + str(curOffSet) + " to " + str(curOffSet + jsonDict[curCSVName]-1) + "\n")
            toReturn[curCSVName] = curOffSet
            curOffSet = curOffSet + jsonDict[curCSVName]
        else:
            print("Error: " + curCSVName + "either does not have a json file or does not exist ")
            exit(1)
    return(toReturn)

"""
    Finds the starting time of the experiment by searching all of the files

    Requirements:
    Each csvFile is in time order and the earliest time is the first entry in the fix_time section

    Parameters:
    dataFramesDict: dictionary {fileName, pandasDF} :dictionary of fileNames with pandas dataframes representing each one
"""
def findEarliestTime(dataFramesDict):
    #earliestTime
    earliestTime = 0.0
    
    for value in dataFramesDict.values():
        curTime = convertTimeStamp(str(value.iloc[0]["fix_time"]))
        if(earliestTime == 0.0):
            earliestTime = curTime
        elif(curTime < earliestTime):
            earliestTime = curTime
    return(earliestTime)

#File must be of format {functionName-color}
def createFuncToColor(pathToFile):
    try:
        toReturn ={}
        with open(pathToFile,"r") as inFile:
            contents = [x.strip() for x in inFile.readlines()]
            for row in contents[1:]:
                splitted = row.split("-")
                if(not str(splitted[0]) in toReturn.keys()):
                    toReturn[str(splitted[0])] = convertColor(splitted[1])
                else:
                    print("Error: " + splitted[0] + " was defined multiple times in file " + pathToFile)
                    exit(1)
        return(toReturn)
    except FileNotFoundError:
        print("Error: Could not find file " + pathToFile)
        exit(1)

def createCombinedDF(listJSONPath,listCSVPath): 
    #get the amount to adjust each AOI
    numAdjust = getNumToAdjustAOI(listJSONPath,listCSVPath)

    #Dictionary used to store all dataframes
    allFrames = {}

    #Read in and create all of the dataFrames, edit their AOI's
    for curPath in listCSVPath:
        #Get the name of the file
        curName = getFileNameFromPath(curPath)
        
        #Read it in
        allFrames[curName] = pd.read_csv(curPath)
        #Update the AOI's
        allFrames[curName].AOI = np.where(allFrames[curName].AOI >= 0, allFrames[curName].AOI + numAdjust[curName] , -1)
    
    #find the earliest time
    earliestTime = findEarliestTime(allFrames)

    #Combine all of the files 
    combinedDF = pd.concat(allFrames,ignore_index=False)

    #Convert time stamp and sort based on time
    combinedDF["fix_time"] = combinedDF["fix_time"].apply(lambda x: convertTimeStamp(str(x), earliestTime))
    combinedDF = combinedDF.sort_values(by=["fix_time"])

    #Conver duration from nanoseconds to milliseconds
    combinedDF["fix_dur"] = (combinedDF["fix_dur"]*(10**-6))
    return(combinedDF)

def createScatter(combinedDF,pathToOutput,partName,timeCol="fix_time",interestCol="AOI",removeWhite = True):
    #assert that timeCol and interestCol are in combinedDF
    if(not timeCol in combinedDF.columns or not interestCol in combinedDF.columns):
        print("Error: Either " + timeCol + " or " + interestCol + " does not exist in the combined")
        exit(1)
    
    #remove the whitespace
    scatterDF = combinedDF.copy()
    if(removeWhite):
        scatterDF = scatterDF[scatterDF["AOI"] != -1]
    
    #only get the fix_time and AOI
    scatterDF = scatterDF[[timeCol,interestCol]]
    endPath = pathToOutput + "/" + partName + "_scatterData.csv"
    scatterDF.to_csv(endPath,index = False)
    return

def createAlpscarf(combinedDF,pathToOutput,partName,durationCol="fix_dur",interestCol = "function",removeWhite = True):

    #assert that timeCol and interestCol are in combinedDF
    if(not durationCol in combinedDF.columns or not interestCol in combinedDF.columns):
        print("Error: Either " + durationCol + " or " + interestCol + " does not exist in the combined")
        exit(1)
    
    #Remove the whitespace
    alpDF = combinedDF.copy()
    if(removeWhite):
        alpDF = alpDF[alpDF["AOI"] != -1]
    
    #Get the duration and the column of interest
    alpDF = alpDF[[durationCol,interestCol]]

    #Rename all aois to AOI_$num
    if(interestCol=="AOI"):
        alpDF.loc[:,interestCol] = alpDF[interestCol].apply(lambda x: convertAOI(str(x)))

    
    #Add particiapnts col and rename fix_dur
    alpDF.loc[:,"p_name"] = [partName]*len(alpDF[durationCol])
    alpDF = alpDF.rename(index=str,columns={durationCol:"dwell_duration",interestCol:"AOI"})

    #reorder the columns
    columnsToReorder = alpDF.columns.tolist()
    columnsToReorder.reverse()
    alpDF = alpDF[columnsToReorder]

    #CreatealpscarfData
    endPath = pathToOutput + "/" + partName + "_alpscarfData.csv"
    alpDF.to_csv(endPath,index=False)
    return

def createRadial(combinedDF,pathToOutput,partName,interestCol="function",stimulusCol="which_file",durationCol="fix_dur",removeWhite = True):
    
    #Ensure that all the columns exist within combinedDF
    if(not (interestCol in combinedDF.columns and stimulusCol in combinedDF.columns and durationCol in combinedDF.columns)):
        print("Error: One or more of the following does not exist in the combinedDF")
        print(interestCol + " " + stimulusCol + " " + durationCol)
        exit(1)
    
    radialDF = combinedDF.copy()

    #Remove the whitespace from the combinedDF
    if(removeWhite):
        radialDF = radialDF[radialDF["AOI"] != -1]

    #Make sure that interestCol and stimulusCol are not the same. if they are throw an error
    if(interestCol == stimulusCol):
        print("Error: The Stimulus column and AOIName column for the radial graphs can not both be '" + interestCol + "'")
        exit(1)

    #Just get the columns we want and add the participant column
    radialDF = radialDF[[interestCol,durationCol,stimulusCol]]
    radialDF.loc[:,"Participant"]=[partName]*len(radialDF[durationCol])
    

    #rename the columns accordinlgy and check if the interestColumn is the AOI  number. if it is, then convert them
    if(interestCol == "AOI"):
        radialDF.loc[:,interestCol] = radialDF.loc[:,interestCol].apply(lambda x : convertAOI(str(x)))
    radialDF = radialDF.rename(index=str,columns={durationCol:"FixationDuration",stimulusCol:"Stimulus",interestCol:"AOIName"})
    
    endPath = pathToOutput + "/" + partName+ "_radialData.csv"
    radialDF.to_csv(endPath,index=False)
    return


#funcToColor is a dicionary {functionaName:color} OR {aoi:color}
#if funcToColor is {aoi:color} it must be the ADJUSTED AOI numbers
#The color must be in the right format (must be "#454545")
def createColors(combinedDF,pathToOutput,partName,funcToColor,interestCol="function"):
    
    #Check if the columns exist in the combined DF
    if(not interestCol in combinedDF.columns):
        print("Error: " + interestCol + " does not exist in the combinedDF")
        exit(1)
    

    #get all of the unique values interestCol values in the data frame,
    interestVals = sorted(combinedDF[interestCol].unique())

    expectedOrder = list(range(1,len(interestVals)+1))
    colorsVect = []

    #Search thru all of the values in the interestCol and get their color from the funcToColor dictionart
    for curVal in interestVals:
        if(str(curVal) in funcToColor):
            colorsVect.append(funcToColor[curVal])
        else:
            print("Error: " + str(curVal) + " was in the " + str(interestCol) + " of the combinedDF but did not exist in the funcToColor dicionary")
            print("Double check the file that is used to generate the funcToColor dictionary to ensure that all functions/AOI's are accounted for")
            exit(1)

    #Create the file
    colorsDF = pd.DataFrame()
    colorsDF["AOI"] = interestVals
    colorsDF["AOI_order"] = expectedOrder
    colorsDF["color"] = colorsVect

    endPath = pathToOutput + "/" + partName + "_colors.csv"
    colorsDF.to_csv(endPath,index=False,quotechar = '\'')
    return


def createMultiMatch(combinedDF, pathToOutput,partName,durationCol="fix_dur",pixXCol="pixel_x",pixYCol="pixel_y",removeWhite=True):
    multiDF = combinedDF.copy()
    if(removeWhite):
        multiDF = multiDF[multiDF["AOI"]!=-1]
    multiDF = multiDF[[pixXCol,pixYCol,durationCol]]
    multiDF.loc[:,durationCol] = multiDF.loc[:,durationCol]*(10**-3)
    multiDF = multiDF.rename(index=str,columns={durationCol:"duration",pixXCol:"start_x",pixYCol:"start_y"})
    endPath = pathToOutput+"/"+partName+"_multiMatchData.tsv"
    multiDF.to_csv(endPath,sep="\t",index=False)


def main():

    #getopt stuff 
    try:
        options,arguments = getopt.getopt(sys.argv[1:],"hp:c:a:r:s:i:o:",["help","path=","colors=","alpscarf=","radial=","stimulus=","id=","output="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        exit(1)
    
    #Variables for the graphs
    phasePath ="."
    outputPath="."
    partID=1
    colorsFile=None
    alpScarfAOI=None
    radialInterest=None
    radialStimulus=None
    if(len(options) == 0):
        usage()
        exit(1)
    #Take care of the options
    for opt,arg in options:
        if(opt in ("-p","--path") ):
            phasePath = arg
        elif(opt in ("-c,--colors")):
            colorsFile = arg
        elif(opt in ("-a","--alpscarf")):
            alpScarfAOI=arg
        elif(opt in ("-r","--radial")):
            radialInterest=arg
        elif(opt in ("-s","--stimulus")):
            radialStimulus=arg
        elif(opt in ("-i","--id")):
            partID = arg
        elif(opt in ("-o","--output")):
            outputPath = arg
        elif(opt in ("-h","--help")):
            usage()
            exit(1)
        else:
            assert False, "unhandled option"
    
    #make sure the partID is still an integer
    try:
        int(partID)
    except ValueError:
        print("Participant ID must be an integer")
        exit(1)
    #Modify the ID to be of form Pid
    partID = "P" + str(partID)

    #Modify the phase path and output path to not included the final /
    phasePath = modPathName(phasePath)
    outputPath = modPathName(outputPath)

    #Check to see if the phasePath contains a post2aoi directory. If it doesnt, throw an error
    if(not os.path.exists(phasePath+"/post2aoi")):
        print("Error: The required post2aoi directory does not exist within the path" + phasePath)
        print("Make sure the phase path is a path to a phase directory")
        exit(1)
    else:
        phasePath = phasePath + "/post2aoi"
    
    #Create the output directory if it doesnt exist
    if(not os.path.exists(outputPath + "/output")):
        outputPath = outputPath + "/output"
        os.makedirs(outputPath)
        print("No output directory exists so one will be created with the name 'output' with the following path " + outputPath + "\n")
    else:
        print("Output directory exists at path " + outputPath + ". The contents of it will be overwritten")
        outputPath = outputPath + "/output"
    
    #Create the combinedDF
    listCSV = getFilePaths(phasePath,"/*.csv")
    listJSON = getFilePaths(phasePath,"/*.json")
    myComb = createCombinedDF(listJSON,listCSV)

    #Create colors
    if(colorsFile != None):
        temp = createFuncToColor(colorsFile)
        createColors(myComb,outputPath,partID,temp)

    #Create alp
    if(alpScarfAOI != None):
        createAlpscarf(myComb,outputPath,partID,interestCol=alpScarfAOI)
    else:
        createAlpscarf(myComb,outputPath,partID)
    
    #Create radial
    if(radialInterest == None and radialStimulus == None):
        createRadial(myComb,outputPath,partID)
    elif(radialInterest != None and radialStimulus == None):
        createRadial(myComb,outputPath,partID,interestCol=radialInterest)
    elif(radialInterest == None and radialStimulus != None):
        createRadial(myComb,outputPath,partID,stimulusCol=radialStimulus)
    else:
        createRadial(myComb,outputPath,partID,stimulusCol=radialStimulus,interestCol=radialInterest)

    #Create scatter
    createScatter(myComb,outputPath,partID)
    #Create multimatch
    createMultiMatch(myComb,outputPath,partID)


    
def modPathName(pathName):
    return(pathName if pathName[len(pathName)-1] != "/" else pathName[0:len(pathName)-1])


def usage():
    print("Command line options for getopt\n")
    print("-p --path: requires a path to phase directory (a phase is a directory like 0_startTimestamp-endTimeStamp) THIS DIRECTORY MUST CONTAIN A post2aoi directory")
    print("-c --colors: requires a text file that contains a mapping of functions to hex colors")
    print("-a --alpscarf: requires a string that indicates that the alpscarf plot data should be generate with the AOI column as the passed in argument")
    print("-r --radial: requires a string that indicates the radial data should be generated with the AOIName column as the passed in argumenet")
    print("-s --stimulus: requires a string that indicates the radial data should be genreate with the stimulus column as the passed in argument")
    print("-i --id: requires an int that represents the id of the participant")
    print("-o --output: requires a path to directory where the 'output' subdirectory will be created that stores all of the files")
    print("-h --help: displays this message")
if __name__ == '__main__':
    main()
