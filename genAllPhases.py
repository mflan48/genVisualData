from genVisualPhase import *
import os
import glob




def runAllParticipants(listPart,phaseDict,transDict,distDict):

    transMatrix = pd.DataFrame()
    distMatrix = pd.DataFrame()

    for i in range(0,len(listPart)):
        transMatrix,distMatrix=listPart[i].runParticipant(transMatrix,distMatrix,phaseDict,transDict,distDict)
    
    transMatrix.to_csv("TransitionMatrix.csv",index=False)
    distMatrix.to_csv("DistribtuionMatrix.csv",index=False)


def getDictBug(processedPath,globQuery):
    allPaths = sorted(glob.glob(processedPath + "/" + globQuery,recursive=True))

    


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
    phaseDict={"isRadial":"entity","isAlpScarf":"entity"}
    transDict={}
    distDict={}

    runAllParticipants(listPart,phaseDict,transDict,distDict)


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








if __name__ == "__main__":
    main()





"""
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
"""