""" Utilities specific to rasters

"""
import arcpy
from arcpy.sa import Con,EucDistance,ExtractByAttributes,Plus,Raster,Reclassify,RegionGroup,RemapRange,RemapValue,SetNull
from pylet import arcpyutil
from pylet.arcpyutil.messages import AddMsg
from arcpy import env


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
            
    # Generate the slope X land cover grid where areas below the threshold slope are
    # set to the value 'Maximum Land Cover Class Value + 1'.
    LCGrid = Raster(inLandCoverGrid)
    SLPGrid = Raster(inSlopeGrid)
    
    # find the highest value found in LCC XML file or land cover grid  
    lccValuesDict = lccObj.values
    maxValue = LCGrid.maximum
    xmlValues = lccObj.getUniqueValueIdsWithExcludes()
    for v in xmlValues:
        if v > maxValue:
            maxValue = v

    AddMsg(timer.split() + " Generating land cover above slope threshold grid...")    
    AreaBelowThresholdValue = int(maxValue + 1)
    delimitedVALUE = arcpy.AddFieldDelimiters(SLPGrid,"VALUE")
    whereClause = delimitedVALUE+" >= " + inSlopeThresholdValue
    SLPxLCGrid = Con(SLPGrid, LCGrid, AreaBelowThresholdValue, whereClause)
    
    # determine if a grid code is to be included in the effective reporting unit area calculation    
    # get the frozenset of excluded values (i.e., values not to use when calculating the reporting unit effective area)
    excludedValues = lccValuesDict.getExcludedValueIds()
        
    # if certain land cover codes are tagged as 'excluded = TRUE', generate grid where land cover codes are 
    # preserved for areas coincident with steep slopes, areas below the slope threshold are coded with the 
    # AreaBelowThresholdValue except for where the land cover code is included in the excluded values list.
    # In that case, the excluded land cover values are maintained in the low slope areas.
    if excludedValues:
        # build a whereClause string (e.g. "VALUE" = 11 or "VALUE" = 12") to identify where on the land cover grid excluded values occur
        AddMsg(timer.split() + " Inserting EXCLUDED values into areas below slope threshold...")
        stringStart = delimitedVALUE+" = "
        stringSep = " or "+delimitedVALUE+" = "
        whereExcludedClause = stringStart + stringSep.join([str(item) for item in excludedValues])
        SLPxLCGrid = Con(LCGrid, LCGrid, SLPxLCGrid, whereExcludedClause) 
    
    return SLPxLCGrid


def getEdgeCoreGrid(m, lccObj, lccClassesDict, inLandCoverGrid, PatchEdgeWidth_str, fallBackDirectory, scratchGDBFilename, 
                    processingCellSize_str, timer):
    # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area calculation    
    lccValuesDict = lccObj.values
    landCoverValues = arcpyutil.raster.getRasterValues(inLandCoverGrid)
    
    # get the grid codes for this specified metric
    ClassValuesList = lccClassesDict[m].uniqueValueIds.intersection(landCoverValues)
    
    # get the frozenset of excluded values (i.e., values not to use when calculating the reporting unit effective area)
    ExcludedValueList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)

    # create grid where cover type of interest (e.g., forest) is coded 3, excluded values are coded 1, everything else is coded 2
    reclassPairs = []
    for val in landCoverValues:
        oldValNewVal = []
        oldValNewVal.append(val)
        if val in ClassValuesList:
            oldValNewVal.append(3)
            reclassPairs.append(oldValNewVal)
        elif val in ExcludedValueList:
            oldValNewVal.append(1)
            reclassPairs.append(oldValNewVal)
        else:
            oldValNewVal.append(2)
            reclassPairs.append(oldValNewVal)
            
    AddMsg(timer.split() + " Step 1 of 4: Reclassing land cover grid to Class = 3, Other = 2, and Excluded = 1...")
    reclassGrid = Reclassify(inLandCoverGrid,"VALUE", RemapValue(reclassPairs))
    
    AddMsg(timer.split() + " Step 2 of 4: Setting Class areas to Null...")
    delimitedVALUE = arcpy.AddFieldDelimiters(reclassGrid,"VALUE")
    otherGrid = SetNull(reclassGrid, 1, delimitedVALUE+" = 3")
    
    AddMsg(timer.split() + " Step 3 of 4: Finding distance from Other...")
    distGrid = EucDistance(otherGrid)
    
    AddMsg(timer.split() + " Step 4 of 4: Delimiting Class areas to Edge = 3 and Core = 4...")
    edgeDist = round(float(PatchEdgeWidth_str) * float(processingCellSize_str))
    zonesGrid = Con((distGrid >= edgeDist) & reclassGrid, 4, reclassGrid)
    arcpy.BuildRasterAttributeTable_management(zonesGrid, "Overwrite") 

    arcpy.AddField_management(zonesGrid, "CATEGORY", "TEXT", "#", "#", "10")
    updateCoreEdgeCategoryLabels(zonesGrid)
    
    return zonesGrid

