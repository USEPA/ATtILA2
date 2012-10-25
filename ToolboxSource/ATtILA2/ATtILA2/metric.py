''' Interface for running specific metrics

'''
import os
import errors
import setupAndRestore
from pylet import lcc
from pylet.arcpyutil import polygons

from ATtILA2.constants import metricConstants
from ATtILA2.constants import globalConstants
from ATtILA2.constants import errorConstants
from ATtILA2 import utils
from ATtILA2.utils.tabarea import TabulateAreaTable


class metricCalc():
    # Initial class setup
    def setup(self, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
              metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst):
        self.metricsBaseNameList, self.optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize, 
                                                                                 os.path.dirname(outTable), 
                                                                                 [metricsToRun,optionalFieldGroups] )
        # XML Land Cover Coding file loaded into memory
        self.lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        self.lccClassesDict = self.lccObj.classes
        # alert user if the land cover grid has values undefined in the LCC XML file
        utils.settings.checkGridValuesInLCC(inLandCoverGrid, self.lccObj)
        # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field    
        self.outIdField = utils.settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
        
        # If the user has checked the Intermediates option, name the tabulateArea table. This will cause it to be saved.
        self.tableName = None
        if globalConstants.intermediateName in self.optionalGroupsList: 
            self.tableName = metricConst.shortName + globalConstants.tabulateAreaTableAbbv
        # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
        self.zoneAreaDict = None
        if globalConstants.qaCheckName in self.optionalGroupsList: 
            self.zoneAreaDict = polygons.getIdAreaDict(inReportingUnitFeature, reportingUnitIdField)
        
        # Save other input parameters as class attributes
        self.outTable = outTable
        self.inReportingUnitFeature = inReportingUnitFeature
        self.reportingUnitIdField = reportingUnitIdField
        self.metricConst = metricConst
    
    # Generate output tables
    def makeTables(self, inLandCoverGrid):
        # Construct the ATtILA metric output table
        self.newTable, self.metricsFieldnameDict = utils.table.tableWriterByClass(self.outTable, 
                                                                                  self.metricsBaseNameList, 
                                                                                  self.optionalGroupsList, 
                                                                                  self.metricConst, self.lccObj, 
                                                                                  self.outIdField)
        # generate a zonal tabulate area table
        self.tabAreaTable = TabulateAreaTable(self.inReportingUnitFeature, self.reportingUnitIdField, inLandCoverGrid, 
                                              self.tableName, self.lccObj)
    
    def calculateLCP(self):
        # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        utils.calculate.landCoverProportions(self.lccClassesDict, self.metricsBaseNameList, self.optionalGroupsList, 
                                             self.metricConst, self.outIdField, self.newTable, self.tabAreaTable, 
                                             self.metricsFieldnameDict, self.zoneAreaDict)
 
class metricCalcLCC(metricCalc):
    # Generate output tables
    def makeTables(self, inLandCoverGrid):
        # Construct the ATtILA metric output table
        self.newTable, self.metricsFieldnameDict = utils.table.tableWriterByCoefficient(self.outTable, 
                                                                                        self.metricsBaseNameList, 
                                                                                        self.optionalGroupsList, 
                                                                                        self.metricConst, self.lccObj, 
                                                                                        self.outIdField)
        # generate a zonal tabulate area table
        self.tabAreaTable = TabulateAreaTable(self.inReportingUnitFeature, self.reportingUnitIdField, inLandCoverGrid, 
                                              self.tableName, self.lccObj)
    
    def calculateLCC(self, conversionFactor):
        # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        utils.calculate.landCoverCoefficientCalculator(self.lccObj.values, self.metricsBaseNameList, 
                                                       self.optionalGroupsList, self.metricConst, self.outIdField, 
                                                       self.newTable, self.tabAreaTable, self.metricsFieldnameDict, 
                                                       self.zoneAreaDict, conversionFactor)
    

def runLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                            metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover Proportion Metrics """   
    
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcpConstants()
        
        # Create new instance of metricCalc class to contain parameters
        lcpCalc = metricCalc()
        
        # Initial class setup
        lcpCalc.setup(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        
        # Generate output tables
        lcpCalc.makeTables(inLandCoverGrid)
        
        # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        lcpCalc.calculateLCP()
  
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()

def runLandCoverOnSlopeProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                                   metricsToRun, inSlopeGrid, inSlopeThresholdValue, outTable, processingCellSize, 
                                   snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover on Slope Proportions (Land Cover Slope Overlap)"""
    
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcospConstants()
        # append the slope threshold value to the field suffix 
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inSlopeThresholdValue
        
        # Create new instance of metricCalc class to contain parameters
        lcspCalc = metricCalc()
        
        # Initial class setup
        lcspCalc.setup(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                       metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        
        # replace the inLandCoverGrid
        inLandCoverGrid = utils.raster.getIntersectOfGrids(lcspCalc.lccObj, inLandCoverGrid, inSlopeGrid, inSlopeThresholdValue)
    
        # Generate output tables
        lcspCalc.makeTables(inLandCoverGrid)
        
        # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        lcspCalc.calculateLCP()
        
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()
        
        
def runCoreAndEdgeAreaMetrics(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                            metricsToRun, inEdgeWidth, outTable, processingCellSize, snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover Proportion Metrics """   
    
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.caeamConstants()
        # append the edge width distance value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inEdgeWidth
        
        # Create new instance of metricCalc class to contain parameters
        caeamCalc = metricCalc()
        
        # Initial class setup
        caeamCalc.setup(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        
        # replace the inLandCoverGrid
        inLandCoverGrid = utils.raster.getEdgeCoreGrid(caeamCalc.lccObj, inLandCoverGrid, inEdgeWidth)

        
        # Generate output tables
        caeamCalc.makeTables(inLandCoverGrid)
        
        # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        caeamCalc.calculateLCP()
  
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()

def runRiparianLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                            metricsToRun, inStreamFeatures, inBufferDistance, outTable, processingCellSize, snapRaster, 
                            optionalFieldGroups):
    """ Interface for script executing Riparian Land Cover Proportion Metrics """   
    
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.rlcpConstants()
        # append the buffer distance value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inBufferDistance.split()[0]
                
        # Create new instance of metricCalc class to contain parameters
        rlcpCalc = metricCalc()
        
        # Initial class setup
        rlcpCalc.setup(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                       metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        
        # Generate output tables
        rlcpCalc.makeTables(inLandCoverGrid)
        
        # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        rlcpCalc.calculateLCP()
              
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()
        
    
def runSamplePointLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                            metricsToRun, inPointFeatures, inBufferDistance, outTable, processingCellSize, snapRaster, 
                            optionalFieldGroups):
    """ Interface for script executing Riparian Land Cover Proportion Metrics """   
    
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.rlcpConstants()
        # append the buffer distance value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inBufferDistance.split()[0]
                
        # Create new instance of metricCalc class to contain parameters
        splcpCalc = metricCalc()
        
        # Initial class setup
        splcpCalc.setup(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                       metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        
        # Generate output tables
        splcpCalc.makeTables(inLandCoverGrid)
        
        # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        splcpCalc.calculateLCP()
              
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
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcccConstants()
        
        # Create new instance of metricCalc LCC subclass to contain parameters
        lccCalc = metricCalcLCC()
        
        # Initial class setup
        lccCalc.setup(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
                            
        # see what linear units are used in the tabulate area table 
        outputLinearUnits = settings.getOutputLinearUnits(inReportingUnitFeature)

        # using the output linear units, get the conversion factor to convert the tabulateArea area measures to hectares
        try:
            conversionFactor = conversion.getSqMeterConversionFactor(outputLinearUnits)
        except:
            raise errors.attilaException(errorConstants.linearUnitConversionError)
            #raise
        
        lccCalc.makeTables(inLandCoverGrid)
        
        # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        lccCalc.calculateLCC(conversionFactor)
        
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()


        









