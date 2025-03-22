''' Interface for running specific metrics

'''
import os
import arcpy
import time
from arcpy.sa import Raster, Con
from . import errors
from . import setupAndRestore
from .utils import lcc
from .utils import polygons
from .utils import fields
from .utils import table
from .utils import calculate
from .utils import settings
from .utils import files
from .utils import vector
from .utils import environment
from .utils import parameters
from .utils import raster
from .utils import conversion
from .utils import log
from .utils import messages
from .utils.messages import AddMsg
from .datetimeutil import DateTimer
from .constants import metricConstants
from .constants import globalConstants
from .constants import errorConstants
from . import utils
from .utils.tabarea import TabulateAreaTable
from datetime import datetime
import traceback
import random
import string
from os.path import basename

from .utils import pandasutil


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
              metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst, logFile, ignoreHighest=False):
        self.timer = DateTimer()
        self.logFile = logFile
        AddMsg(f"{self.timer.now()} Setting up environment variables", 0, self.logFile)
        
        # Check to see if the user has specified a Processing cell size other than the cell size of the inLandCoverGrid
        inLandCoverGridCellSize = Raster(inLandCoverGrid).meanCellWidth
        if float(processingCellSize) != inLandCoverGridCellSize:
            AddMsg("Processing cell size and the cell size for the input Land cover grid are not equal. "\
                   "For the most accurate results, it is highly recommended to use the cell size of the input Land cover grid as the Processing cell size.", 1, self.logFile)
        
        # # Check to see if the inLandCoverGrid has an attribute table. If not, build one
        # raster.buildRAT(inLandCoverGrid, self.logFile)
        
        # Run the setup
        self.metricsBaseNameList, self.optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize,
                                                                                 os.path.dirname(outTable),
                                                                                 [metricsToRun,optionalFieldGroups])


        # XML Land Cover Coding file loaded into memory
        self.lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        self.lccClassesDict = self.lccObj.classes
        
        # If the user has checked the Intermediates option, name the tabulateArea table. This will cause it to be saved.
        self.tableName = None
        self.saveIntermediates = globalConstants.intermediateName in self.optionalGroupsList
        if self.saveIntermediates:
            self.tableName = metricConst.shortName + globalConstants.tabulateAreaTableAbbv

        # Set whether to add QA Fields as a class attribute
        self.addQAFields = globalConstants.qaCheckName in self.optionalGroupsList
        
        # Save other input parameters as class attributes
        self.outTable = outTable
        self.inReportingUnitFeature = inReportingUnitFeature
        self.reportingUnitIdField = reportingUnitIdField
        self.metricConst = metricConst
        self.inLandCoverGrid = inLandCoverGrid
        self.snapRaster = snapRaster
        self.processingCellSize = processingCellSize
        self.ignoreHighest = ignoreHighest
        self.scratchNameToBeDeleted =  ""
        self.reportingUnitAreaDict = None
        self.extentList = []

    def _replaceLCGrid(self):
        # Placeholder for internal function to replace the landcover grid.  Several metric Calculations require this step, but others skip it.
        pass

    def _replaceRUFeatures(self):
        # Placeholder for internal function for buffer calculations - most calculations don't require this step.
        pass
    
    def _housekeeping(self):
        # Perform additional housekeeping steps - this must occur after any LCGrid or inRUFeature replacement

        # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
        settings.checkExcludedValuesInClass(self.metricsBaseNameList, self.lccObj, self.lccClassesDict, self.logFile)
        # alert user if the land cover grid has values undefined in the LCC XML file
        settings.checkGridValuesInLCC(self.inLandCoverGrid, self.lccObj, self.logFile, self.ignoreHighest)
        # alert user if the land cover grid cells are not square (default to size along x axis)
        settings.checkGridCellDimensions(self.inLandCoverGrid, self.logFile)
        # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
        self.outIdField = settings.getIdOutField(self.inReportingUnitFeature, self.reportingUnitIdField)

        # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
        self.zoneAreaDict = None
        if globalConstants.qaCheckName in self.optionalGroupsList:
            # Check to see if an outputGeorgraphicCoordinate system is set in the environments. If one is not specified
            # return the spatial reference for the land cover grid. Use the returned spatial reference to calculate the
            # area of the reporting unit's polygon features to store in the zoneAreaDict
            self.outputSpatialRef = settings.getOutputSpatialReference(self.inLandCoverGrid)
            self.zoneAreaDict = polygons.getMultiPartIdAreaDict(self.inReportingUnitFeature, self.reportingUnitIdField, self.outputSpatialRef)


    def _makeAttilaOutTable(self):
        AddMsg(f"{self.timer.now()} Constructing the ATtILA metric output table: {os.path.basename(self.outTable)}", 0, self.logFile)
        # Internal function to construct the ATtILA metric output table
        self.newTable, self.metricsFieldnameDict = table.tableWriterByClass(self.outTable,
                                                                                  self.metricsBaseNameList,
                                                                                  self.optionalGroupsList,
                                                                                  self.metricConst, self.lccObj,
                                                                                  self.outIdField, self.logFile)
    def _makeTabAreaTable(self):
        AddMsg(self.timer.now() + " Generating a zonal tabulate area table", 0, self.logFile)
        # Internal function to generate a zonal tabulate area table
        self.tabAreaTable = TabulateAreaTable(self.inReportingUnitFeature, self.reportingUnitIdField,
                                              self.inLandCoverGrid, self.logFile, self.tableName, self.lccObj)

    def _calculateMetrics(self):
        AddMsg(self.timer.now() + " Processing the tabulate area table and computing metric values", 0, self.logFile)
        # Internal function to process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        # Default calculation is land cover proportions.  this may be overridden by some metrics.
        calculate.landCoverProportions(self.lccClassesDict, self.metricsBaseNameList, self.optionalGroupsList,
                                             self.metricConst, self.outIdField, self.newTable, self.tabAreaTable,
                                             self.metricsFieldnameDict, self.zoneAreaDict, self.reportingUnitAreaDict)

    def _summarizeOutTable(self):
        if self.logFile:
            AddMsg("Summarizing the ATtILA metric output table to log file", 0)
            # Internal function to analyze the output table fields for the log file. This may be overridden by some metrics
            # append the reporting unit id field to the list of category fields; even if it's a numeric field type
            self.metricConst.idFields = self.metricConst.idFields + [self.reportingUnitIdField]
            log.logWriteOutputTableInfo(self.newTable, self.logFile, self.metricConst)
            AddMsg("Summary complete", 0)
    
    def _logEnvironments(self):
        if self.logFile:
            # write environment settings
            log.writeEnvironments(self.logFile, self.snapRaster, self.processingCellSize, self.extentList)
            
            # write the metric class grid values to the log file
            log.logWriteClassValues(self.logFile, self.metricsBaseNameList, self.lccObj, self.metricConst)
    
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
        
        # Record Output Table info to log file
        self._summarizeOutTable()
               
        # Write Environment settings to the log file
        self._logEnvironments()
        
        # ensure cleanup occurs.
        if self.tabAreaTable != None:
            del self.tabAreaTable


