""" Land Cover Proportion Metrics

    This script is associated with an ArcToolbox script tool
    
"""

import arcpy, os, sys
from arcpy import env
from pylet import lcc
from ATtILA2.metrics import fields as outFields
from ATtILA2.metrics import constants as metricConstants

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

def main(argv):
    """ Start Here """
    
    # Script arguments
    Input_reporting_unit_feature = arcpy.Describe(arcpy.GetParameter(0)).catalogPath # Access of catalogPath needed for ArcMap
    Reporting_unit_ID_field = arcpy.GetParameterAsText(1)
    Input_land_cover_grid = arcpy.GetParameterAsText(2)
    lccFilePath = arcpy.GetParameterAsText(4)
    Metrics_to_run = arcpy.GetParameterAsText(5)
    Output_table = arcpy.GetParameterAsText(6)
    Processing_cell_size = arcpy.GetParameterAsText(7)
    Snap_raster = arcpy.GetParameterAsText(8)
    Optional_field_groups = arcpy.GetParameterAsText(9)
    thresholdValue = ""

    ## For debugging    
#    Input_reporting_unit_feature = "D:/ATTILA_Jackson/testzone/shpfiles/wtrshd.shp"
#    Reporting_unit_ID_field = "HUC"
#    Input_land_cover_grid = "D:/ATTILA_Jackson/testzone/grids/lc_mrlc"
#    lccFilePath = "D:/ATTILA_Jackson/testzone/NLCD 2001.lcc"
#    Metrics_to_run = "'for  (Forest)'"
#    Output_table = "D:/ATTILA_Jackson/testzone/testoutputs/File Geodatabase.gdb/qacheck"
#    Processing_cell_size = "30.6618"
#    Snap_raster = "D:/ATTILA_Jackson/testzone/grids/lc_mrlc"
#    Optional_field_groups = "'QACHECK  -  Quality Assurance Checks';'METRICADD  -  Area for all land cover classes'"
#    env.workspace = "D:/ATTILA_Jackson/testzone/testoutputs/Scratch"
#    env.overwriteOutput = True
 
      
    # the variables row and rows are initially set to None, so that they can
    # be deleted in the finally block regardless of where (or if) script fails
    outTable_row = None
    outTable_rows = None
    tabAreaTable_row = None
    tabAreaTable_rows = None
    
    # get current snap environment to restore at end of script
    tempEnvironment0 = env.snapRaster
        
    try:
        # Use this script's name to obtain information on output field naming, additional optional fields, and 
        # field naming overrides.
        
        # determine the maximum size of output field names based on the output table's destination/type
        outTablePath,outTableName = os.path.split(Output_table)
        maxFNameSize = GetFNameSizeLimit(outTablePath, outTableName)        
        
        # Set parameters for metric output field. use this file's name to determine the metric type
        # Parameters = [Fieldname_prefix, Fieldname_suffix, Field_type, Field_Precision, Field_scale]
        # e.g., fldParams = ["p", "", "FLOAT", 6, 1]
        fldParams = outFields.getFieldParametersFromFilePath()

        # get the field name override key using this script's name
        fieldOverrideKey = outFields.getFieldOverrideKeyFromFilePath()
        
        # if any optional fields are selected, get their parameters
        optionalGroupsList = ParseCheckboxSelections(Optional_field_groups)
        
        if metricConstants.qaCheckName in optionalGroupsList:
            # Parameratize optional fields, e.g., optionalFlds = [["LC_Overlap","FLOAT",6,1]]
            qaCheckFlds = outFields.getQACheckFieldParametersFromFilePath()
        else:
            qaCheckFlds = None
            
        if metricConstants.metricAddName in optionalGroupsList:
            addAreaFldParams = metricConstants.areaFieldParameters
            maxFNameSize = maxFNameSize - len(addAreaFldParams[0])
        else:
            addAreaFldParams = None
        
        # Process: inputs
        # XML Land Cover Coding file loaded into memory
        lccObj = lcc.LandCoverClassification(lccFilePath)
        # get dictionary of metric class values (e.g., classValuesDict['for'].uniqueValueIds = (41, 42, 43))
        lccClassesDict = lccObj.classes    
        # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area calculation
        lccValuesDict = lccObj.values
        # get the frozenset of excluded values (i.e., values not to use when calculating the reporting unit effective area)
        excludedValues = lccValuesDict.getExcludedValueIds()
        
        # take the 'Metrics to run' input and parse it into a list of metric ClassNames
        metricsClassNameList = ParseCheckboxSelections(Metrics_to_run)
        
        # use the metricsClassNameList to create a dictionary of ClassName keys with field name values using any user supplied field names
        metricsFieldnameDict = {}
        outputFieldNames = set() # use this set to help make field names unique
        
        for mClassName in metricsClassNameList:
            # generate unique number to replace characters at end of truncated field names
            n = 1
            
            fieldOverrideName = lccClassesDict[mClassName].attributes.get(fieldOverrideKey,None)
            if fieldOverrideName: # a field name override exists
                # see if the provided field name is too long for the output table type
                if len(fieldOverrideName) > maxFNameSize:
                    defaultFieldName = fieldOverrideName # keep track of the originally provided field name
                    fieldOverrideName = fieldOverrideName[:maxFNameSize] # truncate field name to maximum allowable size
                    
                    # see if truncated field name is already used.
                    # if so, truncate further and add a unique number to the end of the name
                    while fieldOverrideName in outputFieldNames:
                        # shorten the field name and increment it
                        truncateTo = maxFNameSize - len(str(n))
                        fieldOverrideName = fieldOverrideName[:truncateTo]+str(n)
                        n = n + 1
                        
                    arcpy.AddWarning("Provided metric name too long for output location. Truncated "+defaultFieldName+" to "+fieldOverrideName)
                    
                # keep track of output field names    
                outputFieldNames.add(fieldOverrideName)
                # add output field name to dictionary
                metricsFieldnameDict[mClassName] = fieldOverrideName
            else:
                # generate output field name
                outputFName = fldParams[0]+mClassName+fldParams[1]
                
                # see if the provided field name is too long for the output table type
                if len(outputFName) > maxFNameSize:
                    defaultFieldName = outputFName # keep track of the originally generated field name
                    
                    prefixLen = len(fldParams[0])
                    suffixLen = len(fldParams[1])
                    maxBaseSize = maxFNameSize - prefixLen - suffixLen - len(thresholdValue)
                        
                    outputFName = fldParams[0]+mClassName[:maxBaseSize]+fldParams[1]+thresholdValue # truncate field name to maximum allowable size
                    
                    # see if truncated field name is already used.
                    # if so, truncate further and add a unique number to the end of the name
                    while outputFName in outputFieldNames:
                        # shorten the field name and increment it
                        truncateTo = maxBaseSize - len(str(n))
                        outputFName = fldParams[0]+mClassName[:truncateTo]+str(n)+fldParams[1]
                        n = n + 1
                        
                    arcpy.AddWarning("Metric field name too long for output location. Truncated "+defaultFieldName+" to "+outputFName)
                    
                # keep track of output field names
                outputFieldNames.add(outputFName)             
                # add output field name to dictionary
                metricsFieldnameDict[mClassName] = outputFName
                    
        # create the specified output table
        newTable = CreateMetricOutputTable(Output_table,Input_reporting_unit_feature,Reporting_unit_ID_field,metricsClassNameList,metricsFieldnameDict,fldParams,qaCheckFlds,addAreaFldParams)
        
        # Process: Tabulate Area
        # set the snap raster environment so the rasterized polygon theme aligns with land cover grid cell boundaries
        env.snapRaster = Snap_raster
        # store the area of each input reporting unit into dictionary (zoneID:area)
        zoneAreaDict = PolygonAreasToDict(Input_reporting_unit_feature, Reporting_unit_ID_field)
        # create name for a temporary table for the tabulate area geoprocess step - defaults to current workspace 
        scratch_Table = arcpy.CreateScratchName("xtmp", "", "Dataset")
        # run the tabulatearea geoprocess
        arcpy.gp.TabulateArea_sa(Input_reporting_unit_feature, Reporting_unit_ID_field, Input_land_cover_grid, "Value", scratch_Table, Processing_cell_size)  

        # Process output table from tabulatearea geoprocess
        # get the VALUE fields from Tabulate Area table
        TabAreaValueFields = arcpy.ListFields(scratch_Table)[2:]
        # get the grid code values from the field names; put in a list of integers
        TabAreaValues = [int(aFld.name.replace("VALUE_","")) for aFld in TabAreaValueFields]
        # create dictionary to later hold the area value of each grid code in the reporting unit
        tabAreaDict = dict(zip(TabAreaValues,[])) 
        
        # alert user if input grid had values not defined in LCC file
        undefinedValues = [aVal for aVal in TabAreaValues if aVal not in lccObj.getUniqueValueIdsWithExcludes()]     
        if undefinedValues:
            arcpy.AddWarning("Following Grid Values undefined in LCC file: "+str(undefinedValues)+"  - By default, the area for undefined grid codes is included when determining the effective reporting unit area.")

        
        # create the cursor to add data to the output table
        outTable_rows = arcpy.InsertCursor(newTable)
        
        # create cursor to search/query the TabAreaOut table
        tabAreaTable_rows = arcpy.SearchCursor(scratch_Table)
        
        for tabAreaTable_row in tabAreaTable_rows:
            # initiate a row to add to the metric output table
            outTable_row = outTable_rows.newRow()

            # get reporting unit id
            zoneIDvalue = tabAreaTable_row.getValue(Reporting_unit_ID_field)            
            # set the reporting unit id value in the output row
            outTable_row.setValue(Reporting_unit_ID_field, zoneIDvalue)
            
            # Process the value fields in the TabulateArea Process output table
            # 1) Go through each value field in the TabulateArea table row and put the area
            #    value for the grid code into a dictionary with the grid code as the key.
            # 2) Determine if the grid code is to be included into the reporting unit effective area sum
            # 3) Calculate the total grid area present in the reporting unit
            valFieldsResults = ProcessTabAreaValueFields(TabAreaValueFields,TabAreaValues,tabAreaDict,tabAreaTable_row,excludedValues)
            tabAreaDict = valFieldsResults[0]
            effectiveAreaSum = valFieldsResults[1]
            excludedAreaSum = valFieldsResults[2]
            
            # sum the areas for the selected metric's grid codes   
            for mClassName in metricsClassNameList: 
                # get the grid codes for this specified metric
                metricGridCodesList = lccClassesDict[mClassName].uniqueValueIds
                # get the class percentage area and it's actual area from the tabulate area table
                metricPercentageAndArea = CalcMetricPercentArea(metricGridCodesList, tabAreaDict, effectiveAreaSum)
                # add the calculation to the output row
                outTable_row.setValue(metricsFieldnameDict[mClassName], metricPercentageAndArea[0])
                
                if addAreaFldParams:
                    outTable_row.setValue(metricsFieldnameDict[mClassName]+"_A", metricPercentageAndArea[1])

            # add QACheck calculations/values to row
            if qaCheckFlds:
                zoneArea = zoneAreaDict[zoneIDvalue]
                overlapCalc = ((effectiveAreaSum+excludedAreaSum)/zoneArea) * 100
                outTable_row.setValue(qaCheckFlds[0][0], overlapCalc)
                outTable_row.setValue(qaCheckFlds[1][0], effectiveAreaSum+excludedAreaSum)
                outTable_row.setValue(qaCheckFlds[2][0], effectiveAreaSum)
                outTable_row.setValue(qaCheckFlds[3][0], excludedAreaSum)
            
            # commit the row to the output table
            outTable_rows.insertRow(outTable_row)

        
        # Housekeeping
        # delete the scratch table
        arcpy.Delete_management(scratch_Table)

                
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        
    except:
        import traceback
        # get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        
        # Concatenate information together concerning the error into a message string
        
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
    
        # Return python error messages for use in script tool
        
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)

        
    finally:
        # delete cursor and row objects to remove locks on the data
        if outTable_row: del outTable_row
        if outTable_rows: del outTable_rows
        if tabAreaTable_rows: del tabAreaTable_rows
        if tabAreaTable_row: del tabAreaTable_row
            
        # restore the environments
        env.snapRaster = tempEnvironment0
        
        # return the spatial analyst license    
        arcpy.CheckInExtension("spatial")
        
        print "Finished."


