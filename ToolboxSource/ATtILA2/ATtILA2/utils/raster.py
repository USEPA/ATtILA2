""" Utilities specific to rasters

"""
import sys, os
import arcpy
from arcpy.sa import *
from pylet import arcpyutil
from arcpy import env
# generate the log file
    
def getIntersectOfGrids(lccObj,inLandCoverGrid, inSlopeGrid, inSlopeThresholdValue):
        
    # Generate the slope X land cover grid where areas below the threshold slope are
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


def getEdgeCoreGrid(m, lccObj, lccClassesDict, inLandCoverGrid, PatchEdgeWidth_str, fallBackDirectory, processingCellSize_str):
    # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area calculation    
    lccValuesDict = lccObj.values
    landCoverValues = arcpyutil.raster.getRasterValues(inLandCoverGrid)
    
    # get the grid codes for this specified metric
    UserValueList = lccClassesDict[m].uniqueValueIds.intersection(landCoverValues)
    
    # get the frozenset of excluded values (i.e., values not to use when calculating the reporting unit effective area)
    WaterValueList = lccValuesDict.getExcludedValueIds().intersection(landCoverValues)

    LandValueList = lccValuesDict.getIncludedValueIds().intersection(landCoverValues)

    OtherValueList = set(landCoverValues) - UserValueList - WaterValueList
    

    import os
    TempOutspace =  fallBackDirectory
    env.cellSize = processingCellSize_str

    # Generate the edge/core/other/excluded grid
    LCGrid = inLandCoverGrid
    
    #Extract User Categories from Land use grid
    env.workspace = os.path.dirname(LCGrid)
    inputLC = os.path.basename(LCGrid)

    ExtractDict = {}
    ExtractDict["ExtractUserCat"]= UserValueList
    ExtractDict["ExtractWater"] = WaterValueList
    ExtractDict["ExtractOther"] = OtherValueList
    
    #Extract User, Water, and Other

    ExtractUserCat = ExtractLU(ExtractDict["ExtractUserCat"], inputLC)
    ExtractWater =  ExtractLU(ExtractDict["ExtractWater"],inputLC)
    ExtractOther = ExtractLU(ExtractDict["ExtractOther"], inputLC)
                           
    #Extract Non User Categories from Land use grid
    StrValuesList = convertList(ExtractDict["ExtractUserCat"])
    values = ",".join(StrValuesList)

    if values == "":
        values = "null"
    ExtractNonUserCat = ExtractByAttributes(inputLC, "VALUE NOT IN (" + values +")")
    
    #change workspace to output space
    env.workspace = TempOutspace
    
    #Calculate the Euclidean distance using the NonUser
    gridcellsize_int = int(processingCellSize_str)
    maxdist = int(PatchEdgeWidth_str) * gridcellsize_int
    
    outEucDistance = EucDistance(ExtractNonUserCat, maxdist, processingCellSize_str)
    

    #Create a new user grid with a single value for the user category (intermediate layer)
    #Convert User Value List into a list of integers
    intUserValueList = convertList(UserValueList)
    if len(intUserValueList) != 0:
        UserRemapRange = RemapRange([[min(intUserValueList), max(intUserValueList), 1]])
        UserSingleReclass = Reclassify(ExtractUserCat, "VALUE", UserRemapRange)
    
    #Create new Euclidean distance raster with a single value and NoData converted to 0(intermediate layer)
    EucRemapRange = RemapRange([[0, maxdist, 2], ["noData", "noData", 0]])
    EucReclass = Reclassify(outEucDistance, "VALUE", EucRemapRange)

    #Run Add Euclidean_Con and ForestSingle together - result: Value 1 = Core, Value 3 = Edge
    if len(intUserValueList) == 0:
        outPlus = EucReclass
    else:
        outPlus = Plus(UserSingleReclass, EucReclass)

    #Change NoData to 0 in CoreEdge raster in prep for final output raster (intermediate layer)
    UserRemapRange = RemapRange([[1,1,1], [3,3,3], ["NoData", "NoData", 0]])
    
    #ZeroedCE = Reclassify("CoreEdge_"+ m, "VALUE", UserRemapRange)
    ZeroedCE = Reclassify(outPlus, "VALUE", UserRemapRange)
    
    #Create new Water with a single value for water (intermediate layer)
    intWaterValueList = convertList(WaterValueList)
    WaterRemapRange = RemapRange([[min(intWaterValueList), max(intWaterValueList), 2], ["NoData", "NoData", 0]])
    H2OSingleReclass = Reclassify(ExtractWater, "VALUE", WaterRemapRange)

    #Create new Other with a single value for other (intermediate layer)
    intOtherValueList = convertList(OtherValueList)
    
    OtherRemapRange = RemapRange([[min(intOtherValueList), max(intOtherValueList), 4], ["NoData", "NoData", 0]])
    OtherSingleReclass = Reclassify(ExtractOther, "VALUE", OtherRemapRange)

    #Create Final Output Raster
    FinalOutputRas = CellStatistics([ZeroedCE, H2OSingleReclass, OtherSingleReclass], "SUM", "DATA")
    FinalRemapRange = RemapRange([[1,1,1],[2,2,2], [3,3,3], [4,4,4], [0,0,"NoData"]])
    FinalRaster = Reclassify(FinalOutputRas, "VALUE", FinalRemapRange)
    FinalRaster.save("CoreEdge_Final_" + m)
    
    arcpy.AddField_management(os.path.join(env.workspace, "CoreEdge_Final_"+ m), "POS", "TEXT", "#", "#", "10")
    updateValuestoRaster("CoreEdge_Final_" + m)
    print "Finished Core Edge Processing"
    ECOGrid = "CoreEdge_Final_" + m
    
    return ECOGrid

