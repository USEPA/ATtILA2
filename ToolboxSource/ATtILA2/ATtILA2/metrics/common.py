'''
Created on Apr 23, 2012

@author: mjacks07
'''
import os
import sys

import arcpy
from arcpy import env
from arcpy.sa import Raster, Con

from pylet import arcpyutil
from pylet import lcc

import fields as outFields
import constants as metricConstants


###########################################################################################################
#Land Cover on Slope Proportions (Land Cover Slope Overlap)
###########################################################################################################

def landCoverOnSlopeProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid,lccName, lccFilePath, 
                                metricsToRun, inSlopeGrid, inSlopeThresholdValue, outTable, processingCellSize, 
                                snapRaster, optionalFieldGroups):
    """ Land Cover on Slope Proportions (Land Cover Slope Overlap)"""
    
    # Check out any necessary licenses
    arcpy.CheckOutExtension("spatial")

    
    # XML Land Cover Coding file loaded into memory
    lccObj = lcc.LandCoverClassification(lccFilePath)
    
    SLPxLCGrid = getIntersectOfGrids(lccObj,inLandCoverGrid, inSlopeGrid, inSlopeThresholdValue)
    
    # save the file if intermediate products outputs are checked
    #SLPxLCGrid.save(arcpy.CreateUniqueName("slxlc"))
    
    
    

def getIntersectOfGrids(lccObj,inLandCoverGrid, inSlopeGrid, inSlopeThresholdValue):
        
    # Generate the slope X land cover gird where areas below the threshold slope are
    # set to the value 'Maximum Land Cover Class Value + 1'.
    LCGrid = Raster(inLandCoverGrid)
    SLPGrid = Raster(inSlopeGrid)
    AreaBelowThresholdValue = int(LCGrid.maximum + 1)
    where_clause = "VALUE >= " + inSlopeThresholdValue
    SLPxLCGrid = Con(SLPGrid, LCGrid, AreaBelowThresholdValue, where_clause)
    
    # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area calculation    
    lccValuesDict = lccObj.values
    
    # get the frozenset of excluded values (i.e., values not to use when calculating the reporting unit effective area)
    excludedValues = lccValuesDict.getExcludedValueIds()
        
    # if certain land cover codes are tagged as 'excluded = TRUE', generate grid where land cover codes are 
    # preserved for areas coincident with steep slopes, areas below the slope threshold are coded with the 
    # AreaBelowThresholdValue except for where the land cover code is included in the excluded values list.
    # In that case, the excluded land cover values are maintained in the low slope areas.
    if excludedValues:
        # build a whereClause string (e.g. "VALUE = 11 or VALUE = 12") to identify where on the land cover grid excluded values occur
        whereExcludedClause = "VALUE = " + " or VALUE = ".join([str(item) for item in excludedValues])
    
        SLPxLCGrid = Con(LCGrid, LCGrid, SLPxLCGrid, whereExcludedClause)
    
    return SLPxLCGrid




###########################################################################################################
#Land Cover Proportions
###########################################################################################################

def landCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid,lccName, lccFilePath, metricsToRun, outTable, processingCellSize, snapRaster, optionalFieldGroups) :
    """ Land Cover Proportion Metrics """   
     
    # Check out any necessary licenses
    arcpy.CheckOutExtension("spatial")
    
      
    # the variables row and rows are initially set to None, so that they can
    # be deleted in the finally block regardless of where (or if) script fails
    outTableRow = None
    outTableRows = None
    tabAreaTableRow = None
    tabAreaTableRows = None
    
    # get current snap environment to restore at end of script
    tempEnvironment0 = env.snapRaster
        
    try:
        # Use this script's name to obtain information on output field naming, additional optional fields, and 
        # field naming overrides.
        
        # determine the maximum size of output field names based on the output table's destination/type
        maxFieldNameSize = arcpyutil.fields.getFieldNameSizeLimit(outTable)        
        
        # Set parameters for metric output field. use this file's name to determine the metric type
        # Parameters = [Fieldname_prefix, Fieldname_suffix, Field_type, Field_Precision, Field_scale]
        # e.g., fldParams = ["p", "", "FLOAT", 6, 1]
        fldParams = outFields.getFieldParametersFromFilePath()

        # get the field name override key using this script's name
        fieldOverrideKey = outFields.getFieldOverrideKeyFromFilePath()
        
        # if any optional fields are selected, get their parameters
        optionalGroupsList = arcpyutil.parameters.splitItemsAndStripDescriptions(optionalFieldGroups, metricConstants.descriptionDelim)
        
        if metricConstants.qaCheckName in optionalGroupsList:
            # Parameratize optional fields, e.g., optionalFlds = [["LC_Overlap","FLOAT",6,1]]
            qaCheckFlds = outFields.getQACheckFieldParametersFromFilePath()
        else:
            qaCheckFlds = None
            
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
                outputFName = fldParams[0]+mClassName+fldParams[1]
                
                thresholdValue = ""
                # see if the provided field name is too long for the output table type
                if len(outputFName) > maxFieldNameSize:
                    defaultFieldName = outputFName # keep track of the originally generated field name
                    
                    prefixLen = len(fldParams[0])
                    suffixLen = len(fldParams[1])
                    maxBaseSize = maxFieldNameSize - prefixLen - suffixLen - len(thresholdValue)
                        
                    outputFName = fldParams[0]+mClassName[:maxBaseSize]+fldParams[1]+thresholdValue # truncate field name to maximum allowable size
                    
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
        newTable = CreateMetricOutputTable(outTable,inReportingUnitFeature,reportingUnitIdField,metricsClassNameList,metricsFieldnameDict,fldParams,qaCheckFlds,addAreaFldParams)
        
        # Process: Tabulate Area
        # set the snap raster environment so the rasterized polygon theme aligns with land cover grid cell boundaries
        env.snapRaster = snapRaster
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
            valFieldsResults = ProcessTabAreaValueFields(TabAreaValueFields,TabAreaValues,tabAreaDict,tabAreaTableRow,excludedValues)
            tabAreaDict = valFieldsResults[0]
            effectiveAreaSum = valFieldsResults[1]
            excludedAreaSum = valFieldsResults[2]
            
            # sum the areas for the selected metric's grid codes   
            for mClassName in metricsClassNameList: 
                # get the grid codes for this specified metric
                metricGridCodesList = lccClassesDict[mClassName].uniqueValueIds
                # get the class percentage area and it's actual area from the tabulate area table
                metricPercentageAndArea = CalcMetricPercentArea(metricGridCodesList, tabAreaDict, effectiveAreaSum)
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
        import traceback
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
        if outTableRow: 
            del outTableRow
        if outTableRows: 
            del outTableRows
        if tabAreaTableRows: 
            del tabAreaTableRows
        if tabAreaTableRow: 
            del tabAreaTableRow
            
        # restore the environments
        env.snapRaster = tempEnvironment0
        
        # return the spatial analyst license    
        arcpy.CheckInExtension("spatial")
        
        print "Finished."


def CalcMetricPercentArea(metricGridCodesList, tabAreaDict, effectiveAreaSum):
    """ Calculates the percentage of the reporting unit effective area occupied by the metric class codes and their total area
    
        DESCRIPTION
        -----------
        Retrieves stored area figures for each grid code associated with selected metric and sums them.
        That number, divided by the total effective area within the reporting unit and multiplied by 100, gives the
        percentage of the effective reporting unit that is occupied by the metric class. Both the percentage and the 
        final area sum are returned.
        
        PARAMETERS
        ----------
        metricGridCodesList: list of all grid values assigned to a metric class in the lcc file (e.g., [41, 42, 43] for the forest class)
        tabAreaDict: dictionary with the area value of each grid code in a reporting unit keyed to the grid code
        effectiveAreaSum: sum of the area of all grid cells in the reporting unit with codes not tagged as excluded in the lcc file
        
        RETURNS
        -------
        Tuple:
            float 1 - the percentage of the reporting unit effective area that is occupied by the metric class codes
            float 2 - the sum of the area of metric class codes
        
    """
    
    metricAreaSum = 0                         
    for aValueID in metricGridCodesList:
        metricAreaSum += tabAreaDict.get(aValueID, 0) #add 0 if the lcc defined value is not found in the grid
    
    if effectiveAreaSum > 0:
        metricPercentArea = (metricAreaSum / effectiveAreaSum) * 100
    else: # all values found in reporting unit are in the excluded set
        metricPercentArea = 0
        
    return metricPercentArea, metricAreaSum


