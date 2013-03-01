""" Utilities specific to area

"""
from ATtILA2.constants import globalConstants

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



def landCoverProportions(lccClassesDict, metricsBaseNameList, optionalGroupsList, metricConst, outIdField, newTable, 
                         tabAreaTable, metricsFieldnameDict, zoneAreaDict):
    """ Creates *outTable* populated with land cover proportions metrics
    
    **Description:**

        Creates *outTable* populated with land cover proportions metrics...
        
    **Arguments:**

        * *lccClassesDict* - dictionary of metric class values 
                        (e.g., classValuesDict['for'].uniqueValueIds = (41, 42, 43))
        * *metricsBaseNameList* - a list of metric BaseNames parsed from the 'Metrics to run' input 
                        (e.g., [for, agt, shrb, devt] or [NITROGEN, IMPERVIOUS])
        * *optionalGroupsList* - list of the selected options parsed from the 'Select options' input
                        (e.g., ["QAFIELDS", "AREAFIELDS", "INTERMEDIATES"])
        * *metricConst* - an object with constants specific to the metric being run (lcp vs lcosp)
        * *outIdField* - a copy of the reportingUnitIdField except where the IdField type = OID
        * *newTable* - the ATtILA created output table 
        * *tabAreaTable* - tabulateArea request output from ArcGIS
        * *metricsFieldnameDict* - a dictionary keyed to the lcc class with the ATtILA generated fieldname as value
        * *zoneAreaDict* -  dictionary with the area of each input polygon keyed to the polygon's ID value. 
                        Used in grid overlap calculations.
        
    **Returns:**

        * None
        
    """
    
    try:      
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
                
                if globalConstants.metricAddName in optionalGroupsList:
                    areaSuffix = globalConstants.areaFieldParameters[0]
                    outTableRow.setValue(metricsFieldnameDict[mBaseName]+areaSuffix, metricPercentageAndArea[1])

            # add QACheck calculations/values to row
            if zoneAreaDict:
                zoneArea = zoneAreaDict[tabAreaTableRow.zoneIdValue]
                overlapCalc = ((tabAreaTableRow.totalArea)/zoneArea) * 100
                
                qaCheckFlds = metricConst.qaCheckFieldParameters
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
        
        

