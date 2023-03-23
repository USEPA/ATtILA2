""" Process NHD 24K for EnviroAtlas Analyses

    This script is associated with an ArcToolbox script tool.
"""

import sys
import os
import arcpy

from arcpy import env
from ATtILA2 import errors
from ATtILA2.utils import parameters, fields
from ATtILA2.datetimeutil import DateTimer

inputArguments = parameters.getParametersAsText([1,4])
processOption = inputArguments[0]
singleGdbWorkspace = inputArguments[1]
multiGdbFolder = inputArguments[2]
gdbFileFilter = inputArguments[3]
singleShpWorkspace = inputArguments[4]
multiShpFolder = inputArguments[5]
shpFileFilter = inputArguments[6]
outputLoc = inputArguments[7]
selectOptions = inputArguments[8]

arcpy.env.overwriteOutput = "True"
timer = DateTimer()
flist = []
nhdWorkspaces = list()

def processMultiMessage(integer):
    arcpy.AddMessage("Processing %s files." % integer)
    arcpy.AddMessage("For each file, the following steps will be performed: \n....")
    
    stepsMsg = '''
Create layer for NHDFlowline.
Select from NHDFlowline layer features with ftypes equal to StreamRiver or Connector. 
Copy selected features to output feature class. The suffix, "_strmLineNAP", will be appended to the filename.
Add NHDFlowline features with ArtificialPath ftype to the selected StreamRiver and Connector features.     
Copy selected NHDFlowline features to output feature class. The suffix, "_strmLine", will be appended to the filename.
Find line ends for selected NHDFlowline features.
Use NEAR to calculate distances between line ends.
Select nodes where the NEAR_DIST value <> 0. These are the terminal nodes.
Copy terminal nodes to intermediate output feature class. The suffix, "_strmEnds", will be appended to the filename.
Create layer for NHDArea.
Select from NHDArea layer features where the ftype = Wash.
Reduce the selected Washes to just those that are within 1 Meter of selected NHDflowlines
Add NHDArea features with ftypes equal to StreamRiver, Rapids, or Lock Chamber features to the selected Washes.
Create layer for NHDWaterbody.
Select from NHDWaterbody layer features with ftype equal to Reservoir, LakePond, or Ice Mass.
Reduce the selected NHDWaterbody features to just those that are within 1 Meter of selected NHDflowlines.
Merge the selected NHDArea features with the selected NHDWaterbody features.
Add field, "tmp_diss", to the merged feature class attribute table and set its value to 1.
Dissolve the merged feature class using the "tmp_diss" field.
Perform a second dissolve on the dissolved feature class using the "tmp_diss" field.
Create layer for the merged and dissolved areal feature class.
Select from the merged and dissolved areal feature class, features that are within 1 Meter of derived terminal nodes.
Add to those features any additional merged and dissolved areal features that intersect the selected NHDFlowlines.
Copy selected merged and dissolved areal features to output feature class. The suffix, "_strmAreal", will be appended to the filename.
.... 
'''
    
    arcpy.AddMessage(stepsMsg)

def checkOutputType(outputLoc):
    odsc = arcpy.Describe(outputLoc)
    # if output location is a folder then create a shapefile otherwise it will be a feature layer
    if odsc.DataType == "Folder":
        ext = ".shp"
    else:
        ext = ""
    return ext

    
def listdirs(rootdir, folderList, fileName):
    # Search all folders and subfolders to find the supplied file. 
    # Return a list with all the folder paths for any folder that contains the supplied file.
    shapefileFolder = "Not Found"
    for file in os.listdir(rootdir):
        if file != fileName:
            d = os.path.join(rootdir, file)
            if os.path.isdir(d):
                listdirs(d, folderList, fileName)
        else:        
            shapefileFolder = str(rootdir)
            folderList.append(shapefileFolder)
            break            
    return folderList

