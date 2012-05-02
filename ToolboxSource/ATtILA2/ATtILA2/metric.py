''' Interface for running specific metrics

'''
import os

import arcpy
from arcpy import env

from pylet import arcpyutil
from pylet import lcc

from ATtILA2.constants import metricConstants
from ATtILA2.constants import globalConstants
from ATtILA2 import utils


_tempEnvironment0 = ""
_tempEnvironment1 = ""

def standardSetup(snapRaster, fallBackDirectory, itemDescriptionPairList=[]):
    """ Standard setup for executing metrics. """
    

    
    # Check out any necessary licenses
    arcpy.CheckOutExtension("spatial")
    
    # get current snap environment to restore at end of script
    _tempEnvironment0 = env.snapRaster
    _tempEnvironment1 = env.workspace
    
    # set the snap raster environment so the rasterized polygon theme aligns with land cover grid cell boundaries
    env.snapRaster = snapRaster
    env.workspace = arcpyutil.environment.getWorkspaceForIntermediates(fallBackDirectory)
    
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
    
    # return the spatial analyst license    
    arcpy.CheckInExtension("spatial")
    
    
    
def runLandCoverOnSlopeProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                                metricsToRun, inSlopeGrid, inSlopeThresholdValue, outTable, processingCellSize, 
                                snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover on Slope Proportions (Land Cover Slope Overlap)"""
    
    metricsClassNameList, optionalGroupsList = standardSetup(snapRaster, os.path.dirname(outTable), [metricsToRun,optionalFieldGroups] )
    
    
    # XML Land Cover Coding file loaded into memory
    lccObj = lcc.LandCoverClassification(lccFilePath)
    lcospConst = metricConstants.lcospConstants()
        
    # append the slope threshold value to the field suffix
    generalSuffix = lcospConst.fieldSuffix
    specificSuffix = generalSuffix+inSlopeThresholdValue
    lcospConst.fieldParameters[1] = specificSuffix
    
    SLPxLCGrid = utils.raster.getIntersectOfGrids(lccObj, inLandCoverGrid, inSlopeGrid, inSlopeThresholdValue)

    # save the file if intermediate products option is checked by user
    if globalConstants.intermediateName in optionalGroupsList: 
        SLPxLCGrid.save(arcpy.CreateUniqueName("slxlc"))
        
        
    
    utils.calculate.landCoverProportions(inReportingUnitFeature, reportingUnitIdField, SLPxLCGrid, lccFilePath, 
                         metricsClassNameList, outTable, processingCellSize, optionalGroupsList, lcospConst)
    
    standardRestore()
    
    
def runLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                         metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover Proportion Metrics """   
    
    metricsClassNameList, optionalGroupsList = standardSetup(snapRaster, os.path.dirname(outTable), [metricsToRun,optionalFieldGroups] )
    
    lcpConst = metricConstants.lcpConstants()
    
    
    utils.calculate.landCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                         metricsClassNameList, outTable, processingCellSize, optionalGroupsList, lcpConst)
    
    standardRestore()
    

    

        
            