def PolygonAreasToDict(fc, key_field):
    """ Calculate polygon areas and import values to dictionary.
        Use the reporting unit ID as the retrieval key """

    zoneAreaDict = {}
    
    cur = arcpy.SearchCursor(fc)
    for row in cur:
        key = row.getValue(key_field)
        area = row.getValue("Shape").area
        zoneAreaDict[key] = (area)
    
    del row
    del cur

    return zoneAreaDict

def GetFNameSizeLimit(outTablePath, outTableName):
    """ Return the maximum size of output field names based on the output table's destination/type.
        64 for file and personal geodatabases, 10 for dBASE tables, and 16 for INFO tables """
    if outTablePath[-3:].lower() == "gdb":
        maxFNameSize = 64 # ESRI maximum for File Geodatabases
    elif outTablePath[-3:].lower() == "mdb":
        maxFNameSize = 64 # ESRI maximum for Personal Geodatabases
    elif outTableName[-3:].lower() == "dbf":
        maxFNameSize = 10 # maximum for dBASE tables
    else:
        maxFNameSize = 16 # maximum for INFO tables
        
    return maxFNameSize
    
def FindIdField(fc, id_field_str):
    """ Find the specified ID field in the feature class """
    orig_Fields = arcpy.ListFields(fc)
    for aFld in orig_Fields:
        if aFld.name == id_field_str:
            IDfield = aFld
            break
        
    return IDfield


