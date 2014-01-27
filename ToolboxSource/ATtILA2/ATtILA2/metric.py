''' Interface for running specific metrics

'''
import os
import arcpy
import errors
import setupAndRestore
import string
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

        # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
        utils.settings.checkExcludedValuesInClass(self.metricsBaseNameList, self.lccObj, self.lccClassesDict)
        # alert user if the land cover grid has values undefined in the LCC XML file
        utils.settings.checkGridValuesInLCC(self.inLandCoverGrid, self.lccObj)
        # alert user if the land cover grid cells are not square (default to size along x axis)
        utils.settings.checkGridCellDimensions(self.inLandCoverGrid)
        # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
        self.outIdField = utils.settings.getIdOutField(self.inReportingUnitFeature, self.reportingUnitIdField)

        # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
        self.zoneAreaDict = None
        if globalConstants.qaCheckName in self.optionalGroupsList:
            # Check to see if an outputGeorgraphicCoordinate system is set in the environments. If one is not specified
            # return the spatial reference for the land cover grid. Use the returned spatial reference to calculate the
            # area of the reporting unit's polygon features to store in the zoneAreaDict
            self.outputSpatialRef = utils.settings.getOutputSpatialReference(self.inLandCoverGrid)
            self.zoneAreaDict = polygons.getIdAreaDict(self.inReportingUnitFeature, self.reportingUnitIdField, self.outputSpatialRef)


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
        AddMsg(self.timer.split() + " Processing the tabulate area table and computing metric values")
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
        from pylet import arcpyutil
        from arcpy import env
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.lcospConstants()
        # append the slope threshold value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inSlopeThresholdValue
        
        # set the environmental extent to the intersection of the reporting unit theme, the land cover grid, and the
        # slope grid. The extent will be aligned to the cell boundaries of the land cover grid
        env.extent = arcpyutil.environment.getAlignedExtent(inLandCoverGrid, processingCellSize, [inReportingUnitFeature, inSlopeGrid])


        # Create new subclass of metric calculation
        class metricCalcLCOSP(metricCalc):
            # Subclass that overrides specific functions for the LandCoverOnSlopeProportions calculation
            def _replaceLCGrid(self):
                # replace the inLandCoverGrid
                self.inLandCoverGrid = utils.raster.getIntersectOfGrids(self.lccObj, self.inLandCoverGrid, self.inSlopeGrid,
                                                                   self.inSlopeThresholdValue)

                if self.saveIntermediates:
                    self.scratchName = arcpy.CreateScratchName(self.metricConst.shortName+"Raster", metricConst.fieldParameters[1], 
                                                               "RasterDataset")
                    self.inLandCoverGrid.save(self.scratchName)
                    #arcpy.CopyRaster_management(self.inLandCoverGrid, self.scratchName)
                    AddMsg(self.timer.split() + " Save intermediate grid complete: "+os.path.basename(self.scratchName))
                    
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


