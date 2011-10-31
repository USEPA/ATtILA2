# LandCoverProportions_ArcGIS.py
# Michael A. Jackson, jackson.michael@epa.gov, majgis@gmail.com
# 2011-10-04

""" Land Cover Proportion Metrics

    DESCRIPTION
    
    ARGUMENTS
    
    REQUIREMENTS
    Spatial Analyst Extension

"""

import sys
import os
import arcpy
from collections import defaultdict
from esdlepy import lcc

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

def main(argv):
    """ Start Here """
    # Script arguments
    Input_reporting_unit_feature = arcpy.GetParameterAsText(0)
    Reporting_unit_ID_field = arcpy.GetParameterAsText(1)
    Input_land_cover_grid = arcpy.GetParameterAsText(2)
    lccFilePath = arcpy.GetParameterAsText(4)
    Metrics_to_run = arcpy.GetParameterAsText(5)
    Output_table = arcpy.GetParameterAsText(6)
    Processing_cell_size = arcpy.GetParameterAsText(7)
    Snap_raster = arcpy.GetParameterAsText(8)
    
    # XML file loaded into memory
    # lccFilePath is hard coded until it can be obtained from the tool dialog
    lccFilePath = r'L:\Priv\LEB\Projects\A-H\ATtILA2\src\ATtILA2.src\LandCoverClassifications\NLCD 2001.lcc'
    lccObj = lcc.LandCoverClassification(lccFilePath)

    # dummy dictionary
    classValuesDict = {}
    classValuesDict['for'] = (41, 42, 43)
    classValuesDict['wetl'] = (90, 91, 92, 93, 94, 95, 96, 97, 98, 99)
    classValuesDict['shrb'] = (51, 52)
    classValuesDict['ng'] = (71, 72, 73, 74)
    classValuesDict['agp'] = (81,)
    classValuesDict['agcr'] = (82,)
    classValuesDict['agcn'] = ()
    classValuesDict['nbar']=(31, 32)
    classValuesDict['ldr'] = (22,)
    classValuesDict['hdr'] = (23,)
    classValuesDict['coin'] = (24,)
    classValuesDict['agug'] = (21,)
    classValuesDict['water'] = (0, 11, 12)
    
    
    # Constants
    
    # Set parameters for metric output field
    mPrefix = "p" # e.g. pFor, rAgt, sNat
    mSuffix = "" # e.g. rFor30
    mField_type = "FLOAT" 
    mField_precision = 6
    mField_scale = 1
    
    # set value to be assign to output fields when the calculation is undefined
    nullValue = -1
    
    # set up containers for warnings if data anomalies are found
    
    emptyClasses = [] # selected metrics with empty value tuples in .lcc file
    extraValues = [] # grid values not contained/defined in .lcc file
    
    # the variables row and rows are initially set to None, so that they can
    # be deleted in the finally block regardless of where (or if) script fails
    out_row = None
    out_rows = None 
    
    TabArea_row = None
    TabArea_rows = None
    
    # get current snap environment to restore at end of script
    tempEnvironment0 = arcpy.env.snapRaster
        
    try:
        # Process: inputs        
        # create the specified output table
        (out_path, out_name) = os.path.split(Output_table)
        # need to strip the dbf extension if the outpath is a geodatabase; 
        # should control this in the validate step or with an arcpy.ValidateTableName call
        if out_path.endswith("gdb"):
            if out_name.endswith("dbf"):
                out_name = out_name[0:-4]
        newTable = arcpy.CreateTable_management(out_path, out_name)
        
        # process the user input to add id field to output table
        IDfield = FindIdField(Input_reporting_unit_feature, Reporting_unit_ID_field)
        arcpy.AddField_management(newTable, IDfield.name, IDfield.type, IDfield.precision, IDfield.scale)
        
        # add standard fields to the output table
        arcpy.AddField_management(newTable, "LC_Overlap", "FLOAT", 6, 1)
    
        # add metric fields to the output table.
        metricsBasenameList = ParseMetricsToRun(Metrics_to_run)
         
        for mBasename in metricsBasenameList:
            arcpy.AddField_management(newTable, mPrefix+mBasename+mSuffix, mField_type, mField_precision, mField_scale)
            
        # delete the 'Field1' field if it exists in the new output table.
        DeleteField1(newTable)
    
        # set the snap raster environment so the rasterized polygon theme aligns with land cover grid cell boundaries
        arcpy.env.snapRaster = Snap_raster
            
        # use resultDict function to find the area of each input reporting unit
        resultDict = PolyAreasToDict(Input_reporting_unit_feature, Reporting_unit_ID_field)
    
 
        # Process: Tabulate Area
        # create name for a temporary table for the tabulate area geoprocess step
        # uses the current workspace - want to change to same workspace as specified in Output_table
        scratch_Table = arcpy.CreateScratchName("xtmp", "", "Dataset")
        arcpy.gp.TabulateArea_sa(Input_reporting_unit_feature, Reporting_unit_ID_field, Input_land_cover_grid, "Value", scratch_Table, Processing_cell_size)  
      

        # Process: outputs
        # get the fields from Tabulate Area table
        tabarea_flds = arcpy.ListFields(scratch_Table)
        
        # create the cursor to add data to the output table
        out_rows = arcpy.InsertCursor(newTable)
        
        # create search cursor on TabAreaOut table
        TabArea_rows = arcpy.SearchCursor(scratch_Table)
        
        for TabArea_row in TabArea_rows:
            # get reporting unit id
            zoneIDvalue = TabArea_row.getValue(Reporting_unit_ID_field)
            
            # add a row to the metric output table
            out_row = out_rows.newRow()
            
            # create dictionary to hold the area value of each grid code within the reporting unit
            tabAreaDict=defaultdict(lambda:0)
            
            # put the area figures for each grid value in a dictionary
            # and determine the total excluded and included value areas 
            # in the reporting unit
            excludedAreaSum = 0
            includedAreaSum = 0
            
            for aFld in tabarea_flds[2:]:
                # store the grid code and it's area value into the searchable dictionary
                valKey = aFld.name[6:]
                valArea = TabArea_row.getValue(aFld.name)
                tabAreaDict[valKey] = valArea

                # check if this grid value was defined in the lcc file
                if lccObj.values[valKey]:
                    # add the area for this grid value to the appropriate sum
                    if lccObj.values[valKey].excluded:
                        excludedAreaSum += valArea
                    else:
                        includedAreaSum += valArea
                
                else: 
                    # this grid value is not defined in the lcc file. 
                    # add the value to the includedAreaSum, and set up a warning
                    includedAreaSum += valArea
                    if not valKey in extraValues:
                        extraValues.append(valKey)
            
            # sum the area values for each selected metric   
            for mBasename in metricsBasenameList:
                # get the values for this specified metric
                metricGridCodesList = classValuesDict[mBasename]
                # mBasenameClass = lccObj.classes[mBasename]
                # metricGridCodesList = mBasenameClass.valueIds
                                
                # if the metric value(s) definition tuple is empty
                if not metricGridCodesList:
                    # put the metric name in the emptyClasses list for a warning message
                    if not mBasename in emptyClasses:
                        emptyClasses.append(mBasename)
                    
                    # assign the output field for this metric the null value    
                    out_row.setValue(mPrefix+mBasename+mSuffix, nullValue)
                    # exit for loop and go to the next metric
                    continue
                
                # use the metric area sums, divide them by the effective reporting unit area, and multiply by 100    
                metricPercentArea = CalcMetricPercentArea(metricGridCodesList, tabAreaDict, includedAreaSum)
                
                out_row.setValue(mPrefix+mBasename+mSuffix, metricPercentArea)

            # set the reporting unit id value
            out_row.setValue(Reporting_unit_ID_field, zoneIDvalue)
            
            # add lc_overlap calculation to row
            zoneArea = resultDict[zoneIDvalue]
            overlapCalc = ((includedAreaSum+excludedAreaSum)/zoneArea) * 100
            out_row.setValue('LC_Overlap', overlapCalc)
            
            # commit the row to the output table
            out_rows.insertRow(out_row)

        # Housekeeping
        # delete the scratch table
        arcpy.Delete_management(scratch_Table)

        # Add warnings if necessary
        if emptyClasses:
            warningString = "The following metric(s) were selected, but were undefined in lcc file: "
            for aItem in emptyClasses:
                warningString = warningString+aItem+", "
                
            arcpy.AddWarning(warningString[:-2]+" - Assigned null value in output.")
            
        if extraValues:
            warningString = "The following grid value(s) were not defined in the lcc file: "
            for aItem in extraValues:
                warningString = warningString+aItem+", "
                
            arcpy.AddWarning(warningString[:-2]+" - The area for these grid cells was still used in metric calculations.")
                
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        
    except:
        arcpy.AddError("Non-tool error occurred")
        
    finally:
        # delete cursor and row objects to remove locks on the data
        if out_row:
            del out_row
        if out_rows:
            del out_rows
        if TabArea_rows:
            del TabArea_rows
        if TabArea_row:
            del TabArea_row
            
        # restore the environments
        arcpy.env.snapRaster = tempEnvironment0
        
        # return the spatial analyst license    
        arcpy.CheckInExtension("spatial")
        

