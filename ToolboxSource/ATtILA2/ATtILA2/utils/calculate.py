""" Utilitites specific to area

"""
from ATtILA2.constants import globalConstants
import ATtILA2
from ATtILA2.utils.tabarea import TabulateAreaTable
from pylet import arcpyutil
import arcpy


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
                         metricsBaseNameList, outTable, optionalGroupsList, metricConst, outIdField):
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
        * *optionalFieldGroups* - optional fields to create
        * *metricConst* - an object with constants specific to the metric being run (lcp vs lcosp)
        * *outIdField* - a copy of the reportingUnitIdField except where the IdField type = OID
        
    **Returns:**

        * None
        
    """
    
    try:      
        # get the field name override key
        fieldOverrideKey = metricConst.fieldOverrideKey

        # Set parameters for metric output field. 
        metricFieldParams = metricConst.fieldParameters
        
        # Parameratize optional fields, e.g., optionalFlds = [["LC_Overlap","FLOAT",6,1]]
        if globalConstants.qaCheckName in optionalGroupsList:
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
        
        # use the metricsBaseNameList to create a dictionary of BaseName keys with field name values using any user supplied field names
        metricsFieldnameDict = {}
        outputFieldNames = set() # use this set to help make field names unique
        
        for mBaseName in metricsBaseNameList:
            # generate unique number to replace characters at end of truncated field names
            n = 1
            
            fieldOverrideName = lccClassesDict[mBaseName].attributes.get(fieldOverrideKey,None)
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
                    
                    arcpy.AddWarning(globalConstants.metricNameTooLong.format(defaultFieldName, fieldOverrideName))
                    
                # keep track of output field names    
                outputFieldNames.add(fieldOverrideName)
                # add output field name to dictionary
                metricsFieldnameDict[mBaseName] = fieldOverrideName
            else:
                # generate output field name
                outputFName = metricFieldParams[0] + mBaseName + metricFieldParams[1]
                
                # see if the provided field name is too long for the output table type
                if len(outputFName) > maxFieldNameSize:
                    defaultFieldName = outputFName # keep track of the originally generated field name
                    
                    prefixLen = len(metricFieldParams[0])
                    suffixLen = len(metricFieldParams[1])
                    maxBaseSize = maxFieldNameSize - prefixLen - suffixLen
                    
                    # truncate field name to maximum allowable size    
                    outputFName = metricFieldParams[0] + mBaseName[:maxBaseSize] + metricFieldParams[1]
                    
                    # see if truncated field name is already used.
                    # if so, truncate further and add a unique number to the end of the name
                    while outputFName in outputFieldNames:
                        # shorten the field name and increment it
                        truncateTo = maxBaseSize - len(str(n))
                        outputFName = metricFieldParams[0]+mBaseName[:truncateTo]+str(n)+metricFieldParams[1]
                        n = n + 1
                        
                    arcpy.AddWarning(globalConstants.metricNameTooLong.format(defaultFieldName, outputFName))
                    
                # keep track of output field names
                outputFieldNames.add(outputFName)
                # add output field name to dictionary
                metricsFieldnameDict[mBaseName] = outputFName
                    
        # create the specified output table
        newTable = ATtILA2.utils.table.CreateMetricOutputTable(outTable,outIdField,metricsBaseNameList,metricsFieldnameDict, 
                                                               metricFieldParams, qaCheckFlds, addAreaFldParams)
        
        # store the area of each input reporting unit into dictionary (zoneID:area). used in grid overlap calculations.
        zoneAreaDict = arcpyutil.polygons.getAreasByIdDict(inReportingUnitFeature, reportingUnitIdField)     
        
        ### Tabulate Area Object ###
        
        # name the table if the user has checked the Intermediates option. If table is not named, it will not be saved.
        if globalConstants.intermediateName in optionalGroupsList:
            tableName = metricConst.shortName + globalConstants.tabulateAreaTableAbbv
        else:
            tableName = None
        tabAreaTable = TabulateAreaTable(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, tableName, 
                                         lccObj)
        
        # create the cursor to add data to the output table
        outTableRows = arcpy.InsertCursor(newTable)        
        
        for tabAreaTableRow in tabAreaTable:
            
            # initiate a row to add to the metric output table
            outTableRow = outTableRows.newRow()
            
            # set the reporting unit id value in the output row
            outTableRow.setValue(outIdField.name, tabAreaTableRow.zoneIdValue)
            
            # sum the areas for the selected metric's grid codes   
            for mBaseName in metricsBaseNameList: 
                # get the grid codes for this specified metric
                metricGridCodesList = lccClassesDict[mBaseName].uniqueValueIds
                # get the class percentage area and it's actual area from the tabulate area table
                metricPercentageAndArea = getMetricPercentAreaAndSum(metricGridCodesList, tabAreaTableRow.tabAreaDict, 
                                                                     tabAreaTableRow.effectiveArea)
                # add the calculation to the output row
                outTableRow.setValue(metricsFieldnameDict[mBaseName], metricPercentageAndArea[0])
                
                if addAreaFldParams:
                    outTableRow.setValue(metricsFieldnameDict[mBaseName]+"_A", metricPercentageAndArea[1])

            # add QACheck calculations/values to row
            if qaCheckFlds:
                zoneArea = zoneAreaDict[tabAreaTableRow.zoneIdValue]
                overlapCalc = ((tabAreaTableRow.totalArea)/zoneArea) * 100
                outTableRow.setValue(qaCheckFlds[0][0], overlapCalc)
                outTableRow.setValue(qaCheckFlds[1][0], tabAreaTableRow.totalArea)
                outTableRow.setValue(qaCheckFlds[2][0], tabAreaTableRow.effectiveArea)
                outTableRow.setValue(qaCheckFlds[3][0], tabAreaTableRow.excludedArea)
            
            # commit the row to the output table
            outTableRows.insertRow(outTableRow)
                
    finally:
        
        # delete cursor and row objects to remove locks on the data
        try:
            del outTableRows
            del outTableRow
            del tabAreaTable
            del tabAreaTableRow
        except:
            pass
        
        

def getCoefficientCalculation(tabAreaDict, lccValuesDict, coeffId, metricConst):
    """  Returns the estimated amount of substance per HECTARE based on supplied coefficient values
    
    **Description:**

        For each grid value in a reporting unit, the area for that value is retrieved and converted to hectares. That
        value is then multiplied by the coefficient stored in the LCC file to estimate the amount of the selected 
        substance found in the reporting unit based on that land cover type. The estimated amount is then summed
        across all land cover types and divided by the total area of the reporting unit, again in hectares. The 
        estimated amount of substance per hectare is then returned.
        
    **Arguments:**
                             
        * *tabAreaDict* - dictionary with the area value of each grid code in a reporting unit keyed to the grid code
        * *lccValuesDict* - dictionary with all the individual VALUES and their attributes supplied in the LCC file
        * *coeffId* - string containing the coefficient Id in LCC file (e.g., "NITROGEN", "PHOSPHORUS")
        * *metricConst* - class of metric constants. Contains tuple of per-unit-area coefficient metrics
        
    **Returns:**

        * float - the calculated metric based on coefficient values and metric type (per unit area or proportion)
        
    """

    coefficientTotalInPolygon = 0
    totalAreaInPolygon = 0 
                        
    for aVal in tabAreaDict:
        valueBaseArea = tabAreaDict[aVal]
        
        # change following line to a conversion function after determining the output linear units from the spatial reference
        valueConvertedArea = valueBaseArea/10000.0
        totalAreaInPolygon += valueConvertedArea
        
        if aVal in lccValuesDict:
            valCoefficient = lccValuesDict[aVal].getCoefficientValueById(coeffId)
            weightedValue = valueConvertedArea * valCoefficient
            coefficientTotalInPolygon += weightedValue
            
        if coeffId in metricConst.perUnitAreaMetrics:
            coefficientCalculation = coefficientTotalInPolygon / totalAreaInPolygon
        else:
            coefficientCalculation = (coefficientTotalInPolygon / totalAreaInPolygon) * 100  
    
    return coefficientCalculation



def landCoverCoefficientCalculator(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, lccObj, 
                         metricsBaseNameList, outTable, optionalGroupsList, metricConst, outIdField):
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
        * *optionalFieldGroups* - optional fields to create
        * *metricConst* - an object with constants specific to the metric being run (lcp vs lcosp)
        * *outIdField* - a copy of the reportingUnitIdField except where the IdField type = OID
        
    **Returns:**

        * None
        
    """
    
    try:
        
        maxFieldNameSize = arcpyutil.fields.getFieldNameSizeLimit(outTable)            
            
        # use the metricsBaseNameList to create a dictionary of ClassName keys with field name values using any user supplied field names
        metricsFieldnameDict = {}
        outputFieldNames = set() # use this set to help make field names unique
        
        # get parameters for metric output field: [Fieldname_prefix, Fieldname_suffix, Field_type, Field_Precision, Field_scale]
        metricFieldParams = metricConst.fieldParameters
        
        for mBaseName in metricsBaseNameList:
            # generate unique number to replace characters at end of truncated field names
            n = 1
            
            fieldOverrideName = lccObj.coefficients[mBaseName].fieldName

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
            metricsFieldnameDict[mBaseName] = fieldOverrideName

        # set up field parameters for any optional output fields
        if globalConstants.qaCheckName in optionalGroupsList:
            # Parameratize optional fields, e.g., optionalFlds = [["LC_Overlap","FLOAT",6,1]]
            qaCheckFields = metricConst.qaCheckFieldParameters
        else:
            qaCheckFields = None
                  
        # create the specified output table
        newTable = ATtILA2.utils.table.CreateMetricOutputTable(outTable,outIdField,metricsBaseNameList,metricsFieldnameDict, 
                                                               metricFieldParams, qaCheckFields)

    
        
        ### Tabulate Area Object ###
        
        # store the area of each input reporting unit into dictionary (zoneID:area). used in grid overlap calculations.
        zoneAreaDict = arcpyutil.polygons.getAreasByIdDict(inReportingUnitFeature, reportingUnitIdField)
        
        # name the table if the user has checked the Intermediates option. If table is not named, it will not be saved.
        if globalConstants.intermediateName in optionalGroupsList:
            tableName = metricConst.shortName + globalConstants.tabulateAreaTableAbbv
        else:
            tableName = None
            
        tabAreaTable = TabulateAreaTable(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, tableName, 
                                         lccObj)
        
        # from the lcc file object, get the dictionary with the VALUES attributes
        lccValuesDict = lccObj.values
      
        # create the cursor to add data to the output table
        outTableRows = arcpy.InsertCursor(newTable)        
        
        for tabAreaTableRow in tabAreaTable:
            
            # initiate a row to add to the metric output table
            outTableRow = outTableRows.newRow()
            # set the reporting unit id value in the output row
            outTableRow.setValue(outIdField.name, tabAreaTableRow.zoneIdValue)
            
            # compute the amount of metric item (e.g., NITROGEN) per unit area using the supplied coefficients   
            for mBaseName in metricsBaseNameList:
                # get coefficient per unit area from the tabulate area table
                coefficientCalculation = getCoefficientCalculation(tabAreaTableRow.tabAreaDict, lccValuesDict, mBaseName, metricConst)
                # add the calculation to the output row
                outTableRow.setValue(metricsFieldnameDict[mBaseName], coefficientCalculation)
                
            # add QACheck calculations/values to row
            if qaCheckFields:
                zoneArea = zoneAreaDict[tabAreaTableRow.zoneIdValue]
                overlapCalc = ((tabAreaTableRow.totalArea)/zoneArea) * 100
                outTableRow.setValue(qaCheckFields[0][0], overlapCalc)
            
            # commit the row to the output table
            outTableRows.insertRow(outTableRow)
                
    finally:
        
        # delete cursor and row objects to remove locks on the data
        try:
            del outTableRows
            del outTableRow
            del tabAreaTable
            del tabAreaTableRow
        except:
            pass
    
    
