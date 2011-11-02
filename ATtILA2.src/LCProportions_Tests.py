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
import traceback
import os
import arcpy
from arcpy import env
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
    lccFilePath = r'E:\Python_projects\attila2-python\ATtILA2.src\LandCoverClassifications\NLCD 2001.lcc'
    lccObj = lcc.LandCoverClassification(lccFilePath)
    lccValuesDict = lccObj.values

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
    
    # the variables row and rows are initially set to None, so that they can
    # be deleted in the finally block regardless of where (or if) script fails
    out_row, out_rows = None, None
    TabArea_row, TabArea_rows = None, None
    
    # get current snap environment to restore at end of script
    tempEnvironment0 = env.snapRaster
        
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
        env.snapRaster = Snap_raster
            
        # store the area of each input reporting unit into dictionary keyed to the reporting unit ID
        resultDict = PolyAreasToDict(Input_reporting_unit_feature, Reporting_unit_ID_field)
    
        # check to see if any selected metrics are not defined in the LCC file
        for mBasename in metricsBasenameList:
            if not classValuesDict[mBasename]:
                # warn the user
                warningString = "The metric "+mBasename.upper()+" is undefined in lcc file"         
                arcpy.AddWarning(warningString+" - Assigned null value in output.")

  
        # Process: Tabulate Area
        # create name for a temporary table for the tabulate area geoprocess step
        scratch_Table = arcpy.CreateScratchName("xtmp", "", "Dataset", out_path)
        arcpy.gp.TabulateArea_sa(Input_reporting_unit_feature, Reporting_unit_ID_field, Input_land_cover_grid, "Value", scratch_Table, Processing_cell_size)  
      

        # Process: outputs
        # get the VALUE fields from Tabulate Area table
        TabAreaValueFields = arcpy.ListFields(scratch_Table)[2:]
        
        # Now get the grid code values from the field names
        TabAreaValues =[]
        for aFld in TabAreaValueFields:
            value = aFld.name.replace("VALUE_","")
            TabAreaValues.append(value)
        
        # create the cursor to add data to the output table
        out_rows = arcpy.InsertCursor(newTable)
        
        # create cursor to search/query the TabAreaOut table
        TabArea_rows = arcpy.SearchCursor(scratch_Table)
        
        for TabArea_row in TabArea_rows:
            # get reporting unit id
            zoneIDvalue = TabArea_row.getValue(Reporting_unit_ID_field)
            
            # add a row to the metric output table
            out_row = out_rows.newRow()
            
            # Process the value fields in the TabulateArea Process output table
            # 1) Go through each value field in the TabulateArea table row and put the area
            #    value for the grid code into a dictionary with the grid code as the key.
            # 2) Determine if the grid code is to be included into the reporting unit effective area sum
            # 3) Calculate the total grid area present in the reporting unit
            # 4) Identify any grid codes not accounted for in the LCC files
            valFieldsResults = ProcessTabAreaValueFields(TabAreaValueFields,TabAreaValues,TabArea_row,lccValuesDict)
            tabAreaDict = valFieldsResults[0]
            includedAreaSum = valFieldsResults[1]
            excludedAreaSum = valFieldsResults[2]
            
            # sum the area values for each selected metric   
            for mBasename in metricsBasenameList:
                # get the values for this specified metric
                metricGridCodesList = classValuesDict[mBasename]
                # mBasenameClass = lccObj.classes[mBasename]
                # metricGridCodesList = mBasenameClass.valueIds
                                
                # if the metric value(s) definition tuple is empty
                if not metricGridCodesList:
                    # assign the null value to the output field for this metric    
                    out_row.setValue(mPrefix+mBasename+mSuffix, nullValue)

                    continue
                
                # determine the area covered by the selected metric
                # divide it by the effective reporting unit area (i.e., includedAreaSum)
                # and multiply the answer by 100    
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

        # alert user if input grid had values not defined in LCC file
        allLCCvalues = lccValuesDict.keys()
        for aFld in TabAreaValueFields:
            value = aFld.name.replace("VALUE_","")
            if not value in allLCCvalues:
                arcpy.AddWarning("The grid value "+value+" was not defined in the lcc file - By default, the area for undefined grid codes is included when determining the effective reporting unit area.")


        # Housekeeping
        # delete the scratch table
        arcpy.Delete_management(scratch_Table)

                
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        
    except:
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
        if out_row: del out_row
        if out_rows: del out_rows
        if TabArea_rows: del TabArea_rows
        if TabArea_row: del TabArea_row
            
        # restore the environments
        env.snapRaster = tempEnvironment0
        
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


def ProcessTabAreaValueFields(TabAreaValueFields,TabAreaValues,TabArea_row,lccValuesDict):
    """ 1) Go through each value field in the TabulateArea table one row at a time and
           put the area value for each grid code into a dictionary with the grid code as the key.
        2) Determine if the grid code is to be included into the reporting unit effective area sum
        3) Calculate the total grid area present in the reporting unit to be used in the LC_overlap calculations
        4) Identify any grid codes not accounted for in the LCC files
    """
    
    # create dictionary to hold the area value of each grid code within the reporting unit
    tabAreaDict=defaultdict(lambda:0)#tabAreaDict.get(key, 0)
    excludedAreaSum = 0  #area of reporting unit not used in metric calculations e.g., water area
    includedAreaSum = 0  #effective area of the reporting unit e.g., land area

    for i, aFld in enumerate(TabAreaValueFields):
        # store the grid code and it's area value into the dictionary
        valKey = TabAreaValues[i]
        valArea = TabArea_row.getValue(aFld.name)
        tabAreaDict[valKey] = valArea

        #add the area of each grid value to the appropriate area sum i.e., included or excluded area
        result = lccValuesDict.get(valKey)
        if result:
            if result.excluded:
                excludedAreaSum += valArea
            else:
                includedAreaSum += valArea               
            
        else:  # this grid value is not defined in the lcc file. 
            # add the value to the includedAreaSum
            includedAreaSum += valArea
                       
    return (tabAreaDict,includedAreaSum,excludedAreaSum)
    
if __name__ == "__main__":
    main(sys.argv)