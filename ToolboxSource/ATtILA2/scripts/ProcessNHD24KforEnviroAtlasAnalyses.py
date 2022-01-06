""" Process NHD 24K for EnviroAtlas Analyses

    This script is associated with an ArcToolbox script tool.
"""

import sys
import arcpy

from arcpy import env
from ATtILA2 import errors
from ATtILA2.utils import parameters
from ATtILA2.datetimeutil import DateTimer

inputArguments = parameters.getParametersAsText([1,4])
processOption = inputArguments[0]
gdbWorkspace = inputArguments[1]
folderWorkspace = inputArguments[2]
fileFilter = inputArguments[3]
outputLoc = inputArguments[4]
selectOptions = inputArguments[5]
#outPrefix = inputArguments[5]


arcpy.env.overwriteOutput = "True"
timer = DateTimer()
flist = []
nhdWorkspaces = list()


def checkOutputType(outputLoc):
    odsc = arcpy.Describe(outputLoc)
    # if output location is a folder then create a shapefile otherwise it will be a feature layer
    if odsc.DataType == "Folder":
        ext = ".shp"
    else:
        ext = ""
    return ext

def main(_argv):
    from ATtILA2.utils.messages import loopProgress, AddMsg
    timer.start()
    
    try:
        # Collect the names of the geodatabases to process
        if processOption == "Single":
            nhdWorkspaces = [gdbWorkspace]
        else:
            env.workspace = folderWorkspace
            nhdWorkspaces = arcpy.ListWorkspaces(fileFilter+"*", "FileGDB")
        
        # Set initial variables
        env.workspace = outputLoc
        ext = checkOutputType(outputLoc)
        intermediateList = []
        saveIntermediates = "INTERMEDIATES" in selectOptions.split("  -  ")
        
        # Initialize custom progress indicator
        totalWS = len(nhdWorkspaces)
        loopProgress = loopProgress(totalWS)
            
        for ws in nhdWorkspaces:
            inWSDesc = arcpy.Describe(ws)
            wsBaseName = inWSDesc.baseName
            hucID = wsBaseName[6:10]

            # Input Feature Classes
            NHDFlowlineFC = ws + "\\Hydrography\\NHDFlowline"
            NHDWaterbodyFC = ws + "\\Hydrography\\NHDWaterbody"
            NHDAreaFC = ws + "\\Hydrography\\NHDArea"
            
            # Input Layer Names
            NHDFlowline_Layer = "NHDFlowline_Layer"
            NHDWaterbody_Layer = "NHDWaterbody_Layer"
            NHDArea_Layer = "NHDArea_Layer"
            
            # Output Feature Classes
            #strmLineFCName = outPrefix+"strmLine"+hucID+ext
            outStrmLineFC = wsBaseName+"_strmLine"+ext
            outStrmArealFC = wsBaseName+"_strmAreal"+ext
            
            # Intermediary Feature Classes
            outStrmEndsFC = wsBaseName+"_strmEnds"+ext
            intermediateList.append(outStrmEndsFC)
            mergeFCName = wsBaseName+"_Merge"+ext
            intermediateList.append(mergeFCName)
            
            
            # Process: Make NHDFlowline Feature Layer
            if processOption == "Single": AddMsg("%s Creating layer for NHDFlowline..." % timer.now())
            arcpy.MakeFeatureLayer_management(NHDFlowlineFC, NHDFlowline_Layer, "", "", "")
            
            # Process: Select Layer By Attribute
            if processOption == "Single": AddMsg("%s Selecting StreamRiver, Connector, and ArtificialPath features from NHDFlowline..." % timer.now())
            Expression = "\"FTYPE\" = 460 OR \"FTYPE\" = 334 OR \"FTYPE\" = 558"   
            arcpy.SelectLayerByAttribute_management(NHDFlowline_Layer, "NEW_SELECTION", Expression)
                        
            # Process: Copy Features            
            if processOption == "Single": AddMsg("%s Copying selected features to %s" % (timer.now(), outStrmLineFC))
            arcpy.CopyFeatures_management(NHDFlowline_Layer, outStrmLineFC, "", "0", "0", "0")
            if processOption == "Single": flist.append(outStrmLineFC)
            
            # Process: Feature Vertices To Points
            if processOption == "Single": AddMsg("%s Finding line ends for selected NHDFlowlines" % (timer.now()))
            strmEndsFC = "in_memory\\strmEnds"
            arcpy.FeatureVerticesToPoints_management(NHDFlowline_Layer, strmEndsFC, "BOTH_ENDS")
            
            # Process: Near
            if processOption == "Single": AddMsg("%s Using NEAR to calculate distances between line ends" % (timer.now()))
            arcpy.Near_analysis(strmEndsFC, strmEndsFC, "", "NO_LOCATION", "NO_ANGLE", "PLANAR")
            
            # Process: Make Feature Layer (2)
            NHDStrmEnds_Layer = "NHDStrmEnds_Layer"
            arcpy.MakeFeatureLayer_management(strmEndsFC, NHDStrmEnds_Layer, "", "", "ORIG_FID ORIG_FID VISIBLE NONE;NEAR_FID NEAR_FID VISIBLE NONE;NEAR_DIST NEAR_DIST VISIBLE NONE")
            
            # Process: Select Layer By Attribute (2)
            if processOption == "Single": AddMsg("%s Selecting terminal nodes (NEAR_DIST <> 0)" % (timer.now()))
            Expression = "\"NEAR_DIST\" <> 0"
            arcpy.SelectLayerByAttribute_management(NHDStrmEnds_Layer, "NEW_SELECTION", Expression)
            
            # Process: Delete Field (2)
            arcpy.DeleteField_management(strmEndsFC, "ORIG_FID;NEAR_FID")
            
            # Process: Copy Features (3)
            if processOption == "Single": AddMsg("%s Copying terminal nodes to %s" % (timer.now(), outStrmEndsFC))
            arcpy.CopyFeatures_management(NHDStrmEnds_Layer, outStrmEndsFC, "", "0", "0", "0")

            arcpy.Delete_management("in_memory")
            
            ## Processing NHDArea Polygons
            if processOption == "Single": AddMsg("%s Creating layer for NHDArea..." % timer.now())
            arcpy.MakeFeatureLayer_management(NHDAreaFC, NHDArea_Layer, "", "", "")
            
            # Process: Select Layer By Attribute (WASHES)
            if processOption == "Single": AddMsg("%s Selecting Wash features from NHDArea..." % timer.now())
            Expression = "\"FTYPE\" = 484"
            arcpy.SelectLayerByAttribute_management(NHDArea_Layer, "NEW_SELECTION", Expression)
            
            # Process: Reduce the selection to those WASHES that are close to selected flowlines
            if processOption == "Single": AddMsg("%s Reducing the selected Washes to just those that are within 1 Meter of selected NHDflowlines..." % timer.now())
            arcpy.SelectLayerByLocation_management(NHDArea_Layer, "WITHIN_A_DISTANCE", outStrmLineFC, "1 Meters", "SUBSET_SELECTION", "NOT_INVERT")
            
            # Process: Add to the Washes Near Streams NHDArea polygons that are StreamRivers or Rapids or Lock Chambers
            if processOption == "Single": AddMsg("%s Adding NHDArea StreamRiver, Rapids, and Lock Chamber features to the selected Washes..." % timer.now())
            Expression = "\"FTYPE\" = 431 OR \"FTYPE\" = 460 OR \"FTYPE\" = 398"
            arcpy.SelectLayerByAttribute_management(NHDArea_Layer, "ADD_TO_SELECTION", Expression)
            
            ## Processing NHDWaterbody Polygons
            if processOption == "Single": AddMsg("%s Creating layer for NHDWaterbody..." % timer.now())
            arcpy.MakeFeatureLayer_management(NHDWaterbodyFC, NHDWaterbody_Layer, "", "", "")
            
            # Process: Select NHDWaterbodies whose FTYPE = Reservoir or LakePond or Ice_Mass
            if processOption == "Single": AddMsg("%s Selecting Reservoir, LakePond, and Ice Mass features from NHDWaterbody..." % timer.now())
            Expression = "\"FTYPE\" = 436 OR \"FTYPE\" = 390 OR \"FTYPE\" = 378"
            arcpy.SelectLayerByAttribute_management(NHDWaterbody_Layer, "NEW_SELECTION", Expression)
            
            # Process: Reduce the selection to those waterbodies that are close to selected flowlines
            if processOption == "Single": AddMsg("%s Reducing the selected NHDWaterbody features to just those that are within 1 Meter of selected NHDflowlines..." % timer.now())
            arcpy.SelectLayerByLocation_management(NHDWaterbody_Layer, "WITHIN_A_DISTANCE", outStrmLineFC, "1 Meters", "SUBSET_SELECTION", "NOT_INVERT")
            
            # Process: Merge
            if processOption == "Single": AddMsg("%s Merging the selected NHDArea features with the selected NHDWaterbody features to %s..." % (timer.now(), mergeFCName))
            arcpy.Merge_management("NHDArea_Layer;NHDWaterbody_Layer", mergeFCName, "")
            
            # Process: Add Field
            if processOption == "Single": AddMsg("%s Adding field, 'tmp_diss', to %s and setting its value to 1..." % (timer.now(), mergeFCName))
            arcpy.AddField_management(mergeFCName, "tmp_diss", "SHORT", "1", "", "", "", "NULLABLE", "NON_REQUIRED", "")
            
            # Process: Calculate Field
            arcpy.CalculateField_management(mergeFCName, "tmp_diss", 1)
            
            # Process: Dissolve
            dissolve1FCName = wsBaseName+"_Dissolve"+ext
            if processOption == "Single": AddMsg("%s Dissolving %s using the 'tmp_diss' field. Output: %s" % (timer.now(), mergeFCName, dissolve1FCName))
            arcpy.Dissolve_management(mergeFCName, dissolve1FCName, "tmp_diss", "", "SINGLE_PART", "DISSOLVE_LINES")
            intermediateList.append(dissolve1FCName)
            
            # Process: Dissolve (2)
            dissolve2FCName = wsBaseName+"_ReDissolve"+ext
            if processOption == "Single": AddMsg("%s Performing a second dissolve using the 'tmp_diss' field. Output: %s" % (timer.now(), dissolve2FCName))
            arcpy.Dissolve_management(dissolve1FCName, dissolve2FCName, "tmp_diss", "", "SINGLE_PART", "DISSOLVE_LINES")
            intermediateList.append(dissolve2FCName)
            
            # Process: Make Feature Layer
            if processOption == "Single": AddMsg("%s Creating layer for merged and dissolved areal features..." % timer.now())
            strmAreal_Layer = "strmAreal"+hucID+"_Layer"
            arcpy.MakeFeatureLayer_management(dissolve2FCName, strmAreal_Layer, "", "", "tmp_diss tmp_diss VISIBLE NONE")
            
            # Process: Select Layer By Location (3)
            if processOption == "Single": AddMsg("%s Selecting merged and dissolved areal features that are within 1 Meter of terminal nodes of %s..." % (timer.now(), outStrmLineFC))
            arcpy.SelectLayerByLocation_management(strmAreal_Layer, "WITHIN_A_DISTANCE", outStrmEndsFC, "1 Meters", "NEW_SELECTION", "NOT_INVERT")
            
            # Process: Select Layer By Location (5)
            if processOption == "Single": AddMsg("%s Adding to that selection any additional merged and dissolved areal features that intersect %s..." % (timer.now(), outStrmLineFC))
            arcpy.SelectLayerByLocation_management(strmAreal_Layer, "INTERSECT", outStrmLineFC, "", "ADD_TO_SELECTION", "NOT_INVERT")
            
            # Process: Copy Features
            if processOption == "Single": AddMsg("%s Copying selected merged and dissolved areal features to %s" % (timer.now(), outStrmArealFC))
            arcpy.CopyFeatures_management(strmAreal_Layer, outStrmArealFC, "", "0", "0", "0")
            if processOption == "Single": flist.append(outStrmArealFC)
            
            # if processOption == "Single": AddMsg("%s Deleting %s, %s, and %s" % (timer.now(), dissolve1FCName, dissolve2FCName, mergeFCName))
            # arcpy.Delete_management([dissolve1FCName, dissolve2FCName, mergeFCName])
            
            if saveIntermediates:
                intermediateList.remove(outStrmEndsFC)
            
            for (intermediateResult) in intermediateList:
                arcpy.Delete_management(intermediateResult)

            loopProgress.update()
            
        try:
            #For each layer in flist add them to ArcMap
            if processOption == "Single":
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