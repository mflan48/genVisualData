import os
import subprocess
import getopt
import glob
import numpy as np
import json
import random
import sys

SEED = 400


def usage():
    print("Command line options for getopt\n")
    print("-p --path: requires a path to the 'processed' directory. The 'processed' directory must contain the directories for each phase. Default is './'")
    print("-c --colors: requires a text file that contains a mapping of functions to hex colors. Default is None")
    print("-a --alpscarf: requires a string that indicates that the alpscarf plot data should be generated with the AOI column as the passed in argument. Default is 'function'")
    print("-r --radial: requires a string that indicates the radial data should be generated with the AOIName column as the passed in argumenet. Default is 'function'")
    print("-s --stimulus: requires a string that indicates the radial data should be genreate with the stimulus column as the passed in argument. Default is 'which_file'")
    print("-i --id: requires an int that represents the id of the participant. Default is 1")
    print("-o --output: requires a path to directory where the each 'output' subdirectory from the genVisualPhase.py will be created. Default is './'")
    print("The default will be the same as the path and every 'output' directory will be created in each phase directory")
    print("If it is not the default, then subdirectories will be created in the passed in directory. These subdirectories will correspond to the phase directories")
    print("-h --help: prints this message")
    print("-j --jsonColorMapping: requires a jsonFile that contains all of the functions. It will then automatically create a file of function to color mapping.")
    print("NOTES:")
    print("If the -c and -j are both not used, then no colors.csv will be created and thus the alpscarf tool cant be used.")
    print("If the -j option and -c is used, the -c option takes precedence and will be used rather than the automatically created one from -j")



#get the list of all of the phase directiries
#Note the current glob search gets all the directories 
#So we added code int his function to not include the output directory in the list
def getListPhase(outputDir,pathToProcessed="."):
    tempList = sorted(glob.glob(pathToProcessed+ "/*/"))
    toReturn = [x for x in [y for y in tempList if y != outputDir + "/"]]
    return(toReturn)

def modPathName(pathName):
    return(pathName if pathName[len(pathName)-1] != "/" else pathName[0:len(pathName)-1])



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
    random.shuffle(toReturn)
    return(toReturn)

#used to create the function to color mapping that will be passed into the command line
def createColorMapping(jsonFileName,outputDir,combComFunc=False):
    #Each list represents a list of rBeg,rEnd,gBeg,gEnd,bBeg,bEnd values that is used 
    #This dict is used for the file funcColors_func.txt which has each software entity be its own color based of the auto g
    #generated coloring scheme
    
    #smaller range
    dictFileCol = {}
    dictFileCol["Help"] = [0,200,244,255,180,200] #Range for light green 
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

    try:
        #Read in the json file 
        with open(jsonFileName,"r") as bugJSON, open(outputDir + "/funcCol_func.txt","w") as toWrite, open(outputDir + "/funcCol_file.txt","w") as myWrite:
            data = json.load(bugJSON)
            #writ the headers
            toWrite.write("Entity-Color\n")
            myWrite.write("Entity-Color\n")
            #get each minsweeper file name 
            for curFile in data:

                #Get the amount entities for that file and create the color range for it
                amountForCol = len(data[curFile])
                curColList = None
                #If we are combining the coments and functions, make the size we want halfed else get the full amount
                if(combComFunc):
                    curColList = createColRange(dictFileCol[curFile],int(amountForCol/2)+1)
                else:
                    curColList = createColRange(dictFileCol[curFile],amountForCol)
                
                
                myWrite.write(curFile+".java-"+dict2[curFile]+'\n')

                #Write to the file each color each entity is supposed to be 
                i = 0
                addI = False
                #We read backwards just incase we need to combine comments and functions
                for entity in list(data[curFile].keys())[::-1]:
                    toWrite.write(entity + "-" + curColList[i] + '\n')
                    #If we are combining comments and functions
                    if(combComFunc):
                        if not addI:
                            i = i+1
                            addI = True
                        else:
                            addI = False
                    else:
                        i = i+1
            #Manually add the NONE one in
            toWrite.write("NONE-000000\n")
    except FileNotFoundError:
        print("error: could not open file "  + jsonFileName)
        exit(1)
    return(outputDir + "/funcCol_func.txt")

