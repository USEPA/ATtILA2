'''
Calculate Road Density Metrics
Created on Sep 14, 2012

@author: thultgren, Torrin Hultgren, hultgren.torrin@epa.gov
'''

import arcpy, os, sys, time
from  pylet.datetimeutil import DateTimer

def updateFieldProps(field):
    ''' This function translates the properties returned by the field describe function into the 
        parameters expected by the AddField tool'''
    typeDictionary = {"SmallInteger":"SHORT","Integer":"LONG","Single":"FLOAT","Double":"DOUBLE","String":"TEXT",
                      "Date":"DATE","OID":"GUID","Blob":"BLOB"}
    field.type = typeDictionary[field.type]
    nullDictionary = {True:"NULLABLE",False:"NON_NULLABLE"}
    field.isNullable = nullDictionary[field.isNullable]
    requiredDictionary = {True:"REQUIRED",False:"NON_REQUIRED"}
    field.required = requiredDictionary[field.required]
    return field

def makeTextID(field,table):
    # add a new and calculate a new text field for the unit ID
    textFieldName = arcpy.ValidateFieldName("txt" + field.name, table)
    arcpy.AddField_management(table,textFieldName,"TEXT","","",30)
    arcpy.CalculateField_management(table, textFieldName,'!'+ field.name +'!',"PYTHON")
    return textFieldName

def createScratchFolder(folderName,templatePath):
    ''' This function traverses the hierarchy provided in the templatePath and finds the next highest path
        where a new scratch folder can be created.  This scratch workspace must be a folder, because reporting
        unit IDs are frequently numeric, and the split function assigns these IDs to the output filenames, and only
        shapefiles can handle filenames that start with a number.  The folderName is assigned to the new folder.'''
    targetPath = ""
    while targetPath == "":
        if arcpy.Describe(arcpy.Describe(templatePath).Path).dataType == u'Folder':
            # If this is a Folder, then we can make the scratch folder here.
            targetPath = arcpy.Describe(templatePath).Path
        else:
            # Go one level up the path and try again.
            templatePath = arcpy.Describe(templatePath).Path
    # Make sure the foldername is unique
    folderName = os.path.basename(arcpy.CreateUniqueName(folderName, targetPath))
    # Create the folder and return the full path
    return arcpy.CreateFolder_management(targetPath, folderName).getOutput(0)

def calculateLength(lines):
    ## Add and calculate a length field for the new shapefile
    lengthFieldName = arcpy.Describe(lines).baseName + "Length"
    lengthFieldName = arcpy.ValidateFieldName(lengthFieldName, lines)
    arcpy.AddField_management(lines,lengthFieldName,"DOUBLE","#","#","#","#","NON_NULLABLE","NON_REQUIRED","#")
    calcExpression = "!" + arcpy.Describe(lines).shapeFieldName + ".LENGTH@KILOMETERS!"
    arcpy.CalculateField_management(lines, lengthFieldName,calcExpression,"PYTHON")
    return lengthFieldName

