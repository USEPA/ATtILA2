

import os, arcpy
from arcpy import env

def getKeyFromFilePath(filePath, delimiter="_"):
    """ Parses full file path to return embedded key.
    
        Expected format:  <key><delimiter>anything
    """

    return os.path.basename(filePath).split(delimiter)[0]


def nameIntermediateFile(fileName,cleanupList):
    '''Quick function to create a scratch name for an intermediate dataset and add that dataset to the cleanup list
    if the user did not choose to keep intermediates
    '''
    
    fileName = arcpy.CreateScratchName(fileName[0],"",fileName[1])
    
    if not cleanupList[0] == "KeepIntermediates":
        cleanupList.append((arcpy.Delete_management,(fileName,)))
        # Had been having a devil of a time with this - a tuple with only one value.  In order to force it to be handled
        # as a tuple (rather than as a string), a comma after the item is necessary.  This is not a typo, it's official
        # python syntax.
    return fileName


def getRasterName(namePrefix):
    ''' Routine for obtaining filenames for raster objects. 
    '''
    if env.overwriteOutput == True:
        scratchName = os.path.join(env.workspace, namePrefix)
        
        # Delete output file if it already exists in the GDB. This prevents errors caused by lingering locks
        try:
            arcpy.Delete_management(scratchName)
        except:
            pass
        
    else:
        scratchName = arcpy.CreateScratchName(namePrefix, "", "RasterDataset")

    return scratchName


def getGdbFolder(filePath):
    '''Parses full file path to a geodatabase and returns its parent folder.
    ''' 
    if (filePath[-4:] == ".gdb"):
        # get the folder that contains the geodatabase
        folderDir = '\\'.join(filePath.split('\\')[0:-1])
    else:
        folderDir = None
        
    return folderDir