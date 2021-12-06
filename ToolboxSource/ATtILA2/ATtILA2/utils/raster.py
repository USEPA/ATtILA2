""" Utilities specific to rasters

"""
import arcpy
import os
from arcpy.sa import Con,EucDistance,Raster,Reclassify,RegionGroup,RemapValue,SetNull,IsNull,Extent
from . import *
from .messages import AddMsg
## this is the code copied from pylet-master\pylet\arcpyutil\raster.py
import arcpy as _arcpy
from arcpy.sa.Functions import CreateConstantRaster
def getRasterPointFromRowColumn(raster, row, column):
    """ Get an arcpy `Point`_ object from an arcpy `Raster`_ object and zero based row and column indexes.

        **Description:**
        
        The row and column are zero-based and start in the upper left corner.  The arcpy `Point`_ object returned has
        X and Y coordinates representing the cell identified by the specified row and column.
        
        
        **Arguments:**
        
        * *raster* - arcpy `Raster`_ object
        * *row* - integer representing the zero based index of the row
        * *column* - integer representing the zero based index of the column
        
        
        **Returns:** 
        
        * arcpy `Point`_ object 
        
        .. _Point: http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#/Point/000v000000mv000000/
        .. _Raster: http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#/Raster/000v000000wt000000/

        
    """    

    
    extent = raster.extent    
    upperLeftX = extent.XMin
    upperLeftY = extent.YMax

    xDistanceFromUpperLeft = column * raster.meanCellWidth
    yDistanceFromUpperLeft = row * raster.meanCellHeight
    
    x = upperLeftX + xDistanceFromUpperLeft
    y = upperLeftY - yDistanceFromUpperLeft

    point = _arcpy.Point(x,y)
    
    return point


def getRasterValues(inRaster):
    """Utility for creating a python list of values from a raster's VALUE field.
    
    ** Description: **
        
        This function will open a search cursor on the raster and iterate through all the rows
        and collect all values in a python list object. By design, values in the raster's VALUE
        field are unique.
    
    **Arguments:**
    
        * *raster* - any raster dataset with an attribute table.
   
    **Returns:**
    
        * *valuesList - a python list of unique values
        
    """
    
    # warn user if input land cover grid has values not defined in LCC file
    rows = _arcpy.SearchCursor(inRaster) 

    valuesList = []
    for row in rows:
        valuesList.append(row.getValue("VALUE"))

    del row
    del rows
        
    return valuesList
## end of the code copied from pylet-master\pylet\arcpyutil\raster.py


def splitRasterYN(inRaster, maxSide):
    """Check if the raster is too large to perform a polygon conversion without first tiling the raster.
    
    ** Description: **
    
    **Arguments:**
    
        * *inRaster* - any raster dataset
        * *maxSide* - integer value
        
    **Returns:**
    
        * *boolean - True, if the raster is too large
        * *list - binary values indicating if number of raster columns and the number of raster rows exceed the specified maximum side 
    
    """
    splitYN = True
    columns = arcpy.GetRasterProperties_management(inRaster, 'COLUMNCOUNT').getOutput(0)
    xsplit = int(float(columns) / maxSide) + 1
    rows = arcpy.GetRasterProperties_management(inRaster, 'ROWCOUNT').getOutput(0)
    ysplit = int (float(rows) / maxSide) + 1
    xySplits = [xsplit, ysplit]
     
    if xsplit*ysplit == 1:
        splitYN = False
        
    return splitYN, xySplits


def clipGridByBuffer(inReportingUnitFeature,outName,inLandCoverGrid,inBufferDistance=None):
    if arcpy.Exists(outName):
        arcpy.Delete_management(outName)
        
    if inBufferDistance:
        # Buffering Reporting unit features...
        cellSize = Raster(inLandCoverGrid).meanCellWidth
        linearUnits = arcpy.Describe(inLandCoverGrid).spatialReference.linearUnitName
        bufferFloat = cellSize * (int(inBufferDistance)+1)
        bufferDistance = "%s %s" % (bufferFloat, linearUnits)
        arcpy.Buffer_analysis(inReportingUnitFeature, "in_memory/ru_buffer", bufferDistance, "#", "#", "ALL")
        
    # Clipping input grid to desired extent...
    if inBufferDistance:
        clippedGrid = arcpy.Clip_management(inLandCoverGrid, "#", outName,"in_memory/ru_buffer", "", "NONE")
        arcpy.Delete_management("in_memory")
    else:
        clippedGrid = arcpy.Clip_management(inLandCoverGrid, "#", outName, inReportingUnitFeature, "", "NONE")
    
    arcpy.BuildRasterAttributeTable_management(clippedGrid, "Overwrite")
    
    return clippedGrid
    
