''' Interface for running specific metrics

'''
import os
import sys
import traceback

import arcpy
from arcpy import env

from pylet import arcpyutil
from pylet import lcc

from ATtILA2.constants import fieldConstants
from ATtILA2.constants import metricConstants
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
    
    
    
def landCoverOnSlopeProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid,lccName, lccFilePath, 
                                metricsToRun, inSlopeGrid, inSlopeThresholdValue, outTable, processingCellSize, 
                                snapRaster, optionalFieldGroups):
    """ Land Cover on Slope Proportions (Land Cover Slope Overlap)"""
    
    standardSetup(snapRaster, os.path.dirname(outTable))
    
    # XML Land Cover Coding file loaded into memory
    lccObj = lcc.LandCoverClassification(lccFilePath)
    
    SLPxLCGrid = utils.raster.getIntersectOfGrids(lccObj, inLandCoverGrid, inSlopeGrid, inSlopeThresholdValue)
    
    # save the file if intermediate products outputs are checked
    #SLPxLCGrid.save(arcpy.CreateUniqueName("slxlc"))
    

    standardRestore(snapRaster)
    
    
def landCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, 
                         metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups):
    """ Land Cover Proportion Metrics """   
    
    standardSetup(snapRaster, os.path.dirname(outTable))
    
    
    landCoverProportionsCalculator(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                         metricsToRun, outTable, processingCellSize, optionalFieldGroups)
    
    standardRestore()
    

    
