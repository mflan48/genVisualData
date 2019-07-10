import pandas as pd
import numpy as np
import datetime
import json
import os
import glob
import sys
import matplotlib.pyplot as plt

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
        exit(1)

    pathFiles = pathToPost + globQuery
    files = glob.glob(pathFiles)

    """
    for i in range(0,len(files)):
        files[i] = os.path.split(files[i])[1]
    """
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


"""
    Read each of the iTrace-post files and creates on big pandas data frame 

    Returns:
    A pandas dataframe in time order of the following format
    (['fix_col', 'fix_line', 'fix_time', 'fix_dur' (milliseconds), 'which_file', 'AOI'])
"""
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


"""
    Creates a csv of the data in scatter plot format ([time],[AOI])

    Parameters: 
    combinedDF: pandasDF :dataFrame of ALL the csv files

    Return:
    Creates csv called "scatterData.csv"
"""
def createScatter(combinedDF, partName = "P0"):
    #only get the fix_time and AOI
    scatterDF = combinedDF[["fix_time","AOI"]].copy()
    #plt.scatter(scatterDF.fix_time,scatterDF.AOI)
    #plt.show()
    #create csv
    scatterDF.to_csv(partName + "_scatterData.csv",index = False)
    return

"""
    Creates a csv of the data in the format for the alpscarf tool ([p_name],[AOI],[dwell_duration])

    Parameters:
    combinedDF: pandasDF :dataFrame of ALL the csv files
    partName: str :name of the participant (could be of form of ID)

    Return:
    Creates csv called "alpscarfData.csv"
"""
def createAlpscarf(combinedDF,colLabel = "AOI",partName = "P_default"):
    """
    #Remove the other stuff
    alpDF = combinedDF[["fix_dur",colLabel]].copy()

    #Rename all the AOIS to AOI_$num
    if(colLabel=="AOI"):
        alpDF.loc[:,colLabel] = alpDF[colLabel].apply(lambda x: convertAOI(str(x)))
    

    #Add the participants column and rename fix_time to dwell_time
    alpDF.loc[:,"p_name"] = [str(partName)]*len(alpDF["fix_dur"])
    alpDF = alpDF.rename(index=str, columns={"fix_dur": "dwell_duration"})        

    #Reorder the columns
    columnsToReorder = alpDF.columns.tolist()
    columnsToReorder.reverse()
    alpDF = alpDF[columnsToReorder]

    #create alpScarfData
    alpDF.to_csv(partName + "_alpscarfData.csv",index = False)
    return
    """
"""
    Creates a csv of the data in the format for the radial transition graph tool ([AOIName],[FixationDuration],[Stimulus],[Participant])

    Parameters:
    combinedDF: pandasDF :dataFrame of ALL the csv files
    partName: str :name of the participant (could be of form of ID)
    isStimFunc: bool :whether or not we should use the function name as the stimulus col or if if should use the file name as stimulus col
    dictAOItoFunc: dict{str:list(str)} : maps a function name to a list of AOI's that correspond to that function

    Return:
    Creates csv called "alpscarfData.csv"
"""
def createRadial(combinedDF,partName = "P_default", isStimFunc = False, dictAOItoFunc = None):
    """
    if(dictAOItoFunc != None and isStimFunc != False):
        print("Radial will create the 'Stimulus' category with the function name and will remove the whitespace AOI's")
    else:
        print("Radial will create the 'Stimulus' category with the file name")

    #Only get AOI and the fixation duration
    radialDF = combinedDF[["AOI","fix_dur"]].copy()

    #Add the stimulus column. If isStimFunc is true, then have stimulus correspond to function AOI is in 
    if(not isStimFunc):
        #add the file that it was in
        radialDF.loc[:,"Stimulus"] = combinedDF["which_file"]
    else:
        #Get the function that the AOI belongs too via dictAOItoFunct
        radialDF.loc[:,"Stimulus"] = combinedDF["AOI"].apply(lambda x: findFuncName(str(x),dictAOItoFunc))
        #Remove the whitespace part since it messes with the rtgct tool
        radialDF = radialDF[radialDF["AOI"] != -1]
    
    #Add a participant number
    radialDF.loc[:,"Participant"] = [partName]*len(radialDF["fix_dur"])

    #rename the columns to fit accordingly
    radialDF = radialDF.rename(index=str,columns={"fix_dur": "FixationDuration", "AOI":"AOIName"})
    radialDF.loc[:,"AOIName"] = radialDF.loc[:,"AOIName"].apply(lambda x: convertAOI(str(x)))

    #Create radialData
    radialDF.to_csv(partName + "_radialData.csv",index=False)
    """

