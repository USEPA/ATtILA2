''' Utilities specific to tables


    .. _arcpy: http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#/What_is_ArcPy/000v000000v7000000/
    .. _Table: 
'''
import os
import arcpy
from pylet import arcpyutil

def CreateMetricOutputTable(outTable, outIdField, metricsBaseNameList, metricsFieldnameDict, metricFieldParams, 
                            qaCheckFlds=None, addAreaFldParams=None):
    """ Returns new empty table for ATtILA metric generation output with appropriate fields for selected metric
    
    **Description:**

        Creates an empty table with fields for the reporting unit id, all selected metrics with appropriate fieldname
        prefixes and suffixes (e.g. pUrb, rFor30), and any selected optional fields (e.g., LC_Overlap)
        
    **Arguments:**

        * *outTable* - file name including path for the ATtILA output table
        * *inReportingUnitFeature* - CatalogPath to the input reporting unit layer
        * *reportingUnitIdField* - fieldname for the input reporting unit id field
        * *metricsBaseNameList* - a list of metric BaseNames parsed from the 'Metrics to run' input 
                                    (e.g., [for, agt, shrb, devt] or [NITROGEN, IMPERVIOUS])
        * *metricsFieldnameDict* - a dictionary of BaseName keys with field name values 
                                    (e.g., "unat":"UINDEX", "for":"pFor", "NITROGEN":"N_Pload")
        * *metricFieldParams* - list of parameters to generate the selected metric output field 
                        (i.e., [Fieldname_prefix, Fieldname_suffix, Field_type, Field_Precision, Field_scale])
        * *qaCheckFlds* - a list of filename parameter lists for one or more selected optional fields fieldname 
                        generation (e.g., optionalFlds = [["LC_Overlap","FLOAT",6,1]])
        * *addAreaFldParams* - a list of filename parameters for the optional Add Area Fields selection 
                        (e.g., ["_A","DOUBLE",15,0])
        
    **Returns:**

        * table (type unknown - string representation?)
        
    """
    outTablePath, outTableName = os.path.split(outTable)
        
    # need to strip the dbf extension if the outpath is a geodatabase; 
    # should control this in the validate step or with an arcpy.ValidateTableName call
    newTable = arcpy.CreateTable_management(outTablePath, outTableName)
    
    # Field objects in ArcGIS 10 service pack 0 have a type property that is incompatible with some of the AddField 
    # tool's Field Type keywords. This addresses that issue
    outIdFieldType = outIdField.type
    if outIdField.type.lower() == "string":
        outIdFieldType = "TEXT"
    
    arcpy.AddField_management(newTable, outIdField.name, outIdFieldType, outIdField.precision, outIdField.scale)
                
    # add metric fields to the output table.
    [arcpy.AddField_management(newTable, metricsFieldnameDict[mBaseName], metricFieldParams[2], metricFieldParams[3], 
                               metricFieldParams[4])for mBaseName in metricsBaseNameList]

    # add any optional fields to the output table
    if qaCheckFlds:
        [arcpy.AddField_management(newTable, qaFld[0], qaFld[1], qaFld[2]) for qaFld in qaCheckFlds]
        
    if addAreaFldParams:
        [arcpy.AddField_management(newTable, metricsFieldnameDict[mBaseName]+addAreaFldParams[0], addAreaFldParams[1], 
                                   addAreaFldParams[2], addAreaFldParams[3])for mBaseName in metricsBaseNameList]
         
    # delete the 'Field1' field if it exists in the new output table.
    arcpyutil.fields.deleteFields(newTable, ["field1"])
    
        
    return newTable


