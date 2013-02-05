

import os, arcpy
from ATtILA2.constants import globalConstants

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
        cleanupList.append((arcpy.Delete_management,(fileName)))

    return fileName