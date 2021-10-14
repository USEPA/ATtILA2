""" Process NAVTEQ for EnviroAtlas Analyses

    This script is associated with an ArcToolbox script tool.
"""

import sys
import time
import arcpy
from arcpy import env
arcpy.env.overwriteOutput = "True"

from ATtILA2 import errors
from ATtILA2.utils import parameters
from ATtILA2.constants import metricConstants
from ATtILA2.utils.messages import AddMsg
from ATtILA2.datetimeutil import DateTimer

flist = []
inputArguments = parameters.getParametersAsText([0])


database = inputArguments[0]
chkWalkable = inputArguments[1]
chkIntDens = inputArguments[2]
chkIAC = inputArguments[3]
outputLoc = inputArguments[4]
prefix = inputArguments[5]

env.workspace = outputLoc

def checkOutputType(outputLoc):
    odsc = arcpy.Describe(outputLoc)
    # if output location is a folder then create a shapefile otherwise it will be a feature layer
    if odsc.DataType == "Folder":
        ext = ".shp"
    else:
        ext = ""
    return ext

def main(_argv):
    timer = DateTimer()
    timer.start()
    time.sleep(1) # A small pause is needed here between quick successive timer calls
    
    #Script arguments
    try:
        ext = checkOutputType(outputLoc)
        metricConst = metricConstants.pnfeaConstants()
        NAVTEQ_LandUseA = database + "\\LandUseA"       
        intersectFromLandUseA = "intersectFromLandUseA"+ext
        intersectFromLandUseAB = "intersectFromLandUseAB"+ext
        NAVTEQ_LandUseB = database + "\\LandUseB"
        NAVTEQ_featureLayer = database + "\\Streets"
        singlepartRoads = "singlepartRoads"+ext
        intermediateList = []
        
        keepFields = [f.name for f in arcpy.ListFields(NAVTEQ_featureLayer)]
        newFields = ["FEAT_TYPE", "MergeClass", "LANES"]
        keepFields.extend(newFields)

        if chkWalkable == "true" or chkIntDens == "true":
            if chkWalkable == "true":
                AddMsg(timer.split()+" Processing walkable roads...")
            else:
                AddMsg(timer.split()+" Processing roads for intersection density analysis...")
                
            walkableFCName = prefix+metricConst.outNameRoadsWalkable+ext

            streetLayer = "streetLayer"

            arcpy.MakeFeatureLayer_management(NAVTEQ_featureLayer, streetLayer)
            AddMsg("From "+NAVTEQ_featureLayer+"...")
            AddMsg("...selecting features where FUNC_CLASS <> 1 or 2")
            arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', 
                                                    "FUNC_CLASS NOT IN ('1','2')")
            AddMsg("...removing from the selection features where FERRY_TYPE <> H")
            arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', 
                                                    "FERRY_TYPE <> 'H'")
            AddMsg("...removing from the selection features where SPEED_CAT = 1, 2, or 3")
            arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', 
                                                    "SPEED_CAT IN ('1', '2', '3')")
            AddMsg("...removing from the selection features where AR_PEDEST = N")
            arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', 
                                                    "AR_PEDEST = 'N'")
            
            if chkWalkable == "true":
                # Write the selected features to a new feature class
                AddMsg("...copying remaining selected features to "+walkableFCName)
                arcpy.CopyFeatures_management(streetLayer, walkableFCName)
                flist.append(walkableFCName)
                
        if chkIntDens == "true":
            if chkWalkable == "true":
                AddMsg(timer.split()+" Processing roads for intersection density analysis...")
                AddMsg("Continuing with the selected features...")
            
            intDensityFCName = prefix+metricConst.outNameRoadsIntDens+ext
            
            AddMsg("...assigning landUseA codes to road segments")
            arcpy.Identity_analysis(streetLayer, NAVTEQ_LandUseA, intersectFromLandUseA)
            intermediateList.append(intersectFromLandUseA)

            AddMsg("...assigning landUseB codes to road segments")           
            arcpy.Identity_analysis(intersectFromLandUseA, NAVTEQ_LandUseB, intersectFromLandUseAB)
            intermediateList.append(intersectFromLandUseAB)

            if ext == ".shp":
                # fieldname size restrictions with shapefiles cause FEAT_TYPE_1 to be truncated to FEAT_TYP_1 
                sql = "FEAT_TYPE = '' And FEAT_TYP_1 <> ''"
                Relevant_Fields = ['FEAT_TYPE', 'FEAT_TYP_1']
            else:
                sql = "FEAT_TYPE = '' And FEAT_TYPE_1 <> ''"
                Relevant_Fields = ['FEAT_TYPE', 'FEAT_TYPE_1']

            #Transfer all meaningful values from field FEAT_TYPE_1 to FEAT_TYPE
            with arcpy.da.UpdateCursor(intersectFromLandUseAB,Relevant_Fields,sql) as cursor:
                for row in cursor:
                    row[0] = row[1]
                    cursor.updateRow(row)
                    
            #Eliminate all fields except those found in the NAVTEQ Streets layer and those needed for this script (FEAT_TYPE, MergeClass, and LANES)
            dropFields = [f.name for f in arcpy.ListFields(intersectFromLandUseAB) if f.name not in keepFields]
            AddMsg("...trimming unnecessary fields")
            arcpy.DeleteField_management(intersectFromLandUseAB, dropFields)
            
            
            #remove airports, amusement parks, beaches, cemeteries, hospitals, industrial complexes, military bases, railyards, shopping centers, and golf course if they have no street name value (ST_NAME)
        
            #values of attribute FEAT_TYPE in LanduseA:
            #AIRPORT              remove
            #AMUSEMENT PARK       remove
            #ANIMAL PARK
            #BEACH                remove
            #CEMETERY,116         remove
            #HOSPITAL,69          remove
            #INDUSTRIAL COMPLEX   remove
            #MILITARY BASE,3      remove
            #PARK (CITY/COUNTY),900 
            #PARK (STATE),54
            #PARK IN WATER
            #PARK/MONUMENT (NATIONAL)
            #RAILYARD,196         remove	
            #SEAPORT/HARBOUR,686
            #SHOPPING CENTRE,2    remove
            #SPORTS COMPLEX
            #UNIVERSITY/COLLEGE,29   

            #values of attribute FEAT_TYPE in LanduseB:
            #AIRCRAFT ROADS
            #GOLF COURSE		            remove
            #NATIVE AMERICAN RESERVATION
            

            AddMsg("...removing roads with no street names from the following land use type areas: \n"+
                   "...    AIRPORT, AMUSEMENT PARK, ANIMAL PARK, BEACH, CEMETERY, HOSPITAL, \n"+
                   "...    INDUSTRIAL COMPLEX, MILITARY BASE, PARK (CITY/COUNTY/STATE), RAILYARD, \n"+
                   "...    SHOPPING CENTRE, or GOLF COURSE")
            
            landUseSet = "'AIRPORT',"\
            "'AMUSEMENT PARK',"\
            "'ANIMAL PARK',"\
            "'BEACH',"\
            "'CEMETERY',"\
            "'HOSPITAL',"\
            "'INDUSTRIAL COMPLEX',"\
            "'MILITARY BASE',"\
            "'PARK (CITY/COUNTY)',"\
            "'PARK (STATE)',"\
            "'RAILYARD',"\
            "'SHOPPING CENTRE',"\
            "'GOLF COURSE'"
            
            sql2 = "FEAT_TYPE IN ("+landUseSet+") And ST_NAME = ''"
            with arcpy.da.UpdateCursor(intersectFromLandUseAB, ["*"], sql2) as cursor:
                for row in cursor:
                    cursor.deleteRow()
                    
            AddMsg("...adding a MergeClass field")
            mergeField = "MergeClass"
            arcpy.AddField_management(intersectFromLandUseAB,mergeField,"SHORT")
            
            AddMsg("...setting MergeClass field value to an initial value of 1")
            arcpy.CalculateField_management(intersectFromLandUseAB,mergeField,1)
            
            AddMsg("...replacing MergeClass field value to 0 where DIR_TRAVEL = 'B'")
            sql3 = "DIR_TRAVEL = 'B'"
            with arcpy.da.UpdateCursor(intersectFromLandUseAB, [mergeField], sql3) as cursor:
                for row in cursor:
                    row[0] = 0
                    cursor.updateRow(row)
                    
            AddMsg("...converting any multipart roads to singlepart")
            # Ensure the road feature class is comprised of singleparts. Multipart features will cause MergeDividedRoads to fail.
            arcpy.MultipartToSinglepart_management(intersectFromLandUseAB, singlepartRoads)
            intermediateList.append(singlepartRoads)
            
            # Merge roads to final output
            AddMsg("...merging divided roads to "+intDensityFCName+" using the MergeClass field and a merge distance of '30 Meters' \n"+
                   "...    Only roads with the same value in the mergeField and within the mergeDistance will be merged. \n"+
                   "...    Roads with a MergeClass value equal to zero are locked and will not be merged. \n"+
                   "...    All non-merged roads are retained.")
            arcpy.MergeDividedRoads_cartography(singlepartRoads, mergeField, "30 Meters", intDensityFCName)
                                
            flist.append(intDensityFCName)

        if chkIAC == "true":
            AddMsg(timer.split()+" Processing interstates, arterials, and connectors...")
            
            iacFCName = prefix+metricConst.outNameRoadsIAC+ext
            streetLayer = "streetLayer"

            arcpy.MakeFeatureLayer_management(NAVTEQ_featureLayer, streetLayer)
            AddMsg("From "+NAVTEQ_featureLayer+"...")
            AddMsg("...selecting features where FUNC_CLASS = 1, 2, 3, or 4")
            arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', 
                                                    "FUNC_CLASS IN ('1','2','3','4')")
            AddMsg("...removing from the selection features where FERRY_TYPE <> H")
            arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', 
                                                    "FERRY_TYPE <> 'H'")


            # Write the selected features to a new feature class
            AddMsg("...copying remaining selected features to "+iacFCName)
            arcpy.CopyFeatures_management(streetLayer, iacFCName)
            
            addedFieldLANES = "LANES"
            arcpy.AddField_management(iacFCName,addedFieldLANES,"DOUBLE")
            AddMsg("...added field named, LANES, to table. Calculating its value as TO_LANES + FROM_LANES")
            calcExpression = "!TO_LANES!+!FROM_LANES!"
            arcpy.CalculateField_management(iacFCName,addedFieldLANES,calcExpression,"PYTHON",'#')

            #inform the user the total number of features having LANES of value 0
            value0FCName = metricConst.value0_LANES+ext
            whereClause_0Lanes = addedFieldLANES + " = 0"
            arcpy.Select_analysis(iacFCName, value0FCName, whereClause_0Lanes)
            AddMsg("Total number of records where the LANES field = 0 is: "+ arcpy.GetCount_management(value0FCName).getOutput(0))

            intermediateList.append(value0FCName)
            
            flist.append(iacFCName)
            
        try:
            #For each layer in flist add them to ArcMap
            for f in flist:
                p = arcpy.mp.ArcGISProject("CURRENT")
                m = p.activeMap
                m.addDataFromPath(outputLoc + "\\"+f)
    
            arcpy.AddMessage("Adding processed layer(s) to view")
            arcpy.AddMessage("The files have been saved to " + outputLoc)
        except:
            arcpy.AddMessage("The files have been saved to " + outputLoc)

    except Exception as e:
        errors.standardErrorHandling(e)
 
    finally:
        for (intermediateResult) in intermediateList:
            arcpy.Delete_management(intermediateResult)
   
if __name__ == "__main__":
    main(sys.argv)