def splitDissolveMerge(lines,repUnits,uIDField,lineClass,mergedLines):
    timer = DateTimer()
    AddMsg(timer.start())
    # Create a scratch folder for the split lines
    splitFolder = createScratchFolder("split" + arcpy.Describe(lines).baseName,lines)
    
    AddMsg("Splitting " + lines)
    AddMsg(time.strftime("%#c",time.localtime()))
    # Split the Lines feature class by the reporting units - output will be individual shapefiles 
    # whose names equal the reporting unit ID values
    arcpy.Split_analysis(lines,repUnits,uIDField.name,splitFolder,"#")
    
    AddMsg("Split complete, beginning dissolve")
    AddMsg(timer.split())
    
    # Get a list of the output feature classes
    arcpy.env.workspace = splitFolder
    splitLinesList = arcpy.ListFeatureClasses()
    
    # Assign a second scratch folder for the dissolve outputs
    dissolveFolder = createScratchFolder("dissolve" + arcpy.Describe(lines).baseName,lines)
    for splitLine in splitLinesList:
        # Get the filename properties of the shapefile to help determine the name of the dissolve output
        descLines = arcpy.Describe(splitLine)
        dissolveFileName = descLines.baseName + "_dissolve." + descLines.extension
        dissolveFile = os.path.join(dissolveFolder,dissolveFileName)
        AddMsg("Dissolving " + descLines.baseName)
        AddMsg(timer.split())
        # Dissolve the lines to get one feature per reporting unit (per line class, if a line class is given)
        arcpy.Dissolve_management(splitLine,dissolveFile,lineClass,"#","MULTI_PART","DISSOLVE_LINES")
        # Add a field to this output shapefile that will contain the reporting unit ID (also the name of the shapefile)
        # so that when we merge the shapefiles the ID will be preserved
        arcpy.AddField_management(dissolveFile,uIDField.name,uIDField.type,uIDField.precision,uIDField.scale,
                                  uIDField.length,uIDField.aliasName,uIDField.isNullable,uIDField.required,
                                  uIDField.domain)
        arcpy.CalculateField_management(dissolveFile, uIDField.name,'"' + descLines.baseName + '"',"PYTHON")
    
    # Get a list of the output feature classes
    arcpy.env.workspace = dissolveFolder
    dissolvedLineList = arcpy.ListFeatureClasses()
    AddMsg("Merging " + mergedLines)
    AddMsg(timer.split())
    # Merge the dissolved roads back together
    mergedLines = arcpy.Merge_management(dissolvedLineList, mergedLines).getOutput(0)
    
    ## Add and calculate a length field for the new shapefile
    lengthFieldName = calculateLength(mergedLines)

    AddMsg("Done merging, cleaning up...")
    AddMsg(timer.stop())
    
    # Clean up intermediate datasets
    arcpy.Delete_management(splitFolder)
    arcpy.Delete_management(dissolveFolder)
    AddMsg(timer.stop())
    return mergedLines, lengthFieldName

import pylet
from pylet.arcpyutil.messages import AddMsg

def splitDissolveMerge2(lines,repUnits,uIDField,lineClass,mergedLines):
    timer = DateTimer()
    AddMsg(timer.start())    
    # The script will be iterating through reporting units and using a whereclause to select each feature, so it will 
    # improve performance if we set up the right syntax for the whereclauses ahead of time.
    repUnitID = arcpy.AddFieldDelimiters(repUnits,uIDField.name)
    AddMsg(repUnitID)
    delimitRUValues = valueDelimiter(arcpy.ListFields(repUnits,uIDField.name)[0].type)
    
    # Get the properties of the unit ID field
    pylet.arcpyutil.fields.convertFieldTypeKeyword(uIDField)
    
    AddMsg("Splitting " + lines)
    AddMsg(time.strftime("%#c",time.localtime()))
    
    i = 0 # Flag used to create the outFeatures the first time through.
    # Create a Search cursor to iterate through the reporting units.
    Rows = arcpy.SearchCursor(repUnits,"","",uIDField.name)

    AddMsg("Performing a cut/dissolve/append for features in each reporting unit")
    # For each reporting unit:
    for row in Rows:            
        
        # Get the reporting unit ID
        rowID = row.getValue(uIDField.name)
        # Set up the whereclause for the reporting units to select one
        whereClausePolys = repUnitID + " = " + delimitRUValues(rowID)
        AddMsg(whereClausePolys)
        # Create an in-memory Feature Layer with the whereclause.  This is analogous to creating a map layer with a 
        # definition expression.
        arcpy.MakeFeatureLayer_management(repUnits,"ru_lyr",whereClausePolys)

        # Clip the features that should be buffered to this reporting unit, and output the result to memory.
        clipResult = arcpy.Clip_analysis(lines,"ru_lyr","in_memory/clip","#")
        # Dissolve the lines to get one feature per reporting unit (per line class, if a line class is given)
        dissolveResult = arcpy.Dissolve_management(clipResult,"in_memory/dissolve",lineClass,"#","MULTI_PART","DISSOLVE_LINES")
        # Add a field to this output shapefile that will contain the reporting unit ID (also the name of the shapefile)
        # so that when we merge the shapefiles the ID will be preserved
        arcpy.AddField_management(dissolveResult,uIDField.name,uIDField.type,uIDField.precision,uIDField.scale,
                                  uIDField.length,uIDField.aliasName,uIDField.isNullable,uIDField.required,
                                  uIDField.domain)
        arcpy.CalculateField_management(dissolveResult, uIDField.name,'"' + str(rowID) + '"',"PYTHON")
       
        if i == 0: # If it's the first time through
            # Save the output as the specified output feature class.
            arcpy.CopyFeatures_management(dissolveResult,mergedLines)
            i = 1 # Toggle the flag.
        else: # If it's not the first time through and the output feature class already exists
            # Append the in-memory result to the output feature class
            arcpy.Append_management(dissolveResult,mergedLines,"NO_TEST")
        
        # Clean up intermediate datasets
        arcpy.Delete_management("ru_lyr")
        arcpy.Delete_management(clipResult)
        arcpy.Delete_management(dissolveResult)

    ## Add and calculate a length field for the new shapefile
    lengthFieldName = calculateLength(mergedLines)
    AddMsg(timer.stop())
    return mergedLines, lengthFieldName

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

