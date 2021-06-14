""" Identify Overlapping Polygons

    This script is associated with an ArcToolbox script tool.
"""

import sys
import arcpy
arcpy.env.overwriteOutput = "True"
from ATtILA2.utils import parameters
from ATtILA2.utils import polygons
from ATtILA2.constants import metricConstants
overlaplist = []
flist = []
nonoverlapGroupDict = {}
inputArguments = parameters.getParametersAsText([0])


database = inputArguments[0]
chkWalkable = inputArguments[1]
chkIntDens = inputArguments[2]
chkIAC = inputArguments[3]
outputLoc = inputArguments[4]

def checkOutputType(outputLoc):
    odsc = arcpy.Describe(outputLoc)
    # if output location is a folder then create a shapefile otherwise it will be a feature layer
    if odsc.DataType == "Folder":
        ext = ".shp"
    else:
        ext = ""
    return ext

def main(_argv):
    #Script arguments
    try:
        metricConst = metricConstants.pnfeaConstants()
        NAVTEQ_LandUseA = database + "\\LandUseA"
        intersectFromLandUseA = "intersectFromLandUseA"
        NAVTEQ_LandUseB = database + "\\LandUseB"
        NAVTEQ_featureLayer = database + "\\Streets"
        intermediateList = []

        if chkWalkable == "true" or chkIntDens == "true":

            streetLayer = "streetLayer"

            arcpy.MakeFeatureLayer_management(NAVTEQ_featureLayer, streetLayer)
            arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', 
                                                    "FUNC_CLASS NOT IN ('1','2')")
            arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', 
                                                    "FERRY_TYPE <> 'H'")

            arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', 
                                                    "SPEED_CAT IN ('1', '2', '3')")
            arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', 
                                                    "AR_PEDEST = 'N'")
            # Write the selected features to a new feature class
            arcpy.CopyFeatures_management(streetLayer, metricConst.outNameRoadsWalkable)
        if chkIntDens == "true":


            arcpy.Identity_analysis(metricConst.outNameRoadsWalkable, NAVTEQ_LandUseA, intersectFromLandUseA)
            intermediateList.append(intersectFromLandUseA)
            arcpy.Identity_analysis(intersectFromLandUseA, NAVTEQ_LandUseB, metricConst.outNameRoadsIntDens)

            sql = "FEAT_TYPE = '' And FEAT_TYPE_1 <> ''"
            Relevant_Fields = ['FEAT_TYPE', 'FEAT_TYPE_1']

            #Transfer all meaningful values from field FEAT_TYPE_1 to FEAT_TYPE
            with arcpy.da.UpdateCursor(metricConst.outNameRoadsIntDens,Relevant_Fields,sql) as cursor:
                for row in cursor:
                    row[0] = row[1]
                    cursor.updateRow(row)
            #remove airports, amusement parks, beaches, cemeteries, hospitals, industrial complexes, military bases, railyards, shopping centers, and golf course if they have no street name value (ST_NAME)
        
            #values of attribute FEAT_TYPE in LanduseA:
            #PARK (CITY/COUNTY),900 	
            #SEAPORT/HARBOUR,686
            #ANIMAL PARK,229
            #RAILYARD,196		remove
            #CEMETERY,116		remove
            #HOSPITAL,69		remove
            #PARK (STATE),54
            #UNIVERSITY/COLLEGE,29
            #MILITARY BASE,3	remove
            #SHOPPING CENTRE,2	remove
            #SPORTS COMPLEX

            #values of attribute FEAT_TYPE in LanduseB:
            #GOLF COURSE		remove

            sql2 = "FEAT_TYPE IN ('CEMETERY', 'SHOPPING CENTRE', 'RAILYARD','HOSPITAL','MILITARY BASE','GOLF COURSE') And ST_NAME = ''"
            with arcpy.da.UpdateCursor(metricConst.outNameRoadsIntDens, ["*"], sql2) as cursor:
                for row in cursor:
                    cursor.deleteRow()
            addedField = "Merge_Class"
            arcpy.AddField_management(metricConst.outNameRoadsIntDens,addedField,"SHORT")
            arcpy.CalculateField_management(metricConst.outNameRoadsIntDens,addedField,1)
            sql3 = "DIR_TRAVEL = 'B'"
            with arcpy.da.UpdateCursor(metricConst.outNameRoadsIntDens, [addedField], sql3) as cursor:
                for row in cursor:
                    row[0] = 0
                    cursor.updateRow(row)
            if chkWalkable != "true":
                intermediateList.append(metricConst.outNameRoadsWalkable)
        if chkIAC == "true":
            streetLayer = "streetLayer"

            arcpy.MakeFeatureLayer_management(NAVTEQ_featureLayer, streetLayer)
            arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', 
                                                    "FUNC_CLASS IN ('1','2','3','4')")
            arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', 
                                                    "FERRY_TYPE <> 'H'")


            # Write the selected features to a new feature class
            arcpy.CopyFeatures_management(streetLayer, metricConst.outNameRoadsIAC)
            addedFieldLANES = "LANES"
            arcpy.AddField_management(metricConst.outNameRoadsIAC,addedFieldLANES,"DOUBLE")
            calcExpression = "!TO_LANES!+!FROM_LANES!"
            arcpy.CalculateField_management(metricConst.outNameRoadsIAC,addedFieldLANES,calcExpression,"PYTHON",'#')

            #add a warning of the total number of features having LANES of value 0
            whereClause_0Lanes = addedFieldLANES + " = 0"
            arcpy.Select_analysis(metricConst.outNameRoadsIAC, metricConst.value0_LANES, whereClause_0Lanes)
            arcpy.AddWarning("Total number of records where the LANES field = 0 is: "+ arcpy.GetCount_management(metricConst.value0_LANES).getOutput(0))
            intermediateList.append(metricConst.value0_LANES)

    except Exception as e:
        errors.standardErrorHandling(e)
 
    finally:
        for (intermediateResult) in intermediateList:
            arcpy.Delete_management(intermediateResult)
   
if __name__ == "__main__":
    main(sys.argv)