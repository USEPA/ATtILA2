'''
Created on Apr 23, 2012

@author: mjacks07
'''
import os
import arcpy
from pylet import arcpyutil


def CalcMetricPercentArea(metricGridCodesList, tabAreaDict, effectiveAreaSum):
    """ Calculates the percentage of the reporting unit effective area occupied by the metric class codes and their total area
    
        DESCRIPTION
        -----------
        Retrieves stored area figures for each grid code associated with selected metric and sums them.
        That number, divided by the total effective area within the reporting unit and multiplied by 100, gives the
        percentage of the effective reporting unit that is occupied by the metric class. Both the percentage and the 
        final area sum are returned.
        
        PARAMETERS
        ----------
        metricGridCodesList: list of all grid values assigned to a metric class in the lcc file (e.g., [41, 42, 43] for the forest class)
        tabAreaDict: dictionary with the area value of each grid code in a reporting unit keyed to the grid code
        effectiveAreaSum: sum of the area of all grid cells in the reporting unit with codes not tagged as excluded in the lcc file
        
        RETURNS
        -------
        Tuple:
            float 1 - the percentage of the reporting unit effective area that is occupied by the metric class codes
            float 2 - the sum of the area of metric class codes
        
    """
    
    metricAreaSum = 0                         
    for aValueID in metricGridCodesList:
        metricAreaSum += tabAreaDict.get(aValueID, 0) #add 0 if the lcc defined value is not found in the grid
    
    if effectiveAreaSum > 0:
        metricPercentArea = (metricAreaSum / effectiveAreaSum) * 100
    else: # all values found in reporting unit are in the excluded set
        metricPercentArea = 0
        
    return metricPercentArea, metricAreaSum


def ProcessTabAreaValueFields(TabAreaValueFields, TabAreaValues, tabAreaDict, tabAreaTableRow, excludedValues):
    """ Processes the 'VALUE_' fields in a supplied row object for exclusion/inclusion status in metric area/percentage calculations. 
    
        DESCRIPTION
        -----------
        1) Go through each 'VALUE_' field in the TabulateArea table one row at a time and put the area value
           for each grid code into a dictionary with the grid code as the key.
        2) Determine if the area for the grid code is to be included into the reporting unit effective area sum.
        3) Keep a running total of effective and excluded area within the reporting unit. Added together, these 
           area sums provide the total grid area present in the reporting unit. That value is used to calculate
           the amount of overlap between the reporting unit polygon and the underlying land cover grid.
           
        PARAMETERS
        ----------
        TabAreaValueFields: a list of the 'VALUE_' fieldnames from a TabulateArea generated table
        TabAreaValues: a list of integer grid code values generated from the 'VALUE_' fieldnames
        tabAreaDict: an empty dictionary to be populated with a key:value pair of gridcode:area
        tabAreaTableRow: the current row object from TabluateArea output table arcpy SearchCursor
        excludedValues: a frozenset of values not to use when calculating the reporting unit effective area.
        
        RETURNS
        -------
        Tuple:
            dictionary - dictionary with the area value of each grid code in a reporting unit keyed to the grid code
            float 1 - sum of the area within the reporting unit to be included in the percentage calculations
            float 2 - sum of the area within the reporting unit to be excluded from percentage calculations
            
    """
    
    excludedAreaSum = 0  #area of reporting unit not used in metric calculations e.g., water area
    effectiveAreaSum = 0  #effective area of the reporting unit e.g., land area

    for i, aFld in enumerate(TabAreaValueFields):
        # store the grid code and it's area value into the dictionary
        valKey = TabAreaValues[i]
        valArea = tabAreaTableRow.getValue(aFld.name)
        tabAreaDict[valKey] = valArea

        #add the area of each grid value to the appropriate area sum i.e., effective or excluded area
        if valKey in excludedValues:
            excludedAreaSum += valArea
        else:
            effectiveAreaSum += valArea               
                       
    return (tabAreaDict, effectiveAreaSum, excludedAreaSum)


def CreateMetricOutputTable(outTable, inReportingUnitFeature, reportingUnitIdField, metricsClassNameList, metricsFieldnameDict, fldParams, qaCheckFlds, addAreaFldParams):
    """ Returns new empty table for ATtILA metric generation output with appropriate fields for selected metric
    
        DESCRIPTION
        -----------
        Creates an empty table with fields for the reporting unit id, all selected metrics with appropriate fieldname
        prefixes and suffixes (e.g. pUrb, rFor30), and any selected optional fields (e.g., LC_Overlap)
        
        PARAMETERS
        ----------
        outTable: file name including path for the ATtILA output table
        inReportingUnitFeature: CatalogPath to the input reporting unit layer
        reportingUnitIdField: fieldname for the input reporting unit id field
        metricsClassNameList: a list of metric ClassNames parsed from the 'Metrics to run' input (e.g., [for, agt, shrb, devt])
        metricsFieldnameDict: a dictionary of ClassName keys with field name values (e.g., "unat":"UINDEX", "for":"pFor")
        fldParams: list of parameters to generate the selected metric output field (i.e., [Fieldname_prefix, Fieldname_suffix, Field_type, Field_Precision, Field_scale])
        qaCheckFlds: a list of filename parameter lists for one or more selected optional fields fieldname generation (e.g., optionalFlds = [["LC_Overlap","FLOAT",6,1]])
        addAreaFldParams: a list of filename parameters for the optional Add Area Fields selection (e.g., ["_A","DOUBLE",15,0])
        
        RETURNS
        -------
        Table
        
    """
    outTablePath, outTableName = os.path.split(outTable)
        
    # need to strip the dbf extension if the outpath is a geodatabase; 
    # should control this in the validate step or with an arcpy.ValidateTableName call
    newTable = arcpy.CreateTable_management(outTablePath, outTableName)
    
    # process the user input to add id field to output table
    IDfield = arcpyutil.fields.getFieldByName(inReportingUnitFeature, reportingUnitIdField)
    arcpy.AddField_management(newTable, IDfield.name, IDfield.type, IDfield.precision, IDfield.scale)
                
    # add metric fields to the output table.
    [arcpy.AddField_management(newTable, metricsFieldnameDict[mClassName], fldParams[2], fldParams[3], fldParams[4])for mClassName in metricsClassNameList]

    # add any optional fields to the output table
    if qaCheckFlds:
        [arcpy.AddField_management(newTable, qaFld[0], qaFld[1], qaFld[2]) for qaFld in qaCheckFlds]
        
    if addAreaFldParams:
        [arcpy.AddField_management(newTable, metricsFieldnameDict[mClassName]+addAreaFldParams[0], addAreaFldParams[1], addAreaFldParams[2], addAreaFldParams[3])for mClassName in metricsClassNameList]
         
    # delete the 'Field1' field if it exists in the new output table.
    arcpyutil.fields.deleteFields(newTable, ["field1"])
    
        
    return newTable