""" Utilities specific to rasters

"""
import arcpy
from arcpy.sa import *
from pylet import arcpyutil

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


def getEdgeCoreGrid(m, lccObj, lccClassesDict, inLandCoverGrid, PatchEdgeWidth, fallBackDirectory):
    # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area calculation    
    lccValuesDict = lccObj.values
    
    # get the grid codes for this specified metric
    UserValueList = lccClassesDict[m].uniqueValueIds
    
    # get the frozenset of excluded values (i.e., values not to use when calculating the reporting unit effective area)
    WaterValueList = lccValuesDict.getExcludedValueIds()
    
    LandValueList = lccValuesDict.getIncludedValueIds()
    
    OtherValueList = LandValueList - UserValueList
   
    
    from arcpy import env
    import os
    TempOutspace =  arcpyutil.environment.getWorkspaceForIntermediates(fallBackDirectory) 
    arcpy.AddMessage(WaterValueList)
    arcpy.AddMessage(LandValueList)
    arcpy.AddMessage(UserValueList)
    arcpy.AddMessage(OtherValueList)
    
    # Generate the edge/core/other/excluded grid
#    LCGrid = Raster(inLandCoverGrid)
    LCGrid = inLandCoverGrid
    
    #Extract User Categories from Landuse grid
    env.workspace = os.path.dirname(LCGrid)
    inputLC = os.path.basename(LCGrid)

    ExtractDict = {}
    ExtractDict["ExtractUserCat"]= UserValueList
    ExtractDict["ExtractWater"] = WaterValueList
    ExtractDict["ExtractOther"] = OtherValueList
    #Extract User, Water, and Other 
    for k in ExtractDict.keys():
        outputgrid = k
        #Set up the values for the sql expression
        StrValuesList = convertList(ExtractDict[k])
        values = ",".join(StrValuesList)
        #Extract the  selected categories from the Landuse grid
        attExtract = ExtractByAttributes(inputLC, "VALUE IN (" + values + ")")
        attExtract.save(os.path.join(TempOutspace, outputgrid))
    
    #Extract Non User Categories from Landuse grid
    outputNUgrid = "ExtractNonUser"
    StrValuesList = convertList(ExtractDict["ExtractUserCat"])
    values = ",".join(StrValuesList)
    attExtract = ExtractByAttributes(inputLC, "VALUE NOT IN (" + values +")")
    attExtract.save(os.path.join(TempOutspace, outputNUgrid))
    
    #change workspace to output space
    env.workspace = TempOutspace
    
    #Calculate the Euclidean distance using the NonUser
    gridcellsize = getRasterGridSize(outputNUgrid) 
    arcpy.AddMessage(gridcellsize)
    maxdist = PatchEdgeWidth * gridcellsize
    arcpy.AddMessage("MaxDist =" + str(maxdist))
    outEucDistance = EucDistance(outputNUgrid, maxdist, str(gridcellsize))
    outEucDistance.save("outEucDistance")
#    #Create a new user grid with a single value for the user category (intermediate layer)
#    #Convert User Value List into a list of integers
#    intUserValueList = convertList(UserValueList)
#    
#    UserRemapRange = RemapRange([[min(intUserValueList), max(intUserValueList), 1]])
#    UserSingleReclass = Reclassify("ExtractUserCat", "VALUE", UserRemapRange)
#    UserSingleReclass.save("UserSingleReclass")
#    
#    #Create new Euclidean distance raster with a single value and NoData converted to 0(intermediate layer)
#    EucRemapRange = RemapRange([[0, maxdist, 2], ["noData", "noData", 0]])
#    EucReclass = Reclassify(outEucDistance, "VALUE", EucRemapRange)
#    EucReclass.save("EucReclass")
#    #Run Add Euclidean_Con and ForestSingle together - result: Value 1 = Core, Value 3 = Edge
#    outPlus = Plus(UserSingleReclass, EucReclass)
#    outPlus.save("CoreEdge")
#    
#    #Add Pos field to CoreEdge raster and populate it
#    arcpy.AddField_management(os.path.join(env.workspace, "CoreEdge"), "POS", "TEXT", "#", "#", "10")
#    updateValuestoRaster("CoreEdge")
#
#    #Change NoData to 0 in CoreEdge raster in prep for final output raster (intermediate layer)
#    UserRemapRange = RemapRange([[1,1,1], [3,3,3], ["NoData", "NoData", 0]])
#    ZeroedCE = Reclassify("CoreEdge", "VALUE", UserRemapRange)
#    ZeroedCE.save("ZeroedCE")
#    #Create new Water with a single value for water (intermediate layer)
#    intWaterValueList = convertList(WaterValueList)
#    
#    WaterRemapRange = RemapRange([[min(intWaterValueList), max(intWaterValueList), 2], ["NoData", "NoData", 0]])
#    H2OSingleReclass = Reclassify("ExtractWater", "VALUE", WaterRemapRange)
#    H2OSingleReclass.save("H2OSingleReclass")
#    #Create new Other with a single value for other (intermediate layer)
#    intOtherValueList = convertList(OtherValueList)
#    
#    OtherRemapRange = RemapRange([[min(intOtherValueList), max(intOtherValueList), 4], ["NoData", "NoData", 0]])
#    OtherSingleReclass = Reclassify("ExtractOther", "VALUE", OtherRemapRange)
#    OtherSingleReclass.save("OtherSingleReclass")
#    #Create Final Output Raster
#    FinalOutputRas = CellStatistics([ZeroedCE, H2OSingleReclass, OtherSingleReclass], "SUM", "DATA")
#    FinalRemapRange = RemapRange([[1,1,1],[2,2,2], [3,3,3], [4,4,4], [0,0,"NoData"]])
#    FinalRaster = Reclassify(FinalOutputRas, "VALUE", FinalRemapRange)
#    FinalRaster.save("CoreEdge_Final")
#    
#    arcpy.AddField_management(os.path.join(env.workspace, "CoreEdge_Final"), "POS", "TEXT", "#", "#", "10")
#    updateValuestoRaster("CoreEdge_Final")
    
    ECOGrid = LCGrid
    
    return ECOGrid

def getRasterGridSize(Landcovergrid):

    #Get the cell size for the land use grid
    XBand = arcpy.GetRasterProperties_management(Landcovergrid, "CELLSIZEX" )
    YBand = arcpy.GetRasterProperties_management(Landcovergrid, "CELLSIZEY")
    #Check to make sure the grid size are square if it is not generate an error
    if int(float(str(XBand))) == int(float(str(YBand))):
        return int(float(str(XBand)))
    else:
        arcpy.AddError("Uh oh the grids are not square!!! X Band Value will only be used")  
        
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