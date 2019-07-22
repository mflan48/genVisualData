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
    return (datetime.datetime.strptime(timeStamp, "%Y-%m-%d %H:%M:%S.%f")).timestamp() - startValue

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


#JUST GET THE ORIGNAL MINESWEEPER FILE NAME AND ADD .java
#how we store the 
def getFileNameFromPath(filePath):
    #split path to just get the file then just get the file.java
    return(os.path.split(filePath)[1].split(".")[0] + ".java")
        #fileName.split(".")[0] + ".java")



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





def createScatter(combinedDF,timeCol="fix_time",interestCol="AOI",removeWhite = True):
    #assert that timeCol and interestCol are in combinedDF
    if(not timeCol in combinedDF.columns or not interestCol in combinedDF.columns):
        print("Error: Either " + timeCol + " or " + interestCol + " does not exist in the combined")
        exit(1)
    
    #remove the whitespace
    scatterDF = combinedDF.copy()
    if(removeWhite):
        scatterDF = scatterDF[scatterDF["AOI"] != -1]
    
    #firstTime = convertTimeStamp(str(scatterDF[timeCol].iloc[0]))
    #scatterDF[timeCol] = scatterDF[timeCol].apply(lambda x: convertTimeStamp(str(x),firstTime))

    #only get the fix_time and AOI
    scatterDF = scatterDF[[timeCol,interestCol]]
    return(scatterDF)

def createAlpscarf(combinedDF,partName,durationCol="fix_dur",interestCol = "function",removeWhite = True):

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

    return(alpDF)

def createRadial(combinedDF,partName,interestCol="function",stimulusCol="which_file",durationCol="fix_dur",removeWhite = True):
    
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
    
    return(radialDF)


#funcToColor is a dicionary {functionaName:color} OR {aoi:color}
#if funcToColor is {aoi:color} it must be the ADJUSTED AOI numbers
#The color must be in the right format (must be "#454545")
def createColors(combinedDF,funcToColor,interestCol="function"):
    
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
    return(colorsDF)


def createMultiMatch(combinedDF,durationCol="fix_dur",pixXCol="pixel_x",pixYCol="pixel_y",removeWhite=True):
    multiDF = combinedDF.copy()
    if(removeWhite):
        multiDF = multiDF[multiDF["AOI"]!=-1]
    multiDF = multiDF[[pixXCol,pixYCol,durationCol]]
    multiDF.loc[:,durationCol] = multiDF.loc[:,durationCol]*(10**-3)
    multiDF = multiDF.rename(index=str,columns={durationCol:"duration",pixXCol:"start_x",pixYCol:"start_y"})
    return(multiDF)

#Create all of the files with the right options in the phaseDF
#phaseDF must contain a column that has the phase number in it
#OutputPath must not contain final "/"
def createPhase(phaseDF,outputPath,partID,isColors:str=None,isAlpScarf:str=None,isRadial:str=None,isStimulus:str=None):
    
    #file path Prefix
    prefix = outputPath + "/" + partID + "_"
    
    #Check if we should create the colors file
    if(isColors != None):
        temp = createFuncToColor(isColors)
        colorsDF = createColors(phaseDF,temp)
        colorsDF.to_csv(prefix+ "colors.csv",index=False)
    
    #Create the alpscarf
    alpScarfDF = None
    if(isAlpScarf != None):
        alpScarfDF = createAlpscarf(phaseDF,partID,interestCol=isAlpScarf)
    else:
        alpScarfDF = createAlpscarf(phaseDF,partID)
    alpScarfDF.to_csv(prefix+"alpscarf.csv",index=False)


    #Create radial
    radialDF = None
    if(isRadial == None and isStimulus == None):
        radialDF = createRadial(phaseDF,partID)
    elif(isRadial != None and isStimulus == None):
        radialDF = createRadial(phaseDF,partID,interestCol=isRadial)
    elif(isRadial == None and isStimulus != None):
        radialDF = createRadial(phaseDF,partID,stimulusCol=isStimulus)
    else:
        radialDF = createRadial(phaseDF,partID,stimulusCol=isStimulus,interestCol=isRadial)
    radialDF.to_csv(prefix+"radial.csv",index=False)

    #Create scatter
    scatterDF = createScatter(phaseDF)
    scatterDF.to_csv(prefix+"scatter.csv",index=False)
    
    #Create multimatch
    multiDF = createMultiMatch(phaseDF)
    multiDF.to_csv(prefix+"mulitMatch.csv",index=False)