#AOInum must be a string
#dictAOItoFunc must be {string : list of strings }
def findFuncName(AOINum, dictAOItoFunc):
    toReturn = None
    for key,value in dictAOItoFunc.items():
        if(AOINum in value):
            toReturn = key
            return(str(toReturn))
    print("Error: Could not find AOI number " + AOINum + " in dictAOItoFunc ")
    print('Potential error could be that the type of AOINum is wrong')
    print("Type AOINum = ",end=' ')
    print(type(AOINum),end=' ')
    print(" Correct type should be str")
    exit(1)



def createColors():
    """
        if(colorMatching == None):
            print("No color csv will be created for the alpscarf tool")
            return
        
        #Get the total amount of AOI's 
        totalAOI = 0
        for value in colorMatching.values():
            totalAOI += len(value)
        
        #If there is no expected order, just make it go 1,2,3,4,5,6...
        if(expectedOrder == None):
            expectedOrder = list(range(1,totalAOI+1))
        
        #Create the AOI list
        aoiList = list(range(-1,totalAOI-1))

        colorsVect = []
        for i in range(-1,len(aoiList)-1):

            #Find the key in dictionary that has the number i
            isFound = False
            for key, value in colorMatching.items():
                if(str(i) in value):
                    colorsVect.append(key)
                    isFound = True
                    break
            #If it wasn't found throw and error
            if(not isFound):
                print("Error: Color matching contains an invalid AOI number")
                exit(1)
        
        aoiList = list(map(convertAOI,aoiList))
        colorsVect = list(map(convertColor,colorsVect))
        
        #Create the pandas DF and create csv from it
        colorsDF = pd.DataFrame()
        colorsDF["AOI"] = aoiList
        colorsDF["AOI_order"] = expectedOrder
        colorsDF["color"] = colorsVect

        colorsDF.to_csv(partName+ "_colors.csv",index = False,quotechar = '\'')
    """
 
"""
    This program will create 3 or 4 csv files depending on the command line arguments passed in. Those csv files are as follows
    1) A csv file with the experiment data in the format for scatter plots ([time],[AOI])
    2) A csv file with the experiment data in the format for the alpscarf tool ([p_name],[AOI],[dwell_duration])
    3) A csv file with the experiment data in the format for the radial transition graph tool ([AOIName],[FixationDuration],[Stimulus],[Participant])
    4) OPTIONAL: A csv file with the coloring list for the alpscarf tool ([AOI],[AOI_order],[color]) and with the mapping of AOIS to functions

    The program will also output to stdout which AOI's number map to which file

    Usage:
    python3 genVisualData.py <path to jsonFiles> <path to csvFiles> <participantID> OPTIONAL<fileToColorMatching>

    Requirements:
    pandas module
    glob module
    csvPath and jsonPath directories only contain csv and json files generated from itrace post
"""
def main():

    ABSPATH = "./619/Bug1/processed/1_1560946280495-1560946413840/post2aoi"
    #print(getFileNames("./post2aoi","/*.csv"))
    #print(getFileNames("./post2aoi","/*.json"))
    listCSV = getFilePaths(ABSPATH,"/*.csv")
    listJSON = getFilePaths(ABSPATH,"/*.json")
    
    print(createCombinedDF(listJSON,listCSV).to_string(index=False))



    """
    argc = len(sys.argv)
    argv = sys.argv
    """




#Return tuple of dicitonaries
#1st one is dictinoary of {color:AOI} 2nd is dictionary {functionName:AOI}
#File must be of format AOINumber,Top,Left,Bottom,Right,Component,Color
#Where top,left,bottom,right is taken directyl from the json file and is the adjusted AOI numbers
def parseAOI_Func_Color(fileName):

    colorDict = {}
    funcDict = {}
    with open(fileName,"r") as inFile:
        contents = [x.strip() for x in inFile.readlines()[1:] ]
        for row in contents:
            #Split row by ,
            splitRow = row.split(',')
            #Get the color, AOI, and Func
        
            aoi = str(splitRow[0])
            component= str(splitRow[5])
            color = str(splitRow[6])
           
            if(component in funcDict):
                funcDict[component].append(aoi)
            else:
                funcDict[component] = [aoi]
            
            if(color in colorDict):
                colorDict[color].append(aoi)
            else:
                colorDict[color] = [aoi]
    return( (colorDict,funcDict) )




if __name__ == '__main__':
    main()




"""
Command line options for getopt
-p --path (requires path) : path to phase directory (a phase is a directory like 0_startTimestamp-endTimeStamp) THIS DIRECTORY MUST CONTAIN A post2aoi directory
-c --colors (requires file): text file that contains a mapping of functions to hex colors
-g --global : option that indicates the scarf plot data be generated based on the files rather than the 
-i --id (optional but if used, requires int): the id of the participant 
"""