def ProcessTabAreaValueFields(TabAreaValueFields, TabAreaValues, tabAreaDict, tabAreaTableRow, excludedValues):
    """ Processes the 'VALUE_' fields in a supplied row object for exclusion/inclusion status in metric area/percentage calculations. 
    
        DESCRIPTION
        -----------
        1) Go through each 'VALUE_' field in the TabulateArea table one row at a time and put the area value
           for each grid code into a dictionary with the grid code as the key.
        2) Determine if the area for the grid code is to be included into the reporting unit effective area sum.
        3) Keep a running total of effective and excluded area within the reporting unit. Added together, these 
           area sums provide the total grid area present in the reporting unit. That value is used to calculate
           the amount of overlap between the reporting unit polygon and the underlying land cover grid.
           
        PARAMETERS
        ----------
        TabAreaValueFields: a list of the 'VALUE_' fieldnames from a TabulateArea generated table
        TabAreaValues: a list of integer grid code values generated from the 'VALUE_' fieldnames
        tabAreaDict: an empty dictionary to be populated with a key:value pair of gridcode:area
        tabAreaTableRow: the current row object from TabluateArea output table arcpy SearchCursor
        excludedValues: a frozenset of values not to use when calculating the reporting unit effective area.
        
        RETURNS
        -------
        Tuple:
            dictionary - dictionary with the area value of each grid code in a reporting unit keyed to the grid code
            float 1 - sum of the area within the reporting unit to be included in the percentage calculations
            float 2 - sum of the area within the reporting unit to be excluded from percentage calculations
            
    """
    
    excludedAreaSum = 0  #area of reporting unit not used in metric calculations e.g., water area
    effectiveAreaSum = 0  #effective area of the reporting unit e.g., land area

    for i, aFld in enumerate(TabAreaValueFields):
        # store the grid code and it's area value into the dictionary
        valKey = TabAreaValues[i]
        valArea = tabAreaTableRow.getValue(aFld.name)
        tabAreaDict[valKey] = valArea

        #add the area of each grid value to the appropriate area sum i.e., effective or excluded area
        if valKey in excludedValues:
            excludedAreaSum += valArea
        else:
            effectiveAreaSum += valArea               
                       
    return (tabAreaDict, effectiveAreaSum, excludedAreaSum)


def CreateMetricOutputTable(outTable, inReportingUnitFeature, reportingUnitIdField, metricsClassNameList, metricsFieldnameDict, fldParams, qaCheckFlds, addAreaFldParams):
    """ Returns new empty table for ATtILA metric generation output with appropriate fields for selected metric
    
        DESCRIPTION
        -----------
        Creates an empty table with fields for the reporting unit id, all selected metrics with appropriate fieldname
        prefixes and suffixes (e.g. pUrb, rFor30), and any selected optional fields (e.g., LC_Overlap)
        
        PARAMETERS
        ----------
        outTable: file name including path for the ATtILA output table
        inReportingUnitFeature: CatalogPath to the input reporting unit layer
        reportingUnitIdField: fieldname for the input reporting unit id field
        metricsClassNameList: a list of metric ClassNames parsed from the 'Metrics to run' input (e.g., [for, agt, shrb, devt])
        metricsFieldnameDict: a dictionary of ClassName keys with field name values (e.g., "unat":"UINDEX", "for":"pFor")
        fldParams: list of parameters to generate the selected metric output field (i.e., [Fieldname_prefix, Fieldname_suffix, Field_type, Field_Precision, Field_scale])
        qaCheckFlds: a list of filename parameter lists for one or more selected optional fields fieldname generation (e.g., optionalFlds = [["LC_Overlap","FLOAT",6,1]])
        addAreaFldParams: a list of filename parameters for the optional Add Area Fields selection (e.g., ["_A","DOUBLE",15,0])
        
        RETURNS
        -------
        Table
        
    """
    outTablePath, outTableName = os.path.split(outTable)
        
    # need to strip the dbf extension if the outpath is a geodatabase; 
    # should control this in the validate step or with an arcpy.ValidateTableName call
    newTable = arcpy.CreateTable_management(outTablePath, outTableName)
    
    # process the user input to add id field to output table
    IDfield = arcpyutil.fields.getFieldByName(inReportingUnitFeature, reportingUnitIdField)
    arcpy.AddField_management(newTable, IDfield.name, IDfield.type, IDfield.precision, IDfield.scale)
                
    # add metric fields to the output table.
    [arcpy.AddField_management(newTable, metricsFieldnameDict[mClassName], fldParams[2], fldParams[3], fldParams[4])for mClassName in metricsClassNameList]

    # add any optional fields to the output table
    if qaCheckFlds:
        [arcpy.AddField_management(newTable, qaFld[0], qaFld[1], qaFld[2]) for qaFld in qaCheckFlds]
        
    if addAreaFldParams:
        [arcpy.AddField_management(newTable, metricsFieldnameDict[mClassName]+addAreaFldParams[0], addAreaFldParams[1], addAreaFldParams[2], addAreaFldParams[3])for mClassName in metricsClassNameList]
         
    # delete the 'Field1' field if it exists in the new output table.
    arcpyutil.fields.deleteFields(newTable, ["field1"])
    
        
    return newTable