def main():

    random.seed(SEED)

    #getopt stuff 
    try:
        options,arguments = getopt.getopt(sys.argv[1:],"hp:c:a:r:s:i:o:j:",["help","path=","colors=","alpscarf=","radial=","stimulus=","id=","output=","jsonMapping="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        exit(1)
    
    #Variables for the call to genVisualPhase.py
    processedPath =os.getcwd()
    outputPath=os.getcwd()
    partID=1
    colorsFile=None
    alpScarfAOI=None
    radialInterest=None
    radialStimulus=None
    jsonMapping=None
    if(len(options) == 0):
        usage()
        exit(1)

    #Take care of the options
    for opt,arg in options:
        if(opt in ("-p","--path") ):
            processedPath = arg
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
        elif(opt in ("-o","--output")):
            outputPath = arg
        elif(opt in ("-h","--help")):
            usage()
            exit(1)
        elif(opt in ("-j","--jsonMapping")):
            jsonMapping = arg
        else:
            assert False, "unhandled option"


    #Make sure all of the command line options were valid

    
    #Modify the processedPath and outputPath to not include the final /
    processedPath = modPathName(processedPath)
    outputPath = modPathName(outputPath)

    #Check if the processed path exist
    if(not os.path.exists(processedPath)):
        print("Error: " + processedPath + " does not exist")
        exit(1)
    
    #Check if the output path exist
    if(not os.path.exists(outputPath+"/output")):
        outputPath = outputPath + "/output"
        os.makedirs(outputPath)
    else:
        outputPath = outputPath + "/output"
    
    forJson = ""
    if(jsonMapping != None):
        forJson = createColorMapping(jsonMapping,outputDir=outputPath)

    #Get the paths and store them to traverse 
    paths = getListPhase(outputPath,processedPath)
    for path in paths:
        #Always add the phase path and the ID
        toRun = ["python3","genVisualPhase.py","-p",path,"-i",str(partID)]
        
        #Create the directory to place this phases ouput and add it 
        curPhase = path.split("/")[-2]
        curOutPath = outputPath + "/" + curPhase
        if(not os.path.exists(curOutPath)):
            os.mkdir(curOutPath)
        toRun.append("-o")
        toRun.append(curOutPath)
        
        #Add all the other command line arguments 
        if(colorsFile != None):
            toRun.append("-c")
            toRun.append(colorsFile)
        elif(jsonMapping != None):
            toRun.append("-c")
            toRun.append(forJson)
        
        if(alpScarfAOI != None):
            toRun.append("-a")
            toRun.append(alpScarfAOI)
        if(radialInterest != None):
            toRun.append("-r")
            toRun.append(radialInterest)
        if(radialStimulus != None):
            toRun.append("-s")
            toRun.append(radialStimulus)
        
        print("------RUNNING FOLLOWING COMMAND------")
        print(" ".join(toRun))
        print("\n")
        if(subprocess.call(toRun)):
            print("******ERROR RUNNING THIS COMMAND,CHECK THE OUTPUT******\n")

    print("----FINISHED----")




if __name__=="__main__":
    main()


"""
For this script, the output option will either be the input path directly, or something else
If its not the input path, we will go into that directory, and either create or look for the current phases
directory, (similar to the structure from itrace-post (0_123124-234234)). We will then call the genVisualyPhase.py script 
and pass in that directory as the output

The input has to be the path to the processed directory
"""

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
    print("-h --help: displays this message")
"""

"""
    #wider range
    dictFileCol = {}
    dictFileCol["Help"] = [0,200,200,255,150,200] #Range for light green 
    dictFileCol["Piece"] = [205,255,205,255,70,200] #Range for light yellow 
    dictFileCol["Space"] = [100,240,100,240,100,240] #Range for grey
    dictFileCol["MineSweeperBoard"] = [100,255,40,160,100,255] #Range for DarkRed and DarkBlue
    dictFileCol["MineButton"] = [30,200,0,150,120,255] #Range for purple
    dictFileCol["MineSweeperGui"] = [150,255,100,200,0,100] #Range for Orange
    dictFileCol["CustomMenu"] = [100,200,120,180,0,120] #Range for Dark yellow
    dictFileCol["MineGenerator"] = [0,180,210,255,210,255] #Range for light blue
    dictFileCol["MineSweeper"] = [0,100,80,140,0,100] #Range for dark green
"""


