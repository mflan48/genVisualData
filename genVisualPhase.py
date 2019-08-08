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
    AOI_myStrX
"""
def convertAOI(myStrX):
    return ("AOI_" + str(myStrX))

"""
    Convert a hex color to the hex color format for alpscarf

    Parameters:
    myColor: str :a string of the hex color

    Return:
    The hex color in the right format for the colors.csv
"""
def convertColor(myColor):
    return ( ("\"" + "#"+str(myColor) + "\"" ) if myColor[0] != '#' else ("\"" + str(myColor) + "\"") )


#JUST GET THE ORIGNAL MINESWEEPER FILE NAME AND ADD .java
def getFileNameFromPath(filePath):
    #split path to just get the file then just get the file.java
    return(os.path.split(filePath)[1].split(".")[0] + ".java")

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

def createScatter(phaseDF,timeCol="fix_time",interestCol="AOI"):
    #assert that timeCol and interestCol are in phaseDF
    if(not timeCol in phaseDF.columns or not interestCol in phaseDF.columns):
        print("Error: Either " + timeCol + " or " + interestCol + " does not exist in the combined")
        exit(1)
    
    scatterDF = phaseDF.copy()
    #only get the fix_time and AOI
    scatterDF = scatterDF[[timeCol,interestCol]]
    return(scatterDF)

def createAlpscarf(phaseDF,partName,durationCol="fix_dur",interestCol = "function"):

    #assert that timeCol and interestCol are in phaseDF
    if(not durationCol in phaseDF.columns or not interestCol in phaseDF.columns):
        print("Error: Either " + durationCol + " or " + interestCol + " does not exist in the combined")
        exit(1)
    
    alpDF = phaseDF.copy()
    
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

def createRadial(phaseDF,partName,interestCol="function",stimulusCol="which_file",durationCol="fix_dur"):
    
    #Ensure that all the columns exist within phaseDF
    if(not (interestCol in phaseDF.columns and stimulusCol in phaseDF.columns and durationCol in phaseDF.columns)):
        print("Error: One or more of the following does not exist in the phaseDF")
        print(interestCol + " " + stimulusCol + " " + durationCol)
        exit(1)
    
    radialDF = phaseDF.copy()

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
def createColors(phaseDF,funcToColor,interestCol="entity"):
    
    #Check if the columns exist in the combined DF
    if(not interestCol in phaseDF.columns):
        print("Error: " + interestCol + " does not exist in the phaseDF")
        exit(1)
    

    #get all of the unique values interestCol values in the data frame,
    interestVals = sorted(phaseDF[interestCol].unique())

    expectedOrder = list(range(1,len(interestVals)+1))
    colorsVect = []

    #Search thru all of the values in the interestCol and get their color from the funcToColor dictionart
    for curVal in interestVals:
        if(str(curVal) in funcToColor):
            colorsVect.append(funcToColor[curVal])
        else:
            print("Error: " + str(curVal) + " was in the " + str(interestCol) + " of the phaseDF but did not exist in the funcToColor dicionary")
            print("Double check the file that is used to generate the funcToColor dictionary to ensure that all functions/AOI's are accounted for")
            exit(1)

    #Create the file
    colorsDF = pd.DataFrame()
    colorsDF["AOI"] = interestVals
    colorsDF["AOI_order"] = expectedOrder
    colorsDF["color"] = colorsVect
    return(colorsDF)

def createMultiMatch(phaseDF,durationCol="fix_dur",pixXCol="pixel_x",pixYCol="pixel_y"):
    multiDF = phaseDF.copy()
    multiDF = multiDF[[pixXCol,pixYCol,durationCol]]
    multiDF.loc[:,durationCol] = multiDF.loc[:,durationCol]*(10**-3)
    multiDF = multiDF.rename(index=str,columns={durationCol:"duration",pixXCol:"start_x",pixYCol:"start_y"})
    return(multiDF)

#Create all of the files with the right options in the phaseDF
#phaseDF must contain a column that has the phase number in it
#OutputPath must not contain final "/"
def createSinglePhase(phaseDF,outputPath,partID,phaseNumber,isColors=None,isAlpScarf=None,isRadial=None,isStimulus=None):
    
    #file path Prefix
    prefix = outputPath + "/" + partID + "_Phase" + str(phaseNumber) + "_"
    
    #Check if we should create the colors file
    if(isColors != None):
        temp = createFuncToColor(isColors)
        colorsDF = createColors(phaseDF,temp)
        colorsDF.to_csv(prefix+ "colors.csv",index=False,quotechar ='\'')
    
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
    multiDF.to_csv(prefix+"multiMatch.tsv",index=False,sep='\t')

#The mergedDF represents a dataframe that has all of the times converted
#This will create three data frames that have an extra column that indicates what phase they are on
def parseMergeCSV(mergedDF,endPhase0,endPhase1,timeCol="fix_time",entityCol="entity",removeWhite=True,removeNONE=False):
    phaseZeroDF = None
    phaseOneDF = None
    phaseTwoDF = None

    copiedDF = mergedDF.copy()
    copiedDF = copiedDF.astype({timeCol:'int64'})


    phaseZeroDF = copiedDF.loc[copiedDF[timeCol] < endPhase0].copy()
    phaseOneDF = copiedDF.loc[ (endPhase0 <= copiedDF[timeCol]) & (copiedDF[timeCol] < endPhase1)].copy()
    phaseTwoDF = copiedDF.loc[endPhase1 <= copiedDF[timeCol]].copy()

    if(removeWhite):
        phaseZeroDF = phaseZeroDF[phaseZeroDF["AOI"]!=-1]
        phaseOneDF = phaseOneDF[phaseOneDF["AOI"]!=-1]
        phaseTwoDF = phaseTwoDF[phaseTwoDF["AOI"]!=-1]
    if(removeNONE):
        phaseZeroDF = phaseZeroDF[phaseZeroDF[entityCol]!="NONE"]
        phaseOneDF = phaseOneDF[phaseOneDF[entityCol]!="NONE"]
        phaseTwoDF = phaseTwoDF[phaseTwoDF[entityCol]!="NONE"]


    phaseZeroDF["Phase"] = "Phase0"
    phaseOneDF["Phase"] = "Phase1"
    phaseTwoDF["Phase"] = "Phase2"

    return(phaseZeroDF,phaseOneDF,phaseTwoDF)

def createMergeDF(csvFile,timeCol="fix_time",durCol="fix_dur"):
    #Read in the csv and convert the timestamps to unix time and convert the duration column to millisec
    mergedDF = pd.read_csv(csvFile)
    #mergedDF[timeCol] = mergedDF[timeCol].apply(lambda x: convertTimeStamp(str(x)))
    mergedDF[durCol] = mergedDF[durCol]*(10**-6)
    return(mergedDF)

#listFix is the list of software entities visited in the correct order
#Return dataframe that is of following form
"""
    cols Memeber_Variable   Comment ...
    rows
    Member_Variable 0   0   ...  
    Comment 1   3   
    .
    .
    .