def runCoreAndEdgeAreaMetrics(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                            metricsToRun, inEdgeWidth, outTable, processingCellSize, snapRaster, optionalFieldGroups):
    """ Interface for script executing Core/Edge Metrics """

    try:
        from pylet import arcpyutil
        from arcpy import env
        
        # retrieve the attribute constants associated with this metric
        metricConst = metricConstants.caeamConstants()
        # append the edge width distance value to the field suffix
        metricConst.fieldParameters[1] = metricConst.fieldSuffix + inEdgeWidth
        # for the core and edge fields, add the edge width to the  field suffix
        for i, aFldParams in enumerate(metricConst.additionalFields):
            aFldParams[1] = aFldParams[1] + inEdgeWidth
            metricConst.additionalFields[i] = aFldParams
        
        metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize,
                                                                                 os.path.dirname(outTable),
                                                                                 [metricsToRun,optionalFieldGroups] )
        
        # set the environmental extent to that of the reporting unit theme, aligned to the land cover grid, and buffered with the edge width
        env.extent = arcpyutil.environment.getBufferedExtent(inReportingUnitFeature, inLandCoverGrid, processingCellSize, inEdgeWidth)
        
        lccObj = lcc.LandCoverClassification(lccFilePath)
        # get the dictionary with the LCC CLASSES attributes
        lccClassesDict = lccObj.classes
        
        outIdField = utils.settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
        
        # alert user if the LCC XML document has any values within a class definition that are also tagged as 'excluded' in the values node.
        utils.settings.checkExcludedValuesInClass(metricsBaseNameList, lccObj, lccClassesDict)
        # alert user if the land cover grid has values undefined in the LCC XML file
        utils.settings.checkGridValuesInLCC(inLandCoverGrid, lccObj)
     
        #Create the output table outside of metricCalc so that result can be added for multiple metrics
        newtable, metricsFieldnameDict = utils.table.tableWriterByClass(outTable, metricsBaseNameList,optionalGroupsList, 
                                                                                  metricConst, lccObj, outIdField, 
                                                                                  metricConst.additionalFields)
        # Run metric calculate for each metric in list
        for m in metricsBaseNameList:
        
            class metricCalcCAEAM(metricCalc):
                # Subclass that overrides specific functions for the CoreAndEdgeAreaMetric calculation
                def _replaceLCGrid(self):
                    # replace the inLandCoverGrid
                    AddMsg(self.timer.split() + " Generating core and edge grid for class: " + m)
                    self.inLandCoverGrid = utils.raster.getEdgeCoreGrid(m, self.lccObj, self.lccClassesDict, self.inLandCoverGrid, 
                                                                        self.inEdgeWidth, os.path.dirname(outTable), 
                                                                        globalConstants.scratchGDBFilename, processingCellSize)
                    AddMsg(self.timer.split() + " Core and edge grid complete")
                    
                    if self.saveIntermediates:
                        self.scratchName = arcpy.CreateScratchName(self.metricConst.shortName+"Raster", m+inEdgeWidth, "RasterDataset")
                        self.inLandCoverGrid.save(self.scratchName)
                        #arcpy.CopyRaster_management(self.inLandCoverGrid, self.scratchName)
                        AddMsg(self.timer.split() + " Save intermediate grid complete: "+os.path.basename(self.scratchName))


                #skip over make out table since it has already been made
                def _makeAttilaOutTable(self):
                    pass  
                
                def _makeTabAreaTable(self):
                    AddMsg(self.timer.split() + " Generating a zonal tabulate area table")
                    # Internal function to generate a zonal tabulate area table
                    class categoryTabAreaTable(TabulateAreaTable):
                        #Update definition so Tabulate Table is run on the POS field.
                        def _createNewTable(self):
                            self._value = "CATEGORY"
                            if self._tableName:
                                self._destroyTable = False
                                self._tableName = arcpy.CreateScratchName(self._tableName, m+inEdgeWidth, self._datasetType)
                            else:
                                self._tableName = arcpy.CreateScratchName(self._tempTableName, m+inEdgeWidth, self._datasetType)
            
        
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
                    utils.settings.checkGridCellDimensions(self.inLandCoverGrid)
                    # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
                    self.outIdField = utils.settings.getIdOutField(self.inReportingUnitFeature, self.reportingUnitIdField)
                
                    # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
                    self.zoneAreaDict = None
                    if globalConstants.qaCheckName in self.optionalGroupsList:
                        # Check to see if an outputGeorgraphicCoordinate system is set in the environments. If one is not specified
                        # return the spatial reference for the land cover grid. Use the returned spatial reference to calculate the
                        # area of the reporting unit's polygon features to store in the zoneAreaDict
                        self.outputSpatialRef = utils.settings.getOutputSpatialReference(self.inLandCoverGrid)
                        self.zoneAreaDict = polygons.getIdAreaDict(self.inReportingUnitFeature, self.reportingUnitIdField, self.outputSpatialRef)

                # Update calculateMetrics to calculate Core to Edge Ratio
                def _calculateMetrics(self):
                    self.newTable = newtable
                    self.metricsFieldnameDict = metricsFieldnameDict

                    # calculate Core to Edge ratio
                    utils.calculate.getCoreEdgeRatio(self.outIdField, self.newTable, self.tabAreaTable, self.metricsFieldnameDict,
                                                      self.zoneAreaDict, self.metricConst, m)

            # Create new instance of metricCalc class to contain parameters
            caeamCalc = metricCalcCAEAM(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                          m, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
    
            caeamCalc.inEdgeWidth = inEdgeWidth
    
            # Run Calculation
            caeamCalc.run()
            
            caeamCalc.metricsBaseNameList = metricsBaseNameList

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
        
        # Create new instance of metricCalc class to contain parameters
        rlcpCalc = metricCalcRLCP(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                       metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)

        # Assign class attributes unique to this module.
        rlcpCalc.inStreamFeatures = inStreamFeatures
        rlcpCalc.inBufferDistance = inBufferDistance

        # Run Calculation
        rlcpCalc.run()      

        # Clean up intermediates
        if not rlcpCalc.saveIntermediates:
            # note, this is actually deleting the buffers, not the source reporting units.
            arcpy.Delete_management(rlcpCalc.inReportingUnitFeature)
        
    except Exception, e:
        errors.standardErrorHandling(e)

    finally:
        setupAndRestore.standardRestore()

def runSamplePointLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                            metricsToRun, inPointFeatures, ruLinkField, inBufferDistance, outTable, processingCellSize, 
                            snapRaster, optionalFieldGroups):
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

        # Create new instance of metricCalc class to contain parameters
        splcpCalc = metricCalcSPLCP(inReportingUnitFeature, ruLinkField, inLandCoverGrid, lccFilePath,
                       metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)

        # Assign class attributes unique to this module.
        splcpCalc.inPointFeatures = inPointFeatures
        splcpCalc.inBufferDistance =  inBufferDistance
        splcpCalc.ruLinkField = ruLinkField

        # Run Calculation
        splcpCalc.run()

        # Clean up intermediates.  
        if not splcpCalc.saveIntermediates:
            # note, this is actually deleting the buffers, not the source reporting units.
            arcpy.Delete_management(splcpCalc.bufferName)            

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

    except Exception, e:
        errors.standardErrorHandling(e)

    finally:
        setupAndRestore.standardRestore()



