# arcpyh.py
# Michael A. Jackson - jackson.michael@epa.gov, majgis@gmail.com
# 2011-09-22

"""
arcpy helper

System Requirements:
    ArcGIS 10.0 (Python 2.6)
    
"""

def getSortedFieldMappings(arcpy, tablePath, putTheseFirst):
    """ Return sorted field mappings of the given table

        arcpy: instance of arcpy module
        tablePath:  Path to a table
        putTheseFirst: list of field names to put first; order is matched
        
        Example usage:
        
            fieldMappings = arcpyh.getSortedFieldMappings(arcpy, inTablePath, putTheseFirst)
            arcpy.TableToTable_conversion(inTablePath, outWorkspace, outName, None, fieldMappings)
        
    """
    
    fieldMappings = arcpy.FieldMappings()
    fieldMappings.addTable(tablePath)

    fieldMaps = [fieldMappings.getFieldMap(fieldIndex) for fieldIndex in range(0,fieldMappings.fieldCount)]
    fieldMaps.sort(key=lambda fmap: fmap.getInputFieldName(0).lower())

    if putTheseFirst:
        # Move those matching putTheseFirst to front of list
        for fieldMapsIndex, fieldMap in enumerate(fieldMaps):
            fieldName = fieldMap.getInputFieldName(0).lower()
            if fieldName in putTheseFirst:
                fieldMaps.insert(0, fieldMaps.pop(fieldMapsIndex))
                
        # Make order of those moved to front of list match putTheseFirst
        for putTheseFirstIndex, inFieldName in enumerate(putTheseFirst):
            for fieldMapsIndex, fieldMap in enumerate(fieldMaps):
                fieldName = fieldMap.getInputFieldName(0).lower()
                if inFieldName == fieldName:
                    if putTheseFirstIndex != fieldMapsIndex:
                        fieldMaps.insert(putTheseFirstIndex, fieldMaps.pop(fieldMapsIndex))
                    break;

    fieldMappings.removeAll()
    
    for fieldMap in fieldMaps:
        fieldMappings.addFieldMap(fieldMap)

    return fieldMappings
