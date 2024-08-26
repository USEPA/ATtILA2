''' Tasks specific to setting up and restoring environments.
'''

import arcpy
from arcpy import env
from .utils import environment
from .utils import parameters
from .utils.messages import AddMsg
from ATtILA2.constants import globalConstants
from datetime import datetime

_tempEnvironment0 = ""
_tempEnvironment1 = ""
_tempEnvironment2 = ""
_tempEnvironment3 = ""
_tempEnvironment4 = ""
_tempEnvironment5 = ""
_tempEnvironment6 = ""
_tempEnvironment7 = ""


def standardSetup(snapRaster, processingCellSize, fallBackDirectory, itemDescriptionPairList=[], logFile=None):
    """ Standard setup for executing metrics. """
    
    # Check out any necessary licenses
    arcpy.CheckOutExtension("spatial")
    
    # get current snap environment to restore at end of script
    _tempEnvironment0 = env.snapRaster
    _tempEnvironment1 = env.workspace
    _tempEnvironment2 = env.cellSize
    _tempEnvironment3 = env.extent
    _tempEnvironment4 = env.outputMFlag
    _tempEnvironment5 = env.outputZFlag
    _tempEnvironment6 = env.parallelProcessingFactor
    _tempEnvironment7 = env.outputCoordinateSystem

    env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, fallBackDirectory)
    
    # set the raster environments so the rasterized polygon theme aligns with land cover grid cell boundaries
    if snapRaster:
        env.snapRaster = snapRaster
    if processingCellSize:
        env.cellSize = processingCellSize
    
    # Streams and road crossings script fails in certain circumstances when M (linear referencing dimension) is enabled.
    # Disable for the duration of the tool.
    env.outputMFlag = "Disabled"
    
    # Do not copy Z values when making copies of features.
    env.outputZFlag = "Disabled" 
    
    # Until the Pairwise geoprocessing tools can be incorporated into ATtILA, disable the Parallel Processing Factor if the environment is set
    currentFactor = str(env.parallelProcessingFactor)
    if currentFactor == 'None' or currentFactor == '0':
        pass
    else:
        # Advise the user that results when using parallel processing may be different from results obtained without its use.
        # arcpy.AddWarning("Parallel processing is enabled. Results may vary from values calculated otherwise.")
        # arcpy.AddWarning("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.")
        AddMsg("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.", 1, logFile)
        env.parallelProcessingFactor = None
    
    itemTuples = []
    for itemDescriptionPair in itemDescriptionPairList:
        processed = parameters.splitItemsAndStripDescriptions(itemDescriptionPair, globalConstants.descriptionDelim)
        itemTuples.append(processed)
        
        if globalConstants.intermediateName in processed:
            msg = "Intermediates are stored in this directory: {0}\n"
            AddMsg(msg.format(env.workspace), 0, logFile)
        
    return itemTuples

    
def standardRestore(logFile=None):
    """ Standard restore for executing metrics. """
    
    # close the log file
    if logFile:
        logFile.write("\nEnded: {0}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        logFile.write("\n---End of Log File---\n")
        logFile.close()
        AddMsg('Log file closed')
    
    # restore the environments
    env.snapRaster = _tempEnvironment0
    env.workspace = _tempEnvironment1
    env.cellSize = _tempEnvironment2
    env.extent = _tempEnvironment3
    env.outputMFlag = _tempEnvironment4
    env.outputZFlag = _tempEnvironment5
    env.parallelProcessingFactor = _tempEnvironment6
    env.outputCoordinateSystem = _tempEnvironment7
    
    # return the spatial analyst license    
    try:
        arcpy.CheckInExtension("spatial")
    except:
        pass
