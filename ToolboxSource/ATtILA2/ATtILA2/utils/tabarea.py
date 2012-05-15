import ATtILA2
from ATtILA2.constants import globalConstants
import arcpy
from pylet import lcc

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
        

def getMetricCoefficientProduct(tabAreaValueFields, tabAreaValues, metricName, lccObj, tabAreaTableRow):
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
    metricCoefficientSum = 0
    metricAreaSum = 0
    assert isinstance(lccObj, lcc.LandCoverClassification)
    
    valuesDict = lccObj.values
                        
    for i, aFld in enumerate(tabAreaValueFields):
        aValueID = tabAreaValues[i]
        aValArea = tabAreaTableRow.getValue(aFld.name)
        #sum all area for all values to report out on overlap of reporting unit thems and land cover grid
        metricAreaSum = metricAreaSum + aValArea
        #for nitrogen and phosphorus area needs to be converted to hectares


        lccValue = valuesDict[aValueID]
        assert isinstance(lccValue, lcc.LandCoverValue)
        aValCoef = lccValue.getCoefficientValueById(metricName)
        
        
        
        
        

        metricAreaSum += tabAreaDict.get(aValueID, 0) #add 0 if the lcc defined value is not found in the grid
    
    return (metricCoefficientSum, metricAreaSum)

#    excludedAreaSum = 0  #area of reporting unit not used in metric calculations e.g., water area
#    effectiveAreaSum = 0  #effective area of the reporting unit e.g., land area
#
#    for i, aFld in enumerate(TabAreaValueFields):
#        # store the grid code and it's area value into the dictionary
#        valKey = TabAreaValues[i]
#        valArea = tabAreaTableRow.getValue(aFld.name)
#        tabAreaDict[valKey] = valArea
#
#        #add the area of each grid value to the appropriate area sum i.e., effective or excluded area
#        if valKey in excludedValues:
#            excludedAreaSum += valArea
#        else:
#            effectiveAreaSum += valArea               
#                       
#    return (tabAreaDict, effectiveAreaSum, excludedAreaSum)
        
        
def processTabAreaTableByValue(scratchTable, lccObj, newTable, zoneAreaDict, reportingUnitIdField, metricsNameList,
                               lccClassesDict, metricsFieldnameDict, optionalGroupsList, qaCheckFlds):    
    """ """
    
    try:                
        # Process output table from tabulatearea geoprocess
        # get the VALUE fields from Tabulate Area table
        tabAreaValueFields = arcpy.ListFields(scratchTable)[2:]
        # get the grid code values from the field names; put in a list of integers
        tabAreaValues = [int(aFld.name.replace("VALUE_","")) for aFld in tabAreaValueFields]
              
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
             
            # sum the areas for the selected metric's grid codes   
            for metricName in metricsNameList: 
                # get the sum of the coefficient products from the tabulate area table
                metricCoefficientSum = getMetricCoefficientProduct(tabAreaValueFields, tabAreaValues, metricName, lccObj, 
                                                                   tabAreaTableRow)
                
                # add the calculation to the output row
                outTableRow.setValue(metricsFieldnameDict[metricName], metricCoefficientSum)
        
            # add QACheck calculations/values to row
            if globalConstants.qaCheckName in optionalGroupsList:
                zoneArea = zoneAreaDict[zoneIDvalue]
                overlapCalc = ((effectiveAreaSum+excludedAreaSum)/zoneArea) * 100
                outTableRow.setValue(qaCheckFlds[0][0], overlapCalc)
                outTableRow.setValue(qaCheckFlds[1][0], effectiveAreaSum+excludedAreaSum)
            
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