def runLandCoverProportionsORIGINAL(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
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
    except Exception as e:
        errors.standardErrorHandling(e)

    finally:
        setupAndRestore.standardRestore()


def runLandCoverProportions(toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                                     metricsToRun, outTable, perCapitaYN, inCensusDataset, inPopField, processingCellSize, 
                                     snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover Proportion Metrics and Population Density Metrics """
    
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcpConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, 
                          outTable, perCapitaYN, inCensusDataset, inPopField, processingCellSize, snapRaster, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None.
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # Check to see if the inLandCoverGrid has an attribute table. If not, build one
        raster.buildRAT(inLandCoverGrid, logFile)
        
        # Create new subclass of metric calculation
        class metricCalcLCP(metricCalc):        
        
            def _makeAttilaOutTable(self):
                #AddMsg(self.timer.now() + " Constructing the ATtILA metric output table: "+self.outTable, 0, self.logFile)
                AddMsg(f"{self.timer.now()} Constructing the ATtILA metric output table: {os.path.basename(self.outTable)}", 0, self.logFile)
                # Internal function to construct the ATtILA metric output table
                if perCapitaYN == "true":     
                    self.newTable, self.metricsFieldnameDict = table.tableWriterByClass(self.outTable, 
                                                                                        self.metricsBaseNameList,
                                                                                        self.optionalGroupsList, 
                                                                                        self.metricConst, 
                                                                                        self.lccObj, 
                                                                                        self.outIdField, 
                                                                                        self.logFile,
                                                                                        self.metricConst.additionalFields)
                else:
                    self.newTable, self.metricsFieldnameDict = table.tableWriterByClass(self.outTable,
                                                                                        self.metricsBaseNameList,
                                                                                        self.optionalGroupsList,
                                                                                        self.metricConst, 
                                                                                        self.lccObj,
                                                                                        self.outIdField,
                                                                                        self.logFile)     
        
            def _calculateMetrics(self):
                # Initiate our flexible cleanuplist
                if lcpCalc.saveIntermediates:
                    lcpCalc.cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
                else:
                    lcpCalc.cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
                    
                self.zonePopulationDict = None
                if perCapitaYN == "true":
                    self.index = 0
                    
                    # Generate name for reporting unit population count table.
                    self.popTable = files.nameIntermediateFile([metricConst.valueCountTableName,'Dataset'],self.cleanupList)

                    # Generate table with population counts by reporting unit
                    AddMsg(self.timer.now() + " Calculating population within each reporting unit", 0, self.logFile) 
                    self.populationTable, self.populationField = table.createPolygonValueCountTable(self.inReportingUnitFeature,
                                                                         self.reportingUnitIdField,
                                                                         self.inCensusDataset,
                                                                         self.inPopField,
                                                                         self.popTable,
                                                                         self.metricConst,
                                                                         self.index,
                                                                         self.cleanupList,
                                                                         self.logFile)
                    
                    # Assemble dictionary with the reporting unit's ID as key, and the area-weighted population as the value
                    self.zonePopulationDict = table.getIdValueDict(self.populationTable, 
                                                                   self.reportingUnitIdField, 
                                                                   self.populationField)

                
                AddMsg(self.timer.now() + " Processing the tabulate area table and computing metric values", 0, self.logFile)
                # Internal function to process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
                # Default calculation is land cover proportions.  this may be overridden by some metrics.
                calculate.landCoverProportions(self.lccClassesDict, self.metricsBaseNameList, self.optionalGroupsList,
                                               self.metricConst, self.outIdField, self.newTable, self.tabAreaTable,
                                               self.metricsFieldnameDict, self.zoneAreaDict, self.reportingUnitAreaDict, self.zonePopulationDict,
                                               self.conversionFactor)

        
        # Create new instance of metricCalc class to contain parameters
        lcpCalc = metricCalcLCP(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                             metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst, logFile)
        
        # Assign class attributes unique to this module.
        lcpCalc.logFile
        lcpCalc.perCapitaYN = perCapitaYN
        lcpCalc.inCensusDataset = inCensusDataset
        lcpCalc.inPopField = inPopField
        lcpCalc.extentList = [inReportingUnitFeature, inLandCoverGrid, inCensusDataset]
        lcpCalc.cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup

        # see what linear units are used in the tabulate area table
        outputLinearUnits = settings.getOutputLinearUnits(inLandCoverGrid)

        # using the output linear units, get the conversion factor to convert the tabulateArea area measures to square meters
        try:
            conversionFactor = conversion.getSqMeterConversionFactor(outputLinearUnits)
        except:
            raise errors.attilaException(errorConstants.linearUnitConversionError)

        # Set the conversion factor as a class attribute
        lcpCalc.conversionFactor = conversionFactor

        
        # Run Calculation
        lcpCalc.run()
    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
        
        errors.standardErrorHandling(e, logFile)

    finally:
        if not lcpCalc.cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in lcpCalc.cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete", 0)
        
        setupAndRestore.standardRestore(logFile)
        

def runLandCoverOnSlopeProportions(toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                                   metricsToRun, inSlopeGrid, inSlopeThresholdValue, outTable, processingCellSize,
                                   snapRaster, optionalFieldGroups, clipLCGrid):
    """ Interface for script executing Land Cover on Slope Proportions (Land Cover Slope Overlap)"""

    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcospConstants()
        # append the slope threshold value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inSlopeThresholdValue
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, 
                          inSlopeGrid, inSlopeThresholdValue, outTable, processingCellSize, snapRaster, optionalFieldGroups, clipLCGrid]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # Check to see if the inLandCoverGrid has an attribute table. If not, build one
        raster.buildRAT(inLandCoverGrid, logFile)
        
        # # This block of code can be used if we want to change the Slope Threshold input to a double parameter type
        # # If we do that, we'd also have to change the tool validation property to comment out the inZeroAndAboveIntegerIndex = 7 line 
        # # to cause a check for integer values

        # # validThresholdValue = inSlopeThresholdValue
        # # aDecimal = '.'
        # # aNegative = '-'
        # # firstCharacter = inSlopeThresholdValue[0]
        # # if firstCharacter == aNegative:
        # #     validThresholdValue = inSlopeThresholdValue.replace(firstCharacter, "n", 1)
        # #
        # # if aDecimal in validThresholdValue:
        # #     finalThresholdValue = validThresholdValue.replace(".","pt")
        # # else:
        # #     finalThresholdValue = validThresholdValue
        
        #If clipLCGrid is selected, clip the input raster to the extent of the reporting unit theme or the to the extent
        #of the selected reporting unit(s). If the metric is susceptible to edge-effects (e.g., core and edge metrics, 
        #patch metrics) extend the clip envelope an adequate distance.       
        
        from arcpy import env        
        _tempEnvironment1 = env.workspace
        env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))

        if clipLCGrid == "true":
            inLandCoverGrid, scratchName = raster.clipRaster(inReportingUnitFeature, inLandCoverGrid, DateTimer, metricConst, logFile)
            
        
        # Create new subclass of metric calculation
        class metricCalcLCOSP(metricCalc):
            # Subclass that overrides specific functions for the LandCoverOnSlopeProportions calculation
            def _replaceLCGrid(self):
                # replace the inLandCoverGrid
                self.inLandCoverGrid = raster.getIntersectOfGrids(self.lccObj, self.inLandCoverGrid, self.inSlopeGrid,
                                                                   self.inSlopeThresholdValue,self.timer, self.logFile)

                if self.saveIntermediates:
                    self.namePrefix = self.metricConst.shortName+"_"+"Raster"+metricConst.fieldParameters[1]+"_"
                    self.scratchName = arcpy.CreateScratchName(self.namePrefix, "", "RasterDataset")
                    self.inLandCoverGrid.save(self.scratchName)
                    AddMsg(f"{self.timer.now()} Save intermediate grid complete: {basename(self.scratchName)}", 0, self.logFile)
                    
        # Set toogle to ignore 'below slope threshold' marker in slope/land cover hybrid grid when checking for undefined values
        ignoreHighest = True
        
        # Create new instance of metricCalc class to contain parameters
        lcspCalc = metricCalcLCOSP(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst, logFile, ignoreHighest)

        lcspCalc.inSlopeGrid = inSlopeGrid
        lcspCalc.inSlopeThresholdValue = inSlopeThresholdValue
        lcspCalc.extentList = [inReportingUnitFeature, inLandCoverGrid, inSlopeGrid]

        # Run Calculation
        lcspCalc.run()
        
        if clipLCGrid == "true":
            arcpy.Delete_management(scratchName) 

    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
        
        errors.standardErrorHandling(e, logFile)

    finally:
        setupAndRestore.standardRestore(logFile)
        
        if arcpy.glob.os.path.basename(arcpy.sys.executable) == globalConstants.arcExecutable:
            env.workspace = _tempEnvironment1
        
        
def runFloodplainLandCoverProportions(toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                                   metricsToRun, inFloodplainGeodataset, outTable, processingCellSize, snapRaster, 
                                   optionalFieldGroups, clipLCGrid):
    """ Interface for script executing Floodplain Land Cover Proportions """
        
    try:
        timer = DateTimer()
        
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.flcpConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, 
                          inFloodplainGeodataset, outTable, processingCellSize, snapRaster, optionalFieldGroups, clipLCGrid]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # Check to see if the inLandCoverGrid has an attribute table. If not, build one
        raster.buildRAT(inLandCoverGrid, logFile)
          
        #If clipLCGrid is selected, clip the input raster to the extent of the reporting unit theme or the to the extent
        #of the selected reporting unit(s). If the metric is susceptible to edge-effects (e.g., core and edge metrics, 
        #patch metrics) extend the clip envelope an adequate distance.        
        from arcpy import env        
        _tempEnvironment1 = env.workspace
        env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))

        if clipLCGrid == "true":
            inLandCoverGrid, scratchName = raster.clipRaster(inReportingUnitFeature, inLandCoverGrid, DateTimer, metricConst, logFile)
  
          
        # Create new subclass of metric calculation
        class metricCalcFLCPRaster(metricCalc):
            # Subclass that overrides specific functions for the FloodplainLandCoverProportions calculation
            def _replaceLCGrid(self):
                # Initiate our flexible cleanuplist
                if flcpCalc.saveIntermediates:
                    flcpCalc.cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
                else:
                    flcpCalc.cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
                
                # replace the inLandCoverGrid
                AddMsg(f"{self.timer.now()} Generating land cover in floodplain grid", 0, self.logFile)
                self.inLandCoverGrid = raster.getSetNullGrid(self.inFloodplainGeodataset, self.inLandCoverGrid, self.nullValuesList, self.logFile)
                    
                if self.saveIntermediates:
                    self.namePrefix = self.metricConst.landcoverGridName
                    self.scratchName = arcpy.CreateScratchName(self.namePrefix, "", "RasterDataset")
                    self.inLandCoverGrid.save(self.scratchName)
                    AddMsg(f"{self.timer.now()} Save intermediate grid complete: {basename(self.scratchName)}", 0, self.logFile)
                    
                    
            def _housekeeping(self):
                # Perform additional housekeeping steps - this must occur after any LCGrid or inRUFeature replacement
            
                # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
                settings.checkExcludedValuesInClass(self.metricsBaseNameList, self.lccObj, self.lccClassesDict, self.logFile)
                # alert user if the land cover grid has values undefined in the LCC XML file
                settings.checkGridValuesInLCC(self.inLandCoverGrid, self.lccObj, self.logFile, self.ignoreHighest)
                # alert user if the land cover grid cells are not square (default to size along x axis)
                settings.checkGridCellDimensions(self.inLandCoverGrid, self.logFile)
                # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
                self.outIdField = settings.getIdOutField(self.inReportingUnitFeature, self.reportingUnitIdField)
            
                # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
                self.zoneAreaDict = None
                if self.addQAFields:
                    AddMsg(f"{self.timer.now()} Tabulating the area of the floodplains within each reporting unit", 0, self.logFile)
                    fpTabAreaTable = files.nameIntermediateFile([self.metricConst.fpTabAreaName, "Dataset"], self.cleanupList)   

                    log.logArcpy("arcpy.sa.TabulateArea",(self.inReportingUnitFeature, self.reportingUnitIdField, self.inFloodplainGeodataset, "VALUE", fpTabAreaTable, processingCellSize),logFile)            
                    arcpy.sa.TabulateArea(self.inReportingUnitFeature, self.reportingUnitIdField, self.inFloodplainGeodataset, "VALUE", fpTabAreaTable, processingCellSize)
            
                    # This technique allows the use of all non-zero values in a grid to designate floodplain areas instead of just '1'. 
                    self.excludedValueFields = ["VALUE_0"]
                    self.zoneAreaDict = table.getZoneSumValueDict(fpTabAreaTable, self.reportingUnitIdField, self.excludedValueFields)
                                    
                     
        class metricCalcFLCPPolygon(metricCalc):
            # Subclass that overrides specific functions for the FloodplainLandCoverProportions calculation
            def _replaceRUFeatures(self):
                # Initiate our flexible cleanuplist
                if flcpCalc.saveIntermediates:
                    flcpCalc.cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
                else:
                    flcpCalc.cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
                     
                # Generate a default filename for the output feature class
                self.zonesName = self.metricConst.zoneByRUName
                 
                # replace the inReportingUnitFeature
                self.inReportingUnitFeature, self.cleanupList = vector.getIntersectOfPolygons(self.inReportingUnitFeature, 
                                                                                              self.reportingUnitIdField, 
                                                                                              self.inFloodplainGeodataset,
                                                                                              self.zonesName, 
                                                                                              self.cleanupList, 
                                                                                              self.timer,
                                                                                              self.logFile)
 
  
        # Do a Describe on the floodplain input to determine if it is a raster or polygon feature
        desc = arcpy.Describe(inFloodplainGeodataset)
         
        if desc.datasetType == "RasterDataset":
            # Create new instance of metricCalc class to contain parameters
            flcpCalc = metricCalcFLCPRaster(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst, logFile)
        else:
            # Create new instance of metricCalc class to contain parameters
            flcpCalc = metricCalcFLCPPolygon(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst, logFile)
         
        # Assign class attributes unique to this module.
        flcpCalc.inFloodplainGeodataset = inFloodplainGeodataset
        flcpCalc.nullValuesList = [0] # List of values in the binary floodplain grid to set to null
        flcpCalc.cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
        flcpCalc.extentList = [inReportingUnitFeature, inLandCoverGrid, inFloodplainGeodataset] # List of input themes to find the intersection extent
        
        # Before generating the replacement reporting unit feature, if QA Fields is selected, get a dictionary of the reporting unit polygon area
        # and the effective area within the reporting unit (i.e., the land area in the reporting unit if water areas are excluded). If no grid values 
        # are tagged as excluded, these values are identical. Use this dictionary to calculate 1) what percentage of the reporting unit's effective area 
        # is within the replacement reporting unit boundaries (e.g., 18% of the effective area within the reporting unit is in the riparian buffer zone), and
        # 2) the overall percentage of the reporting unit that is within the buffer area (e.g., 25% of the reporting unit is in the riparian buffer zone).
        if flcpCalc.addQAFields:
            # First generate the dictionary with the RU ID as the key and the vector measurement of the reporting unit area as its value. 
            outputSpatialRef = settings.getOutputSpatialReference(inLandCoverGrid)
            flcpCalc.reportingUnitAreaDict = polygons.getMultiPartIdAreaDict(inReportingUnitFeature, reportingUnitIdField, outputSpatialRef)
            
            # Now alter the dictionary's value to be a list with two values: 
            # index 0 will be the vector measure of the reporting unit polygon, and 
            # index 1 will be the raster measure of the effective area within the reporting unit.
        
            # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area total    
            lccValuesDict = flcpCalc.lccObj.values
            # Get the grid values for the input land cover grid
            landCoverValues = raster.getRasterValues(inLandCoverGrid, logFile)
            # get the list of excluded values that are found in the input land cover raster
            excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)
            
            if len(excludedValuesList) > 0:
                AddMsg(f"{timer.now()} Excluded values found in the land cover grid. Calculating effective areas for each reporting unit", 0, flcpCalc.logFile)
                # Use ATtILA's TabulateAreaTable operation to return an object where a tabulate area table can be easily queried.
                if flcpCalc.saveIntermediates:
                    # name the table so that it will be saved
                    ruTableName = metricConst.shortName + globalConstants.ruTabulateAreaTableAbbv
                else:
                    ruTableName = None
                ruAreaTable = TabulateAreaTable(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, logFile, ruTableName, flcpCalc.lccObj)
                
                for ruAreaTableRow in ruAreaTable:
                    key = ruAreaTableRow.zoneIdValue
                    area = ruAreaTableRow.effectiveArea
                    # make the value of key a list
                    flcpCalc.reportingUnitAreaDict[key] = [flcpCalc.reportingUnitAreaDict[key]]
                    flcpCalc.reportingUnitAreaDict[key].append(area)
            
            else:
                AddMsg(f"{timer.now()} No excluded values found in the land cover grid. Reporting unit effective area equals total reporting unit area. Recording reporting unit areas", flcpCalc.logFile)
                for aKey in flcpCalc.reportingUnitAreaDict.keys():
                    area = flcpCalc.reportingUnitAreaDict[aKey]
                    # make the value of key a list
                    flcpCalc.reportingUnitAreaDict[aKey] = [flcpCalc.reportingUnitAreaDict[aKey]]
                    flcpCalc.reportingUnitAreaDict[aKey].append(area)                    
        

        # Run Calculation 
        flcpCalc.run()
          
        if clipLCGrid == "true":
            arcpy.Delete_management(scratchName) 
 
    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
            
        errors.standardErrorHandling(e, logFile)
 
    finally:
        if not flcpCalc.cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in flcpCalc.cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete", 0)
        
        setupAndRestore.standardRestore(logFile)
        
        if arcpy.glob.os.path.basename(arcpy.sys.executable) == globalConstants.arcExecutable:
            env.workspace = _tempEnvironment1


def runPatchMetrics(toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun,
                          inPatchSize, inMaxSeparation, outTable, mdcpYN, processingCellSize, snapRaster, 
                          optionalFieldGroups, clipLCGrid):
    """ Interface for script executing Patch Metrics """

    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        # Start the timer
        timer = DateTimer()
        
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.pmConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun,
                          inPatchSize, inMaxSeparation, outTable, mdcpYN, processingCellSize, snapRaster, optionalFieldGroups, clipLCGrid]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # Check to see if the inLandCoverGrid has an attribute table. If not, build one
        raster.buildRAT(inLandCoverGrid, logFile)
        
        AddMsg(f"{timer.now()} Setting up initial environment variables", 0, logFile)
        
        # index the reportingUnitIdField to speed query results
        ruIdIndex = "ruIdIndex_ATtILA"
        indexNames = [indx.name for indx in arcpy.ListIndexes(inReportingUnitFeature)]
        if ruIdIndex not in indexNames:
            arcpy.AddIndex_management(inReportingUnitFeature, reportingUnitIdField, ruIdIndex)
        
        # setup the appropriate metric fields to add to output table depending on if MDCP is selected or not
        if mdcpYN == "true":
            metricConst.additionalFields = metricConst.additionalFields + metricConst.mdcpFields
        else:
            metricConst.additionalFields = metricConst.additionalFields
            
        
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize,
                                                                                os.path.dirname(outTable),
                                                                                [metricsToRun,optionalFieldGroups])
        
        if globalConstants.intermediateName in optionalGroupsList:
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))

        lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        lccClassesDict = lccObj.classes
        
        # Check to see if an outputGeorgraphicCoordinate system is set in the environments. If one is not specified
        # return the spatial reference for the land cover grid. Use the returned spatial reference to calculate the
        # area of the reporting unit's polygon features to store in the zoneAreaDict
        outputSpatialRef = settings.getOutputSpatialReference(inLandCoverGrid)

        # Compile a dictionary with key:value pair of ZoneId:ZoneArea
        zoneAreaDict = polygons.getMultiPartIdAreaDict(inReportingUnitFeature, reportingUnitIdField, outputSpatialRef)
        
        # see what linear units are output in any tabulate area calculations
        outputLinearUnits = settings.getOutputLinearUnits(inLandCoverGrid)        

        # using the output linear units, get the conversion factor to convert area measures to metric appropriate values
        try:
            conversionFactor = conversion.getSqMeterConversionFactor(outputLinearUnits)
        except:
            raise errors.attilaException(errorConstants.linearUnitConversionError)
        
        # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
        settings.checkExcludedValuesInClass(metricsBaseNameList, lccObj, lccClassesDict, logFile)
        
        # alert user if the land cover grid has values undefined in the LCC XML file
        settings.checkGridValuesInLCC(inLandCoverGrid, lccObj, logFile)
        
        # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
        outIdField = settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
         
        #Create the output table outside of metricCalc so that result can be added for multiple metrics
        AddMsg(f"{timer.now()} Constructing the ATtILA metric output table: {basename(outTable)}", 0, logFile)
        newtable, metricsFieldnameDict = table.tableWriterByClass(outTable, metricsBaseNameList,optionalGroupsList, 
                                                                                  metricConst, lccObj, outIdField, logFile,
                                                                                  metricConst.additionalFields)
                
        #If clipLCGrid is selected, clip the input raster to the extent of the reporting unit theme or the to the extent
        #of the selected reporting unit(s). If the metric is susceptible to edge-effects (e.g., core and edge metrics, 
        #patch metrics) extend the clip envelope an adequate distance.

        if clipLCGrid == "true":
            from arcpy import env        
            _startingWorkSpace= env.workspace
            env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))
            inLandCoverGrid, scratchName = raster.clipRaster(inReportingUnitFeature, inLandCoverGrid, DateTimer, metricConst, logFile)
            env.workspace = _startingWorkSpace
        
            
        # Run metric calculate for each metric in list
        for m in metricsBaseNameList:
            # Subclass that overrides specific functions for the MDCP calculation
            class metricCalcPM(metricCalc):

                def _replaceLCGrid(self):
                    # replace the inLandCoverGrid
                    AddMsg(f"{self.timer.now()} Creating Patch Grid for Class:{m}", 0, self.logFile)
                    scratchNameReference = [""]
                    self.inLandCoverGrid = raster.createPatchRaster(m, self.lccObj, self.lccClassesDict, self.inLandCoverGrid,
                                                                    self.metricConst, self.maxSeparation, self.minPatchSize, 
                                                                    timer, scratchNameReference, self.logFile)
                    self.scratchNameToBeDeleted = scratchNameReference[0]
                    AddMsg(f"{self.timer.now()} Patch Grid Completed for Class:{m}. Intermediate: {basename(self.scratchNameToBeDeleted)}", 0, self.logFile)

                #skip over make out table since it has already been made
                def _makeAttilaOutTable(self):
                    pass

                #set the tabAreaTable attribute for the metric class to "None" since this metric does not require it
                def _makeTabAreaTable(self):
                    self.tabAreaTable = None
                
                #Update housekeeping so it doesn't check for lcc codes
                def _housekeeping(self):
                    # Perform additional housekeeping steps - this must occur after any LCGrid or inRUFeature replacement
                    # Removed alert about lcc codes since the lcc values are not used in the Core/Edge calculations
                    # alert user if the land cover grid cells are not square (default to size along x axis)
                    settings.checkGridCellDimensions(self.inLandCoverGrid, self.logFile)
                        
                # Update calculateMetrics to populate Patch Metrics and MDCP
                def _calculateMetrics(self):
                    AddMsg(f"{self.timer.now()} Calculating Patch Numbers by Reporting Unit for Class:{m}", 0, self.logFile)
                    
                    per = '[PER UNIT]'
                    AddMsg(f"{timer.now()} The following steps will be performed for each reporting unit:", 0, logFile)    
                    AddMsg("\n---")
                    AddMsg(f"{timer.now()} {per} 1) Create a feature layer of the single reporting unit.", 0, logFile)
                    AddMsg(f"{timer.now()} {per} 2) Set the geoprocessing extent to just the extent of the selected reporting unit.", 0, logFile)
                    AddMsg(f"{timer.now()} {per} 3) Copy the single reporting unit feature layer to a new feature class.", 0, logFile)
                    AddMsg(f"{timer.now()} {per} 4) Calculate the area of patches within reporting unit with TabulateArea:", 0, logFile)
                    AddMsg(f"{timer.now()} {per}     4a) arcpy.sa.TabulateArea(newFeatureClass, reportingUnitIdField, inLandCoverGrid,'Value', tabareaTable, processingCellSize)", 0, logFile)
                    AddMsg(f"{timer.now()} {per} 5) Loop through each row in the TabulateArea table (only one row in table) and calculate the patch metrics: ", 0, logFile)
                    AddMsg(f"{timer.now()} {per}     5a) other area = value of 'Value_0' field ", 0, logFile)
                    AddMsg(f"{timer.now()} {per}     5b) excluded area = value of 'Value__9999' field", 0, logFile)
                    AddMsg(f"{timer.now()} {per}     5c) create a list of all patch area values for the row (all fields except 'Value_0' and 'Value__9999'):", 0, logFile)
                    AddMsg(f"{timer.now()} {per}       c1) numPatch = len(patchAreaList)", 0, logFile)
                    AddMsg(f"{timer.now()} {per}       c2) patchArea = sum(patchAreaList)", 0, logFile)
                    AddMsg(f"{timer.now()} {per}       c3) lrgPatch = max(patchAreaList)", 0, logFile)
                    AddMsg(f"{timer.now()} {per}       c4) mdnpatch = numpy.median(patchAreaList)", 0, logFile)
                    AddMsg(f"{timer.now()} {per}       c5) avePatch = patchArea/numPatch", 0, logFile)
                    AddMsg(f"{timer.now()} {per}       c6) lrgProportion = (lrgPatch/patchArea) * 100", 0, logFile)
                    AddMsg(f"{timer.now()} {per}       c7) patchDensity = numPatch/(patchArea + otherArea) in square kilometers", 0, logFile)    
                    AddMsg(f"{timer.now()} {per} 6) Insert calculated values into Output table.", 0, logFile)
                    AddMsg(f"{timer.now()} {per} 7) Delete reporting unit feature layer, reporting unit feature class, and TabulateArea table.", 0, logFile)
                    AddMsg("---\n")
                    
                    # calculate Patch metrics
                    AddMsg(f"{timer.now()} Starting calculations per reporting unit...", 0, logFile)
                    self.pmResultsDict = calculate.getPatchNumbers(self.outIdField, self.newTable, self.reportingUnitIdField, self.metricsFieldnameDict,
                                                      self.zoneAreaDict, self.metricConst, m, self.inReportingUnitFeature, 
                                                      self.inLandCoverGrid, processingCellSize, conversionFactor)
 
                    AddMsg(f"{timer.now()} Patch analysis has been run for Class:{m}", 0, self.logFile)
                    
                    # get class name (may have been modified from LCC XML input by ATtILA)
                    outClassName = metricsFieldnameDict[m][1]
                    
                    if mdcpYN == "true": #calculate MDCP value
                    
                        AddMsg(f"{self.timer.now()} Calculating MDCP for Class:{m}", 0, self.logFile)
                        
                        # create and name intermediate data layers
                        rastoPolyFeatureName = f"{metricConst.shortName}_{outClassName}_{metricConst.rastertoPoly}_"
                        rastoPolyFeature = files.nameIntermediateFile([rastoPolyFeatureName, "FeatureClass"], cleanupList)
                        rasterCentroidFeatureName = f"{metricConst.shortName}_{outClassName}_{metricConst.rastertoPoint}_"
                        rasterCentroidFeature = files.nameIntermediateFile([rasterCentroidFeatureName, "FeatureClass"], cleanupList)
                        polyDissolvedPatchFeatureName = f"{metricConst.shortName}_{outClassName}_{metricConst.polyDissolve}_"
                        polyDissolvedFeature = files.nameIntermediateFile([polyDissolvedPatchFeatureName, "FeatureClass"], cleanupList)
                        nearPatchTable = files.nameIntermediateFile([outClassName + metricConst.nearTable, "Dataset"], cleanupList)            
                        
                        # run the calculation script. get the results back as a dictionary keyed to RU id values
                        self.mdcpDict =  vector.tabulateMDCP(self.inLandCoverGrid, self.inReportingUnitFeature, 
                                                                   self.reportingUnitIdField, rastoPolyFeature, rasterCentroidFeature, polyDissolvedFeature,
                                                                   nearPatchTable, self.zoneAreaDict, timer, self.pmResultsDict, self.logFile)
                        # place the results into the output table
                        calculate.getMDCP(self.outIdField, self.newTable, self.mdcpDict, self.optionalGroupsList,
                                                 outClassName)
                        
                        AddMsg(f"{self.timer.now()} MDCP analysis has been run for Class:{m}", 0, self.logFile)
                    
                    if self.saveIntermediates:
                        pass
                    else:
                        arcpy.Delete_management(pmCalc.scratchNameToBeDeleted)
                
                #skip over output table statistics routine as it will be performed later
                def _summarizeOutTable(self):
                    pass
                
                def _logEnvironments(self):
                    pass

            # Create new instance of metricCalc class to contain parameters
            pmCalc = metricCalcPM(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                      m, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst, logFile)
            
            pmCalc.newTable = newtable
            pmCalc.metricsFieldnameDict = metricsFieldnameDict
            pmCalc.maxSeparation = inMaxSeparation
            pmCalc.minPatchSize = inPatchSize
            pmCalc.outIdField = outIdField
            pmCalc.zoneAreaDict = zoneAreaDict
            
            #Run Calculation
            pmCalc.run()
            
            pmCalc.metricsBaseNameList = metricsBaseNameList
 
        
        if logFile:
            AddMsg("Summarizing the ATtILA metric output table to log file", 0)
            # append the reporting unit id field to the list of category fields; even if it's a numeric field type
            metricConst.idFields = metricConst.idFields + [reportingUnitIdField]
            log.logWriteOutputTableInfo(outTable, logFile, metricConst)
            AddMsg("Summary complete", 0)   
            
            # write the standard environment settings to the log file
            log.writeEnvironments(logFile, snapRaster, processingCellSize, extentList=[inReportingUnitFeature, inLandCoverGrid])
            # parameters are: logFile, snapRaster, processingCellSize, extentList
            # if extentList is set to None, the env.extent setting will reported.
            # Place eventList here, if the extents of the datasets have been altered and you wish to use the new extents.
            # for snapRaster and processingCellSize, if the parameter is None, no entry will
            # will be recorded in the log for that parameter
            
            # write the class definitions to the log file
            log.logWriteClassValues(logFile, metricsBaseNameList, lccObj, metricConst)
        
        
        if clipLCGrid == "true":
            arcpy.Delete_management(scratchName)     
    
    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
            
        errors.standardErrorHandling(e, logFile)

    finally:
        setupAndRestore.standardRestore(logFile)
        
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete")
        
        indexNames = [indx.name for indx in arcpy.ListIndexes(inReportingUnitFeature)]
        if ruIdIndex in indexNames:
            arcpy.RemoveIndex_management(inReportingUnitFeature, ruIdIndex)


def runCoreAndEdgeMetrics(toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun,
                          inEdgeWidth, outTable, processingCellSize, snapRaster, optionalFieldGroups, clipLCGrid):
    """ Interface for script executing Core/Edge Metrics """

    try:
        timer = DateTimer()
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.caemConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun,
                          inEdgeWidth, outTable, processingCellSize, snapRaster, optionalFieldGroups, clipLCGrid]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # grab the current date and time for log file
        metricConst.logTimeStamp = datetime.now().strftime(globalConstants.logFileExtension)
        # append the edge width distance value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inEdgeWidth
        # for the core and edge fields, add the edge width to the  field suffix
        for i, fldParams in enumerate(metricConst.additionalFields):
            fldParams[1] = metricConst.additionalSuffixes[i] + inEdgeWidth
        
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize,
                                                                                os.path.dirname(outTable),
                                                                                [metricsToRun,optionalFieldGroups])

        lccObj = lcc.LandCoverClassification(lccFilePath)
        
        if logFile:
            # write the metric class grid values to the log file
            log.logWriteClassValues(logFile, metricsBaseNameList, lccObj, metricConst)
        
        # get the dictionary with the LCC CLASSES attributes
        lccClassesDict = lccObj.classes
        
        outIdField = settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
        
        # Check to see if the inLandCoverGrid has an attribute table. If not, build one
        raster.buildRAT(inLandCoverGrid, logFile)
                
        # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
        settings.checkExcludedValuesInClass(metricsBaseNameList, lccObj, lccClassesDict, logFile)
        
        # alert user if the land cover grid has values undefined in the LCC XML file
        settings.checkGridValuesInLCC(inLandCoverGrid, lccObj, logFile)
     
        #Create the output table outside of metricCalc so that result can be added for multiple metrics
        AddMsg(f"{timer.now()} Constructing the ATtILA metric output table: {basename(outTable)}", 0, logFile)
        newtable, metricsFieldnameDict = table.tableWriterByClass(outTable, metricsBaseNameList,optionalGroupsList, 
                                                                                  metricConst, lccObj, outIdField, logFile,
                                                                                  metricConst.additionalFields)
 
        #If clipLCGrid is selected, clip the input raster to the extent of the reporting unit theme or the to the extent
        #of the selected reporting unit(s). If the metric is susceptible to edge-effects (e.g., core and edge metrics, 
        #patch metrics) extend the clip envelope an adequate distance.       

        from arcpy import env        
        _tempEnvironment1 = env.workspace
        env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))


        if clipLCGrid == "true":
            inLandCoverGrid, scratchName = raster.clipRaster(inReportingUnitFeature, inLandCoverGrid, DateTimer, metricConst, logFile, inEdgeWidth)
        
        
        # Run metric calculate for each metric in list
        for m in metricsBaseNameList:
        
            class metricCalcCAEM(metricCalc):
                # Subclass that overrides specific functions for the CoreAndEdgeAreaMetric calculation
                def _replaceLCGrid(self):                      
                    # replace the inLandCoverGrid
                    AddMsg(f"{self.timer.now()} Generating core and edge grid for Class: {m.upper()}", 0, self.logFile)
                    
                    scratchNameReference =  [""];
                    self.inLandCoverGrid = raster.getEdgeCoreGrid(m, self.lccObj, self.lccClassesDict, self.inLandCoverGrid, self.inEdgeWidth,
                                                                        self.timer, metricConst.shortName, scratchNameReference, self.logFile)
                    self.scratchNameToBeDeleted = scratchNameReference[0]
                    AddMsg(f"{self.timer.now()} Class {m.upper()} core and edge grid complete. Intermediate: {os.path.basename(self.scratchNameToBeDeleted)}", 0, self.logFile)
                    
                    #Moved the save intermediate grid to the calcMetrics function so it would be one of the last steps to be performed

                #skip over make out table since it has already been made
                def _makeAttilaOutTable(self):
                    pass  
                
                def _makeTabAreaTable(self):
                    AddMsg(f"{self.timer.now()} Generating a zonal tabulate area table", 0, self.logFile)
                    # Internal function to generate a zonal tabulate area table
                    class categoryTabAreaTable(TabulateAreaTable):
                        #Update definition so Tabulate Table is run on the POS field.
                        def _createNewTable(self):
                            self._value = "CATEGORY"
                            if self._tableName:
                                self._destroyTable = False
                                self._tableName = arcpy.CreateScratchName(self._tableName+m.upper()+inEdgeWidth+"_", "", self._datasetType)
                            else:
                                self._tableName = arcpy.CreateScratchName(self._tempTableName+m.upper()+inEdgeWidth+"_", "", self._datasetType)

                            log.logArcpy('arcpy.gp.TabulateArea_sa', (self._inReportingUnitFeature, self._reportingUnitIdField, self._inLandCoverGrid, 
                                  self._value, self._tableName), logFile)
                            arcpy.gp.TabulateArea_sa(self._inReportingUnitFeature, self._reportingUnitIdField, self._inLandCoverGrid, self._value, self._tableName)
                            
                            self._tabAreaTableRows = arcpy.SearchCursor(self._tableName)        
                            self._tabAreaValueFields = arcpy.ListFields(self._tableName, "", "DOUBLE")
                            self._tabAreaValues = [aFld.name for aFld in self._tabAreaValueFields]
                            self._tabAreaDict = dict(zip(self._tabAreaValues,[])) 
                             
                    self.lccObj = None
                    
                    self.tabAreaTable = categoryTabAreaTable(self.inReportingUnitFeature, self.reportingUnitIdField,
                                              self.inLandCoverGrid, self.tableName, self.lccObj)
                    
                # Update housekeeping. Moved checks for undefined grid values and excluded grid values in class definitions
                # out of the for loop. Now they are only ran once at the beginning of the metric run
                def _housekeeping(self):
                    # Perform additional housekeeping steps - this must occur after any LCGrid or inRUFeature replacement

                    # alert user if the land cover grid cells are not square (default to size along x axis)
                    settings.checkGridCellDimensions(self.inLandCoverGrid, self.logFile)
                    # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
                    self.outIdField = settings.getIdOutField(self.inReportingUnitFeature, self.reportingUnitIdField)
                
                    # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
                    self.zoneAreaDict = None
                    if globalConstants.qaCheckName in self.optionalGroupsList:
                        # Check to see if an outputGeorgraphicCoordinate system is set in the environments. If one is not specified
                        # return the spatial reference for the land cover grid. Use the returned spatial reference to calculate the
                        # area of the reporting unit's polygon features to store in the zoneAreaDict
                        self.outputSpatialRef = settings.getOutputSpatialReference(self.inLandCoverGrid)
                        self.zoneAreaDict = polygons.getMultiPartIdAreaDict(self.inReportingUnitFeature, self.reportingUnitIdField, self.outputSpatialRef)

                # Update calculateMetrics to calculate Core to Edge Ratio
                def _calculateMetrics(self):
                    self.newTable = newtable
                    self.metricsFieldnameDict = metricsFieldnameDict

                    # calculate Core to Edge ratio
                    calculate.getCoreEdgeRatio(self.outIdField, self.newTable, self.tabAreaTable, self.metricsFieldnameDict,
                                                      self.zoneAreaDict, self.metricConst, m)
                    AddMsg(f"{self.timer.now()} Core/Edge Ratio calculations are complete for class: {m.upper()}", 0, self.logFile)
                
                #skip over output table statistics routine as it will be performed later
                def _summarizeOutTable(self):
                    pass
                
                def _logEnvironments(self):
                    pass


            # Create new instance of metricCalc class to contain parameters
            caemCalc = metricCalcCAEM(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                          m, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst, logFile)
    
            caemCalc.inEdgeWidth = inEdgeWidth
    
            # Run Calculation
            caemCalc.run()
            
            caemCalc.metricsBaseNameList = metricsBaseNameList

            #delete the intermediate raster if save intermediates option is not chosen 
            if caemCalc.saveIntermediates:
                pass
            else:
                directory = env.workspace
                path = os.path.join(directory, caemCalc.scratchNameToBeDeleted)
                arcpy.Delete_management(path)

        
        if logFile:
            AddMsg("Summarizing the ATtILA metric output table to log file", 0)
            # append the reporting unit id field to the list of category fields; even if it's a numeric field type
            metricConst.idFields = metricConst.idFields + [reportingUnitIdField]
            log.logWriteOutputTableInfo(outTable, logFile, metricConst)
            AddMsg("Summary complete", 0)
            
            # write the standard environment settings to the log file
            log.writeEnvironments(logFile, snapRaster, processingCellSize, extentList=[inReportingUnitFeature, inLandCoverGrid])
            # parameters are: logFile, snapRaster, processingCellSize, extentList
            # if extentList is set to None, the env.extent setting will reported.
            # Place eventList here, if the extents of the datasets have been altered and you wish to use the new extents.
            # for snapRaster and processingCellSize, if the parameter is None, no entry will
            # will be recorded in the log for that parameter
        
        
        if clipLCGrid == "true":
            arcpy.Delete_management(scratchName)

    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
            
        errors.standardErrorHandling(e, logFile)

    finally:
        setupAndRestore.standardRestore(logFile)
        
        if arcpy.glob.os.path.basename(arcpy.sys.executable) == globalConstants.arcExecutable:
            env.workspace = _tempEnvironment1
        

def runRiparianLandCoverProportions(toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                            metricsToRun, inStreamFeatures, inBufferDistance, enforceBoundary, outTable, processingCellSize, snapRaster,
                            optionalFieldGroups):
    """ Interface for script executing Riparian Land Cover Proportion Metrics """
    try:
        timer = DateTimer()
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.rlcpConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, 
                          inStreamFeatures, inBufferDistance, enforceBoundary, outTable, processingCellSize, snapRaster, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # Check to see if the inLandCoverGrid has an attribute table. If not, build one
        raster.buildRAT(inLandCoverGrid, logFile)
        
        # append the buffer distance value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inBufferDistance.split()[0]
        # append the buffer distance value to the percent buffer field
        metricConst.qaCheckFieldParameters[5][0] = "%s%s" % (metricConst.pctBufferBase, inBufferDistance.split()[0])
        metricConst.qaCheckFieldParameters[4][0] = "%s%s" % (metricConst.totaPctBase, inBufferDistance.split()[0])

        class metricCalcRLCP(metricCalc):
            """ Subclass that overrides buffering function for the RiparianLandCoverProportions calculation """
            def _replaceRUFeatures(self):
                # check for duplicate ID entries in reporting unit feature. Perform dissolve if found
                self.duplicateIds = fields.checkForDuplicateValues(self.inReportingUnitFeature, self.reportingUnitIdField)
                # Initiate our flexible cleanuplist
                if rlcpCalc.saveIntermediates:
                    rlcpCalc.cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
                else:
                    rlcpCalc.cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
                if self.duplicateIds:
                    # Get a unique name with full path for the output features - will default to current workspace:
                    self.namePrefix = self.metricConst.shortName + "_Dissolve"+self.inBufferDistance.split()[0]
                    self.dissolveName = utils.files.nameIntermediateFile([self.namePrefix,"FeatureClass"], rlcpCalc.cleanupList)
                    AddMsg(f"Duplicate ID values found in reporting unit feature. Forming multipart features. Intermediate: {basename(self.dissolveName)}", self.logFile)
                    log.logArcpy("arcpy.Dissolve_management", (self.inReportingUnitFeature, self.dissolveName, self.reportingUnitIdField,"","MULTI_PART"), logFile)
                    self.inReportingUnitFeature = arcpy.Dissolve_management(self.inReportingUnitFeature, self.dissolveName, self.reportingUnitIdField,"","MULTI_PART")
                    
                # Generate a default filename for the buffer feature class
                self.bufferName = f"{self.metricConst.shortName}_Buffer{self.inBufferDistance.replace(' ','')}_"
                
                # Generate the buffer area to use in the metric calculation
                if enforceBoundary == "true":
                    self.inReportingUnitFeature, self.cleanupList = vector.bufferFeaturesByIntersect(self.inStreamFeatures,
                                                                                     self.inReportingUnitFeature,
                                                                                     self.bufferName, self.inBufferDistance,
                                                                                     self.reportingUnitIdField,
                                                                                     self.cleanupList, self.timer, self.logFile)
                else:
                    self.inReportingUnitFeature, self.cleanupList = vector.bufferFeaturesWithoutBorders(self.inStreamFeatures,
                                                                                     self.inReportingUnitFeature,
                                                                                     self.bufferName, self.inBufferDistance,
                                                                                     self.reportingUnitIdField,
                                                                                     self.cleanupList, self.timer, self.logFile)
                
                # add the altered inReportingUnitFeature to the list of features to determine the intersection extent
                self.extentList.append(self.inReportingUnitFeature) 
        
        # Create new instance of metricCalc class to contain parameters
        rlcpCalc = metricCalcRLCP(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                       metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst, logFile)

        # Assign class attributes unique to this module.
        rlcpCalc.inStreamFeatures = inStreamFeatures
        rlcpCalc.inBufferDistance = inBufferDistance
        rlcpCalc.enforceBoundary = enforceBoundary
        rlcpCalc.extentList = [inReportingUnitFeature, inLandCoverGrid]

        rlcpCalc.cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
        
        # Before generating the replacement reporting unit feature, if QA Fields is selected, get a dictionary of the reporting unit polygon area
        # and the effective area within the reporting unit (i.e., the land area in the reporting unit if water areas are excluded). If no grid values 
        # are tagged as excluded, these values are identical. Use this dictionary to calculate 1) what percentage of the reporting unit's effective area 
        # is within the replacement reporting unit boundaries (e.g., 18% of the effective area within the reporting unit is in the riparian buffer zone), and
        # 2) the overall percentage of the reporting unit that is within the buffer area (e.g., 25% of the reporting unit is in the riparian buffer zone).
        if rlcpCalc.addQAFields:
            # First generate the dictionary with the RU ID as the key and the vector measurement of the reporting unit area as its value. 
            outputSpatialRef = settings.getOutputSpatialReference(inLandCoverGrid)
            rlcpCalc.reportingUnitAreaDict = polygons.getMultiPartIdAreaDict(inReportingUnitFeature, reportingUnitIdField, outputSpatialRef)
            
            # Now alter the dictionary's value to be a list with two values: 
            # index 0 will be the vector measure of the reporting unit polygon, and 
            # index 1 will be the raster measure of the effective area within the reporting unit.
        
            # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area total    
            lccValuesDict = rlcpCalc.lccObj.values
            # Get the grid values for the input land cover grid
            landCoverValues = raster.getRasterValues(inLandCoverGrid, logFile)
            # get the list of excluded values that are found in the input land cover raster
            excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)
            
            if len(excludedValuesList) > 0:
                AddMsg(f"{timer.now()} Excluded values found in the land cover grid. Calculating effective areas for each reporting unit.", 0, logFile)
                # Use ATtILA's TabulateAreaTable operation to return an object where a tabulate area table can be easily queried.
                if rlcpCalc.saveIntermediates:
                    # name the table so that it will be saved
                    ruTableName = metricConst.shortName + globalConstants.ruTabulateAreaTableAbbv
                else:
                    ruTableName = None
                ruAreaTable = TabulateAreaTable(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, logFile, ruTableName, rlcpCalc.lccObj)
                
                for ruAreaTableRow in ruAreaTable:
                    key = ruAreaTableRow.zoneIdValue
                    area = ruAreaTableRow.effectiveArea
                    # make the value of key a list
                    rlcpCalc.reportingUnitAreaDict[key] = [rlcpCalc.reportingUnitAreaDict[key]]
                    rlcpCalc.reportingUnitAreaDict[key].append(area)
            
            else:
                AddMsg(f"{timer.now()} No excluded values found in the land cover grid. Reporting unit effective area equals total reporting unit area. Recording reporting unit areas...", 0, logFile)
                for aKey in rlcpCalc.reportingUnitAreaDict.keys():
                    area = rlcpCalc.reportingUnitAreaDict[aKey]
                    # make the value of key a list
                    rlcpCalc.reportingUnitAreaDict[aKey] = [rlcpCalc.reportingUnitAreaDict[aKey]]
                    rlcpCalc.reportingUnitAreaDict[aKey].append(area)                    
        

        # Run Calculation
        rlcpCalc.run()      
       
    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
        
        errors.standardErrorHandling(e, logFile)

    finally:
        if not rlcpCalc.cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in rlcpCalc.cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete", 0)
        
        setupAndRestore.standardRestore(logFile)


def runSamplePointLandCoverProportions(toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                            metricsToRun, inPointFeatures, ruLinkField='', inBufferDistance='#', enforceBoundary='', outTable='', processingCellSize='', 
                            snapRaster='', optionalFieldGroups=''):
    """ Interface for script executing Sample Point Land Cover Proportion Metrics """

    try:
        timer = DateTimer()
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.splcpConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, inPointFeatures, 
                          ruLinkField, inBufferDistance, enforceBoundary, outTable, processingCellSize, snapRaster, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # Check to see if the inLandCoverGrid has an attribute table. If not, build one
        raster.buildRAT(inLandCoverGrid, logFile)
        
        # append the buffer distance value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inBufferDistance.split()[0]
        # append the buffer distance value to the percent buffer field
        metricConst.qaCheckFieldParameters[5][0] = "%s%s" % (metricConst.pctBufferBase, inBufferDistance.split()[0])
        metricConst.qaCheckFieldParameters[4][0] = "%s%s" % (metricConst.totaPctBase, inBufferDistance.split()[0])

        class metricCalcSPLCP(metricCalc):
            """ Subclass that overrides specific functions for the SamplePointLandCoverProportions calculation """
            def _replaceRUFeatures(self):
                # check for duplicate ID entries. Perform dissolve if found
                self.duplicateIds = fields.checkForDuplicateValues(self.inReportingUnitFeature, self.reportingUnitIdField)
                
                # Initiate our flexible cleanuplist
                if splcpCalc.saveIntermediates:
                    splcpCalc.cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
                else:
                    splcpCalc.cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
                
                if self.duplicateIds:
                    # Get a unique name with full path for the output features - will default to current workspace:
                    self.namePrefix = f"{self.metricConst.shortName}_Dissolve{self.inBufferDistance.split()[0]}_"
                    self.dissolveName = utils.files.nameIntermediateFile([self.namePrefix,"FeatureClass"], splcpCalc.cleanupList)
                    AddMsg(f"{timer.now()} Duplicate ID values found in reporting unit feature. Forming multipart features: {basename(self.dissolveName)}", 0, self.logFile)
                    log.logArcpy("arcpy.Dissolve_management", (self.inReportingUnitFeature, self.dissolveName, self.reportingUnitIdField,"","MULTI_PART"), logFile)
                    self.inReportingUnitFeature = arcpy.Dissolve_management(self.inReportingUnitFeature, self.dissolveName, self.reportingUnitIdField,"","MULTI_PART")
                    
                # Generate a default filename for the buffer feature class
                self.bufferName = f"{self.metricConst.shortName}_Buffer{self.inBufferDistance.replace(' ','')}_"
                
                # Buffer the points and use the output as the new reporting units
                if enforceBoundary == "true":
                    self.inReportingUnitFeature = vector.bufferFeaturesByID(self.inPointFeatures,
                                                                                  self.inReportingUnitFeature,
                                                                                  self.bufferName,self.inBufferDistance,
                                                                                  self.reportingUnitIdField,self.ruLinkField,
                                                                                  self.timer, self.logFile)
                    # Since we are replacing the reporting unit features with the buffered features we also need to replace
                    # the unique identifier field - which is now the ruLinkField.
                    self.reportingUnitIdField = self.ruLinkField
                else:
                    self.inReportingUnitFeature, self.cleanupList = vector.bufferFeaturesWithoutBorders(self.inPointFeatures,
                                                                                     self.inReportingUnitFeature,
                                                                                     self.bufferName, self.inBufferDistance,
                                                                                     self.reportingUnitIdField,
                                                                                     self.cleanupList, self.timer, self.logFile)

                # add the altered inReportingUnitFeature to the list of features to determine the intersection extent
                self.extentList.append(self.inReportingUnitFeature)
        
        # Create new instance of metricCalc class to contain parameters
        splcpCalc = metricCalcSPLCP(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                       metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst, logFile)

        # Assign class attributes unique to this module.
        splcpCalc.inPointFeatures = inPointFeatures
        splcpCalc.inBufferDistance = inBufferDistance
        splcpCalc.ruLinkField = ruLinkField
        splcpCalc.enforceBoundary = enforceBoundary
        splcpCalc.cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
        splcpCalc.extentList = [inReportingUnitFeature, inLandCoverGrid]
        
        # Before generating the replacement reporting unit feature, if QA Fields is selected, get a dictionary of the reporting unit polygon area
        # and the effective area within the reporting unit (i.e., the land area in the reporting unit if water areas are excluded). If no grid values 
        # are tagged as excluded, these values are identical. Use this dictionary to calculate 1) what percentage of the reporting unit's effective area 
        # is within the replacement reporting unit boundaries (e.g., 18% of the effective area within the reporting unit is in the riparian buffer zone), and
        # 2) the overall percentage of the reporting unit that is within the buffer area (e.g., 25% of the reporting unit is in the riparian buffer zone).
        if splcpCalc.addQAFields:
            # First generate the dictionary with the RU ID as the key and the vector measurement of the reporting unit area as its value. 
            outputSpatialRef = settings.getOutputSpatialReference(inLandCoverGrid)
            splcpCalc.reportingUnitAreaDict = polygons.getMultiPartIdAreaDict(inReportingUnitFeature, reportingUnitIdField, outputSpatialRef)
            
            # Now alter the dictionary's value to be a list with two values: 
            # index 0 will be the vector measure of the reporting unit polygon, and 
            # index 1 will be the raster measure of the effective area within the reporting unit.
        
            # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area total    
            lccValuesDict = splcpCalc.lccObj.values
            # Get the grid values for the input land cover grid
            landCoverValues = raster.getRasterValues(inLandCoverGrid, logFile)
            # get the list of excluded values that are found in the input land cover raster
            excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)
            
            if len(excludedValuesList) > 0:
                AddMsg(f"{timer.now()} Excluded values found in the land cover grid. Calculating effective areas for each reporting unit.", 0, logFile)
                # Use ATtILA's TabulateAreaTable operation to return an object where a tabulate area table can be easily queried.
                if splcpCalc.saveIntermediates:
                    # name the table so that it will be saved
                    ruTableName = metricConst.shortName + globalConstants.ruTabulateAreaTableAbbv
                else:
                    ruTableName = None
                ruAreaTable = TabulateAreaTable(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, logFile, ruTableName, splcpCalc.lccObj)
                
                for ruAreaTableRow in ruAreaTable:
                    key = ruAreaTableRow.zoneIdValue
                    area = ruAreaTableRow.effectiveArea
                    # make the value of key a list
                    splcpCalc.reportingUnitAreaDict[key] = [splcpCalc.reportingUnitAreaDict[key]]
                    splcpCalc.reportingUnitAreaDict[key].append(area)
            
            else:
                AddMsg(f"{timer.now()} No excluded values found in the land cover grid. Reporting unit effective area equals total reporting unit area. Recording reporting unit areas.", 0, logFile)
                for aKey in splcpCalc.reportingUnitAreaDict.keys():
                    area = splcpCalc.reportingUnitAreaDict[aKey]
                    # make the value of key a list
                    splcpCalc.reportingUnitAreaDict[aKey] = [splcpCalc.reportingUnitAreaDict[aKey]]
                    splcpCalc.reportingUnitAreaDict[aKey].append(area)                    
        

        # Run Calculation
        splcpCalc.run()

        # Clean up intermediates.  
        if not splcpCalc.saveIntermediates:
            # note, this is actually deleting the buffers, not the source reporting units.
            arcpy.Delete_management(splcpCalc.inReportingUnitFeature)
            
            if splcpCalc.duplicateIds:
                arcpy.Delete_management(splcpCalc.dissolveName)

    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
        
        errors.standardErrorHandling(e, logFile)

    finally:
        if not splcpCalc.cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in splcpCalc.cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete", 0)
        
        setupAndRestore.standardRestore(logFile)


def runLandCoverCoefficientCalculator(toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName,
                                      lccFilePath, metricsToRun, outTable, processingCellSize, snapRaster,
                                      optionalFieldGroups):
    """Interface for script executing Land Cover Coefficient Calculator"""

    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcccConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                          metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # Check to see if the inLandCoverGrid has an attribute table. If not, build one
        raster.buildRAT(inLandCoverGrid, logFile)
        
        # Create new LCC metric calculation subclass
        class metricCalcLCC(metricCalc):
            # Subclass that overrides specific functions for the land Cover Coefficient calculation
            def _makeAttilaOutTable(self):
                # Construct the ATtILA metric output table
                self.newTable, self.metricsFieldnameDict = table.tableWriterByCoefficient(self.outTable,
                                                                                                self.metricsBaseNameList,
                                                                                                self.optionalGroupsList,
                                                                                                self.metricConst, self.lccObj,
                                                                                                self.outIdField, self.logFile)
            def _calculateMetrics(self):
                # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
                calculate.landCoverCoefficientCalculator(self.lccObj.values, self.metricsBaseNameList,
                                                               self.optionalGroupsList, self.metricConst, self.outIdField,
                                                               self.newTable, self.tabAreaTable, self.metricsFieldnameDict,
                                                               self.zoneAreaDict, self.conversionFactor)

        # Instantiate LCC metric calculation subclass
        lccCalc = metricCalcLCC(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst, logFile)

        # see what linear units are used in the tabulate area table
        outputLinearUnits = settings.getOutputLinearUnits(inLandCoverGrid)

        # using the output linear units, get the conversion factor to convert the tabulateArea area measures to hectares
        try:
            conversionFactor = conversion.getSqMeterConversionFactor(outputLinearUnits)
        except:
            raise errors.attilaException(errorConstants.linearUnitConversionError)
            #raise

        # Set the conversion factor as a class attribute
        lccCalc.conversionFactor = conversionFactor
        
        # create a list of input themes to find the intersection extent
        lccCalc.extentList = [inReportingUnitFeature, inLandCoverGrid]

        # Run calculation
        lccCalc.run()

    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
        
        errors.standardErrorHandling(e, logFile)

    finally:
        setupAndRestore.standardRestore(logFile)


def runRoadDensityCalculator(toolPath, inReportingUnitFeature, reportingUnitIdField, inRoadFeature, outTable, roadClassField="",
                             streamRoadCrossings="#", roadsNearStreams="#", inStreamFeature="#", inBufferDistance="#",
                             optionalFieldGroups="#"):
    """Interface for script executing Road Density Calculator"""
    from arcpy import env

    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        # Work on making as generic as possible
        ### Initialization
        # Start the timer
        timer = DateTimer()
        
        # Get the metric constants
        metricConst = metricConstants.rdmConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inRoadFeature, outTable, roadClassField, streamRoadCrossings, 
                          roadsNearStreams, inStreamFeature, inBufferDistance, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # create a list of input themes to find the intersection extent
        # put it here when one of the inputs might be altered (e.g., inReportingUnitFeature, inLandCoverGrid)
        # but you want the original inputs to be used for the extent intersection
        if logFile:
            extentList = [inReportingUnitFeature, inRoadFeature, inStreamFeature]
        
        # Set the output workspace
        AddMsg(f"{timer.now()} Setting up environment variables", 0, logFile)
        _tempEnvironment1 = env.workspace
        env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))
        _tempEnvironment4 = env.outputMFlag
        _tempEnvironment5 = env.outputZFlag
        # Streams and road crossings script fails in certain circumstances when M (linear referencing dimension) is enabled.
        # Disable for the duration of the tool.
        env.outputMFlag = "Disabled"
        env.outputZFlag = "Disabled"
        # Strip the description from the "additional option" and determine whether intermediates are stored.
        processed = parameters.splitItemsAndStripDescriptions(optionalFieldGroups, globalConstants.descriptionDelim)
        if globalConstants.intermediateName in processed:
            msg = "Intermediates are stored in this directory: {0}\n"
            AddMsg(msg.format(env.workspace), 0, logFile)
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
        
        # Until the Pairwise geoprocessing tools can be incorporated into ATtILA, disable the Parallel Processing Factor if the environment is set
        _tempEnvironment6 = env.parallelProcessingFactor
        currentFactor = str(env.parallelProcessingFactor)
        if currentFactor == 'None' or currentFactor == '0':
            pass
        else:
            # Advise the user that results when using parallel processing may be different from results obtained without its use.
            AddMsg("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.", 1, logFile)
            env.parallelProcessingFactor = None
        
        # Create a copy of the reporting unit feature class that we can add new fields to for calculations.  This 
        # is more appropriate than altering the user's input data. A dissolve will handle the condition of non-unique id
        # values and will also keep only the OID, shape, and reportingUnitIdField fields
        desc = arcpy.Describe(inReportingUnitFeature)
        tempName = f"{metricConst.shortName}_{desc.baseName}_"
        tempReportingUnitFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        AddMsg(f"{timer.now()} Creating temporary copy of {desc.name}. Intermediate: {basename(tempReportingUnitFeature)}", 0, logFile)
        log.logArcpy("arcpy.Dissolve_management",(inReportingUnitFeature, basename(tempReportingUnitFeature), reportingUnitIdField,"","MULTI_PART"),logFile)
        inReportingUnitFeature = arcpy.Dissolve_management(inReportingUnitFeature, basename(tempReportingUnitFeature), reportingUnitIdField,"","MULTI_PART")

        # Get the field properties for the unitID, this will be frequently used
        # If the field is numeric, it creates a text version of the field.
        uIDField = settings.processUIDField(inReportingUnitFeature,reportingUnitIdField)

        AddMsg(f"{timer.now()} Calculating reporting unit area", 0, logFile)
        # Add a field to the reporting units to hold the area value in square kilometers

        # Add and populate afield to hold the reporting unit's area (or just recalculate if it already exists
        unitArea = vector.addAreaField(inReportingUnitFeature,metricConst.areaFieldname,logFile)

        # If necessary, create a copy of the road feature class to remove M values.  The env.outputMFlag will work
        # for most datasets except for shapefiles with M and Z values. The Z value will keep the M value from being stripped
        # off. This is more appropriate than altering the user's input data.
        desc = arcpy.Describe(inRoadFeature)
        if desc.HasM or desc.HasZ:
            tempName = f"{metricConst.shortName}_{arcpy.Describe(inRoadFeature).baseName}_"
            tempLineFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Creating temporary copy of {desc.name}. Intermediate: {basename(tempLineFeature)}", 0, logFile)
            log.logArcpy("arcpy.FeatureClassToFeatureClass_conversion",(inRoadFeature, env.workspace, basename(tempLineFeature)),logFile)
            inRoadFeature = arcpy.FeatureClassToFeatureClass_conversion(inRoadFeature, env.workspace, basename(tempLineFeature))


        # Calculate the density of the roads by reporting unit.
        # Get a unique name for the merged roads and prep for cleanup
        mergedRoads = files.nameIntermediateFile(metricConst.roadsByReportingUnitName,cleanupList)
        AddMsg(f"{timer.now()} Calculating road density by reporting unit. Intermediate: {basename(mergedRoads)}", 0, logFile)
        mergedRoads, roadLengthFieldName = calculate.lineDensityCalculator(inRoadFeature,inReportingUnitFeature,
                                                                           uIDField,unitArea,mergedRoads,
                                                                           metricConst.roadDensityFieldName,
                                                                           metricConst.roadLengthFieldName,
                                                                           roadClassField,
                                                                           metricConst.totalImperviousAreaFieldName,
                                                                           logFile)

        # Build and populate final output table.
        AddMsg(f"{timer.now()} Compiling calculated values into output table", 0, logFile)
        log.logArcpy("arcpy.TableToTable_conversion",(inReportingUnitFeature,os.path.dirname(outTable),basename(outTable)), logFile)
        arcpy.TableToTable_conversion(inReportingUnitFeature,os.path.dirname(outTable),basename(outTable))
        
        # Get a list of unique road class values
        if roadClassField:
            classValues = fields.getUniqueValues(mergedRoads,roadClassField)
        else:
            classValues = []
        # Compile a list of fields that will be transferred from the merged roads feature class into the output table
        fromFields = [roadLengthFieldName, metricConst.roadDensityFieldName,metricConst.totalImperviousAreaFieldName]
        # Transfer the values to the output table, pivoting the class values into new fields if necessary.
        table.transferField(mergedRoads,outTable,fromFields,fromFields,uIDField.name,roadClassField,classValues,logFile)
        
        # If the Streams By Roads (STXRD) box is checked...
        if streamRoadCrossings and streamRoadCrossings != "false":
            # If necessary, create a copy of the stream feature class to remove M values.  The env.outputMFlag will work
            # for most datasets except for shapefiles with M and Z values. The Z value will keep the M value from being stripped
            # off. This is more appropriate than altering the user's input data.
            desc = arcpy.Describe(inStreamFeature)
            if desc.HasM or desc.HasZ:
                tempName = f"{metricConst.shortName}_{desc.baseName}_"
                tempLineFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
                AddMsg(f"{timer.now()} Creating temporary copy of {desc.name}. Intermediate: {basename(tempLineFeature)}", 0, logFile)
                log.logArcpy("arcpy.FeatureClassToFeatureClass_conversion",(inStreamFeature, env.workspace, basename(tempLineFeature)), logFile)
                inStreamFeature = arcpy.FeatureClassToFeatureClass_conversion(inStreamFeature, env.workspace, basename(tempLineFeature))

            
            AddMsg(f"{timer.now()} Calculating Stream and Road Crossings (STXRD)", 0, logFile)
            
            # Calculate the density of the streams by reporting unit.
            # Get a unique name for the merged streams:
            mergedStreams = files.nameIntermediateFile(metricConst.streamsByReportingUnitName,cleanupList)
            AddMsg(f"{timer.now()} Calculating stream density by reporting unit. Intermediate: {basename(mergedStreams)}", 0, logFile)
            mergedStreams, streamLengthFieldName = calculate.lineDensityCalculator(inStreamFeature,
                                                                                   inReportingUnitFeature,
                                                                                   uIDField,
                                                                                   unitArea,mergedStreams,
                                                                                   metricConst.streamDensityFieldName,
                                                                                   metricConst.streamLengthFieldName,
                                                                                   "","",logFile)

            # Get a unique name for the road/stream intersections:
            roadStreamMultiPoints = files.nameIntermediateFile(metricConst.roadStreamMultiPoints,cleanupList)
            # Get a unique name for the points of crossing:
            roadStreamIntersects = files.nameIntermediateFile(metricConst.roadStreamIntersects,cleanupList)
            # Get a unique name for the roads by streams summary table:
            roadStreamSummary = files.nameIntermediateFile(metricConst.roadStreamSummary,cleanupList)
            
            # Perform the roads/streams intersection and calculate the number of crossings and crossings per km
            vector.findIntersections(mergedRoads,inStreamFeature,mergedStreams,uIDField,roadStreamMultiPoints,
                                           roadStreamIntersects,roadStreamSummary,streamLengthFieldName,
                                           metricConst.xingsPerKMFieldName,timer,roadClassField,logFile)
            
            # Transfer values to final output table.
            AddMsg(f"{timer.now()} Compiling calculated values into output table", 0, logFile)
            # Compile a list of fields that will be transferred from the merged roads feature class into the output table
            fromFields = [streamLengthFieldName, metricConst.streamDensityFieldName]
            # Transfer the values to the output table, pivoting the class values into new fields if necessary.
            # Possible to add stream class values here if desired.
            table.transferField(mergedStreams,outTable,fromFields,fromFields,uIDField.name,None,None,logFile)
            # Transfer crossings fields - note the renaming of the count field.
            fromFields = ["FREQUENCY", metricConst.xingsPerKMFieldName]
            toFields = [metricConst.streamRoadXingsCountFieldname,metricConst.xingsPerKMFieldName]
            # Transfer the values to the output table, pivoting the class values into new fields if necessary.
            table.transferField(roadStreamSummary,outTable,fromFields,toFields,uIDField.name,roadClassField,classValues,logFile)
            

        if roadsNearStreams and roadsNearStreams != "false":
            AddMsg(f"{timer.now()} Calculating Roads Near Streams (RNS)", 0, logFile)
            if not streamRoadCrossings or streamRoadCrossings == "false":  # In case merged streams haven't already been calculated:
                # Create a copy of the stream feature class, if necessary, to remove M values.  The env.outputMFlag will work
                # for most datasets except for shapefiles with M and Z values. The Z value will keep the M value from being stripped
                # off. This is more appropriate than altering the user's input data.
                desc = arcpy.Describe(inStreamFeature)
                if desc.HasM or desc.HasZ:
                    tempName = f"{metricConst.shortName}_{desc.baseName}_"
                    tempLineFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
                    AddMsg(f"{timer.now()} Creating temporary copy of {desc.name}. Intermediate: {basename(tempLineFeature)}", 0, logFile)
                    log.logArcpy("arcpy.FeatureClassToFeatureClass_conversion",(inStreamFeature,env.workspace,os.path.basename(tempLineFeature)), logFile)
                    inStreamFeature = arcpy.FeatureClassToFeatureClass_conversion(inStreamFeature, env.workspace, os.path.basename(tempLineFeature))
                
                # Calculate the density of the streams by reporting unit.
                # Get a unique name for the merged streams:
                mergedStreams = files.nameIntermediateFile(metricConst.streamsByReportingUnitName,cleanupList)
                AddMsg(f"{timer.now()} Calculating stream density by reporting unit. Intermediate: {basename(mergedStreams)}", 0, logFile)
                mergedStreams, streamLengthFieldName = calculate.lineDensityCalculator(inStreamFeature,
                                                                                       inReportingUnitFeature,
                                                                                       uIDField,unitArea,mergedStreams,
                                                                                       metricConst.streamDensityFieldName,
                                                                                       metricConst.streamLengthFieldName,
                                                                                       "","",logFile)
            # Get a unique name for the buffered streams:
            streamBuffer = files.nameIntermediateFile(metricConst.streamBuffers,cleanupList)
            # Set a unique name for the undissolved  road/stream buffer intersections
            tmp1RdsNearStrms = files.nameIntermediateFile(metricConst.tmp1RNS,cleanupList)
            # Set a unique name for the undissolved  road/stream buffer intersections with reporting unit IDs attached
            tmp2RdsNearStrms = files.nameIntermediateFile(metricConst.tmp2RNS,cleanupList)
            # Get a unique name for the dissolved road/stream intersections:
            roadsNearStreams = files.nameIntermediateFile(metricConst.roadsNearStreams,cleanupList)
            
            # append the buffer distance to the rns field name base
            distString = inBufferDistance.split()[0]
            rnsFieldName = f"{metricConst.rnsFieldName}{distString}"

            vector.roadsNearStreams(inStreamFeature, mergedStreams, inBufferDistance, inRoadFeature, inReportingUnitFeature, streamLengthFieldName,uIDField, streamBuffer, 
                                          tmp1RdsNearStrms, tmp2RdsNearStrms, roadsNearStreams, rnsFieldName,metricConst.roadLengthFieldName, timer, logFile, roadClassField)
            # Transfer values to final output table.
            AddMsg(f"{timer.now()} Compiling calculated values into output table", 0, logFile)
            fromFields = [rnsFieldName]
            # Transfer the values to the output table, pivoting the class values into new fields if necessary.
            table.transferField(roadsNearStreams,outTable,fromFields,fromFields,uIDField.name,roadClassField,classValues,logFile)
        
        if logFile:
            AddMsg("Summarizing the ATtILA metric output table to log file", 0)
            # append the reporting unit id field to the list of category fields; even if it's a numeric field type
            metricConst.idFields = metricConst.idFields + [reportingUnitIdField]
            log.logWriteOutputTableInfo(outTable, logFile, metricConst)
            AddMsg("Summary complete", 0)
            
            # write to the log file some of the environment settings
            log.writeEnvironments(logFile, None, None, extentList)
    
    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
        
        errors.standardErrorHandling(e, logFile)

    finally:
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete")
        
        if logFile:
            logFile.write(f"\nEnded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            logFile.write("\n---End of Log File---\n")
            logFile.close()
            AddMsg('Log file closed')
        
        if arcpy.glob.os.path.basename(arcpy.sys.executable) == globalConstants.arcExecutable:    
            env.workspace = _tempEnvironment1
            env.outputMFlag = _tempEnvironment4
            env.outputZFlag = _tempEnvironment5
            env.parallelProcessingFactor = _tempEnvironment6


def runStreamDensityCalculator(toolPath, inReportingUnitFeature, reportingUnitIdField, inLineFeature, outTable, strmOrderField="", 
                               optionalFieldGroups="#"):
    """Interface for script executing Road Density Calculator"""
    from arcpy import env

    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        # Work on making as generic as possible
        ### Initialization
        # Start the timer
        timer = DateTimer()
        
        # Get the metric constants
        metricConst = metricConstants.sdmConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inLineFeature, outTable, strmOrderField, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # create a list of input themes to find the intersection extent
        # put it here when one of the inputs might be altered (e.g., inReportingUnitFeature, inLandCoverGrid)
        # but you want the original inputs to be used for the extent intersection
        if logFile:
            extentList = [inReportingUnitFeature, inLineFeature]
        
        # Set the output workspace
        AddMsg(f"{timer.now()} Setting up environment variables", 0, logFile)
        _tempEnvironment1 = env.workspace
        env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))
        _tempEnvironment4 = env.outputMFlag
        _tempEnvironment5 = env.outputZFlag
        # Streams and road crossings script fails in certain circumstances when M (linear referencing dimension) is enabled.
        # Disable for the duration of the tool.
        env.outputMFlag = "Disabled"
        env.outputZFlag = "Disabled"
        # Strip the description from the "additional option" and determine whether intermediates are stored.
        processed = parameters.splitItemsAndStripDescriptions(optionalFieldGroups, globalConstants.descriptionDelim)
        if globalConstants.intermediateName in processed:
            msg = "Intermediates are stored in this directory: {0}\n"
            AddMsg(msg.format(env.workspace), 0, logFile)
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
        
        # Until the Pairwise geoprocessing tools can be incorporated into ATtILA, disable the Parallel Processing Factor if the environment is set
        _tempEnvironment6 = env.parallelProcessingFactor
        currentFactor = str(env.parallelProcessingFactor)
        if currentFactor == 'None' or currentFactor == '0':
            pass
        else:
            # Advise the user that results when using parallel processing may be different from results obtained without its use.
            AddMsg("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.", 1, logFile)
            env.parallelProcessingFactor = None
        
        # Create a copy of the reporting unit feature class that we can add new fields to for calculations.  This 
        # is more appropriate than altering the user's input data. A dissolve will handle the condition of non-unique id
        # values and will also keep only the OID, shape, and reportingUnitIdField fields
        desc = arcpy.Describe(inReportingUnitFeature)
        tempName = f"{metricConst.shortName}_{desc.baseName}_" 
        tempReportingUnitFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        AddMsg(f"{timer.now()} Creating temporary copy of {desc.name}. Intermediate: {basename(tempReportingUnitFeature)}", 0, logFile)
        log.logArcpy("arcpy.Dissolve_management",(inReportingUnitFeature,os.path.basename(tempReportingUnitFeature),reportingUnitIdField,"","MULTI_PART"),logFile)
        inReportingUnitFeature = arcpy.Dissolve_management(inReportingUnitFeature, os.path.basename(tempReportingUnitFeature), reportingUnitIdField,"","MULTI_PART")

        # Get the field properties for the unitID, this will be frequently used
        uIDField = settings.processUIDField(inReportingUnitFeature,reportingUnitIdField)

        AddMsg(f"{timer.now()} Calculating reporting unit area", 0, logFile)
        # Add a field to the reporting units to hold the area value in square kilometers
        # Check for existence of field.
        fieldList = arcpy.ListFields(inReportingUnitFeature,metricConst.areaFieldname)
        # Add and populate the area field (or just recalculate if it already exists
        unitArea = vector.addAreaField(inReportingUnitFeature,metricConst.areaFieldname, logFile)
        if not fieldList: # if the list of fields that exactly match the validated fieldname is empty...
            if not cleanupList[0] == "KeepIntermediates":
                # ...add this to the list of items to clean up at the end.
                pass
                # *** this was previously necessary when the field was added to the input - now that a copy of the input
                #     is used instead, this is not necessary.
                #cleanupList.append((arcpy.DeleteField_management,(inReportingUnitFeature,unitArea)))

        # If necessary, create a copy of the stream feature class to remove M values.  The env.outputMFlag should work
        # for most datasets except for shapefiles with M and Z values, but doesn't. The Z value will keep the M value 
        # from being stripped off for several data types.
        desc = arcpy.Describe(inLineFeature)
        if desc.HasM or desc.HasZ:
            tempName = f"{metricConst.shortName}_{desc.baseName}_"
            tempLineFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Creating temporary copy of {desc.name}. Intermediate: {basename(tempLineFeature)}", 0, logFile)
            log.logArcpy("arcpy.FeatureClassToFeatureClass_conversion",(inLineFeature, env.workspace, basename(tempLineFeature)),logFile)
            inLineFeature = arcpy.FeatureClassToFeatureClass_conversion(inLineFeature, env.workspace, basename(tempLineFeature))

        # Calculate the density of the streams by reporting unit.
        # Get a unique name for the merged streams and prep for cleanup:
        mergedInLines = files.nameIntermediateFile(metricConst.linesByReportingUnitName,cleanupList)
        AddMsg(f"{timer.now()} Calculating stream density by reporting unit. Intermediate: {basename(mergedInLines)}", 0, logFile)
        mergedInLines, lineLengthFieldName = calculate.lineDensityCalculator(inLineFeature,inReportingUnitFeature,
                                                                                 uIDField,unitArea,mergedInLines,
                                                                                 metricConst.lineDensityFieldName,
                                                                                 metricConst.lineLengthFieldName,
                                                                                 strmOrderField,"",logFile)

        # Build and populate final output table.
        AddMsg(f"{timer.now()} Compiling calculated values into output table", 0, logFile)
        log.logArcpy("arcpy.TableToTable_conversion",(inReportingUnitFeature,os.path.dirname(outTable),os.path.basename(outTable)),logFile)
        arcpy.TableToTable_conversion(inReportingUnitFeature,os.path.dirname(outTable),os.path.basename(outTable))
        # Get a list of unique road class values
        if strmOrderField:
            orderValues = fields.getUniqueValues(mergedInLines,strmOrderField)
        else:
            orderValues = []
        # Compile a list of fields that will be transferred from the merged roads feature class into the output table
        fromFields = [lineLengthFieldName, metricConst.lineDensityFieldName]
        # Transfer the values to the output table, pivoting the class values into new fields if necessary.
        table.transferField(mergedInLines,outTable,fromFields,fromFields,uIDField.name,strmOrderField,orderValues,logFile)
        
        if logFile:
            AddMsg("Summarizing the ATtILA metric output table to log file", 0)
            # append the reporting unit id field to the list of category fields; even if it's a numeric field type
            metricConst.idFields = metricConst.idFields + [reportingUnitIdField]
            log.logWriteOutputTableInfo(outTable, logFile, metricConst)
            AddMsg("Summary complete", 0)
            
            # write the standard environment settings to the log file
            log.writeEnvironments(logFile, None, None, extentList)
            # parameters are: logFile, snapRaster, processingCellSize, extentList
            # if extentList is set to None, the env.extent setting will reported.
            # Place eventList here, if the extents of the datasets have been altered and you wish to use the new extents.
            # for snapRaster and processingCellSize, if the parameter is None, no entry will
            # will be recorded in the log for that parameter
        
    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
        
        errors.standardErrorHandling(e, logFile)

    finally:
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete")
        
        if logFile:
            logFile.write(f"\nEnded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            logFile.write("\n---End of Log File---\n")
            logFile.close()
            AddMsg('Log file closed')
        
        if arcpy.glob.os.path.basename(arcpy.sys.executable) == globalConstants.arcExecutable:    
            env.workspace = _tempEnvironment1
            env.outputMFlag = _tempEnvironment4
            env.outputZFlag = _tempEnvironment5
            env.parallelProcessingFactor = _tempEnvironment6
        

def runLandCoverDiversity(toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, outTable, processingCellSize, 
                          snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover Diversity Metrics """

    try:
        class metricLCDCalc:
            """ This class contains the  steps to perform a land cover diversity calculation."""

            # Initialization
            def __init__(self, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, metricsToRun, outTable, 
                         processingCellSize, snapRaster, optionalFieldGroups, metricConst, logFile):
                self.timer = DateTimer()
                self.logFile = logFile
                AddMsg(f"{self.timer.now()} Setting up environment variables", 0, logFile)
                
                # Run the setup
                self.metricsBaseNameList, self.optionalGroupsList = setupAndRestore.standardSetup(snapRaster, 
                                                                                                  processingCellSize, 
                                                                                                  os.path.dirname(outTable), 
                                                                                                  [metricsToRun,optionalFieldGroups])
                
                # Save other input parameters as class attributes
                self.outTable = outTable
                self.inReportingUnitFeature = inReportingUnitFeature
                self.reportingUnitIdField = reportingUnitIdField
                self.metricConst = metricConst
                self.inLandCoverGrid = inLandCoverGrid
                self.snapRaster = snapRaster
                self.processingCellSize = processingCellSize
                self.extentList = [inReportingUnitFeature, inLandCoverGrid]

                # If the user has checked the Intermediates option, name the tabulateArea table. This will cause it to be saved.
                self.tableName = None
                self.saveIntermediates = globalConstants.intermediateName in self.optionalGroupsList
                if self.saveIntermediates:
                    self.tableName = metricConst.shortName + globalConstants.tabulateAreaTableAbbv
                                    
            def _logEnvironments(self):
                if self.logFile:
                    # write environment settings
                    log.writeEnvironments(self.logFile, self.snapRaster, self.processingCellSize, self.extentList)
                    
            def _housekeeping(self):
                # alert user if the land cover grid cells are not square (default to size along x axis)
                settings.checkGridCellDimensions(self.inLandCoverGrid, self.logFile)
                # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
                self.outIdField = settings.getIdOutField(self.inReportingUnitFeature, self.reportingUnitIdField)
                # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
                self.zoneAreaDict = None
                if globalConstants.qaCheckName in self.optionalGroupsList:
                    # Check to see if an outputGeorgraphicCoordinate system is set in the environments. If one is not specified
                    # return the spatial reference for the land cover grid. Use the returned spatial reference to calculate the
                    # area of the reporting unit's polygon features to store in the zoneAreaDict
                    self.outputSpatialRef = settings.getOutputSpatialReference(self.inLandCoverGrid)
                    self.zoneAreaDict = polygons.getMultiPartIdAreaDict(self.inReportingUnitFeature, self.reportingUnitIdField, self.outputSpatialRef)
                    
            def _makeAttilaOutTable(self):
                #AddMsg(self.timer.now() + " Constructing the ATtILA metric output table: "+self.outTable, 0, self.logFile)
                AddMsg(f"{self.timer.now()} Constructing the ATtILA metric output table: {os.path.basename(self.outTable)}", 0, self.logFile)
                # Internal function to construct the ATtILA metric output table
                self.newTable, self.metricsFieldnameDict = table.tableWriterNoLcc(self.outTable,
                                                                                        self.metricsBaseNameList,
                                                                                        self.optionalGroupsList,
                                                                                        self.metricConst,
                                                                                        self.outIdField,
                                                                                        self.logFile)
                
            def _makeTabAreaTable(self):
                AddMsg(f"{self.timer.now()} Generating a zonal tabulate area table", 0, self.logFile)
                # Internal function to generate a zonal tabulate area table
                self.tabAreaTable = TabulateAreaTable(self.inReportingUnitFeature, self.reportingUnitIdField,
                                                      self.inLandCoverGrid, self.logFile, self.tableName)
                
            def _calculateMetrics(self):
                AddMsg(f"{self.timer.now()} Processing the tabulate area table and computing metric values", 0, self.logFile)
                # Internal function to process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
                calculate.landCoverDiversity(self.metricConst, self.outIdField, self.newTable, self.tabAreaTable, self.zoneAreaDict)
                
            def _summarizeOutTable(self):
                if self.logFile:
                    AddMsg("Summarizing the ATtILA metric output table to log file", 0)
                    # Internal function to analyze the output table fields for the log file. This may be overridden by some metrics
                    # append the reporting unit id field to the list of category fields; even if it's a numeric field type
                    self.metricConst.idFields = self.metricConst.idFields + [self.reportingUnitIdField]
                    log.logWriteOutputTableInfo(self.newTable, self.logFile, self.metricConst)
                    AddMsg("Summary complete", 0)
                    
            # Function to run all the steps in the calculation process
            def run(self):
            
                # Perform additional housekeeping
                self._housekeeping()
                
                # Make Output Tables
                self._makeAttilaOutTable()
                
                # Generate Tabulation tables
                self._makeTabAreaTable()
                
                # Run final metric calculation
                self._calculateMetrics()
                
                # Summarize the ATtILA metric output table to log file
                self._summarizeOutTable()
                
                # Write Environment settings to the log file
                self._logEnvironments()
                

        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcdConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, outTable, processingCellSize, 
                          snapRaster, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # Check to see if the inLandCoverGrid has an attribute table. If not, build one
        raster.buildRAT(inLandCoverGrid, logFile)
        
        metricsToRun = metricConst.fixedMetricsToRun
        
        lcdCalc = metricLCDCalc(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, metricsToRun, outTable, 
                                processingCellSize, snapRaster, optionalFieldGroups, metricConst, logFile)
        lcdCalc.run()

    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
            
        errors.standardErrorHandling(e, logFile)

    finally:
        setupAndRestore.standardRestore(logFile)


def runPopulationDensityCalculator(toolPath, inReportingUnitFeature, reportingUnitIdField, inCensusFeature, inPopField, outTable,
                                   popChangeYN, inCensusFeature2, inPopField2, optionalFieldGroups):
    """ Interface for script executing Population Density Metrics """
    from arcpy import env

    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        ### Initialization
        # Start the timer
        timer = DateTimer()

        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.pdmConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inCensusFeature, inPopField, outTable,
                          popChangeYN, inCensusFeature2, inPopField2, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)

        # create a list of input themes to find the intersection extent
        # put it here when one of the inputs might be altered (e.g., inReportingUnitFeature, inLandCoverGrid)
        # but you want the original inputs to be used for the extent intersection
        if logFile:
            extentList = [inReportingUnitFeature, inCensusFeature, inCensusFeature2]
        
        # Set the output workspace
        AddMsg(f"{timer.now()} Setting up environment variables", 0, logFile)
        _tempEnvironment1 = env.workspace
        env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))
        # Strip the description from the "additional option" and determine whether intermediates are stored.
        processed = parameters.splitItemsAndStripDescriptions(optionalFieldGroups, globalConstants.descriptionDelim)
        if globalConstants.intermediateName in processed:
            msg = "Intermediates are stored in this directory: {0}\n"
            AddMsg(msg.format(env.workspace), 0, logFile)
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
        
        # Until the Pairwise geoprocessing tools can be incorporated into ATtILA, disable the Parallel Processing Factor if the environment is set
        _tempEnvironment6 = env.parallelProcessingFactor
        currentFactor = str(env.parallelProcessingFactor)
        if currentFactor == 'None' or currentFactor == '0':
            pass
        else:
            # Advise the user that results when using parallel processing may be different from results obtained without its use.
            AddMsg("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.", 1, logFile)
            env.parallelProcessingFactor = None
        
        # Create a copy of the reporting unit feature class that we can add new fields to for calculations.  This 
        # is more appropriate than altering the user's input data. A dissolve will handle the condition of non-unique id
        # values and will also keep only the OID, shape, and reportingUnitIdField fields
        desc = arcpy.Describe(inReportingUnitFeature)
        tempName = f"{metricConst.shortName}_{desc.baseName}_"
        tempReportingUnitFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        AddMsg(f"{timer.now()} Creating temporary copy of {desc.name}. Intermediate: {basename(tempReportingUnitFeature)}", 0, logFile)
        log.logArcpy("arcpy.Dissolve_management",(inReportingUnitFeature, basename(tempReportingUnitFeature), reportingUnitIdField,"","MULTI_PART"),logFile)
        inReportingUnitFeature = arcpy.Dissolve_management(inReportingUnitFeature, basename(tempReportingUnitFeature), reportingUnitIdField,"","MULTI_PART")

        # Add and populate the area field (or just recalculate if it already exists
        ruAreaFld = metricConst.areaFieldname
        log.logArcpy("arcpy.management.CalculateGeometryAttributes",(inReportingUnitFeature, [[ruAreaFld, "AREA"]],"", "SQUARE_KILOMETERS"), logFile)
        arcpy.management.CalculateGeometryAttributes(inReportingUnitFeature, [[ruAreaFld, "AREA"]],"", "SQUARE_KILOMETERS")
        
        # Build the final output table.
        AddMsg(f"{timer.now()} Creating output table: {basename(outTable)}", 0, logFile)
        log.logArcpy("arcpy.conversion.ExportTable",(inReportingUnitFeature,outTable),logFile)
        arcpy.conversion.ExportTable(inReportingUnitFeature,outTable)
        
        AddMsg(f"{timer.now()} Calculating population density", 0, logFile)
        # Create an index value to keep track of intermediate outputs and fieldnames.
        index = ""
        #if popChangeYN is checked:
        if popChangeYN == "true":
            index = "1"
        # Perform population density calculation for first (only?) population feature class
        calculate.getWeightedPopDensity(inReportingUnitFeature,reportingUnitIdField,ruAreaFld,inCensusFeature,inPopField,
                                        outTable,metricConst,cleanupList,index,timer,logFile)

        #if popChangeYN is checked:
        if popChangeYN == "true":
            index = "2"
            AddMsg(f"{timer.now()} Calculating population density for second feature class", 0, logFile)
            # Perform population density calculation for second population feature class
            calculate.getWeightedPopDensity(inReportingUnitFeature,reportingUnitIdField,ruAreaFld,inCensusFeature2,inPopField2,
                                            outTable,metricConst,cleanupList,index,timer,logFile)
            
            AddMsg(f"{timer.now()} Calculating population change", 0, logFile)
            # Set up a calculation expression for population change
            calcExpression = "getPopChange(!popCnt_T1!,!popCnt_T2!)"
            codeBlock = """def getPopChange(pop1,pop2):
    if pop1 == 0:
        if pop2 == 0:
            return 0
        else:
            return 1
    else:
        return ((pop2-pop1)/pop1)*100"""
            
            # Calculate the population density
            vector.addCalculateField(outTable,metricConst.populationChangeFieldName,"DOUBLE",calcExpression,codeBlock,logFile)       

        AddMsg(f"{timer.now()} Calculation complete", 0, logFile)
        
        if logFile:
            AddMsg("Summarizing the ATtILA metric output table to log file", 0)
            # append the reporting unit id field to the list of category fields; even if it's a numeric field type
            metricConst.idFields = metricConst.idFields + [reportingUnitIdField]
            log.logWriteOutputTableInfo(outTable, logFile, metricConst)
            AddMsg("Summary complete", 0)
            
            # write the standard environment settings to the log file
            log.writeEnvironments(logFile, None, None, extentList)   
            # parameters are: logFile, snapRaster, processingCellSize, extentList
            # Place eventList here, if the extents of the datasets have been altered and you wish to use the new extents.
            # if extentList is set to None, the env.extent setting will reported.
            # for snapRaster and processingCellSize, if the parameter is None, no entry will
            # will be recorded in the log for that parameter
    
    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
            
        errors.standardErrorHandling(e, logFile)

    finally:
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete")
        
        if logFile:
            logFile.write(f"\nEnded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            logFile.write("\n---End of Log File---\n")
            logFile.close()
            AddMsg('Log file closed')
        
        if arcpy.glob.os.path.basename(arcpy.sys.executable) == globalConstants.arcExecutable:    
            env.workspace = _tempEnvironment1
            env.parallelProcessingFactor = _tempEnvironment6
        

def runPopulationInFloodplainMetrics(toolPath, inReportingUnitFeature, reportingUnitIdField, inCensusDataset, inPopField, inFloodplainDataset, 
                                     outTable, optionalFieldGroups):
    """ Interface for script executing Population In Floodplain Metrics """
    from arcpy import env

    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        ### Initialization
        # Start the timer
        timer = DateTimer()
        
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.pifmConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inCensusDataset, inPopField, inFloodplainDataset, outTable, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # create a list of input themes to find the intersection extent. 
        # put it here when one of the inputs might be altered (e.g., inReportingUnitFeature, inLandCoverGrid)
        # but you want the original inputs to be used for the extent intersection
        if logFile:
            extentList = [inReportingUnitFeature, inCensusDataset, inFloodplainDataset]
        
        AddMsg(f"{timer.now()} Setting up environment variables", 0, logFile)
        _tempEnvironment0 = env.snapRaster
        _tempEnvironment1 = env.workspace
        _tempEnvironment2 = env.cellSize
        _tempEnvironment6 = env.parallelProcessingFactor
        
        # Until the Pairwise geoprocessing tools can be incorporated into ATtILA, disable the Parallel Processing Factor if the environment is set
        currentFactor = str(env.parallelProcessingFactor)
        if currentFactor == 'None' or currentFactor == '0':
            pass
        else:
            # Advise the user that results when using parallel processing may be different from results obtained without its use.
            AddMsg("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.", 1, logFile)
            env.parallelProcessingFactor = None
        
        # set the workspace for ATtILA intermediary files
        env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))
            
        # Strip the description from the "additional option" and determine whether intermediates are stored.
        processed = parameters.splitItemsAndStripDescriptions(optionalFieldGroups, globalConstants.descriptionDelim)
        if globalConstants.intermediateName in processed:
            msg = "Intermediates are stored in this directory: {0}\n"
            AddMsg(msg.format(env.workspace), 0, logFile)

            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
        
        popCntFields = metricConst.populationCountFieldNames
            
        # Do a Describe on the population and floodplain inputs. Determine if they are raster or polygon
        descCensus = arcpy.Describe(inCensusDataset)
        descFldpln = arcpy.Describe(inFloodplainDataset)   
        
        # Check if a population field is selected if the inCensusDataset is a polygon feature
        descCensus = arcpy.Describe(inCensusDataset)
        if descCensus.datasetType != "RasterDataset" and inPopField == '':
            raise errors.attilaException(errorConstants.missingFieldError) 

        # Create an index value to keep track of intermediate outputs and field names.
        index = 0
        
        # Generate name for reporting unit population count table.
        suffix = metricConst.fieldSuffix[index]
        popTable_RU = files.nameIntermediateFile([f"{metricConst.popCntTableName}{suffix}_",'Dataset'],cleanupList)

        ### Metric Calculation        
         
        # tool gui does not have a snapRaster parameter. When the census dataset is a raster, the snapRaster will
        # be set to the census raster. To record this correctly in the log file, set up the snapRaster variable.
        snapRaster = None
        processingCellSize = None
        
        if descCensus.datasetType == "RasterDataset":
            # set the raster environments so the raster operations align with the census grid cell boundaries
            env.snapRaster = inCensusDataset
            env.cellSize = descCensus.meanCellWidth
            
            # setting variables so they can be reported in the log file
            snapRaster = inCensusDataset
            processingCellSize = str(descCensus.meanCellWidth)
            
            # calculate the population for the reporting unit using zonal statistics as table
            AddMsg(f"{timer.now()} Calculating population within each reporting unit. Intermediate: {basename(popTable_RU)}", 0, logFile)
            log.logArcpy("arcpy.sa.ZonalStatisticsAsTable",(inReportingUnitFeature,reportingUnitIdField,inCensusDataset,popTable_RU,"DATA","SUM"), logFile)
            arcpy.sa.ZonalStatisticsAsTable(inReportingUnitFeature, reportingUnitIdField, inCensusDataset, popTable_RU, "DATA", "SUM")
            
            # Rename the population count field.
            outPopField = metricConst.populationCountFieldNames[index]
            log.logArcpy("arcpy.AlterField_management", (popTable_RU, "SUM", outPopField, outPopField), logFile)
            arcpy.AlterField_management(popTable_RU, "SUM", outPopField, outPopField)
            
            # Set variables for the floodplain population calculations
            index = 1
            suffix = metricConst.fieldSuffix[index]
            popTable_FP = files.nameIntermediateFile([f"{metricConst.popCntTableName}{suffix}_",'Dataset'],cleanupList)
            
            if descFldpln.datasetType == "RasterDataset":
                # Use SetNull to eliminate non-floodplain areas and to replace the floodplain cells with values from the 
                # PopulationRaster. The snap raster, and cell size have already been set to match the census raster
                AddMsg(f"{timer.now()} Setting floodplain areas to population values.", 0, logFile)
                delimitedVALUE = arcpy.AddFieldDelimiters(inFloodplainDataset,"VALUE")
                whereClause = delimitedVALUE+" = 0"
                log.logArcpy("arcpy.sa.SetNull",(inFloodplainDataset, inCensusDataset, whereClause),logFile)
                inCensusDataset = arcpy.sa.SetNull(inFloodplainDataset, inCensusDataset, whereClause)
                
                if globalConstants.intermediateName in processed:
                    namePrefix = metricConst.floodplainPopName
                    scratchName = arcpy.CreateScratchName(namePrefix, "", "RasterDataset")
                    inCensusDataset.save(scratchName)
                    AddMsg(f"{timer.now()} Save intermediate grid complete: {basename(scratchName)}", 0, logFile)
                    
                 
            else: # floodplain feature is a polygon
                # Assign the reporting unit ID to intersecting floodplain polygon segments using Identity
                fileNameBase = descFldpln.baseName
                tempName = f"{metricConst.shortName}_{fileNameBase}_Identity_"
                tempPolygonFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
                AddMsg(f"{timer.now()} Assigning reporting unit IDs to intersecting floodplain features. Intermediate: {basename(tempPolygonFeature)}", 0, logFile)
                log.logArcpy("arcpy.Identity_analysis", (inFloodplainDataset, inReportingUnitFeature, tempPolygonFeature), logFile)
                arcpy.Identity_analysis(inFloodplainDataset, inReportingUnitFeature, tempPolygonFeature)
                inReportingUnitFeature = tempPolygonFeature
            
            AddMsg(f"{timer.now()} Calculating population within floodplain areas for each reporting unit. Intermediate: {basename(popTable_FP)}", 0, logFile)
            # calculate the population for the reporting unit using zonal statistics as table
            # The snap raster, and cell size have been set to match the census raster
            log.logArcpy("arcpy.sa.ZonalStatisticsAsTable",(inReportingUnitFeature,reportingUnitIdField,inCensusDataset,popTable_FP,"DATA","SUM"), logFile)
            arcpy.sa.ZonalStatisticsAsTable(inReportingUnitFeature, reportingUnitIdField, inCensusDataset, popTable_FP, "DATA", "SUM")
            
            # Rename the population count field.
            outPopField = metricConst.populationCountFieldNames[index]
            log.logArcpy("arcpy.AlterField_management",(popTable_FP, "SUM", outPopField, outPopField),logFile)
            arcpy.AlterField_management(popTable_FP, "SUM", outPopField, outPopField)

        else: # census features are polygons
            
            # Create a copy of the census feature class that we can add new fields to for calculations.
            fieldMappings = arcpy.FieldMappings()
            fieldMappings.addTable(inCensusDataset)
            [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name != inPopField]
        
            tempName = f"{metricConst.shortName}_{descCensus.baseName}_Work_"
            tempCensusFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Creating a working copy of {basename(inCensusDataset)}. Intermediate: {basename(tempCensusFeature)}", 0, logFile)
            log.logArcpy("arcpy.FeatureClassToFeatureClass_conversion",(inCensusDataset,env.workspace,basename(tempCensusFeature),"",fieldMappings),logFile)
            inCensusDataset = arcpy.FeatureClassToFeatureClass_conversion(inCensusDataset,env.workspace,basename(tempCensusFeature),"",fieldMappings)
            
            # Add a dummy field to the copied census feature class and calculate it to a value of 1.
            classField = "tmpClass"
            log.logArcpy("arcpy.AddField_management",(inCensusDataset,classField,"SHORT"),logFile)
            arcpy.AddField_management(inCensusDataset,classField,"SHORT")
            
            log.logArcpy("arcpy.CalculateField_management",(inCensusDataset,classField,1),logFile)
            arcpy.CalculateField_management(inCensusDataset,classField,1)
            
            # Perform population count calculation for the reporting unit
            AddMsg(f"{timer.now()} Calculating population within reporting units. Intermediate: {basename(popTable_RU)}", 0, logFile)
            calculate.getPolygonPopCount(inReportingUnitFeature,reportingUnitIdField,inCensusDataset,inPopField,
                                      classField,popTable_RU,metricConst,index,logFile)
        
            # Set variables for the floodplain population calculations   
            index = 1
            suffix = metricConst.fieldSuffix[index]
            popTable_FP = files.nameIntermediateFile([f"{metricConst.popCntTableName}{suffix}_",'Dataset'],cleanupList)
            
            if descFldpln.datasetType == "RasterDataset":
                # Convert the Raster floodplain to Polygon
                delimitedVALUE = arcpy.AddFieldDelimiters(inFloodplainDataset,"VALUE")
                whereClause = f"{delimitedVALUE} = 0"
                log.logArcpy("arcpy.sa.SetNull",(inFloodplainDataset, 1, whereClause),logFile)
                nullGrid = arcpy.sa.SetNull(inFloodplainDataset, 1, whereClause)
                
                tempName = f"{metricConst.shortName}_{descFldpln.baseName}_Poly_"
                tempPolygonFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
                AddMsg(f"{timer.now()} Converting floodplain raster to a polygon feature. Intermediate: {basename(tempPolygonFeature)}", 0, logFile)
                
                # This may fail if a polgyon created is too large. Need a routine to more elegantly reduce the maxVertices in any one polygon
                maxVertices = 250000
                try:
                    log.logArcpy("arcpy.RasterToPolygon_conversion",(nullGrid,tempPolygonFeature,"NO_SIMPLIFY","VALUE","",maxVertices),logFile)
                    inFloodplainDataset = arcpy.RasterToPolygon_conversion(nullGrid,tempPolygonFeature,"NO_SIMPLIFY","VALUE","",maxVertices)
                except:
                    AddMsg(f"{timer.now()} Converting raster to polygon with maximum vertices technique", 0, logFile)
                    maxVertices = maxVertices / 2
                    log.logArcpy("arcpy.RasterToPolygon_conversion",(nullGrid,tempPolygonFeature,"NO_SIMPLIFY","VALUE","",maxVertices), logFile)
                    inFloodplainDataset = arcpy.RasterToPolygon_conversion(nullGrid,tempPolygonFeature,"NO_SIMPLIFY","VALUE","",maxVertices)
                
            else: # floodplain input is a polygon dataset
                # Create a copy of the floodplain feature class that we can add new fields to for calculations.
                # To reduce operation overhead and disk space, keep only the first field of the floodplain feature
                fieldMappings = arcpy.FieldMappings()
                fieldMappings.addTable(inFloodplainDataset)
                [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name != fieldMappings.fields[0].name]
                
                tempName = f"{metricConst.shortName}_{descFldpln.baseName}_Work_"
                tempFldplnFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
                AddMsg(f"{timer.now()} Creating a working copy of {basename(inFloodplainDataset)}. Intermediate: {basename(tempFldplnFeature)}", 0, logFile)
                log.logArcpy("arcpy.FeatureClassToFeatureClass_conversion",(inFloodplainDataset,env.workspace,basename(tempFldplnFeature),"",fieldMappings),logFile)
                inFloodplainDataset = arcpy.FeatureClassToFeatureClass_conversion(inFloodplainDataset,env.workspace, basename(tempFldplnFeature),"", fieldMappings)
                
            # Add a field and calculate it to a value of 1. This field will use as the classField in Tabulate Intersection operation below
            classField = "tmpClass"
            log.logArcpy("arcpy.AddField_management",(inFloodplainDataset,classField,"SHORT"),logFile)
            arcpy.AddField_management(inFloodplainDataset,classField,"SHORT")
            
            log.logArcpy("arcpy.CalculateField_management",(inFloodplainDataset,classField,1),logFile)
            arcpy.CalculateField_management(inFloodplainDataset,classField,1)

            # intersect the floodplain polygons with the reporting unit polygons
            fileNameBase = descFldpln.baseName
            # need to eliminate the tool's shortName from the fileNameBase if the floodplain polygon was derived from a raster
            fileNameBase = fileNameBase.replace(metricConst.shortName+"_","")
            tempName = f"{metricConst.shortName}_{fileNameBase}_Identity_"
            tempPolygonFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Assigning reporting unit IDs to floodplain features. Intermediate: {basename(tempPolygonFeature)}", 0, logFile)
            log.logArcpy("arcpy.Identity_analysis",(inFloodplainDataset, inReportingUnitFeature, tempPolygonFeature),logFile)
            arcpy.Identity_analysis(inFloodplainDataset, inReportingUnitFeature, tempPolygonFeature)
    
            AddMsg(f"{timer.now()} Calculating population within floodplain areas for each reporting unit. Intermediate: {basename(popTable_FP)}", 0, logFile)
            # Perform population count calculation for second feature class area
            calculate.getPolygonPopCount(tempPolygonFeature,reportingUnitIdField,inCensusDataset,inPopField,
                                          classField,popTable_FP,metricConst,index,logFile)
        
        # Build and populate final output table.
        AddMsg(f"{timer.now()} Calculating the percent of the population that is within a floodplain", 0, logFile)
        
        # Construct a list of fields to retain in the output metrics table
        keepFields = metricConst.populationCountFieldNames
        keepFields.append(reportingUnitIdField)
        fieldMappings = arcpy.FieldMappings()
        fieldMappings.addTable(popTable_RU)
        [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name not in keepFields]

        log.logArcpy("arcpy.TableToTable_conversion",(popTable_RU,os.path.dirname(outTable), basename(outTable), "", fieldMappings), logFile)
        arcpy.TableToTable_conversion(popTable_RU,os.path.dirname(outTable), basename(outTable), "", fieldMappings)
        
        # Compile a list of fields that will be transferred from the floodplain population table into the output table
        fromFields = [popCntFields[index]]
        toField = popCntFields[index]
        # Transfer the values to the output table
        table.transferField(popTable_FP,outTable,fromFields,[toField],reportingUnitIdField,None,None,logFile)
        
        # Set up a calculation expression for population change
        calcExpression = f"getPopPercent(!{popCntFields[0]}!,!{popCntFields[1]}!)"
        codeBlock = """def getPopPercent(pop1,pop2):
                            if pop1 == 0:
                                if pop2 == 0:
                                    return 0
                                else:
                                    return 1
                            else:
                                return (pop2/pop1)*100"""
            
        # Calculate the percent population within floodplain
        vector.addCalculateField(outTable,metricConst.populationProportionFieldName,"DOUBLE",calcExpression,codeBlock,logFile)   

        AddMsg(f"{timer.now()} Calculation complete", 0, logFile)
        
        if logFile:
            AddMsg("Summarizing the ATtILA metric output table to log file", 0)
            # append the reporting unit id field to the list of category fields; even if it's a numeric field type
            metricConst.idFields = metricConst.idFields + [reportingUnitIdField]
            log.logWriteOutputTableInfo(outTable, logFile, metricConst)
            AddMsg("Summary complete", 0)
            
            # write the standard environment settings to the log file
            log.writeEnvironments(logFile, snapRaster, processingCellSize, extentList)
            # parameters are: logFile, snapRaster, processingCellSize, extentList
            # if extentList is set to None, the env.extent setting will reported.
            # Place eventList here, if the extents of the datasets have been altered and you wish to use the new extents.
            # for snapRaster and processingCellSize, if the parameter is None, no entry will
            # will be recorded in the log for that parameter
            
    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
            
        errors.standardErrorHandling(e, logFile)

    finally:
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete")
        
        if logFile:
            logFile.write(f"\nEnded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            logFile.write("\n---End of Log File---\n")
            logFile.close()
            AddMsg('Log file closed')
        
        if arcpy.glob.os.path.basename(arcpy.sys.executable) == globalConstants.arcExecutable:    
            env.snapRaster = _tempEnvironment0
            env.workspace = _tempEnvironment1
            env.cellSize = _tempEnvironment2
            env.parallelProcessingFactor = _tempEnvironment6
        

def runPopulationLandCoverViews(toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                    metricsToRun, viewRadius, minPatchSize="", inCensusRaster="", outTable="", processingCellSize="", 
                    snapRaster="", optionalFieldGroups=""):
    """ Interface for script executing Population With Potential Views Metrics """
    try:
       
        ''' Initialization Steps '''
        from arcpy import env
        timer = DateTimer()
        
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.plcvConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, viewRadius, 
                          minPatchSize, inCensusRaster, outTable, processingCellSize, snapRaster, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # Check to see if the inLandCoverGrid has an attribute table. If not, build one
        raster.buildRAT(inLandCoverGrid, logFile)
        
        AddMsg(f"{timer.now()} Setting up environment variables", 0, logFile)
         
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize,
                                                                                os.path.dirname(outTable),
                                                                                [metricsToRun,optionalFieldGroups])
 
        # XML Land Cover Coding file loaded into memory
        lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        lccClassesDict = lccObj.classes
        # Get the lccObj values dictionary. This contains all the properties of each value specified in the Land Cover Classification XML    
        lccValuesDict = lccObj.values
        # create a list of all the grid values in the selected land cover grid
        landCoverValues = raster.getRasterValues(inLandCoverGrid, logFile)
        # get the frozenset of excluded values (i.e., values marked as EXCLUDED in the Land Cover Classification XML)
        excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)

        # # append the view radius distance value to the field suffix
        # newSuffix = metricConst.fieldSuffix + viewRadius
        # metricConst.fieldParameters[1] = newSuffix
        # # for the output fields, add the input view radius to the field suffix
        # for i, fldParams in enumerate(metricConst.additionalFields):
        #     fldParams[1] = metricConst.additionalSuffixes[i] + viewRadius
         
         
        ''' Housekeeping Steps ''' 
        # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
        settings.checkExcludedValuesInClass(metricsBaseNameList, lccObj, lccClassesDict, logFile)
        # alert user if the land cover grid has values undefined in the LCC XML file
        settings.checkGridValuesInLCC(inLandCoverGrid, lccObj, logFile)
        # alert user if the land cover grid cells are not square (default to size along x axis)
        settings.checkGridCellDimensions(inLandCoverGrid, logFile)
        # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
        outIdField = settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
         
        # Determine if the user wants to save the intermediate products
        saveIntermediates = globalConstants.intermediateName in optionalGroupsList

 
        # Initiate our flexible cleanuplist
        cleanupList = []
        if saveIntermediates:
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
             
 
        ''' Make ATtILA Output Table '''
        #Create the output table outside of metricCalc so that result can be added for multiple metrics
        AddMsg(f"{timer.now()} Constructing the ATtILA metric output table: {basename(outTable)}", 0, logFile)
        newtable, metricsFieldnameDict = table.tableWriterByClass(outTable, metricsBaseNameList,optionalGroupsList, 
                                                                                  metricConst, lccObj, outIdField, 
                                                                                  logFile, metricConst.additionalFields)

        # Newtable is unnecessary. It will be reconstructed later in the script via the metricsFieldnameDict. Need to
        # remove the table for now as it will cause an error if overwriting Geoprocessing outputs is not allowed.
        if arcpy.Exists(newtable):
            arcpy.Delete_management(newtable)
            
        ''' Metric Computations '''
 
        # Generate table with population counts by reporting unit
        AddMsg(f"{timer.now()} Calculating population within each reporting unit", 0, logFile) 
        index = 0

        populationTable, populationField = table.createPolygonValueCountTable(inReportingUnitFeature,
                                                                              reportingUnitIdField,
                                                                              inCensusRaster,
                                                                              "",
                                                                              newtable,
                                                                              metricConst,
                                                                              index,
                                                                              cleanupList,
                                                                              logFile)
        
        # Eliminate unnecessary fields from the population table
        fields.deleteFields(populationTable, ["ZONE_CODE", "COUNT", "AREA"])
        
        # Set up list for the viewGrid Con operation. First value is the where clause value, the second is the true constant 
        conValues = [0,1]
        
        # Determine if a transformation method is needed to project datasets (e.g. different datums are used). 
        transformMethod = conversion.getTransformMethod(inLandCoverGrid, inCensusRaster)
        descCensus = arcpy.Describe(inCensusRaster)
        spatialCensus = descCensus.spatialReference
 
        # Run metric calculate for each metric in list
        for m in metricsBaseNameList:
            # get the grid codes for this specified metric
            classValuesList = lccClassesDict[m].uniqueValueIds.intersection(landCoverValues)
            
            # process the inLandCoverGrid for the selected class
            AddMsg(f"{timer.now()} Determining population with minimal views of Class:{m.upper()}.", 0, logFile) 
            viewGrid = raster.getPatchViewGrid(m, classValuesList, excludedValuesList, inLandCoverGrid, landCoverValues, 
                                          viewRadius, conValues, minPatchSize, timer, saveIntermediates, metricConst, logFile)
  
            
            if viewGrid.maximum == None:
                AddMsg("Here")
                AddMsg(f"The view grid contained nothing but NODATA. Aborting Population Land Cover Views for class: {m} ", 1, logFile)
                continue
            
            
            # save the intermediate raster if save intermediates option has been chosen 
            if saveIntermediates:
                namePrefix = f"{metricConst.shortName}_{m.upper()}{metricConst.viewRasterOutputName}_"
                scratchName = arcpy.CreateScratchName(namePrefix, "", "RasterDataset")
                viewGrid.save(scratchName)
                AddMsg(f"{timer.now()} Save intermediate grid complete: {basename(scratchName)}", 0, logFile)
                
                # add a CATEGORY field for raster labels; make it large enough to hold your longest category label.
                AddMsg(f"{timer.now()} Adding CATEGORY field for raster labels.", 0, logFile)
                if not viewGrid.hasRAT:
                    log.logArcpy("arcpy.BuildRasterAttributeTable_management",(viewGrid, "Overwrite"),logFile)
                    arcpy.BuildRasterAttributeTable_management(viewGrid, "Overwrite")
                
                log.logArcpy("arcpy.AddField_management",(viewGrid, "CATEGORY", "TEXT", "#", "#", "20"),logFile)
                arcpy.AddField_management(viewGrid, "CATEGORY", "TEXT", "#", "#", "20")
                
                # The categoryDict should be in the format {integer1 : "category1 string", integer2: "category2 string", etc}
                categoryDict = {1: "Potential View Area"}
                raster.updateCategoryLabels(viewGrid, categoryDict)
                             
            # convert view area raster to polygon
            
            # get output name for projected viewPolygon
            namePrefix = f"{metricConst.shortName}_{m.upper()}{metricConst.viewPolygonOutputName}_"
            viewPolygonFeature = files.nameIntermediateFile([namePrefix + "","FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Converting view raster to a polygon feature. Intermediate: {basename(viewPolygonFeature)}", 0, logFile)
            
            # Check if viewPolygon is the same projection as the census raster, if not project it
            if transformMethod != "":
                log.logArcpy("arcpy.conversion.RasterToPolygon",(viewGrid,"tempPoly","NO_SIMPLIFY","Value","SINGLE_OUTER_PART",None),logFile)
                tmpRasterPolygon = arcpy.conversion.RasterToPolygon(viewGrid,"tempPoly","NO_SIMPLIFY","Value","SINGLE_OUTER_PART",None)
                
                log.logArcpy("arcpy.Project_management",("tempPoly",viewPolygonFeature,spatialCensus,transformMethod),logFile)
                arcpy.Project_management("tempPoly",viewPolygonFeature,spatialCensus,transformMethod)
                
                log.logArcpy("arcpy.Delete_management",(tmpRasterPolygon,),logFile)
                arcpy.Delete_management(tmpRasterPolygon)
            else:
                log.logArcpy("arcpy.conversion.RasterToPolygon",(viewGrid,viewPolygonFeature,"NO_SIMPLIFY","Value","SINGLE_OUTER_PART",None),logFile)
                arcpy.conversion.RasterToPolygon(viewGrid,viewPolygonFeature,"NO_SIMPLIFY","Value","SINGLE_OUTER_PART",None)
            
            # Save the current environment settings, then set to match the census raster 
            tempEnvironment0 = env.snapRaster
            tempEnvironment1 = env.cellSize            
            env.snapRaster = inCensusRaster
            env.cellSize = descCensus.meanCellWidth
            AddMsg(f"{timer.now()} Setting geoprocessing environmental parameters for snap raster and cell size to match {descCensus.baseName}", 0, logFile)
            
            # Extract Census pixels which are in the view area
            AddMsg(f"{timer.now()} Extracting population pixels within the potential view area.", 0, logFile) 
            log.logArcpy("arcpy.sa.ExtractByMask",(inCensusRaster, viewPolygonFeature), logFile)
            viewPopGrid = arcpy.sa.ExtractByMask(inCensusRaster, viewPolygonFeature)
            
            # save the intermediate raster if save intermediates option has been chosen 
            if saveIntermediates:
                namePrefix = f"{metricConst.shortName}_{m.upper()}{metricConst.areaPopRasterOutputName}_"
                scratchName = arcpy.CreateScratchName(namePrefix, "", "RasterDataset")
                viewPopGrid.save(scratchName)
                AddMsg(f"{timer.now()} Save intermediate grid complete: {basename(scratchName)}", 0, logFile)
                
            # Calculate the extracted population for each reporting unit
            namePrefix = f"{metricConst.shortName}_{m.upper()}{metricConst.areaValueCountTableName}_"
            areaPopTable = files.nameIntermediateFile([namePrefix + "","Dataset"],cleanupList)
            AddMsg(f"{timer.now()} Calculating population within minimal-view areas for each reporting unit. Intermediate: {basename(areaPopTable)}", 0, logFile)
            log.logArcpy("arcpy.sa.ZonalStatisticsAsTable",(inReportingUnitFeature,reportingUnitIdField,viewPopGrid,areaPopTable,"DATA","SUM"),logFile)
            arcpy.sa.ZonalStatisticsAsTable(inReportingUnitFeature,reportingUnitIdField,viewPopGrid,areaPopTable,"DATA","SUM")
            
            # reset the environments
            AddMsg("{0} Restoring snap raster geoprocessing environmental parameter to {1}".format(timer.now(), os.path.basename(tempEnvironment0)), 0, logFile)
            AddMsg("{0} Restoring cell size geoprocessing environmental parameter to {1}".format(timer.now(), tempEnvironment1), 0, logFile)
            env.snapRaster = tempEnvironment0
            env.cellSize = tempEnvironment1
            
            AddMsg(f"{timer.now()} Transferring values from {basename(areaPopTable)} to {basename(outTable)}.", 0, logFile)
            # get the field that will be transferred from the view population table into the output table
            fromField = "SUM"
            toField = metricsFieldnameDict[m][0] #generated metric field name for the current land cover class
            
            # Transfer the fromField values to the output table
            table.addJoinCalculateField(areaPopTable, populationTable, fromField, toField, reportingUnitIdField,logFile)
            
            # Assign 0 to reporting units where no population was calculated in the view/non-view area
            AddMsg(f"{timer.now()} Assigning 0 to reporting units where no population was calculated in the view/non-view area.", 0, logFile)
            calculate.replaceNullValues(populationTable, toField, metricConst.valueWhenNULL, logFile)

            # Replace the inField name suffix to identify the calcField     
            calcField = toField.replace(metricConst.fieldSuffix,metricConst.pctSuffix)
            
            # Calculate the percent population within view area
            AddMsg(f"{timer.now()} Calculating the percent population within view area.", 0, logFile)
            calculate.percentageValue(populationTable, toField, populationField, calcField, logFile)

            # Calculate the population for minimum view
            AddMsg(f"{timer.now()} Calculating the population for minimum view.", 0, logFile)
            calcField_WOVPOP = toField.replace(metricConst.fieldSuffix,metricConst.wovFieldSuffix)
            calculate.differenceValue(populationTable, populationField, toField, calcField_WOVPOP, logFile)

            # Calculate the percent population without view area
            AddMsg(f"{timer.now()} Calculating the percent population without view area.", 0, logFile)
            calcField_WOVPCT = calcField_WOVPOP.replace(metricConst.wovFieldSuffix,metricConst.wovPctSuffix)
            calculate.percentageValue(populationTable, calcField_WOVPOP, populationField, calcField_WOVPCT, logFile)
           
            # delete temporary features
            if arcpy.Exists("tempPoly"):
                log.logArcpy("arcpy.Delete_management",(tmpRasterPolygon,), logFile)
                arcpy.Delete_management(tmpRasterPolygon)
                
            AddMsg(f"{timer.now()} Calculation complete for Class:{m.upper()}", 0, logFile)
            
        if logFile:
            AddMsg("Summarizing the ATtILA metric output table to log file", 0)
            # append the reporting unit id field to the list of category fields; even if it's a numeric field type
            metricConst.idFields = metricConst.idFields + [reportingUnitIdField]
            log.logWriteOutputTableInfo(outTable, logFile, metricConst)
            AddMsg("Summary complete", 0)
            
            # write the standard environment settings to the log file
            log.writeEnvironments(logFile, snapRaster, processingCellSize, extentList=[inReportingUnitFeature, inLandCoverGrid, inCensusRaster])
            # parameters are: logFile, snapRaster, processingCellSize, extentList
            # if extentList is set to None, the env.extent setting will reported.
            # Place eventList here, if the extents of the datasets have been altered and you wish to use the new extents.
            # for snapRaster and processingCellSize, if the parameter is None, no entry will
            # will be recorded in the log for that parameter

            # write the metric class grid values to the log file
            log.logWriteClassValues(logFile, metricsBaseNameList, lccObj, metricConst)
                
    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
            
        errors.standardErrorHandling(e, logFile)
 
    finally:
        setupAndRestore.standardRestore(logFile)
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete")

                
def runFacilityLandCoverViews(toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                     metricsToRun, inFacilityFeature, viewRadius, viewThreshold, outTable="", processingCellSize="", 
                     snapRaster="", optionalFieldGroups=""):
    #""" Interface for script executing Facility Land Cover Views Metrics """
    try:

        metricConst = metricConstants.flcvConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, 
                          inFacilityFeature, viewRadius, viewThreshold, outTable, processingCellSize, snapRaster, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # Check to see if the inLandCoverGrid has an attribute table. If not, build one
        raster.buildRAT(inLandCoverGrid, logFile)
        
        # append the view threshold value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + viewThreshold
        # for the high view field, add the view threshold to the  field suffix
        for i, fldParams in enumerate(metricConst.additionalFields):
            fldParams[1] = metricConst.additionalSuffixes[i] + viewThreshold
        
        class metricCalcFLCV(metricCalc):
            """ Subclass that overrides buffering function for the FacilitiesLandCoverViews calculation """
            def _replaceRUFeatures(self):
                # check for duplicate ID entries in reporting unit feature. Perform dissolve if found
                self.duplicateIds = fields.checkForDuplicateValues(self.inReportingUnitFeature, self.reportingUnitIdField)
                    
                if self.duplicateIds:
                    # Get a unique name with full path for the output features - will default to current workspace:            
                    self.namePrefix = self.metricConst.shortName + "_FacDissolve"+self.inBufferDistance.split()[0]+"_"
                    self.dissolveName = utils.files.nameIntermediateFile([self.namePrefix,"FeatureClass"], flcvCalc.cleanupList)
                    AddMsg(f"{self.timer.now()} Duplicate ID values found in reporting unit feature. Forming multipart features. Intermediate: {basename(self.dissolveName)}", 0, self.logFile)
                    log.logArcpy("arcpy.Dissolve_management",(self.inReportingUnitFeature,self.dissolveName,self.reportingUnitIdField,"","MULTI_PART"),logFile)
                    self.inReportingUnitFeature = arcpy.Dissolve_management(self.inReportingUnitFeature, self.dissolveName,self.reportingUnitIdField,"","MULTI_PART")

                # Make a temporary facility point layer so that a field of the same name as reportingUnitIdField could be deleted
                # Get a unique name with full path for the output features - will default to current workspace:
                self.namePrefix = self.metricConst.facilityCopyName+self.viewRadius.split()[0]+"_"
                self.inPointFacilityName = utils.files.nameIntermediateFile([self.namePrefix,"FeatureClass"], flcvCalc.cleanupList)
                AddMsg(f"{self.timer.now()} Creating a copy of the Facility feature. Intermediate: {basename(self.inPointFacilityName)}", 0, self.logFile)
                log.logArcpy("arcpy.FeatureClassToFeatureClass_conversion",(self.inFacilityFeature,arcpy.env.workspace,basename(self.inPointFacilityName)),logFile)
                self.inPointFacilityFeature = arcpy.FeatureClassToFeatureClass_conversion(self.inFacilityFeature,arcpy.env.workspace, basename(self.inPointFacilityName))

                # Delete all fields from the copied facilities feature
                AddMsg(f"{self.timer.now()} Deleting unnecessary fields from {basename(self.inPointFacilityName)}", 0, self.logFile)
                self.facilityFields = arcpy.ListFields(self.inPointFacilityFeature)
                self.deleteFieldList = []
                for aFld in self.facilityFields:
                    if aFld.required != True:
                        self.deleteFieldList.append(aFld.name)
                utils.fields.deleteFields(self.inPointFacilityFeature, self.deleteFieldList)        
        
                # Intersect the point theme with the reporting unit theme to transfer the reporting unit id to the points
                # Get a unique name with full path for the output features - will default to current workspace:
                self.namePrefix = self.metricConst.facilityWithRUIDName+self.viewRadius.split()[0]+"_"
                self.intersectResultName = utils.files.nameIntermediateFile([self.namePrefix,"FeatureClass"], flcvCalc.cleanupList)
                AddMsg(f"{self.timer.now()} Assigning reporting unit ID to {basename(self.inPointFacilityName)}. Intermediate: {basename(self.intersectResultName)}", 0, self.logFile)
                log.logArcpy("arcpy.Intersect_analysis",([self.inPointFacilityFeature,self.inReportingUnitFeature],self.intersectResultName,"NO_FID","","POINT"),logFile)
                self.intersectResult = arcpy.Intersect_analysis([self.inPointFacilityFeature,self.inReportingUnitFeature],self.intersectResultName,"NO_FID","","POINT")

                # Buffer the facility features with the reporting unit IDs to desired distance
                # Get a unique name with full path for the output features - will default to current workspace:
                self.namePrefix = self.metricConst.viewBufferName+self.viewRadius.split()[0]+"_"
                self.bufferResultName = utils.files.nameIntermediateFile([self.namePrefix,"FeatureClass"], flcvCalc.cleanupList)
                AddMsg(f"{self.timer.now()} Buffering {basename(self.intersectResultName)} to {viewRadius}. Intermediate: {basename(self.bufferResultName)}", 0, self.logFile)
                log.logArcpy("arcpy.Buffer_analysis",(self.intersectResult,self.bufferResultName,viewRadius,"","","NONE","", "PLANAR"), logFile)
                self.bufferResult = arcpy.Buffer_analysis(self.intersectResult,self.bufferResultName,viewRadius,"","","NONE","", "PLANAR")

                self.inReportingUnitFeature = self.bufferResult
                
                # add the altered inReportingUnitFeature to the list of features to determine the intersection extent
                self.extentList.append(self.inReportingUnitFeature)
                

            def _makeAttilaOutTable(self):
                # Construct two tables: 
                # 1) a land cover proportions table for individual facility buffer zones, and
                # 2) a metric output table
                
                # Get a unique name with full path for the land cover proportions table - will default to current workspace:
                self.namePrefix = self.metricConst.lcpTableName+self.viewRadius.split()[0]+"_"
                self.facilityLCPTable = utils.files.nameIntermediateFile([self.namePrefix,"Dataset"], flcvCalc.cleanupList)
                
                # add QA fields and class area fields to the land cover proportions table
                self.facilityOptionsList = ["QAFIELDS"]
                
                # tag the facility ID field for the land cover proportions table
                self.facilityIdField = utils.fields.getFieldByName(self.bufferResult, "ORIG_FID")
                
                # Save the output metric field name parameters and replace them with the land cover proportions field name parameters
                self.oldFieldParameters = self.metricConst.fieldParameters
                self.metricConst.fieldParameters = self.metricConst.lcpFieldParameters
                
                # Construct the land cover proportions table
                AddMsg(f"{self.timer.now()} Constructing facility buffer land cover proportions table. Intermediate: {basename(self.facilityLCPTable)}", 0, self.logFile)
                self.lcpTable, self.lcpMetricsFieldnameDict = table.tableWriterByClass(self.facilityLCPTable,
                                                                                    self.metricsBaseNameList,
                                                                                    self.facilityOptionsList,
                                                                                    self.metricConst, self.lccObj,
                                                                                    self.facilityIdField, self.logFile)
                # Restore the output metric field name parameters 
                self.metricConst.fieldParameters = self.oldFieldParameters
                
                # Construct the ATtILA metric output table
                #AddMsg("{0} Constructing the ATtILA metric output table: {1}".format(self.timer.now(), self.outTable), 0, self.logFile)
                AddMsg(f"{self.timer.now()} Constructing the ATtILA metric output table: {basename(self.outTable)}", 0, self.logFile)
                # Internal function to construct the ATtILA metric output table
                self.newTable, self.metricsFieldnameDict = table.tableWriterByClass(self.outTable,
                                                                                  self.metricsBaseNameList,
                                                                                  self.optionalGroupsList,
                                                                                  self.metricConst, self.lccObj,
                                                                                  self.outIdField, self.logFile,
                                                                                  self.metricConst.additionalFields)
                
                # Add an additional field for the facility counts within each reporting unit. Used AddFields so that the 
                # field properties could be defined and retrieved from the metric constants. 
                log.logArcpy("arcpy.management.AddFields",(self.newTable, self.metricConst.singleFields),logFile)
                arcpy.management.AddFields(self.newTable, self.metricConst.singleFields)


            def _makeTabAreaTable(self):
                AddMsg(f"{self.timer.now()} Generating a zonal tabulate area table for view buffer areas", 0, self.logFile)
                # Make a tabulate area table. Use the facility id field as the Zone field to calculate values for each
                # facility buffer area instead of the reporting unit as a whole. 
                self.tabAreaTable = TabulateAreaTable(self.inReportingUnitFeature, self.facilityIdField.name,
                                                      self.inLandCoverGrid, self.logFile, self.tableName, self.lccObj)
                

                tabTableName = basename(self.tabAreaTable._tableName)
                AddMsg(f"{self.timer.now()} Completed zonal tabulate area table. Intermediate: {tabTableName}", 0, self.logFile)

            
            def _calculateMetrics(self):
                AddMsg(f"{self.timer.now()} Processing the tabulate area table and computing metric values", 0, self.logFile)
                # Perform some preliminary housekeeping steps. These steps will not be performed in the normal Housekeeping
                # routine as the add QA and Area Fields options which trigger their creation are not available in the 
                # tool's user dialog box. See the overall metricCalc Class for more detail about Housekeeping.
                
                # Set the outputSpatialRef and zoneAreaDict using the generated facility buffer feature.
                self.outputSpatialRef = settings.getOutputSpatialReference(self.inLandCoverGrid)
                self.zoneAreaDict = None
                self.zoneAreaDict = polygons.getMultiPartIdAreaDict(self.inReportingUnitFeature, self.facilityIdField.name, self.outputSpatialRef)
                
                # Generate a table of land cover proportions within each facility's view area.
                calculate.landCoverProportions(self.lccClassesDict, self.metricsBaseNameList, self.facilityOptionsList,
                                               self.metricConst, self.facilityIdField, self.facilityLCPTable, self.tabAreaTable,
                                               self.lcpMetricsFieldnameDict, self.zoneAreaDict, self.reportingUnitAreaDict)
                
                # Take the land cover proportions table and count the number of facilities that have low views of selected land cover classes.                        
                calculate.landCoverViews(self.metricsBaseNameList,self.metricConst,self.viewRadius,self.viewThreshold, self.cleanupList, 
                                         self.outTable, self.newTable, self.reportingUnitIdField,
                                         self.facilityLCPTable, self.intersectResult, self.metricsFieldnameDict,self.lcpMetricsFieldnameDict,
                                         self.timer, self.logFile)
            
                    
        # Create new instance of metricCalc class to contain parameters            
        flcvCalc = metricCalcFLCV(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                                  metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst, logFile)
        
        # Assign class attributes unique to this module.
        flcvCalc.inFacilityFeature = inFacilityFeature
        flcvCalc.viewRadius = viewRadius
        flcvCalc.viewThreshold = viewThreshold
        flcvCalc.metricsToRun = metricsToRun
        flcvCalc.extentList = [inReportingUnitFeature, inLandCoverGrid]
        
        # Initiate our flexible cleanuplist
        flcvCalc.cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
        if flcvCalc.saveIntermediates:
            flcvCalc.cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            flcvCalc.cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))


        # Run Calculation
        flcvCalc.run()

    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
            
        errors.standardErrorHandling(e, logFile)
 
    finally:
        if not flcvCalc.cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in flcvCalc.cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete", 0)
        
        setupAndRestore.standardRestore(logFile)
          