def getIntersectOfGrids(lccObj,inLandCoverGrid, inSlopeGrid, inSlopeThresholdValue, timer):            
    # Generate the slope X land cover grid where:
    #   1) land cover codes are preserved for areas on steep slopes,
    #   2) areas below the slope threshold are coded with the AreaBelowThresholdValue (Maximum Land Cover Class Value + 1).
    #   3) cells tagged as excluded are reinserted into the low slope areas.
    LCGrid = Raster(inLandCoverGrid)
    SLPGrid = Raster(inSlopeGrid)
    
    # find the highest value found in LCC XML file or land cover grid and add 1 to it
    addOne = True
    AreaBelowThresholdValue = getMaximumValue(LCGrid, lccObj, addOne)

    AddMsg(timer.now() + " Generating land cover above slope threshold grid...")    
    delimitedVALUE = arcpy.AddFieldDelimiters(SLPGrid,"VALUE")
    whereClause = delimitedVALUE+" >= " + inSlopeThresholdValue
    SLPxLCGrid = Con(SLPGrid, LCGrid, AreaBelowThresholdValue, whereClause)
     
    # get the frozenset of excluded values (i.e., values not to use when calculating the reporting unit effective area)
    excludedValues = lccObj.values.getExcludedValueIds()

    if excludedValues:
        AddMsg(timer.now() + " Inserting EXCLUDED values into areas below slope threshold...")
        # build a whereClause string (e.g. "VALUE" = 11 or "VALUE" = 12") to identify where excluded values occur on the land cover grid
        whereExcludedClause = buildWhereValueClause(SLPGrid, excludedValues)
        SLPxLCGrid = Con(LCGrid, LCGrid, SLPxLCGrid, whereExcludedClause) 
    
    return SLPxLCGrid


def getSetNullGrid(inConditionalGrid, inReplacementGrid, nullValuesList):
    # Identify inConditionalGrid grid cells whose values are in the nullValuesList and set them to NODATA. 
    # Replace the other cell values with values from the inLandCoverGrid.
    conditionalRaster = Raster(inConditionalGrid)   
    
    # build whereClause string (e.g. "VALUE" = 11 or "VALUE" = 12") to identify areas to set to NODATA
    whereClause = buildWhereValueClause(conditionalRaster, nullValuesList)

    replaceRaster = Raster(inReplacementGrid)
    nullSubstituteGrid = SetNull(conditionalRaster, replaceRaster, whereClause)
    
    return nullSubstituteGrid


def buildWhereValueClause(inRaster, valueList, exclude=False):
    # build whereClause string (e.g. "VALUE" <> 11 or "VALUE" <> 12") or 
    # (e.g. "VALUE" = 11 or "VALUE" = 12") depending on the state of the exclude boolean
    delimitedVALUE = arcpy.AddFieldDelimiters(inRaster,"VALUE")
    if exclude:
        operandStr = " <> "
    else:
        operandStr = " = "
    
    stringStart = delimitedVALUE+operandStr
    stringSep = " or "+delimitedVALUE+operandStr
        
    whereClause = stringStart + stringSep.join([str(item) for item in valueList])
    
    return whereClause


def addValuetoExcluded(aValue, lccObj):
    ''' This function adds a value to the list of values tagged as excluded in an LCC XML file.
    
    ** Description: **
    
        This function will retrieve the frozen set of values tagged as excluded in the LCC XML file,
        convert the frozen set to a list, and append the supplied value to that list. The new list
        of values is returned.
    
    **Arguments:**
    
        * *number* - an integer or float value
        * *lccObj* - a class object of the selected land cover classification file 
        
    **Returns:**
    
        * *list - a python list
        
    '''
    
    lccValuesDict = lccObj.values
    excludedValuesFrozen = lccValuesDict.getExcludedValueIds()
    excludedValues = [item for item in excludedValuesFrozen]
    excludedValues.append(aValue)
    
    return excludedValues


