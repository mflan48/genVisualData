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

"""
    Gets the amount of AOI's in a passed in jsonFile

    Requirements:
    pathName is a valid path and does not include the ending /

    Parameters:
    pathName: string :path to where the jsonFile is
    jsonFileName: string :the name of the json file to read

    Return:
    Length of the json file which corresponds to how many AOI's are in that file (including the -1 AOI which is either whitespace or not an AOI)    
"""
def getAmountAOI(pathName,jsonFileName):
    toOpen = pathName  + "/" + jsonFileName
    with open(toOpen) as jsonFile:
        return(len(json.load(jsonFile)))

"""
    Searches a given directory for all json files and returns a dictionary with following key value pair
    {fileName : amount of AOI's}

    Parameters:
    pathName: string :the path to search for .json files (these files are the ones generated from Ian's AOI tool)

    Return:
    A dictionary of {fileName : amountAOI's in file}
"""
def getAllAOISize(pathName):
    #Check if the path exist
    if(not os.path.exists(pathName)):
        print("Error: Could not find path" + pathName)
        exit(1)

    #use glob module to find all of the json files in the path
    myPath = pathName + "/*.json"
    files = glob.glob(myPath)

    #If there are no files, throw error
    if(len(files) == 0):
        print("Error: No json files found in path " + pathName)
        exit(1)
    

    toReturn = {}
    #Go thru each of the files and get the length of the AOI's in them 
    for i in files:
        #Split the path and get the file
        temp = os.path.split(i)
        
        #get the file name without the .json extension
        toReturn[os.path.splitext(temp[1])[0]] = getAmountAOI(temp[0], temp[1])
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
def getNumToAdjustAOI(jsonPath, csvPath):

    #Create the dictionary of AOI sizes
    jsonDict = getAllAOISize(jsonPath)

    #find all the csv's in the csvPath
    csvPathName = csvPath + "/*.csv" 
    csvFiles = glob.glob(csvPathName)
    if(len(csvFiles) == 0):
        print("Error: No files exist")
        exit(1)
    elif(len(jsonDict) != len(csvFiles)):
        print("Error: there are different amount of .csv files and .json files")
        exit(1)

    #keeps track of the offset AOI number
    curOffSet = 0

    toReturn = {}

    for i in csvFiles:
        #get the the .csv fileName
        splittedPath = os.path.splitext(os.path.split(i)[1])[0]

        #Check to see if it exist in the jsonDict. If it does then print the numbers for which it AOIS will be globally
        # If its not, that means either the .csv doesnt exist or their was not a jsonFile for it 
        if(splittedPath in jsonDict.keys()):
            print(splittedPath + " AOI's will be number " + str(curOffSet) + " to " + str(curOffSet + jsonDict[splittedPath]-1) + "\n")
            toReturn[splittedPath] = curOffSet
            curOffSet = curOffSet + jsonDict[splittedPath]
        else:
            print("Error: " + splittedPath + "either does not have a json file or does not exist ")
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
    Creates the colorMatching dictionary based off an input file

    Requirments:
    Each line of Match file is of the following format
    Color1,<...>        <...> means the list of AOI's with this color each seperated by commas.  Ex: 1,3,5,45,69

    Parameters:
    matchFile: string :the name of the file to read from

    Return:
    Dictionary with key value pair {hex color: list AOIs with that color}
"""
def createColorMatching(matchFile):

    toReturn = {}
    try:
        with open(matchFile, "r") as colorFile:
            contents = [x.strip("\n") for x in colorFile.readlines()]
            for line in contents:
                stripped = line.replace(" ","").split(",")
                color = stripped[0]
                AOIs = stripped[1:]
                if(not color in toReturn.keys()):
                    toReturn[color] = AOIs
                else:
                    print("Error: Multiple colors exist in" + matchFile)
                    exit(1)
    except FileNotFoundError:
        print("Error: " + matchFile + " could not be found")
        exit(1)

    return(toReturn)

"""
    Read each of the iTrace-post files and creates on big pandas data frame 

    Parameters:
    jsonPath: string :path to directry with jsonFiles
    csvPath: string :path to directory with csvFiles

    Returns:
    A pandas dataframe in time order of the following format
    (['fix_col', 'fix_line', 'fix_time', 'fix_dur' (milliseconds), 'which_file', 'AOI'])