def runNeighborhoodProportions(toolPath, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, inNeighborhoodSize,
                      burnIn, burnInValue="", minPatchSize="#", createZones="", zoneBin_str="", overWrite="",
                      outWorkspace="#", optionalFieldGroups="#"):
    """ Interface for script executing Generate Proximity Polygons utility """
    
    from arcpy import env
    from arcpy.sa import Reclassify,RegionGroup,RemapValue,RemapRange

    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.npConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, inNeighborhoodSize, burnIn, burnInValue, 
                          minPatchSize, createZones, zoneBin_str, overWrite, outWorkspace, optionalFieldGroups]

        # create a log file if requested, otherwise logFile = None
        outTable = os.path.join(str(outWorkspace), metricConst.name)
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        
        # Check to see if the inLandCoverGrid has an attribute table. If not, build one
        raster.buildRAT(inLandCoverGrid, logFile)
        
        ### Initialization
        # Start the timer
        timer = DateTimer()
        AddMsg(f"{timer.now()} Setting up environment variables", 0, logFile)
        processingCellSize = Raster(inLandCoverGrid).meanCellWidth
        snapRaster = inLandCoverGrid
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster,processingCellSize,outWorkspace,
                                                                               [metricsToRun,optionalFieldGroups])

        # Process the Land Cover Classification XML
        lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        lccClassesDict = lccObj.classes
        # Get the lccObj values dictionary. This contains all the properties of each value specified in the Land Cover Classification XML    
        lccValuesDict = lccObj.values
        # create a list of all the grid values in the selected land cover grid
        landCoverValues = raster.getRasterValues(inLandCoverGrid, logFile)
        # get the frozenset of excluded values (i.e., values marked as EXCLUDED in the Land Cover Classification XML)
        excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)
                
        # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
        settings.checkExcludedValuesInClass(metricsBaseNameList, lccObj, lccClassesDict, logFile)
        # alert user if the land cover grid has values undefined in the LCC XML file
        settings.checkGridValuesInLCC(inLandCoverGrid, lccObj, logFile)
        # alert user if the land cover grid cells are not square (default to size along x axis)
        settings.checkGridCellDimensions(inLandCoverGrid, logFile)
        
        # Determine if the user wants to save the intermediate products
        saveIntermediates = globalConstants.intermediateName in optionalGroupsList
        
        # determine the active map to add the output raster/features    
        try:
            currentProject = arcpy.mp.ArcGISProject("CURRENT")
            actvMap = currentProject.activeMap
        except:
            actvMap = None
        
        # Save the current environment settings, then set to desired condition  
        tempEnvironment0 = env.overwriteOutput
        if overWrite == "true":
            env.overwriteOutput = True
            AddMsg("The 'Allow geoprocessing tools to overwrite existing datasets' option has been set to TRUE per your request. The option will be reset to FALSE upon completion of this tool.", 1, logFile)
        else:
            env.overwriteOutput = False

        # create list of layers to add to the active Map
        addToActiveMap = []
        
        ### Computations
        
        # If necessary, generate a grid of excluded areas (e.g., water bodies) to be burnt into the proximity grid 
        # This only needs to be done once regardless of the number of requested class proximity outputs  
        burnInGrid = None
        if burnIn == "true":
            if len(excludedValuesList) == 0:
                AddMsg("No excluded values in selected Land Cover Classification file. No BURN IN areas will be processed.", 1, logFile)
                burnIn = "false"
            else:
                AddMsg(f"{timer.now()} Processing BURN IN areas.", 0, logFile)
                
                if int(minPatchSize) > 1:
                    # create class (value = 0) / other (value = 0) / excluded grid (value = 1) raster
                    # define the reclass values
                    classValue = 0
                    excludedValue = 1
                    otherValue = 0
                    newValuesList = [classValue, excludedValue, otherValue]
                    
                    # generate a reclass list where each item in the list is a two item list: the original grid value, and the reclass value
                    classValuesList = []
                    reclassPairs = raster.getInOutOtherReclassPairs(landCoverValues, classValuesList, excludedValuesList, newValuesList)
            
                    AddMsg(f"{timer.now()} Reclassifying excluded values in land cover to 1. All other values = 0.", 0, logFile)
                    log.logArcpy("arcpy.sa.Reclassify",(inLandCoverGrid,"VALUE", RemapValue(reclassPairs)),logFile)
                    excludedBinary = arcpy.sa.Reclassify(inLandCoverGrid,"VALUE", RemapValue(reclassPairs))

                    AddMsg(f"{timer.now()} Calculating size of excluded area patches.", 0, logFile)
                    log.logArcpy("arcpy.sa.RegionGroup",(excludedBinary,"EIGHT","WITHIN","ADD_LINK"), logFile)
                    regionGrid = arcpy.sa.RegionGroup(excludedBinary,"EIGHT","WITHIN","ADD_LINK")
                
                    AddMsg(f"{timer.now()} Assigning {burnInValue} to excluded area patches >= {minPatchSize} cells in size.", 0, logFile)
                    delimitedCOUNT = arcpy.AddFieldDelimiters(regionGrid,"COUNT")
                    whereClause = delimitedCOUNT+" >= " + minPatchSize + " AND LINK = 1"
                    log.logArcpy("arcpy.sa.Con", (regionGrid, int(burnInValue), 0, whereClause), logFile)
                    burnInGrid = arcpy.sa.Con(regionGrid, int(burnInValue), 0, whereClause)
                else:
                    # create class (value = 0) / other (value = 0) / excluded grid (value = burnInValue) raster
                    # define the reclass values
                    classValue = 0
                    excludedValue = int(burnInValue)
                    otherValue = 0
                    newValuesList = [classValue, excludedValue, otherValue]
                    
                    # generate a reclass list where each item in the list is a two item list: the original grid value, and the reclass value
                    classValuesList = []
                    reclassPairs = raster.getInOutOtherReclassPairs(landCoverValues, classValuesList, excludedValuesList, newValuesList)
            
                    AddMsg(f"{timer.now()} Reclassifying excluded values in land cover to {burnInValue}. All other values = 0.", 0, logFile)
                    burnInGrid = Reclassify(inLandCoverGrid,"VALUE", RemapValue(reclassPairs))

                
                # save the intermediate raster if save intermediates option has been chosen
                if saveIntermediates: 
                    namePrefix = f"{metricConst.shortName}_{minPatchSize}_{metricConst.burnInGridName}"
                    if overWrite == "false":
                        namePrefix = f"{namePrefix}_"
                    scratchName = files.getRasterName(namePrefix)
                    AddMsg(f"{timer.now()} Saving intermediate grid: {basename(scratchName)}", 0, logFile)
                    burnInGrid.save(scratchName)
                    AddMsg(f"{timer.now()} Save intermediate grid complete: {basename(scratchName)}")

        # Run metric calculate for each metric in list
        for m in metricsBaseNameList:
            # get the grid codes for this specified metric
            classValuesList = lccClassesDict[m].uniqueValueIds.intersection(landCoverValues)
 
            # process the inLandCoverGrid for the selected class
            AddMsg(f"{timer.now()} Processing neighborhood proportions grid for {m.upper()}.", 0, logFile)
            
            maxCellCount = pow(int(inNeighborhoodSize), 2)
                 
            # create class (value = 1) / other (value = 0) / excluded grid (value = 0) raster
            # define the reclass values
            classValue = 1
            excludedValue = 0
            otherValue = 0
            newValuesList = [classValue, excludedValue, otherValue]
            
            # generate a reclass list where each item in the list is a two item list: the original grid value, and the reclass value
            reclassPairs = raster.getInOutOtherReclassPairs(landCoverValues, classValuesList, excludedValuesList, newValuesList)
              
            AddMsg(f"{timer.now()} Reclassifying selected {m.upper()} land cover class to 1. All other values = 0.", 0, logFile)
            log.logArcpy("arcpy.sa.Reclassify",(inLandCoverGrid,"VALUE", RemapValue(reclassPairs)), logFile)
            reclassGrid = arcpy.sa.Reclassify(inLandCoverGrid,"VALUE", RemapValue(reclassPairs))
            
            AddMsg(f"{timer.now()} Performing focal SUM on reclassified raster using {inNeighborhoodSize} x {inNeighborhoodSize} cell neighborhood.", 0, logFile)
            neighborhood = arcpy.sa.NbrRectangle(int(inNeighborhoodSize), int(inNeighborhoodSize), "CELL")
            log.logArcpy("arcpy.sa.FocalStatistics", (f'reclassGrid == {classValue}', neighborhood, "SUM", "NODATA"), logFile)
            nbrCntGrid = arcpy.sa.FocalStatistics(reclassGrid == classValue, neighborhood, "SUM", "NODATA")
                
            AddMsg(f"{timer.now()} Calculating the proportion of land cover class within {inNeighborhoodSize} x {inNeighborhoodSize} cell neighborhood.", 0, logFile)
            log.logArcpy("arcpy.sa.RasterCalculator",("[nbrCntGrid]", ["x"], (f' (x / {maxCellCount}) * 100') ), logFile)
            proximityGrid = arcpy.sa.RasterCalculator([nbrCntGrid], ["x"], (f' (x / {maxCellCount}) * 100') )
            
            # get output grid name
            namePrefix = f"{m.upper()}_{inNeighborhoodSize}{metricConst.proxRasterOutName}"
            if overWrite == "false":
                namePrefix = f"{namePrefix}_"
            proximityGridName = files.getRasterName(namePrefix)
            
            if burnIn == "true":
                AddMsg(f"{timer.now()} Burning excluded areas into proportions grid.", 0, logFile)
                delimitedVALUE = arcpy.AddFieldDelimiters(burnInGrid,"VALUE")
                whereClause = delimitedVALUE+" = 0"
                log.logArcpy("arcpy.sa.Con",(burnInGrid, proximityGridName, burnInGrid, whereClause), logFile)
                proximityGrid = arcpy.sa.Con(burnInGrid, proximityGrid, burnInGrid, whereClause)
        
        
            # Add output grid name to the list of features to add to the Contents pane
            datasetList = arcpy.ListDatasets()
            if proximityGridName in datasetList:
                arcpy.Delete_management(proximityGridName)
            AddMsg(f"{timer.now()} Saving proportions grid: {basename(proximityGridName)}.", 0, logFile)
            try:
                proximityGrid.save(proximityGridName)
            except:
                raise errors.attilaException(errorConstants.rasterOutputFormatError) 
            AddMsg(f"{timer.now()} Save proportions grid complete: {basename(proximityGridName)}.", 0, logFile)
            addToActiveMap.append(proximityGridName)
                  
            # save the intermediate raster if save intermediates option has been chosen 
            if saveIntermediates:
                namePrefix = f"{m.upper()}_{inNeighborhoodSize}{metricConst.proxFocalSumOutName}"
                if overWrite == "false":
                    namePrefix = f"{namePrefix}_"
                scratchName = files.getRasterName(namePrefix)  
                datasetList = arcpy.ListDatasets()
                if scratchName in datasetList:
                    arcpy.Delete_management(scratchName)
                AddMsg(f"{timer.now()} Saving intermediate grid: {basename(scratchName)}.", 0, logFile)
                try:
                    nbrCntGrid.save(scratchName)
                except:
                    raise errors.attilaException(errorConstants.rasterOutputFormatError)
                AddMsg(f"{timer.now()} Save intermediate grid complete: {basename(scratchName)}.", 0, logFile)
  
            # convert neighborhood proportions raster to zones if createZones is selected
            if createZones == "true":
                # To reclass the proportions grid, the max grid value is 100
                maxGridValue = 100
        
                # Set up break points to reclass proximity grid into % classes
                reclassBins = raster.getRemapBinsByPercentStep(maxGridValue, int(zoneBin_str))
                rngRemap = RemapRange(reclassBins)
                
                time.sleep(1) # A small pause is needed here between quick successive timer calls
                AddMsg(f"{timer.now()} Reclassifying proportions grid into {zoneBin_str}% breaks.", 0, logFile)
                # nbrZoneGrid = Reclassify(proximityGrid, "VALUE", rngRemap)
                # The simple reclassify operation above, often leaves the ESRI default layer name in the saved 
                # nbrZoneGrid when the land cover raster is relatively small. Although the nbrZoneGrid appears to have the
                # correct name in the catalog, when the raster is added to a map, the layer name is displayed in the TOC
                # instead of the saved raster name (e.g., Reclass_NI_91 instead of NI_9_Zone0). The technique below appears
                # to alleviate that problem without adding substantial time to the reclassification operation.
                nbrZoneGrid = (Reclassify(proximityGrid, "VALUE", rngRemap) * 1)
                if logFile:
                    # capture the reclass operation to the log file. The usual logArcpy technique won't work
                    logFile.write(f'{timer.now()}   [CMD] (Reclassify({proximityGridName}, VALUE, {rngRemap}) * 1)\n')
                namePrefix = f"{m.upper()}_{inNeighborhoodSize}{metricConst.proxZoneRaserOutName}"
                if overWrite == "false":
                    namePrefix = f"{namePrefix}_"
                scratchName = files.getRasterName(namePrefix)
                datasetList = arcpy.ListDatasets()
                if scratchName in datasetList:
                    arcpy.Delete_management(scratchName)
                try:
                    AddMsg(f"{timer.now()} Saving {zoneBin_str}% breaks zone raster: {basename(scratchName)}", 0, logFile)
                    nbrZoneGrid.save(scratchName)
                except:
                    raise errors.attilaException(errorConstants.rasterOutputFormatError)
                AddMsg(f"{timer.now()} Save intermediate grid complete: {basename(scratchName)}.", 0, logFile)
                addToActiveMap.append(scratchName)
 
     
        if logFile:
            # write the standard environment settings to the log file
            log.writeEnvironments(logFile, snapRaster, processingCellSize, extentList=[inLandCoverGrid])
            # parameters are: logFile, snapRaster, processingCellSize, extentList
            # if extentList is set to None, the env.extent setting will reported.
            # Place eventList here, if the extents of the datasets have been altered and you wish to use the new extents.
            # for snapRaster and processingCellSize, if the parameter is None, no entry will
            # will be recorded in the log for that parameter
        
            # write the metric class grid values to the log file
            log.logWriteClassValues(logFile, metricsBaseNameList, lccObj, metricConst)
        
        # add outputs to the active map
        if actvMap != None:
            for aFeature in addToActiveMap:
                actvMap.addDataFromPath(aFeature)
                AddMsg(("Adding {0} to {1} view").format(os.path.basename(aFeature), actvMap.name))

    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
            
        errors.standardErrorHandling(e, logFile)

    finally:
        setupAndRestore.standardRestore(logFile)
        env.overwriteOutput = tempEnvironment0