def main(_argv):
    from ATtILA2.utils.messages import loopProgress, AddMsg
    timer.start()
    
    try:
        # Until the Pairwise geoprocessing tools can be incorporated into ATtILA, disable the Parallel Processing Factor if the environment is set
        tempEnvironment0 = env.parallelProcessingFactor
        currentFactor = str(env.parallelProcessingFactor)
        if currentFactor == 'None' or currentFactor == '0':
            pass
        else:
            arcpy.AddWarning("ATtILA can produce unreliable data when Parallel Processing is enabled. Parallel Processing has been temporarily disabled.")
            env.parallelProcessingFactor = None
            
        ### COLLECT THE NAMES OF THE WORKSPACES TO PROCESS
        
        if processOption == "Single geodatabase":
            # The tool validation script ensures the singleGdbWorkspace has the required NHD files. No further processing is required. Add the workspace to the list to process.
            nhdWorkspaces = [singleGdbWorkspace]
            
        elif processOption == "Single shapefile":
            # The tool validation script ensures the singleShpWorkspace has the required NHD files. No further processing is required. Add the workspace to the list to process.
            folderList = []
            nhdWorkspaces = listdirs(singleShpWorkspace, folderList, "NHDArea.shp")
        
        elif processOption == "Multiple geodatabases":
            # The tool validation script is not able to check that the multiple geodatabases have the required NHD files. Perform the validation here.
            env.workspace = multiGdbFolder
            childWorkspaces = arcpy.ListWorkspaces(gdbFileFilter, "FileGDB")
            nhdWorkspaces = []
            nonNHDWorkspaces = []
            
            if len(childWorkspaces) == 0:
                AddMsg("No geodatabases beginning with %s found in %s. Please check the Geodatabase file filter string and the proper placement of any wildcard ('*') characters." % (gdbFileFilter, multiGdbFolder), 2)
            else:
                # Go thru each workspace and find the geodatabases where NHDArea is found. Keep a list of geodatabases where NHDArea is not found as well.
                for ws in childWorkspaces:
                    env.workspace = ws
                    fc = arcpy.ListFeatureClasses("*Area", "Polygon", "Hydrography")
                    
                    if len(fc) >= 1:
                        # NHDArea found. Add workspace to list for processing
                        nhdWorkspaces.append(ws)
                    else:
                        # NHDArea not found. Add workspace to list to alert user that this workspace will not be processed
                        nonNHDWorkspaces.append(ws)
                    
                if len(childWorkspaces) > len(nhdWorkspaces):
                    AddMsg("Found %s geodatabases in %s using the filter string '%s'. Only %s geodatabases contain all of the necessary NHD layers." % (len(childWorkspaces), multiGdbFolder, gdbFileFilter, len(nhdWorkspaces)), 1)
                    for nws in nonNHDWorkspaces:
                        AddMsg("%s was not processed" % (str(nws)), 1)
                else:
                    AddMsg("Found %s geodatabases in %s using the filter string '%s'. All %s subfolders contained the necessary NHD layers." % (len(childWorkspaces), multiGdbFolder, gdbFileFilter, len(nhdWorkspaces)))

        else: # Multiple shapefiles
            # The tool validation script is not able to check that the multiple geodatabases have the required NHD files. Perform the validation here.
            env.workspace = multiShpFolder
            childFolders = arcpy.ListWorkspaces(shpFileFilter, "Folder")
            nhdWorkspaces = []
            nonNHDFolders = []
            
            if len(childFolders) == 0:
                AddMsg("No folders beginning with %s found in %s. Please check the Shapefile folder filter string." % (shpFileFilter, multiShpFolder), 2)
            else:
                # Go thru each subfolder and find the folders where NHDArea.shp is found. Keep a list of folders where NHDArea.shp is not found as well.
                for f in childFolders:
                    folderList = []
                    folderList = listdirs(f, folderList, "NHDArea.shp")
                    if folderList:
                        # NHDArea.shp found. Add workspace to list for processing
                        nhdWorkspaces.extend(folderList)
                    else:
                        # NHDArea.shp not found. Add workspace to list to alert user that this workspace will not be processed
                        nonNHDFolders.append(str(f))

                if len(nhdWorkspaces) == 0:
                    AddMsg("Found %s folders in %s using the filter string '%s'. Did not find any folder with the required NHD feature files." % (len(childFolders), multiShpFolder, shpFileFilter), 2)
                elif len(childFolders) > len(nhdWorkspaces):
                    AddMsg("Found %s folders in %s using the filter string '%s'. Only %s subfolders contained all of the necessary NHD shapefiles." % (len(childFolders), multiShpFolder, shpFileFilter, len(nhdWorkspaces)), 1)
                    for f in nonNHDFolders:
                        AddMsg("%s was not processed." % (str(f)), 1)
                else:
                    AddMsg("Found %s folders in %s using the filter string '%s'. All %s subfolders contained the necessary NHD shapefiles." % (len(childFolders), multiShpFolder, shpFileFilter, len(nhdWorkspaces)))


        ### PROCESS THE WORKSPACES
        
        # Determine if input is a shapefile or a geodatabase feature class
        processType = processOption.split()[1][0:3]
        
        # Set initial variables
        env.workspace = outputLoc
        ext = checkOutputType(outputLoc)
        intermediateList = []
        saveIntermediates = "INTERMEDIATES" in selectOptions.split("  -  ")
        
        # Initialize custom progress indicator
        totalWS = len(nhdWorkspaces)
        loopProgress = loopProgress(totalWS)
        
        if totalWS > 1: processMultiMessage(totalWS)
            
        for ws in nhdWorkspaces:
            # Input Feature Classes
            if processType == 'geo':
                inWSDesc = arcpy.Describe(ws)
                wsBaseName = inWSDesc.baseName
                NHDFlowlineFC = ws + "\\Hydrography\\NHDFlowline"
                NHDWaterbodyFC = ws + "\\Hydrography\\NHDWaterbody"
                NHDAreaFC = ws + "\\Hydrography\\NHDArea"
            else:
                #if processOption == "Single geodatabase":
                if processOption == "Single shapefile":
                    wsBaseName = os.path.basename(singleShpWorkspace)
                else:
                    pathList = multiShpFolder.split(os.path.sep)
                    wsList = ws.split(os.path.sep)
                    nameIndex = len(pathList)
                    wsBaseName = wsList[nameIndex]
                    
                NHDFlowlineFC = ws + "\\NHDFlowline.shp"
                NHDWaterbodyFC = ws + "\\NHDWaterbody.shp"
                NHDAreaFC = ws + "\\NHDArea.shp"

            
            # Input Layer Names
            NHDFlowline_Layer = "NHDFlowline_Layer"
            NHDWaterbody_Layer = "NHDWaterbody_Layer"
            NHDArea_Layer = "NHDArea_Layer"
            
            # Output Feature Classes
            outStrmLineFC = wsBaseName+"_strmLine"+ext
            outStrmArealFC = wsBaseName+"_strmAreal"+ext
            outStrmLineNAPFC = wsBaseName+"_strmLineNAP"+ext
            
            # Intermediary Feature Classes
            outStrmEndsFC = wsBaseName+"_strmEnds"+ext
            intermediateList.append(outStrmEndsFC)
            mergeFCName = wsBaseName+"_Merge"+ext
            intermediateList.append(mergeFCName)
            
            # Determine if FTYPE field is a text or numeric field type
            ftypeField = fields.getFieldByName(NHDFlowlineFC, "ftype")
            
            # Process: Make NHDFlowline Feature Layer Without Artificial Paths
            if totalWS == 1: AddMsg("%s Creating layer for NHDFlowline..." % timer.now())
            arcpy.MakeFeatureLayer_management(NHDFlowlineFC, NHDFlowline_Layer, "", "", "")
            
            # Process: Select Layer By Attribute
            if totalWS == 1: AddMsg("%s Selecting StreamRiver and Connector features from NHDFlowline..." % timer.now())
            if ftypeField.type == "String":
                Expression = "\"FTYPE\" = '460' OR \"FTYPE\" = '334' OR \"FTYPE\" = 'StreamRiver' OR \"FTYPE\" = 'Connector'"
            else:
                Expression = "\"FTYPE\" = 460 OR \"FTYPE\" = 334"
                
            arcpy.SelectLayerByAttribute_management(NHDFlowline_Layer, "NEW_SELECTION", Expression)
                        
            # Process: Copy Features            
            if totalWS == 1: AddMsg("%s Copying selected features to %s" % (timer.now(), outStrmLineNAPFC))
            arcpy.CopyFeatures_management(NHDFlowline_Layer, outStrmLineNAPFC, "", "0", "0", "0")
            if totalWS == 1: flist.append(outStrmLineNAPFC)
            
            # Process: Select Layer By Attribute
            if totalWS == 1: AddMsg("%s Adding NHDFlowline features with ArtificialPath ftype to the selected StreamRiver and Connector features..." % timer.now())
            if ftypeField.type == "String":
                Expression = "\"FTYPE\" = '558' OR \"FTYPE\" = 'ArtificialPath'"
            else:
                Expression = "\"FTYPE\" = 558"
                
            arcpy.SelectLayerByAttribute_management(NHDFlowline_Layer, "ADD_TO_SELECTION", Expression)
                        
            # Process: Copy Features            
            if totalWS == 1: AddMsg("%s Copying selected NHDFlowline features to %s" % (timer.now(), outStrmLineFC))
            arcpy.CopyFeatures_management(NHDFlowline_Layer, outStrmLineFC, "", "0", "0", "0")
            if totalWS == 1: flist.append(outStrmLineFC)
            
            # Process: Feature Vertices To Points
            if totalWS == 1: AddMsg("%s Finding line ends for selected NHDFlowlines" % (timer.now()))
            strmEndsFC = "in_memory\\strmEnds"
            arcpy.FeatureVerticesToPoints_management(NHDFlowline_Layer, strmEndsFC, "BOTH_ENDS")
            
            # Process: Near
            if totalWS == 1: AddMsg("%s Using NEAR to calculate distances between line ends" % (timer.now()))
            arcpy.Near_analysis(strmEndsFC, strmEndsFC, "", "NO_LOCATION", "NO_ANGLE", "PLANAR")
            
            # Process: Make Feature Layer (2)
            NHDStrmEnds_Layer = "NHDStrmEnds_Layer"
            arcpy.MakeFeatureLayer_management(strmEndsFC, NHDStrmEnds_Layer, "", "", "ORIG_FID ORIG_FID VISIBLE NONE;NEAR_FID NEAR_FID VISIBLE NONE;NEAR_DIST NEAR_DIST VISIBLE NONE")
            
            # Process: Select Layer By Attribute (2)
            if totalWS == 1: AddMsg("%s Selecting terminal nodes (NEAR_DIST <> 0)" % (timer.now()))
            Expression = "\"NEAR_DIST\" <> 0"
            arcpy.SelectLayerByAttribute_management(NHDStrmEnds_Layer, "NEW_SELECTION", Expression)
            
            # Process: Delete Field (2)
            arcpy.DeleteField_management(strmEndsFC, "ORIG_FID;NEAR_FID")
            
            # Process: Copy Features (3)
            if totalWS == 1: AddMsg("%s Copying terminal nodes to %s" % (timer.now(), outStrmEndsFC))
            arcpy.CopyFeatures_management(NHDStrmEnds_Layer, outStrmEndsFC, "", "0", "0", "0")

            arcpy.Delete_management("in_memory")
            
            ## Processing NHDArea Polygons
            if totalWS == 1: AddMsg("%s Creating layer for NHDArea..." % timer.now())
            arcpy.MakeFeatureLayer_management(NHDAreaFC, NHDArea_Layer, "", "", "")
            
            # Process: Select Layer By Attribute (WASHES)
            if totalWS == 1: AddMsg("%s Selecting Wash features from NHDArea..." % timer.now())
            if ftypeField.type == "String":
                Expression = "\"FTYPE\" = '484' OR \"FTYPE\" = 'Wash'"
            else:
                Expression = "\"FTYPE\" = 484"
                
            arcpy.SelectLayerByAttribute_management(NHDArea_Layer, "NEW_SELECTION", Expression)
            
            # Process: Reduce the selection to those WASHES that are close to selected flowlines
            if totalWS == 1: AddMsg("%s Reducing the selected Washes to just those that are within 1 Meter of selected NHDflowlines..." % timer.now())
            arcpy.SelectLayerByLocation_management(NHDArea_Layer, "WITHIN_A_DISTANCE", outStrmLineFC, "1 Meters", "SUBSET_SELECTION", "NOT_INVERT")
            
            # Process: Add to the Washes Near Streams NHDArea polygons that are StreamRivers or Rapids or Lock Chambers
            if totalWS == 1: AddMsg("%s Adding NHDArea StreamRiver, Rapids, and Lock Chamber features to the selected Washes..." % timer.now())
            if ftypeField.type == "String":
                Expression = "\"FTYPE\" = '431' OR \"FTYPE\" = '460' OR \"FTYPE\" = '398' OR \"FTYPE\" = 'Rapids' OR \"FTYPE\" = 'StreamRiver' OR \"FTYPE\" = 'Lock Chamber'"
            else:
                Expression = "\"FTYPE\" = 431 OR \"FTYPE\" = 460 OR \"FTYPE\" = 398"
                
            arcpy.SelectLayerByAttribute_management(NHDArea_Layer, "ADD_TO_SELECTION", Expression)
            
            ## Processing NHDWaterbody Polygons
            if totalWS == 1: AddMsg("%s Creating layer for NHDWaterbody..." % timer.now())
            arcpy.MakeFeatureLayer_management(NHDWaterbodyFC, NHDWaterbody_Layer, "", "", "")
            
            # Process: Select NHDWaterbodies whose FTYPE = Reservoir or LakePond or Ice_Mass
            if totalWS == 1: AddMsg("%s Selecting Reservoir, LakePond, and Ice Mass features from NHDWaterbody..." % timer.now())
            if ftypeField.type == "String":
                Expression = "\"FTYPE\" = '436' OR \"FTYPE\" = '390' OR \"FTYPE\" = '378' OR \"FTYPE\" = 'Reservoir' OR \"FTYPE\" = 'LakePond' OR \"FTYPE\" = 'Ice Mass'"
            else:
                Expression = "\"FTYPE\" = 436 OR \"FTYPE\" = 390 OR \"FTYPE\" = 378"
                
            arcpy.SelectLayerByAttribute_management(NHDWaterbody_Layer, "NEW_SELECTION", Expression)
            
            # Process: Reduce the selection to those waterbodies that are close to selected flowlines
            if totalWS == 1: AddMsg("%s Reducing the selected NHDWaterbody features to just those that are within 1 Meter of selected NHDflowlines..." % timer.now())
            arcpy.SelectLayerByLocation_management(NHDWaterbody_Layer, "WITHIN_A_DISTANCE", outStrmLineFC, "1 Meters", "SUBSET_SELECTION", "NOT_INVERT")
            
            # Process: Merge
            if totalWS == 1: AddMsg("%s Merging the selected NHDArea features with the selected NHDWaterbody features to %s..." % (timer.now(), mergeFCName))
            arcpy.Merge_management("NHDArea_Layer;NHDWaterbody_Layer", mergeFCName, "")
            
            # Process: Add Field
            if totalWS == 1: AddMsg("%s Adding field, 'tmp_diss', to %s and setting its value to 1..." % (timer.now(), mergeFCName))
            arcpy.AddField_management(mergeFCName, "tmp_diss", "SHORT", "1", "", "", "", "NULLABLE", "NON_REQUIRED", "")
            
            # Process: Calculate Field
            arcpy.CalculateField_management(mergeFCName, "tmp_diss", 1)
            
            # Process: Dissolve
            dissolve1FCName = wsBaseName+"_Dissolve"+ext
            if totalWS == 1: AddMsg("%s Dissolving %s using the 'tmp_diss' field. Output: %s" % (timer.now(), mergeFCName, dissolve1FCName))
            arcpy.Dissolve_management(mergeFCName, dissolve1FCName, "tmp_diss", "", "SINGLE_PART", "DISSOLVE_LINES")
            intermediateList.append(dissolve1FCName)
            
            # Process: Dissolve (2)
            dissolve2FCName = wsBaseName+"_ReDissolve"+ext
            if totalWS == 1: AddMsg("%s Performing a second dissolve using the 'tmp_diss' field. Output: %s" % (timer.now(), dissolve2FCName))
            arcpy.Dissolve_management(dissolve1FCName, dissolve2FCName, "tmp_diss", "", "SINGLE_PART", "DISSOLVE_LINES")
            intermediateList.append(dissolve2FCName)
            
            # Process: Make Feature Layer
            if totalWS == 1: AddMsg("%s Creating layer for merged and dissolved areal features..." % timer.now())
            strmAreal_Layer = "strmAreal_Layer"
            arcpy.MakeFeatureLayer_management(dissolve2FCName, strmAreal_Layer, "", "", "tmp_diss tmp_diss VISIBLE NONE")
            
            # Process: Select Layer By Location (3)
            if totalWS == 1: AddMsg("%s Selecting merged and dissolved areal features that are within 1 Meter of terminal nodes of %s..." % (timer.now(), outStrmLineFC))
            arcpy.SelectLayerByLocation_management(strmAreal_Layer, "WITHIN_A_DISTANCE", outStrmEndsFC, "1 Meters", "NEW_SELECTION", "NOT_INVERT")
            
            # Process: Select Layer By Location (5)
            if totalWS == 1: AddMsg("%s Adding to that selection any additional merged and dissolved areal features that intersect %s..." % (timer.now(), outStrmLineFC))
            arcpy.SelectLayerByLocation_management(strmAreal_Layer, "INTERSECT", outStrmLineFC, "", "ADD_TO_SELECTION", "NOT_INVERT")
            
            # Process: Copy Features
            if totalWS == 1: AddMsg("%s Copying selected merged and dissolved areal features to %s" % (timer.now(), outStrmArealFC))
            arcpy.CopyFeatures_management(strmAreal_Layer, outStrmArealFC, "", "0", "0", "0")
            if totalWS == 1: flist.append(outStrmArealFC)

            
            if saveIntermediates:
                intermediateList.remove(outStrmEndsFC)
                if totalWS == 1: flist.append(outStrmEndsFC)
            
            for (intermediateResult) in intermediateList:
                arcpy.Delete_management(intermediateResult)

            loopProgress.update()

        #For each layer in flist add them to ArcMap
        if totalWS == 1:            
            try:
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
        env.parallelProcessingFactor = tempEnvironment0
        
        for (intermediateResult) in intermediateList:
            arcpy.Delete_management(intermediateResult)
   
if __name__ == "__main__":
    main(sys.argv)