# Extracts land use values so that they can be temporary.
def ExtractLU(ValueList, inputLandcover):
    #Set up the values for the sql expression
    StrValuesList = convertList(ValueList)
    values = ",".join(StrValuesList)
    #Extract the  selected categories from the Landuse grid
    if values == "":
        values = "null"    
    attExtract = ExtractByAttributes(inputLandcover, "VALUE IN (" + values + ")")
    return attExtract
   
def convertList(inList):
    outList = []
    for l in inList:
        if type(l) is not int:
            outList.append(int(l))
        elif type(l) is int:
            outList.append(str(l))  
    return outList

def updateValuestoRaster(Raster):
    #Updates the POS field in the ForestCoreEdge with "Core" and "Edge" values
    rows = arcpy.UpdateCursor(Raster)
    row = rows.next()
    
    while row:
        #VALUE = 1 indicates a Core cell, Value = 3 is an Edge cell
        v = row.getValue("Value")
        if v == 1:
            row.POS = "Core"
        elif v == 3:
            row.POS = "Edge"
        elif v == 2:
            row.POS = "Water"
        elif v == 4:
            row.POS = "Other"
        rows.updateRow(row)
        row = rows.next()

def createPatchRaster(m,lccObj, lccClassesDict, inLandCoverGrid, fallBackDirectory, MaxSeperation, MinPatchSize, processingCellSize_str):

    import os

    # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area calculation    
    lccValuesDict = lccObj.values
    landCoverValues = arcpyutil.raster.getRasterValues(inLandCoverGrid)
    
    # get the grid codes for this specified metric
    UserValueList = lccClassesDict[m].uniqueValueIds.intersection(landCoverValues)
    
    # Generate the edge/core/other/excluded grid
    LCGrid = inLandCoverGrid
    
    #Extract User Categories from Land use grid
    env.workspace = os.path.dirname(LCGrid)
    inputLC = os.path.basename(LCGrid)
    
    #Extract User
    ExtractUserCat = ExtractLU(UserValueList, inputLC)
    
    #reset workspace to user defined output space (this is necessary because ArcGIS looks for the input landcover in
    #the workspace even if another path is called).


    TempOutspace =  fallBackDirectory
    env.workspace = TempOutspace
    
    #Create new User Grid with a single value for the user category(intermediate layer)
    intUserValueList = []
    
    #Convert Forest Value List into a list of integers
    intUserValueList = convertList(UserValueList)
    if len(intUserValueList) != 0:
        UserRemapRange = RemapRange([[min(intUserValueList), max(intUserValueList), 1]])
        UserSingle = Reclassify(ExtractUserCat, "Value", UserRemapRange)
    else:
        UserSingle = ExtractUserCat
    
    #Check to see if Maximum Separation > 0 if it is then skip to regions group analysis otherwise run
    #Euclidean distance
    if MaxSeperation == 0:
        #Run Regions group then run TabArea_FeatureLayer
        UserSingleRegionGroup = RegionGroup(UserSingle,"EIGHT","CROSS","ADD_LINK","")
        if MinPatchSize > 1:
            FinalPatchRas = ExtractByAttributes(UserSingleRegionGroup, "COUNT >" + str(MinPatchSize -1))
            FinalPatchRas.save("FinalPatches")
            return FinalPatchRas
        else:
            UserSingleRegionGroup.save("FinalPatches")
            return UserSingleRegionGroup