def runIntersectionDensity(toolPath, inLineFeature, mergeLines, mergeField="#", mergeDistance='#', outputCS="#", cellSize="#", 
                           searchRadius="#", areaUnits="#", outRaster="#", optionalFieldGroups="#"):
    """ Interface for script executing Intersection Density utility """
    from arcpy import env
    
    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.idConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inLineFeature, mergeLines, mergeField, mergeDistance, outputCS, cellSize, 
                          searchRadius, areaUnits, outRaster, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outRaster, toolPath)
        
        ### Initialization
        # Start the timer
        timer = DateTimer()
        AddMsg(f"{timer.now()} Setting up environment variables", 0, logFile)
        
        # set up dummy variables to pass to standardSetup in setupAndRestore. SetupAndRestore will set the environmental
        # variables as desired and pass back the optionalGroupsList to use for intermediate products retention.
        # metricsBaseNameList is not used for this tool.
        metricsToRun = 'item1  -  description1;item2  -  description2'
        snapRaster = False

        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster,cellSize,os.path.dirname(outRaster),
                                                                              [metricsToRun,optionalFieldGroups])  

        if globalConstants.intermediateName in optionalGroupsList:
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
        
        # determine the active map to add the output raster/features    
        try:
            currentProject = arcpy.mp.ArcGISProject("CURRENT")
            actvMap = currentProject.activeMap    
        except:
            actvMap = None
        
        # create list of layers to add to the active Map
        addToActiveMap = []
        
        # Do a Describe on the Road feature input and get the file's basename.
        descInLines = arcpy.Describe(inLineFeature)
        inBaseName = descInLines.baseName
        
        # if no specific geoprocessing environment extent is set, temporarily set it to match the inLineFeature. It will be reset during the standardRestore
        nonSpecificExtents = ["NONE", "MAXOF", "MINOF"]
        envExtent = str(env.extent).upper()
        if envExtent in nonSpecificExtents:
            AddMsg(f"{timer.now()} Using {inBaseName}'s extent for geoprocessing steps.", 0, logFile)
            env.extent = descInLines.extent
        else:
            AddMsg(f"{timer.now()} Extent found in Geoprocessing environment settings used for processing.", 0, logFile)
            
        ### Computations
        
        # Set a variable to create, if necessary, a copy of the road feature class that we can add new fields to for calculations.
        makeCopy = True
        
        # Get the spatial reference for the input line theme
        spatialRef = descInLines.spatialReference
        # Strip off ESRI's spatial reference code from the string representation
        inLineCS = spatialRef.exportToString().split(";")[0]
        
        # PROJECT, if necessary
        # The inLineFeature needs to be in a projected coordinate system for the MergeDividedRoads and the KernelDensity operations 
        if inLineCS != outputCS:
            # Project the road feature to the selected output coordinate system.
            prjPrefix = f"{metricConst.shortName}_{inBaseName}_{metricConst.prjRoadName}_"       
            prjFeatureName = files.nameIntermediateFile([prjPrefix, "FeatureClass"], cleanupList)
            outCS = arcpy.SpatialReference(text=outputCS)
            AddMsg(f"{timer.now()} Projecting {inBaseName} to {outCS.name}. Intermediate: {basename(prjFeatureName)}", 0, logFile)
            log.logArcpy("arcpy.Project_management", (inLineFeature, prjFeatureName, outCS), logFile)
            inRoadFeature = arcpy.Project_management(inLineFeature, prjFeatureName, outCS)
            
            # No need to make a copy of the inLineFeature to add fields to. Can use the projected Feature instead
            makeCopy = False
        else:
            inRoadFeature = inLineFeature

        # MERGE LINES, if requested
        if mergeLines == "true":
            if mergeField == "":
                if makeCopy: # The inLineFeature was not already copied by the PROJECT operation.
                    # Create a copy of the road feature class that we can add new fields to for calculations.
                    namePrefix = f"{metricConst.shortName}_{inBaseName}_"
                    copyFeatureName = files.nameIntermediateFile([namePrefix,"FeatureClass"],cleanupList)
                    AddMsg(f"{timer.now()} Copying {inBaseName} to {basename(copyFeatureName)}.", 0, logFile)
                    log.logArcpy("arcpy.FeatureClassToFeatureClass_conversion",(inLineFeature,env.workspace,basename(copyFeatureName)),logFile)
                    inRoadFeature = arcpy.FeatureClassToFeatureClass_conversion(inLineFeature,env.workspace,basename(copyFeatureName))

                # No merge field was supplied. Add a field to the copied inRoadFeature and populate it with a constant value
                AddMsg(f"{timer.now()} Adding a dummy field to {arcpy.Describe(inRoadFeature).baseName} and assigning value 1 to all records.", 0, logFile)
                mergeField = metricConst.dummyFieldName
                log.logArcpy("arcpy.AddField_management", (inRoadFeature,mergeField,"SHORT"), logFile)
                arcpy.AddField_management(inRoadFeature,mergeField,"SHORT")
                
                log.logArcpy("arcpy.CalculateField_management", (inRoadFeature,mergeField,1), logFile)
                arcpy.CalculateField_management(inRoadFeature,mergeField,1)
            
            # Ensure the road feature class is comprised of singleparts. Multipart features will cause MergeDividedRoads to fail.
            namePrefix = f"{metricConst.shortName}_{inBaseName}_{metricConst.singlepartRoadName}_"
            singlepartFeatureName = files.nameIntermediateFile([namePrefix,"FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Converting Multipart features to Singlepart. Intermediary output: {basename(singlepartFeatureName)}", 0, logFile)
            arcpy.MultipartToSinglepart_management(inRoadFeature, singlepartFeatureName)

            # Generate single-line road features in place of matched pairs of divided road lanes.
            # Only roads with the same value in the mergeField and within the mergeDistance will be merged. All non-merged roads are retained.
            # Input features with the Merge Field parameter value equal to zero are locked and will not be merged, even if adjacent features are not locked
            namePrefix = f"{metricConst.shortName}_{inBaseName}_{metricConst.mergedRoadName}_"
            mergedFeatureName = files.nameIntermediateFile([namePrefix,"FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Merging divided road features. Intermediary output: {basename(mergedFeatureName)}", 0, logFile)
            
            # This is also the final reassignment of the inRoadFeature variable
            log.logArcpy("arcpy.MergeDividedRoads_cartography",(singlepartFeatureName,mergeField,mergeDistance,mergedFeatureName),logFile)
            inRoadFeature = arcpy.MergeDividedRoads_cartography(singlepartFeatureName,mergeField,mergeDistance,mergedFeatureName)

        # UNSPLIT LINES
        # We're only going to use two parameters for the arcpy.UnsplitLine_management tool. 
        # The original code used a third parameter to focus the unsplit operation on the  "ST_NAME" field. 
        # However, this will cause an intersection wherever a street name changes regardless if it's an actual intersection. 
        # Less importantly, it would require the user to identify which field in the "roads" layer is the street name field 
        # adding more clutter to the tool interface.
        unsplitPrefix = f"{metricConst.shortName}_{inBaseName}_{metricConst.unsplitRoadName}_" 
        unsplitFeatureName = files.nameIntermediateFile([unsplitPrefix, "FeatureClass"], cleanupList)
        AddMsg(f"{timer.now()} Unsplitting {arcpy.Describe(inRoadFeature).baseName}. Intermediate: {basename(unsplitFeatureName)}", 0, logFile)
        log.logArcpy("arcpy.UnsplitLine_management", (inRoadFeature, unsplitFeatureName), logFile)
        arcpy.UnsplitLine_management(inRoadFeature, unsplitFeatureName)
        
        # INTERSECT LINES WITH THEMSELVES
        intersectPrefix = f"{metricConst.shortName}_{inBaseName}_{metricConst.roadIntersectName}_" 
        intersectFeatureName = files.nameIntermediateFile([intersectPrefix, "FeatureClass"], cleanupList) 
        AddMsg(f"{timer.now()} Finding intersections. Intermediate: {basename(intersectFeatureName)}.", 0, logFile)
        log.logArcpy("arcpy.Intersect_analysis",([unsplitFeatureName,unsplitFeatureName],intersectFeatureName,"ONLY_FID",'',"POINT"),logFile)
        arcpy.Intersect_analysis([unsplitFeatureName, unsplitFeatureName], intersectFeatureName, "ONLY_FID",'',"POINT")

        # DELETE REDUNDANT INTERSECTION POINTS THAT OCCUR AT THE SAME LOCATION
        AddMsg(f"{timer.now()} Deleting identical intersections.", 0, logFile)
        log.logArcpy("arcpy.DeleteIdentical_management", (intersectFeatureName, "Shape"), logFile)
        arcpy.DeleteIdentical_management(intersectFeatureName, "Shape")

        # Calculate a magnitude-per-unit area from the intersection features using a kernel function to fit a smoothly tapered surface to each point. 
        # The output cell size, search radius, and area units can be altered by the user
        AddMsg(f"{timer.now()} Performing kernel density: Result saved as {basename(outRaster)}.", 0, logFile)
        # Sometimes, often when the extent of an area is small, the ESRI default layer name is retained in the
        # saved output raster. Although the output raster appears to have the correct name in the catalog, when the 
        # raster is added to a map, the layer name is displayed in the TOC instead. Multiplying the result by 1  
        # appears to alleviate that problem without adding substantial time to the overall operation.
        den = (arcpy.sa.KernelDensity(intersectFeatureName, "NONE", int(cellSize), int(searchRadius), areaUnits) * 1)
        if logFile:
            # capture the operation to the log file. The usual logArcpy technique won't work
            logFile.write(f'{timer.now()}   [CMD] (arcpy.sa.KernelDensity({intersectFeatureName}, "NONE", int({cellSize}), int({searchRadius}), areaUnits) * 1) * 1)\n')

        # Save the kernel density raster
        den.save(outRaster)
        AddMsg(f"{timer.now()} Kernel density grid save complete: {arcpy.Describe(den).baseName}", 0, logFile)
        
        # Add it to the list of features to add to the Contents pane
        addToActiveMap.append(outRaster)
        
        # add outputs to the active map
        if actvMap != None:
            for aFeature in addToActiveMap:
                actvMap.addDataFromPath(aFeature)
                AddMsg(f"Adding {basename(aFeature)} to {actvMap.name} view")
        
        if logFile:
            # write the standard environment settings to the log file
            log.writeEnvironments(logFile, None, None, extentList=[inLineFeature])
            # parameters are: logFile, snapRaster, processingCellSize, extentList
            # if extentList is set to None, the env.extent setting will reported.
            # Place eventList here, if the extents of the datasets have been altered and you wish to use the new extents.
            # for snapRaster and processingCellSize, if the parameter is None, no entry will
            # will be recorded in the log for that parameter

    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
            
        errors.standardErrorHandling(e, logFile)
 
    finally:
        setupAndRestore.standardRestore(logFile)
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete")
                
                
def runCreateWalkabilityCostRaster(toolPath, inWalkFeatures, inImpassableFeatures='', maxTravelDistStr='', walkValueStr='', baseValueStr='',
                                   outRaster='', cellSizeStr='', snapRaster='', optionalFieldGroups=''):
    """ Interface for script executing Create Walkability Cost Raster utility """

    from arcpy import env
    import math
    

    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        ### Setup
        
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.cwcrConstants()
    
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inWalkFeatures, inImpassableFeatures, maxTravelDistStr, walkValueStr, baseValueStr,
                          outRaster, cellSizeStr, snapRaster, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outRaster, toolPath)
        
        ### Initialization
        # Start the timer
        timer = DateTimer()
        AddMsg(f"{timer.now()} Setting up environment variables", 0, logFile)
    
        # set up dummy variables to pass to standardSetup in setupAndRestore. SetupAndRestore will set the environmental
        # variables as desired and pass back the optionalGroupsList to use for intermediate products retention.
        # metricsBaseNameList is not used for this tool.
        metricsToRun = 'item1  -  description1;item2  -  description2'
    
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster,cellSizeStr,os.path.dirname(outRaster),
                                                                              [metricsToRun,optionalFieldGroups])  
    
        if globalConstants.intermediateName in optionalGroupsList:
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
        
        # Do a Describe on the Snap Raster input and get the file's basename.
        descSnapRaster = arcpy.Describe(snapRaster)
        snapBaseName = descSnapRaster.baseName
        
        # Check to see if the user has specified a Processing cell size other than the cell size of the inLandCoverGrid
        cellSize = conversion.convertNumStringToNumber(cellSizeStr)
        x = cellSize
        y = Raster(snapRaster).meanCellWidth
        
        if x%y == 0 or y%x == 0:
            pass
        else:
            AddMsg("The Processing cell size and the input Snap raster's cell size are not equal to each other nor are they multiples or factors of each other. "\
                   "To best use the output of this tool with the Walkable Parks Tool, it is highly recommended that the Processing cell size is set "\
                   "as either equal to the Snap raster's cell size, a factor of the Snap raster's cell size, or a multiple of the Snap raster's cell size.", 1, logFile)
        
        # if no specific geoprocessing environment extent is set, temporarily set it to match the snapRaster. It will be reset during the standardRestore
        nonSpecificExtents = ["NONE", "MAXOF", "MINOF"]
        envExtent = str(env.extent).upper()
        if envExtent in nonSpecificExtents:
            AddMsg(f"{timer.now()} Using {snapBaseName}'s extent for geoprocessing steps.", 0, logFile)
            env.extent = descSnapRaster.extent
        else:
            AddMsg(f"{timer.now()} Extent found in Geoprocessing environment settings used for processing.", 0, logFile)
        
        # if no specific geoprocessing environment outputCoodinateSystem is set, temporarily set it to match the snapRaster. It will be reset during the standardRestore
        nonSpecificOCS = ["NONE"]
        envOCS = str(env.outputCoordinateSystem).upper()
        if envOCS in nonSpecificOCS:
            outSR = descSnapRaster.spatialReference
            AddMsg(f"{timer.now()} Using {snapBaseName}'s spatial reference for geoprocessing steps: {outSR.name}", 0, logFile)
            env.outputCoordinateSystem = outSR
        else:
            AddMsg(f"{timer.now()} OutputCoordinateSystem found in Geoprocessing environment settings used for processing.", 0, logFile)
    
        
        ### Computations
        
        # Convert number strings to either floating-point or integer numbers. ATtILA converts input parameters to text.
        walkNumber = conversion.convertNumStringToNumber(walkValueStr)
        baseNumber = conversion.convertNumStringToNumber(baseValueStr)
        distNumber = conversion.convertNumStringToNumber(maxTravelDistStr) 
        
        ## convert all input walkable features to a single raster
        
        AddMsg(f"{timer.now()} Processing Walkability features.", 0, logFile)
        walkName = f"{metricConst.shortName}_Walk"
        # merge all input Walkability features into separate line and polygon feature classes
        mergedWalkFeatures, cleanupList = vector.mergeVectorsByType(inWalkFeatures, walkName, cleanupList, timer, logFile)
        
        # mergedWalkFeatures is a list of feature class catalog paths and possible nonsense strings with invalid catalog path characters. 
        # Create a list of just the catalog paths.  
        vectorsToRaster = [fc for fc in mergedWalkFeatures if arcpy.Exists(fc)]
        
        # create the Walkable raster. 
        walkRaster, cleanupList = raster.getWalkabilityGrid(vectorsToRaster, walkNumber, baseNumber, walkName, cellSize, cleanupList, timer, logFile)
        
        walkRasterPath = arcpy.Describe(walkRaster).catalogPath
        
        ## if applicable, convert all input impassable features to a single raster and combine with walkable raster
        if inImpassableFeatures:
            # auto calculate the impass value and inform the user. Consider changing this to an input parameter.
            impassNumber = math.ceil(distNumber / cellSize)
            AddMsg(f"{timer.now()} Impass Value = {impassNumber}. Calculated as (Maximum walking distance / Cost raster cell size) rounded up to the nearest integer.", 0, logFile)
            
            AddMsg(f"{timer.now()} Processing Impassable features.", 0, logFile)
            impassName = f"{metricConst.shortName}_Impass"
            # merge all input Impassable features into separate line and polygon feature classes
            mergedImpassFeatures, cleanupList = vector.mergeVectorsByType(inImpassableFeatures, impassName, cleanupList, timer, logFile)
            
            # mergedWalkFeatures is a list of feature class catalog paths and possible nonsense strings with invalid catalog path characters. 
            # Create a list of just the catalog paths.    
            vectorsToRaster = [fc for fc in mergedImpassFeatures if arcpy.Exists(fc)]
            
            # create the Impassable raster
            impassRaster, cleanupList = raster.getWalkabilityGrid(vectorsToRaster, impassNumber, baseNumber, impassName, cellSize, cleanupList, timer, logFile)
            
            impassRasterPath = arcpy.Describe(impassRaster).catalogPath
            
            # combine the Walkable and Impassable rasters. 
            AddMsg(f"{timer.now()} Stacking the Walkable raster on the Impassable raster for final output.", 0, logFile)
            log.logArcpy('arcpy.sa.Con', (f'({walkRaster} == {baseNumber})', impassRaster, walkRaster), logFile)
            costRaster = arcpy.sa.Con((walkRaster == baseNumber), impassRaster, walkRaster)
            
            categoryDict = {walkNumber: "Walkable", baseNumber: "Base", impassNumber: "Impassable"}
        else:
            impassRasterPath = ''
            AddMsg(f"{timer.now()} Creating a copy of the Walkable raster for the final output.", 0, logFile)
            costRaster = walkRaster
            
            categoryDict = {walkNumber: "Walkable", baseNumber: "Base"}
        
        costRaster.save(outRaster)
        
        # add category labels to the raster
        AddMsg(f"{timer.now()} Finalizing {basename(outRaster)} by adding labels.", 0, logFile)
        log.logArcpy('arcpy.BuildRasterAttributeTable_management', (costRaster, "Overwrite"), logFile)
        arcpy.BuildRasterAttributeTable_management(costRaster, "Overwrite")
        
        log.logArcpy('arcpy.AddField_management', (costRaster, "CATEGORY", "TEXT", "#", "#", "10"), logFile)
        arcpy.AddField_management(costRaster, "CATEGORY", "TEXT", "#", "#", "10")
        
        raster.updateCategoryLabels(costRaster, categoryDict)
        
        if logFile:
            # write the standard environment settings to the log file
            log.writeEnvironments(logFile, snapRaster, cellSizeStr, extentList=[walkRasterPath, impassRasterPath])
            # parameters are: logFile, snapRaster, processingCellSize, extentList
            # if extentList is set to None, the env.extent setting will reported.
            # Place eventList here, if the extents of the datasets have been altered and you wish to use the new extents.
            # for snapRaster and processingCellSize, if the parameter is None, no entry will
            # will be recorded in the log for that parameter
    
    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
    
        errors.standardErrorHandling(e, logFile)
    
    finally:
        setupAndRestore.standardRestore(logFile)
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete")


