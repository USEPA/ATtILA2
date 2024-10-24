''' Interface for running specific metrics

'''
import os
import arcpy
import time
from arcpy.sa import Raster
from . import errors
from . import setupAndRestore
#from pylet import lcc
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
from .utils.messages import AddMsg
from .datetimeutil import DateTimer
from .constants import metricConstants
from .constants import globalConstants
from .constants import errorConstants
from . import utils
from .utils.tabarea import TabulateAreaTable
#from arcpy import ListFields, FieldInfo, FieldMap

#from sympy.logic.boolalg import false

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
              metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst, ignoreHighest=False):
        self.timer = DateTimer()
        AddMsg(self.timer.start() + " Setting up environment variables")
        
        # Check to see if the user has specified a Processing cell size other than the cell size of the inLandCoverGrid
        inLandCoverGridCellSize = Raster(inLandCoverGrid).meanCellWidth
        if float(processingCellSize) != inLandCoverGridCellSize:
            AddMsg("Processing cell size and the cell size for the input Land cover grid are not equal.\n"\
                   "For the most accurate results, it is highly recommended to use the cell size of the input Land cover grid as the Processing cell size.", 1)
        
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

        # Set whether to add QA Fields as a class attribute
        self.addQAFields = globalConstants.qaCheckName in self.optionalGroupsList
        
        # Save other input parameters as class attributes
        self.outTable = outTable
        self.inReportingUnitFeature = inReportingUnitFeature
        self.reportingUnitIdField = reportingUnitIdField
        self.metricConst = metricConst
        self.inLandCoverGrid = inLandCoverGrid
        self.ignoreHighest = ignoreHighest
        self.scratchNameToBeDeleted =  ""
        self.reportingUnitAreaDict = None

    def _replaceLCGrid(self):
        # Placeholder for internal function to replace the landcover grid.  Several metric Calculations require this step, but others skip it.
        pass

    def _replaceRUFeatures(self):
        # Placeholder for internal function for buffer calculations - most calculations don't require this step.
        pass

    def _housekeeping(self):
        # Perform additional housekeeping steps - this must occur after any LCGrid or inRUFeature replacement

        # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
        settings.checkExcludedValuesInClass(self.metricsBaseNameList, self.lccObj, self.lccClassesDict)
        # alert user if the land cover grid has values undefined in the LCC XML file
        settings.checkGridValuesInLCC(self.inLandCoverGrid, self.lccObj, self.ignoreHighest)
        # alert user if the land cover grid cells are not square (default to size along x axis)
        settings.checkGridCellDimensions(self.inLandCoverGrid)
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
        AddMsg(self.timer.now() + " Constructing the ATtILA metric output table")
        # Internal function to construct the ATtILA metric output table
        self.newTable, self.metricsFieldnameDict = table.tableWriterByClass(self.outTable,
                                                                                  self.metricsBaseNameList,
                                                                                  self.optionalGroupsList,
                                                                                  self.metricConst, self.lccObj,
                                                                                  self.outIdField)
    def _makeTabAreaTable(self):
        AddMsg(self.timer.now() + " Generating a zonal tabulate area table")
        # Internal function to generate a zonal tabulate area table
        self.tabAreaTable = TabulateAreaTable(self.inReportingUnitFeature, self.reportingUnitIdField,
                                              self.inLandCoverGrid, self.tableName, self.lccObj)

    def _calculateMetrics(self):
        AddMsg(self.timer.now() + " Processing the tabulate area table and computing metric values")
        # Internal function to process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
        # Default calculation is land cover proportions.  this may be overridden by some metrics.
        calculate.landCoverProportions(self.lccClassesDict, self.metricsBaseNameList, self.optionalGroupsList,
                                             self.metricConst, self.outIdField, self.newTable, self.tabAreaTable,
                                             self.metricsFieldnameDict, self.zoneAreaDict, self.reportingUnitAreaDict)

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


def runLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                                     metricsToRun, outTable, perCapitaYN, inCensusDataset, inPopField, processingCellSize, 
                                     snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover Proportion Metrics and Population Density Metrics """
    
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcpConstants()
        
        # Create new subclass of metric calculation
        class metricCalcLCP(metricCalc):        
        
            def _makeAttilaOutTable(self):
                AddMsg(self.timer.now() + " Constructing the ATtILA metric output table")
                # Internal function to construct the ATtILA metric output table
                if perCapitaYN == "true":     
                    self.newTable, self.metricsFieldnameDict = table.tableWriterByClass(self.outTable, 
                                                                                        self.metricsBaseNameList,
                                                                                        self.optionalGroupsList, 
                                                                                        self.metricConst, 
                                                                                        self.lccObj, 
                                                                                        self.outIdField, 
                                                                                        self.metricConst.additionalFields)
                else:
                    self.newTable, self.metricsFieldnameDict = table.tableWriterByClass(self.outTable,
                                                                                        self.metricsBaseNameList,
                                                                                        self.optionalGroupsList,
                                                                                        self.metricConst, 
                                                                                        self.lccObj,
                                                                                        self.outIdField)     
        
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
                    AddMsg(self.timer.now() + " Calculating population within each reporting unit") 
                    self.populationTable, self.populationField = table.createPolygonValueCountTable(self.inReportingUnitFeature,
                                                                         self.reportingUnitIdField,
                                                                         self.inCensusDataset,
                                                                         self.inPopField,
                                                                         self.popTable,
                                                                         self.metricConst,
                                                                         self.index,
                                                                         self.cleanupList)
                    
                    # Assemble dictionary with the reporting unit's ID as key, and the area-weighted population as the value
                    self.zonePopulationDict = table.getIdValueDict(self.populationTable, 
                                                                   self.reportingUnitIdField, 
                                                                   self.populationField)

                
                AddMsg(self.timer.now() + " Processing the tabulate area table and computing metric values")
                # Internal function to process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
                # Default calculation is land cover proportions.  this may be overridden by some metrics.
                calculate.landCoverProportions(self.lccClassesDict, self.metricsBaseNameList, self.optionalGroupsList,
                                               self.metricConst, self.outIdField, self.newTable, self.tabAreaTable,
                                               self.metricsFieldnameDict, self.zoneAreaDict, self.reportingUnitAreaDict, self.zonePopulationDict,
                                               self.conversionFactor)

        
        # Create new instance of metricCalc class to contain parameters
        lcpCalc = metricCalcLCP(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                             metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        
        # Assign class attributes unique to this module.
        lcpCalc.perCapitaYN = perCapitaYN
        lcpCalc.inCensusDataset = inCensusDataset
        lcpCalc.inPopField = inPopField
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
        errors.standardErrorHandling(e)

    finally:
        if not lcpCalc.cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in lcpCalc.cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
        setupAndRestore.standardRestore()
        

def runLandCoverOnSlopeProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                                   metricsToRun, inSlopeGrid, inSlopeThresholdValue, outTable, processingCellSize,
                                   snapRaster, optionalFieldGroups, clipLCGrid):
    """ Interface for script executing Land Cover on Slope Proportions (Land Cover Slope Overlap)"""

    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcospConstants()
        # append the slope threshold value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inSlopeThresholdValue
        
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
            timer = DateTimer()
            AddMsg(timer.now() + " Reducing input Land cover grid to smallest recommended size...")
            pathRoot = os.path.splitext(inLandCoverGrid)[0]
            namePrefix = "%s_%s" % (metricConst.shortName, os.path.basename(pathRoot))
            scratchName = arcpy.CreateScratchName(namePrefix,"","RasterDataset")
            inLandCoverGrid = raster.clipGridByBuffer(inReportingUnitFeature, scratchName, inLandCoverGrid)
            AddMsg(timer.now() + " Reduction complete")

        
        # Create new subclass of metric calculation
        class metricCalcLCOSP(metricCalc):
            # Subclass that overrides specific functions for the LandCoverOnSlopeProportions calculation
            def _replaceLCGrid(self):
                # replace the inLandCoverGrid
                self.inLandCoverGrid = raster.getIntersectOfGrids(self.lccObj, self.inLandCoverGrid, self.inSlopeGrid,
                                                                   self.inSlopeThresholdValue,self.timer)

                if self.saveIntermediates:
                    self.namePrefix = self.metricConst.shortName+"_"+"Raster"+metricConst.fieldParameters[1]+"_"
                    self.scratchName = arcpy.CreateScratchName(self.namePrefix, "", "RasterDataset")
                    self.inLandCoverGrid.save(self.scratchName)
                    #arcpy.CopyRaster_management(self.inLandCoverGrid, self.scratchName)
                    AddMsg(self.timer.now() + " Save intermediate grid complete: "+os.path.basename(self.scratchName))
                    
        # Set toogle to ignore 'below slope threshold' marker in slope/land cover hybrid grid when checking for undefined values
        ignoreHighest = True
        
        # Create new instance of metricCalc class to contain parameters
        lcspCalc = metricCalcLCOSP(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst, ignoreHighest)

        lcspCalc.inSlopeGrid = inSlopeGrid
        lcspCalc.inSlopeThresholdValue = inSlopeThresholdValue

        # Run Calculation
        lcspCalc.run()
        
        if clipLCGrid == "true":
            arcpy.Delete_management(scratchName) 

    except Exception as e:
        errors.standardErrorHandling(e)

    finally:
        setupAndRestore.standardRestore()
        env.workspace = _tempEnvironment1
        
        
def runFloodplainLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                                   metricsToRun, inFloodplainGeodataset, outTable, processingCellSize, snapRaster, 
                                   optionalFieldGroups, clipLCGrid):
    """ Interface for script executing Floodplain Land Cover Proportions """
        
    try:
        timer = DateTimer()
        
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.flcpConstants()
          
        #If clipLCGrid is selected, clip the input raster to the extent of the reporting unit theme or the to the extent
        #of the selected reporting unit(s). If the metric is susceptible to edge-effects (e.g., core and edge metrics, 
        #patch metrics) extend the clip envelope an adequate distance.        
        from arcpy import env        
        _tempEnvironment1 = env.workspace
        env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))

        if clipLCGrid == "true":
            AddMsg(timer.now() + " Reducing input Land cover grid to smallest recommended size...")
            pathRoot = os.path.splitext(inLandCoverGrid)[0]
            namePrefix = "%s_%s" % (metricConst.shortName, os.path.basename(pathRoot))
            scratchName = arcpy.CreateScratchName(namePrefix,"","RasterDataset")
            inLandCoverGrid = raster.clipGridByBuffer(inReportingUnitFeature, scratchName, inLandCoverGrid)
            AddMsg(timer.now() + " Reduction complete")
  
          
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
                AddMsg(timer.now() + " Generating land cover in floodplain grid...")
                self.inLandCoverGrid = raster.getSetNullGrid(self.inFloodplainGeodataset, self.inLandCoverGrid, self.nullValuesList)
                    
                if self.saveIntermediates:
                    self.namePrefix = self.metricConst.landcoverGridName
                    self.scratchName = arcpy.CreateScratchName(self.namePrefix, "", "RasterDataset")
                    self.inLandCoverGrid.save(self.scratchName)
                    AddMsg(self.timer.now() + " Save intermediate grid complete: "+os.path.basename(self.scratchName))
                    
                    
            def _housekeeping(self):
                # Perform additional housekeeping steps - this must occur after any LCGrid or inRUFeature replacement
            
                # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
                settings.checkExcludedValuesInClass(self.metricsBaseNameList, self.lccObj, self.lccClassesDict)
                # alert user if the land cover grid has values undefined in the LCC XML file
                settings.checkGridValuesInLCC(self.inLandCoverGrid, self.lccObj, self.ignoreHighest)
                # alert user if the land cover grid cells are not square (default to size along x axis)
                settings.checkGridCellDimensions(self.inLandCoverGrid)
                # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
                self.outIdField = settings.getIdOutField(self.inReportingUnitFeature, self.reportingUnitIdField)
            
                # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
                self.zoneAreaDict = None
                if self.addQAFields:
                    AddMsg(self.timer.now() + " Tabulating the area of the floodplains within each reporting unit...")
                    fpTabAreaTable = files.nameIntermediateFile([self.metricConst.fpTabAreaName, "Dataset"], self.cleanupList)   
            
                    arcpy.sa.TabulateArea(self.inReportingUnitFeature, self.reportingUnitIdField, self.inFloodplainGeodataset, "VALUE", fpTabAreaTable, processingCellSize)
            
                    # self.zoneAreaDict = table.getIdValueDict(fpTabAreaTable, self.reportingUnitIdField, "VALUE_1")
                    # This new techniques allows the use of all non-zero values in a grid to designate floodplain areas instead of just '1'. 
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
                                                                                              self.cleanupList, self.timer)
 
  
        # Do a Describe on the floodplain input to determine if it is a raster or polygon feature
        desc = arcpy.Describe(inFloodplainGeodataset)
         
        if desc.datasetType == "RasterDataset":
            # Create new instance of metricCalc class to contain parameters
            flcpCalc = metricCalcFLCPRaster(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        else:
            # Create new instance of metricCalc class to contain parameters
            flcpCalc = metricCalcFLCPPolygon(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
         
        # Assign class attributes unique to this module.
        flcpCalc.inFloodplainGeodataset = inFloodplainGeodataset
        flcpCalc.nullValuesList = [0] # List of values in the binary floodplain grid to set to null
        flcpCalc.cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
        
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
            landCoverValues = raster.getRasterValues(inLandCoverGrid)
            # get the list of excluded values that are found in the input land cover raster
            excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)
            
            if len(excludedValuesList) > 0:
                AddMsg("%s Excluded values found in the land cover grid. Calculating effective areas for each reporting unit..." % timer.now())
                # Use ATtILA's TabulateAreaTable operation to return an object where a tabulate area table can be easily queried.
                if flcpCalc.saveIntermediates:
                    # name the table so that it will be saved
                    ruTableName = metricConst.shortName + globalConstants.ruTabulateAreaTableAbbv
                else:
                    ruTableName = None
                ruAreaTable = TabulateAreaTable(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, ruTableName, flcpCalc.lccObj)
                
                for ruAreaTableRow in ruAreaTable:
                    key = ruAreaTableRow.zoneIdValue
                    area = ruAreaTableRow.effectiveArea
                    # make the value of key a list
                    flcpCalc.reportingUnitAreaDict[key] = [flcpCalc.reportingUnitAreaDict[key]]
                    flcpCalc.reportingUnitAreaDict[key].append(area)
            
            else:
                AddMsg("%s No excluded values found in the land cover grid. Reporting unit effective area equals total reporting unit area. Recording reporting unit areas..." % timer.now())
                for aKey in flcpCalc.testAreaDict.keys():
                    area = flcpCalc.reportingUnitAreaDict[aKey]
                    # make the value of key a list
                    flcpCalc.reportingUnitAreaDict[aKey] = [flcpCalc.reportingUnitAreaDict[aKey]]
                    flcpCalc.reportingUnitAreaDict[aKey].append(area)                    
        

        # Run Calculation 
        flcpCalc.run()
          
        if clipLCGrid == "true":
            arcpy.Delete_management(scratchName) 
 
    except Exception as e:
        errors.standardErrorHandling(e)
 
    finally:
        if not flcpCalc.cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in flcpCalc.cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
        setupAndRestore.standardRestore()
        env.workspace = _tempEnvironment1


def runPatchMetrics(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun,
                          inPatchSize, inMaxSeparation, outTable, mdcpYN, processingCellSize, snapRaster, 
                          optionalFieldGroups, clipLCGrid):
    """ Interface for script executing Patch Metrics """
    
    #from .utils import settings

    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        # Start the timer
        timer = DateTimer()
        AddMsg(timer.start() + " Setting up initial environment variables")
        
        # index the reportingUnitIdField to speed query results
        ruIdIndex = "ruIdIndex_ATtILA"
        indexNames = [indx.name for indx in arcpy.ListIndexes(inReportingUnitFeature)]
        if ruIdIndex not in indexNames:
            arcpy.AddIndex_management(inReportingUnitFeature, reportingUnitIdField, ruIdIndex)
        
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.pmConstants()
        
        # setup the appropriate metric fields to add to output table depending on if MDCP is selected or not
        if mdcpYN:
            metricConst.additionalFields = metricConst.additionalFields + metricConst.mdcpFields
        else:
            metricConst.additionalFields = metricConst.additionalFields
            
        
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize,
                                                                                os.path.dirname(outTable),
                                                                                [metricsToRun,optionalFieldGroups] )
        
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
        settings.checkExcludedValuesInClass(metricsBaseNameList, lccObj, lccClassesDict)
        
        # alert user if the land cover grid has values undefined in the LCC XML file
        settings.checkGridValuesInLCC(inLandCoverGrid, lccObj)
        
        # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
        outIdField = settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
         
        #Create the output table outside of metricCalc so that result can be added for multiple metrics
        AddMsg(timer.now() + " Creating output table")
        newtable, metricsFieldnameDict = table.tableWriterByClass(outTable, metricsBaseNameList,optionalGroupsList, 
                                                                                  metricConst, lccObj, outIdField, 
                                                                                  metricConst.additionalFields)
                
        #If clipLCGrid is selected, clip the input raster to the extent of the reporting unit theme or the to the extent
        #of the selected reporting unit(s). If the metric is susceptible to edge-effects (e.g., core and edge metrics, 
        #patch metrics) extend the clip envelope an adequate distance.

        if clipLCGrid == "true":
            AddMsg(timer.now() + " Reducing input Land cover grid to smallest recommended size...")
            
            # from . import utils
            from arcpy import env        
            _startingWorkSpace= env.workspace
            env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))
            pathRoot = os.path.splitext(inLandCoverGrid)[0]
            namePrefix = "%s_%s" % (metricConst.shortName, os.path.basename(pathRoot))
            scratchName = arcpy.CreateScratchName(namePrefix,"","RasterDataset")
            inLandCoverGrid = raster.clipGridByBuffer(inReportingUnitFeature, scratchName, inLandCoverGrid, inMaxSeparation)
            env.workspace = _startingWorkSpace
            
            AddMsg(timer.now() + " Reduction complete")
        
            
        # Run metric calculate for each metric in list
        for m in metricsBaseNameList:
            # Subclass that overrides specific functions for the MDCP calculation
            class metricCalcPM(metricCalc):

                def _replaceLCGrid(self):
                    # replace the inLandCoverGrid
                    AddMsg(self.timer.now() + " Creating Patch Grid for Class:"+m)
                    scratchNameReference = [""]
                    self.inLandCoverGrid = raster.createPatchRaster(m, self.lccObj, self.lccClassesDict, self.inLandCoverGrid,
                                                                          self.metricConst, self.maxSeparation,
                                                                          self.minPatchSize, processingCellSize, timer,
                                                                          scratchNameReference)
                    self.scratchNameToBeDeleted = scratchNameReference[0]
                    AddMsg(self.timer.now() + " Patch Grid Completed for Class:"+m)

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
                    settings.checkGridCellDimensions(self.inLandCoverGrid)
                        
                # Update calculateMetrics to populate Patch Metrics and MDCP
                def _calculateMetrics(self):
                    
                    AddMsg(self.timer.now() + " Calculating Patch Numbers by Reporting Unit for Class:" + m)
                     
                    # calculate Patch metrics
                    self.pmResultsDict = calculate.getPatchNumbers(self.outIdField, self.newTable, self.reportingUnitIdField, self.metricsFieldnameDict,
                                                      self.zoneAreaDict, self.metricConst, m, self.inReportingUnitFeature, 
                                                      self.inLandCoverGrid, processingCellSize, conversionFactor)
 
                    AddMsg(timer.now() + " Patch analysis has been run for Class:" + m)
                    
                    # get class name (may have been modified from LCC XML input by ATtILA)
                    outClassName = metricsFieldnameDict[m][1]
                    
                    if mdcpYN == "true": #calculate MDCP value
                    
                        AddMsg(self.timer.now() + " Calculating MDCP for Class:" + m)
                        
                        # create and name intermediate data layers
                        rastoPolyFeatureName = ("%s_%s_%s" % (metricConst.shortName, outClassName, metricConst.rastertoPoly))
                        rastoPolyFeature = files.nameIntermediateFile([rastoPolyFeatureName, "FeatureClass"], cleanupList)
                        rasterCentroidFeatureName = ("%s_%s_%s" % (metricConst.shortName, outClassName, metricConst.rastertoPoint))
                        rasterCentroidFeature = files.nameIntermediateFile([rasterCentroidFeatureName, "FeatureClass"], cleanupList)
                        polyDissolvedPatchFeatureName = ("%s_%s_%s" % (metricConst.shortName, outClassName, metricConst.polyDissolve))
                        polyDissolvedFeature = files.nameIntermediateFile([polyDissolvedPatchFeatureName, "FeatureClass"], cleanupList)
                        nearPatchTable = files.nameIntermediateFile([outClassName + metricConst.nearTable, "Dataset"], cleanupList)            
                        
                        # run the calculation script. get the results back as a dictionary keyed to RU id values
                        self.mdcpDict =  vector.tabulateMDCP(self.inLandCoverGrid, self.inReportingUnitFeature, 
                                                                   self.reportingUnitIdField, rastoPolyFeature, rasterCentroidFeature, polyDissolvedFeature,
                                                                   nearPatchTable, self.zoneAreaDict, timer, self.pmResultsDict)
                        # place the results into the output table
                        calculate.getMDCP(self.outIdField, self.newTable, self.mdcpDict, self.optionalGroupsList,
                                                 outClassName)
                        
                        AddMsg(self.timer.now() + " MDCP analysis has been run for Class:" + m)
                    
                    if self.saveIntermediates:
                        pass
                    else:
                        arcpy.Delete_management(pmCalc.scratchNameToBeDeleted)

            # Create new instance of metricCalc class to contain parameters
            pmCalc = metricCalcPM(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                      m, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
            
            pmCalc.newTable = newtable
            pmCalc.metricsFieldnameDict = metricsFieldnameDict
            pmCalc.maxSeparation = inMaxSeparation
            pmCalc.minPatchSize = inPatchSize
            pmCalc.outIdField = outIdField
            pmCalc.zoneAreaDict = zoneAreaDict
            
            #Run Calculation
            pmCalc.run()
            
            pmCalc.metricsBaseNameList = metricsBaseNameList

        if clipLCGrid == "true":
            arcpy.Delete_management(scratchName)     
    
    except Exception as e:
        errors.standardErrorHandling(e)

    finally:
        setupAndRestore.standardRestore()
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
        arcpy.RemoveIndex_management(inReportingUnitFeature, ruIdIndex)


def runCoreAndEdgeMetrics(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun,
                          inEdgeWidth, outTable, processingCellSize, snapRaster, optionalFieldGroups, clipLCGrid):
    """ Interface for script executing Core/Edge Metrics """

    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.caemConstants()
        # append the edge width distance value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inEdgeWidth
        # for the core and edge fields, add the edge width to the  field suffix
        for i, fldParams in enumerate(metricConst.additionalFields):
            fldParams[1] = metricConst.additionalSuffixes[i] + inEdgeWidth
        
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize,
                                                                                os.path.dirname(outTable),
                                                                                [metricsToRun,optionalFieldGroups] )

        lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        lccClassesDict = lccObj.classes
        
        outIdField = settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
        
        # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
        settings.checkExcludedValuesInClass(metricsBaseNameList, lccObj, lccClassesDict)
        
        # alert user if the land cover grid has values undefined in the LCC XML file
        settings.checkGridValuesInLCC(inLandCoverGrid, lccObj)
     
        #Create the output table outside of metricCalc so that result can be added for multiple metrics
        newtable, metricsFieldnameDict = table.tableWriterByClass(outTable, metricsBaseNameList,optionalGroupsList, 
                                                                                  metricConst, lccObj, outIdField, 
                                                                                  metricConst.additionalFields)
 
        #If clipLCGrid is selected, clip the input raster to the extent of the reporting unit theme or the to the extent
        #of the selected reporting unit(s). If the metric is susceptible to edge-effects (e.g., core and edge metrics, 
        #patch metrics) extend the clip envelope an adequate distance.       

        from arcpy import env        
        _tempEnvironment1 = env.workspace
        env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))


        if clipLCGrid == "true":
            timer = DateTimer()
            AddMsg("%s Reducing input Land cover grid to smallest recommended size..." % timer.now())
            pathRoot = os.path.splitext(inLandCoverGrid)[0]
            namePrefix = "%s_%s" % (metricConst.shortName, os.path.basename(pathRoot))
            scratchName = arcpy.CreateScratchName(namePrefix,"","RasterDataset")
            inLandCoverGrid = raster.clipGridByBuffer(inReportingUnitFeature, scratchName, inLandCoverGrid, inEdgeWidth)
            AddMsg("%s Reduction complete" % timer.now())
        
        # Run metric calculate for each metric in list
        for m in metricsBaseNameList:
        
            class metricCalcCAEM(metricCalc):
                # Subclass that overrides specific functions for the CoreAndEdgeAreaMetric calculation
                def _replaceLCGrid(self):
                    # replace the inLandCoverGrid
                    AddMsg("%s Generating core and edge grid for Class: %s" % (self.timer.now(), m.upper()))
                    scratchNameReference =  [""];
                    self.inLandCoverGrid = raster.getEdgeCoreGrid(m, self.lccObj, self.lccClassesDict, self.inLandCoverGrid, 
                                                                        self.inEdgeWidth, processingCellSize,
                                                                        self.timer, metricConst.shortName, scratchNameReference)
                    self.scratchNameToBeDeleted = scratchNameReference[0]
                    AddMsg("%s Core and edge grid complete for Class: %s" % (self.timer.now(), m.upper()))
                    
                    #Moved the save intermediate grid to the calcMetrics function so it would be one of the last steps to be performed

                #skip over make out table since it has already been made
                def _makeAttilaOutTable(self):
                    pass  
                
                def _makeTabAreaTable(self):
                    AddMsg("%s Generating a zonal tabulate area table" % self.timer.now())
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

                            arcpy.gp.TabulateArea_sa(self._inReportingUnitFeature, self._reportingUnitIdField, self._inLandCoverGrid, 
                                 self._value, self._tableName)
                            
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
                    settings.checkGridCellDimensions(self.inLandCoverGrid)
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
                    AddMsg("%s Core/Edge Ratio calculations are complete for class: %s" % (self.timer.now(), m.upper()))


            # Create new instance of metricCalc class to contain parameters
            caemCalc = metricCalcCAEM(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                          m, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
    
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

            
        if clipLCGrid == "true":
            arcpy.Delete_management(scratchName)

    except Exception as e:
        errors.standardErrorHandling(e)

    finally:
        setupAndRestore.standardRestore()
        env.workspace = _tempEnvironment1
        

def runRiparianLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                            metricsToRun, inStreamFeatures, inBufferDistance, enforceBoundary, outTable, processingCellSize, snapRaster,
                            optionalFieldGroups):
    """ Interface for script executing Riparian Land Cover Proportion Metrics """
    try:
        timer = DateTimer()
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.rlcpConstants()
        # append the buffer distance value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inBufferDistance.split()[0]
        # append the buffer distance value to the percent buffer field
        metricConst.qaCheckFieldParameters[5][0] = "%s%s" % (metricConst.pctBufferBase, inBufferDistance.split()[0])
        metricConst.qaCheckFieldParameters[4][0] = "%s%s" % (metricConst.totaPctBase, inBufferDistance.split()[0])

        class metricCalcRLCP(metricCalc):
            """ Subclass that overrides buffering function for the RiparianLandCoverProportions calculation """
            def _replaceRUFeatures(self):
                # check for duplicate ID entries in reportng unit feature. Perform dissolve if found
                self.duplicateIds = fields.checkForDuplicateValues(self.inReportingUnitFeature, self.reportingUnitIdField)
                # Initiate our flexible cleanuplist
                if rlcpCalc.saveIntermediates:
                    rlcpCalc.cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
                else:
                    rlcpCalc.cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
                if self.duplicateIds:
                    AddMsg("Duplicate ID values found in reporting unit feature. Forming multipart features...")
                    # Get a unique name with full path for the output features - will default to current workspace:
                    self.namePrefix = self.metricConst.shortName + "_Dissolve"+self.inBufferDistance.split()[0]
                    self.dissolveName = utils.files.nameIntermediateFile([self.namePrefix,"FeatureClass"], rlcpCalc.cleanupList)
                    self.inReportingUnitFeature = arcpy.Dissolve_management(self.inReportingUnitFeature, self.dissolveName, 
                                                                            self.reportingUnitIdField,"","MULTI_PART")
                    
                # Generate a default filename for the buffer feature class
                self.bufferName = "%s_Buffer%s" % (self.metricConst.shortName, self.inBufferDistance.replace(" ",""))
                
                # Generate the buffer area to use in the metric calculation
                if enforceBoundary == "true":
                    self.inReportingUnitFeature, self.cleanupList = vector.bufferFeaturesByIntersect(self.inStreamFeatures,
                                                                                     self.inReportingUnitFeature,
                                                                                     self.bufferName, self.inBufferDistance,
                                                                                     self.reportingUnitIdField,
                                                                                     self.cleanupList)
                else:
                    self.inReportingUnitFeature, self.cleanupList = vector.bufferFeaturesWithoutBorders(self.inStreamFeatures,
                                                                                     self.inReportingUnitFeature,
                                                                                     self.bufferName, self.inBufferDistance,
                                                                                     self.reportingUnitIdField,
                                                                                     self.cleanupList)
        
        # Create new instance of metricCalc class to contain parameters
        rlcpCalc = metricCalcRLCP(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                       metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)

        # Assign class attributes unique to this module.
        rlcpCalc.inStreamFeatures = inStreamFeatures
        rlcpCalc.inBufferDistance = inBufferDistance
        rlcpCalc.enforceBoundary = enforceBoundary

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
            landCoverValues = raster.getRasterValues(inLandCoverGrid)
            # get the list of excluded values that are found in the input land cover raster
            excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)
            
            if len(excludedValuesList) > 0:
                AddMsg("%s Excluded values found in the land cover grid. Calculating effective areas for each reporting unit..." % timer.now())
                # Use ATtILA's TabulateAreaTable operation to return an object where a tabulate area table can be easily queried.
                if rlcpCalc.saveIntermediates:
                    # name the table so that it will be saved
                    ruTableName = metricConst.shortName + globalConstants.ruTabulateAreaTableAbbv
                else:
                    ruTableName = None
                ruAreaTable = TabulateAreaTable(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, ruTableName, rlcpCalc.lccObj)
                
                for ruAreaTableRow in ruAreaTable:
                    key = ruAreaTableRow.zoneIdValue
                    area = ruAreaTableRow.effectiveArea
                    # make the value of key a list
                    rlcpCalc.reportingUnitAreaDict[key] = [rlcpCalc.reportingUnitAreaDict[key]]
                    rlcpCalc.reportingUnitAreaDict[key].append(area)
            
            else:
                AddMsg("%s No excluded values found in the land cover grid. Reporting unit effective area equals total reporting unit area. Recording reporting unit areas..." % timer.now())
                for aKey in rlcpCalc.testAreaDict.keys():
                    area = rlcpCalc.reportingUnitAreaDict[aKey]
                    # make the value of key a list
                    rlcpCalc.reportingUnitAreaDict[aKey] = [rlcpCalc.reportingUnitAreaDict[aKey]]
                    rlcpCalc.reportingUnitAreaDict[aKey].append(area)                    
        

        # Run Calculation
        rlcpCalc.run()      
       
    except Exception as e:
        errors.standardErrorHandling(e)

    finally:
        if not rlcpCalc.cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in rlcpCalc.cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
        setupAndRestore.standardRestore()

def runSamplePointLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                            metricsToRun, inPointFeatures, ruLinkField='', inBufferDistance='#', enforceBoundary='', outTable='', processingCellSize='', 
                            snapRaster='', optionalFieldGroups=''):
    """ Interface for script executing Sample Point Land Cover Proportion Metrics """

    try:
        timer = DateTimer()
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.splcpConstants()
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
                    AddMsg("Duplicate ID values found in reporting unit feature. Forming multipart features...")
                    # Get a unique name with full path for the output features - will default to current workspace:
                    self.namePrefix = self.metricConst.shortName + "_Dissolve"+self.inBufferDistance.split()[0]
                    self.dissolveName = utils.files.nameIntermediateFile([self.namePrefix,"FeatureClass"], splcpCalc.cleanupList)
                    self.inReportingUnitFeature = arcpy.Dissolve_management(self.inReportingUnitFeature, self.dissolveName, 
                                                                            self.reportingUnitIdField,"","MULTI_PART")
                    
                # Generate a default filename for the buffer feature class
                self.bufferName = "%s_Buffer%s" % (self.metricConst.shortName, self.inBufferDistance.replace(" ",""))
                
                # Buffer the points and use the output as the new reporting units
                if enforceBoundary == "true":
                    self.inReportingUnitFeature = vector.bufferFeaturesByID(self.inPointFeatures,
                                                                                  self.inReportingUnitFeature,
                                                                                  self.bufferName,self.inBufferDistance,
                                                                                  self.reportingUnitIdField,self.ruLinkField)
                    # Since we are replacing the reporting unit features with the buffered features we also need to replace
                    # the unique identifier field - which is now the ruLinkField.
                    self.reportingUnitIdField = self.ruLinkField
                else:
                    self.inReportingUnitFeature, self.cleanupList = vector.bufferFeaturesWithoutBorders(self.inPointFeatures,
                                                                                     self.inReportingUnitFeature,
                                                                                     self.bufferName, self.inBufferDistance,
                                                                                     self.reportingUnitIdField,
                                                                                     self.cleanupList)

        # Create new instance of metricCalc class to contain parameters
        splcpCalc = metricCalcSPLCP(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                       metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)

        # Assign class attributes unique to this module.
        splcpCalc.inPointFeatures = inPointFeatures
        splcpCalc.inBufferDistance = inBufferDistance
        splcpCalc.ruLinkField = ruLinkField
        splcpCalc.enforceBoundary = enforceBoundary
        splcpCalc.cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
        
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
            landCoverValues = raster.getRasterValues(inLandCoverGrid)
            # get the list of excluded values that are found in the input land cover raster
            excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)
            
            if len(excludedValuesList) > 0:
                AddMsg("%s Excluded values found in the land cover grid. Calculating effective areas for each reporting unit..." % timer.now())
                # Use ATtILA's TabulateAreaTable operation to return an object where a tabulate area table can be easily queried.
                if splcpCalc.saveIntermediates:
                    # name the table so that it will be saved
                    ruTableName = metricConst.shortName + globalConstants.ruTabulateAreaTableAbbv
                else:
                    ruTableName = None
                ruAreaTable = TabulateAreaTable(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, ruTableName, splcpCalc.lccObj)
                
                for ruAreaTableRow in ruAreaTable:
                    key = ruAreaTableRow.zoneIdValue
                    area = ruAreaTableRow.effectiveArea
                    # make the value of key a list
                    splcpCalc.reportingUnitAreaDict[key] = [splcpCalc.reportingUnitAreaDict[key]]
                    splcpCalc.reportingUnitAreaDict[key].append(area)
            
            else:
                AddMsg("%s No excluded values found in the land cover grid. Reporting unit effective area equals total reporting unit area. Recording reporting unit areas..." % timer.now())
                for aKey in splcpCalc.testAreaDict.keys():
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
        errors.standardErrorHandling(e)

    finally:
        if not splcpCalc.cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in splcpCalc.cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
        setupAndRestore.standardRestore()


def runLandCoverCoefficientCalculator(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName,
                                      lccFilePath, metricsToRun, outTable, processingCellSize, snapRaster,
                                      optionalFieldGroups):
    """Interface for script executing Land Cover Coefficient Calculator"""

    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcccConstants()

        # Create new LCC metric calculation subclass
        class metricCalcLCC(metricCalc):
            # Subclass that overrides specific functions for the land Cover Coefficient calculation
            def _makeAttilaOutTable(self):
                # Construct the ATtILA metric output table
                self.newTable, self.metricsFieldnameDict = table.tableWriterByCoefficient(self.outTable,
                                                                                                self.metricsBaseNameList,
                                                                                                self.optionalGroupsList,
                                                                                                self.metricConst, self.lccObj,
                                                                                                self.outIdField)
            def _calculateMetrics(self):
                # process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
                calculate.landCoverCoefficientCalculator(self.lccObj.values, self.metricsBaseNameList,
                                                               self.optionalGroupsList, self.metricConst, self.outIdField,
                                                               self.newTable, self.tabAreaTable, self.metricsFieldnameDict,
                                                               self.zoneAreaDict, self.conversionFactor)

        # Instantiate LCC metric calculation subclass
        lccCalc = metricCalcLCC(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                      metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)

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

        # Run calculation
        lccCalc.run()

    except Exception as e:
        errors.standardErrorHandling(e)

    finally:
        setupAndRestore.standardRestore()



def runRoadDensityCalculator(inReportingUnitFeature, reportingUnitIdField, inRoadFeature, outTable, roadClassField="",
                             streamRoadCrossings="#", roadsNearStreams="#", inStreamFeature="#", bufferDistance="#",
                             optionalFieldGroups="#"):
    """Interface for script executing Road Density Calculator"""
    from arcpy import env

    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        # Work on making as generic as possible
        ### Initialization
        # Start the timer
        timer = DateTimer()
        AddMsg(timer.start() + " Setting up environment variables")
        # Get the metric constants
        metricConst = metricConstants.rdmConstants()
        # Set the output workspace
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
            msg = "\nIntermediates are stored in this directory: {0}\n"
            arcpy.AddMessage(msg.format(env.workspace)) 
            #AddMsg(msg.format(env.workspace))
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
            # arcpy.AddWarning("Parallel processing is enabled. Results may vary from values calculated otherwise.")
            arcpy.AddWarning("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.")
            env.parallelProcessingFactor = None
        
        # Create a copy of the reporting unit feature class that we can add new fields to for calculations.  This 
        # is more appropriate than altering the user's input data. A dissolve will handle the condition of non-unique id
        # values and will also keep only the OID, shape, and reportingUnitIdField fields
        desc = arcpy.Describe(inReportingUnitFeature)
        tempName = "%s_%s" % (metricConst.shortName, desc.baseName)
        tempReportingUnitFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        AddMsg(timer.now() + " Creating temporary copy of " + desc.name)
        inReportingUnitFeature = arcpy.Dissolve_management(inReportingUnitFeature, os.path.basename(tempReportingUnitFeature), 
                                                           reportingUnitIdField,"","MULTI_PART")

        # Get the field properties for the unitID, this will be frequently used
        # If the field is numeric, it creates a text version of the field.
        uIDField = settings.processUIDField(inReportingUnitFeature,reportingUnitIdField)

        AddMsg(timer.now() + " Calculating reporting unit area")
        # Add a field to the reporting units to hold the area value in square kilometers
        # Check for existence of field.
        fieldList = arcpy.ListFields(inReportingUnitFeature,metricConst.areaFieldname)
        # Add and populate the area field (or just recalculate if it already exists
        unitArea = vector.addAreaField(inReportingUnitFeature,metricConst.areaFieldname)
        if not fieldList: # if the list of fields that exactly match the validated fieldname is empty...
            if not cleanupList[0] == "KeepIntermediates":
                # ...add this to the list of items to clean up at the end.
                pass
                # *** this was previously necessary when the field was added to the input - now that a copy of the input
                #     is used instead, this is not necessary.
                #cleanupList.append((arcpy.DeleteField_management,(inReportingUnitFeature,unitArea)))

        # If necessary, create a copy of the road feature class to remove M values.  The env.outputMFlag will work
        # for most datasets except for shapefiles with M and Z values. The Z value will keep the M value from being stripped
        # off. This is more appropriate than altering the user's input data.
        desc = arcpy.Describe(inRoadFeature)
        if desc.HasM or desc.HasZ:
            tempName = "%s_%s" % (metricConst.shortName, arcpy.Describe(inRoadFeature).baseName)
            tempLineFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
            AddMsg(timer.now() + " Creating temporary copy of " + desc.name)
            inRoadFeature = arcpy.FeatureClassToFeatureClass_conversion(inRoadFeature, env.workspace, os.path.basename(tempLineFeature))


        AddMsg(timer.now() + " Calculating road density")
        # Get a unique name for the merged roads and prep for cleanup
        mergedRoads = files.nameIntermediateFile(metricConst.roadsByReportingUnitName,cleanupList)

        # Calculate the density of the roads by reporting unit.
        mergedRoads, roadLengthFieldName = calculate.lineDensityCalculator(inRoadFeature,inReportingUnitFeature,
                                                                                 uIDField,unitArea,mergedRoads,
                                                                                 metricConst.roadDensityFieldName,
                                                                                 metricConst.roadLengthFieldName,
                                                                                 roadClassField,
                                                                                 metricConst.totalImperviousAreaFieldName)

        # Build and populate final output table.
        AddMsg(timer.now() + " Compiling calculated values into output table")
        arcpy.TableToTable_conversion(inReportingUnitFeature,os.path.dirname(outTable),os.path.basename(outTable))
        # Get a list of unique road class values
        if roadClassField:
            classValues = fields.getUniqueValues(mergedRoads,roadClassField)
        else:
            classValues = []
        # Compile a list of fields that will be transferred from the merged roads feature class into the output table
        fromFields = [roadLengthFieldName, metricConst.roadDensityFieldName,metricConst.totalImperviousAreaFieldName]
        # Transfer the values to the output table, pivoting the class values into new fields if necessary.
        table.transferField(mergedRoads,outTable,fromFields,fromFields,uIDField.name,roadClassField,classValues)
        
        # If the Streams By Roads (STXRD) box is checked...
        if streamRoadCrossings and streamRoadCrossings != "false":
            # If necessary, create a copy of the stream feature class to remove M values.  The env.outputMFlag will work
            # for most datasets except for shapefiles with M and Z values. The Z value will keep the M value from being stripped
            # off. This is more appropriate than altering the user's input data.
            desc = arcpy.Describe(inStreamFeature)
            if desc.HasM or desc.HasZ:
                tempName = "%s_%s" % (metricConst.shortName, desc.baseName)
                tempLineFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
                AddMsg(timer.now() + " Creating temporary copy of " + desc.name)
                inStreamFeature = arcpy.FeatureClassToFeatureClass_conversion(inStreamFeature, env.workspace, os.path.basename(tempLineFeature))

            
            AddMsg(timer.now() + " Calculating Stream and Road Crossings (STXRD)")
            # Get a unique name for the merged streams:
            mergedStreams = files.nameIntermediateFile(metricConst.streamsByReportingUnitName,cleanupList)

            # Calculate the density of the streams by reporting unit.
            mergedStreams, streamLengthFieldName = calculate.lineDensityCalculator(inStreamFeature,
                                                                                         inReportingUnitFeature,
                                                                                         uIDField,
                                                                                         unitArea,mergedStreams,
                                                                                         metricConst.streamDensityFieldName,
                                                                                         metricConst.streamLengthFieldName)

            # Get a unique name for the road/stream intersections:
            roadStreamMultiPoints = files.nameIntermediateFile(metricConst.roadStreamMultiPoints,cleanupList)
            # Get a unique name for the points of crossing:
            roadStreamIntersects = files.nameIntermediateFile(metricConst.roadStreamIntersects,cleanupList)
            # Get a unique name for the roads by streams summary table:
            roadStreamSummary = files.nameIntermediateFile(metricConst.roadStreamSummary,cleanupList)
            
            # Perform the roads/streams intersection and calculate the number of crossings and crossings per km
            vector.findIntersections(mergedRoads,inStreamFeature,mergedStreams,uIDField,roadStreamMultiPoints,
                                           roadStreamIntersects,roadStreamSummary,streamLengthFieldName,
                                           metricConst.xingsPerKMFieldName,roadClassField)
            
            # Transfer values to final output table.
            AddMsg(timer.now() + " Compiling calculated values into output table")
            # Compile a list of fields that will be transferred from the merged roads feature class into the output table
            fromFields = [streamLengthFieldName, metricConst.streamDensityFieldName]
            # Transfer the values to the output table, pivoting the class values into new fields if necessary.
            # Possible to add stream class values here if desired.
            table.transferField(mergedStreams,outTable,fromFields,fromFields,uIDField.name,None)
            # Transfer crossings fields - note the renaming of the count field.
            fromFields = ["FREQUENCY", metricConst.xingsPerKMFieldName]
            toFields = [metricConst.streamRoadXingsCountFieldname,metricConst.xingsPerKMFieldName]
            # Transfer the values to the output table, pivoting the class values into new fields if necessary.
            table.transferField(roadStreamSummary,outTable,fromFields,toFields,uIDField.name,roadClassField,classValues)
            

        if roadsNearStreams and roadsNearStreams != "false":
            AddMsg(timer.now() + " Calculating Roads Near Streams (RNS)")
            if not streamRoadCrossings or streamRoadCrossings == "false":  # In case merged streams haven't already been calculated:
                # Create a copy of the stream feature class, if necessary, to remove M values.  The env.outputMFlag will work
                # for most datasets except for shapefiles with M and Z values. The Z value will keep the M value from being stripped
                # off. This is more appropriate than altering the user's input data.
                desc = arcpy.Describe(inStreamFeature)
                if desc.HasM or desc.HasZ:
                    tempName = "%s_%s" % (metricConst.shortName, desc.baseName)
                    tempLineFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
                    AddMsg(timer.now() + " Creating temporary copy of " + desc.name)
                    inStreamFeature = arcpy.FeatureClassToFeatureClass_conversion(inStreamFeature, env.workspace, os.path.basename(tempLineFeature))
                
                # Get a unique name for the merged streams:
                mergedStreams = files.nameIntermediateFile(metricConst.streamsByReportingUnitName,cleanupList)
                # Calculate the density of the streams by reporting unit.
                mergedStreams, streamLengthFieldName = calculate.lineDensityCalculator(inStreamFeature,
                                                                                             inReportingUnitFeature,
                                                                                             uIDField,unitArea,mergedStreams,
                                                                                             metricConst.streamDensityFieldName,
                                                                                             metricConst.streamLengthFieldName)
            # Get a unique name for the buffered streams:
            streamBuffer = files.nameIntermediateFile(metricConst.streamBuffers,cleanupList)
            # Set a unique name for the undissolved  road/stream buffer intersections
            tmp1RdsNearStrms = files.nameIntermediateFile(metricConst.tmp1RNS,cleanupList)
            # Set a unique name for the undissolved  road/stream buffer intersections with reporting unit IDs attached
            tmp2RdsNearStrms = files.nameIntermediateFile(metricConst.tmp2RNS,cleanupList)
            # Get a unique name for the dissolved road/stream intersections:
            roadsNearStreams = files.nameIntermediateFile(metricConst.roadsNearStreams,cleanupList)
            
            # append the buffer distance to the rns field name base
            distString = bufferDistance.split()[0]
            rnsFieldName = metricConst.rnsFieldName+distString

            vector.roadsNearStreams(inStreamFeature, mergedStreams, bufferDistance, inRoadFeature, inReportingUnitFeature, streamLengthFieldName,uIDField, streamBuffer, 
                                          tmp1RdsNearStrms, tmp2RdsNearStrms, roadsNearStreams, rnsFieldName,metricConst.roadLengthFieldName, roadClassField)
            # Transfer values to final output table.
            AddMsg(timer.now() + " Compiling calculated values into output table")
            fromFields = [rnsFieldName]
            # Transfer the values to the output table, pivoting the class values into new fields if necessary.
            table.transferField(roadsNearStreams,outTable,fromFields,fromFields,uIDField.name,roadClassField,classValues)
    
    except Exception as e:
        errors.standardErrorHandling(e)

    finally:
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
        env.workspace = _tempEnvironment1
        env.outputMFlag = _tempEnvironment4
        env.outputZFlag = _tempEnvironment5
        env.parallelProcessingFactor = _tempEnvironment6


def runStreamDensityCalculator(inReportingUnitFeature, reportingUnitIdField, inLineFeature, outTable, lineCategoryField="", 
                               optionalFieldGroups="#"):
    """Interface for script executing Road Density Calculator"""
    from arcpy import env

    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        # Work on making as generic as possible
        ### Initialization
        # Start the timer
        timer = DateTimer()
        AddMsg(timer.start() + " Setting up environment variables")
        # Get the metric constants
        metricConst = metricConstants.sdmConstants()
        # Set the output workspace
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
            msg = "\nIntermediates are stored in this directory: {0}\n"
            arcpy.AddMessage(msg.format(env.workspace))
            #AddMsg(msg.format(env.workspace))
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
            # arcpy.AddWarning("Parallel processing is enabled. Results may vary from values calculated otherwise.")
            arcpy.AddWarning("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.")
            env.parallelProcessingFactor = None
        
        # Create a copy of the reporting unit feature class that we can add new fields to for calculations.  This 
        # is more appropriate than altering the user's input data. A dissolve will handle the condition of non-unique id
        # values and will also keep only the OID, shape, and reportingUnitIdField fields
        desc = arcpy.Describe(inReportingUnitFeature)
        tempName = "%s_%s" % (metricConst.shortName, desc.baseName)
        tempReportingUnitFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        AddMsg(timer.now() + " Creating temporary copy of " + desc.name)
        inReportingUnitFeature = arcpy.Dissolve_management(inReportingUnitFeature, os.path.basename(tempReportingUnitFeature), 
                                                           reportingUnitIdField,"","MULTI_PART")

        # Get the field properties for the unitID, this will be frequently used
        uIDField = settings.processUIDField(inReportingUnitFeature,reportingUnitIdField)

        AddMsg(timer.now() + " Calculating reporting unit area")
        # Add a field to the reporting units to hold the area value in square kilometers
        # Check for existence of field.
        fieldList = arcpy.ListFields(inReportingUnitFeature,metricConst.areaFieldname)
        # Add and populate the area field (or just recalculate if it already exists
        unitArea = vector.addAreaField(inReportingUnitFeature,metricConst.areaFieldname)
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
            tempName = "%s_%s" % (metricConst.shortName, desc.baseName)
            tempLineFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
            AddMsg(timer.now() + " Creating temporary copy of " + desc.name)
            inLineFeature = arcpy.FeatureClassToFeatureClass_conversion(inLineFeature, env.workspace, os.path.basename(tempLineFeature))


        AddMsg(timer.now() + " Calculating feature density")
        # Get a unique name for the merged roads and prep for cleanup
        mergedInLines = files.nameIntermediateFile(metricConst.linesByReportingUnitName,cleanupList)

        # Calculate the density of the roads by reporting unit.
        mergedInLines, lineLengthFieldName = calculate.lineDensityCalculator(inLineFeature,inReportingUnitFeature,
                                                                                 uIDField,unitArea,mergedInLines,
                                                                                 metricConst.lineDensityFieldName,
                                                                                 metricConst.lineLengthFieldName,
                                                                                 lineCategoryField)

        # Build and populate final output table.
        AddMsg(timer.now() + " Compiling calculated values into output table")
        arcpy.TableToTable_conversion(inReportingUnitFeature,os.path.dirname(outTable),os.path.basename(outTable))
        # Get a list of unique road class values
        if lineCategoryField:
            categoryValues = fields.getUniqueValues(mergedInLines,lineCategoryField)
        else:
            categoryValues = []
        # Compile a list of fields that will be transferred from the merged roads feature class into the output table
        fromFields = [lineLengthFieldName, metricConst.lineDensityFieldName]
        # Transfer the values to the output table, pivoting the class values into new fields if necessary.
        table.transferField(mergedInLines,outTable,fromFields,fromFields,uIDField.name,lineCategoryField,categoryValues)
        
    except Exception as e:
        errors.standardErrorHandling(e)

    finally:
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
        env.workspace = _tempEnvironment1
        env.outputMFlag = _tempEnvironment4
        env.outputZFlag = _tempEnvironment5
        env.parallelProcessingFactor = _tempEnvironment6
        

def runLandCoverDiversity(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, outTable, processingCellSize, 
                          snapRaster, optionalFieldGroups):
    """ Interface for script executing Land Cover Diversity Metrics """

    try:
        class metricLCDCalc:
            """ This class contains the  steps to perform a land cover diversity calculation."""

            # Initialization
            def __init__(self, inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, metricsToRun, outTable, 
                         processingCellSize, snapRaster, optionalFieldGroups, metricConst):
                self.timer = DateTimer()
                AddMsg(self.timer.start() + " Setting up environment variables")
                
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

                # If the user has checked the Intermediates option, name the tabulateArea table. This will cause it to be saved.
                self.tableName = None
                self.saveIntermediates = globalConstants.intermediateName in self.optionalGroupsList
                if self.saveIntermediates:
                    self.tableName = metricConst.shortName + globalConstants.tabulateAreaTableAbbv
                    
                
            def _housekeeping(self):
                # alert user if the land cover grid cells are not square (default to size along x axis)
                settings.checkGridCellDimensions(self.inLandCoverGrid)
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
                AddMsg(self.timer.now() + " Constructing the ATtILA metric output table")
                # Internal function to construct the ATtILA metric output table
                self.newTable, self.metricsFieldnameDict = table.tableWriterNoLcc(self.outTable,
                                                                                        self.metricsBaseNameList,
                                                                                        self.optionalGroupsList,
                                                                                        self.metricConst,
                                                                                        self.outIdField)
                
            def _makeTabAreaTable(self):
                AddMsg(self.timer.now() + " Generating a zonal tabulate area table")
                # Internal function to generate a zonal tabulate area table
                self.tabAreaTable = TabulateAreaTable(self.inReportingUnitFeature, self.reportingUnitIdField,
                                                      self.inLandCoverGrid, self.tableName)
                
            def _calculateMetrics(self):
                AddMsg(self.timer.now() + " Processing the tabulate area table and computing metric values")
                # Internal function to process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
                calculate.landCoverDiversity(self.metricConst, self.outIdField, 
                                                   self.newTable, self.tabAreaTable, self.zoneAreaDict)
                
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
                

        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcdConstants()
        metricsToRun = metricConst.fixedMetricsToRun
        
        lcdCalc = metricLCDCalc(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, metricsToRun, outTable, 
                                processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        lcdCalc.run()

    except Exception as e:
        errors.standardErrorHandling(e)

    finally:
        setupAndRestore.standardRestore()


def runPopulationDensityCalculator(inReportingUnitFeature, reportingUnitIdField, inCensusFeature, inPopField, outTable,
                                   popChangeYN, inCensusFeature2, inPopField2, optionalFieldGroups):
    """ Interface for script executing Population Density Metrics """
    from arcpy import env

    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        ### Initialization
        # Start the timer
        timer = DateTimer()
        AddMsg(timer.start() + " Setting up environment variables")

        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.pdmConstants()

        # Set the output workspace
        _tempEnvironment1 = env.workspace
        env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))
        # Strip the description from the "additional option" and determine whether intermediates are stored.
        processed = parameters.splitItemsAndStripDescriptions(optionalFieldGroups, globalConstants.descriptionDelim)
        if globalConstants.intermediateName in processed:
            msg = "\nIntermediates are stored in this directory: {0}\n"
            arcpy.AddMessage(msg.format(env.workspace))
            #AddMsg(msg.format(env.workspace))
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
            # arcpy.AddWarning("Parallel processing is enabled. Results may vary from values calculated otherwise.")
            arcpy.AddWarning("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.")
            env.parallelProcessingFactor = None
        
        # Create a copy of the reporting unit feature class that we can add new fields to for calculations.  This 
        # is more appropriate than altering the user's input data. A dissolve will handle the condition of non-unique id
        # values and will also keep only the OID, shape, and reportingUnitIdField fields
        desc = arcpy.Describe(inReportingUnitFeature)
        tempName = "%s_%s_" % (metricConst.shortName, desc.baseName)
        tempReportingUnitFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
        AddMsg(timer.now() + " Creating temporary copy of " + desc.name)
        inReportingUnitFeature = arcpy.Dissolve_management(inReportingUnitFeature, os.path.basename(tempReportingUnitFeature), 
                                                           reportingUnitIdField,"","MULTI_PART")

        # Add and populate the area field (or just recalculate if it already exists
        ruArea = vector.addAreaField(inReportingUnitFeature,metricConst.areaFieldname)
        
        # Build the final output table.
        AddMsg(timer.now() + " Creating output table")
        arcpy.TableToTable_conversion(inReportingUnitFeature,os.path.dirname(outTable),os.path.basename(outTable))
        
        AddMsg(timer.now() + " Calculating population density")
        # Create an index value to keep track of intermediate outputs and fieldnames.
        index = ""
        #if popChangeYN is checked:
        if popChangeYN == "true":
            index = "1"
        # Perform population density calculation for first (only?) population feature class
        calculate.getPopDensity(inReportingUnitFeature,reportingUnitIdField,ruArea,inCensusFeature,inPopField,
                                      env.workspace,outTable,metricConst,cleanupList,index)

        #if popChangeYN is checked:
        if popChangeYN == "true":
            index = "2"
            AddMsg(timer.now() + " Calculating population density for second feature class")
            # Perform population density calculation for second population feature class
            calculate.getPopDensity(inReportingUnitFeature,reportingUnitIdField,ruArea,inCensusFeature2,inPopField2,
                                          env.workspace,outTable,metricConst,cleanupList,index)
            
            AddMsg(timer.now() + " Calculating population change")
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
            vector.addCalculateField(outTable,metricConst.populationChangeFieldName,calcExpression,codeBlock)       

        AddMsg(timer.now() + " Calculation complete")
    except Exception as e:
        errors.standardErrorHandling(e)

    finally:
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
        env.workspace = _tempEnvironment1
        env.parallelProcessingFactor = _tempEnvironment6
        

def runPopulationInFloodplainMetrics(inReportingUnitFeature, reportingUnitIdField, inCensusDataset, inPopField, inFloodplainDataset, 
                                     outTable, optionalFieldGroups):
    """ Interface for script executing Population In Floodplain Metrics """
    from arcpy import env

    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        ### Initialization
        # Start the timer
        timer = DateTimer()
        AddMsg(timer.start() + " Setting up environment variables")
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
            # arcpy.AddWarning("Parallel processing is enabled. Results may vary from values calculated otherwise.")
            arcpy.AddWarning("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.")
            env.parallelProcessingFactor = None
        
        # set the workspace for ATtILA intermediary files
        env.workspace = environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))
            
        # Strip the description from the "additional option" and determine whether intermediates are stored.
        processed = parameters.splitItemsAndStripDescriptions(optionalFieldGroups, globalConstants.descriptionDelim)
        if globalConstants.intermediateName in processed:
            msg = "\nIntermediates are stored in this directory: {0}\n"
            arcpy.AddMessage(msg.format(env.workspace))

            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
        
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.pifmConstants()
        popCntFields = metricConst.populationCountFieldNames
            
        # Do a Describe on the population and floodplain inputs. Determine if they are raster or polygon
        descCensus = arcpy.Describe(inCensusDataset)
        descFldpln = arcpy.Describe(inFloodplainDataset)   

        # Create an index value to keep track of intermediate outputs and field names.
        index = 0
        
        # Generate name for reporting unit population count table.
        suffix = metricConst.fieldSuffix[index]
        popTable_RU = files.nameIntermediateFile([metricConst.popCntTableName + suffix,'Dataset'],cleanupList)

        ### Metric Calculation
        AddMsg(timer.now() + " Calculating population within each reporting unit")        
         
        if descCensus.datasetType == "RasterDataset":
            # set the raster environments so the raster operations align with the census grid cell boundaries
            env.snapRaster = inCensusDataset
            env.cellSize = descCensus.meanCellWidth
            
            # calculate the population for the reporting unit using zonal statistics as table
            arcpy.sa.ZonalStatisticsAsTable(inReportingUnitFeature, reportingUnitIdField, inCensusDataset, popTable_RU, "DATA", "SUM")
            
            # Rename the population count field.
            outPopField = metricConst.populationCountFieldNames[index]
            arcpy.AlterField_management(popTable_RU, "SUM", outPopField, outPopField)
            
            # Set variables for the floodplain population calculations
            index = 1
            suffix = metricConst.fieldSuffix[index]
            popTable_FP = files.nameIntermediateFile([metricConst.popCntTableName + suffix,'Dataset'],cleanupList)
            
            if descFldpln.datasetType == "RasterDataset":
                # Use SetNull to eliminate non-floodplain areas and to replace the floodplain cells with values from the 
                # PopulationRaster. The snap raster, and cell size have already been set to match the census raster
                AddMsg(timer.now() + " Setting non-floodplain areas to NULL")
                delimitedVALUE = arcpy.AddFieldDelimiters(inFloodplainDataset,"VALUE")
                # whereClause = delimitedVALUE+" <> 1"
                whereClause = delimitedVALUE+" = 0"
                inCensusDataset = arcpy.sa.SetNull(inFloodplainDataset, inCensusDataset, whereClause)
                
                if globalConstants.intermediateName in processed:
                    namePrefix = "%s_" % (metricConst.floodplainPopName)
                    scratchName = arcpy.CreateScratchName(namePrefix, "", "RasterDataset")
                    inCensusDataset.save(scratchName)
                    AddMsg(timer.now() + " Save intermediate grid complete: "+os.path.basename(scratchName))
                    
                 
            else: # floodplain feature is a polygon
                # Assign the reporting unit ID to intersecting floodplain polygon segments using Identity
                fileNameBase = descFldpln.baseName
                tempName = "%s_%s_%s" % (metricConst.shortName, fileNameBase, "Identity")
                tempPolygonFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
                AddMsg(timer.now() + " Assigning reporting unit IDs to intersecting floodplain features")
                arcpy.Identity_analysis(inFloodplainDataset, inReportingUnitFeature, tempPolygonFeature)
                inReportingUnitFeature = tempPolygonFeature
            
            AddMsg(timer.now() + " Calculating population within floodplain areas for each reporting unit")
            # calculate the population for the reporting unit using zonal statistics as table
            # The snap raster, and cell size have been set to match the census raster
            arcpy.sa.ZonalStatisticsAsTable(inReportingUnitFeature, reportingUnitIdField, inCensusDataset, popTable_FP, "DATA", "SUM")
                
            # Rename the population count field.
            outPopField = metricConst.populationCountFieldNames[index]
            arcpy.AlterField_management(popTable_FP, "SUM", outPopField, outPopField)

        else: # census features are polygons
            # Check that the user supplied a population field
            if len(inPopField) == 0:
                raise errors.attilaException(errorConstants.missingFieldError)
                
            
            # Create a copy of the census feature class that we can add new fields to for calculations.
            fieldMappings = arcpy.FieldMappings()
            fieldMappings.addTable(inCensusDataset)
            [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name != inPopField]
        
            tempName = "%s_%s" % (metricConst.shortName, descCensus.baseName)
            tempCensusFeature = files.nameIntermediateFile([tempName + "_Work","FeatureClass"],cleanupList)
            inCensusDataset = arcpy.FeatureClassToFeatureClass_conversion(inCensusDataset,env.workspace,
                                                                                 os.path.basename(tempCensusFeature),"",
                                                                                 fieldMappings)
            
            # Add a dummy field to the copied census feature class and calculate it to a value of 1.
            classField = "tmpClass"
            arcpy.AddField_management(inCensusDataset,classField,"SHORT")
            arcpy.CalculateField_management(inCensusDataset,classField,1)
            
            # Perform population count calculation for the reporting unit
            calculate.getPolygonPopCount(inReportingUnitFeature,reportingUnitIdField,inCensusDataset,inPopField,
                                      classField,popTable_RU,metricConst,index)
        
            # Set variables for the floodplain population calculations   
            index = 1
            suffix = metricConst.fieldSuffix[index]
            popTable_FP = files.nameIntermediateFile([metricConst.popCntTableName + suffix,'Dataset'],cleanupList)
            
            if descFldpln.datasetType == "RasterDataset":
                # Convert the Raster floodplain to Polygon
                AddMsg(timer.now() + " Converting floodplain raster to a polygon feature")
                delimitedVALUE = arcpy.AddFieldDelimiters(inFloodplainDataset,"VALUE")
                whereClause = delimitedVALUE+" = 0"
                nullGrid = arcpy.sa.SetNull(inFloodplainDataset, 1, whereClause)
                tempName = "%s_%s" % (metricConst.shortName, descFldpln.baseName + "_Poly")
                tempPolygonFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
                
                # This may fail if a polgyon created is too large. Need a routine to more elegantly reduce the maxVertices in any one polygon
                maxVertices = 250000
                try:
                    inFloodplainDataset = arcpy.RasterToPolygon_conversion(nullGrid,tempPolygonFeature,"NO_SIMPLIFY","VALUE","",maxVertices)
                except:
                    arcpy.AddMessage("Converting raster to polygon with maximum vertices technique")
                    maxVertices = maxVertices / 2
                    inFloodplainDataset = arcpy.RasterToPolygon_conversion(nullGrid,tempPolygonFeature,"NO_SIMPLIFY","VALUE","",maxVertices)
                
            else: # floodplain input is a polygon dataset
                # Create a copy of the floodplain feature class that we can add new fields to for calculations.
                # To reduce operation overhead and disk space, keep only the first field of the floodplain feature
                fieldMappings = arcpy.FieldMappings()
                fieldMappings.addTable(inFloodplainDataset)
                [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name != fieldMappings.fields[0].name]
                
                tempName = "%s_%s" % (metricConst.shortName, descFldpln.baseName)
                tempFldplnFeature = files.nameIntermediateFile([tempName + "_Work","FeatureClass"],cleanupList)
                inFloodplainDataset = arcpy.FeatureClassToFeatureClass_conversion(inFloodplainDataset,env.workspace,
                                                                                     os.path.basename(tempFldplnFeature),"",
                                                                                     fieldMappings)
                
            # Add a field and calculate it to a value of 1. This field will use as the classField in Tabulate Intersection operation below
            classField = "tmpClass"
            arcpy.AddField_management(inFloodplainDataset,classField,"SHORT")
            arcpy.CalculateField_management(inFloodplainDataset,classField,1)

            # intersect the floodplain polygons with the reporting unit polygons
            fileNameBase = descFldpln.baseName
            # need to eliminate the tool's shortName from the fileNameBase if the floodplain polygon was derived from a raster
            fileNameBase = fileNameBase.replace(metricConst.shortName+"_","")
            tempName = "%s_%s_%s" % (metricConst.shortName, fileNameBase, "Identity")
            tempPolygonFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
            AddMsg(timer.now() + " Assigning reporting unit IDs to floodplain features")
            arcpy.Identity_analysis(inFloodplainDataset, inReportingUnitFeature, tempPolygonFeature)
    
            AddMsg(timer.now() + " Calculating population within floodplain areas for each reporting unit")
            # Perform population count calculation for second feature class area
            calculate.getPolygonPopCount(tempPolygonFeature,reportingUnitIdField,inCensusDataset,inPopField,
                                          classField,popTable_FP,metricConst,index)
        
        # Build and populate final output table.
        AddMsg(timer.now() + " Calculating the percent of the population that is within a floodplain")
        
        # Construct a list of fields to retain in the output metrics table
        keepFields = metricConst.populationCountFieldNames
        keepFields.append(reportingUnitIdField)
        fieldMappings = arcpy.FieldMappings()
        fieldMappings.addTable(popTable_RU)
        [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name not in keepFields]

        arcpy.TableToTable_conversion(popTable_RU,os.path.dirname(outTable),os.path.basename(outTable),"",fieldMappings)
        
        # Compile a list of fields that will be transferred from the floodplain population table into the output table
        fromFields = [popCntFields[index]]
        toField = popCntFields[index]
        # Transfer the values to the output table
        table.transferField(popTable_FP,outTable,fromFields,[toField],reportingUnitIdField,None)
        
        # Set up a calculation expression for population change
        calcExpression = "getPopPercent(!"+popCntFields[0]+"!,!"+popCntFields[1]+"!)"
        codeBlock = """def getPopPercent(pop1,pop2):
                            if pop1 == 0:
                                if pop2 == 0:
                                    return 0
                                else:
                                    return 1
                            else:
                                return (pop2/pop1)*100"""
            
        # Calculate the percent population within floodplain
        vector.addCalculateField(outTable,metricConst.populationProportionFieldName,calcExpression,codeBlock)   

        AddMsg(timer.now() + " Calculation complete")
    except Exception as e:
        errors.standardErrorHandling(e)

    finally:
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
        env.snapRaster = _tempEnvironment0
        env.workspace = _tempEnvironment1
        env.cellSize = _tempEnvironment2
        env.parallelProcessingFactor = _tempEnvironment6
        

def runPopulationLandCoverViews(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                    metricsToRun, viewRadius, minPatchSize="", inCensusRaster="", outTable="", processingCellSize="", 
                    snapRaster="", optionalFieldGroups=""):
    """ Interface for script executing Population With Potential Views Metrics """
    try:
       
        ''' Initialization Steps '''
        from arcpy import env
        timer = DateTimer()
        AddMsg(timer.start() + " Setting up environment variables")
         
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize,
                                                                                os.path.dirname(outTable),
                                                                                [metricsToRun,optionalFieldGroups] )
 
        # XML Land Cover Coding file loaded into memory
        lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        lccClassesDict = lccObj.classes
        # Get the lccObj values dictionary. This contains all the properties of each value specified in the Land Cover Classification XML    
        lccValuesDict = lccObj.values
        # create a list of all the grid values in the selected land cover grid
        landCoverValues = raster.getRasterValues(inLandCoverGrid)
        # get the frozenset of excluded values (i.e., values marked as EXCLUDED in the Land Cover Classification XML)
        excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)
         
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.plcvConstants()

        # # append the view radius distance value to the field suffix
        # newSuffix = metricConst.fieldSuffix + viewRadius
        # metricConst.fieldParameters[1] = newSuffix
        # # for the output fields, add the input view radius to the field suffix
        # for i, fldParams in enumerate(metricConst.additionalFields):
        #     fldParams[1] = metricConst.additionalSuffixes[i] + viewRadius
         
         
        ''' Housekeeping Steps ''' 
        # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
        settings.checkExcludedValuesInClass(metricsBaseNameList, lccObj, lccClassesDict)
        # alert user if the land cover grid has values undefined in the LCC XML file
        settings.checkGridValuesInLCC(inLandCoverGrid, lccObj)
        # alert user if the land cover grid cells are not square (default to size along x axis)
        settings.checkGridCellDimensions(inLandCoverGrid)
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
        newtable, metricsFieldnameDict = table.tableWriterByClass(outTable, metricsBaseNameList,optionalGroupsList, 
                                                                                  metricConst, lccObj, outIdField, 
                                                                                  metricConst.additionalFields)

        # Newtable is unnecessary. It will be reconstructed later in the script via the metricsFieldnameDict. Need to
        # remove the table for now as it will cause an error if overwriting Geoprocessing outputs is not allowed.
        if arcpy.Exists(newtable):
            arcpy.Delete_management(newtable)
            
        ''' Metric Computations '''
 
        # Generate table with population counts by reporting unit
        AddMsg(timer.now() + " Calculating population within each reporting unit") 
        index = 0

        populationTable, populationField = table.createPolygonValueCountTable(inReportingUnitFeature,
                                                                              reportingUnitIdField,
                                                                              inCensusRaster,
                                                                              "",
                                                                              newtable,
                                                                              metricConst,
                                                                              index,
                                                                              cleanupList)
        
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
            #AddMsg(("Determining population with minimal views of {} class...").format(m.upper()))  
            viewGrid = raster.getPatchViewGrid(m, classValuesList, excludedValuesList, inLandCoverGrid, landCoverValues, 
                                          viewRadius, conValues, minPatchSize, timer, saveIntermediates, metricConst)
  
            # save the intermediate raster if save intermediates option has been chosen 
            if saveIntermediates:
                namePrefix = "%s_%s%s_" % (metricConst.shortName, m.upper(), metricConst.viewRasterOutputName)
                scratchName = arcpy.CreateScratchName(namePrefix, "", "RasterDataset")
                viewGrid.save(scratchName)
                
                # add a CATEGORY field for raster labels; make it large enough to hold your longest category label.
                arcpy.BuildRasterAttributeTable_management(viewGrid, "Overwrite")
                arcpy.AddField_management(viewGrid, "CATEGORY", "TEXT", "#", "#", "20")
                # The categoryDict should be in the format {integer1 : "category1 string", integer2: "category2 string", etc}
                categoryDict = {1: "Potential View Area"}
                raster.updateCategoryLabels(viewGrid, categoryDict)
                
                AddMsg(timer.now() + " Save intermediate grid complete: "+os.path.basename(scratchName))
                             
            # convert view area raster to polygon
            AddMsg(timer.now() + " Converting view raster to a polygon feature")
            # get output name for projected viewPolygon
            namePrefix = "%s_%s%s_" % (metricConst.shortName, m.upper(), metricConst.viewPolygonOutputName)
            viewPolygonFeature = files.nameIntermediateFile([namePrefix + "","FeatureClass"],cleanupList)
            
            # Check if viewPolygon is the same projection as the census raster, if not project it
            if transformMethod != "":
                arcpy.conversion.RasterToPolygon(viewGrid,"tempPoly","NO_SIMPLIFY","Value","SINGLE_OUTER_PART",None)
                arcpy.Project_management("tempPoly",viewPolygonFeature,spatialCensus,transformMethod)
                arcpy.Delete_management("tempPoly")
            else:
                arcpy.conversion.RasterToPolygon(viewGrid,viewPolygonFeature,"NO_SIMPLIFY","Value","SINGLE_OUTER_PART",None)
            
            # Save the current environment settings, then set to match the census raster 
            tempEnvironment0 = env.snapRaster
            tempEnvironment1 = env.cellSize            
            env.snapRaster = inCensusRaster
            env.cellSize = descCensus.meanCellWidth
            AddMsg("Setting geoprocessing environmental parameters for snap raster and cell size to match %s" % descCensus.baseName)
            
            # Extract Census pixels which are in the view area
            AddMsg(("{} Extracting population pixels within the potential view area...").format(timer.now())) 
            viewPopGrid = arcpy.sa.ExtractByMask(inCensusRaster, viewPolygonFeature)
            
            # save the intermediate raster if save intermediates option has been chosen 
            if saveIntermediates:
                namePrefix = "%s_%s%s_" % (metricConst.shortName, m.upper(), metricConst.areaPopRasterOutputName)
                scratchName = arcpy.CreateScratchName(namePrefix, "", "RasterDataset")
                viewPopGrid.save(scratchName)
                AddMsg(timer.now() + " Save intermediate grid complete: "+os.path.basename(scratchName))
                
            # Calculate the extracted population for each reporting unit
            AddMsg(timer.now() + " Calculating population within minimal-view areas for each reporting unit")
            namePrefix = "%s_%s%s_" % (metricConst.shortName, m.upper(), metricConst.areaValueCountTableName)
            areaPopTable = files.nameIntermediateFile([namePrefix + "","Dataset"],cleanupList)
            arcpy.sa.ZonalStatisticsAsTable(inReportingUnitFeature,reportingUnitIdField,viewPopGrid,areaPopTable,"DATA","SUM")
            
            # reset the environments
            AddMsg("Restoring snap raster geoprocessing environmental parameter to %s" % os.path.basename(tempEnvironment0))
            AddMsg("Restoring cell size geoprocessing environmental parameter to %s" % tempEnvironment1)
            env.snapRaster = tempEnvironment0
            env.cellSize = tempEnvironment1
            
            # get the field that will be transferred from the view population table into the output table
            fromField = "SUM"
            toField = metricsFieldnameDict[m][0] #generated metric field name for the current land cover class
            
            # Transfer the fromField values to the output table
            table.addJoinCalculateField(areaPopTable, populationTable, fromField, toField, reportingUnitIdField)
            
            # Assign 0 to reporting units where no population was calculated in the view/non-view area
            calculate.replaceNullValues(populationTable, toField, metricConst.valueWhenNULL)

            # Replace the inField name suffix to identify the calcField     
            calcField = toField.replace(metricConst.fieldSuffix,metricConst.pctSuffix)
            
            # Calculate the percent population within view area
            calculate.percentageValue(populationTable, toField, populationField, calcField)

            # Calculate the population for minimum view
            calcField_WOVPOP = toField.replace(metricConst.fieldSuffix,metricConst.wovFieldSuffix)
            calculate.differenceValue(populationTable, populationField, toField, calcField_WOVPOP)

            # Calculate the percent population without view area
            calcField_WOVPCT = calcField_WOVPOP.replace(metricConst.wovFieldSuffix,metricConst.wovPctSuffix)
            calculate.percentageValue(populationTable, calcField_WOVPOP, populationField, calcField_WOVPCT)
            AddMsg(timer.now() + " Calculation complete")
           
            # delete temporary features
            if arcpy.Exists("tempPoly"):
                arcpy.Delete_management("tempPoly")
                
    except Exception as e:
        errors.standardErrorHandling(e)
 
    finally:
        setupAndRestore.standardRestore()
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)

                

def runFacilityLandCoverViews(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                     metricsToRun, inFacilityFeature, viewRadius, viewThreshold, outTable="", processingCellSize="", 
                     snapRaster="", optionalFieldGroups=""):
    #""" Interface for script executing Facility Land Cover Views Metrics """
    try:

        metricConst = metricConstants.flcvConstants()
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
                    AddMsg("Duplicate ID values found in reporting unit feature. Forming multipart features...")
                    # Get a unique name with full path for the output features - will default to current workspace:            
                    self.namePrefix = self.metricConst.shortName + "_FacDissolve"+self.inBufferDistance.split()[0]+"_"
                    self.dissolveName = utils.files.nameIntermediateFile([self.namePrefix,"FeatureClass"], flcvCalc.cleanupList)
                    self.inReportingUnitFeature = arcpy.Dissolve_management(self.inReportingUnitFeature, self.dissolveName, 
                                                                            self.reportingUnitIdField,"","MULTI_PART")

                # Make a temporary facility point layer so that a field of the same name as reportingUnitIdField could be deleted
                # Get a unique name with full path for the output features - will default to current workspace:
                self.namePrefix = self.metricConst.facilityCopyName+self.viewRadius.split()[0]+"_"
                self.inPointFacilityName = utils.files.nameIntermediateFile([self.namePrefix,"FeatureClass"], flcvCalc.cleanupList)
                AddMsg(("{0} Creating a copy of the Facility feature. Intermediate: {1}").format(self.timer.now(), os.path.basename(self.inPointFacilityName)))
                self.inPointFacilityFeature = arcpy.FeatureClassToFeatureClass_conversion(self.inFacilityFeature, arcpy.env.workspace, os.path.basename(self.inPointFacilityName))

                # Delete all fields from the copied facilities feature
                AddMsg(("{0} Deleting unnecessary fields from {1}").format(self.timer.now(), os.path.basename(self.inPointFacilityName)))
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
                AddMsg(("{0} Assigning reporting unit ID to {1}. Intermediate: {2}").format(self.timer.now(), os.path.basename(self.inPointFacilityName), os.path.basename(self.intersectResultName)))
                self.intersectResult = arcpy.Intersect_analysis([self.inPointFacilityFeature,self.inReportingUnitFeature],self.intersectResultName,"NO_FID","","POINT")

                # Buffer the facility features with the reporting unit IDs to desired distance
                # Get a unique name with full path for the output features - will default to current workspace:
                self.namePrefix = self.metricConst.viewBufferName+self.viewRadius.split()[0]+"_"
                self.bufferResultName = utils.files.nameIntermediateFile([self.namePrefix,"FeatureClass"], flcvCalc.cleanupList)
                AddMsg(("{0} Buffering {1} to {2}. Intermediate: {3}").format(self.timer.now(), os.path.basename(self.intersectResultName), viewRadius, os.path.basename(self.bufferResultName)))
                self.bufferResult = arcpy.Buffer_analysis(self.intersectResult,self.bufferResultName,viewRadius,"","","NONE","", "PLANAR")

                self.inReportingUnitFeature = self.bufferResult
                

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
                AddMsg("%s Constructing facility buffer land cover proportions table. Intermediate: %s" % (self.timer.now(), os.path.basename(self.facilityLCPTable)))
                self.lcpTable, self.lcpMetricsFieldnameDict = table.tableWriterByClass(self.facilityLCPTable,
                                                                                    self.metricsBaseNameList,
                                                                                    self.facilityOptionsList,
                                                                                    self.metricConst, self.lccObj,
                                                                                    self.facilityIdField)
                # Restore the output metric field name parameters 
                self.metricConst.fieldParameters = self.oldFieldParameters
                
                # Construct the ATtILA metric output table
                AddMsg("%s Constructing the ATtILA metric output table: %s" % (self.timer.now(), os.path.basename(self.outTable)))
                # Internal function to construct the ATtILA metric output table
                self.newTable, self.metricsFieldnameDict = table.tableWriterByClass(self.outTable,
                                                                                  self.metricsBaseNameList,
                                                                                  self.optionalGroupsList,
                                                                                  self.metricConst, self.lccObj,
                                                                                  self.outIdField,
                                                                                  self.metricConst.additionalFields)
                
                # Add an additional field for the facility counts within each reporting unit. Used AddFields so that the 
                # field properties could be defined and retrieved from the metric constants. 
                arcpy.management.AddFields(self.newTable, self.metricConst.singleFields)


            def _makeTabAreaTable(self):
                AddMsg(self.timer.now() + " Generating a zonal tabulate area table for view buffer areas")
                # Make a tabulate area table. Use the facility id field as the Zone field to calculate values for each
                # facility buffer area instead of the reporting unit as a whole. 
                self.tabAreaTable = TabulateAreaTable(self.inReportingUnitFeature, self.facilityIdField.name,
                                                      self.inLandCoverGrid, self.tableName, self.lccObj)
                

                tabTableName = os.path.basename(self.tabAreaTable._tableName)
                # AddMsg("tabTableName = "+tabTableName)
                AddMsg("%s Completed zonal tabulate area table. Intermediate: %s" % (self.timer.now(), tabTableName))

            
            def _calculateMetrics(self):
                AddMsg(self.timer.now() + " Processing the tabulate area table and computing metric values")
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
                                         self.timer)
            
                    
        # Create new instance of metricCalc class to contain parameters            
        flcvCalc = metricCalcFLCV(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                                  metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
        
        # Assign class attributes unique to this module.
        flcvCalc.inFacilityFeature = inFacilityFeature
        flcvCalc.viewRadius = viewRadius
        flcvCalc.viewThreshold = viewThreshold
        flcvCalc.metricsToRun = metricsToRun
        
        # Initiate our flexible cleanuplist
        flcvCalc.cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
        if flcvCalc.saveIntermediates:
            flcvCalc.cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            flcvCalc.cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))


        # Run Calculation
        flcvCalc.run()

    except Exception as e:
        errors.standardErrorHandling(e)
 
    finally:
        if not flcvCalc.cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in flcvCalc.cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
        setupAndRestore.standardRestore()
        
        
# def runNeighborhoodProportionsQA(inLandCoverGrid, _lccName, lccFilePath, metricsToRun, inNeighborhoodSize,
#                       burnIn, burnInValue="", minPatchSize="#", createZones="", zoneBin_str="", overWrite="",
#                       outWorkspace="#", optionalFieldGroups="#"):
#     """ Interface for script executing Generate Proximity Polygons utility """
#
#     from arcpy import env
#     from arcpy.sa import Con,Raster,Reclassify,RegionGroup,RemapValue,RemapRange
#
#     # process the inLandCoverGrid for the selected class
#     AddMsg("Processing neighborhood proportions grid...")
#
#     # get output grid name. Add it to the list of features to add to the Contents pane
#     namePrefix = "ProxGrid"
#     proximityGridName = files.getRasterName(namePrefix)
#
#
#     # generate a reclass list where each item in the list is a two item list: the original grid value, and the reclass value
#     reclassPairs = [[0, 0], [10, 0], [20, 0], [30, 0], [40, 1], [70, 1], [91, 1], [92, 1]]
#
#
#     AddMsg("Reclassifying selected land cover class to 1. All other values = 0...")
#     reclassGrid = arcpy.sa.Float(Reclassify(inLandCoverGrid,"VALUE", RemapValue(reclassPairs)))
#     namePrefix = "ClassGrid"
#     reclassScratchName = files.getRasterName(namePrefix)
#     reclassGrid.save(reclassScratchName)
#
#     AddMsg("Building raster attribute table...")
#     arcpy.management.BuildRasterAttributeTable(reclassGrid, "Overwrite")
#
#     desc = arcpy.Describe(reclassGrid)
#     AddMsg("baseNaem = "+desc.baseName)
#     AddMsg("catalogPath = "+desc.catalogPath)
#     AddMsg("file = "+desc.file)
#     AddMsg("name = "+desc.name)
#     AddMsg("path = "+desc.path)
#
#     env.snapRaster = reclassGrid
#     AddMsg("setting cellSize")
#     AddMsg("reclassScratchName = "+reclassScratchName)
#     env.cellSize = reclassScratchName
#     # arcpy.env.cellSizeProjectionMethod = "CONVERT_UNITS"
#     # arcpy.env.cellAlignment = "DEFAULT"
#
#     AddMsg("Performing focal SUM on reclassified raster using cell neighborhood...")
#     neighborhoodStr = "Rectangle 251 251 CELL"
#     AddMsg("neighborhoodStr = "+neighborhoodStr)
#
#     fullPath = 'r"'+reclassScratchName+'"'
#     AddMsg("reclassScratchName = "+fullPath)
#
#     nbrCntGrid = arcpy.sa.FocalStatistics(reclassGrid, neighborhoodStr, "SUM", "NODATA", 90)
#     namePrefix = "CountGrid"
#     nbrCntGridScratchName = files.getRasterName(namePrefix)  
#     nbrCntGrid.save(nbrCntGridScratchName)
#     AddMsg(" Save intermediate grid complete: "+os.path.basename(nbrCntGridScratchName))
#
#     AddMsg("Calculating the proportion of land cover class within cell neighborhood...")
#     proximityGrid = arcpy.sa.RasterCalculator([nbrCntGrid], ["x"], (' (x / 63001) * 100') )
#
#
#
#
#     proximityGrid.save(proximityGridName) 
#     AddMsg("Save proportions grid complete")
          


def runNeighborhoodProportions(inLandCoverGrid, _lccName, lccFilePath, metricsToRun, inNeighborhoodSize,
                      burnIn, burnInValue="", minPatchSize="#", createZones="", zoneBin_str="", overWrite="",
                      outWorkspace="#", optionalFieldGroups="#"):
    """ Interface for script executing Generate Proximity Polygons utility """
    
    from arcpy import env
    from arcpy.sa import Con,Raster,Reclassify,RegionGroup,RemapValue,RemapRange

    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.npConstants()
        
        ### Initialization
        # Start the timer
        timer = DateTimer()
        AddMsg(timer.start() + " Setting up environment variables")
        processingCellSize = Raster(inLandCoverGrid).meanCellWidth
        snapRaster = inLandCoverGrid
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster,processingCellSize,outWorkspace,
                                                                               [metricsToRun,optionalFieldGroups] )

        # Process the Land Cover Classification XML
        lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        lccClassesDict = lccObj.classes
        # Get the lccObj values dictionary. This contains all the properties of each value specified in the Land Cover Classification XML    
        lccValuesDict = lccObj.values
        # create a list of all the grid values in the selected land cover grid
        landCoverValues = raster.getRasterValues(inLandCoverGrid)
        # get the frozenset of excluded values (i.e., values marked as EXCLUDED in the Land Cover Classification XML)
        excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)
        
        # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
        settings.checkExcludedValuesInClass(metricsBaseNameList, lccObj, lccClassesDict)
        # alert user if the land cover grid has values undefined in the LCC XML file
        settings.checkGridValuesInLCC(inLandCoverGrid, lccObj)
        # alert user if the land cover grid cells are not square (default to size along x axis)
        settings.checkGridCellDimensions(inLandCoverGrid)
        
        # Determine if the user wants to save the intermediate products
        saveIntermediates = globalConstants.intermediateName in optionalGroupsList
        
        # determine the active map to add the output raster/features    
        currentProject = arcpy.mp.ArcGISProject("CURRENT")
        actvMap = currentProject.activeMap
        
        # Save the current environment settings, then set to desired condition  
        tempEnvironment0 = env.overwriteOutput
        if overWrite == "true":
            env.overwriteOutput = True
            arcpy.AddWarning("The 'Allow geoprocessing tools to overwrite existing datasets' option has been set to TRUE per your request. The option will be reset to FALSE upon completion of this tool.")
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
                arcpy.AddWarning("No excluded values in selected Land Cover Classification file. No BURN IN areas will be processed.")
                burnIn = "false"
            else:
                AddMsg("Processing BURN IN areas...")
                
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
            
                    AddMsg(("{0} Reclassing excluded values in land cover to 1. All other values = 0...").format(timer.now()))
                    excludedBinary = Reclassify(inLandCoverGrid,"VALUE", RemapValue(reclassPairs))

                    AddMsg(("{0} Calculating size of excluded area patches...").format(timer.now()))
                    regionGrid = RegionGroup(excludedBinary,"EIGHT","WITHIN","ADD_LINK")
                
                    #AddMsg(("{0} Assigning {1} to patches >= minimum size threshold...").format(timer.now(), burnInValue))
                    AddMsg(("{0} Assigning {1} to excluded area patches >= {2} cells in size...").format(timer.now(), burnInValue, minPatchSize))
                    delimitedCOUNT = arcpy.AddFieldDelimiters(regionGrid,"COUNT")
                    whereClause = delimitedCOUNT+" >= " + minPatchSize + " AND LINK = 1"
                    burnInGrid = Con(regionGrid, int(burnInValue), 0, whereClause)
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
            
                    AddMsg(("{0} Reclassing excluded values in land cover to {1}. All other values = 0...").format(timer.now(),burnInValue))
                    burnInGrid = Reclassify(inLandCoverGrid,"VALUE", RemapValue(reclassPairs))

                
                # save the intermediate raster if save intermediates option has been chosen
                if saveIntermediates: 
                    # namePrefix = metricConst.burnInGridName
                    namePrefix = ("{0}_{1}_{2}").format(metricConst.shortName,minPatchSize,metricConst.burnInGridName)
                    scratchName = files.getRasterName(namePrefix)
                    AddMsg(timer.now() + " Saving intermediate grid: "+os.path.basename(scratchName))
                    burnInGrid.save(scratchName)
                    AddMsg(timer.now() + " Save intermediate grid complete: "+os.path.basename(scratchName))

        # Run metric calculate for each metric in list
        for m in metricsBaseNameList:
            # get the grid codes for this specified metric
            classValuesList = lccClassesDict[m].uniqueValueIds.intersection(landCoverValues)
 
            # process the inLandCoverGrid for the selected class
            AddMsg(("Processing {0} neighborhood proportions grid...").format(m.upper()))

            # proximityGrid, nbrCntGrid = raster.getNbrPctWithBurnInGrid(inNeighborhoodSize, landCoverValues, classValuesList, 
            #                                                         excludedValuesList, inLandCoverGrid, burnIn, burnInGrid, timer)
            
            maxCellCount = pow(int(inNeighborhoodSize), 2)
                 
            # create class (value = 1) / other (value = 0) / excluded grid (value = 0) raster
            # define the reclass values
            classValue = 1
            excludedValue = 0
            otherValue = 0
            newValuesList = [classValue, excludedValue, otherValue]
            
            # generate a reclass list where each item in the list is a two item list: the original grid value, and the reclass value
            reclassPairs = raster.getInOutOtherReclassPairs(landCoverValues, classValuesList, excludedValuesList, newValuesList)
              
            AddMsg(("{0} Reclassifying selected land cover class to 1. All other values = 0...").format(timer.now()))
            reclassGrid = Reclassify(inLandCoverGrid,"VALUE", RemapValue(reclassPairs))
            
            AddMsg(("{0} Performing focal SUM on reclassified raster using {1} x {1} cell neighborhood...").format(timer.now(), inNeighborhoodSize))
            neighborhood = arcpy.sa.NbrRectangle(int(inNeighborhoodSize), int(inNeighborhoodSize), "CELL")
            nbrCntGrid = arcpy.sa.FocalStatistics(reclassGrid == classValue, neighborhood, "SUM", "NODATA")
                
            AddMsg(("{0} Calculating the proportion of land cover class within {1} x {1} cell neighborhood...").format(timer.now(), inNeighborhoodSize))
            proximityGrid = arcpy.sa.RasterCalculator([nbrCntGrid], ["x"], (' (x / '+str(maxCellCount)+') * 100') )
        
            if burnIn == "true":
                AddMsg(("{0} Burning excluded areas into proportions grid...").format(timer.now()))
                delimitedVALUE = arcpy.AddFieldDelimiters(burnInGrid,"VALUE")
                whereClause = delimitedVALUE+" = 0"
                proximityGrid = Con(burnInGrid, proximityGrid, burnInGrid, whereClause)
        
        
            
            # get output grid name. Add it to the list of features to add to the Contents pane
            namePrefix = ("{0}_{1}{2}").format(m.upper(),inNeighborhoodSize,metricConst.proxRasterOutName)
            proximityGridName = files.getRasterName(namePrefix)
            datasetList = arcpy.ListDatasets()
            if proximityGridName in datasetList:
                arcpy.Delete_management(proximityGridName)
            AddMsg(timer.now() + " Saving proportions grid: "+os.path.basename(proximityGridName))
            try:
                proximityGrid.save(proximityGridName)
            except:
                raise errors.attilaException(errorConstants.rasterOutputFormatError) 
            AddMsg(timer.now() + " Save proportions grid complete: "+os.path.basename(proximityGridName))
            addToActiveMap.append(proximityGridName)
                  
            # save the intermediate raster if save intermediates option has been chosen 
            if saveIntermediates:
                namePrefix = ("{0}_{1}{2}").format(m.upper(),inNeighborhoodSize,metricConst.proxFocalSumOutName)
                scratchName = files.getRasterName(namePrefix)  
                datasetList = arcpy.ListDatasets()
                if scratchName in datasetList:
                    arcpy.Delete_management(scratchName)
                AddMsg(timer.now() + " Saving intermediate grid: "+os.path.basename(scratchName))
                try:
                    nbrCntGrid.save(scratchName)
                except:
                    raise errors.attilaException(errorConstants.rasterOutputFormatError)
                AddMsg(timer.now() + " Save intermediate grid complete: "+os.path.basename(scratchName))
  
            # convert neighborhood proportions raster to zones if createZones is selected
            if createZones == "true":
                # To reclass the proportions grid, the max grid value is 100
                maxGridValue = 100
        
                # Set up break points to reclass proximity grid into % classes
                reclassBins = raster.getRemapBinsByPercentStep(maxGridValue, int(zoneBin_str))
                rngRemap = RemapRange(reclassBins)
                
                time.sleep(1) # A small pause is needed here between quick successive timer calls
                AddMsg(("{0} Reclassifying proportions grid into {1}% breaks...").format(timer.now(), zoneBin_str))
                # nbrZoneGrid = Reclassify(proximityGrid, "VALUE", rngRemap)
                # The simple reclassify operation above, often leaves the ESRI default layer name in the saved 
                # nbrZoneGrid when the land cover raster is relatively small. Although the nbrZoneGrid appears to have the
                # correct name in the catalog, when the raster is added to a map, the layer name is displayed in the TOC
                # instead of the saved raster name (e.g., Reclass_NI_91 instead of NI_9_Zone0). The technique below appears
                # to alleviate that problem without adding substantial time to the reclassification operation.
                nbrZoneGrid = (Reclassify(proximityGrid, "VALUE", rngRemap) * 1)
                namePrefix = ("{0}_{1}{2}").format(m.upper(),inNeighborhoodSize,metricConst.proxZoneRaserOutName)
                scratchName = files.getRasterName(namePrefix)
                datasetList = arcpy.ListDatasets()
                if scratchName in datasetList:
                    arcpy.Delete_management(scratchName)
                try:
                    nbrZoneGrid.save(scratchName)
                except:
                    raise errors.attilaException(errorConstants.rasterOutputFormatError)
                addToActiveMap.append(scratchName)
 
     
        # add outputs to the active map
        if actvMap != None:
            for aFeature in addToActiveMap:
                actvMap.addDataFromPath(aFeature)
                AddMsg(("Adding {0} to {1} view").format(os.path.basename(aFeature), actvMap.name))

    except Exception as e:
        errors.standardErrorHandling(e)

    finally:
        setupAndRestore.standardRestore()
        env.overwriteOutput = tempEnvironment0


def runIntersectionDensity(inLineFeature, mergeLines, mergeField="#", mergeDistance='#', outputCS="#", cellSize="#", 
                           searchRadius="#", areaUnits="#", outRaster="#", optionalFieldGroups="#"):
    """ Interface for script executing Intersection Density utility """
    from arcpy import env
    
    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.idConstants()
        
        ### Initialization
        # Start the timer
        timer = DateTimer()
        AddMsg(timer.start() + " Setting up environment variables")
        
        # set up dummy variables to pass to standardSetup in setupAndRestore. SetupAndRestore will set the environmental
        # variables as desired and pass back the optionalGroupsList to use for intermediate products retention.
        # metricsBaseNameList is not used for this tool.
        metricsToRun = 'item1  -  description1;item2  -  description2'
        snapRaster = False

        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster,cellSize,os.path.dirname(outRaster),
                                                                              [metricsToRun,optionalFieldGroups] )  

        if globalConstants.intermediateName in optionalGroupsList:
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
        
        # determine the active map to add the output raster/features    
        currentProject = arcpy.mp.ArcGISProject("CURRENT")
        actvMap = currentProject.activeMap    
        
        # create list of layers to add to the active Map
        addToActiveMap = []
        
        # Do a Describe on the Road feature input and get the file's basename.
        descInLines = arcpy.Describe(inLineFeature)
        inBaseName = descInLines.baseName
        
        # if no specific geoprocessing environment extent is set, temporarily set it to match the inLineFeature. It will be reset during the standardRestore
        nonSpecificExtents = ["NONE", "MAXOF", "MINOF"]
        envExtent = str(env.extent).upper()
        if envExtent in nonSpecificExtents:
            AddMsg(("Using {0}'s extent for geoprocessing steps.").format(inBaseName))
            env.extent = descInLines.extent
        else:
            AddMsg("Extent set in Geoprocessing environment used for processing.")
            
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
            prjPrefix = "%s_%s_%s_" % (metricConst.shortName, inBaseName, metricConst.prjRoadName)       
            prjFeatureName = files.nameIntermediateFile([prjPrefix, "FeatureClass"], cleanupList)
            outCS = arcpy.SpatialReference(text=outputCS)
            AddMsg(("{0} Projecting {1} to {2}. Intermediate: {3}").format(timer.now(), inBaseName, outCS.name, os.path.basename(prjFeatureName)))
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
                    namePrefix = "%s_%s_" % (metricConst.shortName, inBaseName)
                    copyFeatureName = files.nameIntermediateFile([namePrefix,"FeatureClass"],cleanupList)
                    AddMsg(("{0} Copying {1} to {2}...").format(timer.now(), inBaseName, os.path.basename(copyFeatureName)))
                    inRoadFeature = arcpy.FeatureClassToFeatureClass_conversion(inLineFeature,env.workspace,
                                                                                 os.path.basename(copyFeatureName))

                # No merge field was supplied. Add a field to the copied inRoadFeature and populate it with a constant value
                AddMsg(("{0} Adding a dummy field to {1} and assigning value 1 to all records...").format(timer.now(), arcpy.Describe(inRoadFeature).baseName))
                mergeField = metricConst.dummyFieldName
                arcpy.AddField_management(inRoadFeature,mergeField,"SHORT")
                arcpy.CalculateField_management(inRoadFeature,mergeField,1)
            
            # Ensure the road feature class is comprised of singleparts. Multipart features will cause MergeDividedRoads to fail.
            namePrefix = "%s_%s_%s_" % (metricConst.shortName, inBaseName, metricConst.singlepartRoadName)
            singlepartFeatureName = files.nameIntermediateFile([namePrefix,"FeatureClass"],cleanupList)
            AddMsg(("{0} Converting Multipart features to Singlepart. Intermediary output: {1}").format(timer.now(), os.path.basename(singlepartFeatureName)))
            arcpy.MultipartToSinglepart_management(inRoadFeature, singlepartFeatureName)

            # Generate single-line road features in place of matched pairs of divided road lanes.
            # Only roads with the same value in the mergeField and within the mergeDistance will be merged. All non-merged roads are retained.
            # Input features with the Merge Field parameter value equal to zero are locked and will not be merged, even if adjacent features are not locked
            namePrefix = "%s_%s_%s_" % (metricConst.shortName, inBaseName, metricConst.mergedRoadName)
            mergedFeatureName = files.nameIntermediateFile([namePrefix,"FeatureClass"],cleanupList)
            AddMsg(("{0} Merging divided road features. Intermediary output: {1}").format(timer.now(), os.path.basename(mergedFeatureName)))
            
            # This is also the final reassignment of the inRoadFeature variable
            inRoadFeature = arcpy.MergeDividedRoads_cartography(singlepartFeatureName, mergeField, mergeDistance, mergedFeatureName)

        # UNSPLIT LINES
        # We're only going to use two parameters for the arcpy.UnsplitLine_management tool. 
        # The original code used a third parameter to focus the unsplit operation on the  "ST_NAME" field. 
        # However, this will cause an intersection wherever a street name changes regardless if it's an actual intersection. 
        # Less importantly, it would require the user to identify which field in the "roads" layer is the street name field 
        # adding more clutter to the tool interface.
        unsplitPrefix = "%s_%s_%s_" % (metricConst.shortName, inBaseName, metricConst.unsplitRoadName) 
        unsplitFeatureName = files.nameIntermediateFile([unsplitPrefix, "FeatureClass"], cleanupList)
        AddMsg(("{0} Unsplitting {1}. Intermediate: {2}").format(timer.now(), arcpy.Describe(inRoadFeature).baseName, os.path.basename(unsplitFeatureName)))
        arcpy.UnsplitLine_management(inRoadFeature, unsplitFeatureName)
        
        # INTERSECT LINES WITH THEMSELVES
        intersectPrefix = "%s_%s_%s_" % (metricConst.shortName, inBaseName, metricConst.roadIntersectName) 
        intersectFeatureName = files.nameIntermediateFile([intersectPrefix, "FeatureClass"], cleanupList) 
        AddMsg(("{0} Finding intersections. Intermediate: {1}.").format(timer.now(), os.path.basename(intersectFeatureName)))
        arcpy.Intersect_analysis([unsplitFeatureName, unsplitFeatureName], intersectFeatureName, "ONLY_FID",'',"POINT")

        # DELETE REDUNDANT INTERSECTION POINTS THAT OCCUR AT THE SAME LOCATION
        AddMsg(("{0} Deleting identical intersections...").format(timer.now()))
        arcpy.DeleteIdentical_management(intersectFeatureName, "Shape")

        # Calculate a magnitude-per-unit area from the intersection features using a kernel function to fit a smoothly tapered surface to each point. 
        # The output cell size, search radius, and area units can be altered by the user
        AddMsg(("{0} Performing kernel density: Result saved as {1}.").format(timer.now(), os.path.basename(outRaster)))
        # Sometimes, often when the extent of an area is small, the ESRI default layer name is retained in the
        # saved output raster. Although the output raster appears to have the correct name in the catalog, when the 
        # raster is added to a map, the layer name is displayed in the TOC instead. Multiplying the result by 1  
        # appears to alleviate that problem without adding substantial time to the overall operation.
        den = (arcpy.sa.KernelDensity(intersectFeatureName, "NONE", int(cellSize), int(searchRadius), areaUnits) * 1)

        # Save the kernel density raster
        den.save(outRaster)
        
        # Add it to the list of features to add to the Contents pane
        addToActiveMap.append(outRaster)
        
        # add outputs to the active map
        if actvMap != None:
            for aFeature in addToActiveMap:
                actvMap.addDataFromPath(aFeature)
                AddMsg(("Adding {0} to {1} view").format(os.path.basename(aFeature), actvMap.name))

    except Exception as e:
        errors.standardErrorHandling(e)
 
    finally:
        setupAndRestore.standardRestore()
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
                
                
def runNearRoadLandCoverProportions(inRoadFeature, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, inRoadWidthOption,
                      widthLinearUnit="", laneCntFld="#", laneWidth="#", laneDistFld="#", bufferDist="#", removeLinesYN="",
                      cutoffLength="#", overWrite="", outWorkspace='#',  processingCellSize="#", snapRaster="#", optionalFieldGroups="#"):
    """ Interface for script executing Near Road Land Cover Proportions tool """
    
    from arcpy import env
#    from arcpy.sa import Con,Raster,Reclassify,RegionGroup,RemapValue,RemapRange

    cleanupList = [] # This is an empty list object that will contain tuples of the form (function, arguments) as needed for cleanup
    try:
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.nrlcpConstants()
        
        ### Initialization
        # Start the timer
        timer = DateTimer()
        AddMsg(timer.start() + " Setting up environment variables")
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster,processingCellSize,outWorkspace,
                                                                               [metricsToRun,optionalFieldGroups] )

        # Process the Land Cover Classification XML
        lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        lccClassesDict = lccObj.classes
        # Get the lccObj values dictionary. This contains all the properties of each value specified in the Land Cover Classification XML    
#        lccValuesDict = lccObj.values
        # create a list of all the grid values in the selected land cover grid
#        landCoverValues = raster.getRasterValues(inLandCoverGrid)
        # get the frozenset of excluded values (i.e., values marked as EXCLUDED in the Land Cover Classification XML)
#        excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)
        
        # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
        settings.checkExcludedValuesInClass(metricsBaseNameList, lccObj, lccClassesDict)
        # alert user if the land cover grid has values undefined in the LCC XML file
        settings.checkGridValuesInLCC(inLandCoverGrid, lccObj)
        # alert user if the land cover grid cells are not square (default to size along x axis)
        settings.checkGridCellDimensions(inLandCoverGrid)
        
        # Determine if the user wants to save the intermediate products       
        if globalConstants.intermediateName in optionalGroupsList:
#            saveIntermediates = True
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
#            saveIntermediates = False
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
        
        # determine the active map to add the output raster/features    
#        currentProject = arcpy.mp.ArcGISProject("CURRENT")
#        actvMap = currentProject.activeMap
        
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
        arcpy.Dissolve_management(mergeBuffFeature, finalBuffFeature)        
        
        

    except Exception as e:
        errors.standardErrorHandling(e)
 
    finally:
        setupAndRestore.standardRestore()
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
                
                
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
#         AddMsg(timer.start() + " Setting up environment variables")
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
# #        landCoverValues = raster.getRasterValues(inLandCoverGrid)
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
#         errors.standardErrorHandling(e)
#
#     finally:
#         setupAndRestore.standardRestore()
#         if not cleanupList[0] == "KeepIntermediates":
#             for (function,arguments) in cleanupList:
#                 # Flexibly executes any functions added to cleanup array.
#                 function(*arguments)