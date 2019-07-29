from genVisualPhase import *
import os
import sys
import glob



#kwargs represents isColors,isAlpScarf,isRadial,isStimulus
def createAllPhases(phase1,phase2,phase3,partID,outputPath,isColors=None,isAlpScarf=None,isRadial=None,isStimulus=None):

    createSinglePhase(phase1,outputPath,partID,1,isColors=isColors,isAlpScarf=isAlpScarf,isRadial=isRadial,isStimulus=isStimulus)
    createSinglePhase(phase2,outputPath,partID,2,isColors=isColors,isAlpScarf=isAlpScarf,isRadial=isRadial,isStimulus=isStimulus)
    createSinglePhase(phase3,outputPath,partID,3,isColors=isColors,isAlpScarf=isAlpScarf,isRadial=isRadial,isStimulus=isStimulus)

#**kawgs can be entityCol or allEntity
#Return the concatenated dataframe of the three transition matrixes
def createAllTransMatrix(phase1,phase2,phase3,partID,entityCol=None,allEntity=None):

    trans1 = createTransMatrix(phase1,partID,1,entityCol=entityCol,allEntity=allEntity)
    trans2 = createTransMatrix(phase2,partID,2,entityCol=entityCol,allEntity=allEntity)
    trans3 = createTransMatrix(phase3,partID,3,entityCol=entityCol,allEntity=allEntity)
    return(pd.concat([trans1,trans2,trans3],ignore_index=True))

#Return concatenated dataframe of the three distribtuion matrices
def createAllDistMatrix(phase1,phase2,phase3,partID,entityCol=None,wantEntity=None):
    
    dist1 = createDistMatrix(phase1,partID,1,entityCol=entityCol,wantEntity=wantEntity)
    dist2 = createDistMatrix(phase2,partID,2,entityCol=entityCol,wantEntity=wantEntity)
    dist3 = createDistMatrix(phase3,partID,3,entityCol=entityCol,wantEntity=wantEntity)
    return(pd.concat([dist1,dist2,dist3],ignore_index=True))

#Gnerate the visual files for a participant and return the updated transition and distribtuionmatirx dataframes
def runOneParticipant(dataCSV,endTime0,endTime1,partID,outputPath,transDF,distDF,phaseDict,transDict,distDict):
    mergedDF = createMergeDF(dataCSV)
    phase1,phase2,phase3 = parseMergeCSV(mergedDF,endPhase0=endTime0,endPhase1=endTime1)
    createAllPhases(phase1,phase2,phase3,partID,outputPath,**phaseDict)
    temp = createAllTransMatrix(phase1,phase2,phase3,partID,**transDict)
    temp2 = createAllDistMatrix(phase1,phase2,phase3,partID,**distDict)
    updateTransDF = pd.concat([transDF,temp],ignore_index=True)
    updateDistDF = pd.concat([distDF,temp2],ignore_index=True)
    return(updateTransDF,updateDistDF)

#Run all participants
def runAllParticipants(listDataFiles,listTimes,listID,listOut,phaseDict,transDict,distDict):
    #ALL THE LIST MUST BE PARRELL VECTORS AND MUST BE SAME SIZE
    if( not (len(listDataFiles) ==len(listTimes) == len(listID)==len(listOut) ) ):
        print("Error: all of the lsit files must be the same length")
        exit(1)
    transMatrix = pd.DataFrame()
    distMatrix = pd.DataFrame()
    for i in range(0,len(listTimes)):
        curData = listDataFiles[i]
        curEnd0 = listTimes[i][0]
        curEnd1 = listTimes[i][1]
        curID = listID[i]
        curOut = listOut[i]

        transMatrix,distMatrix=runOneParticipant(curData,curEnd0,curEnd1,
                                                curID,curOut,transMatrix,distMatrix,phaseDict,transDict,distDict)
    
    transMatrix.to_csv("TransitionMatrix.csv",index=False)
    distMatrix.to_csv("DistribtuionMatrix.csv",index=False)


def getDictBug(processedPath,globQuery):
    allPaths = sorted(glob.glob(processedPath + "/" + globQuery,recursive=True))

    


def main():

    largeTime = 9999999999999
    #getDictBug("./processed_data","**/*.csv")
    #exit(1)
    #dictIDtoBug1 = {}
    #dictIDtoBug2 = {}
    #dictIDtoTimes = {}

    listDataFiles = ["processed_data/P102/bug1/merged_data.csv","processed_data/P103/bug1/merged_data.csv","processed_data/P105/bug1/merged_data.csv",
                    "processed_data/P106/bug1/merged_data.csv","processed_data/P201/bug1/merged_data.csv"
                    ,"processed_data/P202/bug1/merged_data.csv","processed_data/P203/bug1/merged_data.csv","processed_data/P204/bug1/merged_data.csv"
                    ,"processed_data/P205/bug1/merged_data.csv","processed_data/P206/bug1/merged_data.csv","processed_data/P207/bug1/merged_data.csv"
                    ,"processed_data/P208/bug1/merged_data.csv","processed_data/P301/bug1/merged_data.csv"]
    listTimes = [ (1563562294634,1563562897067), (1563826245007,1563826812264), (1563976958363, largeTime) 
                , (1564063779601,1564064007823), (1563464280705,1563464828802)
                , (1563553936859,1563554256514), (1563986919996,1563987376814), (1563902610406,1563902773703)
                , (1563893868347, largeTime), (1564006098289,1564006333456), (1564076425290, 1564076670887)
                , (1564083265380, 1564083358841), (1564087432075, 1564087668731)]




    listID = ["P102","P103","P105","P106","P201","P202","P203","P204","P205","P206","P207","P208","P301"]
    listOut=["./Bug1_Output"]*13
    phaseDict={"isRadial":"entity","isAlpScarf":"entity"}
    transDict={}
    distDict={}

    runAllParticipants(listDataFiles,listTimes,listID,listOut,phaseDict,transDict,distDict)


#listDataFiles,listTimes,listID,listOut
class PartTrial:

    def __init__(self,pathToData,pathToOutput,timeTuple,ID):
        self.pathToData = pathToData
        self.pathToOutput = pathToOutput
        self.timeTuple = timeTuple
        self.ID = ID
    
    def runParticipant(self,transDF,distDF,phaseDict,transDict,distDict):
        mergedDF = createMergeDF(self.pathToData)
        phase1,phase2,phase3 = parseMergeCSV(mergedDF, endPhase0=self.timeTuple[0], endPhase1=self.timeTuple[1])
        createAllPhases(phase1, phase2, phase3, self.ID, self.pathToOutput, **phaseDict)
        temp = createAllTransMatrix(phase1, phase2, phase3, self.ID, **transDict)
        temp2 = createAllDistMatrix(phase1, phase2, phase3, self.ID, **distDict)
        updateTransDF = pd.concat([transDF,temp],ignore_index=True)
        updateDistDF = pd.concat([distDF,temp2],ignore_index=True)
        return(updateTransDF,updateDistDF)








if __name__ == "__main__":
    main()
