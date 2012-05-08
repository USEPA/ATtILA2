""" Utilitites specific to area

"""
from ATtILA2.constants import metricConstants, globalConstants
import ATtILA2
from pylet import arcpyutil, lcc
import arcpy
import traceback
import sys

def getMetricPercentAreaAndSum(metricGridCodesList, tabAreaDict, effectiveAreaSum):
    """ Calculates the percentage of the reporting unit effective area occupied by the metric class codes and their 
    total area
    
    **Description:**

        Retrieves stored area figures for each grid code associated with selected metric and sums them.
        That number, divided by the total effective area within the reporting unit and multiplied by 100, gives the
        percentage of the effective reporting unit that is occupied by the metric class. Both the percentage and the 
        final area sum are returned.
        
    **Arguments:**

        * *metricGridCodesList* - list of all grid values assigned to a metric class in the lcc file (e.g., [41, 42, 43] 
                                for the forest class)
                             
        * *tabAreaDict* - dictionary with the area value of each grid code in a reporting unit keyed to the grid code
        
        * *effectiveAreaSum* - sum of the area of all grid cells in the reporting unit with codes not tagged as excluded 
                                in the lcc file
        
    **Returns:**

        * float - the percentage of the reporting unit effective area that is occupied by the metric class codes
        * float - the sum of the area of metric class codes
        
    """
    
    metricAreaSum = 0                         
    for aValueID in metricGridCodesList:
        metricAreaSum += tabAreaDict.get(aValueID, 0) #add 0 if the lcc defined value is not found in the grid
    
    if effectiveAreaSum > 0:
        metricPercentArea = (metricAreaSum / effectiveAreaSum) * 100
    else: # all values found in reporting unit are in the excluded set
        metricPercentArea = 0
        
    return metricPercentArea, metricAreaSum


def landCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccObj, 
                         metricsClassNameList, outTable, processingCellSize, optionalGroupsList, metricConst):
    """ Creates *outTable* populated with land cover proportions metrics
    
    **Description:**

        Creates *outTable* populated with land cover proportions metrics...
        
    **Arguments:**

        * *inReportingUnitFeature* - Input reporting units
        * *reportingUnitIdField* - name of unique id field in reporting units
        * *inLandCoverGrid* - land cover raster
        * *lccObj* - land cover classification(lcc) object
        * *metricsToRun* - list of class ids to include in processing
        * *outTable* - full path to an output table to be created/populated
        * *processingCellSize* - processing cell size
        * *optionalFieldGroups* - optional fields to create
        * *metricConst* - an object with constants specific to the metric being run (lcp vs lcosp)
        
    **Returns:**

        * None
        
    """
    
    try:
        # Used for intellisense.  Will also raise error if metricConst is not the right type of object        
        assert isinstance(metricConst, metricConstants.baseMetricConstants) 
        
        # get the field name override key
        fieldOverrideKey = metricConst.fieldOverrideKey

        # Set parameters for metric output field. 
        # Parameters = [Fieldname_prefix, Fieldname_suffix, Field_type, Field_Precision, Field_scale]
        # e.g., fldParams = ["p", "", "FLOAT", 6, 1]
        fldParams = metricConst.fieldParameters
        
        if globalConstants.qaCheckName in optionalGroupsList:
            # Parameratize optional fields, e.g., optionalFlds = [["LC_Overlap","FLOAT",6,1]]
            qaCheckFlds = metricConst.qaCheckFieldParameters
        else:
            qaCheckFlds = None
        
        maxFieldNameSize = arcpyutil.fields.getFieldNameSizeLimit(outTable)            
        if globalConstants.metricAddName in optionalGroupsList:
            addAreaFldParams = globalConstants.areaFieldParameters
            maxFieldNameSize = maxFieldNameSize - len(addAreaFldParams[0])
        else:
            addAreaFldParams = None
        
        # Process: inputs
        # get dictionary of metric class values (e.g., classValuesDict['for'].uniqueValueIds = (41, 42, 43))
        lccClassesDict = lccObj.classes    
        # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area calculation
        lccValuesDict = lccObj.values
        # get the frozenset of excluded values (i.e., values not to use when calculating the reporting unit effective area)
        excludedValues = lccValuesDict.getExcludedValueIds()
        
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
                
                # see if the provided field name is too long for the output table type
                if len(outputFName) > maxFieldNameSize:
                    defaultFieldName = outputFName # keep track of the originally generated field name
                    
                    prefixLen = len(fldParams[0])
                    suffixLen = len(fldParams[1])
                    maxBaseSize = maxFieldNameSize - prefixLen - suffixLen
                    
                    # truncate field name to maximum allowable size    
                    outputFName = fldParams[0] + mClassName[:maxBaseSize] + fldParams[1]
                    
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
        newTable = ATtILA2.utils.table.CreateMetricOutputTable(outTable,inReportingUnitFeature,reportingUnitIdField,
                                                               metricsClassNameList,metricsFieldnameDict,fldParams,
                                                               qaCheckFlds, addAreaFldParams)
        
        
        
        
        # Process: Tabulate Area
        # store the area of each input reporting unit into dictionary (zoneID:area)
        zoneAreaDict = arcpyutil.polygons.getAreasByIdDict(inReportingUnitFeature, reportingUnitIdField)
        # create name for a temporary table for the tabulate area geoprocess step - defaults to current workspace 
        scratch_Table = arcpy.CreateScratchName("xtmp", "", "Dataset")
        # run the tabulatearea geoprocess
        arcpy.gp.TabulateArea_sa(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, "Value", scratch_Table, 
                                 processingCellSize)  

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
            valFieldsResults = ATtILA2.utils.field.ProcessTabAreaValueFields(TabAreaValueFields, TabAreaValues, 
                                                                             tabAreaDict, tabAreaTableRow, excludedValues)
            tabAreaDict = valFieldsResults[0]
            effectiveAreaSum = valFieldsResults[1]
            excludedAreaSum = valFieldsResults[2]
            
            # sum the areas for the selected metric's grid codes   
            for mClassName in metricsClassNameList: 
                # get the grid codes for this specified metric
                metricGridCodesList = lccClassesDict[mClassName].uniqueValueIds
                
                # get the class percentage area and it's actual area from the tabulate area table
                metricPercentageAndArea = ATtILA2.utils.calculate.getMetricPercentAreaAndSum(metricGridCodesList, 
                                                                                             tabAreaDict, effectiveAreaSum)
                
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
        

