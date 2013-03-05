''' Utilities specific to tables


    .. _arcpy: http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#/What_is_ArcPy/000v000000v7000000/
    .. _Table: 
'''
import os
import arcpy
from pylet import arcpyutil
from ATtILA2.constants import globalConstants

def createMetricOutputTable(outTable, outIdField, metricsBaseNameList, metricsFieldnameDict, metricFieldParams, 
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
    outIdFieldType = arcpyutil.fields.convertFieldTypeKeyword(outIdField)
    
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


def tableWriterByClass(outTable, metricsBaseNameList, optionalGroupsList, metricConst, lccObj, outIdField):
    """ Processes tool dialog parameters and options for output table generation. Class metrics option.
        
    **Description:**

        Processes the input and output parameters and selected options from the ATtILA tool dialog for output table
        generation. After processing the data, this function calls the CreateMetricTableOutput function which
        creates an empty table with fields for the reporting unit id, all selected metrics with appropriate fieldname
        prefixes and suffixes (e.g. pUrb, rFor30), and any selected optional fields (e.g., LC_Overlap). 
        
        This function is used when the selected metrics are represented by the class nodes in the .lcc file
        
        Returns the created output table and a dictionary of the selected lcc classes and their generated fieldnames
        
    **Arguments:**

        * *outTable* - file name including path for the ATtILA output table

        * *metricsBaseNameList* - a list of metric BaseNames parsed from the 'Metrics to run' input 
                        (e.g., [for, agt, shrb, devt] or [NITROGEN, IMPERVIOUS])

        * *optionalGroupsList* - list of the selected options parsed from the 'Select options' input
                        (e.g., ["QAFIELDS", "AREAFIELDS", "INTERMEDIATES"])
        * *metricConst* - a class object with the variable constants for a particular metric family as attributes 
        * *lccObj* - a class object of the selected land cover classification file 
        * *outIdField* - the output id field. Generally a clone of the input id field except where the fieldtype = "OID"
        
    **Returns:**

        * table (type unknown - string representation?)
        * dict - a dictionary of BaseName keys with field name values (e.g., "unat":"UINDEX", "for":"pFor", 
                        "NITROGEN":"N_Pload")
        
    """

    # get the field name override key
    fieldOverrideKey = metricConst.fieldOverrideKey

    # Set parameters for metric output field. 
    metricFieldParams = metricConst.fieldParameters
    
    # Parameratize optional fields, e.g., optionalFlds = [["LC_Overlap","FLOAT",6,1]]
    if globalConstants.qaCheckName in optionalGroupsList:
        qaCheckFlds = metricConst.qaCheckFieldParameters
    else:
        qaCheckFlds = None
    
    maxFieldNameSize = arcpyutil.fields.getFieldNameSizeLimit(outTable)            
    if globalConstants.metricAddName in optionalGroupsList:
        addAreaFldParams = globalConstants.areaFieldParameters
        maxFieldNameSize = maxFieldNameSize - len(addAreaFldParams[0])
    else:
        addAreaFldParams = None
    
    # Process: inputs
    # get dictionary of metric class values (e.g., classValuesDict['for'].uniqueValueIds = (41, 42, 43))
    lccClassesDict = lccObj.classes    
    
    # use the metricsBaseNameList to create a dictionary of BaseName keys with field name values using any user supplied field names
    metricsFieldnameDict = {}
    outputFieldNames = set() # use this set to help make field names unique
    
    for mBaseName in metricsBaseNameList:
        # generate unique number to replace characters at end of truncated field names
        n = 1
        
        fieldOverrideName = lccClassesDict[mBaseName].attributes.get(fieldOverrideKey,None)
        if fieldOverrideName: # a field name override exists
            # see if the provided field name is too long for the output table type
            if len(fieldOverrideName) > maxFieldNameSize:
                defaultFieldName = fieldOverrideName # keep track of the originally provided field name
                fieldOverrideName = fieldOverrideName[:maxFieldNameSize] # truncate field name to maximum allowable size
                
                # see if truncated field name is already used.
                # if so, truncate further and add a unique number to the end of the name
                while fieldOverrideName in outputFieldNames:
                    # shorten the field name and increment it
                    truncateTo = maxFieldNameSize - len(str(n))
                    fieldOverrideName = fieldOverrideName[:truncateTo]+str(n)
                    n = n + 1
                
                arcpy.AddWarning(globalConstants.metricNameTooLong.format(defaultFieldName, fieldOverrideName))
                
            # keep track of output field names    
            outputFieldNames.add(fieldOverrideName)
            # add output field name to dictionary
            metricsFieldnameDict[mBaseName] = fieldOverrideName
        else:
            # generate output field name
            outputFName = metricFieldParams[0] + mBaseName + metricFieldParams[1]
            
            # see if the provided field name is too long for the output table type
            if len(outputFName) > maxFieldNameSize:
                defaultFieldName = outputFName # keep track of the originally generated field name
                
                prefixLen = len(metricFieldParams[0])
                suffixLen = len(metricFieldParams[1])
                maxBaseSize = maxFieldNameSize - prefixLen - suffixLen
                
                # truncate field name to maximum allowable size    
                outputFName = metricFieldParams[0] + mBaseName[:maxBaseSize] + metricFieldParams[1]
                
                # see if truncated field name is already used.
                # if so, truncate further and add a unique number to the end of the name
                while outputFName in outputFieldNames:
                    # shorten the field name and increment it
                    truncateTo = maxBaseSize - len(str(n))
                    outputFName = metricFieldParams[0]+mBaseName[:truncateTo]+str(n)+metricFieldParams[1]
                    n = n + 1
                    
                arcpy.AddWarning(globalConstants.metricNameTooLong.format(defaultFieldName, outputFName))
                
            # keep track of output field names
            outputFieldNames.add(outputFName)
            # add output field name to dictionary
            metricsFieldnameDict[mBaseName] = outputFName
                
    # create the specified output table
    newTable = createMetricOutputTable(outTable,outIdField,metricsBaseNameList,metricsFieldnameDict, 
                                                           metricFieldParams, qaCheckFlds, addAreaFldParams)
    
    return newTable, metricsFieldnameDict


def tableWriterByCoefficient(outTable, metricsBaseNameList, optionalGroupsList, metricConst, lccObj, outIdField):
    """ Processes tool dialog parameters and options for output table generation. Coefficient metrics option.
        
    **Description:**

        Processes the input and output parameters and selected options from the ATtILA tool dialog for output table
        generation. After processing the data, this function calls the CreateMetricTableOutput function which
        creates an empty table with fields for the reporting unit id, all selected metrics with appropriate fieldname
        prefixes and suffixes (e.g. pUrb, rFor30), and any selected optional fields (e.g., LC_Overlap). 
        
        This function is used when the selected metrics are represented by the coefficient node in the .lcc file
        
        Returns the created output table and a dictionary of the selected lcc coefficients and their generated fieldnames
        
    **Arguments:**

        * *outTable* - file name including path for the ATtILA output table

        * *metricsBaseNameList* - a list of metric BaseNames parsed from the 'Metrics to run' input 
                        (e.g., [for, agt, shrb, devt] or [NITROGEN, IMPERVIOUS])

        * *optionalGroupsList* - list of the selected options parsed from the 'Select options' input
                        (e.g., ["QAFIELDS", "AREAFIELDS", "INTERMEDIATES"])
        * *metricConst* - a class object with the variable constants for a particular metric family as attributes 
        * *lccObj* - a class object of the selected land cover classification file 
        * *outIdField* - the output id field. Generally a clone of the input id field except where the fieldtype = "OID"
        
    **Returns:**

        * table (type unknown - string representation?)
        * dict - a dictionary of BaseName keys with field name values (e.g., "unat":"UINDEX", "for":"pFor", 
                        "NITROGEN":"N_Pload")
        
    """
    
    maxFieldNameSize = arcpyutil.fields.getFieldNameSizeLimit(outTable)            
        
    # use the metricsBaseNameList to create a dictionary of ClassName keys with field name values using any user supplied field names
    metricsFieldnameDict = {}
    outputFieldNames = set() # use this set to help make field names unique
    
    # get parameters for metric output field: [Fieldname_prefix, Fieldname_suffix, Field_type, Field_Precision, Field_scale]
    metricFieldParams = metricConst.fieldParameters
    
    for mBaseName in metricsBaseNameList:
        # generate unique number to replace characters at end of truncated field names
        n = 1
        
        fieldOverrideName = lccObj.coefficients[mBaseName].fieldName

        # see if the provided field name is too long for the output table type
        if len(fieldOverrideName) > maxFieldNameSize:
            defaultFieldName = fieldOverrideName # keep track of the originally provided field name
            fieldOverrideName = fieldOverrideName[:maxFieldNameSize] # truncate field name to maximum allowable size
            
            # see if truncated field name is already used.
            # if so, truncate further and add a unique number to the end of the name
            while fieldOverrideName in outputFieldNames:
                # shorten the field name and increment it
                truncateTo = maxFieldNameSize - len(str(n))
                fieldOverrideName = fieldOverrideName[:truncateTo]+str(n)
                n = n + 1
                
            arcpy.AddWarning("Provided metric name too long for output location. Truncated %s to %s" % 
                             (defaultFieldName, fieldOverrideName))
            
        # keep track of output field names    
        outputFieldNames.add(fieldOverrideName)
        # add output field name to dictionary
        metricsFieldnameDict[mBaseName] = fieldOverrideName

    # set up field parameters for any optional output fields
    if globalConstants.qaCheckName in optionalGroupsList:
        # get optional fields and their parameters, e.g., optionalFlds = [["LC_Overlap","FLOAT",6,1]]
        qaCheckFields = metricConst.qaCheckFieldParameters
    else:
        qaCheckFields = None
              
    # create the specified output table
    newTable = createMetricOutputTable(outTable,outIdField,metricsBaseNameList,metricsFieldnameDict, 
                                                           metricFieldParams, qaCheckFields)
    
    return newTable, metricsFieldnameDict


def transferField(fromTable,toTable,fromFields,toFields,joinField,classField="#",classValues=[]):
    """ This is currently undocumented and needs documentation """    
    toTableView = arcpy.MakeTableView_management(toTable,"toTableView")
    transferFields = zip(fromFields,toFields)
    for (fromField,toField) in transferFields:
        if classField == '#':
            whereClause = ""
            addJoinCalculateField(fromTable,toTableView,fromField,toField,joinField,whereClause)
        else:
            classFieldDelim = arcpy.AddFieldDelimiters(fromTable,classField)
            delimitRUValues = arcpyutil.fields.valueDelimiter(arcpy.ListFields(fromTable,classField)[0].type)
            for classVal in classValues:
                outField = toField + str(classVal)
                whereClause = classFieldDelim + " = " + delimitRUValues(classVal)
                addJoinCalculateField(fromTable,toTableView,fromField,outField,joinField,whereClause)
    arcpy.Delete_management(toTableView)

def addJoinCalculateField(fromTable,toTableView,fromField,outField,joinField,whereClause):
    """ This is currently undocumented and needs documentation """
    # Get the properties of the from field for transfer
    fromField = arcpy.ListFields(fromTable,fromField)[0]
    arcpy.AddField_management(toTableView,outField,fromField.type,fromField.precision,fromField.scale,
                          fromField.length,fromField.aliasName,fromField.isNullable,fromField.required,
                          fromField.domain)        
    fromTableView = arcpy.MakeTableView_management(fromTable,"fromTableView",whereClause)
    arcpy.JoinField_management(toTableView,joinField,fromTableView,joinField,fromField.name)
    arcpy.CalculateField_management(toTableView,fromField.name,'!'+ outField +'!',"PYTHON")
    arcpy.Delete_management(fromTableView)