def getMaximumValue(inRaster, lccObj, addOne=False):
    """Utility for calculating the highest value from a raster's VALUE field or an LCC XML file.
    
    ** Description: **
        
        This function will determine the highest value between a raster's VALUE field and the VALUES section of
        an Land Cover Coding Scheme XML file. Once found, that maximum value is returned or it can be increased 
        by a value of one. The increased value is not found in either the raster or the LCC XML, and can be used
        to reclass grid cells as 'other' for metric calculations.
        An integer value is returned
    
    **Arguments:**
    
        * *raster* - any raster dataset with an attribute table.
        * *lccObj* - a class object of the selected land cover classification (LCC) XML file 
        * *boolean* - True, if calculating a value 1 higher than found in either raster or LCC XML 
   
    **Returns:**
    
        * *integer
        
    """
    # find the highest value found in LCC XML file or land cover grid 
    maxValue = inRaster.maximum
    xmlValues = lccObj.getUniqueValueIdsWithExcludes()
    for v in xmlValues:
        if v > maxValue:
            maxValue = v
    
    if addOne:
        # Add 1 to the highest value      
        maxValue = int(maxValue + 1)
    
    return maxValue


def getEdgeCoreGrid(m, lccObj, lccClassesDict, inLandCoverGrid, PatchEdgeWidth_str, processingCellSize_str, timer, shortName, scratchNameReference):
    # create grid where cover type of interest (e.g., forest) is coded 3, excluded values are coded 1, everything else is coded 2
    
    # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area calculation    
    lccValuesDict = lccObj.values
    
    #landCoverValues = raster.getRasterValues(inLandCoverGrid)
    landCoverValues = getRasterValues(inLandCoverGrid)

    # get the grid codes for this specified metric
    classValuesList = lccClassesDict[m].uniqueValueIds.intersection(landCoverValues)
    
    # get the frozenset of excluded values (i.e., values not to use when calculating the reporting unit effective area)
    excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)

    # define the reclass values with the format: newValuesList = [classValue, excludedValue, otherValue]
    classValue = 3
    excludedValue = 1
    otherValue = 2
    
    newValuesList = [classValue, excludedValue, otherValue]
    
    # generate a reclass list where each item in the list is a two item list: the original grid value, and the reclass value
    reclassPairs = getInOutOtherReclassPairs(landCoverValues, classValuesList, excludedValuesList, newValuesList)
            
    AddMsg(timer.now() + " Step 1 of 4: Reclassing land cover grid to Class = 3, Other = 2, and Excluded = 1...")
    reclassGrid = Reclassify(inLandCoverGrid,"VALUE", RemapValue(reclassPairs))
    
    AddMsg(timer.now() + " Step 2 of 4: Setting Class areas to Null...")
    delimitedVALUE = arcpy.AddFieldDelimiters(reclassGrid,"VALUE")
    otherGrid = SetNull(reclassGrid, 1, delimitedVALUE+" = 3")
    
    AddMsg(timer.now() + " Step 3 of 4: Finding distance from Other...")
    distGrid = EucDistance(otherGrid)
    
    AddMsg(timer.now() + " Step 4 of 4: Delimiting Class areas to Edge = 3 and Core = 4...")
    edgeDist = (float(PatchEdgeWidth_str) + 0.5) * float(processingCellSize_str) 

    zonesGrid = Con((distGrid >= edgeDist) & reclassGrid, 4, reclassGrid)
    
    # it appears that ArcGIS cannot process the BuildRasterAttributeTable request without first saving the raster.
    # This step wasn't the case earlier. Either ESRI changed things, or I altered something in ATtILA that unwittingly caused this. -DE
    namePrefix = shortName+"_"+"Raster"+m.upper()+PatchEdgeWidth_str+"_"
    scratchName = arcpy.CreateScratchName(namePrefix, "", "RasterDataset")
    scratchNameReference[0] = scratchName
    zonesGrid.save(scratchName)
            
    arcpy.BuildRasterAttributeTable_management(zonesGrid, "Overwrite")  
    arcpy.AddField_management(zonesGrid, "CATEGORY", "TEXT", "#", "#", "10")
    
    # Use categoryDict to pass on labels; should be in the format {gridValue1 : "category1 string", gridValue2: "category2 string", etc}
    categoryDict = {1:"Excluded", 2:"Other", 3:"Edge", 4:"Core"}
    updateCategoryLabels(zonesGrid, categoryDict)
            
    return zonesGrid

