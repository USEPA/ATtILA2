""" Utilities specific to vectors

"""

import arcpy, pylet, files
from pylet.arcpyutil.messages import AddMsg
from pylet.arcpyutil.fields import valueDelimiter
from arcpy.sa.Functions import SetNull


def bufferFeaturesByID(inFeatures, repUnits, outFeatures, bufferDist, ruIDField, ruLinkField):
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
        
    **Returns:**
        * *outFeatures* - output feature class 
    """
    try:
        # Get a unique name with full path for the output features - will default to current workspace:
        outFeatures = arcpy.CreateScratchName(outFeatures,"","FeatureClass")
        
        # First perform a buffer on all the points with the specified distance.  
        # By using the "LIST" option and the unit ID field, the output contains a single multipart feature for every 
        # reporting unit.  The output is written to the user's scratch workspace.
        AddMsg("Buffering input features...")
        bufferedFeatures = arcpy.Buffer_analysis(inFeatures,"in_memory/bFeats", bufferDist,"FULL","ROUND","LIST",ruLinkField)
        
        # If the input features are polygons, we need to erase the the input polyons from the buffer output
        inGeom = arcpy.Describe(inFeatures).shapeType
        if inGeom == "Polygon":
            AddMsg("Erasing polygon areas from buffer areas...")
            newBufferFeatures = arcpy.Erase_analysis(bufferedFeatures,inFeatures,"in_memory/bFeats2")
            arcpy.Delete_management(bufferedFeatures)
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
        loopProgress = pylet.arcpyutil.messages.loopProgress(n)

        i = 0 # Flag used to create the outFeatures the first time through.
        # Create a Search cursor to iterate through the reporting units with buffered features.
        Rows = arcpy.SearchCursor(bufferedFeatures,"","",ruLinkField)
        AddMsg("Clipping buffered features to each reporting unit...")
        # For each reporting unit:
        for row in Rows:
            # Get the reporting unit ID
            rowID = row.getValue(ruLinkField)
            # Set up the whereclause for the buffered features and the reporting units to select one of each
            whereClausePts = buffUnitID + " = " + delimitBuffValues(rowID)
            whereClausePolys = repUnitID + " = " + delimitRUValues(rowID)
            
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

# def bufferFeaturesByIntersect_old(inFeatures, repUnits, outFeatures, bufferDist, unitID):
#     """Returns a feature class that contains only those portions of each reporting unit that are within a buffered 
#         distance of a layer - the buffered features may be any geometry
#     **Description:**
#         This tool intersects reporting units with buffered features that fall within the reporting unit. The buffer size (in map 
#         units) is determined by the user. A new feature class is created that can be used as a reporting unit theme to 
#         calculate metrics with the buffered areas. It is useful for generating metrics near streams that fall within the
#         reporting unit.
#         
#         This tool makes the assumption that there is no attribute that links the features to be buffered with the 
#         reporting units.  Because of this, it cannot buffer all the features at once - it must iterate through each
#         reporting unit, first clipping features to the reporting unit boundaries, then buffering only those features
#         and then finally clipping the buffers again to the reporting unit.  If the features can be linked to reporting
#         units via an attribute, it should be faster to use the bufferFeaturesByID tool instead.
#     **Arguments:**
#         * *inFeatures* - one or more feature class that will be buffered
#         * *repUnits* - reporting units that will be used for the clip
#         * *outFeatures* - a feature class (without full path) that will be created as the output of this tool
#         * *bufferDist* - distance in the units of the spatial reference of the input data to buffer
#         * *unitID* - a field that exists in repUnits that contains a unique identifier for the reporting units.  
#         
#     **Returns:**
#         * *outFeatures* - output feature class 
#     """
#     try:
#         
#         # Get a unique name with full path for the output features - will default to current workspace:
#         outFeatures = arcpy.CreateScratchName(outFeatures,"","FeatureClass")
#         
#         inFeaturesList = inFeatures.split(";")
#         inFeatGeomDict = {}
#         for inFC in inFeaturesList:
#             inFeatGeomDict[inFC] = arcpy.Describe(inFC).shapeType
#         
#         # The script will be iterating through reporting units and using a whereclause to select each feature, so it will 
#         # improve performance if we set up the right syntax for the whereclauses ahead of time.
#         repUnitID = arcpy.AddFieldDelimiters(repUnits,unitID)
#         delimitRUValues = valueDelimiter(arcpy.ListFields(repUnits,unitID)[0].type)
#         
#         # Get the properties of the unit ID field
#         uIDField = arcpy.ListFields(repUnits,unitID)[0]
#         pylet.arcpyutil.fields.convertFieldTypeKeyword(uIDField)
#         
#         # Get a count of the number of reporting units to give an accurate progress estimate.
#         n = int(arcpy.GetCount_management(repUnits).getOutput(0))
#         # Initialize custom progress indicator
#         loopProgress = pylet.arcpyutil.messages.loopProgress(n)
#         
#         i = 0 # Flag used to create the outFeatures the first time through.
#         # Create a Search cursor to iterate through the reporting units.
#         Rows = arcpy.SearchCursor(repUnits,"","",unitID)
#         
#         AddMsg("Buffering riparian features in each reporting unit")
#         # For each reporting unit:
#         for row in Rows:            
#             
#             # Get the reporting unit ID
#             rowID = row.getValue(unitID)
#             # Set up the whereclause for the reporting units to select one
#             whereClausePolys = repUnitID + " = " + delimitRUValues(rowID)
#             
#             # Create an in-memory Feature Layer with the whereclause.  This is analogous to creating a map layer with a 
#             # definition expression.
#             arcpy.MakeFeatureLayer_management(repUnits,"ru_lyr",whereClausePolys)
#             
#             # Initialize list of buffered features to merge
#             bufferList = []
#             # Initialize list of polygon features for erase
#             eraseList = []
#             # Initialize a counter to help with naming intermediate results
#             j = 1
#             
#             # For each input Feature Class:
#             for inFC in inFeaturesList:
#                 jStr = str(j) #string version of the counter
#                 # Clip the features that should be buffered to this reporting unit, and output the result to memory.
#                 clipResult = arcpy.Clip_analysis(inFC,"ru_lyr","in_memory/clip" + jStr,"#")
#                 
#                 if inFeatGeomDict[inFC] == "Polygon":
#                     eraseList.append(clipResult)
#                 
#                 # Buffer these in-memory selected features and merge the output into a single multipart feature
#                 bufferResult = arcpy.Buffer_analysis(clipResult,"in_memory/clip_buffer" + jStr,bufferDist,"FULL","ROUND","ALL","#")
#                 
#                 # Add this result to the list of buffered features
#                 bufferList.append(bufferResult)               
#                 
#                 j += 1 # increment counter
#                
#             if len(inFeaturesList) > 1:
#                 try:
#                     # Union all of the buffered features
#                     unionBuffer = arcpy.Union_analysis(bufferList,"in_memory/union_buffer","ONLY_FID")
#                 except:
#                     badList = []
#                     for aResult in bufferList:
#                         badBuffer = arcpy.FeatureClassToFeatureClass_conversion(aResult,"%scratchworkspace%","badBuffer")
#                         # There is a small chance that this buffer operation will produce a feature class with invalid geometry.  Try a repair.
#                         arcpy.RepairGeometry_management(badBuffer,"DELETE_NULL")
#                         badList.append(badBuffer)
#                         unionBuffer = arcpy.Union_analysis(badList,"in_memory/union_buffer","ONLY_FID")
#                 
#                     arcpy.Delete_management(badBuffer)
#                     
#                 # Dissolve the union layer
#                 bufferResult = arcpy.Dissolve_management(unionBuffer,"in_memory/dissolve_union")
#             else:
#                 bufferResult = bufferList[0]
# 
#             # If the input features are polygons, we need to remove the interior polygons from the buffer areas.
#             # Investigate alternate approach (with license check) of "OUTSIDE_ONLY" option in Buffer_analysis
#             try:
#                 for eraseFeatures in eraseList:
#                     newBufferResult = arcpy.Erase_analysis(bufferResult,eraseFeatures,"in_memory/erase_buffer")
#                     arcpy.Delete_management(bufferResult)
#                     bufferResult = newBufferResult
#             except:
#                 for eraseFeatures in eraseList:
#                     badEraseFeatures = arcpy.FeatureClassToFeatureClass_conversion(eraseFeatures,"%scratchworkspace%","badEraseFeatures")
#                     badBuffer = arcpy.FeatureClassToFeatureClass_conversion(bufferResult,"%scratchworkspace%","badBuffer")
#                     # There is a small chance that this buffer operation will produce a feature class with invalid geometry.  Try a repair.
#                     arcpy.RepairGeometry_management(badBuffer,"DELETE_NULL")
#                     arcpy.RepairGeometry_management(badEraseFeatures,"DELETE_NULL")
#                     
#                     newBufferResult = arcpy.Erase_analysis(badBuffer,badEraseFeatures,"in_memory/erase_buffer")
#                     arcpy.Delete_management(bufferResult)
#                     bufferResult = newBufferResult
#                     
#                     arcpy.Delete_management(badBuffer)
#                     arcpy.Delete_management(badEraseFeatures)
#                                   
#             
#                 
#             # Add a field to this output that will contain the reporting unit ID so that when we merge the buffers
#             # the reporting unit IDs will be maintained.  
#             arcpy.AddField_management(bufferResult,uIDField.name,uIDField.type,uIDField.precision,uIDField.scale,
#                                       uIDField.length,uIDField.aliasName,uIDField.isNullable,uIDField.required,
#                                       uIDField.domain)
#             arcpy.CalculateField_management(bufferResult, uIDField.name,'"' + str(rowID) + '"',"PYTHON")
#             
#             # Because of the potential for invalid geometries in the buffered features, embed the clip in a try 
#             # statement to catch and handle errors.
#             try:
#                 if i == 0: # If it's the first time through
#                     # Clip the buffered points using the reporting unit boundaries, and save the output as the specified output
#                     # feature class.
#                     arcpy.Clip_analysis(bufferResult,"ru_lyr",outFeatures,"#")
#                     i = 1 # Toggle the flag.
#                 else: # If it's not the first time through and the output feature class already exists
#                     # Perform the clip, but output the result to memory rather than writing to disk
#                     clipResult2 = arcpy.Clip_analysis(bufferResult,"ru_lyr","in_memory/finalclip","#")
#                     # Append the in-memory result to the output feature class
#                     arcpy.Append_management(clipResult2,outFeatures,"NO_TEST")
#                     # Delete the in-memory result to conserve system resources
#                     arcpy.Delete_management(clipResult2)
#             except:
#                 badBuffer = arcpy.FeatureClassToFeatureClass_conversion(bufferResult,"%scratchworkspace%","badbuffer")
#                 # There is a small chance that this buffer operation will produce a feature class with invalid geometry.  Try a repair.
#                 arcpy.RepairGeometry_management(badBuffer,"DELETE_NULL")
#                 if i == 0: # If it's the first time through
#                     # Clip the buffered points using the reporting unit boundaries, and save the output as the specified output
#                     # feature class.
#                     arcpy.Clip_analysis(badBuffer,"ru_lyr",outFeatures,"#")
#                     i = 1 # Toggle the flag.
#                 else: # If it's not the first time through and the output feature class already exists
#                     # Perform the clip, but output the result to memory rather than writing to disk
#                     clipResult2 = arcpy.Clip_analysis(badBuffer,"ru_lyr","in_memory/finalclip","#")
#                     # Append the in-memory result to the output feature class
#                     arcpy.Append_management(clipResult2,outFeatures,"NO_TEST")
#                     # Delete the in-memory result to conserve system resources
#                     arcpy.Delete_management(clipResult2)
#                 arcpy.Delete_management(badBuffer)
# 
#             arcpy.Delete_management("in_memory") # Clean up all in-memory data created for this reporting unit
#             arcpy.Delete_management("ru_lyr")
#             loopProgress.update()
#     
#         return outFeatures
#     
#     finally:
#         try:
#             # Clean up the search cursor object
#             del Rows
#         except:
#             pass 

