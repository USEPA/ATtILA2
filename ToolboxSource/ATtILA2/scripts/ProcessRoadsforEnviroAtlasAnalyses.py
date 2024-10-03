""" Process Roads for EnviroAtlas Analyses

    This script is associated with an ArcToolbox script tool.
"""
# Work on this tomorrow tryin Don's style with user defined database and then an if statements using metric constants. Start wtih streetmaps first!
import sys
import arcpy
from arcpy import env
arcpy.env.overwriteOutput = "True"

from ATtILA2 import errors
from ATtILA2.utils import parameters
from ATtILA2.utils import calculate
from ATtILA2.constants import metricConstants
from ATtILA2.utils.messages import AddMsg
from ATtILA2.datetimeutil import DateTimer
from ATtILA2.utils import log
from datetime import datetime

# set up a list for feature class names to add to the ArcGIS Project's TOC
flist = []

inputArguments = parameters.getParametersAsText()

versionName = inputArguments[0] #Change everything in the following code to match this and hopefully work
inStreetsgdb = inputArguments[1]
chkWalkableYN = inputArguments[2]
chkIntDensYN = inputArguments[3]
chkIACYN = inputArguments[4]
outWorkspace = inputArguments[5]
fnPrefix = inputArguments[6] 
optionalFieldGroups = inputArguments[7] # Logfile will be an option here
env.workspace = outWorkspace
toolPath = __file__ # This can be used for when scripts are run from a stand-alone script and not from metric.py

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
    
    #Script arguments
    try:
        # Until the Pairwise geoprocessing tools can be incorporated into ATtILA, disable the Parallel Processing Factor if the environment is set
        tempEnvironment0 = env.parallelProcessingFactor
        currentFactor = str(env.parallelProcessingFactor)
        if currentFactor == 'None' or currentFactor == '0':
            pass
        else:
            arcpy.AddWarning("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.")
            env.parallelProcessingFactor = None
        
        ext = checkOutputType(outWorkspace)
        
        metricConst = metricConstants.prfeaConstants()

        parametersList = [versionName, inStreetsgdb, chkWalkableYN, chkIntDensYN, chkIACYN, outWorkspace, fnPrefix, optionalFieldGroups] #check this last one with logfile in the tool

        logFile = log.setupLogFile(optionalFieldGroups, metricConst, parametersList, outWorkspace+"\\"+fnPrefix, toolPath) #toolPath?
        AddMsg(f"{timer.start()} Setting up initial environment variables", 0, logFile)

        # setup additional metric constants
        inputStreets = inStreetsgdb + "\\Streets"
        singlepartRoads = "singlepartRoads"+ext
        intermediateList = []
        keepFields = [f.name for f in arcpy.ListFields(inputStreets)]
        newFields = ["FEATURE_TYPE", "FEAT_TYPE", "MergeClass", "LANES"]
        keepFields.extend(newFields)
        intersectFinal = "intersectFinal"+ext

        #NAVTEQ 2011 Options 
        NAVTEQ_LandUseA = inStreetsgdb + "\\LandUseA"       
        intersectFromLandUseA = "intersectFromLandUseA"+ext
        NAVTEQ_LandUseB = inStreetsgdb + "\\LandUseB"
        
        #NAVTEQ 2019 Options
        NAVTEQLandArea = inStreetsgdb + "\\MapLanduseArea"
        NAVTEQFacilityArea = inStreetsgdb + "\\MapFacilityArea"
        link = inStreetsgdb + "\\Link"
        intersectFromLandArea = "intersectFromLandUse"+ext
        
        #StreetMapOptions
        SMLandArea = inStreetsgdb + "\\MapLandArea\\MapLandArea"
        
        # Begin process by making a feature layer from the Streets feature class
        AddMsg(f"{timer.now()} Creating feature layer from {inputStreets}", 0, logFile)
        streetLayer = "streetLayer"
        arcpy.MakeFeatureLayer_management(inputStreets, streetLayer)

        
        if chkWalkableYN == "true" or chkIntDensYN == "true":
            if chkWalkableYN == "true":
                AddMsg(f"{timer.now()} Processing walkable roads", 0, logFile)
            else:
                AddMsg(f"{timer.now()} Processing roads for intersection density analysis", 0, logFile)
            
            if versionName == 'NAVTEQ 2011': #NAVTEQ 2011
                whereClause = metricConst.WlkSelectNAV11
                WlkMsg = metricConst.WlkMsgNAV11
                
                # OLD NAVTEQ SELECTION FOR ENVIROATLAS
                # AddMsg("From "+inputStreets+"...")
                # AddMsg("...selecting features where FUNC_CLASS <> 1 or 2")
                # arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', 
                #                                         "FUNC_CLASS NOT IN ('1','2')")
                # AddMsg("...removing from the selection features where FERRY_TYPE <> H")
                # arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', 
                #                                         "FERRY_TYPE <> 'H'")
                # AddMsg("...removing from the selection features where SPEED_CAT = 1, 2, or 3")
                # arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', 
                #                                         "SPEED_CAT IN ('1', '2', '3')")
                # AddMsg("...removing from the selection features where AR_PEDEST = N")
                # arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', 
                #                                         "AR_PEDEST = 'N'")
            
            elif versionName == 'NAVTEQ 2019': #NAVTEQ 2019
                whereClause = metricConst.WlkSelectNAV19
                WlkMsg = metricConst.WlkMsgNAV19
            
            elif versionName == 'ESRI StreetMap': #StreetMaps
                whereClause = metricConst.WlkSelectSM
                WlkMsg = metricConst.WlkMsgSM
                
            arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', whereClause, "INVERT")
            AddMsg(f"{timer.now()} {WlkMsg}", 0, logFile)

            if chkWalkableYN == "true":
                walkableFCName = fnPrefix+metricConst.outNameRoadsWalkable+ext
                AddMsg(f"{timer.now()} Saving selected features to: {walkableFCName}", 0, logFile)
                arcpy.CopyFeatures_management(streetLayer, walkableFCName)
                flist.append(walkableFCName)
                

        if chkIntDensYN == "true":
            # get the output feature class name
            intDensityFCName = fnPrefix+metricConst.outNameRoadsIntDens+ext
            mergeField = "MergeClass"
            
            if chkWalkableYN == "true":
                AddMsg(f"{timer.now()} Continuing intersection density processing with the selected features", 0, logFile)
        
            AddMsg(f"{timer.now()} Removing from the selection features where {metricConst.speedCatDict[versionName]}", 0, logFile)
            arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', metricConst.speedCatDict[versionName])
            
            if versionName == 'NAVTEQ 2011': #NAVTEQ 2011
                AddMsg(f"{timer.now()} Assigning landUseA codes to road segments", 0, logFile)
                arcpy.Identity_analysis(streetLayer, NAVTEQ_LandUseA, intersectFromLandUseA)
                intermediateList.append(intersectFromLandUseA)

                AddMsg(f"{timer.now()} Assigning landUseB codes to road segments", 0, logFile)           
                arcpy.Identity_analysis(intersectFromLandUseA, NAVTEQ_LandUseB, intersectFinal)
                intermediateList.append(intersectFinal)

                if ext == ".shp":
                    # fieldname size restrictions with shapefiles cause FEAT_TYPE_1 to be truncated to FEAT_TYP_1 
                    sql = "FEAT_TYPE = '' And FEAT_TYP_1 <> ''"
                    Relevant_Fields = ['FEAT_TYPE', 'FEAT_TYP_1']
                else:
                    sql = "FEAT_TYPE = '' And FEAT_TYPE_1 <> ''"
                    Relevant_Fields = ['FEAT_TYPE', 'FEAT_TYPE_1']

                #Transfer all meaningful values from field FEAT_TYPE_1 to FEAT_TYPE
                with arcpy.da.UpdateCursor(intersectFinal,Relevant_Fields,sql) as cursor:
                    for row in cursor:
                        row[0] = row[1]
                        cursor.updateRow(row)
                
            elif versionName == 'NAVTEQ 2019':  #NAVTEQ 2019
                AddMsg(f"{timer.now()} Assigning landArea codes to road segments",0,logFile)
                arcpy.Identity_analysis(streetLayer, NAVTEQLandArea, intersectFromLandArea)
                intermediateList.append(intersectFromLandArea)

                AddMsg(f"{timer.now()} Assigning FacilityArea codes to road segments",0,logFile)           
                arcpy.Identity_analysis(intersectFromLandArea, NAVTEQFacilityArea, intersectFinal)
                intermediateList.append(intersectFinal)

                if ext == ".shp":
                    # fieldname size restrictions with shapefiles cause FEAT_TYPE_1 to be truncated to FEAT_TYP_1 
                    sql = "FEATURE_TY = 0 And FEATURE_1 <> 0" # Not sure how this is truncated? FIGURE THIS OUT TOMORROW 9/12
                    Relevant_Fields = ['FEATURE_TY', 'FEATURE_1']
                else:
                    sql = "FEATURE_TY = 0 And FEATURE_1 <> 0" # Ask Don why this line of code!
                    Relevant_Fields = ['FEATURE_TY', 'FEATURE_1']

                #Transfer all meaningful values from field FEAT_TYPE_1 to FEAT_TYPE
                with arcpy.da.UpdateCursor(intersectFinal, Relevant_Fields, sql) as cursor:
                    for row in cursor:
                        row[0] = row[1]
                        cursor.updateRow(row)
            
            elif versionName == 'ESRI StreetMap': # ESRI StreetMaps
                AddMsg(f"{timer.now()} Assigning MapLandArea codes to road segments",0,logFile)
                arcpy.Identity_analysis(streetLayer, SMLandArea, intersectFinal)
                intermediateList.append(intersectFinal)

            # dropFields = [f.name for f in arcpy.ListFields(intersectFinal) if f.name not in keepFields]
            # AddMsg(f"{timer.now()} Trimming unnecessary fields",0,logFile)
            # arcpy.DeleteField_management(intersectFinal, dropFields)  #THIS SET OF CODE SLOWS THINGS DOWN A LOT

            AddMsg(f"{timer.now()} Removing roads with no street names from the following land use type areas: AIRPORT, AMUSEMENT PARK, BEACH, CEMETERY, HOSPITAL, INDUSTRIAL COMPLEX, MILITARY BASE, RAILYARD, SHOPPING CENTER, or GOLF COURSE", 0, logFile)
            unnamedStreetsSQL = metricConst.unnamedStreetsDict[versionName]
            with arcpy.da.UpdateCursor(intersectFinal, ["*"], unnamedStreetsSQL) as cursor:
                for row in cursor:
                    cursor.deleteRow()
            
            AddMsg(f"{timer.now()} Adding a MergeClass field",0,logFile)
            arcpy.AddField_management(intersectFinal,mergeField,"SHORT")
        
            AddMsg(f"{timer.now()} Setting MergeClass to an initial value of 1", 0, logFile)
            arcpy.CalculateField_management(intersectFinal,mergeField,1)
            
            dirTravelSQL = metricConst.dirTravelDict[versionName]
            dirTravelFld = dirTravelSQL.split(' = ')[0]
            AddMsg(f"{timer.now()} Replacing MergeClass value to 0 for rows where {dirTravelFld} = 'B'", 0, logFile)
            with arcpy.da.UpdateCursor(intersectFinal, [mergeField], dirTravelSQL) as cursor:
                for row in cursor:
                    row[0] = 0
                    cursor.updateRow(row)
        
            AddMsg(f"{timer.now()} Converting any multipart roads to singlepart", 0, logFile)
            # Ensure the road feature class is comprised of singleparts. Multipart features will cause MergeDividedRoads to fail.
            arcpy.MultipartToSinglepart_management(intersectFinal, singlepartRoads)
            intermediateList.append(singlepartRoads)
            AddMsg(f"{timer.now()} Merging divided roads to {intDensityFCName} using the MergeClass field and a merge distance of '30 Meters'. Only roads with the same value in the mergeField and within the mergeDistance will be merged. Roads with a MergeClass value equal to zero are locked and will not be merged. All non-merged roads are retained.", 
                   0, logFile)
            
            arcpy.MergeDividedRoads_cartography(singlepartRoads, mergeField, "30 Meters", intDensityFCName)                    
            AddMsg(f"{timer.now()} Finished processing {intDensityFCName}", 0, logFile)
            flist.append(intDensityFCName)
            

        if chkIACYN == "true":
            AddMsg(f"{timer.now()} Processing {inputStreets} for interstates, arterials, and connectors", 0, logFile)
            # get the name for the output feature class
            iacFCName = fnPrefix+metricConst.outNameRoadsIAC+ext
            lanesField = "LANES"
            ToFromFields = metricConst.laneFieldDict[versionName]
            
            if chkWalkableYN == "true" or chkIntDensYN == "true":
                # this is probably unnecessary, but it makes sure everything is reset
                AddMsg(f"{timer.now()} Clearing all selections on {inputStreets}")
                arcpy.SelectLayerByAttribute_management(streetLayer, 'CLEAR_SELECTION')

            if versionName == 'NAVTEQ 2011':
                AddMsg(f"{timer.now()} Selecting features where FUNC_CLASS = 1, 2, 3, or 4",0,logFile)
                arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', "FUNC_CLASS IN ('1','2','3','4')")
                AddMsg(f"{timer.now()} Removing from the selection features where FERRY_TYPE <> H",0,logFile)
                arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', "FERRY_TYPE <> 'H'")                
                
            elif versionName == 'NAVTEQ 2019': #NAVTEQ2019 #(pickup updating messages here) 
                #try running the join first
                arcpy.management.JoinField(inputStreets, metricConst.Streets_linkfield, link, metricConst.Link_linkfield, ToFromFields)
                AddMsg(f"{timer.now()} Adding {ToFromFields[0]} and {ToFromFields[1]} from Link feature", 0, logFile)
                AddMsg(f"{timer.now()} Selecting features where FuncClass = 1, 2, 3, or 4", 0, logFile)
                arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', "FuncClass <= 4")
                AddMsg(f"{timer.now()} Removing from the selection features where FERRY_TYPE <> H", 0, logFile)
                arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', "FerryType <> 'H'")                
            
            elif versionName == 'ESRI StreetMap': # ESRI StreetMaps
                AddMsg(f"{timer.now()} Selecting features where FuncClass = 1, 2, 3, or 4", 0, logFile)
                arcpy.SelectLayerByAttribute_management(streetLayer, 'NEW_SELECTION', "FuncClass <= 4")
                AddMsg(f"{timer.now()} Removing from the selection features where FERRY_TYPE <> H", 0, logFile)
                arcpy.SelectLayerByAttribute_management(streetLayer, 'REMOVE_FROM_SELECTION', "FerryType <> 'H'")            
            
            # Write the selected features to a new feature class
            AddMsg(f"{timer.now()} Copying remaining selected features to "+iacFCName, 0, logFile)
            arcpy.CopyFeatures_management(streetLayer, iacFCName)
        
            for f in ToFromFields:
                AddMsg(f"{timer.now()} Setting NULL values in {f} field to 0", 0, logFile)
                calculate.replaceNullValues(iacFCName, f, 0)
            
            arcpy.AddField_management(iacFCName,lanesField,"SHORT")
            AddMsg(f"{timer.now()} Added field, LANES, to {iacFCName}. Calculating its value as {ToFromFields[0]} + {ToFromFields[1]}", 0, logFile)
            calcExpression = f"!{ToFromFields[0]}!+!{ToFromFields[1]}!"
            arcpy.CalculateField_management(iacFCName,lanesField,calcExpression,"PYTHON",'#')
            
            AddMsg(f"{timer.now()} Finished processing {iacFCName}", 0, logFile)
                
            #inform the user the total number of features having LANES of value 0
            value0FCName = metricConst.value0_LANES+ext
            whereClause_0Lanes = lanesField + " = 0"
            arcpy.Select_analysis(iacFCName, value0FCName, whereClause_0Lanes)
            zeroCount = arcpy.GetCount_management(value0FCName).getOutput(0)
            if int(zeroCount) > 0:
                arcpy.AddWarning(f"Total number of records where LANES field = 0 in {iacFCName} is: {zeroCount}. Replacing LANES field value to 2 for these records. The user can locate and change these records with the following query: {ToFromFields[0]} = 0 And {ToFromFields[1]} = 0")
                
                #Change the LANES value to 2 where LANES = 0
                sql4 = "LANES = 0"
                with arcpy.da.UpdateCursor(iacFCName, [lanesField], sql4) as cursor:
                    for row in cursor:
                        row[0] = 2
                        cursor.updateRow(row)
            
            intermediateList.append(value0FCName)
            flist.append(iacFCName)
            
        
        try:
            #For each layer in flist add them to ArcMap
            for f in flist:
                p = arcpy.mp.ArcGISProject("CURRENT")
                m = p.activeMap
                m.addDataFromPath(outWorkspace + "\\"+f)
    
            AddMsg("Adding processed layer(s) to view") # Maybe skip this one for the logfile?
        except:
            AddMsg("Unable to add processed layer(s) to view")

    except Exception as e:
        errors.standardErrorHandling(e)
 
    finally:

        if logFile:
            log.writeEnvironments(logFile, None, None, inputStreets) # This is calculating based on input rather than output. Has the same conceptual issue as other ATtILA tools.
            logFile.write("\nEnded: {0}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            logFile.write("\n---End of Log File---\n")
            logFile.close()
            AddMsg('Log file closed')

        env.parallelProcessingFactor = tempEnvironment0
        
        for (intermediateResult) in intermediateList:
            arcpy.Delete_management(intermediateResult)
   
if __name__ == "__main__":
    main(sys.argv)