# def updateCoreEdgeCategoryLabels(Raster):
#     #Updates the CATEGORY field in the ForestCoreEdge with "Core" and "Edge" values
#     rows = arcpy.UpdateCursor(Raster)
#     row = rows.next()
#
#     while row:
#         #VALUE = 1 indicates a Core cell, Value = 3 is an Edge cell
#         v = row.getValue("Value")
#         if v == 4:
#             row.CATEGORY = "Core"
#         elif v == 3:
#             row.CATEGORY = "Edge"
#         elif v == 2:
#             row.CATEGORY = "Other"
#         elif v == 1:
#             row.CATEGORY = "Excluded"
#         rows.updateRow(row)
#         row = rows.next()  
    
    
def createPatchRaster(m,lccObj, lccClassesDict, inLandCoverGrid, metricConst, maxSeparation, minPatchSize, 
                         processingCellSize_str, timer, scratchNameReference):
    # create a list of all the grid values in the selected landcover grid
    #landCoverValues = raster.getRasterValues(inLandCoverGrid)
    landCoverValues = getRasterValues(inLandCoverGrid)
    
    # for the selected land cover class, get the class codes found in the input landcover grid
    lccValuesDict = lccObj.values
    classValuesList = lccClassesDict[m].uniqueValueIds.intersection(landCoverValues)
    
    # get the frozenset of excluded values (i.e., values not to use when calculating the reporting unit effective area)
    excludedValuesList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)
    
    # create class (value = 3) / other (value = 0) / excluded grid (value = -9999) raster
    # define the reclass values
    classValue = metricConst.classValue
    excludedValue = metricConst.excludedValue
    otherValue = metricConst.otherValue
    newValuesList = [classValue, excludedValue, otherValue]
    
    # generate a reclass list where each item in the list is a two item list: the original grid value, and the reclass value
    reclassPairs = getInOutOtherReclassPairs(landCoverValues, classValuesList, excludedValuesList, newValuesList)
            
    AddMsg(timer.now() + " Reclassing land cover to Class:"+m+" = "+str(classValue)+", Other = "+str(otherValue)+
           ", and Excluded = "+str(excludedValue)+"...")
    reclassGrid = Reclassify(inLandCoverGrid,"VALUE", RemapValue(reclassPairs))
     
    # create patch raster where:
    #    clusters of cells within the input threshold distance are considered a single patch
    #    and patches below the input minimum size have been discarded
    
    # Ensure all parameter inputs are the appropriate number type
    intMaxSeparation = int(maxSeparation)
    intMinPatchSize = int(minPatchSize)
    
    # Check if Maximum Separation > 0 if it is then skip to regions group analysis otherwise run Euclidean distance
    if intMaxSeparation == 0:
        AddMsg(timer.now() + " Assigning unique numbers to each unconnected cluster of Class:"+m+"...")
        regionOther = RegionGroup(reclassGrid == classValue,"EIGHT","CROSS","ADD_LINK","0")
    else:
        AddMsg(timer.now() + " Connecting clusters of Class:"+m+" within maximum separation distance...")
        fltProcessingCellSize = float(processingCellSize_str)
        maxSep = intMaxSeparation * float(processingCellSize_str)
        delimitedVALUE = arcpy.AddFieldDelimiters(reclassGrid,"VALUE")
        whereClause = delimitedVALUE+" < " + str(classValue)
        classRaster = SetNull(reclassGrid, 1, whereClause)
        eucDistanceRaster = EucDistance(classRaster, maxSep, fltProcessingCellSize)

        # Run Region Group analysis on UserEuclidPlus, ignores 0/NoData values
        AddMsg(timer.now() + " Assigning unique numbers to each unconnected cluster of Class:"+m+"...")
        UserEuclidRegionGroup = RegionGroup(eucDistanceRaster >= 0,"EIGHT","CROSS","ADD_LINK","0")

        # Maintain the original boundaries of each patch
        regionOther = Con(reclassGrid == classValue,UserEuclidRegionGroup, reclassGrid)

    if intMinPatchSize > 1:
        AddMsg(timer.now() + " Eliminating clusters below minimum patch size...")
        delimitedCOUNT = arcpy.AddFieldDelimiters(regionOther,"COUNT")
        whereClause = delimitedCOUNT+" < " + str(intMinPatchSize)
        regionOtherFinal = Con(regionOther, otherValue, regionOther, whereClause)
    else:
        regionOtherFinal = regionOther

    # add the excluded class areas back to the raster if present
    if excludedValuesList:
        regionOtherExcluded = Con(reclassGrid == excludedValue, reclassGrid, regionOtherFinal)
    else:
        regionOtherExcluded = regionOtherFinal

    # The Patch Metrics tool appears to have trouble calculating its metrics when the raster area is large and the
    # regionOtherExcluded grid is treated as a raster object in memory and not saved as a raster on disk
    namePrefix = metricConst.shortName+"_"+m+"_PatchRast"
    scratchName = arcpy.CreateScratchName(namePrefix, "", "RasterDataset")
    regionOtherExcluded.save(scratchName)
    desc = arcpy.Describe(regionOtherExcluded)
    scratchNameReference[0] = desc.catalogPath
    
    return regionOtherExcluded

    
