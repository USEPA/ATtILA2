import ATtILA2
from ATtILA2.constants import globalConstants
import arcpy

def runTabAreaGeoProcess(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid):
    """ """
    
    # create name for a temporary table for the tabulate area geoprocess step - defaults to current workspace 
    scratchTable = arcpy.CreateScratchName("xtmp", "", "Dataset")
    # run the tabulatearea geoprocess
    arcpy.gp.TabulateArea_sa(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, "Value", scratchTable)
    
    return scratchTable    

def processTabAreaTableByClass(scratchTable, lccObj, newTable, zoneAreaDict, reportingUnitIdField, metricsClassNameList,
                               lccClassesDict, metricsFieldnameDict, optionalGroupsList, qaCheckFlds):    
    """ """
    
    try:                
        # Process output table from tabulatearea geoprocess
        # get the VALUE fields from Tabulate Area table
        TabAreaValueFields = arcpy.ListFields(scratchTable)[2:]
        # get the grid code values from the field names; put in a list of integers
        TabAreaValues = [int(aFld.name.replace("VALUE_","")) for aFld in TabAreaValueFields]
        # create dictionary to later hold the area value of each grid code in the reporting unit
        tabAreaDict = dict(zip(TabAreaValues,[])) 
        
        # alert user if input grid had values not defined in LCC file
        undefinedValues = [aVal for aVal in TabAreaValues if aVal not in lccObj.getUniqueValueIdsWithExcludes()]     
        if undefinedValues:
            arcpy.AddWarning("Following Grid Values undefined in LCC file: "+str(undefinedValues)+"  - By default, the area for undefined grid codes is included when determining the effective reporting unit area.")
        
        # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area calculation
        lccValuesDict = lccObj.values
        # get the frozenset of excluded values (i.e., values not to use when calculating the reporting unit effective area)
        excludedValues = lccValuesDict.getExcludedValueIds()
        
        # create the cursor to add data to the output table
        outTableRows = arcpy.InsertCursor(newTable)
        # create cursor to search/query the TabAreaOut table
        tabAreaTableRows = arcpy.SearchCursor(scratchTable)
        
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
                
                if globalConstants.metricAddName in optionalGroupsList:
                    outTableRow.setValue(metricsFieldnameDict[mClassName]+globalConstants.areaFieldParameters[0], 
                                         metricPercentageAndArea[1])
        
            # add QACheck calculations/values to row
            if globalConstants.qaCheckName in optionalGroupsList:
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
        arcpy.Delete_management(scratchTable)
        
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