def landCoverProportionsCalculator(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccFilePath, 
                         metricsToRun, outTable, processingCellSize, optionalFieldGroups):
       
    try:        
        
        # Set parameters for metric output field. use this file's name to determine the metric type
        # Parameters = [Fieldname_prefix, Fieldname_suffix, Field_type, Field_Precision, Field_scale]
        # e.g., fldParams = ["p", "", "FLOAT", 6, 1]
        fldParams = fieldConstants.getFieldParametersFromFilePath()
        
        # get the field name override key using this script's name
        fieldOverrideKey = fieldConstants.getFieldOverrideKeyFromFilePath()
        
        # if any optional fields are selected, get their parameters
        optionalGroupsList = arcpyutil.parameters.splitItemsAndStripDescriptions(optionalFieldGroups, metricConstants.descriptionDelim)
        
        if metricConstants.qaCheckName in optionalGroupsList:
            # Parameratize optional fields, e.g., optionalFlds = [["LC_Overlap","FLOAT",6,1]]
            qaCheckFlds = fieldConstants.getQACheckFieldParametersFromFilePath()
        else:
            qaCheckFlds = None
        
        maxFieldNameSize = arcpyutil.fields.getFieldNameSizeLimit(outTable)            
        if metricConstants.metricAddName in optionalGroupsList:
            addAreaFldParams = metricConstants.areaFieldParameters
            maxFieldNameSize = maxFieldNameSize - len(addAreaFldParams[0])
        else:
            addAreaFldParams = None
        
        # Process: inputs
        # XML Land Cover Coding file loaded into memory
        lccObj = lcc.LandCoverClassification(lccFilePath)
        # get dictionary of metric class values (e.g., classValuesDict['for'].uniqueValueIds = (41, 42, 43))
        lccClassesDict = lccObj.classes    
        # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area calculation
        lccValuesDict = lccObj.values
        # get the frozenset of excluded values (i.e., values not to use when calculating the reporting unit effective area)
        excludedValues = lccValuesDict.getExcludedValueIds()
        
        # take the 'Metrics to run' input and parse it into a list of metric ClassNames
        metricsClassNameList = arcpyutil.parameters.splitItemsAndStripDescriptions(metricsToRun, metricConstants.descriptionDelim)
        
        # use the metricsClassNameList to create a dictionary of ClassName keys with field name values using any user supplied field names
        metricsFieldnameDict = {}
        outputFieldNames = set() # use this set to help make field names unique
        
        for mClassName in metricsClassNameList:
            # generate unique number to replace characters at end of truncated field names
            n = 1
            
            fieldOverrideName = lccClassesDict[mClassName].attributes.get(fieldOverrideKey,None)
            if fieldOverrideName: # a field name override exists
                # see if the provided field name is too long for the output table type
                if len(fieldOverrideName) > maxFieldNameSize:
                    defaultFieldName = fieldOverrideName # keep track of the originally provided field name
                    fieldOverrideName = fieldOverrideName[:maxFieldNameSize] # truncate field name to maximum allowable size
                    
                    # see if truncated field name is already used.
                    # if so, truncate further and add a unique number to the end of the name
                    while fieldOverrideName in outputFieldNames:
                        # shorten the field name and increment it
                        truncateTo = maxFieldNameSize - len(str(n))
                        fieldOverrideName = fieldOverrideName[:truncateTo]+str(n)
                        n = n + 1
                        
                    arcpy.AddWarning("Provided metric name too long for output location. Truncated "+defaultFieldName+" to "+fieldOverrideName)
                    
                # keep track of output field names    
                outputFieldNames.add(fieldOverrideName)
                # add output field name to dictionary
                metricsFieldnameDict[mClassName] = fieldOverrideName
            else:
                # generate output field name
                outputFName = fldParams[0] + mClassName + fldParams[1]
                
                thresholdValue = ""
                # see if the provided field name is too long for the output table type
                if len(outputFName) > maxFieldNameSize:
                    defaultFieldName = outputFName # keep track of the originally generated field name
                    
                    prefixLen = len(fldParams[0])
                    suffixLen = len(fldParams[1])
                    maxBaseSize = maxFieldNameSize - prefixLen - suffixLen - len(thresholdValue)
                        
                    outputFName = fldParams[0] + mClassName[:maxBaseSize] + fldParams[1] + thresholdValue # truncate field name to maximum allowable size
                    
                    # see if truncated field name is already used.
                    # if so, truncate further and add a unique number to the end of the name
                    while outputFName in outputFieldNames:
                        # shorten the field name and increment it
                        truncateTo = maxBaseSize - len(str(n))
                        outputFName = fldParams[0]+mClassName[:truncateTo]+str(n)+fldParams[1]
                        n = n + 1
                        
                    arcpy.AddWarning("Metric field name too long for output location. Truncated "+defaultFieldName+" to "+outputFName)
                    
                # keep track of output field names
                outputFieldNames.add(outputFName)             
                # add output field name to dictionary
                metricsFieldnameDict[mClassName] = outputFName
                    
        # create the specified output table
        newTable = utils.table.CreateMetricOutputTable(outTable,inReportingUnitFeature,reportingUnitIdField,metricsClassNameList,metricsFieldnameDict,fldParams,qaCheckFlds,addAreaFldParams)
        
        # Process: Tabulate Area

        
        # store the area of each input reporting unit into dictionary (zoneID:area)
        zoneAreaDict = arcpyutil.polygons.getAreasByIdDict(inReportingUnitFeature, reportingUnitIdField)
        # create name for a temporary table for the tabulate area geoprocess step - defaults to current workspace 
        scratch_Table = arcpy.CreateScratchName("xtmp", "", "Dataset")
        # run the tabulatearea geoprocess
        arcpy.gp.TabulateArea_sa(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, "Value", scratch_Table, processingCellSize)  

        # Process output table from tabulatearea geoprocess
        # get the VALUE fields from Tabulate Area table
        TabAreaValueFields = arcpy.ListFields(scratch_Table)[2:]
        # get the grid code values from the field names; put in a list of integers
        TabAreaValues = [int(aFld.name.replace("VALUE_","")) for aFld in TabAreaValueFields]
        # create dictionary to later hold the area value of each grid code in the reporting unit
        tabAreaDict = dict(zip(TabAreaValues,[])) 
        
        # alert user if input grid had values not defined in LCC file
        undefinedValues = [aVal for aVal in TabAreaValues if aVal not in lccObj.getUniqueValueIdsWithExcludes()]     
        if undefinedValues:
            arcpy.AddWarning("Following Grid Values undefined in LCC file: "+str(undefinedValues)+"  - By default, the area for undefined grid codes is included when determining the effective reporting unit area.")

        
        # create the cursor to add data to the output table
        outTableRows = arcpy.InsertCursor(newTable)
        
        # create cursor to search/query the TabAreaOut table
        tabAreaTableRows = arcpy.SearchCursor(scratch_Table)
        
        for tabAreaTableRow in tabAreaTableRows:
            # initiate a row to add to the metric output table
            outTableRow = outTableRows.newRow()

            # get reporting unit id
            zoneIDvalue = tabAreaTableRow.getValue(reportingUnitIdField)            
            # set the reporting unit id value in the output row
            outTableRow.setValue(reportingUnitIdField, zoneIDvalue)
            
            # Process the value fields in the TabulateArea Process output table
            # 1) Go through each value field in the TabulateArea table row and put the area
            #    value for the grid code into a dictionary with the grid code as the key.
            # 2) Determine if the grid code is to be included into the reporting unit effective area sum
            # 3) Calculate the total grid area present in the reporting unit
            valFieldsResults = utils.field.ProcessTabAreaValueFields(TabAreaValueFields, TabAreaValues, tabAreaDict, tabAreaTableRow, excludedValues)
            tabAreaDict = valFieldsResults[0]
            effectiveAreaSum = valFieldsResults[1]
            excludedAreaSum = valFieldsResults[2]
            
            # sum the areas for the selected metric's grid codes   
            for mClassName in metricsClassNameList: 
                # get the grid codes for this specified metric
                metricGridCodesList = lccClassesDict[mClassName].uniqueValueIds
                
                # get the class percentage area and it's actual area from the tabulate area table
                metricPercentageAndArea = utils.area.CalcMetricPercentArea(metricGridCodesList, tabAreaDict, effectiveAreaSum)
                
                # add the calculation to the output row
                outTableRow.setValue(metricsFieldnameDict[mClassName], metricPercentageAndArea[0])
                
                if addAreaFldParams:
                    outTableRow.setValue(metricsFieldnameDict[mClassName]+"_A", metricPercentageAndArea[1])

            # add QACheck calculations/values to row
            if qaCheckFlds:
                zoneArea = zoneAreaDict[zoneIDvalue]
                overlapCalc = ((effectiveAreaSum+excludedAreaSum)/zoneArea) * 100
                outTableRow.setValue(qaCheckFlds[0][0], overlapCalc)
                outTableRow.setValue(qaCheckFlds[1][0], effectiveAreaSum+excludedAreaSum)
                outTableRow.setValue(qaCheckFlds[2][0], effectiveAreaSum)
                outTableRow.setValue(qaCheckFlds[3][0], excludedAreaSum)
            
            # commit the row to the output table
            outTableRows.insertRow(outTableRow)

        
        # Housekeeping
        # delete the scratch table
        arcpy.Delete_management(scratch_Table)

                
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        
    except:
        
        # get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
    
        # Return python error messages for use in script tool
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)

        
    finally:
        # delete cursor and row objects to remove locks on the data
        try:
            del outTableRow
        except:
            pass
        
        try:
            del outTableRows
        except:
            pass

        try:
            del tabAreaTableRows
        except:
            pass  
        
        try:
            del tabAreaTableRow
        except:
            pass  
        
            