def proc_park(parkIDStr):
    AddMsg(f"parkIDStr = {parkIDStr}")
    
    
def runPedestrianAccessAndAvailability(toolPath, inParkFeature, dissolveParkYN='', inCostSurface='', inCensusDataset='', inPopField='', 
                               maxTravelDist='', expandAreaDist='', outRaster='', processingCellSize='', snapRaster='', optionalFieldGroups=''):
    """ Interface for script executing Pedestrian Access And Availability tool """
   
    from arcpy import env
    # from multiprocessing import Process, Lock

    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup

    try:
        ### Setup

        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.paaaConstants()

        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inParkFeature, dissolveParkYN, inCostSurface, inCensusDataset, inPopField, maxTravelDist, expandAreaDist, outRaster, processingCellSize, snapRaster, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outRaster, toolPath)
        
        # # create a list of input themes to find the intersection extent
        # # put it here when one of the inputs might be altered (e.g., inReportingUnitFeature, inLandCoverGrid)
        # # but you want the original inputs to be used for the extent intersection
        # if logFile:
        #     extentList = [inParkFeature, inCostSurface, inCensusDataset]
        
        ### Initialization
        # Start the timer
        timer = DateTimer()
        AddMsg(f"{timer.now()} Setting up environment variables", 0, logFile)

        # set up dummy variables to pass to standardSetup in setupAndRestore. SetupAndRestore will set the environmental
        # variables as desired and pass back the optionalGroupsList to use for intermediate products retention.
        # metricsBaseNameList is not used for this tool.
        metricsToRun = 'item1  -  description1;item2  -  description2'

        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize, os.path.dirname(outRaster),
                                                                              [metricsToRun, optionalFieldGroups])  

        if globalConstants.intermediateName in optionalGroupsList:
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))

        # Check if a population field is selected if the inCensusDataset is a polygon feature
        descCensus = arcpy.Describe(inCensusDataset)
        if descCensus.datasetType != "RasterDataset" and inPopField == '':
            raise errors.attilaException(errorConstants.missingFieldError) 
        
        # Do a Describe on the Cost Surface Raster input and get the file's basename.
        descCSR = arcpy.Describe(inCostSurface)
        csrBaseName = descCSR.baseName

        # Check to see if the user has specified a Processing cell size other than the cell size of the inCostSurface
        cellSize = conversion.convertNumStringToNumber(processingCellSize)
        x = cellSize
        y = Raster(inCostSurface).meanCellWidth

        if x%y == 0 or y%x == 0:
            pass
        else:
            AddMsg("The Processing cell size and the input Cost surface raster's cell size are not equal to each other nor are they multiples or factors of each other. "\
                   "To best use the output of this tool with the Walkable Parks Tool, it is highly recommended that the Processing cell size is set "\
                   "as either equal to the Cost surface raster's cell size, a factor of the Snap raster's cell size, or a multiple of the Cost surface raster's cell size.", 1, logFile)

        # if no specific geoprocessing environment extent is set, temporarily set it to match the inCostSurface. It will be reset during the standardRestore
        nonSpecificExtents = ["NONE", "MAXOF", "MINOF"]
        envExtent = str(env.extent).upper()
        if envExtent in nonSpecificExtents:
            AddMsg(f"{timer.now()} Using {csrBaseName}'s extent for geoprocessing steps.", 0, logFile)
            env.extent = descCSR.extent
        else:
            AddMsg(f"{timer.now()} Extent found in Geoprocessing environment settings used for processing.", 0, logFile)

        # if no specific geoprocessing environment outputCoodinateSystem is set, temporarily set it to match the inCostSurface. It will be reset during the standardRestore
        nonSpecificOCS = ["NONE"]
        envOCS = str(env.outputCoordinateSystem).upper()
        if envOCS in nonSpecificOCS:
            outSR = descCSR.spatialReference
            AddMsg(f"{timer.now()} Using {csrBaseName}'s spatial reference for geoprocessing steps: {outSR.name}", 0, logFile)
            env.outputCoordinateSystem = outSR
        else:
            AddMsg(f"{timer.now()} OutputCoordinateSystem found in Geoprocessing environment settings used for processing.", 0, logFile)


        ### Computations
        
        # Create a copy of the park feature class that we can add new fields to for calculations.  This 
        # is more appropriate than altering the user's input data. 
        desc = arcpy.Describe(inParkFeature)
        tempName = f"{metricConst.shortName}_{desc.baseName}_"
        tempParkFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        AddMsg(f"{timer.now()} Creating temporary copy of {desc.name}. Intermediate: {basename(tempParkFeature)}", 0, logFile)
        
        if dissolveParkYN == 'true':
            log.logArcpy('arcpy.Dissolve_management', (inParkFeature, os.path.basename(tempParkFeature),"","","SINGLE_PART", "DISSOLVE_LINES"), logFile)
            inParkFeature = arcpy.Dissolve_management(inParkFeature, os.path.basename(tempParkFeature),"","","SINGLE_PART", "DISSOLVE_LINES")
        else:
            log.logArcpy('arcpy.FeatureClassToFeatureClass_conversion', (inParkFeature, env.workspace, basename(tempParkFeature)), logFile)
            inParkFeature = arcpy.FeatureClassToFeatureClass_conversion(inParkFeature, env.workspace, basename(tempParkFeature))
        
        # use the OID for identifying Parks
        idFlds = [aFld for aFld in arcpy.ListFields(inParkFeature) if aFld.type == "OID"]
        oidFld = idFlds[0].name
        AddMsg(f"{timer.now()} Collecting id values from {oidFld} for each park.", 0, logFile)
        parksDF = pandasutil.fc_to_pd_df(inParkFeature, oidFld)
        parkList = parksDF[oidFld].to_list()
        
        # Calculate the park area in square meters using the coordinate system set in the spatial analysis environment
        AddMsg(f"{timer.now()} Calculating park area in square meters", 0, logFile)
        calcAreaFld = 'CalcAreaM2'
        log.logArcpy("arcpy.management.AddField", (inParkFeature, calcAreaFld, 'FLOAT'), logFile)
        arcpy.management.AddField(inParkFeature, calcAreaFld, 'FLOAT')
        
        exp = "!SHAPE.AREA@SQUAREMETERS!"
        log.logArcpy("arcpy.CalculateField_management", (inParkFeature, calcAreaFld, exp, "PYTHON"), logFile)
        arcpy.CalculateField_management(inParkFeature, calcAreaFld, exp, "PYTHON")
        
        if globalConstants.intermediateName in optionalGroupsList:
            # Add additional fields for population with access counts and square meters of park accessible per person calculation.  
            log.logArcpy("arcpy.management.AddFields", (inParkFeature, metricConst.parkCalculationFields), logFile)
            arcpy.management.AddFields(inParkFeature, metricConst.parkCalculationFields)
        
        # Get a count of the number of reporting units to give an accurate progress estimate.
        n = len(parkList)
        # Initialize custom progress indicator
        loopProgress = messages.loopProgress(n)
        
        AddMsg(f"{timer.now()} Calculating access and availability for {n} areas.", 0, logFile)
        
        per = '[PER UNIT]'
        AddMsg(f"{timer.now()} The following steps will be performed for each park:", 0, logFile)    
        AddMsg("\n---")
        AddMsg(f"{timer.now()} {per} 1) Select park by its ID value and create a feature layer.", 0, logFile)
        AddMsg(f"{timer.now()} {per} 2) Create a buffer around the park extending 5% beyond the maximum travel distance.", 0, logFile)
        AddMsg(f"{timer.now()} {per} 3) Create Cost Distance raster to the Maximum travel distance with the buffer extent as the processing extent.", 0, logFile)
        AddMsg(f"{timer.now()} {per} 4) Designate the accessibility area by setting all cells to 1 for any cell in the Cost Distance raster >= 0.", 0, logFile)
        AddMsg(f"{timer.now()} {per} 5) Expand the accessibility area if indicated by the Expand area served parameter.", 0, logFile)
        AddMsg(f"{timer.now()} {per} 6) Determine Population within accessibility area.", 0, logFile)
        AddMsg(f"{timer.now()} {per}   6a) If Population parameter input is a raster:", 0, logFile)
        AddMsg(f"{timer.now()} {per}     a1) Set the geoprocessing snap raster and processing cell size environments to the population raster.", 0, logFile) 
        AddMsg(f"{timer.now()} {per}     a2) Use Zonal Statistics As Table with the SUM option to calculate the accessibility area population.", 0, logFile)
        AddMsg(f"{timer.now()} {per}   6b) If Population parameter input is a polygon feature:", 0, logFile)
        AddMsg(f"{timer.now()} {per}     b1) Convert the accessibility area raster to a polygon.", 0, logFile)
        AddMsg(f"{timer.now()} {per}     b2) Use Tabulate Intersection with this polygon and the Population polygons to calculate the accessibility area population.", 0, logFile)
        AddMsg(f"{timer.now()} {per} 7) Determine Availability (Cost distance value to park area divided by surrounding population)", 0, logFile)
        AddMsg("---\n")
        AddMsg(f"{timer.now()} Starting calculations per park...", 0, logFile)
        
        # Create a list to keep track of any park that did not rasterize
        nullRaster = []
    
        # Create a list to keep track of any park where the surrounding population is none
        popNone = []
    
        # Create a list to keep track of any park where the surrounding population is 0
        popZero = []
        
        # Create a list to keep track of the calculated park/population rasters to mosaic
        mosaicRasters = []
        
        # create an Accessibility and Availability dictionary to capture the calculated values for each park
        aaaDict = {}
        
        for parkID in parkList:
            try:
                # # # lock = Lock()
                # # # p = Process(target=proc_park, args=(str(parkID)))
                # # # p.start()
                # # #
                # # # p.join()
                
                distNumber = conversion.convertNumStringToNumber(maxTravelDist)
                expandNumber = conversion.convertNumStringToNumber(expandAreaDist)
                buffDist = distNumber * 1.05
                
                parkRaster, nullRaster, popNone, popZero, valuesList = raster.getParkRaster(metricConst,
                                                                                inParkFeature,
                                                                                oidFld,
                                                                                str(parkID),
                                                                                buffDist,
                                                                                inCostSurface,
                                                                                distNumber,
                                                                                expandNumber,
                                                                                calcAreaFld,
                                                                                inCensusDataset,
                                                                                inPopField,
                                                                                nullRaster,
                                                                                popNone,
                                                                                popZero,
                                                                                cleanupList)
                
                # add the park raster to the mosaic rasters list
                if parkRaster == None:
                    pass
                else:
                    mosaicRasters.append(parkRaster)
                                             
                if globalConstants.intermediateName in optionalGroupsList:
                    # add the accessibility and access calculations to the dictionary for future use
                    aaaDict[parkID] = valuesList
                
                loopProgress.update()
                
            except:
                AddMsg(f"Failed while processing Park ID: {parkID}", 2)
                
        AddMsg(f"{timer.now()} Finished calculations for last park.", 0, logFile)
        
        if globalConstants.intermediateName in optionalGroupsList:
        # create the cursor to add data to the output table
            outTableRows = arcpy.UpdateCursor(inParkFeature)        
            outTableRow = outTableRows.next()
            while outTableRow:
                uid = outTableRow.getValue(oidFld)
                # add the population with access and the square meters available per person values to the copied parks features
                if (uid in aaaDict):
                    outTableRow.setValue(metricConst.calcFieldNames[0], aaaDict[uid][0])
                    outTableRow.setValue(metricConst.calcFieldNames[1], aaaDict[uid][1])
                else:
                    AddMsg("Park ID not found.")
                    
                # commit the row to the output table
                outTableRows.updateRow(outTableRow)
                outTableRow = outTableRows.next()
                
            try:
                del outTableRows
                del outTableRow
            except:
                pass
        
        
        # mosaic the produced park/populations rasters
        if len(mosaicRasters) == 0:
            # check for spaces in directory path
            thisPath = os.getcwd()
            if " " in thisPath:
                AddMsg(f"\nNo individual park population access rasters were generated.", 1, logFile)
                AddMsg(f"This error can occur when the ATtILA toolbox is located in a folder with spaces in its directory path.",1,logFile)
                AddMsg(f'Current ATtILA installation directory: {thisPath.split("ToolboxSource")[0]}',1,logFile)
                AddMsg(f"Exiting...\n", 1, logFile)
            else:
                AddMsg(f"\nNo individual park population access rasters were generated. Exiting...\n", 1, logFile)
        else:
            AddMsg(f"{timer.now()} Merging {(len(mosaicRasters))} calculated park/population rasters. Output: {basename(outRaster)}.", 0, logFile)
            outWS = env.workspace
            arcpy.management.MosaicToNewRaster(mosaicRasters, outWS, basename(outRaster), "#", "64_BIT", env.cellSize, 1, "SUM", "FIRST")   
            
            AddMsg(f"{timer.now()} Deleting {len(mosaicRasters)} individual park rasters.", 0, logFile)
            [arcpy.Delete_management(p) for p in mosaicRasters]
            AddMsg(f"{timer.now()} Individual park rasters deletion complete\n", 0, logFile)   
        
        # report anomalies to the user
        if len(nullRaster) > 0:
            AddMsg(f"Number of areas which did not rasterize: {len(nullRaster)}", 1, logFile)
            AddMsg("  Ids for these areas can be found in the log file if the LOGFILE Additional option was selected.", 1)
            if logFile:
                logFile.write(f"    Non-rasterized Area Ids: {str(nullRaster)}\n\n")
        
        if len(popNone) > 0:
            AddMsg(f"Number of areas where the surrounding population is none: {len(popNone)}", 1, logFile)
            AddMsg("  Ids for these areas can be found in the log file if the LOGFILE Additional option was selected.", 1)
            if logFile:
                logFile.write(f"    Population NONE Area Ids: {str(popNone)}\n\n")
        
        if len(popZero) > 0:    
            AddMsg(f"Number of areas where the surrounding population is zero: {len(popZero)}", 1, logFile)
            AddMsg("  Ids for these areas can be found in the log file if the LOGFILE Additional option was selected.", 1)
            if logFile:
                logFile.write(f"    Population ZERO Area Ids: {str(popZero)}\n\n")
        
        if logFile:
            # write the standard environment settings to the log file
            
            # The analysis extent and coordinate system is set to the cost raster if these environments are not set.
            # Intersecting the inCostSurface extent with the inCensusDataset will show the minimum area of overlap
            log.writeEnvironments(logFile, snapRaster, processingCellSize, extentList = [inCostSurface, inCensusDataset])
            # parameters are: logFile, snapRaster, processingCellSize, extentList
            # if extentList is set to None, the env.extent setting will reported.
            # Place eventList here, if the extents of the datasets have been altered and you wish to use the new extents.
            # for snapRaster and processingCellSize, if the parameter is None, no entry will
            # will be recorded in the log for that parameter

    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())

        errors.standardErrorHandling(e, logFile)

    finally:
        arcpy.Delete_management("in_memory")
        
        setupAndRestore.standardRestore(logFile)
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete")