def getInOutOtherReclassPairs(allRasterValues, selectedValuesList, excludedValuesList, newValuesList):
    # Generate a reclass list where each item in the list is a two item list: the original grid value, and the reclass value
    # Three reclass categories are defined:
    #     first value in the newValuesList is the new code for all values in the selected Class
    #     second value in the newValuesList is the code for any values tagged excluded in the LCC XML
    #     third value in the newvaluesList is the new code for everything else
    
    newIncludedValue = newValuesList[0]
    newExcludedValue = newValuesList[1]
    newOtherValue = newValuesList[2]
    reclassPairs = []
    for val in allRasterValues:
        oldValNewValPair = []
        oldValNewValPair.append(val)
        if val in selectedValuesList:
            oldValNewValPair.append(newIncludedValue)
        elif val in excludedValuesList:
            oldValNewValPair.append(newExcludedValue)
        else:
            oldValNewValPair.append(newOtherValue)
            
        reclassPairs.append(oldValNewValPair)
            
    return reclassPairs

def getRemapBinsByPercentStep(maxValue, pctStep):
    # Generate a reclass list to use in a RemapRange operation
    # The reclass list is comprised of a collection of three item lists (the bin)
    # The three items include:
    #    1) the start value of the reclass range,
    #    2) the end value of the reclass range, 
    #    3) and the new reclass value
    # The number of bins produced equals the maxValue divided by the pctStep
    # The pctStep should be a value between 1 and 100

    breakPnts = [i*(maxValue/100) for i in range(0, 100, pctStep)]
    reclassBins = []
    newValue = pctStep

    i = 1
    for n in range(len(breakPnts)):
        valuesStartStopNew = []
        # start of range
        valuesStartStopNew.append(breakPnts[n]) 
        if n+1 < len(breakPnts):
            # end of range
            valuesStartStopNew.append(breakPnts[n+1])
            # new grid value for values in range
            valuesStartStopNew.append(newValue*i)
        else:
            # end of last bin
            valuesStartStopNew.append(maxValue)
            valuesStartStopNew.append(100)
            
        reclassBins.append(valuesStartStopNew)

        i += 1
    
    return reclassBins

# def getProximityWithBurnInGrid(classValuesList,excludedValuesList,inLandCoverGrid,landCoverValues,neighborhoodSize_str,
#                      burnIn,burnInGrid,timer,rngRemap,zoneBin_str,proximityGridName):
#
#     # create class (value = 1) / other (value = 0) / excluded grid (value = 0) raster
#     # define the reclass values
#     classValue = 1
#     excludedValue = 0
#     otherValue = 0
#     newValuesList = [classValue, excludedValue, otherValue]
#
#     # generate a reclass list where each item in the list is a two item list: the original grid value, and the reclass value
#     reclassPairs = getInOutOtherReclassPairs(landCoverValues, classValuesList, excludedValuesList, newValuesList)
#
#     AddMsg(("{0} Reclassifying selected land cover class to 1. All other values = 0...").format(timer.now()))
#     reclassGrid = Reclassify(inLandCoverGrid,"VALUE", RemapValue(reclassPairs))
#
#     AddMsg(("{0} Performing focal SUM on reclassified raster using {1} x {1} cell neighborhood...").format(timer.now(), neighborhoodSize_str))
#     neighborhood = arcpy.sa.NbrRectangle(int(neighborhoodSize_str), int(neighborhoodSize_str), "CELL")
#     focalGrid = arcpy.sa.FocalStatistics(reclassGrid == classValue, neighborhood, "SUM")
#
#     AddMsg(("{0} Reclassifying focal SUM results into {1}% breaks...").format(timer.now(), zoneBin_str))
#     proximityGrid = Reclassify(focalGrid, "VALUE", rngRemap)
#
#     # Delete output grid if it already exists in the GDB. This prevents errors caused by lingering locks and such
#     try:
#         arcpy.Delete_management(proximityGridName)
#     except:
#         pass
#
#     if burnIn == "true":
#         AddMsg(("{0} Burning excluded areas into proximity grid...").format(timer.now()))
#         delimitedVALUE = arcpy.AddFieldDelimiters(burnInGrid,"VALUE")
#         whereClause = delimitedVALUE+" = 0"
#         proximityGrid = Con(burnInGrid, proximityGrid, burnInGrid, whereClause)
#     else:
#         # pare back the extent of the proximityGrid to the edges of the input land cover grid
#         AddMsg(("{0} Trimming proximity raster to Land cover grid extent...").format(timer.now()))
#         proximityGrid = SetNull(IsNull(reclassGrid) == 1, proximityGrid)
#
#     proximityGrid.save(proximityGridName)
#
#     return proximityGrid, focalGrid


