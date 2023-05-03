''' Tasks specific to setting up and restoring environments.
'''
import arcpy
from arcpy import env
#from pylet import utils
from .utils import environment
from .utils import parameters


from ATtILA2.constants import globalConstants

_tempEnvironment0 = ""
_tempEnvironment1 = ""
_tempEnvironment2 = ""
_tempEnvironment3 = ""
_tempEnvironment4 = ""
_tempEnvironment5 = ""
_tempEnvironment6 = ""


def standardSetup(snapRaster, processingCellSize, fallBackDirectory, itemDescriptionPairList=[]):
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

    env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, fallBackDirectory)
    
    # set the raster environments so the rasterized polygon theme aligns with land cover grid cell boundaries
    if snapRaster:
        env.snapRaster = snapRaster        
    if processingCellSize:
        env.cellSize = processingCellSize
    
    itemTuples = []
    for itemDescriptionPair in itemDescriptionPairList:
        processed = parameters.splitItemsAndStripDescriptions(itemDescriptionPair, globalConstants.descriptionDelim)
        itemTuples.append(processed)
        
        if globalConstants.intermediateName in processed:
            msg = "\nIntermediates are stored in this directory: {0}\n"
            arcpy.AddMessage(msg.format(env.workspace))    
    
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
        arcpy.AddWarning("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.")
        env.parallelProcessingFactor = None
    
    return itemTuples

    
def standardRestore():
    """ Standard restore for executing metrics. """
    
    # restore the environments
    env.snapRaster = _tempEnvironment0
    env.workspace = _tempEnvironment1
    env.cellSize = _tempEnvironment2
    env.extent = _tempEnvironment3
    env.outputMFlag = _tempEnvironment4
    env.outputZFlag = _tempEnvironment5
    env.parallelProcessingFactor = _tempEnvironment6
    
    # return the spatial analyst license    
    try:
        arcpy.CheckInExtension("spatial")
    except:
        pass
    