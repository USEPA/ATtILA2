''' Interface for running specific metrics

'''
import os
import arcpy
import errors
import setupAndRestore
from pylet import lcc
from pylet.arcpyutil import polygons
from pylet.arcpyutil.messages import AddMsg
from pylet.datetimeutil import DateTimer

from ATtILA2.constants import metricConstants
from ATtILA2.constants import globalConstants
from ATtILA2.constants import errorConstants
from ATtILA2 import utils
from ATtILA2.utils.tabarea import TabulateAreaTable

class metricCalc:
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
    
    # Initialization
    def __init__(self, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
              metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst):
        self.timer = DateTimer()
        AddMsg(self.timer.start() + " Setting up environment variables")
        # Run the setup
        self.metricsBaseNameList, self.optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize, 
                                                                                 os.path.dirname(outTable), 
                                                                                 [metricsToRun,optionalFieldGroups] )

        # XML Land Cover Coding file loaded into memory
        self.lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        self.lccClassesDict = self.lccObj.classes

        # If the user has checked the Intermediates option, name the tabulateArea table. This will cause it to be saved.
        self.tableName = None
        self.saveIntermediates = globalConstants.intermediateName in self.optionalGroupsList
        if self.saveIntermediates: 
            self.tableName = metricConst.shortName + globalConstants.tabulateAreaTableAbbv
            
        # Save other input parameters as class attributes
        self.outTable = outTable
        self.inReportingUnitFeature = inReportingUnitFeature
        self.reportingUnitIdField = reportingUnitIdField
        self.metricConst = metricConst
        self.inLandCoverGrid = inLandCoverGrid

    def _replaceLCGrid(self):
        # Placeholder for internal function to replace the landcover grid.  Several metric Calculations require this step, but others skip it.
        pass
    
    def _replaceRUFeatures(self):
        # Placeholder for internal function for buffer calculations - most calculations don't require this step.
        pass
    
    def _housekeeping(self):
        # Perform additional housekeeping steps - this must occur after any LCGrid or inRUFeature replacement
        
        # alert user if the land cover grid has values undefined in the LCC XML file
        utils.settings.checkGridValuesInLCC(self.inLandCoverGrid, self.lccObj)
        # alert user if the land cover grid cells are not square (default to size along x axis)
        utils.settings.checkGridCellDimensions(self.inLandCoverGrid)
        # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field    
        self.outIdField = utils.settings.getIdOutField(self.inReportingUnitFeature, self.reportingUnitIdField)
        
        # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
        self.zoneAreaDict = None
        if globalConstants.qaCheckName in self.optionalGroupsList: 
            self.zoneAreaDict = polygons.getIdAreaDict(self.inReportingUnitFeature, self.reportingUnitIdField)
        
        
    def _makeAttilaOutTable(self):
        AddMsg(self.timer.split() + " Constructing the ATtILA metric output table")
        # Internal function to construct the ATtILA metric output table
        self.newTable, self.metricsFieldnameDict = utils.table.tableWriterByClass(self.outTable, 
                                                                                  self.metricsBaseNameList, 
                                                                                  self.optionalGroupsList, 
                                                                                  self.metricConst, self.lccObj, 
                                                                                  self.outIdField)    
    def _makeTabAreaTable(self):
        AddMsg(self.timer.split() + " Generating a zonal tabulate area table")
        # Internal function to generate a zonal tabulate area table
        self.tabAreaTable = TabulateAreaTable(self.inReportingUnitFeature, self.reportingUnitIdField, 
                                              self.inLandCoverGrid, self.tableName, self.lccObj)
    
    def _calculateMetrics(self):
        AddMsg(self.timer.split() + " Processsing the tabulate area table and computing metric values")
        # Internal function to process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        # Default calculation is land cover proportions.  this may be overridden by some metrics.
        utils.calculate.landCoverProportions(self.lccClassesDict, self.metricsBaseNameList, self.optionalGroupsList, 
                                             self.metricConst, self.outIdField, self.newTable, self.tabAreaTable, 
                                             self.metricsFieldnameDict, self.zoneAreaDict)

    # Function to run all the steps in the calculation process    
    def run(self):    
        # Replace LandCover Grid, if necessary
        self._replaceLCGrid()
        
        # Replace Reporting Unit features, if necessary
        self._replaceRUFeatures()
        
        # Perform additional housekeeping
        self._housekeeping()
        
        # Make Output Tables
        self._makeAttilaOutTable()
        
        # Generate Tabulation tables
        self._makeTabAreaTable()
        
        # Run final metric calculation
        self._calculateMetrics()
        

def runLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                            metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover Proportion Metrics """   
    
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcpConstants()
        
        # Create new instance of metricCalc class to contain parameters
        lcpCalc = metricCalc(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                             metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        
        # Run Calculation
        lcpCalc.run()
  
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
        
        # Create new subclass of metric calculation
        class metricCalcLCOSP(metricCalc):
            # Subclass that overrides specific functions for the LandCoverOnSlopeProportions calculation
            def _replaceLCGrid(self):
                # replace the inLandCoverGrid
                self.inLandCoverGrid = utils.raster.getIntersectOfGrids(self.lccObj, self.inLandCoverGrid, self.inSlopeGrid, 
                                                                   self.inSlopeThresholdValue)
                
                if self.saveIntermediates:
                    self.inLandCoverGrid.save(arcpy.CreateScratchName(self.metricConst.shortName, "", "RasterDataset"))  
        
        # Create new instance of metricCalc class to contain parameters
        lcspCalc = metricCalcLCOSP(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        
        lcspCalc.inSlopeGrid = inSlopeGrid
        lcspCalc.inSlopeThresholdValue = inSlopeThresholdValue
        
        # Run Calculation
        lcspCalc.run()
        
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
        caeamCalc = metricCalcCAEAM(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        
        caeamCalc.inEdgeWidth = inEdgeWidth
        
        # Run Calculation
        caeamCalc.run()
  
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
        
        class metricCalcRLCP(metricCalc):
            """ Subclass that overrides buffering function for the RiparianLandCoverProportions calculation """
            def _replaceRUFeatures(self):
                # Generate a default filename for the buffer feature class
                self.bufferName = self.metricConst.shortName + self.inBufferDistance.split()[0]
                # Generate the buffer area to use in the metric calculation
                self.inReportingUnitFeature = utils.vector.bufferFeaturesByIntersect(self.inStreamFeatures, 
                                                                                     self.inReportingUnitFeature, 
                                                                                     self.bufferName, self.inBufferDistance, 
                                                                                     self.reportingUnitIdField)
            def __del__(self):
                """ Destructor function automatically called when the metric calculation class is no longer in use """
                if not self.saveIntermediates:
                    arcpy.Delete_management(self.bufferName)
        
        # Create new instance of metricCalc class to contain parameters
        rlcpCalc = metricCalcRLCP(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                       metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        
        # Assign class attributes unique to this module.  
        rlcpCalc.inStreamFeatures = inStreamFeatures
        rlcpCalc.inBufferDistance = inBufferDistance
        
        # Run Calculation
        rlcpCalc.run()
              
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()
        
def runSamplePointLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                            metricsToRun, inPointFeatures, ruLinkField, inBufferDistance, outTable, processingCellSize, snapRaster, 
                            optionalFieldGroups):
    """ Interface for script executing Sample Point Land Cover Proportion Metrics """   
    
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.splcpConstants()
        # append the buffer distance value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inBufferDistance.split()[0]
        
        class metricCalcSPLCP(metricCalc):
            """ Subclass that overrides specific functions for the SamplePointLandCoverProportions calculation """
            def _replaceRUFeatures(self):
                # Generate a default filename for the buffer feature class
                self.bufferName = self.metricConst.shortName + self.inBufferDistance.split()[0]
                # Buffer the points and use the output as the new reporting units
                self.inReportingUnitFeature = utils.vector.bufferFeaturesByID(self.inPointFeatures,
                                                                              self.inReportingUnitFeature,
                                                                              self.bufferName,self.inBufferDistance,
                                                                              self.reportingUnitIdField,self.ruLinkField)
            def __del__(self):
                """ Destructor function automatically called when the metric calculation class is no longer in use """
                if not self.saveIntermediates:
                    arcpy.Delete_management(self.bufferName)

        # Create new instance of metricCalc class to contain parameters
        splcpCalc = metricCalcSPLCP(inReportingUnitFeature, ruLinkField, inLandCoverGrid, lccFilePath, 
                       metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        
        # Assign class attributes unique to this module.  
        splcpCalc.inPointFeatures = inPointFeatures
        splcpCalc.inBufferDistance =  inBufferDistance
        splcpCalc.ruLinkField = ruLinkField
        
        # Run Calculation
        splcpCalc.run()
              
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
        
        # Create new LCC metric calculation subclass
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
        
        # Instantiate LCC metric calculation subclass 
        lccCalc = metricCalcLCC(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
              
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
        lccCalc.run()
        
    except Exception, e:
        errors.standardErrorHandling(e)
        
    finally:
        setupAndRestore.standardRestore()


        









