''' Tasks specific to setting up and restoring environments.
'''
import os
import arcpy
from arcpy import env
from .utils import environment
from .utils import parameters
from .utils.messages import AddMsg


from ATtILA2.constants import globalConstants

_tempEnvironment0 = ""
_tempEnvironment1 = ""
_tempEnvironment2 = ""
_tempEnvironment3 = ""
_tempEnvironment4 = ""
_tempEnvironment5 = ""
_tempEnvironment6 = ""


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
            msg = "Intermediates are stored in this directory: {0}\n"
            # arcpy.AddMessage(msg.format(env.workspace))
            AddMsg(msg.format(env.workspace), 0, logFile)
    
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


def createLogFile(inDataset, dateTimeStamp):
    """ Create log file to capture tool processing steps. """
    
    inBaseName = os.path.basename(inDataset)
    inRootName = os.path.splitext(inBaseName)[0]
    logBaseName = ('{0}_{1}').format(inRootName, dateTimeStamp)
    
    odsc = arcpy.Describe(env.workspace)
    
    # determine where to create the log file
    if odsc.DataType == "Folder":
        logPathName = os.path.join(env.workspace, logBaseName)
    else:
        logPathName = os.path.join(os.path.dirname(env.workspace), logBaseName)
    
    try:
        msg = "Created log file: {0}\n"
        arcpy.AddMessage(msg.format(logPathName))
        reportFile = open(logPathName, 'a')
            
        return reportFile
    except:
        AddMsg("Unable to create log file. Continuing metric calculations.", 1)
        if reportFile:
            reportFile.close()
        
        return None


def logWriteParameters(logFile, parametersList, labelsList):
    
    for l, p in zip(labelsList, parametersList):
        if p:
            logFile.write('PARAMETER: {0}: {1}\n'.format(l, p.replace("'"," ")))
    
    logFile.write("\n\n")


def setupLogFile(optionalFieldGroups, metricConst, parametersList, outDataset):
    from datetime import datetime
    processed = parameters.splitItemsAndStripDescriptions(optionalFieldGroups, globalConstants.descriptionDelim)    
    if globalConstants.logName in processed:
        # capture current date and time
        logTimeStamp = datetime.now().strftime(globalConstants.logFileExtension)
        # create the log file in the appropriate folder
        logFile = createLogFile(outDataset, logTimeStamp)
        if logFile:
            # start the log file by capturing the tool's parameters.
            labelsList = metricConst.parameterLabels
            logWriteParameters(logFile, parametersList, labelsList)
    else:
        logFile = None
    
    return logFile