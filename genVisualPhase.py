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
#OutputPath must not contain final "/"
def createOnePhase(phaseDF,outputPath,partID,isColors:str=None,isAlpScarf:str=None,isRadial:str=None,isStimulus:str=None):
    
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

    print(mergedDF[timeCol] < endPhase0)

    phaseZeroDF = mergedDF.loc[mergedDF[timeCol] < endPhase0].copy()
    phaseOneDF = mergedDF.loc[ (endPhase0 <= mergedDF[timeCol]) & (mergedDF[timeCol] < endPhase1)].copy()
    phaseTwoDF = mergedDF.loc[endPhase1 <= mergedDF[timeCol]].copy()
    phaseZeroDF["Phase"] = "Phase0"
    phaseOneDF["Phase"] = "Phase1"
    phaseTwoDF["Phase"] = "Phase2"
    print(phaseZeroDF)
    print(phaseOneDF)
    print(phaseTwoDF)
    return(phaseZeroDF,phaseOneDF,phaseTwoDF)

def createMergeDF(csvFile,timeCol="fix_time",durCol="fix_dur"):
    mergedDF = pd.read_csv(csvFile)
    mergedDF[timeCol] = mergedDF[timeCol].apply(lambda x: convertTimeStamp(str(x)))
    mergedDF[durCol] = mergedDF[durCol]*(10**-6)
    print(mergedDF[timeCol].iloc[0])
    return(mergedDF)


def main():

    #getopt stuff 
    try:
        options,arguments = getopt.getopt(sys.argv[1:],"hc:a:r:s:i:o:",["help","colors=","alpscarf=","radial=","stimulus=","id=","output="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        exit(1)
    
    #Variables for the graphs
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
        if(opt in ("-c,--colors")):
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

    #Modify the output path to not included the final /
    outputPath = modPathName(outputPath)

    
    #Create the output directory if it doesnt exist
    if(not os.path.exists(outputPath)):
        print("Output directory does not exist so one will be created at path " + outputPath)
        os.makedirs(outputPath)

    temp = createMergeDF("./merged_data.csv")
    phase1,phase2,phase3 = parseMergeCSV(temp,1563386418151,1563388213657)
    #print(phase1)
    #createOnePhase(testDF,outputPath,partID,isColors=colorsFile,isAlpScarf=alpScarfAOI,isRadial=radialInterest,isStimulus=radialStimulus)






    
def modPathName(pathName):
    return(pathName if pathName[len(pathName)-1] != "/" else pathName[0:len(pathName)-1])


def usage():
    print("Command line options for getopt\n")
    print("-c --colors: requires a text file that contains a mapping of functions to hex colors")
    print("-a --alpscarf: requires a string that indicates that the alpscarf plot data should be generate with the AOI column as the passed in argument")
    print("-r --radial: requires a string that indicates the radial data should be generated with the AOIName column as the passed in argumenet")
    print("-s --stimulus: requires a string that indicates the radial data should be genreate with the stimulus column as the passed in argument")
    print("-i --id: requires an int that represents the id of the participant")
    print("-o --output: requires a path to directory where the 'output' subdirectory will be created that stores all of the files")
    print("-h --help: displays this message")
if __name__ == '__main__':
    main()