def CalcMetricPercentArea(metricGridCodesList, tabAreaDict, effectiveAreaSum):
    """ Retrieves stored area figures for each grid code associated with selected metric and sums them.
        That number divided by the total effective area within the reporting unit times 100 gives the
        percentage of the effective reporting unit that is classified as the metric class """
    metricAreaSum = 0                         
    for aValueID in metricGridCodesList:
        metricAreaSum += tabAreaDict.get(aValueID, 0) #add 0 if the lcc defined value is not found in the grid
    
    if effectiveAreaSum > 0:
        metricPercentArea = (metricAreaSum / effectiveAreaSum) * 100
    else: # all values found in reporting unit are in the excluded set
        metricPercentArea = 0
        
    return metricPercentArea, metricAreaSum


def DeleteField(theTable,fieldName):
    """ delete the supplied field if it exists in the table. """
    newFieldsList = arcpy.ListFields(theTable)
    for nFld in newFieldsList:
        if nFld.name.lower() == fieldName.lower(): 
            arcpy.DeleteField_management(theTable, nFld.name)
            break
        
    return


def ProcessTabAreaValueFields(TabAreaValueFields,TabAreaValues,tabAreaDict,tabAreaTable_row,excludedValues):
    """ 1) Go through each value field in the TabulateArea table one row at a time and
           put the area value for each grid code into a dictionary with the grid code as the key.
        2) Determine if the area for the grid code is to be included into the reporting unit effective area sum
        3) Keep a running total of effective and excluded area within the reporting unit. Added together, these 
           area sums provide the total grid area present in the reporting unit. That value is used to calculate
           the amount of overlap between the reporting unit polygon and the underlying land cover grid.
    """
    
    excludedAreaSum = 0  #area of reporting unit not used in metric calculations e.g., water area
    effectiveAreaSum = 0  #effective area of the reporting unit e.g., land area

    for i, aFld in enumerate(TabAreaValueFields):
        # store the grid code and it's area value into the dictionary
        valKey = TabAreaValues[i]
        valArea = tabAreaTable_row.getValue(aFld.name)
        tabAreaDict[valKey] = valArea

        #add the area of each grid value to the appropriate area sum i.e., effective or excluded area
        if valKey in excludedValues:
            excludedAreaSum += valArea
        else:
            effectiveAreaSum += valArea               
                       
    return (tabAreaDict,effectiveAreaSum,excludedAreaSum)