def main(_argv):
    """To Do:
        link to toolbox - handle optional parameters
        Configure single output workspace
        distinguish between products and intermediates - handle optional cleanup of intermediates
        Can we produce single summary output table?
        Standardize naming conventions - and clarify departures from ATtILA1
            In summary output table, need to ensure dedicated field per road class.
        Determine what code from normal metric calculation can be used, if any, or if this will be completely independent
        Bring documentation in line with Michael's standard syntax
        remove (archive?) old code
        write module for any frequently repeated code (add/calculate field seems likely candidate)
        standardize messaging.
    """
    
    # User Input
    #===================================================================================================================
    # inRoads = r"C:\temp\ATtILA2_data\shpfiles\mainrds.shp"
    # inStreams = r"C:\temp\ATtILA2_data\shpfiles\streams.shp"
    # inUnits = r"C:\temp\ATtILA2_data\shpfiles\wtrshdDefinedProjection.shp"
    # roadClass = "CLASS"
    # unitID = "HUC_STR"
    # unitArea = "AREA"
    # bufferDist = "30"
    #===================================================================================================================

    inRoads = r"C:\temp\ATtILA2_data\Ohio\Shapefiles\roads_study.shp"
    inStreams = r"C:\temp\ATtILA2_data\Ohio\Shapefiles\nhd_msite.shp"
    inUnits = r"C:\temp\ATtILA2_data\Ohio\TestPolygons\poly_testset_no_slivers.shp"
    roadClass = ""
    unitID = "ID_USE1"
    bufferDist = "30"

    # Get the field properties for the unitID, this will be frequently used
    uIDField = arcpy.ListFields(inUnits,unitID)[0]
    textIDFlag = 0
    if (uIDField.type <> "String"):
        textIDFlag = 1
        unitID = makeTextID(uIDField,inUnits)
        uIDField = arcpy.ListFields(inUnits,unitID)[0]
    uIDField = updateFieldProps(uIDField)
    
    # Add a field to the reporting units to hold the area value in square kilometers
    unitArea = arcpy.ValidateFieldName("AREAKM2", inUnits)
    arcpy.AddField_management(inUnits,unitArea,"DOUBLE","#","#","#","#","NON_NULLABLE","NON_REQUIRED","#")
    calcExpression = "!" + arcpy.Describe(inUnits).shapeFieldName + ".AREA@SQUAREKILOMETERS!"
    arcpy.CalculateField_management(inUnits,unitArea,calcExpression,"PYTHON")
    
    # Get a unique name for the merged roads:
    mergedRoads = arcpy.CreateScratchName("RdsByRU","","FeatureClass",arcpy.Describe(inRoads).path)
    
    # First perform the split/dissolve/merge on the roads
    mergedRoads, roadLengthFieldName = splitDissolveMerge2(inRoads,inUnits,uIDField,roadClass,mergedRoads)

    ## Add a field for the road density
    densityFieldName = arcpy.ValidateFieldName("RDDENS", mergedRoads)
    arcpy.AddField_management(mergedRoads,densityFieldName,"DOUBLE","#","#","#","#","NON_NULLABLE","NON_REQUIRED","#")
   
    # Next join the reporting units layer to the merged roads layer
    arcpy.JoinField_management(mergedRoads, unitID, inUnits, unitID, [unitArea])
    calcExpression = "!" + roadLengthFieldName + "!/!" + unitArea + "!"  
    arcpy.CalculateField_management(mergedRoads, densityFieldName, calcExpression,"PYTHON")

    ## Add a field for the road density regression for total impervious area
    pctiaFieldName = arcpy.ValidateFieldName("PCTIA_RD", mergedRoads)
    arcpy.AddField_management(mergedRoads,pctiaFieldName,"DOUBLE","#","#","#","#","NON_NULLABLE","NON_REQUIRED","#")
 
    # Calculate the road density linear regression for total impervious area:
    calcExpression = "pctiaCalc(!" + densityFieldName + "!)"
    codeblock = """def pctiaCalc(RdDensity):
    pctia = ((RdDensity - 1.78) / 0.16)
    if (RdDensity < 1.79):
        return 0
    elif (RdDensity > 11):
        return -1
    else:
        return pctia"""
    arcpy.CalculateField_management(mergedRoads, pctiaFieldName, calcExpression,"PYTHON",codeblock)
    
    # Get a unique name for the merged streams:
    mergedStreams = arcpy.CreateScratchName("StrByRU","","FeatureClass",arcpy.Describe(inStreams).path)
    
    # Next perform the split/dissolve/merge on the streams
    mergedStreams, streamLengthFieldName = splitDissolveMerge2(inStreams,inUnits,uIDField,"#",mergedStreams)
    
    # Get a unique name for the road/stream intersections:
    roadStreamMultiPoints = arcpy.CreateScratchName("roadStreamMultiPoints","","FeatureClass",arcpy.Describe(inUnits).path)
    # Intersect the roads and the streams - the output is a multipoint feature class with one feature per combination 
    # of road class and streams per reporting unit
    arcpy.Intersect_analysis([mergedRoads,mergedStreams],roadStreamMultiPoints,"ALL","#","POINT")
    
    # Because we want a count of individual intersection features, break apart the multipoints into single points
    roadStreamIntersects = arcpy.CreateScratchName("PtsOfXing","","FeatureClass",arcpy.Describe(inUnits).path)
    arcpy.MultipartToSinglepart_management(roadStreamMultiPoints,roadStreamIntersects)
    
    # Perform a frequency analysis to get a count of the number of crossings per class per reporting unit
    roadStreamSummary = arcpy.CreateScratchName("roadStreamSummary","","Dataset",arcpy.Describe(inUnits).path)
    fieldList = [unitID]
    if roadClass:
        fieldList.append(roadClass)
    arcpy.Frequency_analysis(roadStreamIntersects,roadStreamSummary,fieldList)
    
    # For RNS metric, first buffer all the streams by the desired distance
    streamBuffer = arcpy.CreateScratchName("streamBuffer","","FeatureClass",arcpy.Describe(inStreams).path)
    arcpy.Buffer_analysis(inStreams,streamBuffer,bufferDist,"FULL","ROUND","ALL","#")
    # Intersect the buffered streams with the merged roads
    roadStreamBuffer = arcpy.CreateScratchName("roadStreamBuffer","","FeatureClass",arcpy.Describe(inUnits).path)
    arcpy.Intersect_analysis([mergedRoads,streamBuffer],roadStreamBuffer,"ALL","#","INPUT")
    ## Add and calculate a length field for the new shapefile
    calculateLength(roadStreamBuffer)
    
    ## Add a field for the roads near streams fraction
    rnsFieldName = arcpy.ValidateFieldName("RNS", roadStreamBuffer)
    arcpy.AddField_management(roadStreamBuffer,rnsFieldName,"DOUBLE","#","#","#","#","NON_NULLABLE","NON_REQUIRED","#")
    
    # Next join the merged streams layer to the roads/streambuffer intersection layer
    arcpy.JoinField_management(roadStreamBuffer, unitID, mergedStreams, unitID, [streamLengthFieldName])
    calcExpression = "!" + roadLengthFieldName + "!/!" + streamLengthFieldName + "!"
    arcpy.CalculateField_management(roadStreamBuffer, rnsFieldName, calcExpression,"PYTHON")

    # Cleanup the text ID Field if it was created
    if textIDFlag:
        arcpy.DeleteField_management(inUnits,unitID)
    # Cleanup the square kilometers field.
    arcpy.DeleteField_management(inUnits,unitArea)

