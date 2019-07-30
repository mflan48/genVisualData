from genVisualPhase import *
import os
import glob
from collections import defaultdict
import re
import csv



def main():

    largeTime = 9999999999999

    part102 = PartTrial(pathToData="processed_data/P102/bug1/merged_data.csv",pathToOut1="./Bug1_Output/Phase1",pathToOut2="./Bug1_Output/Phase2"
        ,pathToOut3="./Bug1_Output/Phase3",timeTuple=(1563562294634,1563562897067),ID="P102")

    part103 = PartTrial(pathToData="processed_data/P103/bug1/merged_data.csv",pathToOut1="./Bug1_Output/Phase1",pathToOut2="./Bug1_Output/Phase2"
        ,pathToOut3="./Bug1_Output/Phase3",timeTuple=(1563826245007,1563826812264),ID="P103")

    part105 = PartTrial(pathToData="processed_data/P105/bug1/merged_data.csv",pathToOut1="./Bug1_Output/Phase1",pathToOut2="./Bug1_Output/Phase2"
        ,pathToOut3="./Bug1_Output/Phase3",timeTuple=(1563976958363, largeTime),ID="P105")

    part106 = PartTrial(pathToData="processed_data/P106/bug1/merged_data.csv",pathToOut1="./Bug1_Output/Phase1",pathToOut2="./Bug1_Output/Phase2"
        ,pathToOut3="./Bug1_Output/Phase3",timeTuple=(1564063779601,1564064007823),ID="P106")

    part201 = PartTrial(pathToData="processed_data/P201/bug1/merged_data.csv",pathToOut1="./Bug1_Output/Phase1",pathToOut2="./Bug1_Output/Phase2"
        ,pathToOut3="./Bug1_Output/Phase3",timeTuple=(1563464280705,1563464828802),ID="P201")

    part202 = PartTrial(pathToData="processed_data/P202/bug1/merged_data.csv",pathToOut1="./Bug1_Output/Phase1",pathToOut2="./Bug1_Output/Phase2"
        ,pathToOut3="./Bug1_Output/Phase3",timeTuple=(1563553936859,1563554256514),ID="P202")
            
    part203 = PartTrial(pathToData="processed_data/P203/bug1/merged_data.csv",pathToOut1="./Bug1_Output/Phase1",pathToOut2="./Bug1_Output/Phase2"
        ,pathToOut3="./Bug1_Output/Phase3",timeTuple=(1563986919996,1563987376814),ID="P203")

    part204 = PartTrial(pathToData="processed_data/P204/bug1/merged_data.csv",pathToOut1="./Bug1_Output/Phase1",pathToOut2="./Bug1_Output/Phase2"
        ,pathToOut3="./Bug1_Output/Phase3",timeTuple=(1563902610406,1563902773703),ID="P204")

    part205 = PartTrial(pathToData="processed_data/P205/bug1/merged_data.csv",pathToOut1="./Bug1_Output/Phase1",pathToOut2="./Bug1_Output/Phase2"
        ,pathToOut3="./Bug1_Output/Phase3",timeTuple=(1563893868347, largeTime),ID="P205")

    part206 = PartTrial(pathToData="processed_data/P206/bug1/merged_data.csv",pathToOut1="./Bug1_Output/Phase1",pathToOut2="./Bug1_Output/Phase2"
        ,pathToOut3="./Bug1_Output/Phase3",timeTuple=(1564006098289,1564006333456),ID="P206")

    part207 = PartTrial(pathToData="processed_data/P207/bug1/merged_data.csv",pathToOut1="./Bug1_Output/Phase1",pathToOut2="./Bug1_Output/Phase2"
            ,pathToOut3="./Bug1_Output/Phase3",timeTuple=(1564076425290, 1564076670887),ID="P207")

    part208 = PartTrial(pathToData="processed_data/P208/bug1/merged_data.csv",pathToOut1="./Bug1_Output/Phase1",pathToOut2="./Bug1_Output/Phase2"
            ,pathToOut3="./Bug1_Output/Phase3",timeTuple=(1564083265380, 1564083358841),ID="P208")

    part301 = PartTrial(pathToData="processed_data/P301/bug1/merged_data.csv",pathToOut1="./Bug1_Output/Phase1",pathToOut2="./Bug1_Output/Phase2"
            ,pathToOut3="./Bug1_Output/Phase3",timeTuple=(1564087432075, 1564087668731),ID="P301")
    

    listPart = [part102,part103,part105,part106,part201,part202,part203,part204,part205,part206,part207,part208,part301]
    phaseDict={"isRadial":"entity","isAlpScarf":"entity","isColors":"mapEntityColor.txt"}
    transDict={}
    distDict={}

    myExp = Experiment("./processed_data","./PhaseChanges.csv","./Bug1_Output","./Bug2_Output",phaseDict=phaseDict,transDict=transDict,distDict=distDict)
    myExp.runAllParticipants()


#listDataFiles,listTimes,listID,listOut
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
        
        transMatrix1.to_csv("B1_WNone_TransitionMatrix.csv",index=False)
        distMatrix1.to_csv("B1_WNone_DistributionMatrix.csv",index=False)

        transMatrix2.to_csv("B2_WNone_TransitionMatrix.csv",index=False)
        distMatrix2.to_csv("B2_WNone_DistributionMatrix.csv",index=False)
        
      
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
                endPhase1 = row[end1Col] #if(row[end1Col] != -1) else 9999999999998 #If the entry is -1, that means the time did not exist
                endPhase2 = row[end2Col] #if(row[end2Col] != -1) else 9999999999999
                if(curBug not in toReturn):
                    toReturn[curBug] = {}
                toReturn[curBug][curPart] = (int(endPhase1),int(endPhase2))
        return(toReturn)





if __name__ == "__main__":
    main()




