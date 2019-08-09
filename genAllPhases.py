from genVisualPhase import *
import os
import glob
import re
import csv
import sys
import getopt

def modPathName(pathName):
    return(pathName if pathName[len(pathName)-1] != "/" else pathName[0:len(pathName)-1])

def main():
    try: 
        options,arguments = getopt.getopt(sys.argv[1:],"hp:c:d:o:t:",["help","processed=","changes=","dictPhaseFile=","one=","two="])
    except getopt.GetoptError as err:
        usage()
        print(err)
        exit(1)

    pathToProcessed = None
    pathToChanges = None
    pathToBug1 = None
    pathToBug2 = None
    phaseDict={"isRadial":"entity","isAlpScarf":"entity","isStimulus":"Phase","isColors":"mapEntityColor.txt"}
    transDict={}
    distDict={}

    for opt,arg in options:
        if(opt in ("-h","--help")):
            usage()
            exit(1)
        elif(opt in ("-p","--processed")):
            pathToProcessed = arg
        elif(opt in ("-c","--changes")):
            pathToChanges = arg
        elif(opt in ("-d","--dictPhaseFile")):
            phaseDict = readPhaseDict(arg)
        elif(opt in ("-o","--one")):
            pathToBug1 = arg
        elif(opt in ("-t","--two")):
            pathToBug2 = arg
        else:
            assert False, "unhandled option"
    
    #Check if the pathToProcessed was assigned and it exists
    if(pathToProcessed != None):
        if(not os.path.exists(pathToProcessed) ):
            print("Error: " + pathToProcessed + " does not exist")
            exit(1)
    else:
        print("Error: The -p option was not used and is required")
        exit(1)
    
    #Check if pathToChanges was assigned and it exist
    if(pathToChanges != None):
        if(not os.path.exists(pathToChanges)):
            print("Error: " + pathToProcessed + " does not exist")
            exit(1)
    else:
        print("Error: The -c option was not used and is required")
        exit(1)
    
    #Check if path to bug1 was assigned and it exists
    if(pathToBug1 != None):
        if(not os.path.exists(pathToBug1)):
            print("Error: " + pathToBug1 + " does not exists")
            exit(1)
    else:
        print("Error: the -o option was not used and is required")
        exit(1)
    
    #Check if path to bug2 was assigned and it exists
    if(pathToBug2 != None):
        if(not os.path.exists(pathToBug2)):
            print("Error: " + pathToBug2 + " does not exists")
            exit(1)
    else:
        print("Error: the -t option was not used and is required")
        exit(1)
    
    pathToProcessed = modPathName(pathToProcessed)
    pathToBug1 = modPathName(pathToBug1)
    pathToBug2 = modPathName(pathToBug2)
    
    toRunExp = Experiment(pathToProcessed,pathToChanges,pathToBug1,pathToBug2,phaseDict,transDict,distDict)
    toRunExp.runAllParticipants()


#Files must be of type Command Line Option long : Value
def readPhaseDict(fileName):
    toReturn = {}
    try:
        with open(fileName, "r") as inFile:
            contents = inFile.readlines()
            for row in contents[1:]:
                splitted = row.split(":")
                if(not splitted[0] in toReturn.keys()):
                    toReturn[splitted[0]] = splitted[1]
                else:
                    print("Error: Multiple options exist in readPhaseDict")
                    exit(1)
    except FileNotFoundError as err:
        print(err)
        exit(1)
    return(toReturn)