def runRoadDensityCalculator(inReportingUnitFeature, reportingUnitIdField, inRoadFeature, outTable, roadClassField="",
                             streamRoadCrossings="#", roadsNearStreams="#", inStreamFeature="#", bufferDistance="#",
                             optionalFieldGroups="#"):
    """Interface for script executing Road Density Calculator"""
    from arcpy import env
    from pylet import arcpyutil
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
        env.workspace = arcpyutil.environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))
        # Strip the description from the "additional option" and determine whether intermediates are stored.
        processed = arcpyutil.parameters.splitItemsAndStripDescriptions(optionalFieldGroups, globalConstants.descriptionDelim)
        if globalConstants.intermediateName in processed:
            msg = "\nIntermediates are stored in this directory: {0}\n"
            AddMsg(msg.format(env.workspace))
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
        
        # Create a copy of the reporting unit feature class that we can add new fields to for calculations.  This 
        # is more appropriate than altering the user's input data. Keep only the OID, shape, and reportingUnitIdField fields
        fieldMappings = arcpy.FieldMappings()
        fieldMappings.addTable(inReportingUnitFeature)
        [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name <> reportingUnitIdField]

        AddMsg(timer.split() + " Creating temporary copy of reporting unit layer")
        tempReportingUnitFeature = utils.files.nameIntermediateFile(["tempReportingUnitFeature","FeatureClass"],cleanupList)
        inReportingUnitFeature = arcpy.FeatureClassToFeatureClass_conversion(inReportingUnitFeature,env.workspace,
                                                                             os.path.basename(tempReportingUnitFeature),"",
                                                                             fieldMappings)

        # Get the field properties for the unitID, this will be frequently used
        # If the field is numeric, it creates a text version of the field.
        uIDField = utils.settings.processUIDField(inReportingUnitFeature,reportingUnitIdField)

        AddMsg(timer.split() + " Calculating reporting unit area")
        # Add a field to the reporting units to hold the area value in square kilometers
        # Check for existence of field.
        fieldList = arcpy.ListFields(inReportingUnitFeature,metricConst.areaFieldname)
        # Add and populate the area field (or just recalculate if it already exists
        unitArea = utils.vector.addAreaField(inReportingUnitFeature,metricConst.areaFieldname)
        if not fieldList: # if the list of fields that exactly match the validated fieldname is empty...
            if not cleanupList[0] == "KeepIntermediates":
                # ...add this to the list of items to clean up at the end.
                pass
                # *** this was previously necessary when the field was added to the input - now that a copy of the input
                #     is used instead, this is not necessary.
                #cleanupList.append((arcpy.DeleteField_management,(inReportingUnitFeature,unitArea)))


        AddMsg(timer.split() + " Calculating road density")
        # Get a unique name for the merged roads and prep for cleanup
        mergedRoads = utils.files.nameIntermediateFile(metricConst.roadsByReportingUnitName,cleanupList)

        # Calculate the density of the roads by reporting unit.
        mergedRoads, roadLengthFieldName = utils.calculate.lineDensityCalculator(inRoadFeature,inReportingUnitFeature,
                                                                                 uIDField,unitArea,mergedRoads,
                                                                                 metricConst.roadDensityFieldName,
                                                                                 roadClassField,
                                                                                 metricConst.totalImperviousAreaFieldName)

        # Build and populate final output table.
        AddMsg(timer.split() + " Compiling calculated values into output table")
        arcpy.TableToTable_conversion(inReportingUnitFeature,os.path.dirname(outTable),os.path.basename(outTable))
        # Get a list of unique road class values
        if roadClassField:
            classValues = arcpyutil.fields.getUniqueValues(mergedRoads,roadClassField)
        else:
            classValues = []
        # Compile a list of fields that will be transferred from the merged roads feature class into the output table
        fromFields = [roadLengthFieldName, metricConst.roadDensityFieldName,metricConst.totalImperviousAreaFieldName]
        # Transfer the values to the output table, pivoting the class values into new fields if necessary.
        utils.table.transferField(mergedRoads,outTable,fromFields,fromFields,uIDField.name,roadClassField,classValues)
        
        # If the Streams By Roads (STXRD) box is checked...
        if streamRoadCrossings and streamRoadCrossings <> "false":
            AddMsg(timer.split() + " Calculating Stream and Road Crossings (STXRD)")
            # Get a unique name for the merged streams:
            mergedStreams = utils.files.nameIntermediateFile(metricConst.streamsByReportingUnitName,cleanupList)

            # Calculate the density of the streams by reporting unit.
            mergedStreams, streamLengthFieldName = utils.calculate.lineDensityCalculator(inStreamFeature,
                                                                                         inReportingUnitFeature,
                                                                                         uIDField,
                                                                                         unitArea,mergedStreams,
                                                                                         metricConst.streamDensityFieldName)

            # Get a unique name for the road/stream intersections:
            roadStreamMultiPoints = utils.files.nameIntermediateFile(metricConst.roadStreamMultiPoints,cleanupList)
            # Get a unique name for the points of crossing:
            roadStreamIntersects = utils.files.nameIntermediateFile(metricConst.roadStreamIntersects,cleanupList)
            # Get a unique name for the roads by streams summary table:
            roadStreamSummary = utils.files.nameIntermediateFile(metricConst.roadStreamSummary,cleanupList)
            
            # Perform the roads/streams intersection and calculate the number of crossings and crossings per km
            utils.vector.findIntersections(mergedRoads,mergedStreams,uIDField,roadStreamMultiPoints,
                                           roadStreamIntersects,roadStreamSummary,streamLengthFieldName,
                                           metricConst.xingsPerKMFieldName,roadClassField)
            
            # Transfer values to final output table.
            AddMsg(timer.split() + " Compiling calculated values into output table")
            # Compile a list of fields that will be transferred from the merged roads feature class into the output table
            fromFields = [streamLengthFieldName, metricConst.streamDensityFieldName]
            # Transfer the values to the output table, pivoting the class values into new fields if necessary.
            # Possible to add stream class values here if desired.
            utils.table.transferField(mergedStreams,outTable,fromFields,fromFields,uIDField.name,None)
            # Transfer crossings fields - note the renaming of the count field.
            fromFields = ["FREQUENCY", metricConst.xingsPerKMFieldName]
            toFields = [metricConst.streamRoadXingsCountFieldname,metricConst.xingsPerKMFieldName]
            # Transfer the values to the output table, pivoting the class values into new fields if necessary.
            utils.table.transferField(roadStreamSummary,outTable,fromFields,toFields,uIDField.name,roadClassField,classValues)
            

        if roadsNearStreams and roadsNearStreams <> "false":
            AddMsg(timer.split() + " Calculating Roads Near Streams (RNS)")
            if not streamRoadCrossings or streamRoadCrossings == "false":  # In case merged streams haven't already been calculated:
                # Get a unique name for the merged streams:
                mergedStreams = utils.files.nameIntermediateFile(metricConst.streamsByReportingUnitName,cleanupList)
                # Calculate the density of the streams by reporting unit.
                mergedStreams, streamLengthFieldName = utils.calculate.lineDensityCalculator(inStreamFeature,
                                                                                             inReportingUnitFeature,
                                                                                             uIDField,unitArea,mergedStreams,
                                                                                             metricConst.streamDensityFieldName)
            # Get a unique name for the buffered streams:
            streamBuffer = utils.files.nameIntermediateFile(metricConst.streamBuffers,cleanupList)
            # Get a unique name for the road/stream intersections:
            roadsNearStreams = utils.files.nameIntermediateFile(metricConst.roadsNearStreams,cleanupList)

            utils.vector.roadsNearStreams(mergedStreams, bufferDistance, mergedRoads, streamLengthFieldName,
                                          uIDField, streamBuffer, roadsNearStreams, metricConst.rnsFieldName)
            # Transfer values to final output table.
            AddMsg(timer.split() + " Compiling calculated values into output table")
            fromFields = [metricConst.rnsFieldName]
            # Transfer the values to the output table, pivoting the class values into new fields if necessary.
            utils.table.transferField(roadsNearStreams,outTable,fromFields,fromFields,uIDField.name,roadClassField,classValues)
    
    except Exception, e:
        errors.standardErrorHandling(e)

    finally:
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
        env.workspace = _tempEnvironment1