"""
def createTransMatrix(phaseDF, partID,phaseNum,entityCol=None, allEntity=None):
    
    #if any of the variables are passed in None, set the default values
    if(entityCol==None):
        entityCol="entity"
    if(allEntity==None):
        allEntity=["Member_Variable","Comment","Bug_Report","Class_Signature","Method_Body","Method_Signature","NONE"]
    
    if(not entityCol in phaseDF.columns):
        print("Error: The passed in entity column " + entityCol + " does not exist in the phaseDF")
        exit(1)
    #Get a list of all of the entities in the phaseDF
    listEntity = phaseDF.copy()[entityCol].tolist()
    colEntities = ["ParticipantID","Phase","Source"] + allEntity
    rowEntities = allEntity
    #Create the dataframe to return
    rowDF = pd.Index(rowEntities,name="rows")
    cols = pd.Index(colEntities,name="cols")
    toReturnDF = pd.DataFrame(0,columns=cols,index=rowDF)
    
    for i in range(0,len(listEntity)-1):
        src = listEntity[i]
        dest = listEntity[i+1]
        if(src not in rowEntities or dest not in rowEntities):
            print("Error: One of the following is not in the allEntity list")
            print("Pos. Entries: " + str(src) +  " : " + str(dest))
            print("rowEntity list = " + rowEntities)
            exit(1)
        if(src != dest):
            toReturnDF[src][dest] += 1
            toReturnDF[dest][src] += 1
    #Add a two columns 
    toReturnDF["ParticipantID"] = [str(partID)]*toReturnDF.shape[0]
    toReturnDF["Phase"] = [str(phaseNum)]*toReturnDF.shape[0]
    toReturnDF["Source"]= allEntity
    return(toReturnDF)

#Returns dictionary of percentages of time spend in the values in the wantEntity lsit
def createDistMatrix(phaseDF,partID,phaseNum,entityCol=None,durCol=None,wantEntity=None):
    
    #If non is passed in for any of the default values, update them
    if(entityCol==None):
        entityCol = "entity"
    if(durCol==None):
        durCol="fix_dur"
    if(wantEntity==None):
        wantEntity=["Member_Variable","Comment","Bug_Report","Class_Signature","Method_Body","Method_Signature","NONE"]

    if(not entityCol in phaseDF.columns):
        print("Error: The passed in entity column " + entityCol + " does not exist in the phaseDF")
        exit(1)
    if(not durCol in phaseDF.columns):
        print("Error: The passed in durCol " + durCol + " does not exist in phaseDF")
        exit(1)
    
    #Group the phaseDF by the entity columns
    groups = phaseDF.copy().groupby(entityCol)

    entityDict = {}
    totalTime = 0.0
    for name,curGroup in groups:
        curSum = curGroup[durCol].sum()
        totalTime += float(curSum)
        entityDict[name] = curSum

    toReturn = pd.DataFrame(columns=["ParticipantID","Phase"]+wantEntity)
    myDict = {}
    for key in wantEntity:
        if(not key in entityDict.keys()):
            myDict[key] = str(0) + '%'
        else:
            myDict[key] = str(round(entityDict[key]/totalTime*100,2)) + '%'
    myDict["ParticipantID"]=partID
    myDict["Phase"]=str(phaseNum)
    toReturn = toReturn.append(myDict,ignore_index=True)
    return(toReturn)


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
    #Variavles for the ending times of the phases
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
    createSinglePhase(phase0,zeroDir,partID,0,isColors=colorsFile,isAlpScarf=alpScarfAOI,isRadial=radialInterest,isStimulus=radialStimulus)
    createSinglePhase(phase1,oneDir,partID,1,isColors=colorsFile,isAlpScarf=alpScarfAOI,isRadial=radialInterest,isStimulus=radialStimulus)
    createSinglePhase(phase2,twoDir,partID,2,isColors=colorsFile,isAlpScarf=alpScarfAOI,isRadial=radialInterest,isStimulus=radialStimulus)


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