#The mergedDF represents a dataframe that has all of the times converted
#This will create three data frames that have an extra column that indicates what phase they are on
def parseMergeCSV(mergedDF,endPhase0,endPhase1,timeCol="fix_time"):
    phaseZeroDF = None
    phaseOneDF = None
    phaseTwoDF = None


    phaseZeroDF = mergedDF.loc[mergedDF[timeCol] < endPhase0].copy()
    phaseOneDF = mergedDF.loc[ (endPhase0 <= mergedDF[timeCol]) & (mergedDF[timeCol] < endPhase1)].copy()
    phaseTwoDF = mergedDF.loc[endPhase1 <= mergedDF[timeCol]].copy()
    phaseZeroDF["Phase"] = "Phase0"
    phaseOneDF["Phase"] = "Phase1"
    phaseTwoDF["Phase"] = "Phase2"
    """    
    print(phaseZeroDF)
    print(phaseOneDF)
    print(phaseTwoDF)
    """
    return(phaseZeroDF,phaseOneDF,phaseTwoDF)

def createMergeDF(csvFile,timeCol="fix_time",durCol="fix_dur"):
    #Read in the csv and convert the timestamps to unix time and convert the duration column to millisec
    mergedDF = pd.read_csv(csvFile)
    #mergedDF[timeCol] = mergedDF[timeCol].apply(lambda x: convertTimeStamp(str(x)))
    mergedDF[durCol] = mergedDF[durCol]*(10**-6)
    return(mergedDF)


