''' Interface for running specific metrics

'''
import os
import sys
import traceback

import arcpy
from arcpy import env

from pylet import arcpyutil
from pylet import lcc

from ATtILA2.constants import metricConstants
from ATtILA2.constants import globalConstants
from ATtILA2 import utils


_tempEnvironment0 = ""
_tempEnvironment1 = ""

def standardSetup(snapRaster, fallBackDirectory):
    """ Standard setup for executing metrics. """
    
    # Check out any necessary licenses
    arcpy.CheckOutExtension("spatial")
    
    # get current snap environment to restore at end of script
    _tempEnvironment0 = env.snapRaster
    _tempEnvironment1 = env.workspace
    
    # set the snap raster environment so the rasterized polygon theme aligns with land cover grid cell boundaries
    env.snapRaster = snapRaster
    env.workspace = arcpyutil.environment.getWorkspaceForIntermediates(fallBackDirectory)
    
    
    
def standardRestore():
    """ Standard restore for executing metrics. """
    
    # restore the environments
    env.snapRaster = _tempEnvironment0
    env.workspace = _tempEnvironment1
    
    # return the spatial analyst license    
    arcpy.CheckInExtension("spatial")
    
    
    
def runLandCoverOnSlopeProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid,lccName, lccFilePath, 
                                metricsToRun, inSlopeGrid, inSlopeThresholdValue, outTable, processingCellSize, 
                                snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover on Slope Proportions (Land Cover Slope Overlap)"""
    
    standardSetup(snapRaster, os.path.dirname(outTable))    
    
    # XML Land Cover Coding file loaded into memory
    lccObj = lcc.LandCoverClassification(lccFilePath)
    lcospConst = metricConstants.lcospConstants()
    SLPxLCGrid = utils.raster.getIntersectOfGrids(lccObj, inLandCoverGrid, inSlopeGrid, inSlopeThresholdValue)
    
    # save the file if intermediate products outputs are checked
    #SLPxLCGrid.save(arcpy.CreateUniqueName("slxlc"))
    
    utils.calculate.landCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                         metricsToRun, outTable, processingCellSize, optionalFieldGroups, lcospConst)
    

    standardRestore()
    
    
def runLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                         metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover Proportion Metrics """   
    
    standardSetup(snapRaster, os.path.dirname(outTable))
    
    lcpConst = metricConstants.lcpConstants()
    utils.calculate.landCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                         metricsToRun, outTable, processingCellSize, optionalFieldGroups, lcpConst)
    
    standardRestore()
    

    

        
            








