''' Interface for running specific metrics

'''
import os
import arcpy
import errors
import setupAndRestore
from pylet import lcc

from ATtILA2.constants import metricConstants
from ATtILA2.constants import globalConstants
from ATtILA2 import utils


def runLandCoverOnSlopeProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                                   metricsToRun, inSlopeGrid, inSlopeThresholdValue, outTable, processingCellSize, 
                                   snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover on Slope Proportions (Land Cover Slope Overlap)"""
    
    try:
        
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize, 
                                                                                 os.path.dirname(outTable), 
                                                                                 [metricsToRun,optionalFieldGroups] )
        
        # XML Land Cover Coding file loaded into memory
        lccObj = lcc.LandCoverClassification(lccFilePath)
        lcospConst = metricConstants.lcospConstants()
        
        utils.settings.checkGridValuesInLCC(inLandCoverGrid, lccObj)
        outIdField = utils.settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
            
        # append the slope threshold value to the field suffix
        generalSuffix = lcospConst.fieldSuffix
        specificSuffix = generalSuffix + inSlopeThresholdValue
        lcospConst.fieldParameters[1] = specificSuffix
        
        SLPxLCGrid = utils.raster.getIntersectOfGrids(lccObj, inLandCoverGrid, inSlopeGrid, inSlopeThresholdValue)
    
        # save the file if intermediate products option is checked by user
        if globalConstants.intermediateName in optionalGroupsList: 
            SLPxLCGrid.save(arcpy.CreateUniqueName("slxlc"))
            
        newTable, metricsFieldnameDict = utils.table.tableWriterByClass(outTable, metricsBaseNameList, optionalGroupsList, 
                                                                        lcospConst, lccObj, outIdField)
        
        utils.calculate.landCoverProportions(inReportingUnitFeature, reportingUnitIdField, SLPxLCGrid, lccObj, 
                                             metricsBaseNameList, optionalGroupsList, lcospConst, outIdField, newTable, 
                                             metricsFieldnameDict)
        
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()

    
def runLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                            metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover Proportion Metrics """   
    
    try:
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize, 
                                                                                 os.path.dirname(outTable), 
                                                                                 [metricsToRun,optionalFieldGroups] )
        
        lccObj = lcc.LandCoverClassification(lccFilePath)
        lcpConst = metricConstants.lcpConstants()
        
        utils.settings.checkGridValuesInLCC(inLandCoverGrid, lccObj)
        outIdField = utils.settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
        
        newTable, metricsFieldnameDict = utils.table.tableWriterByClass(outTable, metricsBaseNameList, optionalGroupsList, 
                                                                        lcpConst, lccObj, outIdField)
        
        utils.calculate.landCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccObj, 
                                             metricsBaseNameList, optionalGroupsList, lcpConst, outIdField, newTable, 
                                             metricsFieldnameDict)
        
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()
    
        
    
def runLandCoverCoefficientCalculator(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, 
                                      lccFilePath, metricsToRun, outTable, processingCellSize, snapRaster, 
                                      optionalFieldGroups):
    """Interface for script executing Land Cover Coefficient Calculator"""
            
    try:
        
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize, 
                                                                                 os.path.dirname(outTable), 
                                                                                 [metricsToRun,optionalFieldGroups] )
        
        lccObj = lcc.LandCoverClassification(lccFilePath)
        lcccConst = metricConstants.lcccConstants()
        
        utils.settings.checkGridValuesInLCC(inLandCoverGrid, lccObj)
        outIdField = utils.settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
        
        newTable, metricsFieldnameDict = utils.table.tableWriterByCoefficient(outTable, metricsBaseNameList, 
                                                                              optionalGroupsList, lcccConst, lccObj, 
                                                                              outIdField)
       
        utils.calculate.landCoverCoefficientCalculator(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, 
                                                       lccObj, metricsBaseNameList, optionalGroupsList, lcccConst, 
                                                       outIdField, newTable, metricsFieldnameDict)
        
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()