def runProcessRoadsForEnvioAtlasAnalyses(toolPath, versionName, inStreetsgdb, chkWalkableYN, chkIntDensYN, chkIACYN, chkAllRdsYN, outWorkspace, fnPrefix, optionalFieldGroups):
    """ Process Roads for EnviroAtlas Analyses
    
        This script is associated with an ArcToolbox script tool.
    """

    from arcpy import env
    
    addToActiveMap = [] # set up a list for feature class names to add to the ArcGIS Project's TOC
    
    #Script arguments
    try:
        ### Initialization
        # Start the timer
        timer = DateTimer()
        
        # Save the current environment settings to restore at the end of the script
        _tempEnvironment0 = env.parallelProcessingFactor
        _tempEnvironment1 = env.workspace
        _tempEnvironment2 = env.overwriteOutput
        
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.prfeaConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, versionName, inStreetsgdb, chkWalkableYN, chkIntDensYN, chkIACYN, chkAllRdsYN, outWorkspace, fnPrefix, optionalFieldGroups] #check this last one with logfile in the tool
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outWorkspace+"\\"+fnPrefix, toolPath) #toolPath?
        
        # set up a list to keep track of intermediate products that can be deleted/saved at the end of the tool operation
        intermediateList = []
        
        # checks to see if the geodatabase has the required datasets.
        requiredLayers = metricConst.requiredDict[versionName]
        for fc in requiredLayers:
            filename = f"{inStreetsgdb}{fc}"
            if arcpy.Exists(filename) == False:
                # inform the user what is wrong then kill the operation
                AddMsg(f"Required input, {fc}, was not found in {inStreetsgdb}. Aborting...", 2)
                raise errors.attilaException(errorConstants.missingRoadsError) 
            else:
                if chkIntDensYN == "true":
                    # check for projection
                    descFC = arcpy.Describe(filename)
                    sr = descFC.spatialReference
                    if sr.type != "Projected":
                        AddMsg(f"Required input, {fc}, is not in a projected coordinate system. All inputs for Intersection Density Roads need to be in a projected coordinate system. Aborting...", 2)
                        raise errors.attilaException(errorConstants.unprojectedRoadsError)
        
        # determine the active map to add the output raster/features    
        try:
            currentProject = arcpy.mp.ArcGISProject("CURRENT")
            actvMap = currentProject.activeMap
        except:
            actvMap = None

        # Set the environmental variables to desired condition 
        AddMsg(f"{timer.now()} Setting up initial environment variables", 0, logFile)
        
        # Until the Pairwise geoprocessing tools can be incorporated into ATtILA, disable the Parallel Processing Factor if the environment is set
        currentFactor = str(env.parallelProcessingFactor)
        if currentFactor == 'None' or currentFactor == '0':
            pass
        else:
            arcpy.AddWarning("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.")
            env.parallelProcessingFactor = None
        
        env.overwriteOutput = True
        env.workspace = outWorkspace

        # setup additional metric constants
        ext = files.checkOutputType(outWorkspace) # determine if '.shp' needs to be added to outputs 
        
        inputStreets = f"{inStreetsgdb}\\Streets"
        singlepartRoads = "singlepartRoads"+ext
        keepFields = [f.name for f in arcpy.ListFields(inputStreets)]
        newFields = ["FEATURE_TYPE", "FEAT_TYPE", "MergeClass", "LANES"]
        keepFields.extend(newFields)
        intersectFinal = "intersectFinal"+ext

        #NAVTEQ 2011 Options 
        NAVTEQ_LandUseA = inStreetsgdb + "\\LandUseA"       
        intersectFromLandUseA = "intersectFromLandUseA"+ext
        NAVTEQ_LandUseB = inStreetsgdb + "\\LandUseB"
        
        #NAVTEQ 2019 Options
        NAVTEQLandArea = inStreetsgdb + "\\MapLanduseArea"
        NAVTEQFacilityArea = inStreetsgdb + "\\MapFacilityArea"
        link = inStreetsgdb + "\\Link"
        intersectFromLandArea = "intersectFromLandUse"+ext
        
        #StreetMapOptions
        SMLandArea = inStreetsgdb + "\\MapLandArea\\MapLandArea"
        
        # Begin process by making a feature layer from the Streets feature class
        AddMsg(f"{timer.now()} Creating feature layer from {inputStreets}.", 0, logFile)
        streetLayer = "streetLayer"
        log.logArcpy('arcpy.MakeFeatureLayer_management', (inputStreets, streetLayer), logFile, True)
        arcpy.MakeFeatureLayer_management(inputStreets, streetLayer)

        
        if chkWalkableYN == "true" or chkIntDensYN == "true":
            if chkWalkableYN == "true":
                AddMsg(f"{timer.now()} Processing walkable roads.", 0, logFile)
            else:
                AddMsg(f"{timer.now()} Processing roads for intersection density analysis.", 0, logFile)
            
            whereClause = metricConst.walkSelectDict[versionName]
            WlkMsg = metricConst.walkMsgDict[versionName]
                
            # OLD NAVTEQ SELECTION FOR ENVIROATLAS
            # AddMsg("From "+inputStreets+"...")
            # AddMsg("...selecting features where FUNC_CLASS <> 1 or 2")
            # arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', 
            #                                         "FUNC_CLASS NOT IN ('1','2')")
            # AddMsg("...removing from the selection features where FERRY_TYPE <> H")
            # arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', 
            #                                         "FERRY_TYPE <> 'H'")
            # AddMsg("...removing from the selection features where SPEED_CAT = 1, 2, or 3")
            # arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', 
            #                                         "SPEED_CAT IN ('1', '2', '3')")
            # AddMsg("...removing from the selection features where AR_PEDEST = N")
            # arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', 
            #                                         "AR_PEDEST = 'N'")
            
                
            log.logArcpy('arcpy.SelectLayerByAttribute_management', (streetLayer, 'NEW_SELECTION', whereClause, "INVERT"), logFile)
            arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', whereClause, "INVERT")
            
            AddMsg(f"{timer.now()} {WlkMsg}", 0, logFile)

            if chkWalkableYN == "true":
                walkableFCName = fnPrefix+metricConst.outNameRoadsWalkable+ext
                AddMsg(f"{timer.now()} Saving selected features to: {walkableFCName}", 0, logFile)
                log.logArcpy('arcpy.CopyFeatures_management', (streetLayer, walkableFCName), logFile)
                walkableFC = arcpy.CopyFeatures_management(streetLayer, walkableFCName)
                
                addToActiveMap.append(walkableFC)
                

        if chkIntDensYN == "true":
            # get the output feature class name
            intDensityFCName = fnPrefix+metricConst.outNameRoadsIntDens+ext
            mergeField = "MergeClass"
            
            if chkWalkableYN == "true":
                AddMsg(f"{timer.now()} Continuing with the selected features for processing intersection density roads.", 0, logFile)
        
            AddMsg(f"{timer.now()} Removing from the selection features where {metricConst.speedCatDict[versionName]}.", 0, logFile)
            log.logArcpy('arcpy.SelectLayerByAttribute_management', (streetLayer, 'REMOVE_FROM_SELECTION', metricConst.speedCatDict[versionName]), logFile)
            arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', metricConst.speedCatDict[versionName])
            
            if versionName == 'NAVTEQ 2011': #NAVTEQ 2011
                AddMsg(f"{timer.now()} Assigning landUseA codes to road segments.", 0, logFile)
                log.logArcpy('arcpy.Identity_analysis', (streetLayer, NAVTEQ_LandUseA, intersectFromLandUseA), logFile)
                arcpy.Identity_analysis(streetLayer, NAVTEQ_LandUseA, intersectFromLandUseA)
                
                intermediateList.append(intersectFromLandUseA)

                AddMsg(f"{timer.now()} Assigning landUseB codes to road segments.", 0, logFile)           
                log.logArcpy('arcpy.Identity_analysis', (intersectFromLandUseA, NAVTEQ_LandUseB, intersectFinal), logFile)
                arcpy.Identity_analysis(intersectFromLandUseA, NAVTEQ_LandUseB, intersectFinal)
                
                intermediateList.append(intersectFinal)

                if ext == ".shp":
                    # fieldname size restrictions with shapefiles cause FEAT_TYPE_1 to be truncated to FEAT_TYP_1 
                    relevantFlds = ['FEAT_TYPE', 'FEAT_TYP_1']
                else:
                    relevantFlds = ['FEAT_TYPE', 'FEAT_TYPE_1']

                sql = f"{relevantFlds[0]} = '' And {relevantFlds[1]} <> ''"

                #Transfer all meaningful values from field FEAT_TYPE_1 to FEAT_TYPE
                AddMsg(f"{timer.now()} Transferring values from {relevantFlds[1]} to {relevantFlds[0]}.", 0, logFile)
                with arcpy.da.UpdateCursor(intersectFinal,relevantFlds,sql) as cursor:
                    for row in cursor:
                        row[0] = row[1]
                        cursor.updateRow(row)
                
            elif versionName == 'NAVTEQ 2019':  #NAVTEQ 2019
                AddMsg(f"{timer.now()} Assigning landArea codes to road segments.",0,logFile)
                log.logArcpy('arcpy.Identity_analysis', (streetLayer, NAVTEQLandArea, intersectFromLandArea), logFile)
                arcpy.Identity_analysis(streetLayer, NAVTEQLandArea, intersectFromLandArea)
                
                intermediateList.append(intersectFromLandArea)

                AddMsg(f"{timer.now()} Assigning FacilityArea codes to road segments.",0,logFile)           
                log.logArcpy('arcpy.Identity_analysis', (intersectFromLandArea, NAVTEQFacilityArea, intersectFinal), logFile)
                arcpy.Identity_analysis(intersectFromLandArea, NAVTEQFacilityArea, intersectFinal)
                
                intermediateList.append(intersectFinal)

                if ext == ".shp":
                    # fieldname size restrictions with shapefiles cause FEAT_TYPE_1 to be truncated to FEAT_TYP_1 
                    relevantFlds = ['FEATURE_TY', 'FEATURE__1']
                else:
                    relevantFlds = ['FEATURE_TYPE', 'FEATURE_TYPE_1']
                    
                sql = f"{relevantFlds[0]} = 0 And {relevantFlds[1]} <> 0"

                #Transfer all meaningful values from field FEAT_TYPE_1 to FEAT_TYPE
                AddMsg(f"{timer.now()} Transferring values from {relevantFlds[1]} to {relevantFlds[0]}.", 0, logFile)
                with arcpy.da.UpdateCursor(intersectFinal, relevantFlds, sql) as cursor:
                    for row in cursor:
                        row[0] = row[1]
                        cursor.updateRow(row)
            
            elif versionName == 'ESRI StreetMap': # ESRI StreetMaps
                AddMsg(f"{timer.now()} Assigning MapLandArea codes to road segments.",0,logFile)
                log.logArcpy('arcpy.Identity_analysis', (streetLayer, SMLandArea, intersectFinal), logFile)
                arcpy.Identity_analysis(streetLayer, SMLandArea, intersectFinal)
                
                intermediateList.append(intersectFinal)

            # dropFields = [f.name for f in arcpy.ListFields(intersectFinal) if f.name not in keepFields]
            # AddMsg(f"{timer.now()} Trimming unnecessary fields",0,logFile)
            # arcpy.DeleteField_management(intersectFinal, dropFields)  #THIS SET OF CODE SLOWS THINGS DOWN A LOT

            AddMsg(f"{timer.now()} Removing roads with no street names from the following land use type areas: AIRPORT, AMUSEMENT PARK, BEACH, CEMETERY, HOSPITAL, INDUSTRIAL COMPLEX, MILITARY BASE, RAILYARD, SHOPPING CENTER, and GOLF COURSE.", 0, logFile)
            unnamedStreetsSQL = metricConst.unnamedStreetsDict[f"{versionName}{ext}"]

            with arcpy.da.UpdateCursor(intersectFinal, ["*"], unnamedStreetsSQL) as cursor:
                for row in cursor:
                    cursor.deleteRow()
            
            AddMsg(f"{timer.now()} Adding a MergeClass field.",0,logFile)
            log.logArcpy('arcpy.AddField_management', (intersectFinal,mergeField,"SHORT"), logFile)
            arcpy.AddField_management(intersectFinal,mergeField,"SHORT")
        
            AddMsg(f"{timer.now()} Setting MergeClass to an initial value of 1.", 0, logFile)
            log.logArcpy('arcpy.CalculateField_management', (intersectFinal,mergeField,1), logFile)
            arcpy.CalculateField_management(intersectFinal,mergeField,1)
            
            dirTravelSQL = metricConst.dirTravelDict[versionName]
            dirTravelFld = dirTravelSQL.split(' = ')[0]
            AddMsg(f"{timer.now()} Replacing MergeClass value to 0 for rows where {dirTravelFld} = 'B'.", 0, logFile)
            with arcpy.da.UpdateCursor(intersectFinal, [mergeField], dirTravelSQL) as cursor:
                for row in cursor:
                    row[0] = 0
                    cursor.updateRow(row)
        
            AddMsg(f"{timer.now()} Converting any multipart roads to singlepart.", 0, logFile)
            # Ensure the road feature class is comprised of singleparts. Multipart features will cause MergeDividedRoads to fail.
            log.logArcpy('arcpy.MultipartToSinglepart_management', (intersectFinal, singlepartRoads), logFile)
            arcpy.MultipartToSinglepart_management(intersectFinal, singlepartRoads)
            
            intermediateList.append(singlepartRoads)
            AddMsg(f"{timer.now()} Merging divided roads to {intDensityFCName} using the MergeClass field and a merge distance of '30 Meters'. Only roads with the same value in the mergeField and within the mergeDistance will be merged. Roads with a MergeClass value equal to zero are locked and will not be merged. All non-merged roads are retained.", 0, logFile)
            
            log.logArcpy('arcpy.MergeDividedRoads_cartography', (singlepartRoads, mergeField, "30 Meters", intDensityFCName), logFile)
            intDensityFC = arcpy.MergeDividedRoads_cartography(singlepartRoads, mergeField, "30 Meters", intDensityFCName)
                                
            AddMsg(f"{timer.now()} Finished processing {intDensityFCName}.", 0, logFile)
            addToActiveMap.append(intDensityFC)
            

        if chkIACYN == "true":
            AddMsg(f"{timer.now()} Processing interstates, arterials, and connectors.", 0, logFile)
            # get the name for the output feature class
            iacFCName = f"{fnPrefix}{metricConst.outNameRoadsIAC}{ext}"
            lanesField = "LANES"
            ToFromFields = metricConst.laneFieldDict[versionName]
            
            if chkWalkableYN == "true" or chkIntDensYN == "true":
                # this is probably unnecessary, but it makes sure everything is reset
                AddMsg(f"{timer.now()} Clearing and resetting selections for {inputStreets}.")
                log.logArcpy('arcpy.SelectLayerByAttribute_management', (streetLayer, 'CLEAR_SELECTION'), logFile)
                arcpy.SelectLayerByAttribute_management(streetLayer, 'CLEAR_SELECTION')

            if versionName == 'NAVTEQ 2011':
                AddMsg(f"{timer.now()} Selecting features where FUNC_CLASS = 1, 2, 3, or 4.",0,logFile)
                log.logArcpy('arcpy.SelectLayerByAttribute_management', (streetLayer, 'NEW_SELECTION', "FUNC_CLASS IN ('1','2','3','4')"), logFile)
                arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', "FUNC_CLASS IN ('1','2','3','4')")
                
                AddMsg(f"{timer.now()} Removing from the selection features where FERRY_TYPE <> H.",0,logFile)
                log.logArcpy('arcpy.SelectLayerByAttribute_management', (streetLayer, 'REMOVE_FROM_SELECTION', "FERRY_TYPE <> 'H'"), logFile)
                arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', "FERRY_TYPE <> 'H'")
                
            elif versionName == 'NAVTEQ 2019': #NAVTEQ2019 #(pickup updating messages here) 
                #try running the join first
                AddMsg(f"{timer.now()} Adding {ToFromFields[0]} and {ToFromFields[1]} from {link}.", 0, logFile)
                log.logArcpy('arcpy.management.AddJoin', (streetLayer, metricConst.Streets_linkfield, link, metricConst.Link_linkfield), logFile)
                arcpy.management.AddJoin(streetLayer, metricConst.Streets_linkfield, link, metricConst.Link_linkfield)
                
                AddMsg(f"{timer.now()} Selecting features where FuncClass = 1, 2, 3, or 4.", 0, logFile)
                log.logArcpy('arcpy.SelectLayerByAttribute_management', (streetLayer, 'NEW_SELECTION', "FuncClass <= 4"), logFile)
                arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', "FuncClass <= 4")
                
                AddMsg(f"{timer.now()} Removing from the selection features where FERRY_TYPE <> H.", 0, logFile)
                log.logArcpy('arcpy.SelectLayerByAttribute_management', (streetLayer, 'REMOVE_FROM_SELECTION', "FerryType <> 'H'"), logFile)
                arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', "FerryType <> 'H'")
            
            elif versionName == 'ESRI StreetMap': # ESRI StreetMaps
                AddMsg(f"{timer.now()} Selecting features where FuncClass = 1, 2, 3, or 4.", 0, logFile)
                log.logArcpy('arcpy.SelectLayerByAttribute_management', (streetLayer, 'NEW_SELECTION', "FuncClass <= 4"), logFile)
                arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', "FuncClass <= 4")
                
                AddMsg(f"{timer.now()} Removing from the selection features where FERRY_TYPE <> H.", 0, logFile)
                log.logArcpy('arcpy.SelectLayerByAttribute_management', (streetLayer, 'REMOVE_FROM_SELECTION', "FerryType <> 'H'"), logFile)
                arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', "FerryType <> 'H'")
            
            # Write the selected features to a new feature class
            AddMsg(f"{timer.now()} Exporting remaining selected features to {iacFCName}", 0, logFile)
            log.logArcpy('arcpy.conversion.ExportFeatures', (streetLayer, iacFCName), logFile)
            iacFC = arcpy.conversion.ExportFeatures(streetLayer, iacFCName)    
                
            # need to reset the ToFromFields in case the iacFC is a shapefile
            ToFromFields = metricConst.laneFieldDict[f"{versionName}{ext}"]
        
            for f in ToFromFields:
                AddMsg(f"{timer.now()} Setting NULL values in {f} field to 0.", 0, logFile)
                calculate.replaceNullValues(iacFC, f, 0)
            
            AddMsg(f"{timer.now()} Adding field, LANES, to {iacFCName}. Calculating its value as {ToFromFields[0]} + {ToFromFields[1]}.", 0, logFile)
            log.logArcpy('arcpy.AddField_management', (iacFC,lanesField,"SHORT"), logFile)
            arcpy.AddField_management(iacFC,lanesField,"SHORT")
            
            calcExpression = f"!{ToFromFields[0]}!+!{ToFromFields[1]}!"
            log.logArcpy('arcpy.CalculateField_management', (iacFC,lanesField,calcExpression,"PYTHON",'#'), logFile)
            arcpy.CalculateField_management(iacFC,lanesField,calcExpression,"PYTHON",'#')
                
            #inform the user the total number of features having LANES of value 0
            value0FCName = metricConst.value0_LANES+ext
            whereClause_0Lanes = f"{lanesField} = 0"
            log.logArcpy('arcpy.Select_analysis', (iacFC, value0FCName, whereClause_0Lanes), logFile)
            arcpy.Select_analysis(iacFC, value0FCName, whereClause_0Lanes)
            
            zeroCount = arcpy.GetCount_management(value0FCName).getOutput(0)
            if int(zeroCount) > 0:
                AddMsg(f'{timer.now()} Total number of records where LANES = 0 in {iacFCName} is: {zeroCount}.', 1, logFile)
                AddMsg(f'{timer.now()} Replacing LANES field value to 2 for these records. The user can locate and change these records with the following query: {ToFromFields[0]} = 0 And {ToFromFields[1]} = 0.', 1, logFile)
                
                #Change the LANES value to 2 where LANES = 0
                sql4 = "LANES = 0"
                with arcpy.da.UpdateCursor(iacFC, [lanesField], sql4) as cursor:
                    for row in cursor:
                        row[0] = 2
                        cursor.updateRow(row)
                        
            AddMsg(f"{timer.now()} Finished processing {iacFCName}.", 0, logFile)
                        
            intermediateList.append(value0FCName)
            addToActiveMap.append(iacFC)
        
        
        if chkAllRdsYN == "true":
            AddMsg(f"{timer.now()} Processing all roads.", 0, logFile)
            AllRdsFCName = f"{fnPrefix}{metricConst.outNameRoadsAllRds}{ext}"

            if chkWalkableYN == "true" or chkIntDensYN == "true" or chkIACYN == "true":
            # this is probably unnecessary, but it makes sure everything is reset
                AddMsg(f"{timer.now()} Clearing and resetting selections for {inputStreets}.")
                log.logArcpy('arcpy.SelectLayerByAttribute_management', (streetLayer, 'CLEAR_SELECTION'), logFile)
                arcpy.SelectLayerByAttribute_management(streetLayer, 'CLEAR_SELECTION')

            whereClause = metricConst.AllRdsSelectDict[versionName]
            AllRdsMsg = metricConst.AllRdsMsgDict[versionName]

                
            log.logArcpy('arcpy.SelectLayerByAttribute_management', (streetLayer, 'NEW_SELECTION', whereClause, "INVERT"), logFile)
            arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', whereClause, "INVERT")
            AddMsg(f"{timer.now()} {AllRdsMsg}", 0, logFile)

            AddMsg(f"{timer.now()} Saving selected features to: {AllRdsFCName}", 0, logFile)
            log.logArcpy('arcpy.CopyFeatures_management', (streetLayer, AllRdsFCName), logFile)
            AllRdsFC = arcpy.CopyFeatures_management(streetLayer, AllRdsFCName)
            addToActiveMap.append(AllRdsFC)
            
        if logFile:
            log.writeEnvironments(logFile, None, None, extentList=[inputStreets])
        
        try:
            # add outputs to the active map
            if actvMap != None:
                # AddMsg(f"Adding output(s) to {actvMap.name} view")
                for aFeature in addToActiveMap:
                    actvMap.addDataFromPath(aFeature)
                    AddMsg(f"Adding {arcpy.Describe(aFeature).name} to {actvMap.name} view.")
        
        except:
            AddMsg(f"Unable to add processed layer(s) to {actvMap.name} view.")

    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
            
        errors.standardErrorHandling(e, logFile)
 
    finally:

        if logFile:
            logFile.write(f"\nEnded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            logFile.write("\n---End of Log File---\n")
            logFile.close()
            AddMsg('Log file closed')
        
        if intermediateList:
            [arcpy.Delete_management(i) for i in intermediateList]
                

        env.parallelProcessingFactor = _tempEnvironment0
        env.workspace = _tempEnvironment1
        env.overwriteOutput = _tempEnvironment2


def runPopulationWithinZoneMetrics(toolPath, inReportingUnitFeature, reportingUnitIdField, inCensusDataset, inPopField='', 
                             inZoneDataset='', inBufferDistance='', groupByZoneYN='', zoneIdField='', outTable='', optionalFieldGroups=''):
    """ Interface for script executing Population within Zone Metrics tool """

    from arcpy import env
    
    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    
    try:
        ### Setup
    
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.pwzmConstants()
    
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inReportingUnitFeature, reportingUnitIdField, inCensusDataset, inPopField, 
                          inZoneDataset, inBufferDistance, groupByZoneYN, zoneIdField, outTable, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
            
        ### Initialization
        # Start the timer
        timer = DateTimer()
        AddMsg(f"{timer.now()} Setting up environment variables", 0, logFile)
        
        if arcpy.glob.os.path.basename(arcpy.sys.executable) == globalConstants.arcExecutable:
            _tempEnvironment0 = env.snapRaster
            _tempEnvironment1 = env.workspace
            _tempEnvironment2 = env.cellSize
            _tempEnvironment6 = env.parallelProcessingFactor
        
        # Until the Pairwise geoprocessing tools can be incorporated into ATtILA, disable the Parallel Processing Factor if the environment is set
        currentFactor = str(env.parallelProcessingFactor)
        if currentFactor == 'None' or currentFactor == '0':
            pass
        else:
            # Advise the user that results when using parallel processing may be different from results obtained without its use.
            AddMsg("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.", 1, logFile)
            env.parallelProcessingFactor = None
        
        # set the workspace for ATtILA intermediary files
        env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))
        
        # Strip the description from the "additional option" and determine whether intermediates are stored.
        processed = parameters.splitItemsAndStripDescriptions(optionalFieldGroups, globalConstants.descriptionDelim)
        if globalConstants.intermediateName in processed:
            msg = "\nIntermediates are stored in this directory: {0}\n"
            AddMsg(msg.format(env.workspace), 0, logFile)
        
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
        
        # retrieve the attribute constants associated with this metric
        popCntFields = metricConst.populationCountFieldNames

        # Do a Describe on the population and zone inputs. Determine if they are raster or polygon
        descCensus = arcpy.Describe(inCensusDataset)
        descZone = arcpy.Describe(inZoneDataset)   
        
        # Check if a population field is selected if the inCensusDataset is a polygon feature
        descCensus = arcpy.Describe(inCensusDataset)
        if descCensus.datasetType != "RasterDataset" and inPopField == '':
            raise errors.attilaException(errorConstants.missingFieldError) 
        
        fileNameBase = descZone.baseName
        
        # Create an index value to keep track of intermediate outputs and field names.
        index = 0
        
        # if Group by zone is checked, see if zoneIdField is empty. turn off the Group by zone option if it is.
        if groupByZoneYN == "true":
            fieldIsEmpty = fields.checkForEmptyField(inZoneDataset, zoneIdField)
            if fieldIsEmpty:
                # raise errors.attilaException(errorConstants.emptyFieldError)
                groupByZoneYN = "false"
                AddMsg("The Zone ID field contains only NULL values or whitespace. The Group by zone option can not be performed.", 2, logFile)
                raise errors.attilaException(errorConstants.emptyFieldError)     
    
        ### Is there an optional buffer
        bufferDistanceVal = float(inBufferDistance.split()[0])
        
        if descZone.datasetType == "RasterDataset":
            if bufferDistanceVal > 0:
                AddMsg("Buffering raster zone datasets is not currently supported. Buffer distance has been set to 0.", 1, logFile)
            bufferDistanceVal = 0
        
        elif bufferDistanceVal == 0:
            pass # no need to create a copy; not altering the input feature class or its attribute table.
            
            # fieldMappings = arcpy.FieldMappings()
            # fieldMappings.addTable(inZoneDataset)
            # zoneFields = [fieldMappings.fields[0].name]
            # if groupByZoneYN == "true":
            #     zoneFields.append(zoneIdField)
            #
            # [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name not in zoneFields]
            #
            # tempName = f"{metricConst.shortName}_{descZone.baseName}_Work_"
            # tempZoneinFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
            #
            # AddMsg(f"{timer.now()} Creating a working copy of {descZone.baseName}. Intermediate: {basename(tempZoneinFeature)}", 0, logFile)
            # log.logArcpy(arcpy.FeatureClassToFeatureClass_conversion, (inZoneDataset, env.workspace, basename(tempZoneinFeature), '', fieldMappings), 'arcpy.FeatureClassToFeatureClass_conversion', logFile)
            #
            # inZoneDataset = tempZoneinFeature
        
        else:
            # Change the buffer distance to an integer if appropriate. This reduces the output field name string length by eliminating '_0'.
            if bufferDistanceVal.is_integer():
                bufferDistanceVal = int(bufferDistanceVal)
                
            tempBufferName = f"{metricConst.shortName}_{fileNameBase}_Buffer_"
            tempBufferFeature = files.nameIntermediateFile([tempBufferName,"FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Adding {inBufferDistance} buffer to {descZone.baseName}. Intermediate: {basename(tempBufferFeature)}", 0, logFile)
            log.logArcpy('arcpy.Buffer_analysis', (inZoneDataset, tempBufferFeature, inBufferDistance), logFile)
            arcpy.Buffer_analysis(inZoneDataset, tempBufferFeature, inBufferDistance)
        
            inZoneDataset = tempBufferFeature
        
    
        # Generate name for reporting unit population count table.
        popTable_RU = files.nameIntermediateFile([metricConst.popCntTableName,'Dataset'],cleanupList)
        
        ### Metric Calculation
                
        # tool gui does not have a snapRaster parameter. When the census dataset is a raster, the snapRaster will
        # be set to the census raster. To record this correctly in the log file, set up the snapRaster variable.
        snapRaster = None
        processingCellSize = None
        
        ## if census data are a raster
        if descCensus.datasetType == "RasterDataset":
            AddMsg(f"{timer.now()} Setting the environment snap raster and processing cell size to match {basename(inCensusDataset)}.", 0, logFile)
            # set the raster environments so the raster operations align with the census grid cell boundaries
            env.snapRaster = inCensusDataset
            env.cellSize = descCensus.meanCellWidth
            
            # setting variables so they can be reported in the log file
            snapRaster = inCensusDataset
            processingCellSize = str(descCensus.meanCellWidth)
        
            # calculate the population for the reporting unit using zonal statistics as table
            AddMsg(f"{timer.now()} Calculating population within each reporting unit. Intermediate: {basename(popTable_RU)}", 0, logFile)        
            log.logArcpy('arcpy.sa.ZonalStatisticsAsTable', (inReportingUnitFeature, reportingUnitIdField, inCensusDataset, popTable_RU, "DATA", "SUM"), logFile)
            arcpy.sa.ZonalStatisticsAsTable(inReportingUnitFeature, reportingUnitIdField, inCensusDataset, popTable_RU, "DATA", "SUM")
        
            # Rename the population count field.
            outPopField = metricConst.populationCountFieldNames[index]
            log.logArcpy('arcpy.AlterField_management', (popTable_RU, "SUM", outPopField, outPopField), logFile)
            arcpy.AlterField_management(popTable_RU, "SUM", outPopField, outPopField)
        
            # Set variables for the zone population calculations
            index = 1
            popTable_ZN = files.nameIntermediateFile([metricConst.popCntTableName,'Dataset'],cleanupList)
            
            AddMsg(f"{timer.now()} Preparing for zonal population calculations.", 0, logFile)
            ## if zone data are raster and groupByZoneYN is True then we convert zones to polygon
            if descZone.datasetType == "RasterDataset" and groupByZoneYN == 'true':
                
                # Convert the Raster zones to Polygon
                AddMsg(f"{timer.now()} Setting 0 value cells in {descZone.basename} to NoData.", 0, logFile)
                delimitedVALUE = arcpy.AddFieldDelimiters(inZoneDataset,"VALUE")
                whereClause = f"{delimitedVALUE} = 0"
                log.logArcpy('arcpy.sa.SetNull', (inZoneDataset, inZoneDataset, whereClause), logFile)
                nullGrid = arcpy.sa.SetNull(inZoneDataset, inZoneDataset, whereClause)
                
                tempName = f"{metricConst.shortName}_{descZone.baseName}_Poly_"
                tempPolygonFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
                
                # This may fail if a polygon created is too large. Need a routine to more elegantly reduce the maxVertices in any one polygon
                maxVertices = 250000
                AddMsg(f"{timer.now()} Converting non-zero cells in {descZone.basename} to a polygon feature. Intermediate: {basename(tempPolygonFeature)}", 0, logFile)
                try:
                    log.logArcpy('arcpy.RasterToPolygon_conversion', (nullGrid,tempPolygonFeature,"NO_SIMPLIFY","VALUE","",maxVertices), logFile)
                    arcpy.RasterToPolygon_conversion(nullGrid,tempPolygonFeature,"NO_SIMPLIFY","VALUE","",maxVertices)
                except:
                    AddMsg(f"{timer.now()} Converting non-zero cells in {descZone.basename} to a polygon feature with maximum vertices technique. Intermediate: {basename(tempPolygonFeature)}", 0, logFile)
                    maxVertices = maxVertices / 2
                    log.logArcpy('arcpy.RasterToPolygon_conversion', (nullGrid,tempPolygonFeature,"NO_SIMPLIFY","VALUE","",maxVertices), logFile)
                    arcpy.RasterToPolygon_conversion(nullGrid,tempPolygonFeature,"NO_SIMPLIFY","VALUE","",maxVertices)
                
                inZoneDataset = tempPolygonFeature
                descZone = arcpy.Describe(inZoneDataset)
                zoneIdField = 'gridcode'
            
            
            if descZone.datasetType == "RasterDataset":
                # Use SetNull to eliminate non-zone areas and to replace the in-zone cells with values from the 
                # PopulationRaster. The snap raster, and cell size have already been set to match the census raster
                AddMsg(f"{timer.now()} Setting non-zone areas to NULL. Replace zone areas with population values.", 0, logFile)
                delimitedVALUE = arcpy.AddFieldDelimiters(inZoneDataset,"VALUE")
                whereClause = delimitedVALUE+" = 0"
                log.logArcpy('arcpy.sa.SetNull', (inZoneDataset, inCensusDataset, whereClause), logFile)
                inCensusDataset = arcpy.sa.SetNull(inZoneDataset, inCensusDataset, whereClause)
        
                if globalConstants.intermediateName in processed:
                    scratchName = arcpy.CreateScratchName(metricConst.zonePopName, "", "RasterDataset")
                    inCensusDataset.save(scratchName)
                    AddMsg(f"{timer.now()} Save intermediate grid complete: {basename(scratchName)}", 0, logFile)
                    
                AddMsg(f"{timer.now()} Calculating population within zones for each reporting unit. Intermediate: {basename(popTable_ZN)}", 0, logFile)
                log.logArcpy('arcpy.sa.ZonalStatisticsAsTable', (inReportingUnitFeature, reportingUnitIdField, inCensusDataset, popTable_ZN, "DATA", "SUM"), logFile)
                arcpy.sa.ZonalStatisticsAsTable(inReportingUnitFeature, reportingUnitIdField, inCensusDataset, popTable_ZN, "DATA", "SUM")
        
            else: # zone feature is a polygon
                # Replace the inZoneDataset with a dissolved copy
                tempDissolveName = f"{metricConst.shortName}_{fileNameBase}_Dissolve_"
                tempDissolveFeature = files.nameIntermediateFile([tempDissolveName,"FeatureClass"],cleanupList)
                
                if  groupByZoneYN == "true": # then dissolve by zoneIdField
                    AddMsg(f"{timer.now()} Dissolving {basename(inZoneDataset)} by Zone ID field. Intermediate: {basename(tempDissolveFeature)}", 0, logFile)
                    log.logArcpy("arcpy.management.Dissolve", (inZoneDataset, tempDissolveFeature, zoneIdField), logFile)
                    arcpy.management.Dissolve(inZoneDataset, tempDissolveFeature, zoneIdField)
        
                else: # dissolve all
                    AddMsg(f"{timer.now()} Dissolving all zone features. Intermediate: {basename(tempDissolveFeature)}", 0, logFile)
                    log.logArcpy('arcpy.management.Dissolve', (inZoneDataset, tempDissolveFeature), logFile)
                    arcpy.management.Dissolve(inZoneDataset, tempDissolveFeature)
        
                inZoneDataset = tempDissolveFeature
                
                # Assign the reporting unit ID to intersecting zone polygon segments using Identity
                tempName = f"{metricConst.shortName}_{fileNameBase}_Identity_"
                tempPolygonFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
                AddMsg(f"{timer.now()} Assigning reporting unit IDs to intersecting zone features. Intermediate: {basename(tempPolygonFeature)}", 0, logFile)
                log.logArcpy('arcpy.Identity_analysis', (inZoneDataset, inReportingUnitFeature, tempPolygonFeature), logFile)
                arcpy.Identity_analysis(inZoneDataset, inReportingUnitFeature, tempPolygonFeature)
        
                inReportingUnitFeature = tempPolygonFeature
            
                # calculate the population for the reporting unit using zonal statistics as table
                # The snap raster, and cell size have been set to match the census raster
                if  groupByZoneYN == "true":
            
                    ## Dissolve Identity features by zoneIdField, reportingUnitIdField
                    tempDissolveName = f"{metricConst.shortName}_{fileNameBase}_IdentityDissolve_"
                    tempDissolveFeature = files.nameIntermediateFile([tempDissolveName,"FeatureClass"],cleanupList)
                    AddMsg(f"{timer.now()} Dissolving Identity features by Zone ID field and Reporting unit ID field. Intermediate: {basename(tempDissolveFeature)}", 0, logFile)
                    log.logArcpy('arcpy.management.Dissolve', (inReportingUnitFeature, tempDissolveFeature, [zoneIdField, reportingUnitIdField]), logFile)
                    arcpy.management.Dissolve(inReportingUnitFeature, tempDissolveFeature, [zoneIdField, reportingUnitIdField])
            
                    inReportingUnitFeature = tempDissolveFeature
            
                    # Create new unique OID field.  Can not use original OID because the new output table has its own OID. join will not work
                    AddMsg(f"{timer.now()} Creating unique OID field for {basename(inReportingUnitFeature)}", 0, logFile)
                    currentOID = arcpy.Describe(inReportingUnitFeature).oidFieldName
                    tempSuccess = 0
                    while tempSuccess == 0:
                        tempOID = ''.join(random.choices(string.ascii_lowercase, k=7))
                        tempOID = arcpy.ValidateFieldName(tempOID, inReportingUnitFeature)
                        if tempOID not in [f.name for f in arcpy.ListFields(inReportingUnitFeature)]:
                            tempSuccess = 1
                    calcExpression = f'int(!{currentOID}!)'
                    log.logArcpy('arcpy.CalculateField_management', (inReportingUnitFeature, tempOID, calcExpression, "PYTHON3", "", 'TEXT'), logFile)  
                    arcpy.CalculateField_management(inReportingUnitFeature, tempOID, calcExpression, "PYTHON3", "", 'TEXT')
            
                    AddMsg(f"{timer.now()} Using ZonalStatisticsAsTable for final population counts. Intermediate: {basename(popTable_ZN)}", 0, logFile)
                    log.logArcpy('arcpy.sa.ZonalStatisticsAsTable', (inReportingUnitFeature, tempOID, inCensusDataset, popTable_ZN, "DATA", "SUM"), logFile)
                    arcpy.sa.ZonalStatisticsAsTable(inReportingUnitFeature, tempOID, inCensusDataset, popTable_ZN, "DATA", "SUM")
                    
                    AddMsg(f"{timer.now()} Attaching reporting unit ID field to {basename(popTable_ZN)}.", 0, logFile)
                    log.logArcpy('arcpy.JoinField_management', (popTable_ZN, tempOID, inReportingUnitFeature, tempOID, [reportingUnitIdField, zoneIdField]), logFile)
                    arcpy.JoinField_management(popTable_ZN, tempOID, inReportingUnitFeature, tempOID, [reportingUnitIdField, zoneIdField])
                    
                    AddMsg(f"{timer.now()} Joining reporting unit population table ({basename(popTable_RU)}) to the zone population table ({basename(popTable_ZN)}).", 0, logFile)
                    log.logArcpy('arcpy.JoinField_management', (popTable_ZN, reportingUnitIdField, popTable_RU, reportingUnitIdField, popCntFields[0]), logFile)
                    arcpy.JoinField_management(popTable_ZN, reportingUnitIdField, popTable_RU, reportingUnitIdField, popCntFields[0])
                    
                    popTable_RU = popTable_ZN
                else:
                    AddMsg(f"{timer.now()} Using ZonalStatisticsAsTable for final population counts. Intermediate: {basename(popTable_ZN)}", 0, logFile)
                    log.logArcpy('arcpy.sa.ZonalStatisticsAsTable', (inReportingUnitFeature, reportingUnitIdField, inCensusDataset, popTable_ZN, "DATA", "SUM"), logFile)
                    arcpy.sa.ZonalStatisticsAsTable(inReportingUnitFeature, reportingUnitIdField, inCensusDataset, popTable_ZN, "DATA", "SUM")
        
            # Rename the population count field.
            outPopField = metricConst.populationCountFieldNames[index]
            log.logArcpy('arcpy.AlterField_management', (popTable_ZN, "SUM", outPopField, outPopField), logFile)
            arcpy.AlterField_management(popTable_ZN, "SUM", outPopField, outPopField)
        
            ### End census features are raster ###
        
        else: # census features are polygons
            
            # Create a copy of the census feature class that we can add new fields to for calculations.
            fieldMappings = arcpy.FieldMappings()
            fieldMappings.addTable(inCensusDataset)
            [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name != inPopField]
        
            tempName = f"{metricConst.shortName}_{descCensus.baseName}_Work_"
            tempCensusFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Creating a working copy of {descCensus.baseName}. Intermediate: {basename(tempCensusFeature)}", 0, logFile)
            log.logArcpy('arcpy.FeatureClassToFeatureClass_conversion',(inCensusDataset,env.workspace,basename(tempCensusFeature),"",fieldMappings),logFile)
            inCensusDataset = arcpy.FeatureClassToFeatureClass_conversion(inCensusDataset,env.workspace,basename(tempCensusFeature),"",fieldMappings)
        
            # Add a dummy field to the copied census feature class and calculate it to a value of 1.
            classField = "tmpClass"
            log.logArcpy('arcpy.AddField_management', (inCensusDataset,classField,"SHORT"), logFile)
            arcpy.AddField_management(inCensusDataset,classField,"SHORT")
            
            log.logArcpy('arcpy.CalculateField_management', (inCensusDataset,classField,1), logFile)
            arcpy.CalculateField_management(inCensusDataset,classField,1)
        
            # Perform population count calculation for the reporting unit
            AddMsg(f"{timer.now()} Calculating population within reporting units. Intermediate: {basename(popTable_RU)}", 0, logFile)
            calculate.getPolygonPopCount(inReportingUnitFeature,reportingUnitIdField,inCensusDataset,inPopField,classField,popTable_RU,metricConst,index, logFile)
        
            # Set variables for the zone population calculations   
            index = 1
        
            popTable_ZN = files.nameIntermediateFile([metricConst.popCntTableName,'Dataset'],cleanupList)
        
            AddMsg(f"{timer.now()} Preparing for zonal population calculations.", 0, logFile)
            ## If zone is a raster and census is a polygon we convert zones to polygon
            ## If zone dataset is raster
            if descZone.datasetType == "RasterDataset":
                # Convert the Raster zones to Polygon
                AddMsg(f"{timer.now()} Setting 0 value cells in {descZone.basename} to NoData")
                delimitedVALUE = arcpy.AddFieldDelimiters(inZoneDataset,"VALUE")
                whereClause = f"{delimitedVALUE} = 0"
                log.logArcpy('arcpy.sa.SetNull', (inZoneDataset, 1, whereClause), logFile)
                nullGrid = arcpy.sa.SetNull(inZoneDataset, 1, whereClause)
                  
                tempName = f"{metricConst.shortName}_{descZone.baseName}_Poly_"
                tempPolygonFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        
                # This may fail if a polygon created is too large. Need a routine to more elegantly reduce the maxVertices in any one polygon
                maxVertices = 250000
                AddMsg(f"{timer.now()} Converting non-zero cells in {descZone.basename} to a polygon feature. Intermediate: {basename(tempPolygonFeature)}", 0, logFile)
                try:
                    log.logArcpy('arcpy.RasterToPolygon_conversion', (nullGrid,tempPolygonFeature,"NO_SIMPLIFY","VALUE","",maxVertices), logFile)
                    arcpy.RasterToPolygon_conversion(nullGrid,tempPolygonFeature,"NO_SIMPLIFY","VALUE","",maxVertices)
                except:
                    AddMsg(f"{timer.now()} Converting non-zero cells in {descZone.basename} to a polygon feature with maximum vertices technique. Intermediate: {basename(tempPolygonFeature)}", 0, logFile)
                    maxVertices = maxVertices / 2
                    log.logArcpy('arcpy.RasterToPolygon_conversion', (nullGrid,tempPolygonFeature,"NO_SIMPLIFY","VALUE","",maxVertices), logFile)
                    arcpy.RasterToPolygon_conversion(nullGrid,tempPolygonFeature,"NO_SIMPLIFY","VALUE","",maxVertices)
                
                inZoneDataset = tempPolygonFeature
                descZone = arcpy.Describe(inZoneDataset)
                zoneIdField = 'gridcode'
        
            else: # zone input is a polygon dataset
                ## If groupby, then dissolve by zoneIDField
                if  groupByZoneYN == "true":
                    tempDissolveName = f"{metricConst.shortName}_{fileNameBase}_Dissolve_"
                    tempDissolveFeature = files.nameIntermediateFile([tempDissolveName,"FeatureClass"],cleanupList)
                    AddMsg(f"{timer.now()} Dissolving {basename(inZoneDataset)} by Zone ID field. Intermediate: {basename(tempDissolveFeature)}", 0, logFile)
                    log.logArcpy('arcpy.management.Dissolve', (inZoneDataset, tempDissolveFeature, zoneIdField), logFile)
                    arcpy.management.Dissolve(inZoneDataset, tempDissolveFeature, zoneIdField)
        
                ## Else dissolve all (i.e., ignore overlapping polygons)
                else:
                    tempDissolveName = f"{metricConst.shortName}_{fileNameBase}_Dissolve_"
                    tempDissolveFeature = files.nameIntermediateFile([tempDissolveName,"FeatureClass"],cleanupList)
                    AddMsg(f"{timer.now()} Dissolving {basename(inZoneDataset)}. Intermediate: {basename(tempDissolveFeature)}", 0, logFile)
                    log.logArcpy('arcpy.management.Dissolve', (inZoneDataset, tempDissolveFeature), logFile)
                    arcpy.management.Dissolve(inZoneDataset, tempDissolveFeature)
                
                ## Set inZoneDataset as the dissolved zone features
                inZoneDataset = tempDissolveFeature
        
        
            # Add a field and calculate it to a value of 1. This field will use as the classField in Tabulate Intersection operation below
            classField = "tmpClass"
            log.logArcpy('arcpy.AddField_management', (inZoneDataset,classField,"LONG"), logFile)
            arcpy.AddField_management(inZoneDataset,classField,"LONG")
            
            log.logArcpy('arcpy.CalculateField_management', (inZoneDataset,classField,1), logFile)
            arcpy.CalculateField_management(inZoneDataset,classField,1)
        
            # intersect the zone polygons with the reporting unit polygons
            fileNameBase = descZone.baseName
            # need to eliminate the tool's shortName from the fileNameBase if the zone polygon was derived from a raster
            fileNameBase = fileNameBase.replace(f"{metricConst.shortName}_","")
            tempName = f"{metricConst.shortName}_{fileNameBase}_Identity_"
            tempPolygonFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Assigning reporting unit IDs to {descZone.baseName}. Intermediate: {basename(tempPolygonFeature)}", 0, logFile)
        
            log.logArcpy('arcpy.Identity_analysis', (inZoneDataset, inReportingUnitFeature, tempPolygonFeature), logFile)
            arcpy.Identity_analysis(inZoneDataset, inReportingUnitFeature, tempPolygonFeature)
        
            ## 
            if  groupByZoneYN == "true":
                ## Dissolve Identity features by zoneIdField, reportingUnitIdField
                tempDissolveName = f"{metricConst.shortName}_{fileNameBase}_IdentityDissolve_"
                tempDissolveFeature = files.nameIntermediateFile([tempDissolveName,"FeatureClass"],cleanupList)
                AddMsg(f"{timer.now()} Dissolving {basename(tempPolygonFeature)} by Zone ID field and Reporting unit ID field. Intermediate: {basename(tempDissolveFeature)}", 0, logFile)
                log.logArcpy('arcpy.management.Dissolve', (tempPolygonFeature, tempDissolveFeature, [zoneIdField, reportingUnitIdField]), logFile)
                arcpy.management.Dissolve(tempPolygonFeature, tempDissolveFeature, [zoneIdField, reportingUnitIdField])
        
                tempPolygonFeature = tempDissolveFeature
        
                # Create unique OID field
                currentOID = arcpy.Describe(tempPolygonFeature).oidFieldName
                tempSuccess = 0
                while tempSuccess == 0:
                    tempOID = ''.join(random.choices(string.ascii_lowercase, k=7))
                    tempOID = arcpy.ValidateFieldName(tempOID, tempPolygonFeature)
                    if tempOID not in [f.name for f in arcpy.ListFields(tempPolygonFeature)]:
                        tempSuccess = 1
                AddMsg(f"{timer.now()} Creating unique OID field for {basename(tempPolygonFeature)}", 0, logFile)
                calcExpression = f'int(!{currentOID}!)'
                log.logArcpy('arcpy.CalculateField_management', (tempPolygonFeature, tempOID, calcExpression, "PYTHON3", "", 'TEXT'), logFile)
                arcpy.CalculateField_management(tempPolygonFeature, tempOID, calcExpression, "PYTHON3", "", 'TEXT')
        
                # Perform population count calculation for second feature class area
                AddMsg(f"{timer.now()} Calculating population within zone areas for each reporting unit. Intermediate: {basename(popTable_ZN)}", 0, logFile)
                calculate.getPolygonPopCount(tempPolygonFeature,tempOID,inCensusDataset,inPopField,classField,popTable_ZN,metricConst,index, logFile)
        
                log.logArcpy('arcpy.JoinField_management', (popTable_ZN, tempOID, tempPolygonFeature, tempOID, [reportingUnitIdField, zoneIdField]), logFile)
                arcpy.JoinField_management(popTable_ZN, tempOID, tempPolygonFeature, tempOID, [reportingUnitIdField, zoneIdField])
                
                log.logArcpy('arcpy.JoinField_management', (popTable_ZN, reportingUnitIdField, popTable_RU, reportingUnitIdField, popCntFields[0]), logFile)
                arcpy.JoinField_management(popTable_ZN, reportingUnitIdField, popTable_RU, reportingUnitIdField, popCntFields[0])
                
                popTable_RU = popTable_ZN
        
            else:
                # Perform population count calculation for second feature class area
                AddMsg(f"{timer.now()} Calculating population within zone areas for each reporting unit. Intermediate: {basename(popTable_ZN)}", 0, logFile)
                calculate.getPolygonPopCount(tempPolygonFeature,reportingUnitIdField,inCensusDataset,inPopField,classField,popTable_ZN,metricConst,index, logFile)
        
        
        # Build and populate final output table.
        AddMsg(f"{timer.now()} Calculating the percent of the reporting unit population that is within a zone.", 0, logFile)
        
        fieldMappings = arcpy.FieldMappings()
        fieldMappings.addTable(popTable_RU)
        
        # Set suffix
        if bufferDistanceVal == 0:
            suffix = ""
        else:
            # need to place a valid field name character into the value string if the value is a floating point
            valueStr = str(bufferDistanceVal)
            if valueStr.find('.'):
                suffix = '_' + valueStr.replace('.', '_')
            else:
                suffix = valueStr
        
        if groupByZoneYN == "" or groupByZoneYN == 'false':
            # Construct a list of fields to retain in the output metrics table
            keepFields = metricConst.populationCountFieldNames
            keepFields.append(reportingUnitIdField)
            [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name not in keepFields]
        
            log.logArcpy('arcpy.TableToTable_conversion', (popTable_RU,os.path.dirname(outTable),basename(outTable),"",fieldMappings), logFile)
            arcpy.TableToTable_conversion(popTable_RU,os.path.dirname(outTable),basename(outTable),"",fieldMappings)
            
            # Compile a list of fields that will be transferred from the zone population table into the output table
            fromFields = [popCntFields[index]]
            toFields = [popCntFields[index] + suffix]
            
            # Transfer the values to the output table
            table.transferField(popTable_ZN,outTable,fromFields,toFields,reportingUnitIdField,None,None,logFile)
        
        else:
            keepFields = [zoneIdField, reportingUnitIdField] + metricConst.populationCountFieldNames
        
            newFieldMap = arcpy.FieldMappings()
            
            # A phenomena occurs when the PWZM tool is run first with the Group by option unchecked and then run again with the 
            # Group by option checked; the output table for the second run will have multiple listings for the reportingUnitIdField 
            # when this occurs. If the pattern is repeated, more and more reporting unit id fields will be added to the Group by 
            # output table. The following is a brute force fix. Additional time may result in determining the exact cause.
            addIdField = True

            for f in keepFields:
                i = fieldMappings.findFieldMapIndex(f)
                if f == reportingUnitIdField and addIdField == True:
                    newFieldMap.addFieldMap(fieldMappings.getFieldMap(i))
                    addIdField = False
                elif f == reportingUnitIdField and addIdField == False:
                    continue
                else:
                    newFieldMap.addFieldMap(fieldMappings.getFieldMap(i))
        
        
            log.logArcpy('arcpy.TableToTable_conversion', (popTable_RU,os.path.dirname(outTable),basename(outTable), "", newFieldMap), logFile)
            arcpy.TableToTable_conversion(popTable_RU,os.path.dirname(outTable),basename(outTable), "", newFieldMap)
        
        
            ## rename count field to include buffer
            log.logArcpy('arcpy.AlterField_management', (outTable, popCntFields[index], popCntFields[index] + suffix, popCntFields[index] + suffix ), logFile)
            arcpy.AlterField_management(outTable, popCntFields[index], popCntFields[index] + suffix, popCntFields[index] + suffix )
        
        
        
        # Set up a calculation expression for population change        
        calcExpression = f"getPopPercent(!{popCntFields[0]}!,!{popCntFields[1]}{suffix}!)"
        
        codeBlock = """def getPopPercent(pop1,pop2):
                if pop1 is None or pop2 is None:
                    return None
                elif pop1 == 0 and pop2 == 0:
                    return 0
                elif pop1 == 0 and pop2 != 0:
                    return 1
                else:
                    return (pop2/pop1)*100.0"""
        
        # Calculate the percent population within zone        
        vector.addCalculateField(outTable,metricConst.populationProportionFieldName + suffix, "FLOAT", calcExpression, codeBlock, logFile)   
        
        AddMsg(f"{timer.now()} Calculation complete", 0, logFile)
        
        # check for NULL values in output table
        num_NULL = 0
        with arcpy.da.UpdateCursor(outTable, popCntFields[0]) as cursor:
            for row in cursor:
                for i, value in enumerate(row):
                    if value is None:
                        num_NULL += 1 
                        cursor.deleteRow()
        
        if num_NULL > 0:
            AddMsg(f"{num_NULL} records had NULL values in {popCntFields[0]}. These typically represent zone areas that occur outside of Reporting unit features. They have been deleted from the Output table.", 1, logFile)
        
        
        if logFile:
            AddMsg("Summarizing the ATtILA metric output table to log file", 0)
            # append the reporting unit id field to the list of category fields; even if it's a numeric field type
            metricConst.idFields = metricConst.idFields + [reportingUnitIdField]
            log.logWriteOutputTableInfo(outTable, logFile, metricConst)
            AddMsg("Summary complete", 0)
            
            # write the standard environment settings to the log file
            log.writeEnvironments(logFile, snapRaster, processingCellSize, extentList=[inReportingUnitFeature, inCensusDataset, inZoneDataset])
            # parameters are: logFile, snapRaster, processingCellSize, extentList
            # if extentList is set to None, the env.extent setting will reported.
            # Place eventList here, if the extents of the datasets have been altered and you wish to use the new extents.
            # for snapRaster and processingCellSize, if the parameter is None, no entry will
            # will be recorded in the log for that parameter
    
    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
    
        errors.standardErrorHandling(e, logFile)
    
    finally:
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete")
        
        # close the log file
        if logFile:
            logFile.write(f"\nEnded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            logFile.write("\n---End of Log File---\n")
            logFile.close()
            AddMsg('Log file closed')
        
        if arcpy.glob.os.path.basename(arcpy.sys.executable) == globalConstants.arcExecutable:
            env.snapRaster = _tempEnvironment0
            env.workspace = _tempEnvironment1
            env.cellSize = _tempEnvironment2
            env.parallelProcessingFactor = _tempEnvironment6 

        
def runSelectZonalStatistics(toolPath, inReportingUnitFeature, reportingUnitIdField, inValueRaster, statisticsType, outTable, fieldPrefix, optionalFieldGroups):
    from arcpy import env

    try: 
        metricConst = metricConstants.szsConstants #Change constant name 
        parametersList = [inReportingUnitFeature, reportingUnitIdField, inValueRaster, statisticsType, outTable, fieldPrefix, optionalFieldGroups]
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outTable, toolPath)
        timer = DateTimer() 
        AddMsg(f"{timer.now()} Setting up environment variables", 0, logFile)
        # Ask Don about the environment set up. This is probably not the best way to do it.
        _tempEnvironment0 = env.snapRaster
        _tempEnvironment1 = env.workspace
        _tempEnvironment2 = env.cellSize
        _tempEnvironment6 = env.parallelProcessingFactor
        env.snapRaster = inValueRaster
        env.cellSize = inValueRaster       
        snapRaster = env.snapRaster
        processingCellSize = env.cellSize

        env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))
        statsTypeList = statisticsType.split(";")

        # Run arcpy zonal statistics for "ALL" and "DATA"
        AddMsg(f"{timer.now()} Running zonal statistics as table for {statsTypeList}", 0, logFile)
        if len(statsTypeList) == 1: 
        #If only one statistic type is selected process on just the one.
            if statsTypeList[0] == "MAX": 
                log.logArcpy('arcpy.sa.ZonalStatisticsAsTable', (inReportingUnitFeature, reportingUnitIdField, inValueRaster, outTable, "DATA", 'MAXIMUM'), logFile)
                arcpy.sa.ZonalStatisticsAsTable(inReportingUnitFeature, reportingUnitIdField, inValueRaster, outTable, "DATA", 'MAXIMUM')
            elif statsTypeList[0] == "MIN": 
                log.logArcpy('arcpy.sa.ZonalStatisticsAsTable', (inReportingUnitFeature, reportingUnitIdField, inValueRaster, outTable, "DATA", 'MINIMUM'), logFile)
                arcpy.sa.ZonalStatisticsAsTable(inReportingUnitFeature, reportingUnitIdField, inValueRaster, outTable, "DATA", 'MINIMUM')
            # zone more statement for the percentile
            else:
                log.logArcpy('arcpy.sa.ZonalStatisticsAsTable', (inReportingUnitFeature, reportingUnitIdField, inValueRaster, outTable, "DATA", statsTypeList[0]), logFile)
                arcpy.sa.ZonalStatisticsAsTable(inReportingUnitFeature, reportingUnitIdField, inValueRaster, outTable, "DATA", statsTypeList[0])
        else: 
            log.logArcpy('arcpy.sa.ZonalStatisticsAsTable', (inReportingUnitFeature, reportingUnitIdField, inValueRaster, outTable, "DATA", "ALL"), logFile)
            arcpy.sa.ZonalStatisticsAsTable(inReportingUnitFeature, reportingUnitIdField, inValueRaster, outTable, "DATA", "ALL")
        
        # Add Quality Assurance Field "AREA_OVER"
        AddMsg(f"{timer.now()} Adding quality assurance field: 'AREA_OVER'", 0, logFile)
        log.logArcpy('arcpy.AddField_management', (outTable, metricConst.qaName, globalConstants.defaultIntegerFieldType), logFile)
        arcpy.AddField_management(outTable, metricConst.qaName, globalConstants.defaultIntegerFieldType)
        
        AddMsg(f"{timer.now()} Collecting polygon area values for each Reporting Unit", 0, logFile)
        outputSpatialRef = settings.getOutputSpatialReference(inValueRaster) # Get the raster spatial refernce
        zoneAreaDict = polygons.getMultiPartIdAreaDict(inReportingUnitFeature, reportingUnitIdField, outputSpatialRef)
        
        AddMsg(f"{timer.now()} Calculating 'AREA_OVER': (reporting unit raster area / reporting unit polygon area) * 100", 0, logFile)
        with arcpy.da.UpdateCursor(outTable, [reportingUnitIdField, "AREA", metricConst.qaName]) as cursor: 
            for row in cursor: 
                DictKey = row[0] # DictKey = reportingUnitIdField row
                rasterArea = row[1]
                # arcpy.AddMessage(DictKey) THESE ARE REALLY HELPFUL FOR TROUBLESHOOTING
                # arcpy.AddMessage(Area)
                if DictKey in zoneAreaDict: 
                    polygonArea = zoneAreaDict[DictKey]
                    # arcpy.AddMessage(value)
                    row[2] = rasterArea/polygonArea * 100
                else: 
                    row[2] = None
                cursor.updateRow(row)

        originalFields = [field.name for field in arcpy.ListFields(outTable)]
        
        if len(statsTypeList) > 1 and "ALL" not in statsTypeList: 
            AddMsg(f"{timer.now()} Trimming unnecessary fields", 0, logFile) 
            keepFields2 =  statsTypeList + originalFields[0:5] + [metricConst.qaName]   # Keep basic info fields and user defined statistics
            log.logArcpy('arcpy.DeleteField_management', (outTable, keepFields2, "KEEP_FIELDS"), logFile)
            arcpy.DeleteField_management(outTable, keepFields2, "KEEP_FIELDS")
        
        AddMsg(f"{timer.now()} Updating field names", 0, logFile)
        oldFields = arcpy.ListFields(outTable)
        for field in oldFields: 
            if field.name in metricConst.statisticsFieldNames:
                newFieldName = f"{fieldPrefix}_{field.name}" 
                log.logArcpy('arcpy.management.AlterField', (outTable, field.name, newFieldName, newFieldName), logFile)
                arcpy.management.AlterField(outTable, field.name, newFieldName, newFieldName)


        if logFile:
                AddMsg("Summarizing the ATtILA metric output table to log file", 0)
                # append the reporting unit id field to the list of category fields; even if it's a numeric field type
                metricConst.idFields = metricConst.idFields + [reportingUnitIdField]
                # append the reporting unit id field to the list of category fields; even if it's a numeric field type
                metricConst.idFields = metricConst.idFields + [reportingUnitIdField]
                log.logWriteOutputTableInfo(outTable, logFile, metricConst)
                AddMsg("Summary complete", 0)
                
                # write the standard environment settings to the log file
                log.writeEnvironments(logFile, snapRaster, processingCellSize, extentList=[inReportingUnitFeature, inValueRaster])
                # parameters are: logFile, snapRaster, processingCellSize, extentDataset
                # if extentDataset is set to None, the env.extent setting will reported.
                # for snapRaster and processingCellSize, if the parameter is None, no entry will
                # will be recorded in the log for that parameter
    except Exception as e:
        if logFile:
                # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
                
        errors.standardErrorHandling(e, logFile)       

    finally:
        
        if logFile:
            logFile.write(f"\nEnded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            logFile.write("\n---End of Log File---\n")
            logFile.close()
            AddMsg('Log file closed')
            
        # again ask about environemnt stuff     
        if arcpy.glob.os.path.basename(arcpy.sys.executable) == globalConstants.arcExecutable:    
            env.snapRaster = _tempEnvironment0
            env.workspace = _tempEnvironment1
            env.cellSize = _tempEnvironment2
            env.parallelProcessingFactor = _tempEnvironment6


def runNearRoadLandCoverProportions(toolPath, inRoadFeature, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, inRoadWidthOption,
                      widthLinearUnit="", laneCntFld="#", laneWidth="#", laneDistFld="#", bufferDist="#", removeLinesYN="",
                      cutoffLength="#", overWrite="", outWorkspace='#',  processingCellSize="#", snapRaster="#", optionalFieldGroups="#"):
    """ Interface for script executing Near Road Land Cover Proportions tool """
    
    from arcpy import env
#    from arcpy.sa import Con,Raster,Reclassify,RegionGroup,RemapValue,RemapRange

    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.nrlcpConstants()
        
        # copy input parameters to pass to the log file routine
        parametersList = [toolPath, inRoadFeature, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, inRoadWidthOption, widthLinearUnit, laneCntFld, 
                          laneWidth, laneDistFld, bufferDist, removeLinesYN, cutoffLength, overWrite, outWorkspace,  processingCellSize, snapRaster, optionalFieldGroups]
        # create a log file if requested, otherwise logFile = None
        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outWorkspace, toolPath)
        
        # Check to see if the inLandCoverGrid has an attribute table. If not, build one
        raster.buildRAT(inLandCoverGrid, logFile)
        
        # create a list of input themes to find the intersection extent
        if logFile:
            extentList = [inRoadFeature, inLandCoverGrid]
        
        ### Initialization
        # Start the timer
        timer = DateTimer()
        AddMsg(timer.now() + " Setting up environment variables")
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster,processingCellSize,outWorkspace,
                                                                               [metricsToRun,optionalFieldGroups], logFile,
                                                                               inRoadFeature)

        # Process the Land Cover Classification XML
        lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        lccClassesDict = lccObj.classes
        # Get the lccObj values dictionary. This contains all the properties of each value specified in the Land Cover Classification XML    