def PolyAreasToDict(fc, key_field):
    """ Calculate polygon areas and import values to dictionary.
        Use the reporting unit ID as the retrieval key """

    resultDict = {}
    
    cur = arcpy.SearchCursor(fc)
    for row in cur:
        key = row.getValue(key_field)
        area = row.getValue("Shape").area
        resultDict[key] = (area)
    
    del row
    del cur

    return resultDict

    
def FindIdField(fc, id_field_str):
    """ Find the specified ID field in the feature class """
    orig_Fields = arcpy.ListFields(fc)
    for aFld in orig_Fields:
        if aFld.name == id_field_str:
            IDfield = aFld
            break
        
    return IDfield


def ParseMetricsToRun(metricsString):
    """ Parse the Metrics_to_run string into a list of selected metric base names.
        e.g., 'for  (forest)';'wetl  (wetland)' becomes ['for','wetl'] """
    metricsBasenameList = []
    templist = metricsString.replace("'","").split(';')
    for alist in templist:
        metricsBasenameList.append(alist.split('  ')[0])
        
    return metricsBasenameList


def CalcMetricPercentArea(metricGridCodesList, tabAreaDict, includedAreaSum):
    """ Retrieves stored area figures for each grid code associated with selected metric and sums them.
        That number divided by the total included area within the reporting unit times 100 gives the
        percentage of the effective reporting unit that is classified as the metric base """
    metricAreaSum = 0                         
    for aValueID in metricGridCodesList:
        aValueIDStr = str(aValueID)
        metricAreaSum += tabAreaDict[aValueIDStr]
    
    if includedAreaSum > 0:
        metricPercentArea = (metricAreaSum / includedAreaSum) * 100
    else: # all values found in reporting unit are in the excluded set
        metricPercentArea = 0
        
    return metricPercentArea


def DeleteField1(theTable):
    """ delete the 'Field1' field if it exists in the table. """
    newFieldsList = arcpy.ListFields(theTable)
    for nFld in newFieldsList:
        if nFld.name.lower() == 'field1': 
            arcpy.DeleteField_management(theTable, nFld.name)
            break
        
    return

    
if __name__ == "__main__":
    main(sys.argv)