def runStreamDensityCalculator(inReportingUnitFeature, reportingUnitIdField, inLineFeature, outTable, lineCategoryField="", 
                               optionalFieldGroups="#"):
    """Interface for script executing Road Density Calculator"""
    from arcpy import env
    from pylet import arcpyutil
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
        env.workspace = arcpyutil.environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))
        # Strip the description from the "additional option" and determine whether intermediates are stored.
        processed = arcpyutil.parameters.splitItemsAndStripDescriptions(optionalFieldGroups, globalConstants.descriptionDelim)
        if globalConstants.intermediateName in processed:
            msg = "\nIntermediates are stored in this directory: {0}\n"
            AddMsg(msg.format(env.workspace))
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
        
        # Create a copy of the reporting unit feature class that we can add new fields to for calculations.  This 
        # is more appropriate than altering the user's input data. Keep only the OID, shape, and reportingUnitIdField fields
        fieldMappings = arcpy.FieldMappings()
        fieldMappings.addTable(inReportingUnitFeature)
        [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name <> reportingUnitIdField]

        AddMsg(timer.split() + " Creating temporary copy of reporting unit layer")
        tempReportingUnitFeature = utils.files.nameIntermediateFile(["tempReportingUnitFeature","FeatureClass"],cleanupList)
        inReportingUnitFeature = arcpy.FeatureClassToFeatureClass_conversion(inReportingUnitFeature,env.workspace,
                                                                             os.path.basename(tempReportingUnitFeature),"",
                                                                             fieldMappings)

        # Get the field properties for the unitID, this will be frequently used
        uIDField = utils.settings.processUIDField(inReportingUnitFeature,reportingUnitIdField)

        AddMsg(timer.split() + " Calculating reporting unit area")
        # Add a field to the reporting units to hold the area value in square kilometers
        # Check for existence of field.
        fieldList = arcpy.ListFields(inReportingUnitFeature,metricConst.areaFieldname)
        # Add and populate the area field (or just recalculate if it already exists
        unitArea = utils.vector.addAreaField(inReportingUnitFeature,metricConst.areaFieldname)
        if not fieldList: # if the list of fields that exactly match the validated fieldname is empty...
            if not cleanupList[0] == "KeepIntermediates":
                # ...add this to the list of items to clean up at the end.
                pass
                # *** this was previously necessary when the field was added to the input - now that a copy of the input
                #     is used instead, this is not necessary.
                #cleanupList.append((arcpy.DeleteField_management,(inReportingUnitFeature,unitArea)))


        AddMsg(timer.split() + " Calculating feature density")
        # Get a unique name for the merged roads and prep for cleanup
        mergedInLines = utils.files.nameIntermediateFile(metricConst.linesByReportingUnitName,cleanupList)

        # Calculate the density of the roads by reporting unit.
        mergedInLines, lineLengthFieldName = utils.calculate.lineDensityCalculator(inLineFeature,inReportingUnitFeature,
                                                                                 uIDField,unitArea,mergedInLines,
                                                                                 metricConst.lineDensityFieldName,
                                                                                 lineCategoryField)

        # Build and populate final output table.
        AddMsg(timer.split() + " Compiling calculated values into output table")
        arcpy.TableToTable_conversion(inReportingUnitFeature,os.path.dirname(outTable),os.path.basename(outTable))
        # Get a list of unique road class values
        if lineCategoryField:
            categoryValues = arcpyutil.fields.getUniqueValues(mergedInLines,lineCategoryField)
        else:
            categoryValues = []
        # Compile a list of fields that will be transferred from the merged roads feature class into the output table
        fromFields = [lineLengthFieldName, metricConst.lineDensityFieldName]
        # Transfer the values to the output table, pivoting the class values into new fields if necessary.
        utils.table.transferField(mergedInLines,outTable,fromFields,fromFields,uIDField.name,lineCategoryField,categoryValues)
        
    except Exception, e:
        errors.standardErrorHandling(e)

    finally:
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
        env.workspace = _tempEnvironment1
        

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
                utils.settings.checkGridCellDimensions(self.inLandCoverGrid)
                # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
                self.outIdField = utils.settings.getIdOutField(self.inReportingUnitFeature, self.reportingUnitIdField)
                # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
                self.zoneAreaDict = None
                if globalConstants.qaCheckName in self.optionalGroupsList:
                    # Check to see if an outputGeorgraphicCoordinate system is set in the environments. If one is not specified
                    # return the spatial reference for the land cover grid. Use the returned spatial reference to calculate the
                    # area of the reporting unit's polygon features to store in the zoneAreaDict
                    self.outputSpatialRef = utils.settings.getOutputSpatialReference(self.inLandCoverGrid)
                    self.zoneAreaDict = polygons.getIdAreaDict(self.inReportingUnitFeature, self.reportingUnitIdField, self.outputSpatialRef)
                    
            def _makeAttilaOutTable(self):
                AddMsg(self.timer.split() + " Constructing the ATtILA metric output table")
                # Internal function to construct the ATtILA metric output table
                self.newTable, self.metricsFieldnameDict = utils.table.tableWriterNoLcc(self.outTable,
                                                                                        self.metricsBaseNameList,
                                                                                        self.optionalGroupsList,
                                                                                        self.metricConst,
                                                                                        self.outIdField)
                
            def _makeTabAreaTable(self):
                AddMsg(self.timer.split() + " Generating a zonal tabulate area table")
                # Internal function to generate a zonal tabulate area table
                self.tabAreaTable = TabulateAreaTable(self.inReportingUnitFeature, self.reportingUnitIdField,
                                                      self.inLandCoverGrid, self.tableName)
                
            def _calculateMetrics(self):
                AddMsg(self.timer.split() + " Processing the tabulate area table and computing metric values")
                # Internal function to process the tabulate area table and compute metric values. Use values to populate the ATtILA output table
                utils.calculate.landCoverDiversity(self.optionalGroupsList, self.metricConst, self.outIdField, 
                                                   self.newTable, self.tabAreaTable, self.metricsFieldnameDict, self.zoneAreaDict)
                
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

    except Exception, e:
        errors.standardErrorHandling(e)

    finally:
        setupAndRestore.standardRestore()