def getCoefficientPerUnitArea(tabAreaDict, lccValuesDict, coeffId, conversionFactor):
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
        * *conversionFactor* - float value for the conversion of area values to number of hectares
        
    **Returns:**

        * float - the calculated metric based on coefficient values and metric type (per unit area)
        
    """

    coefficientTotalInPolygon = 0
    totalHectaresInPolygon = 0 
                        
    for aVal in tabAreaDict:
        valueAreaFromOutput = tabAreaDict[aVal]
        valueSqMeters = valueAreaFromOutput * conversionFactor
        valueHectares = valueSqMeters/10000.0
        totalHectaresInPolygon += valueHectares
        
        # check to see if the grid value is defined in the LCC file. Undefined values are not added to the dividend
        if aVal in lccValuesDict:
            valCoefficient = lccValuesDict[aVal].getCoefficientValueById(coeffId)
            weightedValue = valueHectares * valCoefficient
            coefficientTotalInPolygon += weightedValue
        
        if coefficientTotalInPolygon > 0:    
            coefficientCalculation = coefficientTotalInPolygon / totalHectaresInPolygon
        else:
            coefficientCalculation = 0
    
    return coefficientCalculation


def getCoefficientPercentage(tabAreaDict, lccValuesDict, coeffId):
    """  Multiplies the tabulated area of each grid value by it's coefficient and sums the weighted area across all values
    
    **Description:**

        For each grid value in a reporting unit, the area for that value is retrieved and multiplied by the coefficient 
        stored in the LCC file to estimate the amount of the selected substance found in the reporting unit based on 
        that land cover type. The estimated amount is then summed across all land cover types and multiplied by 100. The 
        computed value is then returned.
        
    **Arguments:**
                             
        * *tabAreaDict* - dictionary with the area value of each grid code in a reporting unit keyed to the grid code
        * *lccValuesDict* - dictionary with all the individual VALUES and their attributes supplied in the LCC file
        * *coeffId* - string containing the coefficient Id in LCC file (e.g., "NITROGEN", "PHOSPHORUS")
        
    **Returns:**

        * float - the calculated metric based on coefficient values and metric type (per unit area or proportion)
        
    """

    coefficientTotalInPolygon = 0
    totalAreaInPolygon = 0
                        
    for aVal in tabAreaDict:
        valueAreaFromOutput = tabAreaDict[aVal]
        totalAreaInPolygon =+ valueAreaFromOutput
        
        # check to see if the grid value is defined in the LCC file. Undefined values are not added to the dividend
        if aVal in lccValuesDict:
            valCoefficient = lccValuesDict[aVal].getCoefficientValueById(coeffId)
            weightedValue = valueAreaFromOutput * valCoefficient
            coefficientTotalInPolygon += weightedValue
            
        if coefficientTotalInPolygon > 0:
            coefficientCalculation = (coefficientTotalInPolygon / totalAreaInPolygon) * 100
        else:
            coefficientCalculation = 0
  
    return coefficientCalculation



def landCoverCoefficientCalculator(lccValuesDict, metricsBaseNameList, optionalGroupsList, metricConst, outIdField, 
                                   newTable, tabAreaTable, metricsFieldnameDict, zoneAreaDict, conversionFactor):
    """ Creates *outTable* populated with land cover coefficient metrics
    
    **Description:**

        Creates *outTable* populated with land cover coefficient metrics...
        
    **Arguments:**

        * *lccValuesDict* - dictionary with all the individual VALUES and their attributes supplied in the LCC file 
                        (e.g., lccValuesDict['21'].name = "Developed, Open Space";
                               lccValuesDict['21'].getCoefficientValueById("NITROGEN") = 9.25)
        * *metricsBaseNameList* - a list of metric BaseNames parsed from the 'Metrics to run' input 
                        (e.g., [for, agt, shrb, devt] or [NITROGEN, IMPERVIOUS])
        * *optionalGroupsList* - list of the selected options parsed from the 'Select options' input
                        (e.g., ["QAFIELDS", "AREAFIELDS", "INTERMEDIATES"])
        * *metricConst* - an object with constants specific to the metric being run (lcp or lcosp, etc.)
        * *outIdField* - a copy of the reportingUnitIdField except where the IdField type = OID
        * *newTable* - the ATtILA created output table 
        * *metricsFieldnameDict* - a dictionary keyed to the lcc class with the ATtILA generated fieldname as value
        * *zoneAreaDict* -  dictionary with the area of each input polygon keyed to the polygon's ID value. 
                        Used in grid overlap calculations.
        * *conversionFactor* - conversion factor to convert area measures to square meters. It is a float value
        
    **Returns:**

        * None
        
    """
    
    try:
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
                if mBaseName in metricConst.perUnitAreaMetrics:
                    coefficientCalculation = getCoefficientPerUnitArea(tabAreaTableRow.tabAreaDict, lccValuesDict, 
                                                                       mBaseName, conversionFactor)
                elif mBaseName in metricConst.percentageMetrics:
                    coefficientCalculation = getCoefficientPercentage(tabAreaTableRow.tabAreaDict, lccValuesDict,
                                                                      mBaseName)
                else:
                    arcpy.AddWarning("Procedure for %s undefined. Tell the programmer to add it to metricConstants.py" % 
                                     mBaseName)
                    
                # add the calculation to the output row
                outTableRow.setValue(metricsFieldnameDict[mBaseName], coefficientCalculation)
                
            # add QACheck calculations/values to row
            if globalConstants.qaCheckName in optionalGroupsList:
                zoneArea = zoneAreaDict[tabAreaTableRow.zoneIdValue]
                overlapCalc = ((tabAreaTableRow.totalArea)/zoneArea) * 100
                
                qaCheckFields = metricConst.qaCheckFieldParameters
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


def lineDensityCalculator(inLines,inAreas,areaUID,unitArea,outLines,densityField,lineClass="",iaField=""):
    """ Creates *outLines* that contains one multipart linear feature for each *inArea* for calculating line density
        in kilometers per square kilometer of area.
    
    **Description:**

        Creates *outLines* that contains one multipart linear feature for each *inArea* for calculating line density
        in kilometers per square kilometer of area.  If a line class is specified, then outLines will actually contain
        one feature per class per input Area, and the linear density is also broken out by class.  If a field for 
        calculating total impervious area is given, the function will add and populate that field with a linear
        regression equation.
        
    **Arguments:**

        * *inLines* - input linear feature class with full path
        * *inAreas* - input areal unit feature class with full path
        * *areaUID* - ID field for the areal units feature class.
        * *unitArea* - field in the areal units feature class containing area in square kilometers.
        * *outLines* - desired output linear features with full path
        * *densityField* - desired fieldname for output density field
        * *lineClass* - optional field in the input linear feature class containing classes of linear features.  
        * *iaField* - if total impervious area should be calculated for these lines, the desired output fieldname
        
    **Returns:**

        * None
        
    """
    
    import vector
    
    # First perform the split/dissolve/merge on the roads
    outLines, lineLengthFieldName = vector.splitDissolveMerge(inLines,inAreas,areaUID,outLines,lineClass)

    # Next join the reporting units layer to the merged roads layer
    arcpy.JoinField_management(outLines, areaUID.name, inAreas, areaUID.name, [unitArea])
    # Set up a calculation expression for density.
    calcExpression = "!" + lineLengthFieldName + "!/!" + unitArea + "!"
    densityField = vector.addCalculateField(outLines,densityField,calcExpression)

    if iaField: # if a field has been specified for calculating total impervious area.
        # Calculate the road density linear regression for total impervious area:
        calcExpression = "pctiaCalc(!" + densityField + "!)"
        codeblock = """def pctiaCalc(RdDensity):
        pctia = ((RdDensity - 1.78) / 0.16)
        if (RdDensity < 1.79):
            return 0
        elif (RdDensity > 11):
            return -1
        else:
            return pctia"""
        iaField = vector.addCalculateField(outLines,iaField,calcExpression,codeblock)
    
    return outLines, lineLengthFieldName

def createValueDict(alist):
    valuedict={}
    for a in alist:
        valuedict[(int(a.split(":")[0]))] = float(a.split(":")[1])
    return valuedict

ResultsDict = {}
def createTotalTable(tabAreaTable, zoneAreaDict):
    TotalAreaDict = {}
    CopyDict = {}
    OverlapDict = {}
    for tabAreaTableRow in tabAreaTable:
        alist = []
        TotalArea = 0
        #Calculate Total Area Dictionary
        for k in tabAreaTableRow.tabAreaDict.keys():
            TotalArea = TotalArea + tabAreaTableRow.tabAreaDict[k]
            alist.append(str(k) + ":" + str(tabAreaTableRow.tabAreaDict[k]))

        TotalAreaDict[tabAreaTableRow.zoneIdValue] = TotalArea
        CopyDict[tabAreaTableRow.zoneIdValue]= alist
        # if QAField option is selected calculate overlap
        if zoneAreaDict:
            zoneArea = zoneAreaDict[tabAreaTableRow.zoneIdValue]
            overlapCalc = (zoneArea/TotalArea) * 100
            OverlapDict[tabAreaTableRow.zoneIdValue] = overlapCalc
    #Calculate proportional dictionary
    createProportionsDict(CopyDict,TotalAreaDict)

    return ResultsDict, OverlapDict


#Calculate Proportions
def createProportionsDict(CopyDict, TotalAreaDict):
    import math
    ProportionsDict = {}

    for k in CopyDict.keys():
        indivrowdict = {}
        pSum = 0
        S = 0
        C = 0
        indivrowdict = createValueDict(CopyDict[k])
        for i in indivrowdict.keys():
            if indivrowdict[i] >0:
                #Calculate the percent land use for use in further calculations
                P = indivrowdict[i] / TotalAreaDict[k]
                #Calculate the sum for use in the Shannon-Weiner calculations
                pSum = pSum + (P * math.log(P))
                #Calculate the Simpson Index
                C = C + P * P
                #Calculate the simple diversity
                S = S + 1
                #Population the proportion dictionary
                ProportionsDict[k] =  str(pSum) + "," + str(C) + "," + str(S)

    #Calculate final results to be reported out
    for k in ProportionsDict.keys():
        #Calculate Shannon-Weiner Diversity equation (H)
        H = float(ProportionsDict[k].split(",") [0])* -1

        #Calculate Simple Diversity equation
        S = int(ProportionsDict[k].split(",")[2])
        
        #Calculate Shannon-Weiner Diversity equation (H prime)
        Hprime = H/math.log(S)
        
        #Calculate Simpson Diversity equation
        C = float(ProportionsDict[k].split(",")[1])
        
        #Create Results Dictionary
        ResultsDict[k] = str(H) + "," + str(Hprime) + "," + str(S) + "," + str(C)



    return ResultsDict

        