#        lccValuesDict = lccObj.values
        # create a list of all the grid values in the selected land cover grid
#        landCoverValues = raster.getRasterValues(inLandCoverGrid, logFile)
        # get the frozenset of excluded values (i.e., values marked as EXCLUDED in the Land Cover Classification XML)
#        excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)
        
        # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
        settings.checkExcludedValuesInClass(metricsBaseNameList, lccObj, lccClassesDict, logFile)
        # alert user if the land cover grid has values undefined in the LCC XML file
        settings.checkGridValuesInLCC(inLandCoverGrid, lccObj, logFile)
        # alert user if the land cover grid cells are not square (default to size along x axis)
        settings.checkGridCellDimensions(inLandCoverGrid, logFile)
        
        # Determine if the user wants to save the intermediate products       
        if globalConstants.intermediateName in optionalGroupsList:
#            saveIntermediates = True
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
#            saveIntermediates = False
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
        
        # determine the active map to add the output raster/features    
#        try:
#            currentProject = arcpy.mp.ArcGISProject("CURRENT")
#            actvMap = currentProject.activeMap
#        except:
#            actvMap = None
        
        ### Computations
        
        # Create road buffers
        # Create a copy of the road feature class that we can add new fields to for calculations. 
        # This is more appropriate than altering the user's input data.
        desc = arcpy.Describe(inRoadFeature)
        tempName = "%s_%s" % (metricConst.shortName, desc.baseName)
        tempRoadFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        fieldMappings = arcpy.FieldMappings()
        fieldMappings.addTable(inRoadFeature)
        
        AddMsg("%s Creating a working copy of %s..." % (timer.now(), os.path.basename(inRoadFeature)))
        
        if inRoadWidthOption == "Distance":
            [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.required != True]
            inRoadFeature = arcpy.FeatureClassToFeatureClass_conversion(inRoadFeature,env.workspace,os.path.basename(tempRoadFeature),"",fieldMappings)
            
            AddMsg("%s Adding field, HalfWidth, and calculating its value... " % (timer.now()))   
            halfRoadWidth = float(widthLinearUnit.split()[0]) / 2
            halfLinearUnit = "'%s %s'" % (str(halfRoadWidth), widthLinearUnit.split()[1]) # put linear unit string in quotes
            arcpy.AddField_management(inRoadFeature, 'HalfWidth', 'TEXT')
            AddMsg("...    HalfWidth = %s" % (halfLinearUnit))
            arcpy.CalculateField_management(inRoadFeature, 'HalfWidth', halfLinearUnit)
            
        elif inRoadWidthOption == "Field: Lane Count":
            [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name != laneCntFld]
            inRoadFeature = arcpy.FeatureClassToFeatureClass_conversion(inRoadFeature,env.workspace,os.path.basename(tempRoadFeature),"",fieldMappings)
            
            AddMsg("%s Adding fields, HalfValue and HalfWidth, and calculating their values... " % (timer.now()))
            arcpy.AddField_management(inRoadFeature, 'HalfValue', 'DOUBLE')
            calcExpression = "!%s! * %s / 2" % (str(laneCntFld), laneWidth.split()[0])
            AddMsg("...    HalfValue = %s" % (calcExpression))
            arcpy.CalculateField_management(inRoadFeature, 'HalfValue', calcExpression, 'PYTHON_9.3')
            
            arcpy.AddField_management(inRoadFeature, 'HalfWidth', 'TEXT')
            calcExpression2 = "'!%s! %s'" % ('HalfValue', laneWidth.split()[1]) # put linear unit string in quotes
            AddMsg("...    HalfWidth = %s" % (calcExpression2))
            arcpy.CalculateField_management(inRoadFeature, 'HalfWidth', calcExpression2, 'PYTHON_9.3')
            
        else:
            [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name != laneDistFld]
            inRoadFeature = arcpy.FeatureClassToFeatureClass_conversion(inRoadFeature,env.workspace,os.path.basename(tempRoadFeature),"",fieldMappings)
            
            
            # input field should be a linear distance string. Part 0 = distance value. Part 1 = distance units
            try:
                AddMsg("%s Adding fields, HalfValue and HalfWidth, and calculating their values... " % (timer.now()))
                
                arcpy.AddField_management(inRoadFeature, 'HalfValue', 'DOUBLE')
                calcExpression = "float(!%s!.split()[0]) / 2" % (laneDistFld)
                AddMsg("...    HalfValue = %s" % (calcExpression))
                arcpy.CalculateField_management(inRoadFeature, 'HalfValue', calcExpression, 'PYTHON_9.3')
                
                arcpy.AddField_management(inRoadFeature, 'HalfWidth', 'TEXT')
                #conjunction = '+" "+'
                #calcExpression2 = "str(!%s!)%s!%s!.split()[1]" % ('HalfValue', conjunction, laneDistFld)
                calcExpression2 = "str(!%s!)+' '+!%s!.split()[1]" % ('HalfValue', laneDistFld)
                AddMsg("...    HalfWidth = %s" % (calcExpression2))
                arcpy.CalculateField_management(inRoadFeature, 'HalfWidth', calcExpression2, 'PYTHON_9.3')
                
            except:
                raise errors.attilaException(errorConstants.linearUnitFormatError)
        
        
        AddMsg("%s Buffer road feature using the value in HALFWIDTH with options FULL, FLAT, ALL..." % (timer.now()))
        tempName = "%s_%s" % (metricConst.shortName, '1_RoadEdge')
        edgeBufferFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        arcpy.Buffer_analysis(inRoadFeature, edgeBufferFeature, 'HalfWidth', 'FULL', 'FLAT', 'ALL')
        
        AddMsg("%s Re-buffer the buffered streets by 11.5 meters with options FULL, FLAT, ALL..." % (timer.now())) 
        tempName = "%s_%s" % (metricConst.shortName, '2_RoadBuffer')
        roadBufferFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        arcpy.Buffer_analysis(edgeBufferFeature, roadBufferFeature, '11.5 Meters', 'FULL', 'FLAT', 'ALL')

        
        # Convert the buffer into lines
        AddMsg("%s Converting the resulting polygons into polylines -- referred to as analysis lines.--" % (timer.now()))
        tempName = "%s_%s" % (metricConst.shortName, '3_RdBuffLine')
        rdBuffLineFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        arcpy.PolygonToLine_management(roadBufferFeature, rdBuffLineFeature)


        # Remove interior lines based on cut-off point
        if removeLinesYN == "true":
            AddMsg("%s Adding geometry attributes to polyline feature. Calculating LENGTH in METERS..." % (timer.now()))
            try:
                arcpy.AddGeometryAttributes_management(rdBuffLineFeature,'LENGTH','METERS')
                Expression = 'LENGTH <= %s' % cutoffLength
            except:
                arcpy.AddGeometryAttributes_management(rdBuffLineFeature,'LENGTH_GEODESIC','METERS')
                Expression = 'LENGTH_GEO <= %s' % cutoffLength
            
            
            AddMsg("%s Deleting analysis lines that are <= %s meters in length..." % (timer.now(), cutoffLength))
            #Expression = 'Shape_Length <= 1050'
            #Expression = 'LENGTH <= %s' % cutoffLength
         
            arcpy.MakeFeatureLayer_management(rdBuffLineFeature, 'BuffLine_lyr')
            arcpy.SelectLayerByAttribute_management('BuffLine_lyr', 'NEW_SELECTION', Expression)
            arcpy.DeleteFeatures_management('BuffLine_lyr')
            tempName = "%s_%s" % (metricConst.shortName, '4_BuffLineUse')
            buffLineUseFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
            arcpy.CopyFeatures_management('BuffLine_lyr', buffLineUseFeature)
        else:
            buffLineUseFeature = rdBuffLineFeature

        #Create Road Buffer Areas
        ### This routine needs to be altered to convert input buffer distance units to meters ###
        leftValue = float(bufferDist.split()[0]) - 11.5
        leftUnits = bufferDist.split()[1]
        leftDist = str(leftValue)+' '+leftUnits
        AddMsg("%s Buffering the analysis line by %s with options LEFT, FLAT, ALL..." % (timer.now(), leftDist))
        tempName = "%s_%s_" % (metricConst.shortName, '_Left_'+str(round(leftValue)))
        leftBuffFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        arcpy.Buffer_analysis(buffLineUseFeature, leftBuffFeature, leftDist, 'LEFT', 'FLAT', 'ALL')
        
        AddMsg("%s Buffering the analysis line by 11.5 meters with options RIGHT, FLAT, ALL..." % (timer.now()))
        tempName = "%s_%s_" % (metricConst.shortName, '_Right_11')
        rightBuffFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        arcpy.Buffer_analysis(buffLineUseFeature, rightBuffFeature, '11.5 Meters', 'RIGHT', 'FLAT', 'ALL')        
        
        AddMsg("%s Merging the two buffers together and dissolving..." % (timer.now()))
        tempName = "%s_%s" % (metricConst.shortName, '_Buff_LR')
        mergeBuffFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        arcpy.Merge_management([leftBuffFeature, rightBuffFeature], mergeBuffFeature)
        
        tempName = "%s_%s" % (metricConst.shortName, '_RoadBuffer')
        finalBuffFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        log.logArcpy("arcpy.Dissolve_management",(mergeBuffFeature, finalBuffFeature),logFile)      
        arcpy.Dissolve_management(mergeBuffFeature, finalBuffFeature)
        
        

    except Exception as e:
        if logFile:
            # COMPLETE LOGFILE
            logFile.write("\nSomething went wrong.\n\n")
            logFile.write("Python Traceback Message below:")
            logFile.write(traceback.format_exc())
            
        errors.standardErrorHandling(e, logFile)
 
    finally:
        setupAndRestore.standardRestore(logFile)
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
            AddMsg("Clean up complete")
                
                
