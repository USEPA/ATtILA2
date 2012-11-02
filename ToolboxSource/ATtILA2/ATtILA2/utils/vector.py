""" Utilities specific to vectors

"""

import arcpy, pylet

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
        * *unitID* - a field that exists in both the inFeatures and repUnits that contains a unique identifier for the
                     reporting units.  A reporting unit may have multiple features, but the fields must match.
    """
    try:
        # Get a unique name with full path for the output features - will default to current workspace:
        outFeatures = arcpy.CreateScratchName(outFeatures,"","FeatureClass")
        
        # First perform a buffer on all the points with the specified distance.  
        # By using the "LIST" option and the unit ID field, the output contains a single multipart feature for every 
        # reporting unit.  The output is written to the user's scratch workspace.
        bufferedFeatures = arcpy.Buffer_analysis(inFeatures,"%scratchworkspace%/bFeats", bufferDist,"FULL","ROUND","LIST",ruLinkField)
        
        # The script will be iterating through reporting units and using a whereclause to select each feature, so it will 
        # improve performance if we set up the right syntax for the whereclauses ahead of time.
        buffUnitID = arcpy.AddFieldDelimiters(bufferedFeatures,ruLinkField)
        repUnitID = arcpy.AddFieldDelimiters(repUnits,ruIDField)
        
        # Similarly, the syntax for the whereclause depends on the type of the reporting unit ID field. 
        delimitBuffValues = valueDelimiter(arcpy.ListFields(bufferedFeatures,ruLinkField)[0].type)
        delimitRUValues = valueDelimiter(arcpy.ListFields(repUnits,ruIDField)[0].type)

        i = 0 # Flag used to create the outFeatures the first time through.
        # Create a Search cursor to iterate through the reporting units with buffered features.
        Rows = arcpy.SearchCursor(bufferedFeatures,"","",ruLinkField)
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
    
        return outFeatures
    
    finally:
        # Clean up the search cursor object
        del Rows
        # Delete the temporary buffered features layer from the scratch workspace.  
        arcpy.Delete_management(bufferedFeatures)

def bufferFeaturesByIntersect(inFeatures, repUnits, outFeatures, bufferDist, unitID):
    """Returns a feature class that contains only those portions of each reporting unit that are within a buffered 
        distance of a layer - the buffered features may be any geometry
    **Description:**
        This tool intersects reporting units with buffered features that fall within the reporting unit. The buffer size (in map 
        units) is determined by the user. A new feature class is created that can be used as a reporting unit theme to 
        calculate metrics with the buffered areas. It is useful for generating metrics near streams that fall within the
        reporting unit.
    **Arguments:**
        * *inFeatures* - feature class that will be buffered
        * *repUnits* - reporting units that will be used for the clip
        * *outFeatures* - a feature class (without full path) that will be created as the output of this tool
        * *bufferDist* - distance in the units of the spatial reference of the input data to buffer
        * *unitID* - a field that exists in repUnits that contains a unique identifier for the reporting units.  
    """
    try:
        
        # Get a unique name with full path for the output features - will default to current workspace:
        outFeatures = arcpy.CreateScratchName(outFeatures,"","FeatureClass")
        
        # The script will be iterating through reporting units and using a whereclause to select each feature, so it will 
        # improve performance if we set up the right syntax for the whereclauses ahead of time.
        repUnitID = arcpy.AddFieldDelimiters(repUnits,unitID)
        delimitRUValues = valueDelimiter(arcpy.ListFields(repUnits,unitID)[0].type)
        
        # Get the properties of the unit ID field
        uIDField = arcpy.ListFields(repUnits,unitID)[0]
        pylet.arcpyutil.fields.convertFieldTypeKeyword(uIDField)
        
        i = 0 # Flag used to create the outFeatures the first time through.
        # Create a Search cursor to iterate through the reporting units.
        Rows = arcpy.SearchCursor(repUnits,"","",unitID)
        # For each reporting unit:
        for row in Rows:
            # Get the reporting unit ID
            rowID = row.getValue(unitID)
            # Set up the whereclause for the reporting units to select one
            whereClausePolys = repUnitID + " = " + delimitRUValues(rowID)
            
            # Create an in-memory Feature Layer with the whereclause.  This is analogous to creating a map layer with a 
            # definition expression.
            arcpy.MakeFeatureLayer_management(repUnits,"ru_lyr",whereClausePolys)
            # Clip the features that should be buffered to this reporting unit, and output the result to memory.
            clipResult = arcpy.Clip_analysis(inFeatures,"ru_lyr","in_memory/clip1","#")
            # Buffer these in-memory selected features and merge the output into a single multipart feature
            bufferResult = arcpy.Buffer_analysis(clipResult,"in_memory/clip_buffer",bufferDist,"FULL","ROUND","ALL","#")
            # Add a field to this output that will contain the reporting unit ID so that when we merge the buffers
            # the reporting unit IDs will be maintained.  
            arcpy.AddField_management(bufferResult,uIDField.name,uIDField.type,uIDField.precision,uIDField.scale,
                                      uIDField.length,uIDField.aliasName,uIDField.isNullable,uIDField.required,
                                      uIDField.domain)
            arcpy.CalculateField_management(bufferResult, uIDField.name,'"' + str(rowID) + '"',"PYTHON")
            
            if i == 0: # If it's the first time through
                # Clip the buffered points using the reporting unit boundaries, and save the output as the specified output
                # feature class.
                arcpy.Clip_analysis(bufferResult,"ru_lyr",outFeatures,"#")
                i = 1 # Toggle the flag.
            else: # If it's not the first time through and the output feature class already exists
                # Perform the clip, but output the result to memory rather than writing to disk
                clipResult2 = arcpy.Clip_analysis(bufferResult,"ru_lyr","in_memory/clip2","#")
                # Append the in-memory result to the output feature class
                arcpy.Append_management(clipResult2,outFeatures,"NO_TEST")
                # Delete the in-memory result to conserve system resources
                arcpy.Delete_management(clipResult2)
            # Delete the in-memory Feature Layers.  
            arcpy.Delete_management(bufferResult)
            arcpy.Delete_management(clipResult)
            arcpy.Delete_management("ru_lyr")
    
        return outFeatures
    
    finally:
        # Clean up the search cursor object
        del Rows

def valueDelimiter(fieldType):
    '''Utility for adding the appropriate delimiter to a value in a whereclause.'''
    if fieldType == 'String':
        # If the field type is string, enclose the value in single quotes
        def delimitValue(value):
            return "'" + value + "'"
    else:
        # Otherwise the string is numeric, just convert it to a Python string type for concatenation with no quotes.
        def delimitValue(value):
            return str(value)
    return delimitValue
