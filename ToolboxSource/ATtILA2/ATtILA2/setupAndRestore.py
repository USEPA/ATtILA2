''' Tasks specific to setting up and restoring environments.
'''
import arcpy
from arcpy import env
from pylet import arcpyutil
from ATtILA2.constants import globalConstants

_tempEnvironment0 = ""
_tempEnvironment1 = ""
_tempEnvironment2 = ""

def standardSetup(snapRaster, processingCellSize, fallBackDirectory, itemDescriptionPairList=[]):
    """ Standard setup for executing metrics. """
    

    
    # Check out any necessary licenses
    arcpy.CheckOutExtension("spatial")
    
    # get current snap environment to restore at end of script
    _tempEnvironment0 = env.snapRaster
    _tempEnvironment1 = env.workspace
    _tempEnvironment2 = env.cellSize
    
    # set the snap raster environment so the rasterized polygon theme aligns with land cover grid cell boundaries
    env.snapRaster = snapRaster
    env.workspace = arcpyutil.environment.getWorkspaceForIntermediates(fallBackDirectory)
    env.cellSize = processingCellSize
    
    itemTuples = []
    for itemDescriptionPair in itemDescriptionPairList:
        processed = arcpyutil.parameters.splitItemsAndStripDescriptions(itemDescriptionPair, globalConstants.descriptionDelim)
        itemTuples.append(processed)
        
        if globalConstants.intermediateName in processed:
            msg = "\nIntermediates are stored in this directory: {0}\n"
            arcpy.AddMessage(msg.format(env.workspace))    
    
    return itemTuples

    
    
def standardRestore():
    """ Standard restore for executing metrics. """
    
    # restore the environments
    env.snapRaster = _tempEnvironment0
    env.workspace = _tempEnvironment1
    env.cellSize = _tempEnvironment2
    
    # return the spatial analyst license    
    try:
        arcpy.CheckInExtension("spatial")
    except:
        pass
    

def standardGridChecks(inLandCoverGrid, lccObj):
    """ Standard checks for input grids. """
    
    # warn user if input land cover grid has values not defined in LCC file
    rows = arcpy.SearchCursor(inLandCoverGrid) 

    gridValues = []    
    for row in rows:
        gridValues.append(row.getValue("VALUE"))
    
    undefinedValues = [aVal for aVal in gridValues if aVal not in lccObj.getUniqueValueIdsWithExcludes()]     
    if undefinedValues:
        arcpy.AddWarning("Following Grid Values undefined in LCC file: "+str(undefinedValues) + 
                         " - Please refer to the ATtILA documentation regarding undefined values.")
