import os
import subprocess
import getopt
import glob
import numpy as np
import json

#get the list of all of the phase directiries
def getListPhase(pathToProcessed="."):
    return(glob.glob(pathToProcessed+ "/*/"))


"""
Needs to run the genVisualPhase script on all of the phase subdirectories
Recall that the script requires a phase directory and a output directory and will create all of the files to the  output directory
It can also take in other command line arguments that modify the data being created. We need to get these once and constantly pass it in to the call for genVisualPhase.py
This script should require a path to the processed folder and then when in the processed folder, get all of the subdirectories and call it respecitvely
    print("Command line options for getopt\n")
    print("-p --path: requires a path to phase directory (a phase is a directory like 0_startTimestamp-endTimeStamp) THIS DIRECTORY MUST CONTAIN A post2aoi directory")
    print("-c --colors: requires a text file that contains a mapping of functions to hex colors")
    print("-a --alpscarf: requires a string that indicates that the alpscarf plot data should be generate with the AOI column as the passed in argument")
    print("-r --radial: requires a string that indicates the radial data should be generated with the AOIName column as the passed in argumenet")
    print("-s --stimulus: requires a string that indicates the radial data should be genreate with the stimulus column as the passed in argument")
    print("-i --id: requires an int that represents the id of the participant")
    print("-o --output: requires a path to directory where the 'output' subdirectory will be created that stores all of the files")
"""




#THE CODE IN THIS BLOCK WAS USED TO GENERATE THE FUNCTION COLOR MAPPING FILES
#THIS ONLY HAS TO BE DONE ONCE
#pad the hex with one 0 if needed
def padHex(num):
    return('0x{0:0{1}X}'.format(num,2))

#create the list of hex colors based of the decimal rgb values based in
def createColRange(listRanges,numCol):
    #Get the numbers for each range
    rBeg,rEnd = listRanges[0],listRanges[1]
    gBeg,gEnd = listRanges[2],listRanges[3]
    bBeg,bEnd = listRanges[4],listRanges[5]

    #Get the colors of each range
    redRange = [padHex(x).split('x')[1] for x in np.linspace(rBeg,rEnd,num=numCol,dtype=int)]
    greenRange = [padHex(x).split('x')[1] for x in np.linspace(gBeg,gEnd,num=numCol,dtype=int)]
    blueRange = [padHex(x).split('x')[1] for x in np.linspace(bBeg,bEnd,num=numCol,dtype=int)]

    #Append the ranges together to create the hex color 
    toReturn = []
    for i in range(0,len(redRange)):
        toReturn.append(redRange[i] + greenRange[i]+blueRange[i])
    return(toReturn)

#used to create the function to color mapping that will be passed into the command line
def createColorMapping(jsonFileName):
    #Each list represents a list of rBeg,rEnd,gBeg,gEnd,bBeg,bEnd values that is used 
    #This dict is used for the file funcColors_func.txt which has each software entity be its own color based of the auto g
    #generated coloring scheme
    dictFileCol = {}
    dictFileCol["Help"] = [0,200,244,255,170,200] #Range for light green 
    dictFileCol["Piece"] = [235,255,235,255,90,170] #Range for light yellow 
    dictFileCol["Space"] = [126,230,126,230,126,230] #Range for grey
    dictFileCol["MineSweeperBoard"] = [144,255,80,120,144,255] #Range for DarkRed and DarkBlue
    dictFileCol["MineButton"] = [76,162,0,136,150,255] #Range for purple
    dictFileCol["MineSweeperGui"] = [200,255,130,200,0,76] #Range for Orange
    dictFileCol["CustomMenu"] = [100,160,140,160,0,88] #Range for Dark yellow
    dictFileCol["MineGenerator"] = [0,177,254,255,217,255] #Range for light blue
    dictFileCol["MineSweeper"] = [0,100,88,124,0,100] #Range for dark green

    #This dict is used for the file funcColors_file.txt which has each software entity 
    # in the same FILE (Help.java,CustomMenu.java etc) be the same color
    dict2 = {}
    dict2["Help"] = "97FF00"
    dict2["Piece"] = "FFFF00"
    dict2["Space"] = "808080"
    dict2["MineSweeperBoard"] = "FF0000"
    dict2["MineButton"] = "9B00FF"
    dict2["MineSweeperGui"] = "FFA600"
    dict2["CustomMenu"] = "B29800"
    dict2["MineGenerator"] = "0000FF"
    dict2["MineSweeper"] = "055000"


    #Read in the json file 
    with open(jsonFileName,"r") as bugJSON, open("funcCol_func.txt","w") as toWrite, open("funcCol_file.txt","w") as myWrite:
        data = json.load(bugJSON)
        #writ the headers
        toWrite.write("Entity-Color\n")
        myWrite.write("Entity-Color\n")
        #get each minsweeper file name 
        for curFile in data:

            #Get the amount entities for that file and create the color range for it
            amountForCol = len(data[curFile])
            curColList = createColRange(dictFileCol[curFile],amountForCol)
            
            myWrite.write(curFile+".java-"+dict2[curFile]+'\n')
            #Write to the file each color each entity is supposed to be 
            i = 0
            for entity in data[curFile]:
                toWrite.write(entity + "-" + curColList[i] + '\n')
                i = i + 1
        #Manually add the NONE one in
        toWrite.write("NONE-000000\n")


def main():

    createColorMapping("funcToColor.json")

    paths = getListPhase("./Nick/bug1/processed")
    print(paths)
    for path in paths:
        toRun = ["python3","genVisualPhase.py","-p",path,"-o",path,"-c","funcCol_func.txt"]
        subprocess.call(toRun)





if __name__=="__main__":
    main()



