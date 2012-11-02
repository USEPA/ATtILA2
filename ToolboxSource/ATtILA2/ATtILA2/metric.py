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


class metricCalc():
    """ This class contains the basic steps to perform a land cover metric calculation.
    
    **Description:**
    
        The long metric calculation process only varies slightly from metric to metric.  By embedding the series of 
        calculation steps and parameters in a class object, we can make any step that might need to be altered for 
        a particular calculation into a separate function that can be overridden.  This cuts down on duplicate code and 
        eases maintenance.  Each metric calculation need only instantiate a subclass of metricCalc, override the 
        necessary functions, and then run the main 'run' function - all other code will be inherited from the main 
        class.  If a new step needs to be pulled out of the main 'run' function so that it can be altered, it can be 
        done without affecting any existing code.  
    
    """
    # Function to run all the steps in the calculation process
    def run(self, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
              metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst):
        # Run the setup
        self.metricsBaseNameList, self.optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize, 
                                                                                 os.path.dirname(outTable), 
                                                                                 [metricsToRun,optionalFieldGroups] )
        # XML Land Cover Coding file loaded into memory
        self.lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        self.lccClassesDict = self.lccObj.classes
        # alert user if the land cover grid has values undefined in the LCC XML file
        utils.settings.checkGridValuesInLCC(inLandCoverGrid, self.lccObj)
        # alert user if the land cover grid cells are not square (default to size along x axis)
        utils.settings.checkGridCellDimensions(inLandCoverGrid)
        # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field    
        self.outIdField = utils.settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
        
        # If the user has checked the Intermediates option, name the tabulateArea table. This will cause it to be saved.
        self.tableName = None
        self.saveIntermediates = globalConstants.intermediateName in self.optionalGroupsList
        if self.saveIntermediates: 
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
        self.inLandCoverGrid = inLandCoverGrid
        
        # Replace LandCover Grid, if necessary
        self._replaceLCGrid()
        
        # Make Output Tables
        self._makeAttilaOutTable()
        
        # Generate Tabulation tables
        self._makeTabAreaTable()
        
        # Run final metric calculation
        self._calculateMetrics()
        
    def _makeAttilaOutTable(self):
        # Internal function to construct the ATtILA metric output table
        self.newTable, self.metricsFieldnameDict = utils.table.tableWriterByClass(self.outTable, 
                                                                                  self.metricsBaseNameList, 
                                                                                  self.optionalGroupsList, 
                                                                                  self.metricConst, self.lccObj, 
                                                                                  self.outIdField)    
    def _makeTabAreaTable(self):
        # Internal function to generate a zonal tabulate area table
        self.tabAreaTable = TabulateAreaTable(self.inReportingUnitFeature, self.reportingUnitIdField, 
                                              self.inLandCoverGrid, self.tableName, self.lccObj)
    
    def _calculateMetrics(self):
        # Internal function to process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        utils.calculate.landCoverProportions(self.lccClassesDict, self.metricsBaseNameList, self.optionalGroupsList, 
                                             self.metricConst, self.outIdField, self.newTable, self.tabAreaTable, 
                                             self.metricsFieldnameDict, self.zoneAreaDict)
    
    def _replaceLCGrid(self):
        # Internal function to replace the landcover grid.  Several metric Calculations require this step, but others skip it.
        pass
        

def runLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                            metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover Proportion Metrics """   
    
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcpConstants()
        
        # Create new instance of metricCalc class to contain parameters
        lcpCalc = metricCalc()
        
        # Run Calculation
        lcpCalc.run(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
  
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()

class metricCalcLCOSP(metricCalc):
    # Subclass that overrides specific functions for the LandCoverOnSlopeProportions calculation
    def _replaceLCGrid(self):
        # replace the inLandCoverGrid
        self.inLandCoverGrid = utils.raster.getIntersectOfGrids(self.lccObj, self.inLandCoverGrid, self.inSlopeGrid, 
                                                           self.inSlopeThresholdValue)
        
        if self.saveIntermediates:
            self.inLandCoverGrid.save(arcpy.CreateScratchName(self.metricConst.shortName, "", "RasterDataset"))  

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
        lcspCalc = metricCalcLCOSP()
        
        lcspCalc.inSlopeGrid = inSlopeGrid
        lcspCalc.inSlopeThresholdValue = inSlopeThresholdValue
        
        # Run Calculation
        lcspCalc.run(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                       metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()
        
class metricCalcCAEAM(metricCalc):
    # Subclass that overrides specific functions for the CoreAndEdgeAreaMetric calculation
    def _replaceLCGrid(self):
        # replace the inLandCoverGrid
        self.inLandCoverGrid = utils.raster.getEdgeCoreGrid(self.lccObj, self.inLandCoverGrid, self.inEdgeWidth)
        
        if self.saveIntermediates:
            self.inLandCoverGrid.save(arcpy.CreateScratchName(self.metricConst.shortName, "", "RasterDataset")) 

def runCoreAndEdgeAreaMetrics(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                            metricsToRun, inEdgeWidth, outTable, processingCellSize, snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover Proportion Metrics """   
    
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.caeamConstants()
        # append the edge width distance value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inEdgeWidth        
        
        # Create new instance of metricCalc class to contain parameters
        caeamCalc = metricCalcCAEAM()
        
        # Run Calculation
        caeamCalc.run(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
  
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
                      
        # Generate a default filename for the buffer feature class
        bufferName = metricConst.shortName + inBufferDistance.split()[0]
        
        # Generate the buffer area to use in the metric calculation
        utils.vector.bufferFeaturesByIntersect(inStreamFeatures, inReportingUnitFeature, bufferName, inBufferDistance, reportingUnitIdField)

        # Create new instance of metricCalc class to contain parameters
        rlcpCalc = metricCalc()
        
        # Run Calculation
        rlcpCalc.run(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                       metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
              
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()
        
class metricCalcSPLCP(metricCalc):
    # Subclass that overrides specific functions for the SamplePointLandCoverProportions calculation
    pass

def runSamplePointLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                            metricsToRun, inPointFeatures, ruLinkField, inBufferDistance, outTable, processingCellSize, snapRaster, 
                            optionalFieldGroups):
    """ Interface for script executing Sample Point Land Cover Proportion Metrics """   
    
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.splcpConstants()
        # append the buffer distance value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inBufferDistance.split()[0]

        # Generate a default filename for the buffer feature class
        bufferName = metricConst.shortName + inBufferDistance.split()[0]
        
        # Buffer the points and use the output as the new reporting units
        bufferedFeatures = utils.vector.bufferFeaturesByID(inPointFeatures,inReportingUnitFeature,bufferName,inBufferDistance,reportingUnitIdField,ruLinkField)
        
        # Create new instance of metricCalc class to contain parameters
        splcpCalc = metricCalcSPLCP()
        
        # Run Calculation
        splcpCalc.run(bufferedFeatures, ruLinkField, inLandCoverGrid, lccFilePath, 
                       metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
              
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()

 
class metricCalcLCC(metricCalc):
    # Subclass that overrides specific functions for the land Cover Coefficient calculation
    def _makeAttilaOutTable(self):
        # Construct the ATtILA metric output table
        self.newTable, self.metricsFieldnameDict = utils.table.tableWriterByCoefficient(self.outTable, 
                                                                                        self.metricsBaseNameList, 
                                                                                        self.optionalGroupsList, 
                                                                                        self.metricConst, self.lccObj, 
                                                                                        self.outIdField)
    def _calculateMetrics(self):
        # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        utils.calculate.landCoverCoefficientCalculator(self.lccObj.values, self.metricsBaseNameList, 
                                                       self.optionalGroupsList, self.metricConst, self.outIdField, 
                                                       self.newTable, self.tabAreaTable, self.metricsFieldnameDict, 
                                                       self.zoneAreaDict, self.conversionFactor)
 
    
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
              
        # see what linear units are used in the tabulate area table 
        outputLinearUnits = settings.getOutputLinearUnits(inReportingUnitFeature)

        # using the output linear units, get the conversion factor to convert the tabulateArea area measures to hectares
        try:
            conversionFactor = conversion.getSqMeterConversionFactor(outputLinearUnits)
        except:
            raise errors.attilaException(errorConstants.linearUnitConversionError)
            #raise
               
        # Set the conversion factor as a class attribute
        lccCalc.conversionFactor = conversionFactor
        
        # Run calculation
        lccCalc.run(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()


        









