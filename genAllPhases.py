from genVisualPhase import *
import os
import sys
import glob


def main():
    mergedDF = createMergeDF("./Main/P102_bug1_data.csv")
    phase1,phase2,phase3 = parseMergeCSV(mergedDF,1563544373744,1563544897067)
    #trans1,trans2,trans3 = appendTransMatrix(phase1,phase2,phase3,"P102")
    # print(trans1.to_string(index=False))
    # print(trans2.to_string(index=False))
    # print(trans3.to_string(index=False))
    # #master = pd.DataFrame(columns=["Particpant","Phase","Source","Member_Variable","Comment","Bug_Report","Class_Signature","Method_Body","Method_Signature","NONE"])
    # master = pd.concat([trans1,trans2,trans3],ignore_index=True)
    # print(master.to_string(index=False))
    dist = createAllDistMatrix(phase1,phase2,phase3,"P102")
    print(dist.to_string(index=False))


#kwargs represents isColors,isAlpScarf,isRadial,isStimulus
def createAllPhases(phase1,phase2,phase3,partID,outputPath,**kwargs):
    
    #Parse the kwargs
    col = None
    radial = None
    alp = None
    stim = None
    if(kwargs!=None):
        for key, val in kwargs:
            if(key == "isColors"):
                col=val
            elif(key=="isAlpScarf"):
                alp=val
            elif(key=="isRadial"):
                radial=val
            elif(key=="isStimulus"):
                stim=val

    createSinglePhase(phase1,outputPath,partID,1,isColors=col,isAlpScarf=alp,isRadial=radial,isStimulus=stim)
    createSinglePhase(phase2,outputPath,partID,2,isColors=col,isAlpScarf=alp,isRadial=radial,isStimulus=stim)
    createSinglePhase(phase3,outputPath,partID,3,isColors=col,isAlpScarf=alp,isRadial=radial,isStimulus=stim)

#**kawgs can be entityCol or allEntity
#Return the concatenated dataframe of the three transition matrixes
def createAllTransMatrix(phase1,phase2,phase3,partID,**kwargs):

    entityCol = None
    allEntity=None

    if(kwargs != None):
        #Parse the kwargs
        for key,val in kwargs.items():
            if(key == "entityCol"):
                entityCol=val
            elif(key=="allEntity"):
                allEntity=val
    trans1 = None
    trans2 = None
    trans3 = None

    #Create the entity matrices
    if(entityCol ==None and allEntity == None):
        trans1 = createTransMatrix(phase1,partID,1)
        trans2 = createTransMatrix(phase2,partID,2)
        trans3 = createTransMatrix(phase3,partID,3)
    elif(entityCol==None and allEntity != None):
        trans1 = createTransMatrix(phase1,partID,1,allEntity=allEntity)
        trans2 = createTransMatrix(phase2,partID,2,allEntity=allEntity)
        trans3 = createTransMatrix(phase3,partID,3,allEntity=allEntity)
    elif(entityCol!=None and allEntity == None):
        trans1 = createTransMatrix(phase1,partID,1,entityCol=entityCol)
        trans2 = createTransMatrix(phase2,partID,2,entityCol=entityCol)
        trans3 = createTransMatrix(phase3,partID,3,entityCol=entityCol)
    else:
        trans1 = createTransMatrix(phase1,partID,1,entityCol=entityCol,allEntity=allEntity)
        trans2 = createTransMatrix(phase2,partID,2,entityCol=entityCol,allEntity=allEntity)
        trans3 = createTransMatrix(phase3,partID,3,entityCol=entityCol,allEntity=allEntity)

    
    return(pd.concat([trans1,trans2,trans3],ignore_index=True))

#Return concatenated dataframe of the three distribtuion matrices
def createAllDistMatrix(phase1,phase2,phase3,partID,**kwargs):
    
    entityCol = None
    wantEntity= None
    if(kwargs!=None):
        for key,val in kwargs.items():
            if(key=="entityCol"):
                entityCol=val
            elif(key=="wantEntity"):
                wantEntity=val
    
    dist1=None
    dist2=None
    dist3=None

    if(entityCol == None and wantEntity == None):
        dist1 = createDistMatrix(phase1,partID,1)
        dist2 = createDistMatrix(phase2,partID,2)
        dist3 = createDistMatrix(phase3,partID,3)
    elif(entityCol != None and wantEntity == None):
        dist1 = createDistMatrix(phase1,partID,1,entityCol=entityCol)
        dist2 = createDistMatrix(phase2,partID,2,entityCol=entityCol)
        dist3 = createDistMatrix(phase3,partID,3,entityCol=entityCol)
    elif(entityCol == None and wantEntity != None):
        dist1 = createDistMatrix(phase1,partID,1,wantEntity=wantEntity)
        dist2 = createDistMatrix(phase2,partID,2,wantEntity=wantEntity)
        dist3 = createDistMatrix(phase3,partID,3,wantEntity=wantEntity)
    else:
        dist1 = createDistMatrix(phase1,partID,1,entityCol=entityCol,wantEntity=wantEntity)
        dist2 = createDistMatrix(phase2,partID,2,entityCol=entityCol,wantEntity=wantEntity)
        dist3 = createDistMatrix(phase3,partID,3,entityCol=entityCol,wantEntity=wantEntity)
    return(pd.concat([dist1,dist2,dist3],ignore_index=True))


if __name__ == "__main__":
    main()
