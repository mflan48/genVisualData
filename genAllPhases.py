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



def main():
    listDataFiles = ["processed_data/P-101/bug2/merged_data.csv","processed_data/P-102/bug2/merged_data.csv","processed_data/P-103/bug2/merged_data.csv"
                    ,"processed_data/P-104/bug2/merged_data.csv","processed_data/P-105/bug2/merged_data.csv","processed_data/P-201/bug2/merged_data.csv"]
    listTimes = [(9999999999988,9999999999999),(9999999999988,9999999999999),(9999999999988,9999999999999)
                ,(9999999999988,9999999999999),(9999999999988,9999999999999),(9999999999988,9999999999999)]
    listID = ["P-101","P-102","P-103","P-104","P-105","P-201"]
    listOut=["./Bug2_Output"]*6
    phaseDict={"isRadial":"entity","isAlpScarf":"entity"}
    transDict={}
    distDict={}

    runAllParticipants(listDataFiles,listTimes,listID,listOut,phaseDict,transDict,distDict)

if __name__ == "__main__":
    main()
