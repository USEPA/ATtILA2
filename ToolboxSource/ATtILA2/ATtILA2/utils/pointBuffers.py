'''
Modify reporting unit using point buffers
Created Aug, 2012

@author: thultgren, Torrin Hultgren, hultgren.torrin@epa.gov
'''
import arcpy

inPoints = "C:/temp/ATtILA2_data/shpfiles/bufftstpts.shp"
inPolys = "C:/temp/ATtILA2_data/shpfiles/wtrshdDefinedProjection.shp"
outFC = "C:/temp/ATtILA2_data/shpfiles/buffOutput.shp"
bufferDist = "10000 Meters"
unitID = "HUC_STR" #"MULTI_ID"

def modifyReportingUnit(inPoints, inPolys, outFC, bufferDist, unitID):
    """Returns a feature class that contains only those portions of each reporting unit that are within a buffered 
        distance of a point layer
    **Description:**
        This tool intersects reporting units with circular buffers created from a point theme. The buffer size (in map 
        units) is determined by the user. A new feature class is created that can be used as a reporting unit theme to 
        calculate metrics near the points. It is useful for generating metrics near water quality sample points where 
        watersheds that drain to the sample point are available.
    **Arguments:**
        * *inPoints* - point feature class that will be buffered
        * *inPolys* - reporting units that will be used for the clip
        * *outFC* - a feature class (with full path) that will be created as the output of this tool
        * *bufferDist* - distance in the units of the spatial reference of the input data to buffer the points
        * *unitID* - a field that exists in both the inPoints and inPolys that contains a unique identifier for the
                     reporting units.  A reporting unit may have multiple points, but the fields must match.
    """
    try:
        # First perform a buffer on all the points with the specified distance.  
        # By using the "LIST" option and the unit ID field, the output contains a single multipart feature for every 
        # reporting unit.  The output is written to the user's scratch workspace.
        bufferedPts = arcpy.Buffer_analysis(inPoints,"%scratchworkspace%/bbfpts", bufferDist,"FULL","ROUND","LIST",unitID)
        
        # The script will be iterating through reporting units and using a whereclause to select each feature, so it will 
        # improve performance if we set up the right syntax for the whereclauses ahead of time.
        ptsUnitID = arcpy.AddFieldDelimiters(bufferedPts,unitID)
        plysUnitID = arcpy.AddFieldDelimiters(inPolys,unitID)
        
        # Similarly, the syntax for the whereclause depends on the type of the reporting unit ID field.  Set up a function
        # ahead of time to make this quick and efficient.  
        if arcpy.ListFields(bufferedPts,unitID)[0].type == 'String':
            # If the field type is string, enclose the value in single quotes
            def delimitPtVals(value):
                return "'" + value + "'"
        else:
            # Otherwise the string is numeric, just convert it to a Python string type for concatenation with no quotes.
            def delimitPtVals(value):
                return str(value)
        
        if arcpy.ListFields(inPolys,unitID)[0].type == 'String':
            # If the field type is string, enclose the value in single quotes
            def delimitPlyVals(value):
                return "'" + value + "'"
        else:
            # Otherwise the string is numeric, just convert it to a Python string type for concatenation with no quotes.
            def delimitPlyVals(value):
                return str(value)
        
        i = 0 # Flag used to create the outFC the first time through.
        # Create a Search cursor to iterate through the reporting units with buffered points.
        Rows = arcpy.SearchCursor(bufferedPts,"","",unitID)
        # For each reporting unit:
        for row in Rows:
            # Get the reporting unit ID
            rowID = row.getValue(unitID)
            # Set up the whereclause for the buffered points and the reporting units to select one of each
            whereClausePts = ptsUnitID + " = " + delimitPtVals(rowID)
            whereClausePolys = plysUnitID + " = " + delimitPlyVals(rowID)
            
            # Create an in-memory Feature Layer with the whereclause.  This is analogous to creating a map layer with a 
            # definition expression.
            arcpy.MakeFeatureLayer_management(bufferedPts,"buff_lyr",whereClausePts)
            arcpy.MakeFeatureLayer_management(inPolys,"poly_lyr",whereClausePolys)
            if i == 0: # If it's the first time through
                # Clip the buffered points using the reporting unit boundaries, and save the output as the specified output
                # feature class.
                arcpy.Clip_analysis("buff_lyr","poly_lyr",outFC,"#")
                i = 1 # Toggle the flag.
            else: # If it's not the first time through and the output feature class already exists
                # Perform the clip, but output the result to memory rather than writing to disk
                clipResult = arcpy.Clip_analysis("buff_lyr","poly_lyr","in_memory/buff","#")
                # Append the in-memory result to the output feature class
                arcpy.Append_management(clipResult,outFC,"NO_TEST")
                # Delete the in-memory result to conserve system resources
                arcpy.Delete_management(clipResult)
            # Delete the in-memory Feature Layers.  
            arcpy.Delete_management("buff_lyr")
            arcpy.Delete_management("poly_lyr")
    
    finally:
        # Clean up the search cursor object
        del Rows
        # Delete the temporary buffered points layer from the scratch workspace.  
        arcpy.Delete_management(bufferedPts)