def usage():
    print("----------Description----------\n")
    print("This script is used to generate visual data for all the participants. It will create data for each bug and for each phase in each bug." + 
            "For each of those, it will create files for the following: alpscarf tool, radial transition graph tool, scatter plots, multimatch tool." + 
            "It creates these csv files from the merged_data.csv file that is created in the iTracePost Module." + 
            "For our experiment, we are splitting the merged_data into three 'phases'. These phases are 1)finding initial points" +
            "2)building on initial points and 3)Fixing the bug.  In order to split the data up this way, two epoch times are needed" +
            "These times should be located in a CSV file with the following header\n\n" +
            "Participant,Trial,endPhase1,endPhase2\n\n"+
            "This program also requires a path to a 'processed data' directory that contains all of the merged_data files" +
            "This directory must have the following structure" +
            "Processed_directory only contains subdirectories that represent participants"+
            "For each of th participants directories, it must only contain directories 'bug1' or bug2'"+
            "For each of the bug1 or bug2 directories, it will search for a merged_data.csv file.\n\n" + 
            "The program also requires two output directories, one for each bug. These directories can be based in with the -o and -t option"+
            "Each of these directories must contain three subdirectories named 'Phase1','Phase2','Phase3'\n"
        )

    print("----------Required Arguments----------\n")
    print("-p, --processed : a path to the processed directory that has the structure described above")
    print("-c, --changes : a path to a csv file that contains the times of the phases changes")  
    print("-o,--one : a path to a directory to store the bug1 output")  
    print("-t,--two : a path to a directory to store the bug2 output\n")  

    print("----------Optional Arguments----------\n")
    print("-d, --dictPhaseFile : a file that has the following format\n")
    print("OptionForPhaseDict:Value\n")
    print("This file represents the options that the output files can be created with."+ 
        "the default value will be\n isRadial:entity,isAlpScarf:entity,isStimulus:Phase,isColors:mapEntityColor.txt")

    print("\n")
    print("----------Arguments for PhaseDict Text File----------\n")
    print("isColors: a text file that contains a mapping of functions to hex colors")
    print("isAlpScarf: a string that indicates that the alpscarf plot data should be generate with the AOI column as the passed in argument")
    print("isRadial: a string that indicates the radial data should be generated with the AOIName column as the passed in argument")
    print("isStimulus: a string that indicates the radial data should be genreate with the stimulus column as the passed in argument\n")

class PartTrial:

    def __init__(self,pathToData,pathToOut1,pathToOut2,pathToOut3,timeTuple,ID):
        
        self.pathToData = pathToData
        self.pathToOut1 = pathToOut1
        self.pathToOut2 = pathToOut2
        self.pathToOut3 = pathToOut3
        self.timeTuple = timeTuple
        self.ID = ID
        mergedDF = createMergeDF(pathToData)
        self.phase1, self.phase2, self.phase3 = parseMergeCSV(mergedDF,endPhase0=timeTuple[0],endPhase1=timeTuple[1])
    
    #Create the visual datadistribution matr
    def runParticipant(self,transDF,distDF,phaseDict,transDict,distDict):
        print("Running runParticipant for partTrial with ID=" + self.ID)
        self.createAllPhases(**phaseDict)
        temp = self.createAllTransMatrix(**transDict)
        temp2 = self.createAllDistMatrix(**distDict)
        updateTransDF = pd.concat([transDF,temp],ignore_index=True)
        updateDistDF = pd.concat([distDF,temp2],ignore_index=True)
        return(updateTransDF,updateDistDF)

    #kwargs represents isColors,isAlpScarf,isRadial,isStimulus
    def createAllPhases(self,isColors=None,isAlpScarf=None,isRadial=None,isStimulus=None):

        createSinglePhase(self.phase1,self.pathToOut1,self.ID,1,isColors=isColors,isAlpScarf=isAlpScarf,isRadial=isRadial,isStimulus=isStimulus)
        createSinglePhase(self.phase2,self.pathToOut2,self.ID,2,isColors=isColors,isAlpScarf=isAlpScarf,isRadial=isRadial,isStimulus=isStimulus)
        createSinglePhase(self.phase3,self.pathToOut3,self.ID,3,isColors=isColors,isAlpScarf=isAlpScarf,isRadial=isRadial,isStimulus=isStimulus)

    #**kawgs can be entityCol or allEntity
    #Return the concatenated dataframe of the three transition matrixes
    def createAllTransMatrix(self,entityCol=None,allEntity=None):

        trans1 = createTransMatrix(self.phase1,self.ID,1,entityCol=entityCol,allEntity=allEntity)
        trans2 = createTransMatrix(self.phase2,self.ID,2,entityCol=entityCol,allEntity=allEntity)
        trans3 = createTransMatrix(self.phase3,self.ID,3,entityCol=entityCol,allEntity=allEntity)
        return(pd.concat([trans1,trans2,trans3],ignore_index=True))

    #Return concatenated dataframe of the three distribtuion matrices
    def createAllDistMatrix(self,entityCol=None,wantEntity=None):
        dist1 = createDistMatrix(self.phase1,self.ID,1,entityCol=entityCol,wantEntity=wantEntity)
        dist2 = createDistMatrix(self.phase2,self.ID,2,entityCol=entityCol,wantEntity=wantEntity)
        dist3 = createDistMatrix(self.phase3,self.ID,3,entityCol=entityCol,wantEntity=wantEntity)
        return(pd.concat([dist1,dist2,dist3],ignore_index=True))