"""
def createCombinedDF(jsonPath, csvPath):
        
    #get the amount to adjust each AOI
    numAdjust = getNumToAdjustAOI(jsonPath,csvPath)

    #Dictionary used to store all dataframes
    allFrames = {}

    #find all the csv's in the csvPath
    csvPathName = csvPath + "/*.csv" 
    csvFiles = glob.glob(csvPathName)
    
    #Read in and create all of the dataFrames, edit their AOI's
    for i in csvFiles:
        #Get the name of the file
        curName = os.path.splitext(os.path.split(i)[1])[0]
        
        #Read it in
        allFrames[curName] = pd.read_csv(i)
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
    combined_df:  A dataframe, of the same form as the one returned by createCombinedDF.
                    The resulting dataframe will be sorted by timestamp.
    matching_scheme:  A dictionary that maps new (merged) AOIs to sets of original (automatic) AOIs.
                    This can be loaded from a json.
    
    IMPORTANT: ANY AOI not contained as a key in matching_schemes will not be generated; so make sure 
        the pair {-1: [-1]} is included, otherwise the final DF will not contain any entries where the 
        AOI is -1.
"""
def mergeAOIs(combined_df, matching_scheme):
    if type(matching_scheme) is str:
        with open(matching_scheme) as infile:
            matching_scheme = json.load(infile)

    else:
        assert type(matching_scheme) is dict

    # Create new df to append to
    new_df = pd.DataFrame(combined_df[0:0])

    # Append matching AOIs to new df
    for new_aoi, old_aois in matching_scheme.items():
        for old_aoi in old_aois:
            matching_rows = combined_df.loc[combined_df["AOI"] == old_aoi]
            matching_rows.loc[:, "AOI"] = new_aoi
            new_df = new_df.append(matching_rows)

    # Sort rows by time
    new_df = new_df.sort_values(by='fix_time')

    return new_df

"""
    Creates a csv of the data in scatter plot format ([time],[AOI])

    Parameters: 
    combinedDF: pandasDF :dataFrame of ALL the csv files

    Return:
    Creates csv called "scatterData.csv"
"""
def createScatter(combinedDF, partName = "P_default"):
    #only get the fix_time and AOI
    scatterDF = combinedDF[["fix_time","AOI"]].copy()
    plt.scatter(scatterDF.fix_time,scatterDF.AOI)
    plt.show()
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
def createAlpscarf(combinedDF,partName = "P_default"):
        #Remove the other stuff
        alpDF = combinedDF[["fix_dur","AOI"]].copy()

        #Rename all the AOIS to AOI_$num
        alpDF.loc[:,"AOI"] = alpDF["AOI"].apply(lambda x: convertAOI(str(x)))


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


"""
    Create the colors csv file for the alpscarf tool 

    Parameters:
    combinedDF: pandasDF :dataframe of all of the eye tracking csv info
    colorMatching: dictionary :dictionary of key value {hexColor: list of Aois with this color}
    expectedOrder: list :list of the expected order column. By default it will be 1,2,3,....
    isShaded: bool :a bool for whether or not the AOI's with the same color should be exactly the same color or different shades of that color
        -Note: this is not yet implemented. By default they will all be the same color
    partName: string :the name of the participant

    Return:
    Creates the colors csv file with the following format ([AOI],[AOI_order],[color])
    The order of AOI is by default -1,0,1,... while the AOI_order is the expected order which is 1,2,3,... by default
"""
def createColors(combinedDF, colorMatching = None, expectedOrder = None, isShaded = False, partName = "P_default"):

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
    Creates all of the csv files for the scatter,alpscarf, and radial tranisiton tool 

    Parameters:
    jsonPath: string :path to directory that contains all of the json files
    csvPath: string :path to directory that conatins all of the csv files
    colorMatching: dictionary {color, list of AOI} :dictionary that contains a hex color and a list of AOI's that should be that color
        -this is only used for if we create the colors.csv file
    partName: string :the participants name we are creating these files for 

    Return:
    Creates all of the csvs as listed above