if __name__ == "__main__":
    try:    
        main(sys.argv)
    except Exception, e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "Line %i" % tb.tb_lineno
        print e.message



'''
-Split roads FC by reporting units
-dissolve roads based on class
-add column for reporting unit ID and populate
-merge all dissolved FCs.
-add column for road length and populate
-join to reporting units and calculate density

-split streams by reporting unit
-dissolve streams within each reporting unit
-add column for reporting unit ID and populate
-merge all dissolved features
-add column for stream length and populate


Intersect road and stream dissolved features with MultiPoint output.
Multipart to singlepart point output
Count Frequency of points per class per reporting unit.

Combine into single output table.

RNS - buffer all streams, intersect buffer with dissolved/merged roads
Calculate total length of output and length of roads/total stream length.


Avenue Documentation:
 Road Density Metrics

Total road length (RDLEN) is reported in map units (usually meters). Road density (RDDENS) is reported as total road 
length in km divided by area of reporting unit in square kilometers. Stream/Road crossings (STXRD) calculates two 
metrics, the total number of stream/road crossings in the reporting unit (STXRD_CNT) and the density as number of 
crossings per stream kilometer in the reporting unit (STXRD). If a road class field is provided in the Human Stressors 
Dialog, ATtILA will also calculate each road density metric described above as well as the RNS metric described below 
for each road class found within the roads theme. For example, if there are two road classes coded within the roads 
theme and the STXRD metric is selected, ATtILA will calculate the number of roads/stream crossings per kilometer of 
stream within the reporting unit as well as the number of road/stream crossings per kilometer of stream for road class 
1 and for road class 2. The output field name will have "C[CLASS]" appended. In this example, for road class 1, the 
road/stream crossings per kilometer of stream field name will be STXRDC1. For road class 2, the field name will be 
STXRDC2.

Due to the impervious nature of roads, petroleum products, antifreeze and other vehicle related chemicals, as well as 
road salt and sediment are washed away in storm runoff. When roads are near streams, very often this runoff enters 
surface water directly. Roads near streams (RNS) requires a buffer distance, measured in projected map units if the 
view is projected, or native map units if not. In most cases, map units will be meters. This metric measures the total 
length of roads within the buffer distance divided by the total length of stream in the reporting unit, both lengths 
are measured in map units (e.g., m of road/m of stream).

Caution: RNS can be extremely computationally intensive. You may want to run a few selected reporting units as a test 
before using your entire data set. 

Output Options:
Metric values only" will not save any intermediate data sets required for the calculations. Values will be added to new 
fields in the reporting unit attribute table, or overwrite values if the field already exists. Any fields that were 
overwritten will be displayed in a list when processing is complete, and be included in the metadata file. This is the 
default and recommended choice.

"Metric values and maps" will generate and save values as above, but will also save intermediate themes required to 
calculate the selected metrics (where applicable). An example for the AgtSL (total agriculture on steep slopes) metric 
would be a grid where a 1 represents any agriculture class on steep slopes and a zero represents other land cover types 
and agriculture on slopes below the minimum slope threshold. Detailed information is available in Appendix 3.

Road density can be highly correlated with population density. Therefore, high road density generally corresponds to 
larger amounts of developed land cover and increased amounts of impervious surface. PCTIA_RD uses road density as the 
independent variable in a linear regression model to calculate impervious surface (see May, et al., 1997). Road density 
is calculated as km of road per km2 of reporting unit area. Due to the nature of the regression equation used for 
PCTIA_RD, values below 1.8 are assigned a value of 0, values above 11 km/km2 are considered invalid and will be reported 
as -1. 


Road/stream metrics 
RDDENS, RDLEN, PCTIA_RD Description  A polyline shapefile that consists of all roads (selections are ignored) within the reporting unit(s) of interest, clipped to the reporting unit boundary, and assigned the id of the reporting unit the road segment is located within. If a road class field is specified, the road class attribute is copied to the road feature in the new theme.  
Extent  The extent of the road features within the reporting unit(s) of interest.  
Cell size  n/a  
Attributes  Length, reporting unit ID, road class code (if specified).  
Theme Name  Roads by Reporting Unit  
File Name  rurds+{n}, where n is the value generated by ArcView's MakeTmp request.  


STXRD 

This metric will generate two separate shapefiles (Streams by Reporting Unit shapefile and Points of Crossing shapefile) with the following characteristics: 

Streams by Reporting Unit Description  A polyline shapefile that consists of all streams (selections are ignored) within the reporting unit(s) of interest, clipped to the reporting unit boundary, and assigned the id of the reporting unit the stream segment is located within. If a stream order field is specified, the stream order attribute is copied to the stream feature in the new theme.  
Extent  The extent of the stream features within the reporting unit(s) of interest.  
Cell size  n/a  
Attributes  Length, reporting unit ID, stream code (if specified).  
Theme Name  Streams by Reporting Unit  
File Name  rustrms+{n}, where n is the value generated by ArcView's MakeTmp request.  


Points of Crossing 

Description  A point shapefile that consists of crossing points between selected road features and all streams (selections on streams are ignored) within the reporting unit(s) of interest. If no roads are selected, then all road features are used in defining crossing points.  
Extent  The extent of stream/road crossing points within the reporting unit(s) of interest.  
Cell size  n/a  
Attributes  Record number.  
Theme Name  Points of Crossing  
File Name  cross+{n}, where n is the value generated by ArcView's MakeTmp request  

RNS 

This metric will generate two shapefiles per reporting unit of interest (Stream Buffers and Roads Near Streams) and one single shapefile for the entire study area (Streams by Reporting Unit). The characteristics of each shapefile is as follows: 

Stream Buffers Description  A polygon shapefile of the buffer zone surrounding those streams with one or more road segments within the buffer distance. Only streams with roads within the buffer distance will be buffered. Selections on streams are ignored. This greatly improves the efficiency of the RNS calculations. If two or more distinct buffer areas exist within a reporting unit, the buffer areas are spatially-merged into a single entity. The output shapefile should contain just one record.  
Extent  The extent of buffer area(s)  
Cell size  n/a  
Attributes  ID - arbitrary value  
Theme Name  Stream Buffers ({reporting unit id}+) Example: Stream Buffers (6010204)  
File Name  s_buf+{n}+.shp, where n is the value generated by ArcView's MakeTmp request. Example: s_buf4.shp  


Roads Near Streams

Description  A polyline shapefile of the road segments that are within the specified distance of streams within the reporting unit (i.e., roads clipped within the buffer boundaries). Selections on both the input streams and roads are ignored. If a road class field is specified, the road class attribute is copied to the road feature in the new theme.  
Extent  The extent of road segments within the stream buffer area(s) and within the reporting unit.  
Cell size  n/a  
Attributes  Length, reporting unit id, road class code (if specified).  
Theme Name  Roads Near Streams ({reporting unit id}) Example: Roads Near Streams (6010204)  
File Name  rdclp+{n}+.shp, where n is the value generated by ArcView's MakeTmp request. Example: rdclp12.shp  

Streams by Reporting Unit

Description  A polyline shapefile that consists of all streams (selections are ignored) within the reporting unit(s) of interest, clipped to the reporting unit boundary, and assigned the id of the reporting unit the stream segment is located within. If a stream order field is specified, the stream order attribute is copied to the stream feature in the new theme.  
Extent  The extent of the stream features within the reporting unit(s) of interest.  
Cell size  n/a  
Attributes  Length, reporting unit id, stream order code (if specified).  
Theme Name  Streams by Reporting Unit  
File Name  rustrm+{n}, where n is the value generated by ArcView's MakeTmp request.  

'''