class Experiment:

    def __init__(self,pathProcessed,csvTimes,bugOneOut,bugTwoOut,phaseDict,transDict={},distDict={}):
        self.pathProcessed = pathProcessed
        self.csvTimes = csvTimes
        self.bugOneOut = bugOneOut
        self.bugTwoOut = bugTwoOut
        self.phaseDict = phaseDict
        self.transDict = transDict
        self.distDict = distDict
        self.partBug1,self.partBug2 = self.createAllParticipants()
        
    def createAllParticipants(self):
        dictBug = self.getDictBug(self.pathProcessed)
        dictTimes = self.getDictTimes(self.csvTimes)

        listBug1 = []
        listBug2 = []
        #Create the list participants for bug1 and bug 2
        for curBug,IDS in dictBug.items():
            for curID,path in IDS.items():
                print("Creating partTrial with bug=" + curBug + " ID="+curID)
                curTup=None
                #Try to get the time tuple and thorw error if cant
                try:
                    curTup = dictTimes[curBug][curID]
                except KeyError:
                    print("Error: the keys " + curBug + " : " + curID + " does not exist in the time tuple")
                    exit(1)

                if(curBug == "bug1"):
                    p1 = self.bugOneOut + "/Phase1/"
                    p2 = self.bugOneOut + "/Phase2/"
                    p3 = self.bugOneOut + "/Phase3/"
                    tempPart = PartTrial(path,p1,p2,p3,curTup,curID)
                    listBug1.append(tempPart)
                elif(curBug == "bug2"):
                    p1 = self.bugTwoOut + "/Phase1/"
                    p2 = self.bugTwoOut + "/Phase2/"
                    p3 = self.bugTwoOut + "/Phase3/"  
                    tempPart = PartTrial(path,p1,p2,p3,curTup,curID)
                    listBug2.append(tempPart)
                else:
                    print("THIS SHOULD NEVER HAPPEN")
                    exit(1)
        return(listBug1,listBug2)

    def runAllParticipants(self):

        transMatrix1 = pd.DataFrame()
        distMatrix1 = pd.DataFrame()
        transMatrix2 = pd.DataFrame()
        distMatrix2 = pd.DataFrame()

        print("-----Running all participants for bug 1-----")
        for i in range(0,len(self.partBug1)):
            transMatrix1,distMatrix1= (self.partBug1)[i].runParticipant(transMatrix1,distMatrix1,self.phaseDict,self.transDict,self.distDict)
        
        print("-----Running all participants for bug 2-----")
        for j in range(0,len(self.partBug2)):
            transMatrix2,distMatrix2 = (self.partBug2)[j].runParticipant(transMatrix2,distMatrix2,self.phaseDict,self.transDict,self.distDict)
        
        transMatrix1.to_csv("B1_TransitionMatrix.csv",index=False)
        distMatrix1.to_csv("B1_DistributionMatrix.csv",index=False)

        transMatrix2.to_csv("B2_TransitionMatrix.csv",index=False)
        distMatrix2.to_csv("B2_DistributionMatrix.csv",index=False)
        
      
    #Return a dict of dict that represents the bug, then id, then path to data file for it
    def getDictBug(self,pathProcessed,globQuery="**/*merged_data.csv"):
        toReturn = {}
        allPaths = sorted(glob.glob(pathProcessed + "/" + globQuery,recursive=True))
        for curPath in allPaths:
            directories = curPath.split("/")
            curBug = ""
            curID = ""
            for curDir in directories:
                if(re.match(r"P[0-9]+",curDir)):
                    curID = curDir
                elif(re.match(r"bug[1-2]",curDir)):
                    curBug = curDir
            
            if(curBug == ""  and curID == ""):
                print("Error: The directory" + curPath + " does not contain either a participant ID or bug number")
                exit(1)
            if(curBug not in toReturn):
                toReturn[curBug] = {}
            toReturn[curBug][curID] = curPath
        return(toReturn)

    #Return a dict of dict that represents the bug, participant, and the time tulpe of its phase 1 and phase 2
    def getDictTimes(self,csvPath,partCol="Participant",bugCol="Trial",end1Col="endPhase1",end2Col="endPhase2"):
        toReturn = {}
        
        with open(csvPath,"r") as csvFile:
            csvreader = csv.DictReader(csvFile)
            for row in csvreader:
                curPart = row[partCol]
                curBug = row[bugCol]
                endPhase1 = row[end1Col] 
                endPhase2 = row[end2Col] 
                if(curBug not in toReturn):
                    toReturn[curBug] = {}
                toReturn[curBug][curPart] = (int(endPhase1),int(endPhase2))
        return(toReturn)



if __name__ == "__main__":
    main()