def getNbrPctWithBurnInGrid(inNeighborhoodSize, landCoverValues, classValuesList, excludedValuesList,
                                   inLandCoverGrid, burnIn, burnInGrid, timer):
    # Determine the maximum sum for the neighborhood
    maxCellCount = pow(int(inNeighborhoodSize), 2)
    
    # radiusCnt = int(inNeighborhoodSize)
    # AddMsg("Calculating maximum cell count  %s" % timer.start())
    # testCellCount = getCircleCellCount(inLandCoverGrid, radiusCnt)
    # AddMsg("Max Cell Count = %s  %s" % (testCellCount, timer.split()))
    # # AddMsg("Looking up dictionary cell count  %s" % timer.start())
    # dictCellCount = lookupCircleCellCount(radiusCnt)
    # AddMsg("Dict Cell Count = %s  %s" % (dictCellCount, timer.split()))
    
         
    # create class (value = 1) / other (value = 0) / excluded grid (value = 0) raster
    # define the reclass values
    classValue = 1
    excludedValue = 0
    otherValue = 0
    newValuesList = [classValue, excludedValue, otherValue]
    
    # generate a reclass list where each item in the list is a two item list: the original grid value, and the reclass value
    reclassPairs = getInOutOtherReclassPairs(landCoverValues, classValuesList, excludedValuesList, newValuesList)
      
    AddMsg(("{0} Reclassifying selected land cover class to 1. All other values = 0...").format(timer.now()))
    reclassGrid = Reclassify(inLandCoverGrid,"VALUE", RemapValue(reclassPairs))
    
    AddMsg(("{0} Performing focal SUM on reclassified raster using {1} x {1} cell neighborhood...").format(timer.now(), inNeighborhoodSize))
    neighborhood = arcpy.sa.NbrRectangle(int(inNeighborhoodSize), int(inNeighborhoodSize), "CELL")
    #nbrSumGrid = arcpy.sa.FocalStatistics(reclassGrid == classValue, neighborhood, "SUM", "NODATA")
    nbrCntGrid = arcpy.sa.FocalStatistics(reclassGrid, neighborhood, "SUM", "NODATA")
        
    AddMsg(("{0} Calculating the proportion of land cover class within {1} x {1} cell neighborhood...").format(timer.now(), inNeighborhoodSize))
    proportionsGrid = arcpy.sa.RasterCalculator([nbrCntGrid], ["x"], (' (x / '+str(maxCellCount)+') * 100') )

    if burnIn == "true":
        AddMsg(("{0} Burning excluded areas into proportions grid...").format(timer.now()))
        delimitedVALUE = arcpy.AddFieldDelimiters(burnInGrid,"VALUE")
        whereClause = delimitedVALUE+" = 0"
        proportionsGrid = Con(burnInGrid, proportionsGrid, burnInGrid, whereClause)
    
    proportionsIntGrid = arcpy.sa.Int(proportionsGrid)

    return proportionsIntGrid, nbrCntGrid


def getViewGrid(classValuesList, excludedValuesList, inLandCoverGrid, landCoverValues, viewRadius, conValues, timer):
    # create class (value = 1) / other (value = 0) / excluded grid (value = 0) raster
    # define the reclass values
    classValue = 1
    excludedValue = 0
    otherValue = 0
    newValuesList = [classValue, excludedValue, otherValue]
    
    # generate a reclass list where each item in the list is a two item list: the original grid value, and the reclass value
    reclassPairs = getInOutOtherReclassPairs(landCoverValues, classValuesList, excludedValuesList, newValuesList)
      
    AddMsg(("{0} Reclassifying selected land cover class to 1. All other values = 0...").format(timer.now()))
    reclassGrid = Reclassify(inLandCoverGrid,"VALUE", RemapValue(reclassPairs))
    
    AddMsg(("{0} Performing focal SUM on reclassified raster using {1} cell radius neighborhood...").format(timer.now(), viewRadius))
    neighborhood = arcpy.sa.NbrCircle(int(viewRadius), "CELL")
    focalGrid = arcpy.sa.FocalStatistics(reclassGrid == classValue, neighborhood, "SUM")
    
    AddMsg(("{0} Reclassifying focal SUM results into view = 0 and no-view = 1 binary raster...").format(timer.now()))
