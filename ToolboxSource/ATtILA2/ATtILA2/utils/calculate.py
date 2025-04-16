""" Utilities specific to area

"""

import arcpy
from ATtILA2.setupAndRestore import _tempEnvironment3
from ATtILA2.constants import globalConstants, errorConstants
from ATtILA2 import errors
from . import messages
from . import files
from . import vector
from .table import transferField
from .messages import AddMsg
from .log import logArcpy
from os.path import basename


def getMetricPercentAreaAndSum(metricGridCodesList, tabAreaDict, effectiveAreaSum, excludedValues):
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

        * *excludedValues* - a set of grid values tagged in the xml lcc file to be excluded from the total area calculations
                            (e.g. water areas when the user is concerned with land area calculations)

    **Returns:**

        * float - the percentage of the reporting unit effective area that is occupied by the metric class codes
        * float - the sum of the area of metric class codes

    """

    metricAreaSum = 0                         
    for aValueID in metricGridCodesList:
        if aValueID not in excludedValues:
            metricAreaSum += tabAreaDict.get(aValueID, 0) #add 0 if the lcc defined value is not found in the grid

    if effectiveAreaSum > 0:
        metricPercentArea = (metricAreaSum / effectiveAreaSum) * 100
    else: # all values found in reporting unit are in the excluded set
        metricPercentArea = 0

    return metricPercentArea, metricAreaSum


def landCoverProportions(lccClassesDict, metricsBaseNameList, optionalGroupsList, metricConst, outIdField, newTable, 
                         tabAreaTable, metricsFieldnameDict, zoneAreaDict, reportingUnitAreaDict, zoneValueDict=False,
                         conversionFactor=None):
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
        * *metricsFieldnameDict* - a dictionary keyed to the lcc class with the ATtILA generated fieldname tuple as value
                        The tuple consists of the output fieldname and the class name as modified
                        (e.g., "forest":("fore0_E2A7","fore0")
        * *zoneAreaDict* -  dictionary with the area of each input polygon keyed to the polygon's ID value. 
                        Used in grid overlap calculations.
                        The 'zone' may be the input reporting unit or a polygon that represents an area within 
                        the reporting unit such as a riparian buffer.
        * *reportingUnitAreaDict* -  dictionary with a two item list keyed to the reporting unit's ID value. The two items are: the input reporting unit's 
                        total area and its effective area.
                        Used in buffer area percentage calculations (e.g. land area in the riparian buffer zones comprise 9.6% of the land 
                        area in the reporting unit). If the reporting unit themes is not replaced in the metric calculations, the reportingUnitAreaDict 
                        values are equal to those in the zoneAreaDict.
        * *zoneValueDict* - dictionary with a value for an input polygon feature keyed to the polygon's ID value.
                        Used in lcc class area per value calculations (e.g. square meters of forest per person).

    **Returns:**

        * None

    """

    try:      
        # create the cursor to add data to the output table
        outTableRows = arcpy.InsertCursor(newTable)

        # find the index positions of any non-standard QA fields. Standard QA fields include: OVER, TOTA, EFFA, EXCA.
        # non-standard QA fields include: rTOTA, rEFFA, sTOTA, sEFFA, fTOTA, fEFFA
        if zoneAreaDict:
            calcBuffPct = False
            qaCheckFlds = metricConst.qaCheckFieldParameters
            for aFldParams in qaCheckFlds:
                fldName = aFldParams[0]
                if metricConst.pctBufferName:
                    if fldName.startswith(metricConst.pctBufferName):
                        buffIndx = qaCheckFlds.index(aFldParams)  
                        calcBuffPct = True

                    if fldName.startswith(metricConst.totaPctName):
                        totaPctIndx = qaCheckFlds.index(aFldParams)


                # use else or elif here, if additional non-standard QA fields are added

        # create two sets to store the reporting unit IDs for troublesome per capita polygons: one for where the population 
        # count in the reporting unit is zero, and one for where the reporting unit does not overlap with the input population dataset. 
        # Sets will not allow duplicate values so their len() count will only include an RU ID once.
        zeroCountWarning = set()
        missingCountWarning = set()

        for tabAreaTableRow in tabAreaTable:
            tabAreaDict = tabAreaTableRow.tabAreaDict
            effectiveArea = tabAreaTableRow.effectiveArea
            excludedValues = tabAreaTableRow._excludedValues

            # initiate a row to add to the metric output table
            outTableRow = outTableRows.newRow()

            # set the reporting unit id value in the output row
            outTableRow.setValue(outIdField.name, tabAreaTableRow.zoneIdValue)

            # sum the areas for the selected metric's grid codes   
            for mBaseName in metricsBaseNameList: 
                # get the grid codes for this specified metric
                metricGridCodesList = lccClassesDict[mBaseName].uniqueValueIds
                # get the class percentage area and it's actual area from the tabulate area table
                metricPercentageAndArea = getMetricPercentAreaAndSum(metricGridCodesList, tabAreaDict, effectiveArea, excludedValues)

                # add the calculation to the output row
                outTableRow.setValue(metricsFieldnameDict[mBaseName][0], metricPercentageAndArea[0])

                if globalConstants.metricAddName in optionalGroupsList:
                    areaSuffix = globalConstants.areaFieldParameters[0]
                    outTableRow.setValue(metricsFieldnameDict[mBaseName][0]+areaSuffix, metricPercentageAndArea[1])

                # add per value (e.g., capita) calculations to row
                if zoneValueDict:
                    classSqM = metricPercentageAndArea[1] * conversionFactor

                    # use a try statement in case the reporting unit does not overlap with the input population dataset
                    try:
                        zoneValue = zoneValueDict[tabAreaTableRow.zoneIdValue]

                        # calculate the per capita value
                        
                        # Need to go zoneValue >= 1 as dividing with values below 1 assigns more land cover to the individual 
                        # than exists in the reporting unit. In addition, if the zoneValue is very, very small (e.g. 0.000009),
                        # the perValueCalc value can be so large that it will not fit in the output field
                        if zoneValue >= 1:
                            perValueCalc = classSqM / zoneValue
                        else:
                            # set a null value for areas with a count value of zero
                            perValueCalc = -99999
                            # keep track of the troublesome zone ID
                            zeroCountWarning.add(tabAreaTableRow.zoneIdValue)

                    except:
                        # set a null value for areas that do not overlap the population dataset
                        perValueCalc = -55555
                        # keep track of the troublesome zone ID
                        missingCountWarning.add(tabAreaTableRow.zoneIdValue)

                    # get the output field name identifiers     
                    perValueSuffix = metricConst.perCapitaSuffix
                    meterSquaredSuffix = metricConst.meterSquaredSuffix

                    # set the output field values
                    outTableRow.setValue(metricsFieldnameDict[mBaseName][1]+perValueSuffix, perValueCalc)
                    outTableRow.setValue(metricsFieldnameDict[mBaseName][1]+meterSquaredSuffix, classSqM)

            # add QACheck calculations/values to row
            if zoneAreaDict:
                zoneArea = zoneAreaDict[tabAreaTableRow.zoneIdValue]
                overlapCalc = ((tabAreaTableRow.totalArea)/zoneArea) * 100

                # process standard QA Fields. Standard QA fields include: OVER, TOTA, EFFA, EXCA.
                outTableRow.setValue(qaCheckFlds[0][0], overlapCalc)
                outTableRow.setValue(qaCheckFlds[1][0], tabAreaTableRow.totalArea)
                outTableRow.setValue(qaCheckFlds[2][0], tabAreaTableRow.effectiveArea)
                outTableRow.setValue(qaCheckFlds[3][0], tabAreaTableRow.excludedArea)

                # process non-standard QA fields (e.g., rTOTA, rEFFA)
                if len(qaCheckFlds) > 4:
                    if calcBuffPct:
                        if reportingUnitAreaDict:
                            ruEffectiveArea = reportingUnitAreaDict[tabAreaTableRow.zoneIdValue][1]
                            ruTotalArea = reportingUnitAreaDict[tabAreaTableRow.zoneIdValue][0]
                        else:
                            ruEffectiveArea = zoneAreaDict[tabAreaTableRow.zoneIdValue]
                            ruTotalArea = ruEffectiveArea

                        # calculate the percentage of effective area in the reporting unit to the effective area of the entire reporting unit
                        buffEffectiveArea = tabAreaTableRow.effectiveArea
                        if ruEffectiveArea > 0:
                            effaPercentCalc = (buffEffectiveArea/ruEffectiveArea) * 100
                        else:
                            effaPercentCalc = 0
                        outTableRow.setValue(qaCheckFlds[buffIndx][0], effaPercentCalc)

                        # calculate the percentage of the reporting unit that is in the buffer area
                        buffTotalArea = tabAreaTableRow.totalArea
                        totaPercentCalc = (buffTotalArea/ruTotalArea) * 100
                        outTableRow.setValue(qaCheckFlds[totaPctIndx][0], totaPercentCalc)

                    # use else or elif here, if additional non-standard QA fields are added

            # commit the row to the output table
            outTableRows.insertRow(outTableRow)

        # report to the user if null values for troublesome reporting units were inserted into the output table 
        if len(zeroCountWarning) > 0:
            arcpy.AddWarning("Zero population was found in %s reporting units. A value of -99999 was assigned to the Per Capita fields for those records." % len(zeroCountWarning))        
        if len(missingCountWarning) > 0:
            arcpy.AddWarning("Population data was missing for %s reporting units. A value of -55555 was assigned to the Per Capita fields for those records." % len(missingCountWarning)) 

    finally:

        # delete cursor and row objects to remove locks on the data
        try:
            del outTableRows
            del outTableRow
            del tabAreaTable
            del tabAreaTableRow
        except:
            pass