#        if "PatchMetrics" in AnalysisList:
#            tabulatePatchMetrics("FinalPatches")
#        if "MDCP" in AnalysisList:
#            tabulateMDCP("FinalPatches")
    else:
        #Calclulate Euclidean Distance based on max separation value
        gridcellsize_int = int(processingCellSize_str)
        maxSep = MaxSeperation * gridcellsize_int
        outEucDistance = EucDistance(UserSingle, maxSep, str(gridcellsize_int))

        #Extract only the max seperation value from the Euclidean distance
        EucDistanceExtract = ExtractByAttributes(outEucDistance, "VALUE = " + str(maxSep))
        EucDistanceExtract.save("EucDistance_MaxSep")

        #Reclassify Euclid distance so that NoData = 0
        EucDistReMapRange = RemapRange([[maxSep, maxSep, maxSep],["noData", "noData", 0]])
        EucDistReClass = Reclassify("EucDistance_MaxSep", "VALUE", EucDistReMapRange)

        #Reclassify  Single User Category Grid so that NoData = 0
        UserReMapRange = RemapRange([[1,1,1], ["noData", "noData", 0]])
        UserReClass = Reclassify(UserSingle, "VALUE", UserReMapRange)

        #Add (sum) UserReclass and EucDistanceReclass
        UserEuclidPlus = Plus(UserReClass, EucDistReClass)

        #Run Region Group analysis on UserEuclidPlus, ignores 0/NoData values
        UserEuclidRegionGroup = RegionGroup(UserEuclidPlus,"EIGHT","CROSS","ADD_LINK","0")

        #Reclass Euclid Reclass to -99999
        EucRcReMapRange = RemapRange([[maxSep, maxSep, -99999],[0, 0, 0]])
        EucReClass999 =Reclassify(EucDistReClass,"VALUE", EucRcReMapRange)

        #Add (sum) regions result to EucReClass999 result
        RegionEucPlus = Plus(UserEuclidRegionGroup,EucReClass999)    

        #Extract by Attribute Values greater than one to maintain the original boundaries of each patch
        RegionPatches = ExtractByAttributes(RegionEucPlus, "VALUE > 0")
        if MinPatchSize > 1:
            FinalPatchRas = ExtractByAttributes(RegionPatches, "COUNT >" + str(MinPatchSize -1))
            FinalPatchRas.save("FinalPatches")
            return FinalPatchRas
        else:
            RegionPatches.save("FinalPatches")
            return RegionPatches


#        if "PatchMetrics" in AnalysisList:
#            tabulatePatchMetrics("FinalPatches")
#        if "MDCP" in AnalysisList:
#            tabulateMDCP("FinalPatches", TempOutspace, ReportingUnitFeature, ReportingUnitField, SearchRadius)    
            