def updateCoreEdgeCategoryLabels(Raster):
    #Updates the CATEGORY field in the ForestCoreEdge with "Core" and "Edge" values
    rows = arcpy.UpdateCursor(Raster)
    row = rows.next()
    
    while row:
        #VALUE = 1 indicates a Core cell, Value = 3 is an Edge cell
        v = row.getValue("Value")
        if v == 4:
            row.CATEGORY = "Core"
        elif v == 3:
            row.CATEGORY = "Edge"
        elif v == 2:
            row.CATEGORY = "Other"
        elif v == 1:
            row.CATEGORY = "Excluded"
        rows.updateRow(row)
        row = rows.next()


# def createPatchRaster(m,lccObj, lccClassesDict, inLandCoverGrid, fallBackDirectory, MaxSeperation, MinPatchSize, processingCellSize_str):
# 
#     import os
# 
#     # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area calculation    
#     lccValuesDict = lccObj.values
#     landCoverValues = arcpyutil.raster.getRasterValues(inLandCoverGrid)
#     
#     # get the grid codes for this specified metric
#     UserValueList = lccClassesDict[m].uniqueValueIds.intersection(landCoverValues)
#     
#     # Generate the edge/core/other/excluded grid
#     LCGrid = inLandCoverGrid
#     
#     #Extract User Categories from Land use grid
#     env.workspace = os.path.dirname(LCGrid)
#     inputLC = os.path.basename(LCGrid)
#     
#     #Extract User
#     ExtractUserCat = ExtractLU(UserValueList, inputLC)
#     
#     #reset workspace to user defined output space (this is necessary because ArcGIS looks for the input landcover in
#     #the workspace even if another path is called).
# 
# 
#     TempOutspace =  fallBackDirectory
#     env.workspace = TempOutspace
#     
#     #Create new User Grid with a single value for the user category(intermediate layer)
#     intUserValueList = []
#     
#     #Convert Forest Value List into a list of integers
#     intUserValueList = convertList(UserValueList)
#     if len(intUserValueList) != 0:
#         UserRemapRange = RemapRange([[min(intUserValueList), max(intUserValueList), 1]])
#         UserSingle = Reclassify(ExtractUserCat, "Value", UserRemapRange)
#     else:
#         UserSingle = ExtractUserCat
#     
#     #Check to see if Maximum Separation > 0 if it is then skip to regions group analysis otherwise run
#     #Euclidean distance
#     if MaxSeperation == 0:
#         #Run Regions group then run TabArea_FeatureLayer
#         UserSingleRegionGroup = RegionGroup(UserSingle,"EIGHT","CROSS","ADD_LINK","")
#         if MinPatchSize > 1:
#             FinalPatchRas = ExtractByAttributes(UserSingleRegionGroup, "COUNT >" + str(MinPatchSize -1))
#             FinalPatchRas.save("FinalPatches")
#             return FinalPatchRas
#         else:
#             UserSingleRegionGroup.save("FinalPatches")
#             return UserSingleRegionGroup
# 
# 
# #        if "PatchMetrics" in AnalysisList:
# #            tabulatePatchMetrics("FinalPatches")
# #        if "MDCP" in AnalysisList:
# #            tabulateMDCP("FinalPatches")
#     else:
#         #Calclulate Euclidean Distance based on max separation value
#         gridcellsize_int = int(processingCellSize_str)
#         maxSep = MaxSeperation * gridcellsize_int
#         outEucDistance = EucDistance(UserSingle, maxSep, str(gridcellsize_int))
# 
#         #Extract only the max seperation value from the Euclidean distance
#         EucDistanceExtract = ExtractByAttributes(outEucDistance, "VALUE = " + str(maxSep))
#         EucDistanceExtract.save("EucDistance_MaxSep")
# 
#         #Reclassify Euclid distance so that NoData = 0
#         EucDistReMapRange = RemapRange([[maxSep, maxSep, maxSep],["noData", "noData", 0]])
#         EucDistReClass = Reclassify("EucDistance_MaxSep", "VALUE", EucDistReMapRange)
# 
#         #Reclassify  Single User Category Grid so that NoData = 0
#         UserReMapRange = RemapRange([[1,1,1], ["noData", "noData", 0]])
#         UserReClass = Reclassify(UserSingle, "VALUE", UserReMapRange)
# 
#         #Add (sum) UserReclass and EucDistanceReclass
#         UserEuclidPlus = Plus(UserReClass, EucDistReClass)
# 
#         #Run Region Group analysis on UserEuclidPlus, ignores 0/NoData values
#         UserEuclidRegionGroup = RegionGroup(UserEuclidPlus,"EIGHT","CROSS","ADD_LINK","0")
# 
#         #Reclass Euclid Reclass to -99999
#         EucRcReMapRange = RemapRange([[maxSep, maxSep, -99999],[0, 0, 0]])
#         EucReClass999 =Reclassify(EucDistReClass,"VALUE", EucRcReMapRange)
# 
#         #Add (sum) regions result to EucReClass999 result
#         RegionEucPlus = Plus(UserEuclidRegionGroup,EucReClass999)    
# 
#         #Extract by Attribute Values greater than one to maintain the original boundaries of each patch
#         RegionPatches = ExtractByAttributes(RegionEucPlus, "VALUE > 0")
#         if MinPatchSize > 1:
#             FinalPatchRas = ExtractByAttributes(RegionPatches, "COUNT >" + str(MinPatchSize -1))
#             FinalPatchRas.save("FinalPatches")
#             return FinalPatchRas
#         else:
#             RegionPatches.save("FinalPatches")
#             return RegionPatches
# 
# 
# #        if "PatchMetrics" in AnalysisList:
# #            tabulatePatchMetrics("FinalPatches")
# #        if "MDCP" in AnalysisList:
# #            tabulateMDCP("FinalPatches", TempOutspace, ReportingUnitFeature, ReportingUnitField, SearchRadius)
# 
# # Extracts land use values so that they can be temporary.
# def ExtractLU(ValueList, inputLandcover):
#     #Set up the values for the sql expression
#     StrValuesList = convertList(ValueList)
#     values = ",".join(StrValuesList)
#     #Extract the  selected categories from the Landuse grid
#     if values == "":
#         values = "null"    
#     attExtract = ExtractByAttributes(inputLandcover, "VALUE IN (" + values + ")")
#     return attExtract
#    
# def convertList(inList):
#     outList = []
#     for l in inList:
#         if type(l) is not int:
#             outList.append(int(l))
#         elif type(l) is int:
#             outList.append(str(l))  
#     return outList    
    
    
def createPatchRasterNew(m,lccObj, lccClassesDict, inLandCoverGrid, metricConst, maxSeparation, minPatchSize, 
                         processingCellSize_str, timer):
    # create a list of all the grid values in the selected landcover grid
    landCoverValues = arcpyutil.raster.getRasterValues(inLandCoverGrid)
    
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
            
    AddMsg(timer.split() + " Reclassing land cover to Class:"+m+" = "+str(classValue)+", Other = "+str(otherValue)+
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
        AddMsg(timer.split() + " Assigning unique numbers to each unconnected cluster of Class:"+m+"...")
        regionOther = RegionGroup(reclassGrid == classValue,"EIGHT","CROSS","ADD_LINK","0")
    else:
        AddMsg(timer.split() + " Connecting clusters of Class:"+m+" within maximum separation distance...")
        fltProcessingCellSize = float(processingCellSize_str)
        maxSep = intMaxSeparation * float(processingCellSize_str)
        delimitedVALUE = arcpy.AddFieldDelimiters(reclassGrid,"VALUE")
        whereClause = delimitedVALUE+" < " + str(classValue)
        classRaster = SetNull(reclassGrid, 1, whereClause)
        eucDistanceRaster = EucDistance(classRaster, maxSep, fltProcessingCellSize)

        # Run Region Group analysis on UserEuclidPlus, ignores 0/NoData values
        AddMsg(timer.split() + " Assigning unique numbers to each unconnected cluster of Class:"+m+"...")
        UserEuclidRegionGroup = RegionGroup(eucDistanceRaster >= 0,"EIGHT","CROSS","ADD_LINK","0")

        # Maintain the original boundaries of each patch
        regionOther = Con(reclassGrid == classValue,UserEuclidRegionGroup, reclassGrid)

    if intMinPatchSize > 1:
        AddMsg(timer.split() + " Eliminating clusters below threshold size...")
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