# def landCoverProportionsOLD(lccClassesDict, metricsBaseNameList, optionalGroupsList, metricConst, outIdField, newTable, 
#                          tabAreaTable, metricsFieldnameDict, zoneAreaDict):
#     """ Creates *outTable* populated with land cover proportions metrics
#     
#     **Description:**
# 
#         Creates *outTable* populated with land cover proportions metrics...
#         
#     **Arguments:**
# 
#         * *lccClassesDict* - dictionary of metric class values 
#                         (e.g., classValuesDict['for'].uniqueValueIds = (41, 42, 43))
#         * *metricsBaseNameList* - a list of metric BaseNames parsed from the 'Metrics to run' input 
#                         (e.g., [for, agt, shrb, devt] or [NITROGEN, IMPERVIOUS])
#         * *optionalGroupsList* - list of the selected options parsed from the 'Select options' input
#                         (e.g., ["QAFIELDS", "AREAFIELDS", "INTERMEDIATES"])
#         * *metricConst* - an object with constants specific to the metric being run (lcp vs lcosp)
#         * *outIdField* - a copy of the reportingUnitIdField except where the IdField type = OID
#         * *newTable* - the ATtILA created output table 
#         * *tabAreaTable* - tabulateArea request output from ArcGIS
#         * *metricsFieldnameDict* - a dictionary keyed to the lcc class with the ATtILA generated fieldname tuple as value
#                         The tuple consists of the output fieldname and the class name as modified
#                         (e.g., "forest":("fore0_E2A7","fore0")
#         * *zoneAreaDict* -  dictionary with the area of each input polygon keyed to the polygon's ID value. 
#                         Used in grid overlap calculations.
#         
#     **Returns:**
# 
#         * None
#         
#     """
#     
#     try:      
#         # create the cursor to add data to the output table
#         outTableRows = arcpy.InsertCursor(newTable)        
#         
#         for tabAreaTableRow in tabAreaTable:
#             tabAreaDict = tabAreaTableRow.tabAreaDict
#             effectiveArea = tabAreaTableRow.effectiveArea
#             excludedValues = tabAreaTableRow._excludedValues
#             
#             # initiate a row to add to the metric output table
#             outTableRow = outTableRows.newRow()
#             
#             # set the reporting unit id value in the output row
#             outTableRow.setValue(outIdField.name, tabAreaTableRow.zoneIdValue)
#             
#             # sum the areas for the selected metric's grid codes   
#             for mBaseName in metricsBaseNameList: 
#                 # get the grid codes for this specified metric
#                 metricGridCodesList = lccClassesDict[mBaseName].uniqueValueIds
#                 # get the class percentage area and it's actual area from the tabulate area table
#                 metricPercentageAndArea = getMetricPercentAreaAndSum(metricGridCodesList, tabAreaDict, effectiveArea, excludedValues)
#                 
#                 # add the calculation to the output row
#                 outTableRow.setValue(metricsFieldnameDict[mBaseName][0], metricPercentageAndArea[0])
#                 
#                 if globalConstants.metricAddName in optionalGroupsList:
#                     areaSuffix = globalConstants.areaFieldParameters[0]
#                     outTableRow.setValue(metricsFieldnameDict[mBaseName][0]+areaSuffix, metricPercentageAndArea[1])
# 
#             # add QACheck calculations/values to row
#             if zoneAreaDict:
#                 zoneArea = zoneAreaDict[tabAreaTableRow.zoneIdValue]
#                 overlapCalc = ((tabAreaTableRow.totalArea)/zoneArea) * 100
#                 
#                 qaCheckFlds = metricConst.qaCheckFieldParameters
#                 outTableRow.setValue(qaCheckFlds[0][0], overlapCalc)
#                 outTableRow.setValue(qaCheckFlds[1][0], tabAreaTableRow.totalArea)
#                 outTableRow.setValue(qaCheckFlds[2][0], tabAreaTableRow.effectiveArea)
#                 outTableRow.setValue(qaCheckFlds[3][0], tabAreaTableRow.excludedArea)
#             
#             # commit the row to the output table
#             outTableRows.insertRow(outTableRow)
#                 
#     finally:
#         
#         # delete cursor and row objects to remove locks on the data
#         try:
#             del outTableRows
#             del outTableRow
#             del tabAreaTable
#             del tabAreaTableRow
#         except:
#             pass


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

        # check to see if the grid value is defined in the LCC file. Undefined values are not added to the dividend. 
        # i.e., they will be treated as if they had a coefficient value of 0
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
        valueArea = tabAreaDict[aVal]
        totalAreaInPolygon += valueArea

        # check to see if the grid value is defined in the LCC file. Undefined values are not added to the dividend. 
        # i.e., they will be treated as if they had a coefficient value of 0
        if aVal in lccValuesDict:
            valCoefficient = lccValuesDict[aVal].getCoefficientValueById(coeffId)
            weightedValue = valueArea * valCoefficient
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
        * *metricsFieldnameDict* - a dictionary keyed to the lcc class with the ATtILA generated fieldname tuple as value
                        The tuple consists of the output fieldname and the class name as modified
                        (e.g., "forest":("fore0_E2A7","fore0")                        
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
                outTableRow.setValue(metricsFieldnameDict[mBaseName][0], coefficientCalculation)

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


def lineDensityCalculator(inLines,inAreas,areaUID,unitArea,outLines,densityField,inLengthField,lineClass="",iaField="",logFile=None):
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
        * *inLengthField* - desired fieldname for output length field
        * *lineClass* - optional field in the input linear feature class containing classes of linear features.  
        * *iaField* - if total impervious area should be calculated for these lines, the desired output fieldname

    **Returns:**

        * None

    """

    # from . import vector

    # First perform the split/dissolve/merge on the roads
    outLines, lineLengthFieldName = vector.splitDissolveMerge(inLines,inAreas,areaUID,outLines,inLengthField,lineClass,logFile)

    # Next join the reporting units layer to the merged roads layer
    logArcpy("arcpy.JoinField_management",(outLines, areaUID.name, inAreas, areaUID.name, [unitArea]),logFile)
    arcpy.JoinField_management(outLines, areaUID.name, inAreas, areaUID.name, [unitArea])
    # Set up a calculation expression for density.
    calcExpression = f"!{lineLengthFieldName}!/!{unitArea}!"
    densityField = vector.addCalculateField(outLines,densityField,"DOUBLE",calcExpression,'#',logFile)

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
        
        iaField = vector.addCalculateField(outLines,iaField,"DOUBLE",calcExpression,codeblock,logFile)

    return outLines, lineLengthFieldName


def landCoverDiversity(metricConst, outIdField, newTable, tabAreaTable, zoneAreaDict):
    """ Creates *outTable* populated with land cover diversity metrics

    **Description:**

        Creates *outTable* populated with land cover diversity metrics...

    **Arguments:**

        * *metricConst* - an object with constants specific to the metric being run (lcp vs lcosp)
        * *outIdField* - a copy of the reportingUnitIdField except where the IdField type = OID
        * *newTable* - the ATtILA created output table 
        * *tabAreaTable* - tabulateArea request output from ArcGIS
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

            # calculate the diversity indices (H, H_Prime, C, and S) for the current reporting unit  
            h,hp,s,c = getDiversityIndices(tabAreaTableRow.tabAreaDict, tabAreaTableRow.totalArea)

            # populate metric fields
            outTableRow.S = s
            outTableRow.H = h
            outTableRow.H_Prime = hp
            outTableRow.C = c

            # add QACheck calculations/values to row
            if zoneAreaDict:
                zoneArea = zoneAreaDict[tabAreaTableRow.zoneIdValue]
                overlapCalc = ((tabAreaTableRow.totalArea)/zoneArea) * 100

                qaCheckFlds = metricConst.qaCheckFieldParameters
                outTableRow.setValue(qaCheckFlds[0][0], overlapCalc)


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


def getDiversityIndices(tabAreaDict, totalArea):
    import math

    pSum = 0
    S = 0
    C = 0
    Hprime = 0

    for i in tabAreaDict.values():
        if i >0:
            #Calculate the percent land use for use in further calculations
            P = i / totalArea
            #Calculate the sum for use in the Shannon-Weiner calculations
            pSum += (P * math.log(P))
            #Calculate the Simpson Index
            C += P * P
            #Calculate the simple diversity
            S += 1

    #Calculate Shannon-Weiner Diversity equation (H)
    H = pSum * -1

    #Calculate Shannon-Weiner Diversity equation (H prime)
    if S > 1:
        Hprime = H/math.log(S)

    #Create Results tuple to be reported out
    diversityIndices = (H, Hprime, S, C)

    return diversityIndices 


def getCoreEdgeRatio(outIdField, newTable, tabAreaTable, metricsFieldnameDict, zoneAreaDict, metricConst, m):
    """ Creates *outTable* populated with land cover edge to area metrics

    **Description:**

        Populates the *outTable* with the land cover edge to area ratio, the percent area designated Core,
        and the percent area that is designated Edge for each reporting unit for the supplied LCC class. 

    **Arguments:**

        * *outIdField* - a copy of the reportingUnitIdField except where the IdField type = OID
        * *newTable* - the ATtILA created output table 
        * *tabAreaTable* - tabulateArea request output from ArcGIS
        * *metricsFieldnameDict* - a dictionary keyed to the lcc class with the ATtILA generated fieldname tuple as value
                        The tuple consists of the output fieldname and the class name as modified
                        (e.g., "forest":("fore0_E2A7","fore0")
        * *zoneAreaDict* -  dictionary with the area of each input polygon keyed to the polygon's ID value. 
                        Used in grid overlap calculations.
        * *metricConst* - an object with constants specific to the metric being run (lcp vs lcosp)
        * *m* - a metric BaseName parsed from the 'Metrics to run' input 
                        (e.g., [for, agt, shrb, devt] or [NITROGEN, IMPERVIOUS])


    **Returns:**

        * None

    """  
    CoreEdgeDict = {}

    try:    
        # Calculate Core/Edge metrics and place results in dictionary with zoneIdValue as the key
        for tabAreaTableRow in tabAreaTable:
            edgeArea = 0
            if ("EDGE" in tabAreaTableRow.tabAreaDict):
                edgeArea = tabAreaTableRow.tabAreaDict["EDGE"]
            coreArea = 0
            if ("CORE" in tabAreaTableRow.tabAreaDict):
                coreArea = tabAreaTableRow.tabAreaDict["CORE"]
            otherArea = 0
            if ("OTHER" in tabAreaTableRow.tabAreaDict):
                otherArea = tabAreaTableRow.tabAreaDict["OTHER"]
            excludedArea = 0
            if ("EXCLUDED" in tabAreaTableRow.tabAreaDict):
                excludedArea = tabAreaTableRow.tabAreaDict["EXCLUDED"]

            totalArea = edgeArea + coreArea + otherArea + excludedArea
            effectiveArea = totalArea - excludedArea 

            # test to make sure land cover values exist in this zoneId, then gather metrics
            if effectiveArea > 0:
                percentEdge = (edgeArea/effectiveArea)*100
                percentCore = (coreArea/effectiveArea)*100
                if edgeArea or coreArea > 0: # don't want to divide by zero
                    CtoERatio = (edgeArea/(edgeArea + coreArea))*100
                else:
                    arcpy.AddWarning( m + " landuse doesn't exist in reporting unit feature " + str(tabAreaTableRow.zoneIdValue))
                    CtoERatio = 0
            else:
                arcpy.AddWarning("All landuse is tagged as EXCLUDED in reporting unit feature " + str(tabAreaTableRow.zoneIdValue))
                percentEdge = 0
                percentCore = 0
                CtoERatio = 0

            resultsTuple = (CtoERatio, percentCore, percentEdge, totalArea, effectiveArea, excludedArea)
            CoreEdgeDict[tabAreaTableRow.zoneIdValue] = resultsTuple


        # Check to see if newTable has already been set up
        rowcount = int(arcpy.GetCount_management(newTable).getOutput(0))
        if rowcount == 0:
            outTableRows = arcpy.InsertCursor(newTable)
            for k in CoreEdgeDict.keys():
                # initiate a row to add to the metric output table
                outTableRow = outTableRows.newRow()

                # set the reporting unit id value in the output row
                outTableRow.setValue(outIdField.name, k)

                # commit the row to the output table
                outTableRows.insertRow(outTableRow)
            del outTableRows, outTableRow

        # assemble the names for the core and edge fields    
        outClassName = metricsFieldnameDict[m][1]
        coreFieldName = metricConst.coreField[0]+outClassName+metricConst.coreField[1]
        edgeFieldName = metricConst.edgeField[0]+outClassName+metricConst.edgeField[1]

        # create the cursor to add data to the output table
        outTableRows = arcpy.UpdateCursor(newTable)        
        outTableRow = outTableRows.next()
        while outTableRow:
            uid = outTableRow.getValue(outIdField.name)
            # populate the edge to core ratio for the current reporting unit
            if (uid in CoreEdgeDict):
                outTableRow.setValue(metricsFieldnameDict[m][0], CoreEdgeDict[uid][0])
                outTableRow.setValue(coreFieldName, CoreEdgeDict[uid][1])
                outTableRow.setValue(edgeFieldName, CoreEdgeDict[uid][2])
            else:
                outTableRow.setValue(metricsFieldnameDict[m][0], 0)
                outTableRow.setValue(coreFieldName, 0)
                outTableRow.setValue(edgeFieldName, 0)


            # add QACheck calculations/values to row
            if zoneAreaDict:
                zoneArea = zoneAreaDict[uid]
                qaCheckFlds = metricConst.qaCheckFieldParameters

                if (uid in CoreEdgeDict):
                    overlapCalc = ((CoreEdgeDict[uid][3])/zoneArea) * 100
                    outTableRow.setValue(qaCheckFlds[0][0], overlapCalc)
                    outTableRow.setValue(qaCheckFlds[1][0], CoreEdgeDict[uid][3])
                    outTableRow.setValue(qaCheckFlds[2][0], CoreEdgeDict[uid][4])
                    outTableRow.setValue(qaCheckFlds[3][0], CoreEdgeDict[uid][5])
                else:
                    outTableRow.setValue(qaCheckFlds[0][0], 0)
                    outTableRow.setValue(qaCheckFlds[1][0], 0)
                    outTableRow.setValue(qaCheckFlds[2][0], 0)
                    outTableRow.setValue(qaCheckFlds[3][0], 0)                       

            # commit the row to the output table
            outTableRows.updateRow(outTableRow)
            outTableRow = outTableRows.next()
    finally:

        # delete cursor and row objects to remove locks on the data
        try:
            del outTableRows
            del outTableRow
            del tabAreaTable
            del tabAreaTableRow
        except:
            pass


def getMDCP(outIdField, newTable, mdcpDict, optionalGroupsList, outClassName):
    try:
        # Check to see if newTable has already been set up
        rowcount = int(arcpy.GetCount_management(newTable).getOutput(0))
        if rowcount == 0:
            outTableRows = arcpy.InsertCursor(newTable)
            for k in mdcpDict.keys():
                # initiate a row to add to the metric output table
                outTableRow = outTableRows.newRow()

                # set the reporting unit id value in the output row
                outTableRow.setValue(outIdField.name, k)

                # commit the row to the output table
                outTableRows.insertRow(outTableRow)
            del outTableRows, outTableRow
        # If QA fields are selected, add fields for pwn (patches w/ neighbors) and pwon (patches w/o) for the class
        if globalConstants.qaCheckName in optionalGroupsList:
            arcpy.AddField_management(newTable, outClassName+"_PWN", "LONG")
            arcpy.AddField_management(newTable, outClassName+"_PWON", "LONG")

        mdcpFieldName = outClassName+"_MDCP"

        # create the cursor to add data to the output table
        outTableRows = arcpy.UpdateCursor(newTable)        
        outTableRow = outTableRows.next()
        while outTableRow:
            uid = outTableRow.getValue(outIdField.name)
            # populate the mean distance to edge patch for the current reporting unit
            outTableRow.setValue(mdcpFieldName, mdcpDict[uid].split(",")[2])

            # If QA fields are selected, populate the pwon and pwn fields
            if globalConstants.qaCheckName in optionalGroupsList:
                outTableRow.setValue(outClassName+"_PWN", mdcpDict[uid].split(",")[0])
                outTableRow.setValue(outClassName+"_PWON", mdcpDict[uid].split(",")[1])

            # commit the row to the output table
            outTableRows.updateRow(outTableRow)
            outTableRow = outTableRows.next()

    finally:

        # delete cursor and row objects to remove locks on the data
        try:
            del outTableRows
            del outTableRow

        except:
            pass


def getPatchNumbers(outIdField, newTable, reportingUnitIdField, metricsFieldnameDict, zoneAreaDict, metricConst, m, 
                    inReportingUnitFeature, inLandCoverGrid, processingCellSize, conversionFactor):
    import numpy as np
    from arcpy import env
    
    resultsDict={}

    try:
        # create list to identify EXCLUDED and OTHER VALUE fields in the tabulate area table
        ignoreFieldList = ["VALUE__9999", "VALUE_0"]

        # put the proper field delimiters around the ID field name for SQL expressions
        delimitedField = arcpy.AddFieldDelimiters(inReportingUnitFeature, reportingUnitIdField)

        # Initialize custom progress indicator
        totalRUs = len(zoneAreaDict)
        loopProgress = messages.loopProgress(totalRUs)

        #For each Reporting Unit run Tabulate Area Analysis and add the results to a dictionary
        for aZone in zoneAreaDict.keys():
            # set initial metric values
            numPatch = 0
            patchArea = 0
            otherArea = 0
            excludedArea = 0
            lrgPatch = 0
            avePatch = 0
            mdnPatch = 0
            lrgProportion = 0
            patchDensity = 0

            if isinstance(aZone, int): # reporting unit id is an integer - convert to string for SQL expression
                squery = f"{delimitedField} = {aZone}"
            else: # reporting unit id is a string - enclose it in single quotes for SQL expression
                squery = f"{delimitedField} = '{aZone}'"

            #Create a feature layer of the single reporting unit
            if arcpy.Exists("subwatersheds_Layer"):
                # delete the layer in case the geoprocessing overwrite output option is turned off
                arcpy.Delete_management("subwatersheds_Layer")
            arcpy.MakeFeatureLayer_management(inReportingUnitFeature,"subwatersheds_Layer",squery)

            #Set the geoprocessing extent to just the extent of the selected reporting unit
            selectedRUName = f"selectedRU_{aZone}"
            arcpy.CopyFeatures_management("subwatersheds_Layer", selectedRUName)

            #Tabulate areas of patches within single reporting unit
            if arcpy.Exists("temptable"):
                # delete the temp table in case the geoprocessing overwrite output option is turned off
                arcpy.Delete_management("temptable")
            tabareaTable = "temptable"
            
            # if a reporting unit does not overlap with the land cover grid, the tabulate area operation will fail. 
            # use a try...except operation to handle this situation
            try:
                arcpy.sa.TabulateArea(selectedRUName, reportingUnitIdField, inLandCoverGrid,"Value", tabareaTable, processingCellSize)
                rowcount = int(arcpy.GetCount_management(tabareaTable).getOutput(0))
            except:
                # AddMsg(f"No land cover grid data found in {aZone}", 1)
                rowcount = 0
                #resultsDict[aZone] = (mv,mv,mv,mv,mv,mv,mv,mv,mv,zoneAreaDict[aZone])
           
            if rowcount != 0:
                #Loop through each row in the table and calculate the patch metrics 
                rows = arcpy.SearchCursor(tabareaTable)
                row = rows.next()

                while row:
                    flds = arcpy.ListFields(tabareaTable)
                    valueFieldsList = [f.name for f in flds if "VALUE" in f.name]

                    patchAreaList = [row.getValue(fld) for fld in valueFieldsList if fld not in ignoreFieldList]

                    # find the area of the OTHER and EXCLUDED classes if they are found in the reporting unit
                    try:
                        otherArea = row.getValue("VALUE_0")
                    except:
                        otherArea = 0

                    try:
                        excludedArea = row.getValue("VALUE__9999")
                    except:
                        excludedArea = 0

                    if len(patchAreaList) == 0:
                        AddMsg(f"No patches found in {aZone}", 1)

                    else: 
                        numPatch = len(patchAreaList)
                        patchArea = sum(patchAreaList)
                        lrgPatch = max(patchAreaList)
                        mdnPatch = np.median(patchAreaList)
                        avePatch = patchArea/numPatch
                        lrgProportion = (lrgPatch/patchArea) * 100

                        #convert to square kilometers
                        rasterRUArea = otherArea + patchArea
                        rasterRUAreaKM = rasterRUArea* (conversionFactor/1000000)
                        patchDensity = numPatch/rasterRUAreaKM         

                    row = rows.next()

                resultsDict[aZone] = (lrgProportion,numPatch,avePatch,mdnPatch,patchDensity,lrgPatch,patchArea,otherArea,excludedArea,zoneAreaDict[aZone])

            if arcpy.Exists(selectedRUName):
                arcpy.Delete_management(selectedRUName)

            if arcpy.Exists(tabareaTable):
                arcpy.Delete_management(tabareaTable)
                
            if arcpy.Exists("subwatersheds_Layer"):
                arcpy.Delete_management("subwatersheds_Layer")
                
            loopProgress.update()

        # Restore the original environment extent
        env.extent = _tempEnvironment3

        # Check to see if newTable has already been set up
        rowcount = int(arcpy.GetCount_management(newTable).getOutput(0))
        if rowcount == 0:
            outTableRows = arcpy.InsertCursor(newTable)
            for k in resultsDict.keys():
                # initiate a row to add to the metric output table
                outTableRow = outTableRows.newRow()

                # set the reporting unit id value in the output row
                outTableRow.setValue(outIdField.name, k)

                # commit the row to the output table
                outTableRows.insertRow(outTableRow)
            del outTableRows, outTableRow

        # assemble the names for the patch metric fields 
        outClassName = metricsFieldnameDict[m][1]
        numFieldName = metricConst.numField[0]+outClassName+metricConst.numField[1]
        avgFieldName = metricConst.avgField[0]+outClassName+metricConst.avgField[1]
        mdnFieldName = metricConst.mdnField[0]+outClassName+metricConst.mdnField[1]
        densFieldName = metricConst.densField[0]+outClassName+metricConst.densField[1]
        lrgFieldName = metricConst.lrgField[0]+outClassName+metricConst.lrgField[1]

        # check to see if QA fields are included in table
        fldNames = [f.name for f in arcpy.ListFields(newTable)]
        QAFields = metricConst.overlapName in fldNames

        # create the cursor to add data to the output table
        outTableRows = arcpy.UpdateCursor(newTable)        
        outTableRow = outTableRows.next()
        while outTableRow:
            uid = outTableRow.getValue(outIdField.name)
            # populate the patch metric fields for the current reporting unit
            if (uid in resultsDict):
                outTableRow.setValue(metricsFieldnameDict[m][0], resultsDict[uid][0])
                outTableRow.setValue(numFieldName, resultsDict[uid][1])
                outTableRow.setValue(avgFieldName, resultsDict[uid][2])
                outTableRow.setValue(mdnFieldName, resultsDict[uid][3])
                outTableRow.setValue(densFieldName, resultsDict[uid][4])
                outTableRow.setValue(lrgFieldName, resultsDict[uid][5])
                
            else:
                outTableRow.setValue(metricsFieldnameDict[m][0], 0)
                outTableRow.setValue(numFieldName, 0)
                outTableRow.setValue(avgFieldName, 0)
                outTableRow.setValue(mdnFieldName, 0)
                outTableRow.setValue(densFieldName, 0)
                outTableRow.setValue(lrgFieldName, 0)

            # add QACheck calculations/values to row
            if QAFields:

                qaCheckFlds = metricConst.qaCheckFieldParameters
                effectiveArea = resultsDict[uid][6] + resultsDict[uid][7]
                excludedArea = resultsDict[uid][8]
                vectorRUArea = resultsDict[uid][9]
                rasterRUArea = effectiveArea + excludedArea
                overlapCalc = (rasterRUArea/ vectorRUArea) * 100

                outTableRow.setValue(qaCheckFlds[0][0], overlapCalc)
                outTableRow.setValue(qaCheckFlds[1][0], rasterRUArea)
                outTableRow.setValue(qaCheckFlds[2][0], effectiveArea)
                outTableRow.setValue(qaCheckFlds[3][0], excludedArea)

            # commit the row to the output table
            outTableRows.updateRow(outTableRow)
            outTableRow = outTableRows.next()
    finally:

        # delete cursor and row objects to remove locks on the data
        try:
            del rows
            del row
            del outTableRows
            del outTableRow
            if arcpy.Exists(tabareaTable):
                arcpy.Delete_management(tabareaTable)
        except:
            pass

    return resultsDict


def getWeightedPopDensity(inReportingUnitFeature,reportingUnitIdField,ruAreaFld,inCensusFeature,inPopField,outTable,
                          metricConst,cleanupList,index,timer,logFile):
    """ Performs a transfer of population from input census features to input reporting unit features using simple
        areal weighting.  

    **Description:**

        This function uses Tabulate Intersection to derive a population count for each reporting
        unit and transfers that value to an output table. Population density is then calculated by dividing the
        population count by the reporting unit area.

    **Arguments:**

        * *inReportingUnitFeature* - input Reporting Unit feature class with full path.
        * *reportingUnitIdField* - the name of the field in the reporting unit feature class containing a unique identifier
        * *ruAreaFld* - the name of the field in the reporting unit feature class containing the unit area in square kilometers
        * *inCensusFeature* - input population feature class with full path
        * *inPopField* - the name of the field in the population feature class containing count values
        * *outTable* -  the output table that will contain calculated population and density values
        * *metricConst* - an ATtILA2 object containing constant values to match documentation
        * *cleanupList* - object containing commands and parameters to perform at cleanup time.
        * *index* - if this function is going to be run multiple times, this index is used to keep track of intermediate
                    outputs and fieldnames.
        * *timer* - 
        * *logFile* -

    **Returns:**

        * None

    """
    # If the user specified an index, add an underscore as prefix.
    if index != "":
        index = "_T" + index
        
    popCntTablePrefix = f"pdm_populationCnt{index}_"
    populationTable = files.nameIntermediateFile([popCntTablePrefix,'Dataset'],cleanupList)
        
    # Calculate the weighted population within the reporting units
    arcpy.analysis.TabulateIntersection(inReportingUnitFeature, reportingUnitIdField, inCensusFeature, populationTable, None, inPopField, None, 'SQUARE_KILOMETERS')

    # Compile a list of fields that will be transferred from the intersected feature class into the output table
    fromFields = [f'{inPopField}']
    toField = 'POPCNT' + index
    # Transfer the values to the output table
    AddMsg(f"{timer.now()} Transferring values from {basename(populationTable)} to {basename(outTable)}.", 0, logFile)
    transferField(populationTable,outTable,fromFields,[toField],reportingUnitIdField,None,None,logFile)
    
    AddMsg(f"{timer.now()} Performing density calculation.", 0, logFile)
    # Set up a calculation expression for the final density calculation
    calcExpression = "!" + toField + "!/!" + ruAreaFld + "!"
    # Calculate the population density
    vector.addCalculateField(outTable,metricConst.populationDensityFieldName + index,"DOUBLE",calcExpression,"",logFile)    




def getPolygonPopCount(inPolygonFeature,inPolygonIdField,inCensusFeature,inPopField,classField,
                  outTable,metricConst,index="", logFile=None):
    """ Performs a transfer of population from input census features to input polygon features using simple
        areal weighting.  

    **Description:**

        This function uses Tabulate Intersection to construct a table with a field containing the area weighted
        population count for each input polygon unit. The population field is renamed from the metric constants entry.
        Finally, fields in the constructed table are trimmed down to just the Polygon Id field, the population count
        field, and any required fields such as OID.

    **Arguments:**

        * *inPolygonFeature* - input Polygon feature class with full path.
        * *inPolygonIdField* - the name of the field in the reporting unit feature class containing a unique identifier
        * *inCensusFeature* - input population feature class with full path
        * *inPopField* - the name of the field in the population feature class containing count values
        * *classField* - a field in the population feature class with a constant value
        * *outTable* -  the output table that will contain calculated population values
        * *metricConst* - an ATtILA2 object containing constant values to match documentation
        * *index* - if this function is going to be run multiple times, this index is used to keep track of intermediate
                    outputs and field names.

    **Returns:**

        * None

    """
    # Construct a table with a field containing the area weighted population count for each input polygon unit
    try:
        logArcpy('arcpy.TabulateIntersection_analysis', (inPolygonFeature,[inPolygonIdField],inCensusFeature,outTable,[classField],[inPopField]), logFile)
        arcpy.TabulateIntersection_analysis(inPolygonFeature,[inPolygonIdField],inCensusFeature,outTable,[classField],[inPopField])
    except:
        raise errors.attilaException(errorConstants.tabulateIntersectionError)

    # Rename the population count field.
    outPopField = metricConst.populationCountFieldNames[index]
    logArcpy('arcpy.AlterField_management', (outTable, inPopField, outPopField, outPopField), logFile)
    arcpy.AlterField_management(outTable, inPopField, outPopField, outPopField)

# def replaceNullValues(inTable,inField,newValue,logFile=None):
#     # Replace NULL values in a field with the supplied value
#     whereClause = inField+" IS NULL"
#     logArcpy("arcpy.UpdateCursor",(inTable, whereClause, "", inField),logFile)
#     updateCursor = arcpy.UpdateCursor(inTable, whereClause, "", inField)
#     for updateRow in updateCursor:
#         updateRow.setValue(inField, newValue)
#         # Persist all of the updates for this row.
#         updateCursor.updateRow(updateRow)
#         # Clean up our row element for memory management and to remove locks
#         del updateRow
#     # Clean up our row element for memory management and to remove locks
#     del updateCursor

def replaceNullValues(inTable,inField,newValue,logFile=None):
    # Replace NULL values in a field with the supplied value
    whereClause = f"{inField} IS NULL"
    logArcpy("arcpy.da.UpdateCursor",(inTable, inField, whereClause),logFile)
    with arcpy.da.UpdateCursor(inTable, inField, whereClause) as cursor:
        for row in cursor:
            row[0] = newValue
            cursor.updateRow(row)

def replaceNullsInFields(inTable, fields, newValue, logFile=None):
    with arcpy.da.UpdateCursor(inTable, fields) as cursor:
        for row in cursor:
            for i, fld in enumerate(fields):
                if row[i] is None:
                    row[i] = newValue
                cursor.updateRow(row)

def percentageValue(inTable, numeratorField, denominatorField, percentField, logFile=None):
    # Set up a calculate percentage expression 
    calcExpression = "getValuePercent(!"+numeratorField+"!,!"+denominatorField+"!)"
    codeBlock = """def getValuePercent(n,d):
                        if d == 0:
                            if n == 0:
                                return 0
                            else:
                                return 1
                        else:
                            return (n/d)*100"""

    # Calculate and record the percent population within view area
    vector.addCalculateField(inTable, percentField, "DOUBLE", calcExpression, codeBlock, logFile)

def differenceValue(inTable, totalField, subtratorField, resultField, logFile=None):
    # Set up a calculate percentage expression 
    calcExpression = "getValueDifference(!"+totalField+"!,!"+subtratorField+"!)"
    codeBlock = """def getValueDifference(n,d):
                        return (n-d)"""

    # Calculate and record the percent population within view area
    vector.addCalculateField(inTable, resultField, "DOUBLE", calcExpression, codeBlock, logFile)

def aboveValue(inTable, sourceField, threshold, addedField, logFile=None):
    # Set up a calculate percentage expression 
    calcExpression = "getValuePercent(!"+sourceField+"!, "+ threshold + ")"
    codeBlock = """def getValuePercent(n, d):
                        if n <= d:
                            return 0
                        else:
                            return 1"""

    # Calculate and record the percent population within view area
    vector.addCalculateField(inTable, addedField, "SHORT", calcExpression, codeBlock, logFile)

def belowValue(inTable, sourceField, threshold, addedField, logFile=None):
    # Set up a calculate percentage expression 
    calcExpression = "getValuePercent(!"+sourceField+"!, "+ threshold + ")"
    codeBlock = """def getValuePercent(n, d):
                        if n <= d:
                            return 1
                        else:
                            return 0"""

    # Calculate and record the percent population within view area
    vector.addCalculateField(inTable, addedField, "SHORT", calcExpression, codeBlock, logFile)


def landCoverViews(metricsBaseNameList, metricConst, viewRadius, viewThreshold, cleanupList, outTable, newTable,
                   reportingUnitIdField, facilityLCPTable, facilityRUIDTable, metricsFieldnameDict, lcpFieldnameDict, timer, logFile):

    # assign some metric constants to variables
    lowSuffix = metricConst.fieldSuffix
    highSuffix = metricConst.highSuffix
    belowSuffix = metricConst.belowFieldSuffix
    aboveSuffix = metricConst.aboveFieldSuffix
    cntFldName = metricConst.facilityCountFieldName

    AddMsg(f"{timer.now()} Finding facilities with views below threshold limit for selected class(es).", 0, logFile)
    for mBaseName in metricsBaseNameList:
        # belowValue(inTable, sourceField, threshold, addedField)
        belowValue(facilityLCPTable, lcpFieldnameDict[mBaseName][0], viewThreshold, mBaseName+belowSuffix, logFile)
        # Find facilities with views at or above threshold limit. This value can be used to check if all facilities have land cover information
        aboveValue(facilityLCPTable, lcpFieldnameDict[mBaseName][0], viewThreshold, mBaseName+aboveSuffix, logFile)

    # attach the reporting unit id's to the land cover proportions table by use of a join

    # joining the facilityLCPTable to the facilityRUIDTable will maintain a record for all input facilities. NULL values
    # will be assigned to any facility that did not have any land cover data (i.e., at least 1 raster cell center) in its
    # view radius buffer. This only true if the reporting unit also has at least one facility in it.
    
    AddMsg(f"{timer.now()} Joining {basename(facilityLCPTable)} to {arcpy.Describe(facilityRUIDTable).baseName} to maintain a record for all facilities.", 0, logFile)
    logArcpy("arcpy.management.JoinField", (facilityRUIDTable, "OBJECTID", facilityLCPTable, "ORIG_FID"), logFile)
    arcpy.management.JoinField(facilityRUIDTable, "OBJECTID", facilityLCPTable, "ORIG_FID")
    
    # Summarizing facilities with low views by Reporting Unit
    stats = []
    for mBaseName in metricsBaseNameList:
        stats.append([mBaseName + belowSuffix, "Sum"])

        stats.append([mBaseName + aboveSuffix, "Sum"])
        
    stats.append([metricConst.overlapName, "MIN"])

    # Get a unique name with full path for the output features - will default to current workspace:
    namePrefix = f"{metricConst.statsResultTable}{viewRadius.split()[0]}_"
    statsResultTable = files.nameIntermediateFile([namePrefix,"Dataset"], cleanupList)
    AddMsg(f"{timer.now()} Summarizing facilities with low views by Reporting Unit. Intermediate: {basename(statsResultTable)}", 0, logFile)
    logArcpy("arcpy.Statistics_analysis",(facilityRUIDTable, statsResultTable, stats, reportingUnitIdField),logFile)
    arcpy.Statistics_analysis(facilityRUIDTable, statsResultTable, stats, reportingUnitIdField)

    # INFO tables have been blocked as a possible output format. The following code can be utilized.
    #Rename the fields in the result table
    arcpy.AlterField_management(statsResultTable, "FREQUENCY", cntFldName, cntFldName)
    
    statFields = []
    for mBaseName in metricsBaseNameList:
        oldFieldName = f"SUM_{mBaseName}{metricConst.belowFieldSuffix}"
        newFieldName = metricsFieldnameDict[mBaseName][0]
        statFields.append(newFieldName)
        arcpy.AlterField_management(statsResultTable, oldFieldName, newFieldName, newFieldName)
        
        oldFieldName = f"SUM_{mBaseName}{metricConst.aboveFieldSuffix}"
        newFieldName = f"{mBaseName}{metricConst.highSuffix}{viewThreshold}"
        statFields.append(newFieldName)
        arcpy.AlterField_management(statsResultTable, oldFieldName, newFieldName, newFieldName)

    arcpy.AlterField_management(statsResultTable, "MIN_FLCV_OVER", "MIN_OVER", "MIN_OVER" )
    statFields.append("MIN_OVER")
    
    # reporting units may contain facilities, but if no land cover occurs in their buffer area, NULL values will be in the stats table
    AddMsg(f"{timer.now()} Setting any null values in {basename(statsResultTable)} to -99999", 0, logFile)    
    replaceNullsInFields(statsResultTable, statFields, -99999)
    
    # Report to the user if land cover data was not available for all facilities within a reporting unit.
    # If full land cover data was available, the number of facilities in a reporting unit will equal the low and high counts.
    
    AddMsg(f"{timer.now()} Checking for reporting units with only partial land cover and facilities overlap.")
    statFields.insert(0, cntFldName)

    # with arcpy.da.SearchCursor(statsResultTable, statFields) as cursor:
    #     for row in cursor:
    #         # if (lowValue + highValue != facilityCount)
    #         if row[1] + row[2] != row[0]:
    #             arcpy.AddWarning(f"One or more facilities did not have land cover data within its view radius. "\
    #                              f"Check that the view radius is sufficiently large enough to contain at least one cell center "\
    #                              f"of the land cover grid or that the land cover raster extends beneath all facility features. "\
    #                              f"Problematic reporting units have a value in the {cntFldName} field higher than the sum "\
    #                              f"of the values in the '{lowSuffix}' and '{highSuffix}' fields.")
    #
    #             break
    
    sumWarning = False
    overlapWarning = False
    minIndex = statFields.index('MIN_OVER')
    with arcpy.da.UpdateCursor(statsResultTable, statFields) as cursor:
        for row in cursor:
            # if (lowValue + highValue != facilityCount)
            if row[1] + row[2] != row[0]:
                if row[1] != -99999: # -99999 fields have no land cover for any facility view area
                    for i in range(1,len(statFields)):
                        row[i] = -88888 # -88888 fields have missing land cover for one or more facilities
                    sumWarning = True
            cursor.updateRow(row)
            # if all facilities have some land cover, warn the user if one or more view areas have land cover on the low end
            if row[minIndex] >= 0 and row[minIndex] < 90:
                overlapWarning = True
                
    if sumWarning:            
        arcpy.AddWarning(f"One or more reporting units did not have land cover data within the view radius for all facilities. "\
                         f"Setting metric values for these reporting units to -88888 due to insufficient data.")
    
    if overlapWarning:            
        arcpy.AddWarning(f"One or more facilities had less than 90% overlap between its view area and the land cover raster. "\
                         f"The 'MIN_OVER' field in {basename(outTable)} analyzes the amount of overlap between the land cover "\
                         f"raster and all facilities in a reporting unit and reports out the lowest value found. If 'INTERMEDIATES' "\
                         f"was selected as an 'Additional Option', the saved flcv_FacilityRUID layer will show the amount "\
                         f"of overlap for each facility.")
               
    # Copy the stats table to a table with the requested name
    AddMsg(f"{timer.now()} Saving final output table: {basename(outTable)}", 0, logFile)
    logArcpy('arcpy.conversion.ExportTable', (statsResultTable,outTable), 0, logFile)
    arcpy.conversion.ExportTable(statsResultTable,outTable)


    # # Use the try: finally: section of code when INFO tables are possible as outputs.
    # try:
    #     setWarning = False
    #
    #     # Create the search cursor to query the contents of the BELOW THRESHOLD statistics table
    #     inTableRows = arcpy.SearchCursor(statsResultTable)
    #
    #     # create the insert cursor to add data to the output table
    #     outTableRows = arcpy.InsertCursor(newTable)        
    #
    #     for inRow in inTableRows:
    #         # initiate a row to add to the metric output table
    #         outTableRow = outTableRows.newRow()
    #
    #         # set the reporting unit id value in the output row
    #         outTableRow.setValue(reportingUnitIdField, inRow.getValue(reportingUnitIdField))
    #
    #         # set the number of facilities in the reporting unit in the output row 
    #         facilityCount = inRow.getValue("FREQUENCY")
    #         outTableRow.setValue(cntFldName, facilityCount)
    #
    #         # set the number of facilities in the reporting unit with below threshold views and above threshold views
    #         # in the output row. Do this for each selected metric class 
    #         for mBaseName in metricsBaseNameList:
    #             metricFieldName = metricsFieldnameDict[mBaseName][0]
    #
    #             # assemble the name for the high count field    
    #             outClassName = metricsFieldnameDict[mBaseName][1]
    #             highFieldName = metricConst.highField[0]+outClassName+metricConst.highField[1]
    #
    #             belowStatsFieldName = "SUM_" + mBaseName + belowSuffix
    #             lowValue = inRow.getValue(belowStatsFieldName)
    #             outTableRow.setValue(metricFieldName, lowValue )
    #
    #             aboveStatsFieldName = "SUM_" + mBaseName + aboveSuffix
    #             highValue = inRow.getValue(aboveStatsFieldName)
    #             outTableRow.setValue(highFieldName, highValue)
    #
    #         # commit the row to the output table
    #         outTableRows.insertRow(outTableRow)
    #
    #         if (lowValue + highValue != facilityCount):
    #             setWarning = True
    #
    #     if (setWarning):
    #         arcpy.AddWarning("One or more facilities did not have land cover data within its view radius. "\
    #                          "Check that the view radius is sufficiently large enough to contain at least one cell center "\
    #                          "of the land cover grid or that the land cover raster extends beneath all facility features. "\
    #                          "Problematic reporting units have a value in the "+ cntFldName +" field higher than the sum "\
    #                          "of the values in the '"+ lowSuffix +"' and '"+ highSuffix +"' fields.")
    #
    # finally:
    #
    #     # delete cursor and row objects to remove locks on the data
    #     try:
    #         del outTableRows
    #         del outTableRow
    #         del inRow
    #         del inTableRows
    #     except:
    #         pass