# def runNearRoadLandCoverProportionsNEW(inRoadFeature, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, inRoadWidthOption,
#                       widthLinearUnit="", laneCntFld="#", laneWidth="#", laneDistFld="#", bufferDist="#", removeLinesYN="",
#                       cutoffLength="#", overWrite="", outWorkspace='#',  processingCellSize="#", snapRaster="#", optionalFieldGroups="#"):
#     """ Interface for script executing Near Road Land Cover Proportions tool """
#
#     from arcpy import env
# #    from arcpy.sa import Con,Raster,Reclassify,RegionGroup,RemapValue,RemapRange
#
#     cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
#     try:
#         # retrieve the attribute constants associated with this metric
#         metricConst = metricConstants.nrlcpConstants()
#
#         ### Initialization
#         # Start the timer
#         timer = DateTimer()
#         AddMsg(timer.now() + " Setting up environment variables")
#         metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster,processingCellSize,outWorkspace,
#                                                                                [metricsToRun,optionalFieldGroups] )
#
#         # Process the Land Cover Classification XML
#         lccObj = lcc.LandCoverClassification(lccFilePath)
#         # get the dictionary with the LCC CLASSES attributes
#         lccClassesDict = lccObj.classes
#         # Get the lccObj values dictionary. This contains all the properties of each value specified in the Land Cover Classification XML    
# #        lccValuesDict = lccObj.values
#         # create a list of all the grid values in the selected land cover grid
# #        landCoverValues = raster.getRasterValues(inLandCoverGrid, logFile)
#         # get the frozenset of excluded values (i.e., values marked as EXCLUDED in the Land Cover Classification XML)
# #        excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)
#
#         # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
#         settings.checkExcludedValuesInClass(metricsBaseNameList, lccObj, lccClassesDict)
#         # alert user if the land cover grid has values undefined in the LCC XML file
#         settings.checkGridValuesInLCC(inLandCoverGrid, lccObj)
#         # alert user if the land cover grid cells are not square (default to size along x axis)
#         settings.checkGridCellDimensions(inLandCoverGrid)
#
#         # Determine if the user wants to save the intermediate products       
#         if globalConstants.intermediateName in optionalGroupsList:
# #            saveIntermediates = True
#             cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
#         else:
# #            saveIntermediates = False
#             cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
#
#         # determine the active map to add the output raster/features    
# #        currentProject = arcpy.mp.ArcGISProject("CURRENT")
# #        actvMap = currentProject.activeMap
#
#         ### Computations
#
#         # Create road buffers
#
#
#
#
#     except Exception as e:
#         errors.standardErrorHandling(e, logFile)
#
#     finally:
#         setupAndRestore.standardRestore()
#         if not cleanupList[0] == "KeepIntermediates":
#             for (function,arguments) in cleanupList:
#                 # Flexibly executes any functions added to cleanup array.
#                 function(*arguments)