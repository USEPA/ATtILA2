""" Tasks specific to checking and retrieving settings 
"""
from ATtILA2.constants import globalConstants
from pylet import arcpyutil
import arcpy


def getOutputLinearUnits(inputDataset):
    """ Determines the output coordinate system linear units name """
    # check for output coordinate system setting in the arc environment
    if arcpy.env.outputCoordinateSystem:
        # output coordinate system is set. get it's linear units to use for area conversions
        linearUnits = arcpy.env.outputCoordinateSystem.linearUnitName
    else:
        # no output coordinate system set. get the output linear units for the input reporting unit theme.
        # warning: only use this theme if it is the first theme specified in ensuing geoprocessing tools
        desc = arcpy.Describe(inputDataset)
        linearUnits = desc.spatialReference.linearUnitName
        
    return linearUnits


def getIdOutField(inFeature, inField):
    """ Processes the InputField. If field is an OID type, alters the output field type and name """
    inField = arcpyutil.fields.getFieldByName(inFeature, inField)
    
    if inField.type == "OID":
        newField = arcpy.Field()
        newField.type = "Integer" 
        newField.name = inField.name+"_ID"
        newField.precision = inField.precision
        newField.scale = inField.scale
    else:
        newField = inField
        
    return (newField)


def checkGridValuesInLCC(inLandCoverGrid, lccObj):
    """ Checks input grid values. Warns user if values are undefined in LCC XML file. """
    
    # warn user if input land cover grid has values not defined in LCC file
    rows = arcpy.SearchCursor(inLandCoverGrid) 

    gridValues = []    
    for row in rows:
        gridValues.append(row.getValue("VALUE"))
    
    undefinedValues = [aVal for aVal in gridValues if aVal not in lccObj.getUniqueValueIdsWithExcludes()]     
    if undefinedValues:
        arcpy.AddWarning("Following Grid Values undefined in LCC file: %s - Please refer to the %s documentation regarding undefined values." % 
                         (undefinedValues, globalConstants.titleATtILA))
        
    del row
    del rows