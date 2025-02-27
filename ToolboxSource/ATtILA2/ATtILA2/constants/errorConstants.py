''' Error Constants
'''

errorLookup = {
'ERROR 010092':'''You have an invalid output extent.  This error can occur in the following circumstances:
  1) Some input datasets do not overlap
  2) The extent in your environment settings does not overlap the input datasets
  3) Another extent related issue\n''', 
  
'ERROR 002836': '''This error can occur when geometry errors are present in an input dataset. 
We recommend running 'Repair Geometry' on the inputs and trying again. \n''', 

'ERROR 000012': '''An ID field has been set to 'OBJECTID'. This can cause some ATtILA tools to fail. 
We recommend selecting a different ID field and retrying to run the tool. \n''', 

'ERROR 003911': '''This error may be the result of a field named 'OBJECTID' chosen as an input field parameter. 
If this is the case, select a different input field, or try renaming or copying the 'OBJECTID' field. \n  ''', 
'FAKE ERROR' : '' }

errorCommentPrefix = "Error Comments:\n---------------\n"
errorDetailsPrefix = "\nError Details:\n--------------\n"
errorUnknown = '''Unknown Error. More assistance may be available in the ESRI error documentation or on ATtILA's webpage (https://github.com/USEPA/ATtILA2/wiki/Troubleshooting)
Please report details to: https://ecomments.epa.gov/enviroatlas/ and include 'ATtILA' in the subject line.'''


linearUnitConversionError = '''Unable to determine conversion factor necessary to convert output linear units to metric units.

Please be sure that the Environment Settings > Output Coordinates are not set to a system defined with angular units of 
Decimal Degrees. If an Environment Settings > Output Coordinates is not set, please be sure to select an 'Input reporting
unit feature' that does not have a spatial reference defined with angular units of decimal degrees. 

It is also possible for this error to occur if the linear units defined in the Output Coordinates, if one is set, or the 
'Input reporting unit feature', if an Output Coordinates is not set, is not found in ATtILA's look up table. Please 
compare your linear units with those found in the ATtILA Help file.'''

nonOverlappingExtentsError = '''Input features do not overlap. Unable to perform spatial analysis.

Please be sure that the areal extent of the input Reporting unit features overlaps with the areal extent of all other input layers. '''

rasterSizeError = '''Unable to convert raster to polygon feature.

Input grid may be too large for processing. Try splitting the raster into smaller tiles before re-running the tool. '''

linearUnitFormatError = '''One or more records have invalid or missing entries in the selected Linear Unit Field.

Please correct any erroneous field contents accordingly.

A valid entry is in the form of: linearUnit unitOfMeasure (e.g. 10 Meters).

Valid unitOfMeasure keywords: CENTIMETERS | DECIMALDEGREES | DECIMETERS | FEET | INCHES |
                              KILOMETERS | METERS | MILES | MILLIMETERS | NAUTICALMILES | POINTS |
                              UNKNOWN | YARDS '''

missingNHDFilesError = '''One or more required files are missing in the selected workspace(s). '''

missingFieldError = '''Input field parameter not supplied. 

A population field is required when the input Population raster or polygon feature is a polygon feature.

Please select a field and try re-running the tool. '''

rasterOutputFormatError = '''

An error occurred while attempting to save a raster dataset to the output geodatabase.

This error typically occurs when there may already exist an output raster with the same name and format.
While ATtILA checks for this condition during tool operation, a residual lock file may exist in the output workspace. 

Try running the ATtILA tool again with the same parameters, often this error will not occur on the subsequent attempt, 
or try selecting a new geodatabase to write the output to.

'''


tabulateIntersectionError = '''

An error occurred while attempting to perform a tabulate intersection.

This error has been observed when a conflict occurs between the topologies of the two feature layers input into the function.

If a buffer distance was used by the ATtILA tool, try marginally increasing or decreasing the buffer distance and rerunning the 
tool to see if this error can be avoided.

'''


spatialAnalystNeededError = '''

This tool requires the Spatial Analyst extension.

'''

emptyFieldError = '''

A required field contains only NULL values or whitespace. 

Please inspect all fields selected for the tool inputs and verify their contents.

'''


missingRoadsError = '''

A required input was not found in the Roads geodatabase.

- For **ESRI StreetMap** the following feature classes must be present:  

  - .gdb\\Streets  
  
  - .gdb\\MapLandArea\MapLandArea  

- For **NAVTEQ 2019** the following feature classes must be present:  

  - .gdb\\RoutingApplication\\Streets  
  
  - .gdb\\MapFacilityArea  
  
  - .gdb\\MapLanduseArea  
  
  - .gdb\\link  
  
- For **NAVTEQ 2011** the following feature classes must be present:  

  - .gdb\\Streets  
  
  - .gdb\\LandUseA  
  
  - .gdb\\LandUseB  

'''


unprojectedRoadsError = '''

One or more required files are in an unprojected coordinate system.

- For **ESRI StreetMap** these feature classes must be in a projected coordinate system:  

  - .gdb\\Streets  
  
  - .gdb\\MapLandArea\MapLandArea  

- For **NAVTEQ 2019** these feature classes must be in a projected coordinate system:  

  - .gdb\\RoutingApplication\\Streets  
  
  - .gdb\\MapFacilityArea  
  
  - .gdb\\MapLanduseArea  
  
  - .gdb\\link  
  
- For **NAVTEQ 2011** these feature classes must be in a projected coordinate system:  

  - .gdb\\Streets  
  
  - .gdb\\LandUseA  
  
  - .gdb\\LandUseB  

'''


noEnvWorkspaceError = '''

No arcpy.env.workspace set. Unable to create log file. 

If running ATtILA outside of a traditional ArcGIS install via a standalone script, the log file can be 
created by setting arcpy.env.workspace to a directory path variable at the beginning of the script.

For example:

  outGDB = r"example/Outputs.gdb"
  arcpy.env.workspace = outGDB


If a log file is not necessary, removing the LOGFILE option from the 'Select_options' parameter will allow 
the tool to run to completion.

'''