def runPopulationDensityCalculator(inReportingUnitFeature, reportingUnitIdField, inCensusFeature, inPopField, outTable,
                                   popChangeYN, inCensusFeature2, inPopField2, optionalFieldGroups):
    """ Interface for script executing Population Density Metrics """
    from arcpy import env
    from pylet import arcpyutil
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
        env.workspace = arcpyutil.environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))
        # Strip the description from the "additional option" and determine whether intermediates are stored.
        processed = arcpyutil.parameters.splitItemsAndStripDescriptions(optionalFieldGroups, globalConstants.descriptionDelim)
        if globalConstants.intermediateName in processed:
            msg = "\nIntermediates are stored in this directory: {0}\n"
            AddMsg(msg.format(env.workspace))
            cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
        else:
            cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
        
        # Create a copy of the reporting unit feature class that we can add new fields to for calculations.  This 
        # is more appropriate than altering the user's input data. Keep only the OID, shape, and reportingUnitIdField fields
        fieldMappings = arcpy.FieldMappings()
        fieldMappings.addTable(inReportingUnitFeature)
        [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name <> reportingUnitIdField]

        AddMsg(timer.split() + " Creating temporary copy of reporting unit layer")
        tempReportingUnitFeature = utils.files.nameIntermediateFile(["tempReportingUnitFeature","FeatureClass"],cleanupList)
        inReportingUnitFeature = arcpy.FeatureClassToFeatureClass_conversion(inReportingUnitFeature,env.workspace,
                                                                             os.path.basename(tempReportingUnitFeature),"",
                                                                             fieldMappings)

        # Add and populate the area field (or just recalculate if it already exists
        ruArea = utils.vector.addAreaField(inReportingUnitFeature,metricConst.areaFieldname)
        
        # Build the final output table.
        AddMsg(timer.split() + " Creating output table")
        arcpy.TableToTable_conversion(inReportingUnitFeature,os.path.dirname(outTable),os.path.basename(outTable))
        
        AddMsg(timer.split() + " Calculating population density")
        # Create an index value to keep track of intermediate outputs and fieldnames.
        index = ""
        #if popChangeYN:
        if string.upper(str(popChangeYN)) == "TRUE":
            index = "1"
        # Perform population density calculation for first (only?) population feature class
        utils.calculate.getPopDensity(inReportingUnitFeature,reportingUnitIdField,ruArea,inCensusFeature,inPopField,
                                      env.workspace,outTable,metricConst,cleanupList,index)

        #if popChangeYN:
        if string.upper(str(popChangeYN)) == "TRUE":
            index = "2"
            AddMsg(timer.split() + " Calculating population density for second feature class")
            # Perform population density calculation for second population feature class
            utils.calculate.getPopDensity(inReportingUnitFeature,reportingUnitIdField,ruArea,inCensusFeature2,inPopField2,
                                          env.workspace,outTable,metricConst,cleanupList,index)
            
            AddMsg(timer.split() + " Calculating population change")
            # Set up a calculation expression for population change
            calcExpression = "getPopChange(!popCount_1!,!popCount_2!)"
            codeBlock = """def getPopChange(pop1,pop2):
    if pop1 == 0:
        if pop2 == 0:
            return 0
        else:
            return 1
    else:
        return ((pop2-pop1)/pop1)*100"""
            
            # Calculate the population density
            utils.vector.addCalculateField(outTable,metricConst.populationChangeFieldName,calcExpression,codeBlock)       

        AddMsg(timer.split() + " Calculation complete")
    except Exception, e:
        errors.standardErrorHandling(e)

    finally:
        if not cleanupList[0] == "KeepIntermediates":
            for (function,arguments) in cleanupList:
                # Flexibly executes any functions added to cleanup array.
                function(*arguments)
        env.workspace = _tempEnvironment1
        