def bufferFeaturesByIntersect(inFeatures, repUnits, outFeatures, bufferDist, unitID, cleanupList):
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
        
    **Returns:**
        * *outFeatures* - output feature class 
    """
    from arcpy import env
    import os
    
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
        outputList = []
        # Initialize list of polygon features for erase
        eraseList = []        
        
        for inFC in inFeaturesList:
            inFCDesc = arcpy.Describe(inFC)
            inFCName = inFCDesc.baseName
            if inFCDesc.shapeType == "Polygon":
                eraseList.append(inFC)
            
            if inFCDesc.HasM or inFCDesc.HasZ:
                AddMsg("Creating a copy of "+inFCName+" without M or Z values")
                copyFCNameBase = toolShortName+"_"+inFCName
                copyFCName = files.nameIntermediateFile([copyFCNameBase,"FeatureClass"], cleanupList)
                inFC = arcpy.FeatureClassToFeatureClass_conversion(inFC, env.workspace, os.path.basename(copyFCName))
                inFCDesc = arcpy.Describe(inFC)
                inFCName = inFCDesc.baseName
            else:
                inFCName = toolShortName+"_"+inFCDesc.baseName
            
            # Start by intersecting the input features and the reporting units 
            AddMsg("Intersecting "+inFCDesc.baseName+" and reporting units")
            firstIntersectionName = files.nameIntermediateFile([inFCName+"_intersect","FeatureClass"], cleanupList)
            intersectResult = arcpy.Intersect_analysis([repUnits,inFC],firstIntersectionName,"ALL","","INPUT")
            
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
            else:
                # Get the properties of the unitID field
                fromFieldObj = arcpy.ListFields(intersectResult,unitID)[0]
                # Add the new field to the output table with the appropriate properties and the valid name
                arcpy.AddField_management(intersectResult,newUnitID,fromFieldObj.type,fromFieldObj.precision,fromFieldObj.scale,
                          fromFieldObj.length,fromFieldObj.aliasName,fromFieldObj.isNullable,fromFieldObj.required,
                          fromFieldObj.domain)
                # Copy the field values from the old to the new field
                arcpy.CalculateField_management(intersectResult,newUnitID,arcpy.AddFieldDelimiters(intersectResult,unitID))

            # Buffer these in-memory selected features and merge the output into multipart features by reporting unit ID
            AddMsg("Buffering intersected features")
            bufferName = files.nameIntermediateFile([inFCName+"_buffer","FeatureClass"],cleanupList)
            
            # If the input features are polygons, we need to erase the the input polygons from the buffer output
            inGeom = inFCDesc.shapeType
            if inGeom == "Polygon":
                # When we buffer polygons, we want to exclude the area of the polygon itself.  This can be done using the 
                # "OUTSIDE_ONLY" option in the buffer tool, but that is only available with an advanced license.  Check for
                # the right license level, revert to buffer/erase option if it's not available.
                licenseLevel = arcpy.CheckProduct("ArcInfo")
                if licenseLevel in ["AlreadyInitalized ","Available"]:
                    bufferResult = arcpy.Buffer_analysis(intersectResult,bufferName,bufferDist,"OUTSIDE_ONLY","ROUND","LIST",[newUnitID])
                    AddMsg("Repairing buffer areas for input areal features...")
                    arcpy.RepairGeometry_management (bufferResult)
                else:
                    bufferResult = arcpy.Buffer_analysis(intersectResult,bufferName,bufferDist,"FULL","ROUND","LIST",[newUnitID])
                    AddMsg("Repairing buffer areas for input areal features...")
                    arcpy.RepairGeometry_management (bufferResult)
                    AddMsg("Erasing polygon areas from buffer areas...")
                    bufferErase = files.nameIntermediateFile([inFCName+"_bufferErase","FeatureClass"],cleanupList)
                    newBufferFeatures = arcpy.Erase_analysis(bufferResult,inFC,bufferErase)
                    bufferResult = newBufferFeatures
            else:
                bufferResult = arcpy.Buffer_analysis(intersectResult,bufferName,bufferDist,"FULL","ROUND","LIST",[newUnitID])
                AddMsg("Repairing buffer areas for input linear features...")
                arcpy.RepairGeometry_management (bufferResult)
            
            
            # Intersect the buffers with the reporting units
            AddMsg("Intersecting buffer features and reporting units")
            secondIntersectionName = files.nameIntermediateFile([inFCName+"_2ndintersect","FeatureClass"],cleanupList)
            secondIntersectResult = arcpy.Intersect_analysis([repUnits,bufferResult],secondIntersectionName,"ALL","","INPUT")            

            # Select only those intersected features whose reporting unit IDs match 
            # This ensures that buffer areas that fall outside of the input feature's reporting unit are excluded
            AddMsg("Trimming buffer zones to reporting unit boundaries")
            whereClause = arcpy.AddFieldDelimiters(secondIntersectResult,unitID) + " = " + arcpy.AddFieldDelimiters(secondIntersectResult,newUnitID)
            matchingBuffers = arcpy.MakeFeatureLayer_management(secondIntersectResult,"matchingBuffers",whereClause)

            # Dissolve those by reporting Unit ID.  
            AddMsg("Dissolving second intersection by reporting unit")
            if len(inFeaturesList) > 1:
                finalOutputName = files.nameIntermediateFile([inFCName+"_finalOutput","FeatureClass"],cleanupList)
            else: 
                finalOutputName = outFeatures # If this is the only one, it's already named.
            finalOutput = arcpy.Dissolve_management(matchingBuffers,finalOutputName,unitID)
            
            # Clean up the feature layer selection for the next iteration.
            arcpy.Delete_management(matchingBuffers)
            
            # keep track of list of outputs.  
            outputList.append(finalOutput)
        
        # merge and dissolve buffer features from all input feature classes into a single feature class.
        if len(inFeaturesList) > 1:
            AddMsg("Merging buffer zones from all input Stream features")
            mergeName = files.nameIntermediateFile(["mergeOutput","FeatureClass"],cleanupList)
            mergeOutput = arcpy.Merge_management(outputList,mergeName)
            finalOutput = arcpy.Dissolve_management(mergeOutput,outFeatures,unitID)
            # If any of the input features are polygons, we need to perform a final erase of the interior of these polygons from the output.
            AddMsg("Removing interior waterbody areas from buffer result")
            if len(eraseList) > 0:
                #  Merge all eraseFeatures so we only have to do this once...
                eraseName = files.nameIntermediateFile(["erasePolygons","FeatureClass"],cleanupList)
                eraseFeatureClass = arcpy.Merge_management(eraseList,eraseName)
                # Rename the old final output so that it becomes an intermediate dataset
                oldfinalOutputName = files.nameIntermediateFile([outFeatures+"_preErase","FeatureClass"],cleanupList)
                preEraseOutput = arcpy.Rename_management(finalOutput, oldfinalOutputName, "FeatureClass")
                try:
                    finalOutput = arcpy.Erase_analysis(preEraseOutput,eraseFeatureClass,outFeatures)
                except:
                    badEraseFeatures = arcpy.FeatureClassToFeatureClass_conversion(eraseFeatureClass,"%scratchworkspace%","badEraseFeatures")
                    badBuffer = arcpy.FeatureClassToFeatureClass_conversion(preEraseOutput,"%scratchworkspace%","badBuffer")
                    # There is a small chance that this buffer operation will produce a feature class with invalid geometry.  Try a repair.
                    arcpy.RepairGeometry_management(badBuffer,"DELETE_NULL")
                    arcpy.RepairGeometry_management(badEraseFeatures,"DELETE_NULL")
                    finalOutput = arcpy.Erase_analysis(badBuffer,badEraseFeatures,outFeatures)
                    arcpy.Delete_management(badBuffer)
                    arcpy.Delete_management(badEraseFeatures)
        
        return finalOutput, cleanupList 
    finally:
        pass

# def splitDissolveMerge_old(lines,repUnits,uIDField,mergedLines,lineClass='#'):
#     '''This function performs a split, dissolve, and merge function on a set of line features.
#     **Description:**
#         This function iterates through a set of areal units, clipping line features to each unit, then dissolving those
#         lines (preserving different classes of lines, if that option is chosen, assigning the dissolved line features 
#         the ID of the areal unit, and then merges the multipart dissolved lines back into a single output feature class. 
#         The clipped and dissolved linear features are all stored in-memory, rather than written to disk, to improve 
#         performance.  Only when the features are merged/appended into a final output feature class are they written to 
#         disk.   
#     **Arguments:**
#         * *lines* - the input line feature class
#         * *repUnits* - the input representative areal units feature class that will be used to split the lines
#         * *uIDField* - the ID field of the representative areal units feature class.  Each dissolved line feature will be assigned the respective uID
#         * *lineClass* - optional field containing class values for the line feature class.  these classes are preserved through the split/dissolve/merge process
#         * *mergedLines* - name of the output feature class.
#     **Returns:**
#         * *mergedLines* - name of the output feature class.
#         * *lengthFieldName* - validated name of the field in the output feature class containing length values
#     '''
#     # The script will be iterating through reporting units and using a whereclause to select each feature, so it will 
#     # improve performance if we set up the right syntax for the whereclauses ahead of time.
#     repUnitID = arcpy.AddFieldDelimiters(repUnits,uIDField.name)
#     delimitRUValues = valueDelimiter(arcpy.ListFields(repUnits,uIDField.name)[0].type)
#     
#     # Get the properties of the unit ID field
#     pylet.arcpyutil.fields.convertFieldTypeKeyword(uIDField)
# 
#     # Get a count of the number of reporting units to give an accurate progress estimate.
#     n = int(arcpy.GetCount_management(repUnits).getOutput(0))
#     # Initialize custom progress indicator
#     loopProgress = pylet.arcpyutil.messages.loopProgress(n)
#        
#     i = 0 # Flag used to create the outFeatures the first time through.
#     # Create a Search cursor to iterate through the reporting units.
#     Rows = arcpy.SearchCursor(repUnits,"","",uIDField.name)
#     AddMsg("Clipping and dissolving linear features in each reporting unit...")
#     
#     # For each reporting unit:
#     for row in Rows:            
#         
#         # Get the reporting unit ID
#         rowID = row.getValue(uIDField.name)
#         # Set up the whereclause for the reporting units to select one
#         whereClausePolys = repUnitID + " = " + delimitRUValues(rowID)
# 
#         # Create an in-memory Feature Layer with the whereclause.  This is analogous to creating a map layer with a 
#         # definition expression.
#         ruLayer = arcpy.MakeFeatureLayer_management(repUnits,"ru_lyr",whereClausePolys)
#         
#         # Clip the features that should be buffered to this reporting unit, and output the result to memory.
#         clipResult = arcpy.Clip_analysis(lines,ruLayer,"in_memory/clip","#").getOutput(0)
#         # Dissolve the lines to get one feature per reporting unit (per line class, if a line class is given)
#         dissolveResult = arcpy.Dissolve_management(clipResult,"in_memory/dissolve",lineClass,"#","MULTI_PART",
#                                                    "DISSOLVE_LINES").getOutput(0)
#         # Add a field to this output shapefile that will contain the reporting unit ID (also the name of the shapefile)
#         # so that when we merge the shapefiles the ID will be preserved
#         arcpy.AddField_management(dissolveResult,uIDField.name,uIDField.type,uIDField.precision,uIDField.scale,
#                                   uIDField.length,uIDField.aliasName,uIDField.isNullable,uIDField.required,
#                                   uIDField.domain)
#         arcpy.CalculateField_management(dissolveResult, uIDField.name,'"' + str(rowID) + '"',"PYTHON")
#        
#         if i == 0: # If it's the first time through
#             # Save the output as the specified output feature class.
#             arcpy.CopyFeatures_management(dissolveResult,mergedLines)
#             i = 1 # Toggle the flag.
#         else: # If it's not the first time through and the output feature class already exists
#             # Append the in-memory result to the output feature class
#             arcpy.Append_management(dissolveResult,mergedLines,"NO_TEST")
#         
#         # Clean up intermediate datasets
#         arcpy.Delete_management(ruLayer)
#         arcpy.Delete_management(clipResult)
#         arcpy.Delete_management(dissolveResult)
#         loopProgress.update()
#     
#     ## Add and calculate a length field for the new shapefile
#     lengthFieldName = addLengthField(mergedLines)
#     return mergedLines, lengthFieldName

def splitDissolveMerge(lines,repUnits,uIDField,mergedLines,inLengthField,lineClass=''):
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
    # Intersect the lines and the areal units
    # intersection = arcpy.Intersect_analysis([repUnits, lines],r"in_memory/intersect","ALL","","INPUT")
    # using previous technique of an output layer stored in memory is not dependable for large input datasets

    # Get a unique name with full path for the output features - will default to current workspace:
    intersectFeatures = arcpy.CreateScratchName("tmpIntersect","","FeatureClass")
    intersection = arcpy.Intersect_analysis([repUnits, lines],intersectFeatures,"ALL","","INPUT")
    dissolveFields = uIDField.name
    if lineClass <> '':
        dissolveFields = [uIDField.name, lineClass]
    
    # Dissolve the intersected lines on the unit ID (and optional line class) fields. 
    arcpy.Dissolve_management(intersection,mergedLines,dissolveFields,"","MULTI_PART","DISSOLVE_LINES")
    
    arcpy.Delete_management(intersection)
    ## Add and calculate a length field for the new shapefile
    lengthFieldName = addLengthField(mergedLines,inLengthField)
    return mergedLines, lengthFieldName

def findIntersections(mergedRoads,inStreamFeature,mergedStreams,ruID,roadStreamMultiPoints,roadStreamIntersects,roadStreamSummary,
                      streamLengthFieldName,xingsPerKMFieldName,roadClass=""):
    '''This function performs an intersection analysis on two input line feature classes.  The desired output is 
    a count of the number of intersections per reporting unit ID (both line feature classes already contain this ID).  
    To obtain this cout the intersection output is first converted to singlepart features (from the default of multipart
    and then a frequency analysis performed.
    '''

    # Intersect the roads and the streams - the output is a multipoint feature class with one feature per combination 
    # of road class and streams per reporting unit
    arcpy.Intersect_analysis([mergedRoads,inStreamFeature],roadStreamMultiPoints,"ALL","#","POINT")
    
    # Because we want a count of individual intersection features, break apart the multipoints into single points
    arcpy.MultipartToSinglepart_management(roadStreamMultiPoints,roadStreamIntersects)
    
    # Perform a frequency analysis to get a count of the number of crossings per class per reporting unit
    fieldList = [ruID.name]
    if roadClass:
        fieldList.append(roadClass)
    arcpy.Frequency_analysis(roadStreamIntersects,roadStreamSummary,fieldList)
    
    # Lastly, calculate the number of stream crossings per kilometer of streams.
    # Join the stream layer to the summary table
    arcpy.JoinField_management(roadStreamSummary, ruID.name, mergedStreams, ruID.name, [streamLengthFieldName])
    # Set up a calculation expression for crossings per kilometer.
    calcExpression = "!FREQUENCY!/!" + streamLengthFieldName + "!"    
    addCalculateField(roadStreamSummary,xingsPerKMFieldName,calcExpression)

def roadsNearStreams(inStreamFeature,mergedStreams,bufferDist,inRoadFeature,inReportingUnitFeature,streamLengthFieldName,ruID,streamBuffer,
                     tmp1RdsNearStrms,tmp2RdsNearStrms,roadsNearStreams,rnsFieldName,inLengthField,roadClass=""):
    '''This function calculates roads near streams by first buffering a streams layer by the desired distance
    and then intersecting that buffer with a roads feature class.  This metric measures the total 
    length of roads within the buffer distance divided by the total length of stream in the reporting unit, both lengths 
    are measured in map units (e.g., m of road/m of stream).
    '''
    # For RNS metric, first buffer all the streams by the desired distance
    AddMsg("Buffering stream features...")
    arcpy.Buffer_analysis(inStreamFeature,streamBuffer,bufferDist,"FULL","ROUND","ALL","#")
    # Intersect the stream buffers with the input road layer to find road segments in the buffer zone
    AddMsg("Intersecting road features with stream buffers...")
    intersect1 = arcpy.Intersect_analysis([inRoadFeature, streamBuffer],tmp1RdsNearStrms,"ALL","#","INPUT")
    # Intersect the roads in the buffer zones with the reporting unit feature to assign RU Id values to road segments
    AddMsg("Assigning reporting unit feature ID values to road segments...")
    intersect2 = arcpy.Intersect_analysis([intersect1, inReportingUnitFeature],tmp2RdsNearStrms,"ALL","#","INPUT")
    
    # if overlapping polygons exist in reporting unit theme, the above intersection may result in several rows of data for a given reporting unit.
    # perform a dissolve to get a 1 to 1 relationship with input to output. Include the class field if provided.
    arcpy.AddMessage("Dissolving intersection result and calculating values...")
    dissolveFields = ruID.name
    if roadClass <> '':
        dissolveFields = [ruID.name, roadClass] 
    # Dissolve the intersected lines on the unit ID (and optional line class) fields.
    arcpy.Dissolve_management(intersect2,roadsNearStreams,dissolveFields, "#","MULTI_PART","DISSOLVE_LINES")
    
    arcpy.Delete_management(intersect1)
    arcpy.Delete_management(intersect2)
    
    # Add and calculate a length field for the new shapefile
    roadLengthFieldName = addLengthField(roadsNearStreams,inLengthField)
    
    # Next join the merged streams layer to the roads/streambuffer intersection layer
    arcpy.JoinField_management(roadsNearStreams, ruID.name, mergedStreams, ruID.name, [streamLengthFieldName])
    # Set up a calculation expression for the roads near streams fraction
    calcExpression = "!" + roadLengthFieldName + "!/!" + streamLengthFieldName + "!"
    # Add a field for the roads near streams fraction
    rnsFieldName = addCalculateField(roadsNearStreams,rnsFieldName,calcExpression)


def addAreaField(inAreaFeatures, areaFieldName):
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
    areaFieldName = addCalculateField(inAreaFeatures,areaFieldName,calcExpression)
    return areaFieldName    

def addLengthField(inLineFeatures,lengthFieldName):
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
    # Set a default for the length fieldName
    #lengthFieldName = "LenKM" + lineDescription.baseName
    
    # Set up the calculation expression for length in kilometers
    calcExpression = "!{0}.LENGTH@KILOMETERS!".format(lineDescription.shapeFieldName)
    lengthFieldName = addCalculateField(inLineFeatures,lengthFieldName,calcExpression)
    return lengthFieldName

def addCalculateField(inFeatures,fieldName,calcExpression,codeBlock='#'):
    '''This function checks for the existence of the desired field, and if it does not exist, adds and populates it
    using the given calculation expression
    **Description:**
        This function checks for the existence of the specified field and if it does
        not exist, adds and populates it as appropriate.  The output field is assumed to be of type double.
    **Arguments:**
        * *inFeatures* - the input feature class that will receive the field.
        * *fieldName* - field name string
        * *calcExpression* - string calculation expression in python 
        * *codeBlock* - optional python code block expression       
    **Returns:**
        * *fieldName* - validated fieldname      
    '''
    # Validate the desired field name for the dataset
    fieldName = arcpy.ValidateFieldName(fieldName, arcpy.Describe(inFeatures).path)
    
    # Check for existence of field.
    fieldList = arcpy.ListFields(inFeatures,fieldName)
    if not fieldList: # if the list of fields that exactly match the validated fieldname is empty, then add the field
        arcpy.AddField_management(inFeatures,fieldName,"DOUBLE")
    else: # Otherwise warn the user that the field will be recalculated.
        AddMsg("The field {0} already exists in {1}, its values will be recalculated.".format(fieldName,inFeatures))
    arcpy.CalculateField_management(inFeatures,fieldName,calcExpression,"PYTHON",codeBlock)
    return fieldName      

# def tabulateMDCP_old(PatchLURaster, TempOutspace, ReportingUnitFeature, ReportingUnitField, SearchRadius, rastoPoly, rastoPt, 
#                  polyDiss, clipPolyDiss, nearPatchTable):
#     from arcpy import env
#     resultDict = {}
#     #Convert Final Patch Raster to polygon
# ##    env.workspace = os.path.dirname(PatchLURaster)
# #    arcpy.RasterToPolygon_conversion(PatchLURaster, TempOutspace + "\\FinalPatch_polygon", "NO_Simplify", "VALUE")
#     arcpy.RasterToPolygon_conversion(PatchLURaster, rastoPoly, "NO_Simplify", "VALUE")
#     #Convert Final Patch Raster to points to get the cell centroids
#     arcpy.RasterToPoint_conversion(PatchLURaster, rastoPt, "VALUE")
# 
#     env.workspace = TempOutspace
#     
#     #Dissolve the polygons on Value Field to make sure each patch is represented by a single polygon.
#     arcpy.Dissolve_management(rastoPoly, polyDiss,"grid_code","#",
#                               "MULTI_PART","DISSOLVE_LINES")  
#     
#     #Get a list of Reporting Unit Feature ids
#     idlist = []
#     rows = arcpy.SearchCursor(ReportingUnitFeature)
# 
#     for row in rows:
#         ruid = row.getValue(ReportingUnitField)
#         idlist.append(ruid)
#     del row, rows  
# #    print idlist
#     
#     #Select the Reporting Unit and the intersecting polygons in FinalPatch_poly_diss
#     for i in idlist:
#         AddMsg("Generating Mean Distances for " + i)
#         squery = ReportingUnitField + "='" + i + "'"
#         #Create a feature layer of the single reporting unit
#         arcpy.MakeFeatureLayer_management(ReportingUnitFeature,"subwatersheds_Layer",squery,"#")
# 
#         #Create a feature layer of the FinalPatch_poly_diss
#         arcpy.MakeFeatureLayer_management(polyDiss, "FinalPatch_diss_Layer")
# 
#         #Create a feature layer of the FinalPatch_centroids
#         arcpy.MakeFeatureLayer_management(rastoPt, "FinalPatch_centroids_Layer")
# 
#         #Select the centroids that are in the "subwatersheds_Layer"
#         arcpy.SelectLayerByLocation_management("FinalPatch_centroids_Layer","INTERSECT","subwatersheds_Layer")
#         
#         #Get a list of centroids within the selected Reporting Unit (this is necessary to match the raster processing
#         #selection which selects only grid cells whose center is within the reporting unit).
#         rows = arcpy.SearchCursor("FinalPatch_centroids_Layer")
#         centroidList = []
#         for row in rows:
#             gridid = row.getValue("Grid_Code")
#             if str(gridid) not in centroidList:
#                 centroidList.append(str(gridid))
# 
#         totalnumPatches = len(centroidList)
#         del row, rows  
#           
#         # Select the patches that have centroids within the "subwatershed_Layer" using the centroid list
#         values = ",".join(centroidList)
#         arcpy.SelectLayerByAttribute_management("FinalPatch_diss_Layer", "NEW_SELECTION", "GRID_CODE IN(" + values + ")")
#         arcpy.Clip_analysis("FinalPatch_diss_Layer","subwatersheds_Layer", clipPolyDiss)
#         #Calculate Near Distances for each watershed
# #        arcpy.GenerateNearTable_analysis("FinalPatch_diss_Layer",["FinalPatch_diss_Layer"], "neartable",
# #                                         SearchRadius,"NO_LOCATION","NO_ANGLE","CLOSEST","0")
#         arcpy.GenerateNearTable_analysis(clipPolyDiss,[clipPolyDiss], nearPatchTable,
#                                          SearchRadius,"NO_LOCATION","NO_ANGLE","CLOSEST","0")   
#         #Get total number of patches with neighbors and calculate the mean distance
#         try:
#             rows = arcpy.SearchCursor(nearPatchTable)
#             distlist = []
#             for row in rows:
#                 distance = row.getValue("NEAR_DIST")
#                 distlist.append(distance)
#             del row, rows
#             pwnCount = len(distlist)
#             totalArea = sum(distlist)
#             meanDist = totalArea/pwnCount
#             pwonCount = totalnumPatches - pwnCount
#         except:
#             #if near table is empty the set values to default -999
#             rowcount = int(arcpy.GetCount_management(nearPatchTable).getOutput(0))
#             if rowcount == 0:
#                 arcpy.AddWarning("No patches within search radius found for " + i)
#                 pwnCount = -999
#                 pwonCount = -999
#                 meanDist = -999    
#             else:
#                 AddMsg("Near Distance failed for some reason other than search distance")
#         resultDict[i] = str(pwnCount) +  "," + str(pwonCount) +"," + str(meanDist)
#     return resultDict
    
# def tabulateMDCPOperational(PatchLURaster, inReportingUnitFeature, reportingUnitIdField, rastoPoly, rastoPt, 
#                  polyDiss, clipPolyDiss, nearPatchTable, zoneAreaDict, timer):
#     from pylet import arcpyutil
#     resultDict = {}
#     
#     # put the proper field delimiters around the ID field name for SQL expressions
#     delimitedField = arcpy.AddFieldDelimiters(inReportingUnitFeature, reportingUnitIdField)
#     
#     #Convert Final Patch Raster to polygon
#     AddMsg(timer.split() + " Converting raster patches to polygons...")
#     patchOnlyRaster = SetNull(PatchLURaster, PatchLURaster, "VALUE <= 0")
#     arcpy.RasterToPolygon_conversion(patchOnlyRaster, rastoPoly, "NO_Simplify", "VALUE")
#     
#     #Convert Final Patch Raster to points to get the cell centroids
#     arcpy.RasterToPoint_conversion(patchOnlyRaster, rastoPt, "VALUE")
#     
#     #Create a feature layer of the FinalPatch_centroids
#     arcpy.MakeFeatureLayer_management(rastoPt, "FinalPatch_centroids_Layer")
#     
#     #Dissolve the polygons on Value Field to make sure each patch is represented by a single polygon.
#     AddMsg(timer.split() + " Dissolving patch polygons by value field...")
#     arcpy.Dissolve_management(rastoPoly, polyDiss,"gridcode","#", "MULTI_PART","DISSOLVE_LINES")
#     
#     #Create a feature layer of the FinalPatch_poly_diss
#     arcpy.MakeFeatureLayer_management(polyDiss, "FinalPatch_diss_Layer")
#     
#     # Initialize custom progress indicator
#     totalRUs = len(zoneAreaDict)
#     mdcpLoopProgress = arcpyutil.messages.loopProgress(totalRUs)
#     
#    
#     #Select the Reporting Unit and the intersecting polygons in FinalPatch_poly_diss
#     AddMsg(timer.split() + " Analyzing MDCP by reporting unit...")
#     for aZone in zoneAreaDict.keys():
#         pwnCount = 0
#         pwonCount = 0
#         meanDist = 0
#             
#         if isinstance(aZone, int): # reporting unit id is an integer - convert to string for SQL expression
#             squery = "%s = %s" % (delimitedField, str(aZone))
#         else: # reporting unit id is a string - enclose it in single quotes for SQL expression
#             squery = "%s = '%s'" % (delimitedField, str(aZone))
#         
#         #Create a feature layer of the single reporting unit
#         arcpy.MakeFeatureLayer_management(inReportingUnitFeature,"subwatersheds_Layer",squery,"#")
#         
#         #Select the centroids that are in the "subwatersheds_Layer"
#         arcpy.SelectLayerByLocation_management("FinalPatch_centroids_Layer","INTERSECT","subwatersheds_Layer")
# 
#         centroidCount = int(arcpy.GetCount_management("FinalPatch_centroids_Layer").getOutput(0))
#         
#         # Check to see if any patches exist within reporting unit
#         if centroidCount == 0:
#             arcpy.AddWarning("No patches found in " + str(aZone))
#         
#         else:
# #            #Get a list of centroids within the selected Reporting Unit (this is necessary to match the raster processing
# #            #selection which selects only grid cells whose center is within the reporting unit).
# #            rows = arcpy.SearchCursor("FinalPatch_centroids_Layer")
# #            centroidSet = set()
# #             
# #             for row in rows:
# #                 gridid = row.getValue("grid_code")
# #                 centroidSet.add(str(gridid))
# #       
# #             del row, rows
# #             totalnumPatches = len(centroidSet)
# #              
# #            # Select the patches that have centroids within the "subwatershed_Layer" using the centroid list
# #             values = ",".join(centroidSet)
# #             arcpy.AddMessage("selecting patches by grid code")
# #             arcpy.SelectLayerByAttribute_management("FinalPatch_diss_Layer", "NEW_SELECTION", "gridcode IN (" + values + ")")
# 
# 
#             # Select the patches that have selected centroids within them
#             arcpy.SelectLayerByLocation_management("FinalPatch_diss_Layer", "INTERSECT", "FinalPatch_centroids_Layer")
#             totalnumPatches = int(arcpy.GetCount_management("FinalPatch_diss_Layer").getOutput(0))
# 
#             arcpy.Clip_analysis("FinalPatch_diss_Layer","subwatersheds_Layer", clipPolyDiss)
#             
#             #Calculate Near Distances for each watershed
#             arcpy.GenerateNearTable_analysis(clipPolyDiss,[clipPolyDiss], nearPatchTable,
#                                              "","NO_LOCATION","NO_ANGLE","CLOSEST","0")
# #             arcpy.GenerateNearTable_analysis(clipPolyDiss,[clipPolyDiss], nearPatchTable,
# #                                              SearchRadius,"NO_LOCATION","NO_ANGLE","CLOSEST","0")
#              
#             #Get total number of patches with neighbors and calculate the mean distance
#             try:
#                 # Check to see if any neighboring patches are found
#                 rowcount = int(arcpy.GetCount_management(nearPatchTable).getOutput(0))
#                 if rowcount == 0: # none found
#                     # see if search radius is too short to find nearest patch for any patch
#                     if totalnumPatches > 1:
#                         arcpy.AddWarning("No patches within search radius found for " + str(aZone))
#                         pwonCount = totalnumPatches
#                      
#                 else: # found neighboring patches
#                     rows = arcpy.SearchCursor(nearPatchTable)
#                     distlist = []
#                     for row in rows:
#                         distance = row.getValue("NEAR_DIST")
#                         distlist.append(distance)
#                     del row, rows
#                     pwnCount = len(distlist)
#                     totalDist = sum(distlist)
#                     meanDist = totalDist/pwnCount
#                     pwonCount = totalnumPatches - pwnCount
#                  
#             except:
#                 AddMsg("Near Distance failed for some reason other than search distance")
#                 
#             finally:
#                 arcpy.Delete_management(nearPatchTable)
#                 arcpy.Delete_management(clipPolyDiss)
# 
#                               
#         resultDict[aZone] = str(pwnCount) +  "," + str(pwonCount) +"," + str(meanDist)
#         
#         mdcpLoopProgress.update() 
#               
#     return resultDict


# def tabulateMDCPdissolveErrors(PatchLURaster, inReportingUnitFeature, reportingUnitIdField, rastoPoly, rastoPt, 
#                  polyDiss, clipPolyDiss, nearPatchTable, zoneAreaDict, timer, pmResultsDict):
#     from pylet import arcpyutil
#     resultDict = {}
#     
#     # put the proper field delimiters around the ID field name for SQL expressions
#     delimitedField = arcpy.AddFieldDelimiters(inReportingUnitFeature, reportingUnitIdField)
#     
#     #Convert Final Patch Raster to polygon
#     AddMsg(timer.split() + " Converting raster patches to polygons...")
#     patchOnlyRaster = SetNull(PatchLURaster, PatchLURaster, "VALUE <= 0")
#     arcpy.RasterToPolygon_conversion(patchOnlyRaster, rastoPoly, "NO_Simplify", "VALUE")
#     
#     #Make feature layer of the patch polygons
#     arcpy.MakeFeatureLayer_management(rastoPoly, "Patch_Polygon_Layer")
#      
#     #Convert Final Patch Raster to points to get the cell centroids
#     AddMsg(timer.split() + " Converting raster patch cells to centroid points...")
#     arcpy.RasterToPoint_conversion(patchOnlyRaster, rastoPt, "VALUE")
#      
#     #Create a feature layer of the FinalPatch_centroids
#     arcpy.MakeFeatureLayer_management(rastoPt, "FinalPatch_centroids_Layer")
#     
# #     #Dissolve the polygons on Value Field to make sure each patch is represented by a single polygon.
# #     AddMsg(timer.split() + " Dissolving patch polygons by value field...")
# #     arcpy.Dissolve_management(rastoPoly, polyDiss,"gridcode","#", "MULTI_PART","DISSOLVE_LINES")
# #      
# #     #Create a feature layer of the FinalPatch_poly_diss
# #     arcpy.MakeFeatureLayer_management(polyDiss, "FinalPatch_diss_Layer")
# #     
# #     totalPolygonCount = int(arcpy.GetCount_management("FinalPatch_diss_Layer").getOutput(0))
# #     arcpy.AddMessage("Total Polygon Count = "+str(totalPolygonCount)) 
#     
#     # Initialize custom progress indicator
#     totalRUs = len(zoneAreaDict)
#     mdcpLoopProgress = arcpyutil.messages.loopProgress(totalRUs)
#     
#    
#     #Select the Reporting Unit and the intersecting polygons in FinalPatch_poly_diss
#     AddMsg(timer.split() + " Analyzing MDCP by reporting unit...")
#     for aZone in zoneAreaDict.keys():
#         pwnCount = 0
#         pwonCount = 0
#         meanDist = 0
#             
#         if isinstance(aZone, int): # reporting unit id is an integer - convert to string for SQL expression
#             squery = "%s = %s" % (delimitedField, str(aZone))
#         else: # reporting unit id is a string - enclose it in single quotes for SQL expression
#             squery = "%s = '%s'" % (delimitedField, str(aZone))
#         
#         #Create a feature layer of the single reporting unit
#         arcpy.MakeFeatureLayer_management(inReportingUnitFeature,"subwatersheds_Layer",squery,"#")
#         
# #         ruPatchRaster = arcpy.sa.ExtractByMask(patchOnlyRaster, "subwatersheds_Layer")
# #         
# #         #Convert RU Patch Raster to points to get the cell centroids
# # #         AddMsg(timer.split() + " Converting raster patch cells to centroid points...")
# #         arcpy.RasterToPoint_conversion(ruPatchRaster, rastoPt, "VALUE")
# #      
# #         #Create a feature layer of the FinalPatch_centroids
# #         arcpy.MakeFeatureLayer_management(rastoPt, "FinalPatch_centroids_Layer")
#         
#         #Select the centroids that are in the "subwatersheds_Layer"
#         arcpy.SelectLayerByLocation_management("FinalPatch_centroids_Layer","INTERSECT","subwatersheds_Layer")
# 
#         centroidCount = int(arcpy.GetCount_management("FinalPatch_centroids_Layer").getOutput(0))
# #         arcpy.AddMessage("centroidCount = "+str(centroidCount))
#         
#         # Check to see if any patches exist within reporting unit
#         if centroidCount == 0:
#             arcpy.AddWarning("No patches found in " + str(aZone))
#         
#         else:
#             # clip the patch polygon to the reporting unit boundary
#             arcpy.Clip_analysis(rastoPoly,"subwatersheds_Layer", "wshed_Polygons")
#             
#             #Dissolve the polygons on Value Field to make sure each patch is represented by a single polygon.
# #             arcpy.AddMessage("dissolving polygons")
#             arcpy.Dissolve_management("wshed_Polygons", "in_memory/wshed_Polygons_Diss","gridcode","#", "MULTI_PART","DISSOLVE_LINES")
#              
#             #Create a feature layer of the FinalPatch_poly_diss
#             arcpy.MakeFeatureLayer_management("in_memory/wshed_Polygons_Diss", "FinalPatch_diss_Layer")
#             
#             # Select the patches that have selected centroids within them
#             arcpy.SelectLayerByLocation_management("FinalPatch_diss_Layer", "INTERSECT", "FinalPatch_centroids_Layer")
#             totalnumPatches = int(arcpy.GetCount_management("FinalPatch_diss_Layer").getOutput(0))
# #             arcpy.AddMessage("totalnumPatches = "+str(totalnumPatches))
# 
# #            arcpy.Clip_analysis("FinalPatch_diss_Layer","subwatersheds_Layer", clipPolyDiss)
#             
#             #Calculate Near Distances for each watershed
#             arcpy.GenerateNearTable_analysis("FinalPatch_diss_Layer",["FinalPatch_diss_Layer"], nearPatchTable,
#                                              "","NO_LOCATION","NO_ANGLE","CLOSEST","0")
# #             arcpy.GenerateNearTable_analysis(clipPolyDiss,[clipPolyDiss], nearPatchTable,
# #                                              "","NO_LOCATION","NO_ANGLE","CLOSEST","0")
# #             arcpy.GenerateNearTable_analysis(clipPolyDiss,[clipPolyDiss], nearPatchTable,
# #                                              SearchRadius,"NO_LOCATION","NO_ANGLE","CLOSEST","0")
#              
#             #Get total number of patches with neighbors and calculate the mean distance
#             try:
#                 # Check to see if any neighboring patches are found
#                 rowcount = int(arcpy.GetCount_management(nearPatchTable).getOutput(0))
# #                 arcpy.AddMessage("NearTable row count = "+str(rowcount))
#                 if rowcount == 0: # none found
#                     # see if search radius is too short to find nearest patch for any patch
#                     if totalnumPatches == 1:
#                         arcpy.AddWarning("Single patch in %s. MDCP = 0" % (str(aZone)))
#                         pwonCount = totalnumPatches
#                      
#                 else: # found neighboring patches
#                     rows = arcpy.SearchCursor(nearPatchTable)
#                     distlist = []
#                     for row in rows:
#                         distance = row.getValue("NEAR_DIST")
#                         distlist.append(distance)
#                     del row, rows
#                     pwnCount = len(distlist)
#                     totalDist = sum(distlist)
#                     meanDist = totalDist/pwnCount
#                     pwonCount = totalnumPatches - pwnCount
#                  
#             except:
#                 AddMsg("Near Distance failed for some reason other than search distance")
#                 
#             finally:
#                 pass
# #                arcpy.Delete_management(nearPatchTable)
# #                arcpy.Delete_management(clipPolyDiss)
# 
#                               
#         resultDict[aZone] = str(pwnCount) +  "," + str(pwonCount) +"," + str(meanDist)
#         
#         mdcpLoopProgress.update() 
#               
#     return resultDict



def tabulateMDCP(inPatchRaster, inReportingUnitFeature, reportingUnitIdField, rastoPolyFeature, patchCentroidsFeature, 
                 patchDissolvedFeature, nearPatchTable, zoneAreaDict, timer, pmResultsDict):
    from pylet import arcpyutil
    resultDict = {}
    
    # put the proper field delimiters around the ID field name for SQL expressions
    delimitedField = arcpy.AddFieldDelimiters(inReportingUnitFeature, reportingUnitIdField)
    
    #Convert Final Patch Raster to polygon
    AddMsg(timer.split() + " Converting raster patches to polygons...")
    patchOnlyRaster = SetNull(inPatchRaster, inPatchRaster, "VALUE <= 0")
    arcpy.RasterToPolygon_conversion(patchOnlyRaster, rastoPolyFeature, "NO_Simplify", "VALUE")
    
    #Dissolve the polygons on Value Field to make sure each patch is represented by a single polygon.
    AddMsg(timer.split() + " Dissolving patch polygons by value field...")
    arcpy.Dissolve_management(rastoPolyFeature, patchDissolvedFeature,"gridcode","#", "MULTI_PART","DISSOLVE_LINES")
      
    #Create a feature layer of the FinalPatch_poly_diss
    patchDissolvedLayer = arcpy.MakeFeatureLayer_management(patchDissolvedFeature, "patchDissolvedLayer")
     
    #Convert Final Patch Raster to points to get the cell centroids
    AddMsg(timer.split() + " Converting raster patch cells to centroid points...")
    arcpy.RasterToPoint_conversion(patchOnlyRaster, patchCentroidsFeature, "VALUE")
     
    #Create a feature layer of the FinalPatch_centroids
    patchCentroidsLayer = arcpy.MakeFeatureLayer_management(patchCentroidsFeature, "patchCentroidsLayer")
    
    # Initialize custom progress indicator
    totalRUs = len(zoneAreaDict)
    mdcpLoopProgress = arcpyutil.messages.loopProgress(totalRUs)
    
    noPatches = 0
    singlePatch = 0
   
    #Select the Reporting Unit and the intersecting polygons in FinalPatch_poly_diss
    AddMsg(timer.split() + " Analyzing MDCP by reporting unit...")
    for aZone in zoneAreaDict.keys():
        pwnCount = 0
        pwonCount = 0
        meanDist = 0
            
        if isinstance(aZone, int): # reporting unit id is an integer - convert to string for SQL expression
            squery = "%s = %s" % (delimitedField, str(aZone))
        else: # reporting unit id is a string - enclose it in single quotes for SQL expression
            squery = "%s = '%s'" % (delimitedField, str(aZone))
        
        #Create a feature layer of the single reporting unit
        aReportingUnitLayer = arcpy.MakeFeatureLayer_management(inReportingUnitFeature,"aReportingUnitLayer",squery,"#")
        
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
            # clipPolyDissFeature = arcpy.Clip_analysis(patchDissolvedLayer, aReportingUnitLayer, clipPolyDiss)
            clipPolyDissFeature = arcpy.Clip_analysis(patchDissolvedLayer, aReportingUnitLayer, "in_memory/clipPolyDiss")

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
                arcpy.Dissolve_management(clipPolyDissFeature, "in_memory/wshed_Polygons_Diss","gridcode","#", "MULTI_PART","DISSOLVE_LINES")
                 
                #Create a feature layer of the newly dissolved patches
                arcpy.MakeFeatureLayer_management("in_memory/wshed_Polygons_Diss", "FinalPatch_diss_Layer")
                
                # Re-evaluate the number of patches within the reporting unit
                totalNumPatches = int(arcpy.GetCount_management("FinalPatch_diss_Layer").getOutput(0))
                
                # Generate the Near Distance table for newly dissolved patches
                arcpy.GenerateNearTable_analysis("FinalPatch_diss_Layer",["FinalPatch_diss_Layer"], nearPatchTable,
                                                 "","NO_LOCATION","NO_ANGLE","CLOSEST","0")
                
                if totalNumPatches <> pmPatches:
                    # Alert the user that the problem was not corrected
                    arcpy.AddWarning("Possible error in the number of patches foud in " + str(aZone) +" \n" + \
                                     "Calculated value for MDCP for this reporting unit is suspect")
             
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
                    distlist = []
                    for row in rows:
                        distance = row.getValue("NEAR_DIST")
                        distlist.append(distance)
                    del row, rows
                    
                    pwnCount = len(distlist)
                    totalDist = sum(distlist)
                    meanDist = totalDist/pwnCount
                    pwonCount = totalNumPatches - pwnCount
                 
            except:
                arcpy.AddWarning("Near Distance routine failed in %s" % (str(aZone)))
                meanDist = -9999
                pwnCount = -9999
                pwonCount = -9999
                
            finally:
                arcpy.Delete_management(nearPatchTable)

                              
        resultDict[aZone] = str(pwnCount) +  "," + str(pwonCount) +"," + str(meanDist)
        
        mdcpLoopProgress.update()
        
    if noPatches > 0:
        arcpy.AddWarning("%s reporting units contained no patches. MDCP was set to -9999 for these units." % (str(noPatches)))
    
    if singlePatch > 0:
        arcpy.AddWarning("%s reporting units contained a single patch. MDCP was set to 0 for these units." % (str(singlePatch)))
        
    arcpy.Delete_management(patchCentroidsLayer)
              
    return resultDict
