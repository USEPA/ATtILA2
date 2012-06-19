''' Interface for running specific metrics

'''
import os
import arcpy
import errors
import setupAndRestore
from pylet import lcc
from pylet.arcpyutil import polygons

from ATtILA2.constants import metricConstants
from ATtILA2.constants import globalConstants
from ATtILA2.constants import errorConstants
from ATtILA2 import utils
from ATtILA2.utils.tabarea import TabulateAreaTable

    
def runLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                            metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover Proportion Metrics """   
    
    try:
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize, 
                                                                                 os.path.dirname(outTable), 
                                                                                 [metricsToRun,optionalFieldGroups] )
        # XML Land Cover Coding file loaded into memory
        lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        lccClassesDict = lccObj.classes
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcpConstants()
        # alert user if the land cover grid has values undefined in the LCC XML file
        utils.settings.checkGridValuesInLCC(inLandCoverGrid, lccObj)
        # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field    
        outIdField = utils.settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
        
        # If the user has checked the Intermediates option, name the tabulateArea table. This will cause it to be saved.
        tableName = None
        if globalConstants.intermediateName in optionalGroupsList: 
            tableName = metricConst.shortName + globalConstants.tabulateAreaTableAbbv
        # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
        zoneAreaDict = None
        if globalConstants.qaCheckName in optionalGroupsList: 
            zoneAreaDict = polygons.getIdAreaDict(inReportingUnitFeature, reportingUnitIdField)
        # Construct the ATtILA metric output table
        newTable, metricsFieldnameDict = utils.table.tableWriterByClass(outTable, metricsBaseNameList, optionalGroupsList, 
                                                                        metricConst, lccObj, outIdField)
        # generate a zonal tabulate area table
        tabAreaTable = TabulateAreaTable(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, tableName, 
                                         lccObj)
        # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        utils.calculate.landCoverProportions(lccClassesDict, metricsBaseNameList, optionalGroupsList, metricConst, 
                                             outIdField, newTable, tabAreaTable, metricsFieldnameDict, zoneAreaDict)
        
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()
        
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
        # get the dictionary with the LCC CLASSES attributes
        lccClassesDict = lccObj.classes
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcospConstants()
        # alert user if the land cover grid has values undefined in the LCC XML file
        utils.settings.checkGridValuesInLCC(inLandCoverGrid, lccObj)
        # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
        outIdField = utils.settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
        
        # If the user has checked the Intermediates option, name the tabulateArea table. This will cause it to be saved.
        tableName = None
        if globalConstants.intermediateName in optionalGroupsList: 
            tableName = metricConst.shortName + globalConstants.tabulateAreaTableAbbv
        # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
        zoneAreaDict = None
        if globalConstants.qaCheckName in optionalGroupsList: 
            zoneAreaDict = polygons.getIdAreaDict(inReportingUnitFeature, reportingUnitIdField)
            
        # append the slope threshold value to the field suffix
        generalSuffix = metricConst.fieldSuffix
        specificSuffix = generalSuffix + inSlopeThresholdValue
        metricConst.fieldParameters[1] = specificSuffix
        
        # replace the inLandCoverGrid
        inLandCoverGrid = utils.raster.getIntersectOfGrids(lccObj, inLandCoverGrid, inSlopeGrid, inSlopeThresholdValue)
    
        # save the file if intermediate products option is checked by user
        if globalConstants.intermediateName in optionalGroupsList: 
            inLandCoverGrid.save(arcpy.CreateUniqueName(metricConst.shortName))
        # Construct the ATtILA metric output table    
        newTable, metricsFieldnameDict = utils.table.tableWriterByClass(outTable, metricsBaseNameList, optionalGroupsList, 
                                                                        metricConst, lccObj, outIdField)
        # generate a zonal tabulate area table
        tabAreaTable = TabulateAreaTable(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, tableName, 
                                         lccObj)
        # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        utils.calculate.landCoverProportions(lccClassesDict, metricsBaseNameList, optionalGroupsList, metricConst, 
                                             outIdField, newTable, tabAreaTable, metricsFieldnameDict, zoneAreaDict)
        
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()
        

def runRiparianLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                            metricsToRun, inStreamFeatures, inBufferDistance, outTable, processingCellSize, snapRaster, 
                            optionalFieldGroups):
    """ Interface for script executing Riparian Land Cover Proportion Metrics """   
    
    try:
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize, 
                                                                                 os.path.dirname(outTable), 
                                                                                 [metricsToRun,optionalFieldGroups] )
        # XML Land Cover Coding file loaded into memory
        lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        lccClassesDict = lccObj.classes
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.rlcpConstants()
        # alert user if the land cover grid has values undefined in the LCC XML file
        utils.settings.checkGridValuesInLCC(inLandCoverGrid, lccObj)
        # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
        outIdField = utils.settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
        
        # If the user has checked the Intermediates option, name the tabulateArea table. This will cause it to be saved.
        tableName = None
        if globalConstants.intermediateName in optionalGroupsList: 
            tableName = metricConst.shortName + globalConstants.tabulateAreaTableAbbv
        # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
        zoneAreaDict = None
        if globalConstants.qaCheckName in optionalGroupsList: 
            zoneAreaDict = polygons.getIdAreaDict(inReportingUnitFeature, reportingUnitIdField)
        
        # append the buffer distance value to the field suffix
        generalSuffix = metricConst.fieldSuffix
        specificSuffix = generalSuffix + inBufferDistance
        metricConst.fieldParameters[1] = specificSuffix
        
        # Construct the ATtILA metric output table
        newTable, metricsFieldnameDict = utils.table.tableWriterByClass(outTable, metricsBaseNameList, optionalGroupsList, 
                                                                        metricConst, lccObj, outIdField)
        # generate a zonal tabulate area table
        tabAreaTable = TabulateAreaTable(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, tableName, 
                                         lccObj)
        # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        utils.calculate.landCoverProportions(lccClassesDict, metricsBaseNameList, optionalGroupsList, metricConst, 
                                             outIdField, newTable, tabAreaTable, metricsFieldnameDict, zoneAreaDict)
        
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()
    
        
    
def runLandCoverCoefficientCalculator(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, 
                                      lccFilePath, metricsToRun, outTable, processingCellSize, snapRaster, 
                                      optionalFieldGroups):
    """Interface for script executing Land Cover Coefficient Calculator"""
    
    from ATtILA2.utils import settings
    from pylet.arcpyutil import conversion
            
    try:
        
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize, 
                                                                                 os.path.dirname(outTable), 
                                                                                 [metricsToRun,optionalFieldGroups] )
        # XML Land Cover Coding file loaded into memory
        lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC VALUES attributes
        lccValuesDict = lccObj.values
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcccConstants()
        # alert user if the land cover grid has values undefined in the LCC XML file
        utils.settings.checkGridValuesInLCC(inLandCoverGrid, lccObj)
        # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
        outIdField = utils.settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
        
        # If the user has checked the Intermediates option, name the tabulateArea table. This will cause it to be saved.
        tableName = None
        if globalConstants.intermediateName in optionalGroupsList: 
            tableName = metricConst.shortName + globalConstants.tabulateAreaTableAbbv
        # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
        zoneAreaDict = None
        if globalConstants.qaCheckName in optionalGroupsList: 
            zoneAreaDict = polygons.getIdAreaDict(inReportingUnitFeature, reportingUnitIdField)
            
        # see what linear units are used in the tabulate area table 
        outputLinearUnits = settings.getOutputLinearUnits(inReportingUnitFeature)

        # using the output linear units, get the conversion factor to convert the tabulateArea area measures to hectares
        try:
            conversionFactor = conversion.getSqMeterConversionFactor(outputLinearUnits)
        except:
            raise errors.attilaException(errorConstants.linearUnitConversionError)
            #raise

        # Construct the ATtILA metric output table
        newTable, metricsFieldnameDict = utils.table.tableWriterByCoefficient(outTable, metricsBaseNameList, 
                                                                              optionalGroupsList, metricConst, lccObj, 
                                                                              outIdField)
        # generate a zonal tabulate area table
        tabAreaTable = TabulateAreaTable(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, tableName, 
                                         lccObj)
        # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        utils.calculate.landCoverCoefficientCalculator(lccValuesDict, metricsBaseNameList, optionalGroupsList, 
                                                       metricConst, outIdField, newTable, tabAreaTable, 
                                                       metricsFieldnameDict, zoneAreaDict, conversionFactor)
        
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()
        