def runMDCPMetrics(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
                   metricsToRun, maxSeparation, minPatchsize, SearchRadius, outTable,processingCellSize, snapRaster,
                   optionalFieldGroups):
        try:
            from pylet import arcpyutil
            from arcpy import env
            cleanupList = []
            # retrieve the attribute constants associated with this metric
            metricConst = metricConstants.mdcpConstants()
            # append the edge width distance value to the field suffix
            
            metricsBaseNameList, optionalGroupsList = setupAndRestore.standardSetup(snapRaster, processingCellSize,
                                                                                     os.path.dirname(outTable),
                                                                                     [metricsToRun,optionalFieldGroups] )
            
            # set the environmental extent to that of the reporting unit theme, aligned to the land cover grid, and buffered with the edge width
            env.extent = arcpyutil.environment.getBufferedExtent(inReportingUnitFeature, inLandCoverGrid, processingCellSize)

            
            lccObj = lcc.LandCoverClassification(lccFilePath)
            outIdField = utils.settings.getIdOutField(inReportingUnitFeature, reportingUnitIdField)
            
            env.workspace = arcpyutil.environment.getWorkspaceForIntermediates(globalConstants.scratchGDBFilename, os.path.dirname(outTable))
            # Strip the description from the "additional option" and determine whether intermediates are stored.
            processed = arcpyutil.parameters.splitItemsAndStripDescriptions(optionalFieldGroups, globalConstants.descriptionDelim)
            if globalConstants.intermediateName in processed:
                msg = "\nIntermediates are stored in this directory: {0}\n"
                AddMsg(msg.format(env.workspace))
                cleanupList.append("KeepIntermediates")  # add this string as the first item in the cleanupList to prevent cleanups
            else:
                cleanupList.append((arcpy.AddMessage,("Cleaning up intermediate datasets",)))
            
            #Create the output table outside of metricCalc so that result can be added for multiple metrics
            newtable, metricsFieldnameDict = utils.table.tableWriterByClass(outTable, metricsBaseNameList,optionalGroupsList, 
                                                                                          metricConst, lccObj, outIdField)
            # Run metric calculate for each metric in list
            for m in metricsBaseNameList:
                # Subclass that overrides specific functions for the MDCP calculation
                class metricCalcMDCP(metricCalc):

                    def _replaceLCGrid(self):
                        # replace the inLandCoverGrid
                        AddMsg(self.timer.split() + " Creating Patches")
                        self.inLandCoverGrid = utils.raster.createPatchRaster(m, self.lccObj, self.lccClassesDict, self.inLandCoverGrid,
                                                                              os.path.dirname(outTable), self.maxSeparation,
                                                                              self.minPatchsize, processingCellSize)
                
                        if self.saveIntermediates:
                            self.scratchName = arcpy.CreateScratchName(self.metricConst.shortName+"Raster", m, "RasterDataset")
                            self.inLandCoverGrid.save(self.scratchName)
                            #arcpy.CopyRaster_management(self.inLandCoverGrid, self.scratchName)
                            AddMsg(self.timer.split() + " Save intermediate grid complete: "+os.path.basename(self.scratchName))
                            
                    #skip over make out table since it has already been made
                    def _makeAttilaOutTable(self):
                        pass

                    #skip over make Tabulate Area Table since this metric does not require it
                    def _makeTabAreaTable(self):
                        pass
                    
                    #Update housekeeping so it doesn't check for lcc codes
                    def _housekeeping(self):
                        # Perform additional housekeeping steps - this must occur after any LCGrid or inRUFeature replacement
                        # Removed alert about lcc codes since the lcc values are not used in the Core/Edge calculations
                        # alert user if the land cover grid cells are not square (default to size along x axis)
                        utils.settings.checkGridCellDimensions(self.inLandCoverGrid)
                        # if an OID type field is used for the Id field, create a new field; type integer. Otherwise copy the Id field
                        self.outIdField = utils.settings.getIdOutField(self.inReportingUnitFeature, self.reportingUnitIdField)
                    
                        # If QAFIELDS option is checked, compile a dictionary with key:value pair of ZoneId:ZoneArea
                        self.zoneAreaDict = None
                        if globalConstants.qaCheckName in self.optionalGroupsList:
                            # Check to see if an outputGeorgraphicCoordinate system is set in the environments. If one is not specified
                            # return the spatial reference for the land cover grid. Use the returned spatial reference to calculate the
                            # area of the reporting unit's polygon features to store in the zoneAreaDict
                            self.outputSpatialRef = utils.settings.getOutputSpatialReference(self.inLandCoverGrid)
                            self.zoneAreaDict = polygons.getIdAreaDict(self.inReportingUnitFeature, self.reportingUnitIdField, self.outputSpatialRef)

                    # Update calculateMetrics to populate Mean Distance to Closest Patch
                    def _calculateMetrics(self):
                        self.newTable = newtable
                        self.metricsFieldnameDict = metricsFieldnameDict

                        #calculate MDCP value    
                        
                        rastoPoly = utils.files.nameIntermediateFile(metricConst.rastertoPoly,cleanupList)
                        rastoPt = utils.files.nameIntermediateFile(metricConst.rastertoPoint, cleanupList)
                        polyDiss = utils.files.nameIntermediateFile(metricConst.polyDissolve, cleanupList)
                        clipPolyDiss = utils.files.nameIntermediateFile(metricConst.clipPolyDissolve, cleanupList) 
                        nearPatchTable = utils.files.nameIntermediateFile(metricConst.nearTable, cleanupList)                    
                        AddMsg(self.timer.split() + " Calculating Mean Distances")
                        
                        self.mdcpDict =  utils.vector.tabulateMDCP(self.inLandCoverGrid, os.path.dirname(outTable),
                                                                   self.inReportingUnitFeature, self.reportingUnitIdField,
                                                                   SearchRadius, rastoPoly, rastoPt, polyDiss, clipPolyDiss,
                                                                   nearPatchTable)
                        # update
                        utils.calculate.getMDCP(self.outIdField, self.newTable, self.mdcpDict, self.metricsFieldnameDict,
                                                 self.metricConst, m)
                # Create new instance of metricCalc class to contain parameters
                mdcpCalc = metricCalcMDCP(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath,
                          m, outTable, processingCellSize, snapRaster, optionalFieldGroups, metricConst)
                
                mdcpCalc.maxSeparation = maxSeparation
                mdcpCalc.minPatchsize = minPatchsize
                
                #Run Calculation
                mdcpCalc.run()
                
                mdcpCalc.metricsBaseNameList = metricsBaseNameList
                AddMsg("MDCP analysis has been run for landuse " + m)
        except Exception, e:
            errors.standardErrorHandling(e)

        finally:
            setupAndRestore.standardRestore()
            if not cleanupList[0] == "KeepIntermediates":
                for (function,arguments) in cleanupList:
                    # Flexibly executes any functions added to cleanup array.
                    function(*arguments)