"""
def createAllCSV(jsonPath, csvPath,colorMatching, partName="P_default",dictAOItoFunc = None):

    #Create the dataframe with all the csv files 
    combinedDF = createCombinedDF(jsonPath,csvPath)

    #Create the three csv files
    createScatter(combinedDF,partName)
    createAlpscarf(combinedDF,partName)
    if(dictAOItoFunc == None):
        createRadial(combinedDF,partName,False,None)
    else:
        createRadial(combinedDF,partName,True,dictAOItoFunc)

    createColors(combinedDF,colorMatching,partName = partName)  

#file must be of format "funcName,listNums"
def readAOItoFuncFile(fileName):
    toReturn = {}
    with open(fileName, "r") as inFile:
        contents = [x.strip("\n") for x in inFile.readlines()]
        for line in contents:
            stripped = line.replace(" ","_").split(",")
            funcName = stripped[0]
            AOIs = stripped[1:]

            if(not funcName in toReturn.keys()):
                toReturn[funcName] = AOIs
            else:
                print("Error: Multiple colors exist in" + fileName)
                exit(1)
    return(toReturn)



"""
    This program will create 3 or 4 csv files depending on the command line arguments passed in. Those csv files are as follows
    1) A csv file with the experiment data in the format for scatter plots ([time],[AOI])
    2) A csv file with the experiment data in the format for the alpscarf tool ([p_name],[AOI],[dwell_duration])
    3) A csv file with the experiment data in the format for the radial transition graph tool ([AOIName],[FixationDuration],[Stimulus],[Participant])
    4) OPTIONAL: A csv file with the coloring list for the alpscarf tool ([AOI],[AOI_order],[color]) and with the mapping of AOIS to functions

    The program will also output to stdout which AOI's number map to which file

    Usage:
    python3 genVisualData.py <path to jsonFiles> <path to csvFiles> <participantName> OPTIONAL<fileToColorMatching>

    Requirements:
    pandas module
    glob module
    csvPath and jsonPath directories only contain csv and json files generated from itrace post
"""
def main():

    
    argc = len(sys.argv)
    argv = sys.argv
    
    #Check to make sure the user has the right input
    if(argc != 4 and argc != 5 ):
        print("Usage python3 genVisualData.py <path to jsonFiles> <path to csvFiles> <participantID> OPTIONAL<fileForColorAndFunctionMapping>")
        exit(1)

    #Create the paths as strings
    jsonPath = str(sys.argv[1])
    csvPath = str(sys.argv[2])
    inName = -1

    try:
        inName = int(sys.argv[3])
    except ValueError:
        print("Error: Participant ID must be an integer")
        exit(1)
        
    inName = "P" + str(inName)
    colorMatching = None
    myDictAOItoFunc = None

    #If the user wants to create the colors.csv, they will pass in an ordering 
    if(argc == 5):
        colorMatching,myDictAOItoFunc = parseAOI_Func_Color(argv[4])
    
    #print(colorMatching)
    #print(myDictAOItoFunc)
    
            
    #Check if the jsonFiles path and csvFiles path exist
    if(not os.path.isdir(jsonPath) or not os.path.isdir(csvPath)):
        print("Error: Either " + jsonPath + " or " + csvPath + " does not exist")
        exit(1)

    #Create the csvs
    createAllCSV(jsonPath, csvPath,colorMatching,inName,dictAOItoFunc=myDictAOItoFunc)



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


