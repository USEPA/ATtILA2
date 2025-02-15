""" Utilities specific to vectors

"""

import os
import arcpy
from . import files
from . import messages
from .messages import AddMsg
from .fields import valueDelimiter
from arcpy.sa.Functions import SetNull
from .log import logArcpy
from arcpy import env
from os.path import basename


def bufferFeaturesByID(inFeatures, repUnits, outFeatures, bufferDist, ruIDField, ruLinkField, timer, logFile):
    """Returns a feature class that contains only those portions of each reporting unit that are within a buffered 
        distance of a layer - the buffered features may be any geometry
    **Description:**
        This tool intersects reporting units with buffered features that contain the reporting unit ID. The buffer size (in map 
        units) is determined by the user. A new feature class is created that can be used as a reporting unit theme to 
        calculate metrics near the features. It is useful for generating metrics near water quality sample points where 
        watersheds that drain to the sample point are available.
    **Arguments:**
        * *inFeatures* - feature class that will be buffered
        * *repUnits* - reporting units that will be used for the clip
        * *outFeatures* - a feature class (without full path) that will be created as the output of this tool
        * *bufferDist* - distance in the units of the spatial reference of the input data to buffer
        * *ruIDField* - a field that exists in repUnits that contains a unique identifier for the reporting units.  
        * *ruLinkField* - a field that exists in the inFeatures that contains reporting unit IDs, linking buffered features
                            to reporting units
        ' 'logFile' - optional file used to record processing steps
        
    **Returns:**
        * *outFeatures* - output feature class 
    """
    try:
        # Get a unique name with full path for the output features - will default to current workspace:
        outFeatures = arcpy.CreateScratchName(outFeatures,"","FeatureClass")
        
        # First perform a buffer on all the points with the specified distance.  
        # By using the "LIST" option and the unit ID field, the output contains a single multipart feature for every 
        # reporting unit.  The output is written to the user's scratch workspace.
        AddMsg(f"{timer.now()} Buffering input features: in_memory/bFeats", 0, logFile)
        bufferedFeatures = arcpy.Buffer_analysis(inFeatures,"in_memory/bFeats", bufferDist,"FULL","ROUND","LIST",ruLinkField)
        logArcpy(arcpy.Buffer_analysis, (inFeatures,"in_memory/bFeats", bufferDist,"FULL","ROUND","LIST",ruLinkField), "arcpy.Buffer_analysis", logFile) 
        
        # If the input features are polygons, we need to erase the the input polyons from the buffer output
        inGeom = arcpy.Describe(inFeatures).shapeType
        if inGeom == "Polygon":
            AddMsg(f"{timer.now()} Erasing polygon areas from buffer areas: in_memory/bFeats2", 0, logFile)
            newBufferFeatures = arcpy.Erase_analysis(bufferedFeatures,inFeatures,"in_memory/bFeats2")
            logArcpy(arcpy.Erase_analysis,(bufferedFeatures,inFeatures,"in_memory/bFeats2"), "arcpy.Erase_analysis", logFile)
            arcpy.Delete_management(bufferedFeatures)
            logArcpy(arcpy.Delete_management, (bufferedFeatures,), "arcpy.Delete_management", logFile)
            bufferedFeatures = newBufferFeatures
        
        # The script will be iterating through reporting units and using a whereclause to select each feature, so it will 
        # improve performance if we set up the right syntax for the whereclauses ahead of time.
        buffUnitID = arcpy.AddFieldDelimiters(bufferedFeatures,ruLinkField)
        repUnitID = arcpy.AddFieldDelimiters(repUnits,ruIDField)
        
        # Similarly, the syntax for the whereclause depends on the type of the reporting unit ID field. 
        delimitBuffValues = valueDelimiter(arcpy.ListFields(bufferedFeatures,ruLinkField)[0].type)
        delimitRUValues = valueDelimiter(arcpy.ListFields(repUnits,ruIDField)[0].type)

        # Get a count of the number of reporting units to give an accurate progress estimate.
        n = int(arcpy.GetCount_management(bufferedFeatures).getOutput(0))
        # Initialize custom progress indicator
        loopProgress = messages.loopProgress(n)

        i = 0 # Flag used to create the outFeatures the first time through.
        # Create a Search cursor to iterate through the reporting units with buffered features.
        Rows = arcpy.SearchCursor(bufferedFeatures,"","",ruLinkField)
        AddMsg(f"{timer.now()} Clipping buffered features to each reporting unit: {basename(outFeatures)}", 0, logFile)
        # For each reporting unit:
        for row in Rows:
            # Get the reporting unit ID
            rowID = row.getValue(ruLinkField)
            # Set up the whereclause for the buffered features and the reporting units to select one of each
            whereClausePts = f"{buffUnitID} = {delimitBuffValues(rowID)}"
            whereClausePolys = f"{repUnitID} = {delimitRUValues(rowID)}"
            
            # Create an in-memory Feature Layer with the whereclause.  This is analogous to creating a map layer with a 
            # definition expression.
            arcpy.MakeFeatureLayer_management(bufferedFeatures,"buff_lyr",whereClausePts)
            arcpy.MakeFeatureLayer_management(repUnits,"poly_lyr",whereClausePolys)
            if i == 0: # If it's the first time through
                # Clip the buffered points using the reporting unit boundaries, and save the output as the specified output
                # feature class.
                arcpy.Clip_analysis("buff_lyr","poly_lyr",outFeatures,"#")
                i = 1 # Toggle the flag.
            else: # If it's not the first time through and the output feature class already exists
                # Perform the clip, but output the result to memory rather than writing to disk
                clipResult = arcpy.Clip_analysis("buff_lyr","poly_lyr","in_memory/buff","#")
                # Append the in-memory result to the output feature class
                arcpy.Append_management(clipResult,outFeatures,"NO_TEST")
                # Delete the in-memory result to conserve system resources
                arcpy.Delete_management(clipResult)
            # Delete the in-memory Feature Layers.  
            arcpy.Delete_management("buff_lyr")
            arcpy.Delete_management("poly_lyr")
            loopProgress.update()
    
        return outFeatures
    
    finally:
        try:
            # Clean up the search cursor object
            del Rows
            # Delete the temporary buffered features layer from the scratch workspace.  
            arcpy.Delete_management(bufferedFeatures)
        except:
            pass