#    delimitedVALUE = arcpy.AddFieldDelimiters(focalGrid,"VALUE")
#    whereClause = delimitedVALUE+" = 0"
#    viewGrid = Con(focalGrid, 1, 0, whereClause)
    whereValue = conValues[0]
    trueValue = conValues[1]
    viewGrid = Con(Raster(focalGrid) == whereValue, trueValue)
    return viewGrid

def getPatchViewGrid(m, classValuesList, excludedValuesList, inLandCoverGrid, landCoverValues, viewRadius, conValues, minimumPatchSize, timer, saveIntermediates, metricConst):
    # create class (value = 1) / other (value = 0) / excluded grid (value = 0) raster
    # define the reclass values
    classValue = 1
    excludedValue = 0
    otherValue = 0
    newValuesList = [classValue, excludedValue, otherValue]
    
    # generate a reclass list where each item in the list is a two item list: the original grid value, and the reclass value
    reclassPairs = getInOutOtherReclassPairs(landCoverValues, classValuesList, excludedValuesList, newValuesList)
      
    AddMsg(("{0} Reclassifying selected land cover class, {1}, to 1. All other values = 0...").format(timer.now(), m.upper()))
    reclassGrid = Reclassify(inLandCoverGrid,"VALUE", RemapValue(reclassPairs))
 
    if int(minimumPatchSize) > 1:
        # find patches of selected land cover >= the minimum patch size requirement
                    
        AddMsg(("{0} Calculating size of class patches...").format(timer.now()))
        regionGrid = RegionGroup(reclassGrid,"EIGHT","WITHIN","ADD_LINK")
                    
        AddMsg(("{0} Assigning {1} to patches >= minimum size threshold of {2} cells...").format(timer.now(), "1", minimumPatchSize))
        delimitedCOUNT = arcpy.AddFieldDelimiters(regionGrid,"COUNT")
        whereClause = delimitedCOUNT+" >= " + minimumPatchSize + " AND LINK = 1"
        patchGrid = Con(regionGrid, classValue, 0, whereClause)
    else:
        patchGrid = reclassGrid
        
    # save the intermediate raster if save intermediates option has been chosen
    if saveIntermediates: 
        namePrefix = "%s_%s%s_" % (metricConst.shortName, m.upper(), metricConst.patchGridName)
        scratchName = arcpy.CreateScratchName(namePrefix, "", "RasterDataset")
        patchGrid.save(scratchName)
        
        # add a CATEGORY field for raster labels; make it large enough to hold your longest category label.        
        classLabelSize = len(m) + 1
        if classLabelSize > 10:
            fieldSize = classLabelSize
        else:
            fieldSize = 10
        arcpy.BuildRasterAttributeTable_management(patchGrid, "Overwrite")       
        arcpy.AddField_management(patchGrid, "CATEGORY", "TEXT", "#", "#", str(fieldSize))
        
        # Use categoryDict to pass on labels; should be in the format {gridValue1 : "category1 string", gridValue2: "category2 string", etc}
        # Undefined grid values will appear as NULL
        categoryDict = {0: "Other", 1: m}
        updateCategoryLabels(patchGrid, categoryDict)
                
        AddMsg(timer.now() + " Save intermediate grid complete: "+os.path.basename(scratchName))

    AddMsg(("{0} Performing focal SUM on patches of {1} using {2} cell radius neighborhood...").format(timer.now(), m.upper(), viewRadius))
    neighborhood = arcpy.sa.NbrCircle(int(viewRadius), "CELL")
    focalGrid = arcpy.sa.FocalStatistics(patchGrid == classValue, neighborhood, "SUM")
    
    AddMsg(("{0} Reclassifying focal SUM results into a single-value raster where 1 = potential view area...").format(timer.now()))
    whereValue = conValues[0]
    trueValue = conValues[1]
    viewGrid = Con(Raster(focalGrid) > whereValue, trueValue)
            
    return viewGrid