def main():

    #getopt stuff 
    try:
        options,arguments = getopt.getopt(sys.argv[1:],"hp:c:a:r:s:i:z:o:t:e:f:",["help","path=","colors=","alpscarf=","radial=","stimulus=","id=","zeroDir=","oneDir=","twoDir=","endPhaseZero=","finishPhaseOne="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        exit(1)
    
    #Variables for the graphs
    inputPath = None

    #Variables for directories to each phase output
    zeroDir = None
    oneDir = None
    twoDir = None

    endTime0 = None
    endTime1 = None

    partID=None
    colorsFile=None
    alpScarfAOI=None
    radialInterest=None
    radialStimulus=None
    if(len(options) == 0):
        usage()
        exit(1)
    
    #Take care of the options
    for opt,arg in options:
        if(opt in ("-p","--path")):
            inputPath = arg
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
        elif(opt in ("-z","--zeroDir")):
            zeroDir = arg
        elif(opt in ("-o","--oneDir")):
            oneDir = arg
        elif(opt in ("-t","--twoDir")):
            twoDir = arg
        elif(opt in ("-e","--endPhaseZero")):
            endTime0 = arg
        elif(opt in ("-f","--finishPhaseOne")):
            endTime1 = arg
        elif(opt in ("-h","--help")):
            usage()
            exit(1)
        else:
            assert False, "unhandled option"
    
    #Check to make sure a file was passed in 
    if(inputPath == None):
        print("Error: The -p option was not used. This is a required argument, see usage for more details")
        exit(1)
    elif(not os.path.exists(inputPath)):
        print("Error: " + inputPath + " is not a valid path")
        exit(1)

    #Check to make sure all the putput directories exist
    if(zeroDir ==None):
        print("Error: The -z option was not used. This is a required argument, see usage for more details")
        exit(1)
    elif(not os.path.exists(zeroDir)):
        print("Error: " + zeroDir + " does not exist. Exiting program")
        exit(1)

    if(oneDir == None):
        print("Error: The -o option was not used. This is a required argument, see usage for more details")
        exit(1)
    elif(not os.path.exists(oneDir)):
        print("Error: " + oneDir + " does not exist. Exiting program")
        exit(1)

    if(twoDir == None):
        print("Error: The -t option was not used. This is a required argument, see usage for more details")
        exit(1)
    elif(not os.path.exists(twoDir)):
        print("Error: " + twoDir + " does not exist. Exiting program")
        exit(1)
    
    #Check to make sure the end times were passed in and that they are ints
    if(endTime0 == None):
        print("Error: The -e option was not used. This is a required argument, see usage for more details")
        exit(1)
    if(endTime1 == None):
        print("Error: The -f option was not used. This is a required argument, see usage for details")
        exit(1)

    if(partID == None):
        print("Error: The -i option was not used. This is a required argument, see usage for more details")
        exit(1)
    else:
        #make sure the partID is still an integer
        try:
            int(partID)
        except ValueError:
            print("Participant ID must be an integer")
            exit(1)
    

    #Modify the ID to be of form Pid
    partID = "P" + str(partID)

    #Check if the two end times are valid
    if(endTime0 == None):
        print("Error: The -e option was not used. This is a required argument, see usage for more details")
        exit(1)
    else:
        try:
            int(endTime0)
        except ValueError:
            print("EndPhase0 must be an integer")
            exit(1)

    if(endTime1 == None):
        print("Error: The -f option was not used. This is a required argument, see usage for more details")
        exit(1)
    else:
        try:
            int(endTime1)
        except ValueError:
            print("finishPhase1 must be an integer")
            exit(1)
    
    #Convert them to ints
    endTime0 = int(endTime0)
    endTime1 = int(endTime1)

    #Modify the input/output paths to not included the final /
    inputPath = modPathName(inputPath)
    zeroDir = modPathName(zeroDir)
    oneDir = modPathName(oneDir)
    twoDir = modPathName(twoDir)


    #Create the mergedDF by reading in the file from the input path
    mergedDF = createMergeDF(inputPath)
    phase0,phase1,phase2 = parseMergeCSV(mergedDF,endPhase0 = endTime0,endPhase1 = endTime1)
    createPhase(phase0,zeroDir,partID,isColors=colorsFile,isAlpScarf=alpScarfAOI,isRadial=radialInterest,isStimulus=radialStimulus)
    createPhase(phase1,oneDir,partID,isColors=colorsFile,isAlpScarf=alpScarfAOI,isRadial=radialInterest,isStimulus=radialStimulus)
    createPhase(phase2,twoDir,partID,isColors=colorsFile,isAlpScarf=alpScarfAOI,isRadial=radialInterest,isStimulus=radialStimulus)


def modPathName(pathName):
    return(pathName if pathName[len(pathName)-1] != "/" else pathName[0:len(pathName)-1])


def usage():
    print("----------Description----------\n")
    print("This script is used to generate data for the following: alpscarf tool, radial transition graph tool, scatter plots, multimatch tool." + 
            " It creates these csv files from the merged_data.csv file that is created for each bug for each participant in the iTracePost Module." + 
            " For our experiment, we are splitting the merged_data into three 'phases'. These phases are 1)finding initial points" +
            "2)building on initial points and 3)Fixing the bug.  In order to split the data up this way, two epoch times are passed in as" +
            "command line arguments 'endPhaseZero' and 'finishPhaseOne', where they represent the end time of phase 0 and" +
            "end time of phase 1. After each phase is created, the csv data files for all of the tools/strategies will be created" +
            "for each phase. This will be stored in the passed in arguments 'zeroDir', 'oneDir', and 'twoDir'.\n")

    print("----------Required Arguments----------\n")
    print("-p --path: requires a path to csv file that contains the merged data from iTracePost. This is a REQUIRED argument")
    print("-i --id: requires an int that represents the id of the participant. This is a REQUIRED argument")
    print("-z --zeroDir: requires a path to the directory that will hold the information for Phase Zero data created by the script. This is a REQUIRED argument")
    print("-o --oneDir: requires a path to the directory that will hold the information for Phase One data created by the script. This is a REQUIRED argument")
    print("-t --twoDir: requires a path to the directory that will hold the information for Phase Two data created by the script. This is a REQUIRED argument")
    print("-e --endPhaseZero: requires an epoch time that represents the time phase zero has ended and phase one has started for this participant. This is a REQUIRED argument")
    print("-f --finishPhaseOne: requires an epoch time that represents the time phase one has ended and phase two has started for this participant. This is a REQUIRED argument")
    print("\n")
    print("----------Optional Arguments----------\n")
    print("-c --colors: requires a text file that contains a mapping of functions to hex colors. This is an OPTIONAL argument")
    print("-a --alpscarf: requires a string that indicates that the alpscarf plot data should be generate with the AOI column as the passed in argument. This is an OPTIONAL argument")
    print("-r --radial: requires a string that indicates the radial data should be generated with the AOIName column as the passed in argument. This is an OPTIONAL argument")
    print("-s --stimulus: requires a string that indicates the radial data should be genreate with the stimulus column as the passed in argument. This is an OPTIONAL argument")
    print("-h --help: displays this message\n")
if __name__ == '__main__':
    main()