def bufferFeaturesByIntersect(inFeatures, repUnits, outFeatures, bufferDist, unitID, cleanupList, timer, logFile):
    """Returns a feature class that contains only those portions of each reporting unit that are within a buffered 
        distance of a layer - the buffered features may be any geometry
    **Description:**
        This tool intersects reporting units with buffered features that fall within the reporting unit. The buffer size (in map 
        units) is determined by the user. A new feature class is created that can be used as a reporting unit theme to 
        calculate metrics with the buffered areas. It is useful for generating metrics near streams that fall within the
        reporting unit.
        
        This tool makes the assumption that there is no attribute that links the features to be buffered with the 
        reporting units.  Because of this, it cannot buffer all the features at once - it must iterate through each
        reporting unit, first clipping features to the reporting unit boundaries, then buffering only those features
        and then finally clipping the buffers again to the reporting unit.  If the features can be linked to reporting
        units via an attribute, it should be faster to use the bufferFeaturesByID tool instead.
    **Arguments:**
        * *inFeatures* - one or more feature class that will be buffered
        * *repUnits* - reporting units that will be used for the clip
        * *outFeatures* - a feature class (without full path) that will be created as the output of this tool
        * *bufferDist* - distance in the units of the spatial reference of the input data to buffer
        * *unitID* - a field that exists in repUnits that contains a unique identifier for the reporting units. 
        * *cleanupList* - a list object for tracking intermediate datasets for cleanup at the user's request. 
        ' 'logFile' - optional file used to record processing steps
        
    **Returns:**
        * *outFeatures* - output feature class 
    """
    
    try:
        toolShortName = outFeatures[:outFeatures.find("_")]
        repUnitsName = arcpy.Describe(repUnits).baseName
        outFeatures = files.nameIntermediateFile([outFeatures,"FeatureClass"], cleanupList)
        
        # The tool accepts a semicolon-delimited list of input features - convert this into a python list object
        # it appears that long directory paths in the multivalue input box causes the delimiter to be quote-semicolon-quote
        # instead of just semicolon
        if "';'" in inFeatures:
            inFeatures = inFeatures.replace("';'",";")    
        if '";"' in inFeatures:
            inFeatures = inFeatures.replace('";"',";")
            
        inFeaturesList = inFeatures.split(";")
        outputList = []
        # Initialize list of polygon features for erase
        eraseList = []        
        
        for inFC in inFeaturesList:
            inFCDesc = arcpy.Describe(inFC)
            inFCName = inFCDesc.baseName
            if inFCDesc.shapeType == "Polygon":
                eraseList.append(inFC)
            
            if inFCDesc.HasM or inFCDesc.HasZ:
                copyFCNameBase = f"{toolShortName}_{inFCName}_"
                copyFCName = files.nameIntermediateFile([copyFCNameBase,"FeatureClass"], cleanupList)
                AddMsg(f"{timer.now()} Creating a copy of {inFCName} without M or Z values: {basename(copyFCName)}", 0, logFile)
                logArcpy(arcpy.FeatureClassToFeatureClass_conversion, (inFC, env.workspace, basename(copyFCName)), "arcpy.FeatureClassToFeatureClass_conversion", logFile)
                inFC = arcpy.FeatureClassToFeatureClass_conversion(inFC, env.workspace, basename(copyFCName))
                inFCDesc = arcpy.Describe(inFC)
                inFCName = inFCDesc.baseName

            inFCNamePrefix = f"{toolShortName}_{inFCName}"
            
            # Start by intersecting the input features and the reporting units 
            firstIntersectionName = files.nameIntermediateFile([f"{inFCNamePrefix}_intersect_","FeatureClass"], cleanupList)
            AddMsg(f"{timer.now()} Intersecting {inFCName} and reporting units. Intermediate: {basename(firstIntersectionName)}", 0, logFile)
            
            # If Parallel Processing Factor environment setting is enabled and there is no intersecting features between
            # the reporting units and the stream feature, the Intersect operation will fail. Skip to the next stream feature
            # when this occurs.
            try:
                intersectResult = arcpy.Intersect_analysis([repUnits,inFC],firstIntersectionName,"ALL","","INPUT")
                logArcpy(arcpy.Intersect_analysis, ([repUnits,inFC],firstIntersectionName,"ALL","","INPUT"), "arcpy.Intersect_analysis", logFile)
            except:
                AddMsg(f"No features of {inFCName} intersect with features of {repUnitsName}. Omitting {inFCName} from further processing.", 1, logFile)
                continue
            
            # Check for empty intersect features
            if not arcpy.SearchCursor(firstIntersectionName).next():
                AddMsg(f"No features of {inFCName} intersect with features of {repUnitsName}. Omitting {inFCName} from further processing.", 1, logFile)
                continue

            # We are later going to perform a second intersection with the reporting units layer, which will cause
            # a name collision with the reporting unitID field - in anticipation of this, rename the unitID field.
            # This functionality is dependent on the intermediate dataset being in a geodatabase - no shapefiles allowed.
            # It is also only available starting in 10.2.1, so also check the version number before proceeding
            # IF AlterField isn't an option, revert to add/calculate field methodology - slower and more clunky, but it works.
            newUnitID = arcpy.ValidateFieldName("new"+unitID, intersectResult) 
            gdbTest = arcpy.Describe(intersectResult).dataType
            arcVersion = arcpy.GetInstallInfo()['Version']
            if gdbTest == "FeatureClass" and arcVersion >= '10.2.1':
                arcpy.AlterField_management(intersectResult,unitID,newUnitID,newUnitID)
                logArcpy(arcpy.AlterField_management, (intersectResult,unitID,newUnitID,newUnitID), "arcpy.AlterField_management", logFile)
            else:
                # Get the properties of the unitID field
                fromFieldObj = arcpy.ListFields(intersectResult,unitID)[0]
                # Add the new field to the output table with the appropriate properties and the valid name
                arcpy.AddField_management(intersectResult,newUnitID,fromFieldObj.type,fromFieldObj.precision,fromFieldObj.scale,fromFieldObj.length,
                                          fromFieldObj.aliasName,fromFieldObj.isNullable,fromFieldObj.required,fromFieldObj.domain)
                logArcpy(arcpy.AddField_management, (intersectResult,newUnitID,fromFieldObj.type,fromFieldObj.precision,fromFieldObj.scale,
                          fromFieldObj.length,fromFieldObj.aliasName,fromFieldObj.isNullable,fromFieldObj.required,
                          fromFieldObj.domain), "arcpy.AddField_management", logFile)
                # Copy the field values from the old to the new field
                arcpy.CalculateField_management(intersectResult,newUnitID,arcpy.AddFieldDelimiters(intersectResult,unitID))
                logArcpy(arcpy.CalculateField_management, (intersectResult,newUnitID,arcpy.AddFieldDelimiters(intersectResult,unitID)), "arcpy.CalculateField_management", logFile)

            try:
                # Buffer these in-memory selected features and merge the output into multipart features by reporting unit ID
                bufferPrefix = f"{inFCNamePrefix}_buffer_"
                bufferName = files.nameIntermediateFile([bufferPrefix,"FeatureClass"],cleanupList)
                AddMsg(f"{timer.now()} Buffering intersected features. Intermediate: {basename(bufferName)}", 0, logFile)
                
                # If the input features are polygons, we need to erase the the input polygons from the buffer output
                inGeom = inFCDesc.shapeType
                if inGeom == "Polygon":
                    # When we buffer polygons, we want to exclude the area of the polygon itself.  This can be done using the 
                    # "OUTSIDE_ONLY" option in the buffer tool, but that is only available with an advanced license.  Check for
                    # the right license level, revert to buffer/erase option if it's not available.
                    licenseLevel = arcpy.CheckProduct("ArcInfo")
                    sysExecutable = arcpy.glob.os.path.basename(arcpy.sys.executable)
                    if licenseLevel in ["AlreadyInitialized","Available"] or sysExecutable.upper() == "PYTHON.EXE":
                        bufferResult = arcpy.Buffer_analysis(intersectResult,bufferName,bufferDist,"OUTSIDE_ONLY","ROUND","LIST",[newUnitID])
                        logArcpy(arcpy.Buffer_analysis, (intersectResult,bufferName,bufferDist,"OUTSIDE_ONLY","ROUND","LIST",[newUnitID]), "arcpy.Buffer_analysis", logFile)
                        AddMsg(f"{timer.now()} Repairing buffer areas for input areal features.", 0, logFile)
                        arcpy.RepairGeometry_management(bufferResult)
                        logArcpy(arcpy.RepairGeometry_management, (bufferResult,), "arcpy.RepairGeometry_management", logFile)
                    else:
                        bufferResult = arcpy.Buffer_analysis(intersectResult,bufferName,bufferDist,"FULL","ROUND","LIST",[newUnitID])
                        logArcpy(arcpy.Buffer_analysis, (intersectResult,bufferName,bufferDist,"FULL","ROUND","LIST",[newUnitID]), "arcpy.Buffer_analysis", logFile)
                        AddMsg(f"{timer.now()} Repairing buffer areas for input areal features.", 0, logFile)
                        arcpy.RepairGeometry_management(bufferResult)
                        logArcpy(arcpy.RepairGeometry_management, (bufferResult,), "arcpy.RepairGeometry_management", logFile)
                        bufferErase = files.nameIntermediateFile([f"{inFCNamePrefix}_bufferErase_","FeatureClass"],cleanupList)
                        AddMsg(f"{timer.now()} Erasing polygon areas from buffer areas. Intermediate: {basename(bufferErase)}", 0, logFile)
                        newBufferFeatures = arcpy.Erase_analysis(bufferResult,inFC,bufferErase)
                        logArcpy(arcpy.Erase_analysis, (bufferResult,inFC,bufferErase), "arcpy.Erase_analysis", logFile)
                        bufferResult = newBufferFeatures
                else:
                    bufferResult = arcpy.Buffer_analysis(intersectResult,bufferName,bufferDist,"FULL","ROUND","LIST",[newUnitID])
                    logArcpy(arcpy.Buffer_analysis, (intersectResult,bufferName,bufferDist,"FULL","ROUND","LIST",[newUnitID]), "arcpy.Buffer_analysis", logFile)
                    AddMsg(f"{timer.now()} Repairing buffer areas for input linear features.", 0, logFile)
                    arcpy.RepairGeometry_management(bufferResult)
                    logArcpy(arcpy.RepairGeometry_management, (bufferResult,), "arcpy.RepairGeometry_management", logFile)
            except:
                AddMsg(f"{timer.now()} BUFFER FAILED: Repairing geometry for {basename(firstIntersectionName)} and trying buffer again.", 1, logFile)
                arcpy.management.RepairGeometry(intersectResult)
                logArcpy(arcpy.management.RepairGeometry, (intersectResult,), "arcpy.management.RepairGeometry", logFile)

                inGeom = inFCDesc.shapeType
                if inGeom == "Polygon":
                    # When we buffer polygons, we want to exclude the area of the polygon itself.  This can be done using the 
                    # "OUTSIDE_ONLY" option in the buffer tool, but that is only available with an advanced license.  Check for
                    # the right license level, revert to buffer/erase option if it's not available.
                    licenseLevel = arcpy.CheckProduct("ArcInfo")
                    if licenseLevel in ["AlreadyInitialized","Available"]:
                        bufferResult = arcpy.Buffer_analysis(intersectResult,bufferName,bufferDist,"OUTSIDE_ONLY","ROUND","LIST",[newUnitID])
                        logArcpy(arcpy.Buffer_analysis, (intersectResult,bufferName,bufferDist,"OUTSIDE_ONLY","ROUND","LIST",[newUnitID]), "arcpy.Buffer_analysis", logFile)
                        AddMsg(f"{timer.now()} Repairing buffer areas for input areal features.", 0, logFile)
                        arcpy.RepairGeometry_management(bufferResult)
                        logArcpy(arcpy.RepairGeometry_management, (bufferResult,), "arcpy.RepairGeometry_management", logFile)
                    else:
                        bufferResult = arcpy.Buffer_analysis(intersectResult,bufferName,bufferDist,"FULL","ROUND","LIST",[newUnitID])
                        logArcpy(arcpy.Buffer_analysis, (intersectResult,bufferName,bufferDist,"FULL","ROUND","LIST",[newUnitID]), "arcpy.Buffer_analysis", logFile)
                        AddMsg(f"{timer.now()} Repairing buffer areas for input areal features.", 0, logFile)
                        arcpy.RepairGeometry_management(bufferResult)
                        logArcpy(arcpy.RepairGeometry_management, (bufferResult,), "arcpy.RepairGeometry_management", logFile)
                        bufferErase = files.nameIntermediateFile([f"{inFCName}_bufferErase_","FeatureClass"],cleanupList)
                        AddMsg(f"{timer.now()} Erasing polygon areas from buffer areas: {basename(bufferErase)}", 0, logFile)
                        newBufferFeatures = arcpy.Erase_analysis(bufferResult,inFC,bufferErase)
                        logArcpy(arcpy.Erase_analysis, (bufferResult,inFC,bufferErase), "arcpy.Erase_analysis", logFile)
                        bufferResult = newBufferFeatures
                else:
                    bufferResult = arcpy.Buffer_analysis(intersectResult,bufferName,bufferDist,"FULL","ROUND","LIST",[newUnitID])
                    logArcpy(arcpy.Buffer_analysis, (intersectResult,bufferName,bufferDist,"FULL","ROUND","LIST",[newUnitID]), "arcpy.Buffer_analysis", logFile)
                    AddMsg(f"{timer.now()} Repairing buffer areas for input linear features.".format(timer.now()), 0, logFile)
                    arcpy.RepairGeometry_management(bufferResult)
                    logArcpy(arcpy.RepairGeometry_management, (bufferResult,), "arcpy.RepairGeometry_management", logFile)
            
            # Intersect the buffers with the reporting units
            secondIntersectionName = files.nameIntermediateFile([f"{inFCNamePrefix}_2ndintersect_","FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Intersecting buffer features and reporting units. Intermediate: {basename(secondIntersectionName)}", 0, logFile)
            secondIntersectResult = arcpy.Intersect_analysis([repUnits,bufferResult],secondIntersectionName,"ALL","","INPUT")
            logArcpy(arcpy.Intersect_analysis, ([repUnits,bufferResult],secondIntersectionName,"ALL","","INPUT"), "arcpy.Intersect_analysis", logFile)            

            # # Select only those intersected features whose reporting unit IDs match 
            # # This ensures that buffer areas that fall outside of the input feature's reporting unit are excluded
            # if len(inFeaturesList) > 1:
            #     finalOutputName = files.nameIntermediateFile([inFCNamePrefix+"_final_","FeatureClass"],cleanupList)
            # else: 
            #     finalOutputName = outFeatures # If this is the only one, it's already named.
            #
            # AddMsg(f"{timer.now()} Trimming buffer zones to reporting unit boundaries. Intermediate: {basename(finalOutputName)}", 0, logFile)    
            # whereClause = arcpy.AddFieldDelimiters(secondIntersectResult,unitID) + " = " + arcpy.AddFieldDelimiters(secondIntersectResult,newUnitID)
            # finalOutput = logArcpy(arcpy.MakeFeatureLayer_management, (secondIntersectResult,finalOutputName,whereClause), "arcpy.MakeFeatureLayer_management", logFile)
            #
            # # keep track of list of outputs.  
            # outputList.append(finalOutput)


            # Select only those intersected features whose reporting unit IDs match 
            # This ensures that buffer areas that fall outside of the input feature's reporting unit are excluded
            AddMsg(f"{timer.now()} Trimming buffer zones to reporting unit boundaries", 0, logFile)
            whereClause = arcpy.AddFieldDelimiters(secondIntersectResult,unitID) + " = " + arcpy.AddFieldDelimiters(secondIntersectResult,newUnitID)
            matchingBuffers = arcpy.MakeFeatureLayer_management(secondIntersectResult,"matchingBuffers",whereClause)
            logArcpy(arcpy.MakeFeatureLayer_management, (secondIntersectResult,"matchingBuffers",whereClause), "arcpy.MakeFeatureLayer_management", logFile)
            
            # Dissolve those by reporting Unit ID.  
            if len(inFeaturesList) > 1:
                finalOutputName = files.nameIntermediateFile([inFCNamePrefix+"_final_","FeatureClass"],cleanupList)
            else: 
                finalOutputName = outFeatures # If this is the only one, it's already named.
            
            AddMsg(f"{timer.now()} Dissolving second intersection by reporting unit. Intermediate: {basename(finalOutputName)}", 0, logFile)
            finalOutput = arcpy.Dissolve_management(matchingBuffers,finalOutputName,unitID)
            logArcpy(arcpy.Dissolve_management, (matchingBuffers,finalOutputName,unitID), "arcpy.Dissolve_management", logFile)
            
            # Clean up the feature layer selection for the next iteration.
            arcpy.Delete_management(matchingBuffers)
            logArcpy(arcpy.Delete_management, (matchingBuffers,), "arcpy.Delete_management", logFile)
            
            # keep track of list of outputs.  
            outputList.append(finalOutput)
        
        # merge and dissolve buffer features from all input feature classes into a single feature class.
        if len(outputList) > 1:
            mergeName = files.nameIntermediateFile([f"{toolShortName}_merge_","FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Merging buffer zones from all input Stream features. Intermediate: {basename(mergeName)}", 0, logFile)
            mergeOutput = arcpy.Merge_management(outputList,mergeName)
            logArcpy(arcpy.Merge_management, (outputList,mergeName), "arcpy.Merge_management", logFile)
            AddMsg(f"{timer.now()} Dissolving merged buffer zones. Intermediate: {basename(outFeatures)}", 0, logFile)
            finalOutput = arcpy.Dissolve_management(mergeOutput,outFeatures,unitID)
            logArcpy(arcpy.Dissolve_management, (mergeOutput,outFeatures,unitID), "arcpy.Dissolve_management", logFile)
            # If any of the input features are polygons, we need to perform a final erase of the interior of these polygons from the output.
            AddMsg(f"{timer.now()} Removing interior waterbody areas from dissolve result.", 0, logFile)
            if len(eraseList) > 0:
                #  Merge all eraseFeatures so we only have to do this once.
                eraseName = files.nameIntermediateFile([f"{toolShortName}_erasePolygons_","FeatureClass"],cleanupList)
                eraseFeatureClass = arcpy.Merge_management(eraseList,eraseName)
                logArcpy(arcpy.Merge_management, (eraseList,eraseName), 'arcpy.Merge_management', logFile)
                # Rename the old final output so that it becomes an intermediate dataset
                oldfinalOutputName = files.nameIntermediateFile([f"{outFeatures}_preErase_","FeatureClass"],cleanupList)
                preEraseOutput = arcpy.Rename_management(finalOutput, oldfinalOutputName, "FeatureClass")
                logArcpy(arcpy.Rename_management, (finalOutput, oldfinalOutputName, "FeatureClass"), 'arcpy.Rename_management', logFile)
                try:
                    finalOutput = arcpy.Erase_analysis(preEraseOutput,eraseFeatureClass,outFeatures)
                    logArcpy(arcpy.Erase_analysis, (preEraseOutput,eraseFeatureClass,outFeatures), 'arcpy.Erase_analysis', logFile)
                except:
                    badEraseFeatures = arcpy.FeatureClassToFeatureClass_conversion(eraseFeatureClass,"%scratchworkspace%","badEraseFeatures")
                    logArcpy(arcpy.FeatureClassToFeatureClass_conversion, (eraseFeatureClass,"%scratchworkspace%","badEraseFeatures"), 'arcpy.FeatureClassToFeatureClass_conversion', logFile)
                    badBuffer = arcpy.FeatureClassToFeatureClass_conversion(preEraseOutput,"%scratchworkspace%","badBuffer")
                    logArcpy(arcpy.FeatureClassToFeatureClass_conversion, (preEraseOutput,"%scratchworkspace%","badBuffer"), 'arcpy.FeatureClassToFeatureClass_conversion', logFile)
                    # There is a small chance that this buffer operation will produce a feature class with invalid geometry.  Try a repair.
                    arcpy.RepairGeometry_management(badBuffer,"DELETE_NULL")
                    logArcpy(arcpy.RepairGeometry_management, (badBuffer,"DELETE_NULL"), 'arcpy.RepairGeometry_management', logFile)
                    
                    arcpy.RepairGeometry_management(badEraseFeatures,"DELETE_NULL")
                    logArcpy(arcpy.RepairGeometry_management, (badEraseFeatures,"DELETE_NULL"), 'arcpy.RepairGeometry_management', logFile)
                    
                    finalOutput = arcpy.Erase_analysis(badBuffer,badEraseFeatures,outFeatures)
                    logArcpy(arcpy.Erase_analysis, (badBuffer,badEraseFeatures,outFeatures), 'arcpy.Erase_analysis', logFile)
                    
                    arcpy.Delete_management(badBuffer)
                    logArcpy(arcpy.Delete_management, (badBuffer,), 'arcpy.Delete_management', logFile)
                    
                    arcpy.Delete_management(badEraseFeatures)
                    logArcpy(arcpy.Delete_management, (badEraseFeatures,), 'arcpy.Delete_management', logFile)
        
        return finalOutput, cleanupList 
    finally:
        pass

    
def bufferFeaturesWithoutBorders(inFeatures, repUnits, outFeatures, bufferDist, unitID, cleanupList, timer, logFile):
    """Returns a feature class that contains the area of each reporting unit that is within a buffered distance of a 
        layer - the buffered features may be any geometry.
    **Description:**
        This tool buffers features and identifies the reporting unit that the buffered areas fall within. The buffer 
        size (in linear units) is determined by the user. A new feature class is created that can be used as a reporting 
        unit theme to calculate metrics with the buffered areas. It is useful for generating metrics near streams that 
        fall within the reporting unit.
        
        This tool ignores the boundaries between reporting units when creating buffers. If buffered areas should be
        restricted to the reporting unit where the input feature is located and not extend into nearby reporting units,
        the bufferFreaturesByIntersect should be used instead.
    **Arguments:**
        * *inFeatures* - one or more feature class that will be buffered
        * *repUnits* - reporting units that will be used for the clip
        * *outFeatures* - a feature class (without full path) that will be created as the output of this tool
        * *bufferDist* - distance in the units of the spatial reference of the input data to buffer
        * *unitID* - a field that exists in repUnits that contains a unique identifier for the reporting units. 
        * *cleanupList* - a list object for tracking intermediate datasets for cleanup at the user's request.
        ' 'logFile' - optional file used to record processing steps 
        
    **Returns:**
        * *outFeatures* - output feature class 
    """
    
    try:
        toolShortName = outFeatures[:outFeatures.find("_")]
        outFeatures = files.nameIntermediateFile([outFeatures,"FeatureClass"], cleanupList) 
        
        # The tool accepts a semicolon-delimited list of input features - convert this into a python list object
        # it appears that long directory paths in the multivalue input box causes the delimiter to be quote-semicolon-quote
        # instead of just semicolon
        if "';'" in inFeatures:
            inFeatures = inFeatures.replace("';'",";")    
        if '";"' in inFeatures:
            inFeatures = inFeatures.replace('";"',";")
            
        inFeaturesList = inFeatures.split(";") 
        mergeList = []
        # Initialize list of polygon features for erase
        eraseList = []        
        
        for inFC in inFeaturesList:           
            inFCDesc = arcpy.Describe(inFC)
            inFCName = inFCDesc.baseName 
            
            # because borders are not enforced, features outside of the reporting unit can impact the results.
            # need to find all input features in the reporting units and also those that are within the buffer distance of the reporting unit's edge.
            AddMsg(f"{timer.now()} Selecting features from {inFCName} within {bufferDist} of Reporting units.", 0, logFile)
            inFeatureLayer = arcpy.MakeFeatureLayer_management(inFC, "inFC_lyr")
            logArcpy(arcpy.MakeFeatureLayer_management, (inFC, "inFC_lyr"), "arcpy.MakeFeatureLayer_management", logFile)
            
            arcpy.SelectLayerByLocation_management(inFeatureLayer,'WITHIN_A_DISTANCE', repUnits, bufferDist)
            logArcpy(arcpy.SelectLayerByLocation_management, (inFeatureLayer,'WITHIN_A_DISTANCE', repUnits, bufferDist), "arcpy.SelectLayerByLocation_management", logFile)
            
            if inFCDesc.shapeType == "Polygon":
                eraseList.append(inFC)
            
            inFCNamePrefix = toolShortName+"_"+inFCDesc.baseName 
            
            # Buffer these features and merge the outputs
            namePrefix = inFCNamePrefix+"_Buffer_"
            bufferName = files.nameIntermediateFile([namePrefix,"FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Buffering selected features. Intermediate: {basename(bufferName)}", 0, logFile)
            
            # If the input features are polygons, we need to erase the the input polygons from the buffer output
            inGeom = inFCDesc.shapeType
            if inGeom == "Polygon":
                # When we buffer polygons, we want to exclude the area of the polygon itself.  This can be done using the 
                # "OUTSIDE_ONLY" option in the buffer tool, but that is only available with an advanced license.  Check for
                # the right license level, revert to buffer/erase option if it's not available.
                licenseLevel = arcpy.CheckProduct("ArcInfo")
                if licenseLevel in ["AlreadyInitialized","Available"]:
                    bufferResult = arcpy.Buffer_analysis(inFeatureLayer,bufferName,bufferDist,"OUTSIDE_ONLY")
                    logArcpy(arcpy.Buffer_analysis, (inFeatureLayer,bufferName,bufferDist,"OUTSIDE_ONLY"), "arcpy.Buffer_analysis", logFile)
                else:
                    bufferResult = arcpy.Buffer_analysis(inFeatureLayer,bufferName,bufferDist,"FULL","ROUND")
                    logArcpy(arcpy.Buffer_analysis, (inFeatureLayer,bufferName,bufferDist,"FULL","ROUND"), "arcpy.Buffer_analysis", logFile)

            else:
                bufferResult = arcpy.Buffer_analysis(inFeatureLayer,bufferName,bufferDist,"FULL","ROUND")
                logArcpy(arcpy.Buffer_analysis, (inFeatureLayer,bufferName,bufferDist,"FULL","ROUND"), "arcpy.Buffer_analysis", logFile)
          
            AddMsg(f"{timer.now()} Repairing buffer areas for input features.", 0, logFile)
            arcpy.RepairGeometry_management(bufferResult)
            logArcpy(arcpy.RepairGeometry_management, (bufferResult,), "arcpy.RepairGeometry_management", logFile)
            
            # keep track of list of outputs.  
            mergeList.append(bufferResult)
            
            # remove the temporary stream layer
            arcpy.Delete_management(inFeatureLayer)
            logArcpy(arcpy.Delete_management, (inFeatureLayer,), "arcpy.Delete_management", logFile)

                
        # merge buffer features from all input feature classes into a single feature class.
        # Even if there is only one input, the merge will create a copy of the buffer theme without any unnecessary fields.
        # It is essentially a FeatureClassToFeatureClass operation with fieldMappings.
        fieldMappings = arcpy.FieldMappings()
        fieldMappings.addTable(bufferResult)
        [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name != "BUFF_DIST"]

        namePrefix = toolShortName+"_Merge_"
        mergeName = files.nameIntermediateFile([namePrefix,"FeatureClass"],cleanupList)
        
        if len(inFeaturesList) > 1:
            AddMsg(f"{timer.now()} Merging buffer zones from all input Stream features. Intermediate: {basename(mergeName)}", 0, logFile)
        else:
            AddMsg(f"{timer.now()} Removing unnecessary fields from buffered feature. Intermediate: {basename(mergeName)}", 0, logFile)
        
        mergeOutput = arcpy.Merge_management(mergeList,mergeName,fieldMappings)
        logArcpy(arcpy.Merge_management, (mergeList,mergeName,fieldMappings), "arcpy.Merge_management", logFile)

        
        # Perform an Intersect on erased buffers to assign the Reporting Unit's ID value to the buffer zones within and 
        # to eliminate buffer areas outside of the reporting unit boundaries
        namePrefix = toolShortName+"_Intersect_"
        intersectName = files.nameIntermediateFile([namePrefix,"FeatureClass"],cleanupList)
        AddMsg(f"{timer.now()} Assigning Reporting unit ID values to buffer zones. Intermediate: {basename(intersectName)}", 0, logFile)
        intersectFeatureClass = arcpy.Intersect_analysis([repUnits,mergeOutput],intersectName,"ALL","","INPUT")
        logArcpy(arcpy.Intersect_analysis, ([repUnits,mergeOutput],intersectName,"ALL","","INPUT"), "arcpy.Intersect_analysis", logFile) 
        
        if len(eraseList) > 0:
            # If any of the input features are polygons, we need to perform a final erase of the interior of these polygons from the output.
            
            if len(eraseList) > 1:
                #  Merge all eraseFeatures so we only have to do this once.
                namePrefix = toolShortName+"_ErasePolygons_"
                erasePolygonsName = files.nameIntermediateFile([namePrefix,"FeatureClass"],cleanupList)
                AddMsg(f"{timer.now()} Creating a single erase feature from all polygon Stream features. Intermediate: {basename(erasePolygonsName)}", 0, logFile)
                eraseFeatureClass = arcpy.Merge_management(eraseList, erasePolygonsName)
                logArcpy(arcpy.Merge_management, (eraseList, erasePolygonsName), "arcpy.Merge_management", logFile)
            else:
                eraseFeatureClass = eraseList[0]

            namePrefix = toolShortName+"_Erase_"
            erasedOutputName = files.nameIntermediateFile([namePrefix,"FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Removing interior waterbody areas from buffer result. Intermediate: {basename(erasedOutputName)}", 0, logFile) 
    
            try:
                erasedOutput = arcpy.Erase_analysis(intersectFeatureClass, eraseFeatureClass, erasedOutputName)
                logArcpy(arcpy.Erase_analysis, (intersectFeatureClass, eraseFeatureClass, erasedOutputName), "arcpy.Erase_analysis", logFile)
            except:
                badEraseFeatures = arcpy.FeatureClassToFeatureClass_conversion(eraseFeatureClass,"%scratchworkspace%","badEraseFeatures")
                logArcpy(arcpy.FeatureClassToFeatureClass_conversion, (eraseFeatureClass,"%scratchworkspace%","badEraseFeatures"), "arcpy.FeatureClassToFeatureClass_conversion", logFile)
                
                badBuffer = arcpy.FeatureClassToFeatureClass_conversion(intersectFeatureClass,"%scratchworkspace%","badBuffer")
                logArcpy(arcpy.FeatureClassToFeatureClass_conversion, (intersectFeatureClass,"%scratchworkspace%","badBuffer"), "arcpy.FeatureClassToFeatureClass_conversion", logFile)
                
                # There is a small chance that this buffer operation will produce a feature class with invalid geometry.  Try a repair.
                arcpy.RepairGeometry_management(badBuffer,"DELETE_NULL")
                logArcpy(arcpy.RepairGeometry_management, (badBuffer,"DELETE_NULL"), "arcpy.RepairGeometry_management", logFile)
                
                arcpy.RepairGeometry_management(badEraseFeatures,"DELETE_NULL")
                logArcpy(arcpy.RepairGeometry_management, (badEraseFeatures,"DELETE_NULL"), "arcpy.RepairGeometry_management", logFile)
                
                erasedOutput = arcpy.Erase_analysis(badBuffer, badEraseFeatures, erasedOutputName)
                logArcpy(arcpy.Erase_analysis, (badBuffer, badEraseFeatures, erasedOutputName), "arcpy.Erase_analysis", logFile)
                
                arcpy.Delete_management(badBuffer)
                logArcpy(arcpy.Delete_management, (badBuffer,), "arcpy.Delete_management", logFile)
                
                arcpy.Delete_management(badEraseFeatures)
                logArcpy(arcpy.Delete_management, (badEraseFeatures,), "arcpy.Delete_management", logFile)
        else:
            erasedOutput = intersectFeatureClass
        
        AddMsg(f"{timer.now()} Dissolving intersections by reporting unit.", 0, logFile)
        finalOutput = arcpy.Dissolve_management(erasedOutput,outFeatures,unitID)
        logArcpy(arcpy.Dissolve_management, (erasedOutput,outFeatures,unitID), "arcpy.Dissolve_management", logFile)
        
        return finalOutput, cleanupList 
    finally:
        pass
    
def getIntersectOfPolygons(repUnits, uIDField, secondPoly, outFeatures, cleanupList, timer, logFile=None):
    '''This function performs an intersection and dissolve function on a set of polygon features.
    **Description:**
        This function intersects the representative units with a second polygon feature, splitting the second polygon at unit 
        boundaries and giving unit attributes to the split polygons.  The split polygons are then dissolved by the unit IDs.
    **Arguments:**
        * *repUnits* - the input representative areal units feature class that will be used to split the lines
        * *uIDField* - the ID field of the representative areal units feature class.  Each dissolved line feature will be assigned the respective uID
        * *secondPoly* - the second polygon feature class
        * *outFeatures* - name of the output feature class.
        ' 'logFile' - optional file used to record processing steps
    **Returns:**
        * *outFeatures* - name of the output feature class.
    '''
     
    # Get a unique name with full path for the output features - will default to current workspace:
    toolShortName = outFeatures[:outFeatures.find("_")]
    
    desc1 = arcpy.Describe(repUnits)
    desc2 = arcpy.Describe(secondPoly)
    
    # Intersect the reporting unit features with the floodplain features 
    intersectFeatures = files.nameIntermediateFile([toolShortName+"_Intersect_","FeatureClass"], cleanupList)
    AddMsg(f"{timer.now()} Intersecting {desc1.basename} with {desc2.basename}. Intermediate: {basename(intersectFeatures)}", 0, logFile)
    intersection = arcpy.Intersect_analysis([repUnits, secondPoly],intersectFeatures,"ALL","","INPUT")
    logArcpy(arcpy.Intersect_analysis, ([repUnits, secondPoly],intersectFeatures,"ALL","","INPUT"), "arcpy.Intersect_analysis", logFile)
     
    # Dissolve the intersected lines on the unit ID fields.
    outFeatures = files.nameIntermediateFile([outFeatures,"FeatureClass"], cleanupList)
    dissolveFields = uIDField
    AddMsg(f"{timer.now()} Dissolving {desc2.basename} zone features. Intermediate: {basename(outFeatures)}", 0, logFile)  
    arcpy.Dissolve_management(intersection,outFeatures,dissolveFields,"","MULTI_PART","DISSOLVE_LINES")
    logArcpy(arcpy.Dissolve_management, (intersection,outFeatures,dissolveFields,"","MULTI_PART","DISSOLVE_LINES"), "arcpy.Dissolve_management", logFile)
    
    # Delete following intermediate datasets in order to reduce clutter if Intermediates are to be saved
    #arcpy.Delete_management(intersection)
 
    return outFeatures, cleanupList

def splitDissolveMerge(lines,repUnits,uIDField,mergedLines,inLengthField,lineClass='',logFile=None):
    '''This function performs a intersection and dissolve function on a set of line features.
    **Description:**
        This function intersects the representative units with line features, clipping lines at unit boundaries and 
        giving unit attributes to each line.  The lines are then dissolved by the unit IDs (and a line class, if desired) 
    **Arguments:**
        * *lines* - the input line feature class
        * *repUnits* - the input representative areal units feature class that will be used to split the lines
        * *uIDField* - the ID field of the representative areal units feature class.  Each dissolved line feature will be assigned the respective uID
        * *inLengthField* - desired fieldname base for output length field
        * *lineClass* - optional field containing class values for the line feature class.  these classes are preserved through the split/dissolve/merge process
        * *mergedLines* - name of the output feature class.
    **Returns:**
        * *mergedLines* - name of the output feature class.
        * *lengthFieldName* - validated name of the field in the output feature class containing length values
    '''
    # Get a unique name with full path for the output features - will default to current workspace:
    intersectFeatures = arcpy.CreateScratchName("tmpIntersect","","FeatureClass")
    # Intersect the lines and the areal units
    intersection = arcpy.Intersect_analysis([repUnits, lines],intersectFeatures,"ALL","","INPUT")
    logArcpy(arcpy.Intersect_analysis,([repUnits, lines],intersectFeatures,"ALL","","INPUT"),"arcpy.Intersect_analysis",logFile)
    
    dissolveFields = uIDField.name
    if lineClass != '':
        dissolveFields = [uIDField.name, lineClass]
    
    # Dissolve the intersected lines on the unit ID (and optional line class) fields. 
    arcpy.Dissolve_management(intersection,mergedLines,dissolveFields,"","MULTI_PART","DISSOLVE_LINES")
    logArcpy(arcpy.Dissolve_management,(intersection,mergedLines,dissolveFields,"","MULTI_PART","DISSOLVE_LINES"),"arcpy.Dissolve_management",logFile)
    
    arcpy.Delete_management(intersection)
    logArcpy(arcpy.Delete_management,(intersection,),"arcpy.Delete_management",logFile)
    
    ## Add and calculate a length field for the new shapefile
    lengthFieldName = addLengthField(mergedLines,inLengthField,logFile)
    return mergedLines, lengthFieldName

def findIntersections(mergedRoads,inStreamFeature,mergedStreams,ruID,roadStreamMultiPoints,roadStreamIntersects,roadStreamSummary,
                      streamLengthFieldName,xingsPerKMFieldName,timer,roadClass="",logFile=None):
    '''This function performs an intersection analysis on two input line feature classes.  The desired output is 
    a count of the number of intersections per reporting unit ID (both line feature classes already contain this ID).  
    To obtain this cout the intersection output is first converted to singlepart features (from the default of multipart
    and then a frequency analysis performed.
    '''

    # Intersect the roads and the streams - the output is a multipoint feature class with one feature per combination 
    # of road class and streams per reporting unit
    AddMsg(f"{timer.now()} Intersecting the road and stream features. Intermediate: {basename(roadStreamMultiPoints)}")
    arcpy.Intersect_analysis([mergedRoads,inStreamFeature],roadStreamMultiPoints,"ALL","#","POINT")
    logArcpy(arcpy.Intersect_analysis,([mergedRoads,inStreamFeature],roadStreamMultiPoints,"ALL","#","POINT"),"arcpy.Intersect_analysis", 0, logFile)
    
    # Because we want a count of individual intersection features, break apart the multipoints into single points
    AddMsg(f"{timer.now()} Converting intersection points from multi-point to single point. Intermediate: {basename(roadStreamIntersects)}", 0, logFile)
    arcpy.MultipartToSinglepart_management(roadStreamMultiPoints,roadStreamIntersects)
    logArcpy(arcpy.MultipartToSinglepart_management,(roadStreamMultiPoints,roadStreamIntersects),"arcpy.MultipartToSinglepart_management",logFile)
    
    # Perform a frequency analysis to get a count of the number of crossings per class per reporting unit
    AddMsg(f"{timer.now()} Performing frequency analysis to determine the number crossings per reporting unit. Intermediate: {basename(roadStreamSummary)}", 0, logFile)
    fieldList = [ruID.name]
    if roadClass:
        fieldList.append(roadClass)
    arcpy.Frequency_analysis(roadStreamIntersects,roadStreamSummary,fieldList)
    
    # Lastly, calculate the number of stream crossings per kilometer of streams.
    AddMsg(f"{timer.now()} Calculating the number of stream crossings per kilometer of streams.", 0, logFile)
    # Join the stream layer to the summary table
    arcpy.JoinField_management(roadStreamSummary, ruID.name, mergedStreams, ruID.name, [streamLengthFieldName])
    logArcpy(arcpy.JoinField_management,(roadStreamSummary, ruID.name, mergedStreams, ruID.name, [streamLengthFieldName]),"arcpy.JoinField_management", logFile)
    
    # Set up a calculation expression for crossings per kilometer.
    calcExpression = "!FREQUENCY!/!" + streamLengthFieldName + "!"    
    addCalculateField(roadStreamSummary,xingsPerKMFieldName,"DOUBLE",calcExpression,"",logFile)

def roadsNearStreams(inStreamFeature,mergedStreams,bufferDist,inRoadFeature,inReportingUnitFeature,streamLengthFieldName,ruID,streamBuffer,
                     tmp1RdsNearStrms,tmp2RdsNearStrms,roadsNearStreams,rnsFieldName,inLengthField, timer, logFile, roadClass=""):
    '''This function calculates roads near streams by first buffering a streams layer by the desired distance
    and then intersecting that buffer with a roads feature class.  This metric measures the total 
    length of roads within the buffer distance divided by the total length of stream in the reporting unit, both lengths 
    are measured in map units (e.g., m of road/m of stream).
    '''
    # For RNS metric, first buffer all the streams by the desired distance
    AddMsg(f"{timer.now()} Buffering stream features. Intermediate: {basename(streamBuffer)}", 0, logFile)
    arcpy.Buffer_analysis(inStreamFeature,streamBuffer,bufferDist,"FULL","ROUND","ALL","#")
    logArcpy(arcpy.Buffer_analysis, (inStreamFeature,streamBuffer,bufferDist,"FULL","ROUND","ALL","#"), "arcpy.Buffer_analysis", logFile)
    
    # Intersect the stream buffers with the input road layer to find road segments in the buffer zone
    AddMsg(f"{timer.now()} Intersecting road features with stream buffers.", 0, logFile)
    intersect1 = arcpy.Intersect_analysis([inRoadFeature, streamBuffer],tmp1RdsNearStrms,"ALL","#","INPUT")
    logArcpy(arcpy.Intersect_analysis, ([inRoadFeature, streamBuffer],tmp1RdsNearStrms,"ALL","#","INPUT"), "arcpy.Intersect_analysis", logFile)
    
    # Intersect the roads in the buffer zones with the reporting unit feature to assign RU Id values to road segments
    AddMsg(f"{timer.now()} Assigning reporting unit feature ID values to road segments.", 0, logFile)
    intersect2 = arcpy.Intersect_analysis([intersect1, inReportingUnitFeature],tmp2RdsNearStrms,"ALL","#","INPUT")
    logArcpy(arcpy.Intersect_analysis, ([intersect1, inReportingUnitFeature],tmp2RdsNearStrms,"ALL","#","INPUT"), "arcpy.Intersect_analysis", logFile)
    
    # if overlapping polygons exist in reporting unit theme, the above intersection may result in several rows of data for a given reporting unit.
    # perform a dissolve to get a 1 to 1 relationship with input to output. Include the class field if provided.
    AddMsg(f"{timer.now()} Dissolving intersection result and calculating values. Intermediate: {basename(roadsNearStreams)}", 0, logFile)
    dissolveFields = ruID.name
    if roadClass != '':
        dissolveFields = [ruID.name, roadClass] 
    # Dissolve the intersected lines on the unit ID (and optional line class) fields.
    arcpy.Dissolve_management(intersect2,roadsNearStreams,dissolveFields, "#","MULTI_PART","DISSOLVE_LINES")
    logArcpy(arcpy.Dissolve_management, (intersect2,roadsNearStreams,dissolveFields, "#","MULTI_PART","DISSOLVE_LINES"), "arcpy.Dissolve_management", logFile)
    
    arcpy.Delete_management(intersect1)
    logArcpy(arcpy.Delete_management, (intersect1,), "arcpy.Delete_management", logFile)
    
    arcpy.Delete_management(intersect2)
    logArcpy(arcpy.Delete_management, (intersect2,), "arcpy.Delete_management", logFile)
    
    # Add and calculate a length field for the new shapefile
    roadLengthFieldName = addLengthField(roadsNearStreams,inLengthField,logFile)
    
    # Next join the merged streams layer to the roads/streambuffer intersection layer
    arcpy.JoinField_management(roadsNearStreams, ruID.name, mergedStreams, ruID.name, [streamLengthFieldName])
    logArcpy(arcpy.JoinField_management, (roadsNearStreams, ruID.name, mergedStreams, ruID.name, [streamLengthFieldName]), "arcpy.JoinField_management", logFile)
    
    # Set up a calculation expression for the roads near streams fraction
    calcExpression = "!" + roadLengthFieldName + "!/!" + streamLengthFieldName + "!"
    # Add a field for the roads near streams fraction
    rnsFieldName = addCalculateField(roadsNearStreams,rnsFieldName,"DOUBLE",calcExpression,'#', logFile)


def addAreaField(inAreaFeatures, areaFieldName, logFile=None):
    '''This function checks for the existence of a field containing polygon area in square kilometers and if it does
        not exist, adds and populates it appropriate.
    **Description:**
        This function checks for the existence of a field containing polygon area in square kilometers and if it does
        not exist, adds and populates it appropriate.
    **Arguments:**
        * *inAreaFeatures* - the input feature class that will receive the field.      
    **Returns:**
        * *areaFieldName* - validated fieldname      
    '''
    # Set up the calculation expression for area in square kilometers
    shapeFieldName = arcpy.Describe(inAreaFeatures).shapeFieldName
    calcExpression = "!{0}.AREA@SQUAREKILOMETERS!".format(shapeFieldName)
    areaFieldName = addCalculateField(inAreaFeatures,areaFieldName,"DOUBLE",calcExpression,'#',logFile)
    return areaFieldName    

def addLengthField(inLineFeatures,lengthFieldName,logFile=None):
    '''This function adds and populates a length field for the input line feature class
    **Description:**
        This function checks for the existence of a field containing line area in kilometers and if it does
        not exist, adds and populates it appropriate.
    **Arguments:**
        * *inLineFeatures* - the input feature class that will receive the field. 
        * *lengthFieldName* - the desired fieldname base for the output field    
    **Returns:**
        * *lengthFieldName* - validated fieldname      
    '''
    # Get a describe object
    lineDescription = arcpy.Describe(inLineFeatures)
    
    # Set up the calculation expression for length in kilometers
    calcExpression = "!{0}.LENGTH@KILOMETERS!".format(lineDescription.shapeFieldName)
    lengthFieldName = addCalculateField(inLineFeatures,lengthFieldName,"DOUBLE",calcExpression, '#', logFile)
    return lengthFieldName

def addCalculateField(inFeatures,fieldName,fieldType,calcExpression,codeBlock='#',logFile=None):
    '''This function checks for the existence of the desired field, and if it does not exist, adds and populates it
    using the given calculation expression
    **Description:**
        This function checks for the existence of the specified field and if it does
        not exist, adds and populates it as appropriate.
    **Arguments:**
        * *inFeatures* - the input feature class that will receive the field.
        * *fieldName* - field name string
        ' 'fieldType' - field type string (e.g., "DOUBLE", "SHORT")
        * *calcExpression* - string calculation expression in python 
        * *codeBlock* - optional python code block expression       
        * *logFile' - optional file used to record processing steps
    **Returns:**
        * *fieldName* - validated fieldname      
    '''
    # Validate the desired field name for the dataset
    fieldName = arcpy.ValidateFieldName(fieldName, arcpy.Describe(inFeatures).path)
    
    # Check for existence of field.
    fieldList = arcpy.ListFields(inFeatures,fieldName)
    if not fieldList: # if the list of fields that exactly match the validated fieldname is empty, then add the field
        arcpy.AddField_management(inFeatures,fieldName, fieldType)
        logArcpy(arcpy.AddField_management, (inFeatures,fieldName, fieldType), 'arcpy.AddField_management', logFile)
        
    else: # Otherwise warn the user that the field will be recalculated.
        AddMsg(f"The field {fieldName} already exists in {inFeatures}, its values will be recalculated.")
    arcpy.CalculateField_management(inFeatures,fieldName,calcExpression,"PYTHON",codeBlock)
    logArcpy(arcpy.CalculateField_management, (inFeatures,fieldName,calcExpression,"PYTHON",codeBlock), 'arcpy.CalculateField_management', logFile)
    return fieldName   


def tabulateMDCP(inPatchRaster, inReportingUnitFeature, reportingUnitIdField, rastoPolyFeature, patchCentroidsFeature, 
                 patchDissolvedFeature, nearPatchTable, zoneAreaDict, timer, pmResultsDict, logFile):
    resultDict = {}
    
    # put the proper field delimiters around the ID field name for SQL expressions
    delimitedField = arcpy.AddFieldDelimiters(inReportingUnitFeature, reportingUnitIdField)
    
    #Convert Final Patch Raster to polygon
    AddMsg(f"{timer.now()} Converting raster patches to polygons. Intermediate: {basename(rastoPolyFeature)}", 0, logFile)
    patchOnlyRaster = arcpy.sa.SetNull(inPatchRaster, inPatchRaster, "VALUE <= 0")
    logArcpy(arcpy.sa.SetNull, (inPatchRaster, inPatchRaster, "VALUE <= 0"), "arcpy.sa.SetNull", logFile)
    
    
    # Check to see if all values are NULL (ALLNODATA: 0 = no, 1 = yes)
    dataResult = arcpy.management.GetRasterProperties(patchOnlyRaster, 'ALLNODATA')
    anyPatches = (dataResult.getOutput(0))
    
    if anyPatches == '0':
    
        arcpy.RasterToPolygon_conversion(patchOnlyRaster, rastoPolyFeature, "NO_Simplify", "VALUE")
        logArcpy(arcpy.RasterToPolygon_conversion, (patchOnlyRaster, rastoPolyFeature, "NO_Simplify", "VALUE"), "arcpy.RasterToPolygon_conversion", logFile)
        
        #Dissolve the polygons on Value Field to make sure each patch is represented by a single polygon.
        AddMsg(f"{timer.now()} Dissolving patch polygons by value field. Intermediate: {basename(patchDissolvedFeature)}", 0, logFile)
        arcpy.Dissolve_management(rastoPolyFeature, patchDissolvedFeature,"gridcode","#", "MULTI_PART","DISSOLVE_LINES")
        logArcpy(arcpy.Dissolve_management, (rastoPolyFeature, patchDissolvedFeature,"gridcode","#", "MULTI_PART","DISSOLVE_LINES"), "arcpy.Dissolve_management", logFile)
          
        #Create a feature layer of the FinalPatch_poly_diss
        patchDissolvedLayer = arcpy.MakeFeatureLayer_management(patchDissolvedFeature, "patchDissolvedLayer")
        logArcpy(arcpy.MakeFeatureLayer_management, (patchDissolvedFeature, "patchDissolvedLayer"), "arcpy.MakeFeatureLayer_management", logFile)
         
        #Convert Final Patch Raster to points to get the cell centroids
        AddMsg(f"{timer.now()} Converting raster patch cells to centroid points. Intermediate: {basename(patchCentroidsFeature)}", 0, logFile)
        arcpy.RasterToPoint_conversion(patchOnlyRaster, patchCentroidsFeature, "VALUE")
        logArcpy(arcpy.RasterToPoint_conversion, (patchOnlyRaster, patchCentroidsFeature, "VALUE"), "arcpy.RasterToPoint_conversion", logFile)
         
        #Create a feature layer of the FinalPatch_centroids
        patchCentroidsLayer = arcpy.MakeFeatureLayer_management(patchCentroidsFeature, "patchCentroidsLayer")
        logArcpy(arcpy.MakeFeatureLayer_management, (patchCentroidsFeature, "patchCentroidsLayer"), "arcpy.MakeFeatureLayer_management", logFile)
        
        # Initialize custom progress indicator
        totalRUs = len(zoneAreaDict)
        #mdcpLoopProgress = messages.loopProgress(totalRUs, logFile)
        mdcpLoopProgress = messages.loopProgress(totalRUs)
        
        noPatches = 0
        singlePatch = 0
       
        #Select the Reporting Unit and the intersecting polygons in FinalPatch_poly_diss
        per = '[PER UNIT]'
        AddMsg(f"{timer.now()} The following steps will be performed for each reporting unit:", 0, logFile)    
        AddMsg("\n---")
        AddMsg(f"{timer.now()} {per} 1) Create a feature layer of the reporting unit.", 0, logFile)
        AddMsg(f"{timer.now()} {per} 2) Select centroid points that are in the reporting unit layer.", 0, logFile)
        AddMsg(f"{timer.now()} {per} 3) If number of selected centroids is zero, Set MDCP, PWN, and PWON to -9999.", 0, logFile)
        AddMsg(f"{timer.now()} {per} 4) If number of selected centroids is greater than zero:", 0, logFile)
        AddMsg(f"{timer.now()} {per}   4a) Select patch polygons that intersect the selected centroids.", 0, logFile)
        AddMsg(f"{timer.now()} {per}   4b) Clip the selected patches to the reporting unit boundary.", 0, logFile) 
        AddMsg(f"{timer.now()} {per}   4c) Use GenerateNearTable to create a table with entries for each patch and the distance to its nearest neighbor.", 0, logFile)
        AddMsg(f"{timer.now()} {per}     c1) arcpy.GenerateNearTable_analysis(clipPolyFeature,[clipPolyFeature], nearPatchTable, '','NO_LOCATION','NO_ANGLE','CLOSEST','0')", 0, logFile)
        AddMsg(f"{timer.now()} {per}   4d) If only one patch exists in reporting unit, set MDCP and PWN to 0, and PWON to 1.", 0, logFile) 
        AddMsg(f"{timer.now()} {per}   4d) If more than one patch exists in reporting unit:", 0, logFile)
        AddMsg(f"{timer.now()} {per}     d1) Collect the nearest distance values for all patches in a list.", 0, logFile)
        AddMsg(f"{timer.now()} {per}     d2) PWN = len(distList)", 0, logFile)
        AddMsg(f"{timer.now()} {per}     d3) MDCP = sum(distList)/PWN", 0, logFile)
        AddMsg(f"{timer.now()} {per}     d3) PWON = numPatch - PWN", 0, logFile)
        AddMsg("---\n")
        
        AddMsg(f"{timer.now()} Starting calculations per reporting unit...", 0, logFile)
        
        for aZone in zoneAreaDict.keys():
            pwnCount = 0
            pwonCount = 0
            meanDist = 0
                
            if isinstance(aZone, int): # reporting unit id is an integer - convert to string for SQL expression
                squery = "%s = %s" % (delimitedField, str(aZone))
            else: # reporting unit id is a string - enclose it in single quotes for SQL expression
                squery = "%s = '%s'" % (delimitedField, str(aZone))
            
            #Create a feature layer of the single reporting unit
            if arcpy.Exists("inaReportingUnitLayer"):
                # delete the layer in case the geoprocessing overwrite output option is turned off
                arcpy.Delete_management("inaReportingUnitLayer")
                
            aReportingUnitLayer = arcpy.MakeFeatureLayer_management(inReportingUnitFeature,"inaReportingUnitLayer",squery,"#")
            
            #Select the centroids that are in the "subwatersheds_Layer"
            arcpy.SelectLayerByLocation_management(patchCentroidsLayer,"INTERSECT", aReportingUnitLayer)
    
            centroidCount = int(arcpy.GetCount_management(patchCentroidsLayer).getOutput(0))
            
            # Check to see if any patches exist within reporting unit
            if centroidCount == 0:
                # arcpy.AddWarning("No patches found in %s. MDCP set to -9999" % (str(aZone)))
                meanDist = -9999
                pwnCount = -9999
                pwonCount = -9999
                noPatches += 1
            
            else:
                # Select the patches that have selected centroids within them
                arcpy.SelectLayerByLocation_management(patchDissolvedLayer, "INTERSECT", patchCentroidsLayer)
                
                # Clip the selected patches to the reporting unit boundary
                if arcpy.Exists("clipPolyDiss"):
                    # delete the layer in case the geoprocessing overwrite output option is turned off
                    arcpy.Delete_management("clipPolyDiss")    
                clipPolyDissFeature = arcpy.Clip_analysis(patchDissolvedLayer, aReportingUnitLayer, "clipPolyDiss")
    
                # Determine the number of patches found in this reporting unit using this script's methodology
                totalNumPatches = int(arcpy.GetCount_management(clipPolyDissFeature).getOutput(0))
                
                # Get the number of patches found in this reporting unit from the Patch Metric methodology
                pmPatches = pmResultsDict[aZone][1]
                
                if totalNumPatches == pmPatches:
                    #Calculate Near Distances for each watershed
                    arcpy.GenerateNearTable_analysis(clipPolyDissFeature,[clipPolyDissFeature], nearPatchTable,
                                                 "","NO_LOCATION","NO_ANGLE","CLOSEST","0")
                
                else:
                    # Disagreement in patch numbers possibly caused by imperfect dissolve operation. 
                    # Try to correct with a second dissolve using only the clipped polygons within the reporting unit
                    
                    #Dissolve the polygons on Value Field to make sure each patch is represented by a single polygon.
                    if arcpy.Exists("wshed_Polygons_Diss"):
                        arcpy.Delete_management("wshed_Polygons_Diss")
                    arcpy.Dissolve_management(clipPolyDissFeature, "wshed_Polygons_Diss","gridcode","#", "MULTI_PART","DISSOLVE_LINES")
                     
                    #Create a feature layer of the newly dissolved patches
                    arcpy.MakeFeatureLayer_management("wshed_Polygons_Diss", "FinalPatch_diss_Layer")
                    
                    # Re-evaluate the number of patches within the reporting unit
                    totalNumPatches = int(arcpy.GetCount_management("FinalPatch_diss_Layer").getOutput(0))
                    
                    # Generate the Near Distance table for newly dissolved patches
                    arcpy.GenerateNearTable_analysis("FinalPatch_diss_Layer",["FinalPatch_diss_Layer"], nearPatchTable,
                                                     "","NO_LOCATION","NO_ANGLE","CLOSEST","0")
                    
                    if totalNumPatches != pmPatches:
                        # Alert the user that the problem was not corrected
                        AddMsg("Possible error in the number of patches found in " + str(aZone) +" \n" + \
                                         "Calculated value for MDCP for this reporting unit is suspect", 1, logFile)
                 
                #Get total number of patches and calculate the mean distance
                try:
                    # see if only one patch exists in reporting unit
                    if totalNumPatches == 1:
                        # arcpy.AddWarning("Single patch in %s. MDCP = 0" % (str(aZone)))
                        pwonCount = totalNumPatches
                        meanDist = 0
                        singlePatch += 1
                         
                    else: # found neighboring patches
                        rows = arcpy.SearchCursor(nearPatchTable)
                        distList = []
                        for row in rows:
                            distance = row.getValue("NEAR_DIST")
                            distList.append(distance)
                        del row, rows
                        
                        pwnCount = len(distList)
                        totalDist = sum(distList)
                        meanDist = totalDist/pwnCount
                        pwonCount = totalNumPatches - pwnCount
                     
                except:
                    AddMsg("Near Distance routine failed in %s" % (str(aZone)), 1, logFile)
                    meanDist = -9999
                    pwnCount = -9999
                    pwonCount = -9999
                    
                finally:
                    arcpy.Delete_management(nearPatchTable)
    
                                  
            resultDict[aZone] = f"{pwnCount},{pwonCount},{meanDist}"
            
            # delete the single reporting unit layer
            arcpy.Delete_management(aReportingUnitLayer)
            
            # clean up temporary files
            if arcpy.Exists(clipPolyDissFeature):
                arcpy.Delete_management(clipPolyDissFeature)
            if arcpy.Exists("wshed_Polygons_Diss"):
                arcpy.Delete_management("wshed_Polygons_Diss")
            if arcpy.Exists("FinalPatch_diss_Layer"):
                arcpy.Delete_management("FinalPatch_diss_Layer")
            
            mdcpLoopProgress.update()
            
        if noPatches > 0:
            AddMsg(f"{noPatches} reporting units contained no patches. MDCP was set to -9999 for these units.", 1, logFile)
        
        if singlePatch > 0:
            AddMsg(f"{singlePatch} reporting units contained a single patch. MDCP was set to 0 for these units.", 1, logFile)
            
        arcpy.Delete_management(patchCentroidsLayer)
        logArcpy(arcpy.Delete_management, (patchCentroidsLayer,), "arcpy.Delete_management", logFile)
        
        arcpy.Delete_management(patchDissolvedLayer)
        logArcpy(arcpy.Delete_management, (patchDissolvedLayer,), "arcpy.Delete_management", logFile)
    
    else:
        AddMsg("No reporting units contained patches. Setting MDCP to -9999 for all units.", 1, logFile)
        
        for aZone in zoneAreaDict.keys():
            meanDist = -9999
            pwnCount = -9999
            pwonCount = -9999
            
            resultDict[aZone] = f"{pwnCount},{pwonCount},{meanDist}"
              
    return resultDict


def mergeVectorsByType(inFeatures, fileNameBase, cleanupList, timer, logFile):
    """Returns a list of merged feature classes. List item one is polygon features, item two is polyline features, and item three is point features.
    **Description:**
        This tool accepts the parameterAsText string of feature layers from a multiple value input parameter. It separates those layers
        by shape type, and merges them into three new possible feature classes (polygon, polyline, and/or point) projected to the environment's 
        Output coordinate system. Before the merge operation, ATtILA attempts to determine if a datum transformation is needed and selects a suitable
        transformation method. If no feature layer of a particular class is found, a string with invalid filename characters is returned
        in the list position for that shape type. Using that string with the arcpy function Exists(), a boolean FALSE will be returned. If a 
        FALSE is returned, further feature class operations can be ignored for that feature class type.

    **Arguments:**
        * *inFeatures* - one or more feature class that will be merged
        * *fileNameBase* - a string (without full path) that will be used as the filename prefix to create the outputs of this tool
        * *cleanupList* - a list object for tracking intermediate datasets for cleanup at the user's request
        ' 'logFile' - optional file used to record processing steps 
        
    **Returns:**
        * *mergedOutputs* - list of merged output feature classes. Item one is polygon features, item two is polyline features, and item three is point features 
        * *cleanupList* - a list object for tracking intermediate datasets for cleanup at the user's request
    """
    
    try:
        
        # The tool accepts a semicolon-delimited list of input features - convert this into a python list object
        # it appears that long directory paths in the multivalue input box causes the delimiter to be quote-semicolon-quote
        # instead of just semicolon
        if "';'" in inFeatures:
            inFeatures = inFeatures.replace("';'",";")    
        if '";"' in inFeatures:
            inFeatures = inFeatures.replace('";"',";")
            
        inFeaturesList = inFeatures.split(";") 
        
        lineList = []
        polyList = []
        pointList = []
        
        for inFC in inFeaturesList:           
            fcDesc = arcpy.Describe(inFC) 
            fcType = fcDesc.shapeType
            fcSR = fcDesc.spatialReference
            fcName = fcDesc.baseName
            fcExtent = fcDesc.extent
            
            outCS = env.outputCoordinateSystem
            
            transformList = arcpy.ListTransformations(fcSR, outCS, fcExtent)
            
            if len(transformList) != 0:
                # default to the first transformation method listed. ESRI documentation indicates this is typically the most suitable
                transformMethod = transformList[0]
                AddMsg("A transformation method was needed to project {0} to the Output coordinate system. ATtILA selected "\
                       "{1}. If a more accurate transformation method is needed, please rerun this tool after converting all of the "\
                       "input data to the same projection.".format(fcName, transformMethod), 1, logFile)
                namePrefix = fcName+"_Prj_"
                prjFC = files.nameIntermediateFile([namePrefix, "FeatureClass"], cleanupList)
                AddMsg(f"{timer.now()} Projecting {fcName} to {basename(prjFC)}.", 0, logFile)
                arcpy.management.Project(inFC, prjFC, outCS, transformMethod)
                logArcpy(arcpy.management.Project, (inFC, prjFC, outCS, transformMethod), 'arcpy.management.Project', logFile)   
            else:
                prjFC = inFC
            
            if fcType == "Polygon":
                polyList.append(prjFC)
            elif fcType == "Polyline":
                lineList.append(prjFC)
            elif fcType == "Point":
                pointList.append(prjFC)
            
        
        # merge features from all input feature classes into a single feature class.
        
        mergedOutputs = ['No Polygon @&?$#', 'No PolyLine @&?$#', 'No Point @&?$#']
        
        if len(lineList) > 1:
            namePrefix = fileNameBase+"_Line_Merge_"
            mergeName = files.nameIntermediateFile([namePrefix,"FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Merging {len(lineList)} line features from input features. Intermediate: {os.path.basename(mergeName)}", 0, logFile)
            # use fieldMappings to reduce file size and possible processing time.
            fieldMappings = getMinimumFieldMappings(lineList)
            mergeOutput = arcpy.Merge_management(lineList,mergeName,fieldMappings)
            logArcpy(arcpy.Merge_management, (lineList,mergeName,fieldMappings), 'arcpy.Merge_management', logFile)
            
            mergedOutputs[0] = mergeOutput
        elif len(lineList) == 1:
            mergedOutputs[0] = lineList[0]

        if len(polyList) > 1:
            namePrefix = f"{fileNameBase}_Poly_Merge_"
            mergeName = files.nameIntermediateFile([namePrefix,"FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Merging {len(polyList)} polygon features from input features. Intermediate: {os.path.basename(mergeName)}", 0, logFile)
            # use fieldMappings to reduce file size and possible processing time.
            fieldMappings = getMinimumFieldMappings(polyList)
            mergeOutput = arcpy.Merge_management(polyList,mergeName,fieldMappings)
            logArcpy(arcpy.Merge_management, (polyList,mergeName,fieldMappings), 'arcpy.Merge_management', logFile)
            
            mergedOutputs[1] = mergeOutput
        elif len(polyList) == 1:
            mergedOutputs[1] = polyList[0]
        
        if len(pointList) > 1:            
            namePrefix = f"{fileNameBase}_Point_Merge_"
            mergeName = files.nameIntermediateFile([namePrefix,"FeatureClass"],cleanupList)
            AddMsg(f"{timer.now()} Merging {len(pointList)} point features from input features. Intermediate: {os.path.basename(mergeName)}", 0, logFile)
            # use fieldMappings to reduce file size and possible processing time.
            fieldMappings = getMinimumFieldMappings(pointList)
            mergeOutput = arcpy.Merge_management(pointList,mergeName,fieldMappings)
            logArcpy(arcpy.Merge_management, (pointList,mergeName,fieldMappings), 'arcpy.Merge_management', logFile)
            
            mergedOutputs[2] = mergeOutput
        elif len(pointList) == 1:
            mergedOutputs[2] = pointList[0]
        
        # mergedOutputs is a list [mergedLines, mergedPolygons, mergedPoints]
        return mergedOutputs, cleanupList 
    finally:
        pass
                    
def getMinimumFieldMappings(layerList):
    ''' Returns a fieldMapping object that contains only the first field of the first feature layer in the input layer list
    
    **Description:**
        Processing speeds may increase by eliminating unnecessary table fields. In addition, output file size will be
        reduced saving as much disk space as possible.
        
        This function will construct a fieldMapping object with only one field object, the minimum allowed. It will be the
        first field from the first layer in the input layerList parameter. Using a fieldMapping object, as opposed to 
        arcpy.DeleteField, is a more efficient way of deleting unnecessary/unwanted fields from an attribute table.
        
    **Arguments:**
        * *layerList* - one or more feature class to extract a single field for the fieldMappings object.
        
    **Returns:**
        * *fieldMappings* - fieldMappings object consisting of one FieldMap
    '''
    fieldMappings = arcpy.FieldMappings()
    fieldMappings.addTable(layerList[0])
    fmFields = fieldMappings.fields
    firstName = fmFields[0].name
    [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name != firstName]
    
    return fieldMappings

# def nearRoadsBuffer(inRoadFeature,metricConst,cleanupList,timer,inRoadWidthOption,widthLinearUnit="",laneCntFld="",laneWidth="",laneDistFld="",
#                     removeLinesYN,cutoffLength,bufferDist,roadClass=""):
#     '''This function calculates roads near streams by first buffering a streams layer by the desired distance
#     and then intersecting that buffer with a roads feature class.  This metric measures the total 
#     length of roads within the buffer distance divided by the total length of stream in the reporting unit, both lengths 
#     are measured in map units (e.g., m of road/m of stream).
#     '''
#     import os
#     from arcpy import env
#     from .. import errors
#     from ..constants import errorConstants
#
#     try:
#         # Create a copy of the road feature class that we can add new fields to for calculations. 
#         # This is more appropriate than altering the user's input data.
#         desc = arcpy.Describe(inRoadFeature)
#         tempName = "%s_%s" % (metricConst.shortName, desc.baseName)
#         tempRoadFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
#         fieldMappings = arcpy.FieldMappings()
#         fieldMappings.addTable(inRoadFeature)
#
#         AddMsg("%s Creating a working copy of %s..." % (timer.now(), os.path.basename(inRoadFeature)))
#
#         if inRoadWidthOption == "Distance":
#             [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.required != True]
#             inRoadFeature = arcpy.FeatureClassToFeatureClass_conversion(inRoadFeature,env.workspace,os.path.basename(tempRoadFeature),"",fieldMappings)
#
#             AddMsg("%s Adding field, HalfWidth, and calculating its value... " % (timer.now()))   
#             halfRoadWidth = float(widthLinearUnit.split()[0]) / 2
#             halfLinearUnit = "'%s %s'" % (str(halfRoadWidth), widthLinearUnit.split()[1]) # put linear unit string in quotes
#             arcpy.AddField_management(inRoadFeature, 'HalfWidth', 'TEXT')
#             AddMsg("...    HalfWidth = %s" % (halfLinearUnit))
#             arcpy.CalculateField_management(inRoadFeature, 'HalfWidth', halfLinearUnit)
#
#         elif inRoadWidthOption == "Field: Lane Count":
#             [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name != laneCntFld]
#             inRoadFeature = arcpy.FeatureClassToFeatureClass_conversion(inRoadFeature,env.workspace,os.path.basename(tempRoadFeature),"",fieldMappings)
#
#             AddMsg("%s Adding fields, HalfValue and HalfWidth, and calculating their values... " % (timer.now()))
#             arcpy.AddField_management(inRoadFeature, 'HalfValue', 'DOUBLE')
#             calcExpression = "!%s! * %s / 2" % (str(laneCntFld), laneWidth.split()[0])
#             AddMsg("...    HalfValue = %s" % (calcExpression))
#             arcpy.CalculateField_management(inRoadFeature, 'HalfValue', calcExpression, 'PYTHON_9.3')
#
#             arcpy.AddField_management(inRoadFeature, 'HalfWidth', 'TEXT')
#             calcExpression2 = "'!%s! %s'" % ('HalfValue', laneWidth.split()[1]) # put linear unit string in quotes
#             AddMsg("...    HalfWidth = %s" % (calcExpression2))
#             arcpy.CalculateField_management(inRoadFeature, 'HalfWidth', calcExpression2, 'PYTHON_9.3')
#
#         else:
#             [fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name != laneDistFld]
#             inRoadFeature = arcpy.FeatureClassToFeatureClass_conversion(inRoadFeature,env.workspace,os.path.basename(tempRoadFeature),"",fieldMappings)
#
#
#             # input field should be a linear distance string. Part 0 = distance value. Part 1 = distance units
#             try:
#                 AddMsg("%s Adding fields, HalfValue and HalfWidth, and calculating their values... " % (timer.now()))
#
#                 arcpy.AddField_management(inRoadFeature, 'HalfValue', 'DOUBLE')
#                 calcExpression = "float(!%s!.split()[0]) / 2" % (laneDistFld)
#                 AddMsg("...    HalfValue = %s" % (calcExpression))
#                 arcpy.CalculateField_management(inRoadFeature, 'HalfValue', calcExpression, 'PYTHON_9.3')
#
#                 arcpy.AddField_management(inRoadFeature, 'HalfWidth', 'TEXT')
#                 #conjunction = '+" "+'
#                 #calcExpression2 = "str(!%s!)%s!%s!.split()[1]" % ('HalfValue', conjunction, laneDistFld)
#                 calcExpression2 = "str(!%s!)+' '+!%s!.split()[1]" % ('HalfValue', laneDistFld)
#                 AddMsg("...    HalfWidth = %s" % (calcExpression2))
#                 arcpy.CalculateField_management(inRoadFeature, 'HalfWidth', calcExpression2, 'PYTHON_9.3')
#
#             except:
#                 raise errors.attilaException(errorConstants.linearUnitFormatError)
#
#
#         AddMsg("%s Buffer road feature using the value in HALFWIDTH with options FULL, FLAT, ALL..." % (timer.now()))
#         tempName = "%s_%s" % (metricConst.shortName, '1_RoadEdge')
#         edgeBufferFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
#         arcpy.Buffer_analysis(inRoadFeature, edgeBufferFeature, 'HalfWidth', 'FULL', 'FLAT', 'ALL')
#
#         halfBufferValue = float(bufferDist.split()[0]) / 2
#         halfBufferUnits = bufferDist.split()[1]
#         #halfBufferDist = str(halfBufferValue)+' '+halfBufferUnits
#         halfBufferDist = "%s %s" % (halfBufferValue, halfBufferUnits)
#         AddMsg("%s Re-buffer the buffered streets %s with options FULL, FLAT, ALL..." % (timer.now(), halfBufferDist)) 
#         tempName = "%s_%s" % (metricConst.shortName, '2_RoadBuffer')
#         roadBufferFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
#         arcpy.Buffer_analysis(edgeBufferFeature, roadBufferFeature, halfBufferDist, 'FULL', 'FLAT', 'ALL')
#
#
#         # Convert the buffer into lines
#         AddMsg("%s Converting the resulting polygons into polylines -- referred to as analysis lines.--" % (timer.now()))
#         tempName = "%s_%s" % (metricConst.shortName, '3_RdBuffLine')
#         rdBuffLineFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
#         arcpy.PolygonToLine_management(roadBufferFeature, rdBuffLineFeature)
#
#
#
#         # Remove interior lines based on cut-off point
#         if removeLinesYN == "true":
#             AddMsg("%s Adding geometry attributes to polyline feature. Calculating LENGTH in METERS..." % (timer.now()))
#             try:
#                 arcpy.AddGeometryAttributes_management(rdBuffLineFeature,'LENGTH','METERS')
#                 Expression = 'LENGTH <= %s' % cutoffLength
#             except:
#                 arcpy.AddGeometryAttributes_management(rdBuffLineFeature,'LENGTH_GEODESIC','METERS')
#                 Expression = 'LENGTH_GEO <= %s' % cutoffLength
#
#
#             AddMsg("%s Deleting analysis lines that are <= %s meters in length..." % (timer.now(), cutoffLength))
#             #Expression = 'Shape_Length <= 1050'
#             #Expression = 'LENGTH <= %s' % cutoffLength
#
#             arcpy.MakeFeatureLayer_management(rdBuffLineFeature, 'BuffLine_lyr')
#             arcpy.SelectLayerByAttribute_management('BuffLine_lyr', 'NEW_SELECTION', Expression)
#             arcpy.DeleteFeatures_management('BuffLine_lyr')
#             tempName = "%s_%s" % (metricConst.shortName, '4_BuffLineUse')
#             buffLineUseFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
#             arcpy.CopyFeatures_management('BuffLine_lyr', buffLineUseFeature)
#         else:
#             buffLineUseFeature = rdBuffLineFeature
#
#         #Create Road Buffer Areas
#         ### This routine needs to be altered to convert input buffer distance units to meters ###
#         leftValue = float(bufferDist.split()[0]) - 11.5
#         leftUnits = bufferDist.split()[1]
#         leftDist = str(leftValue)+' '+leftUnits
#         AddMsg("%s Buffering the analysis line by %s with options LEFT, FLAT, ALL..." % (timer.now(), leftDist))
#         tempName = "%s_%s_" % (metricConst.shortName, '_Left_'+str(round(leftValue)))
#         leftBuffFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
#         arcpy.Buffer_analysis(buffLineUseFeature, leftBuffFeature, leftDist, 'LEFT', 'FLAT', 'ALL')
#
#         AddMsg("%s Buffering the analysis line by 11.5 meters with options RIGHT, FLAT, ALL..." % (timer.now()))
#         tempName = "%s_%s_" % (metricConst.shortName, '_Right_11')
#         rightBuffFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
#         arcpy.Buffer_analysis(buffLineUseFeature, rightBuffFeature, '11.5 Meters', 'RIGHT', 'FLAT', 'ALL')        
#
#         AddMsg("%s Merging the two buffers together and dissolving..." % (timer.now()))
#         tempName = "%s_%s" % (metricConst.shortName, '_Buff_LR')
#         mergeBuffFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
#         arcpy.Merge_management([leftBuffFeature, rightBuffFeature], mergeBuffFeature)
#
#         tempName = "%s_%s" % (metricConst.shortName, '_RoadBuffer')
#         finalBuffFeature = files.nameIntermediateFile([tempName,"FeatureClass"],cleanupList)
#         arcpy.Dissolve_management(mergeBuffFeature, finalBuffFeature)  
#
#         return finalBuffFeature, cleanupList
#
#     finally:
#         pass