def updateCategoryLabels(Raster, categoryDict):
    # Updates the CATEGORY field in the Raster with values from the categoryDict
    # The categoryDict should be in the format {integer: string} (e.g. 1: "Core")
    # CAUTION: Undefined grid values will have a NULL category label and will not appear in the TOC
    rows = arcpy.UpdateCursor(Raster)
    row = rows.next()
    
    while row:
        v = row.getValue("Value")
        try:
            row.CATEGORY = categoryDict[v]
            rows.updateRow(row)
        except:
            pass
            
        row = rows.next()


def getCircleCellCount(inRaster, radiusInCells):
    maxCellCount = lookupCircleCellCount(radiusInCells)
    
    if maxCellCount == 0:
        maxCellCount = calcCircleCellCount(inRaster, radiusInCells)
        
    return maxCellCount

def calcCircleCellCount(inRaster,radiusInCells):
    """Utility for calculating the maximum cell count for a circular neighborhood of a given radius.
    
    ** Description: **
        
        This function will create a constant raster with a value of 1, the cell resolution of the
        Raster parameter, and the smallest extent possible to generate one full circular neighborhood area
        with the supplied radius in cell count.
        
        The generated constant raster will be used in a focal statistics circle neighboorhood operation to 
        determine the maximum cell count possible for the neighborhood. The maximum cell count is returned.
    
    **Arguments:**
    
        * *inRaster* - any raster dataset with an attribute table.
        * *radiusInCells* - integer value
   
    **Returns:**
    
        * *integer - maximum cell count for circle neighborhood
        
    """
    
    from arcpy import env
    
    # Prepare to replace and reset the environmental output coordinate system
    tempEnvOCS = env.outputCoordinateSystem
    
    # determine the smallest needed extent to generate one full circular buffer
    # adding 1 to the input radius will give the smallest needed. adding 3 will give some wiggle room
    inRasterDesc = arcpy.Describe(inRaster)
    cellSize = inRasterDesc.meanCellHeight    
    diameterCellCount = (2 * radiusInCells) + 3
    extentWidth = cellSize * diameterCellCount
    
    xMin = inRasterDesc.extent.XMin
    yMin = inRasterDesc.extent.YMin
    xMax = xMin + extentWidth
    yMax = yMin + extentWidth
    
    outExtent = Extent(xMin, yMin, xMax, yMax)
    
    # Extent units will be in the linear units of the environmental output coordinate system
    # Temporarily set them to match the input raster
    env.outputCoordinateSystem = inRasterDesc.spatialReference
    
    oneRaster = CreateConstantRaster(1, "INTEGER", cellSize, outExtent)
    #oneRaster.save("oneRaster")
    
    neighborhood = arcpy.sa.NbrCircle(radiusInCells, "CELL")
    nbrCntGrid = arcpy.sa.FocalStatistics(oneRaster, neighborhood, "SUM", "NODATA")
    #nbrCntGrid.save("nbrCntGrid")
    
    circleCellCount = nbrCntGrid.maximum
    
    # reset the environments
    env.outputCoordinateSystem = tempEnvOCS
    
    return circleCellCount


def lookupCircleCellCount(radiusInCells):
    radiusCellCountDict = dict({
                                1: 5,
                                2: 13,
                                3: 29,
                                4: 49,
                                5: 81,
                                6: 113,
                                7: 149,
                                8: 197,
                                9: 253,
                                10: 317,
                                11: 377,
                                12: 441,
                                13: 529,
                                14: 613,
                                15: 709,
                                16: 797,
                                17: 901,
                                18: 1009,
                                19: 1129,
                                20: 1257,
                                21: 1373,
                                22: 1517,
                                23: 1653,
                                24: 1793,
                                25: 1961,
                                26: 2121,
                                27: 2289,
                                28: 2453,
                                29: 2629,
                                30: 2821,
                                31: 3001,
                                32: 3209,
                                33: 3409,
                                40: 5025,
                                45: 6361,
                                50: 7845,
                                55: 9477,
                                60: 11289,
                                66: 13673,
                                70: 15373,
                                75: 17665,
                                80: 20081,
                                90: 25445,
                                100: 31417,
                                125: 49077,
                                150: 70681,
                                200: 125629,
                                250: 196321,
                                300: 282697,
                                333: 348281,
                                350: 384765,
                                400: 502625,
                                450: 636121,
                                500: 785349,
                                750: 1767121,
                                1000: 3141549
                                })
    
    circleCellCount = radiusCellCountDict.get(radiusInCells, 0)

    return circleCellCount