def CreateMetricOutputTable(Output_table,Input_reporting_unit_feature,Reporting_unit_ID_field,metricsClassNameList,metricsFieldnameDict,fldParams,qaCheckFlds,addAreaFldParams):
    """ Creates an empty table with fields for the reporting unit id, all selected metrics with
        appropriate fieldname prefixes and suffixes (e.g. pUrb, rFor30), and any selected 
        optional fields for quality assurance purposes or additional user
        feedback (e.g., LC_Overlap)
    """
    outTablePath, outTableName = os.path.split(Output_table)
        
    # need to strip the dbf extension if the outpath is a geodatabase; 
    # should control this in the validate step or with an arcpy.ValidateTableName call
    newTable = arcpy.CreateTable_management(outTablePath, outTableName)
    
    # process the user input to add id field to output table
    IDfield = FindIdField(Input_reporting_unit_feature, Reporting_unit_ID_field)
    arcpy.AddField_management(newTable, IDfield.name, IDfield.type, IDfield.precision, IDfield.scale)
                
    # add metric fields to the output table.
    [arcpy.AddField_management(newTable, metricsFieldnameDict[mClassName], fldParams[2], fldParams[3], fldParams[4])for mClassName in metricsClassNameList]

    # add any optional fields to the output table
    if qaCheckFlds:
        [arcpy.AddField_management(newTable, qaFld[0], qaFld[1], qaFld[2]) for qaFld in qaCheckFlds]
        
    if addAreaFldParams:
        [arcpy.AddField_management(newTable, metricsFieldnameDict[mClassName]+addAreaFldParams[0], addAreaFldParams[1], addAreaFldParams[2], addAreaFldParams[3])for mClassName in metricsClassNameList]
         
    # delete the 'Field1' field if it exists in the new output table.
    DeleteField(newTable,"field1")
        
    return (newTable)


def ParseCheckboxSelections(selectionsString):
    """ Returns a list of the items selected by the user.
        The expected input is a string with the following format: 'item<two spaces>description';'item<two spaces>description';'item...'
        e.g., the string, 'for  [pfor] Forest';'wetl  [pwetl]  wetland', becomes the list, ['for','wetl']
    """
    return map((lambda splitItemAndDesc: splitItemAndDesc.split(metricConstants.descriptionDelim)[0]), selectionsString.replace("'","").split(';'))


if __name__ == "__main__":
    main(sys.argv)
    