def landCoverCoefficientCalculator(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccObj, 
                         metricsClassNameList, outTable, processingCellSize, optionalGroupsList, metricConst):
    """ Creates *outTable* populated with land cover coefficient metrics
    
    **Description:**

        Creates *outTable* populated with land cover coefficient metrics...
        
    **Arguments:**

        * *inReportingUnitFeature* - Input reporting units
        * *reportingUnitIdField* - name of unique id field in reporting units
        * *inLandCoverGrid* - land cover raster
        * *lccObj* - land cover classification(lcc) object
        * *metricsToRun* - list of class ids to include in processing
        * *outTable* - full path to an output table to be created/populated
        * *processingCellSize* - processing cell size
        * *optionalFieldGroups* - optional fields to create
        * *metricConst* - an object with constants specific to the metric being run (lcp vs lcosp)
        
    **Returns:**

        * None
        
    """
    
    try:
        # Used for intellisense.  Will also raise error if metricConst is not the right type of object        
        assert isinstance(metricConst, metricConstants.baseMetricConstants) 

        # Set parameters for metric output field. 
        # Parameters = [Fieldname_prefix, Fieldname_suffix, Field_type, Field_Precision, Field_scale]
        # e.g., fldParams = ["p", "", "FLOAT", 6, 1]
        metricFieldParams = metricConst.fieldParameters
        
        if globalConstants.qaCheckName in optionalGroupsList:
            # Parameratize optional fields, e.g., optionalFlds = [["LC_Overlap","FLOAT",6,1]]
            qaCheckFieldsParams = metricConst.qaCheckFieldParameters
        else:
            qaCheckFieldsParams = None
        
        maxFieldNameSize = arcpyutil.fields.getFieldNameSizeLimit(outTable)            
        if globalConstants.metricAddName in optionalGroupsList:
            addAreaFldParams = globalConstants.areaFieldParameters
            maxFieldNameSize = maxFieldNameSize - len(addAreaFldParams[0])
        else:
            addAreaFldParams = None
        
        # Process: inputs
    
        # use the metricsClassNameList to create a dictionary of ClassName keys with field name values using any user supplied field names
        metricsFieldnameDict = {}
        outputFieldNames = set() # use this set to help make field names unique
        
        for mClassName in metricsClassNameList:
            # generate unique number to replace characters at end of truncated field names
            n = 1
            
            fieldOverrideName = lccObj.coefficients[mClassName].fieldName

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

                    
        # create the specified output table
        newTable = ATtILA2.utils.table.CreateMetricOutputTable(outTable, inReportingUnitFeature, reportingUnitIdField, 
                                                               metricsClassNameList, metricsFieldnameDict,
                                                               metricFieldParams, qaCheckFieldsParams, addAreaFldParams)

    finally:
        pass
    
    
