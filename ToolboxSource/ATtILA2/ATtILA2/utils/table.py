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
    '''This function transfers a series of fields from one table to another, and, if a class field is specified, pivots
       the metric fields for those class values into a new field for each class.
    **Description:**
        For each field specified, this function transfers the values from the source table to the destination table. 
        If no class field is specified, this is accomplished by the addJoinCalculateField function - a simple join based
        on reporting unit ID
        If a class field is specified, this function uses a search cursor and update cursor to pivot the metrics to 
        an output table with one row per reporting unit and a metric field for each class.
    **Arguments:**
        * *fromTable* - the source table
        * *toTable* - the destination table
        * *fromFields* - a python list of source fieldnames
        * *toFields* - a python list of desired ouptut fieldnames in the same order as the fromFields list
        * *joinField* - the field common to both tables on which to base the join.  it is assumed that in this context 
                        the fields have the same name in both tables - if this is not a safe assumption, this function 
                        may need to be modified in the future.
        * *classField* - optional field with class values that will be pivoted to output fields
        * *classValues* - a python list of unique values from the classField
    '''
    # Create a zipped list of fields to be transferred - packing and unpacking by using tuples is a little more elegant
    transferFields = zip(fromFields,toFields)
    # Start with the simple case, where no class field is specified.
    if classField == '#': 
        # Iterate through the field list and run the addJoinCalculateField function
        for (fromField,toField) in transferFields:
            addJoinCalculateField(fromTable,toTable,fromField,toField,joinField)
    else:
        # Now the tougher case - pivoting class values.
        # Create a dictionary that will link class values to tuples matching source fieldnames and valid destination fieldnames
        transferClassFields = {}
        # Sort the class values just so the output table fields are in a less random order
        classValues.sort()
        # For each combo of source and destination fields in the transferFields list
        for (fromField,toField) in transferFields:
            # For each class value in the class values list
            for classValue in classValues:
                # if the dictionary doesn't already have an element with this value as the key 
                if not transferClassFields.has_key(classValue):
                    # Add a new empty list to the dictionary with this classValue as key
                    transferClassFields[classValue] = []
                # Obtain a valid output fieldname that combines the desired output fieldname with this class value
                classToField = getClassFieldName(toField,classValue,toTable)
                # Save this combination of source and destination fieldnames to the list keyed to this class value in the dictionary
                transferClassFields[classValue].append((fromField,classToField))
                # Get the properties of the source field
                fromFieldObj = arcpy.ListFields(fromTable,fromField)[0]
                # Add the new field to the output table with the appropriate properties and the valid name
                arcpy.AddField_management(toTable,classToField,fromFieldObj.type,fromFieldObj.precision,fromFieldObj.scale,
                          fromFieldObj.length,fromFieldObj.aliasName,fromFieldObj.isNullable,fromFieldObj.required,
                          fromFieldObj.domain) 
        # In preparation for the upcoming whereclause, add the appropriate delimiters to the join field
        joinFieldDelim = arcpy.AddFieldDelimiters(fromTable,joinField)
        # In preparation for the upcoming whereclause, set up the appropriate delimiter function for the join value
        delimitJoinValues = arcpyutil.fields.valueDelimiter(arcpy.ListFields(fromTable,joinField)[0].type)
        # Initialize an update cursor on the output table
        updateCursor = arcpy.UpdateCursor(toTable)
        # For each row in the output table (each reporting unit)
        for updateRow in updateCursor:
            # Grab the reporting unit ID
            joinID = updateRow.getValue(joinField)
            # Create a whereclause for selecting the corresponding rows in the source table
            whereClause = joinFieldDelim + " = " + delimitJoinValues(joinID)
            # Initialize a search cursor on the source table for this reporting unit
            fetchCursor = arcpy.SearchCursor(fromTable,whereClause)
            # For each row in the source table (which should correspond to each class in this reporting unit)
            for fetchRow in fetchCursor:
                # obtain the class value that will link us to the correct output field
                classValue = fetchRow.getValue(classField)
                # for each desired output metric (which we have saved in a list of tuples with the input and valid output fieldnames)
                for (fromField,toField) in transferClassFields[classValue]:
                    # Set the output field value equal to the correct source value
                    updateRow.setValue(toField,fetchRow.getValue(fromField))
                # Clean up our row element for memory management and to remove locks
                del fetchRow
            # Clean up our row element for memory management and to remove locks
            del fetchCursor
            # Persist all of the updates for this row.
            updateCursor.updateRow(updateRow)
            # Clean up our row element for memory management and to remove locks
            del updateRow
        # Clean up our row element for memory management and to remove locks
        del updateCursor
            

def addJoinCalculateField(fromTable,toTable,fromField,toField,joinField):
    '''This function transfers one field to another via a simple JoinField operation, but also allows for a field to be 
       renamed as part of the transfer.
    **Description:**
        The arcpy.JoinField function permanently joins a specified field to an output table, but does not allow that
        field to be renamed.  This function facilitates that renaming by first adding and populating the desired field
        to the source table, then joining the renamed field to the output table, then cleaning up the renamed field
        from the source table.  
    **Arguments:**
        * *fromTable* - the source table
        * *toTable* - the destination table
        * *fromField* - the source fieldname
        * *toField* - the desired output fieldname
        * *joinField* - the field common to both tables on which to base the join.  it is assumed that in this context 
                        the fields have the same name in both tables - if this is not a safe assumption, this function 
                        may need to be modified in the future.
    '''
    if fromField <> toField:
        # Get the properties of the from field for transfer
        fromField = arcpy.ListFields(fromTable,fromField)[0]
        arcpy.AddField_management(fromTable,toField,fromField.type,fromField.precision,fromField.scale,
                              fromField.length,fromField.aliasName,fromField.isNullable,fromField.required,
                              fromField.domain)        
        arcpy.CalculateField_management(fromTable,toField,'!'+ fromField.name +'!',"PYTHON")
    arcpy.JoinField_management(toTable,joinField,fromTable,joinField,toField)
    if fromField <> toField:
        arcpy.DeleteField_management(fromTable,toField)
    
def getClassFieldName(fieldName,classVal,table):
    '''This function generates a valid fieldname based on the combination of a desired fieldname and a class value
    **Description:**
        The expectation for the ATtILA output table is one field per metric per class value, if a class is specified.
        A simple concatenation of metric fieldname and class value has the potential to be trimmed, depending on the
        limits of the output table format (i.e. 10 characters for dbf files).  This function thus concatenates the
        desired fieldname with the specified class value, tries the arcpy field validation, and if the concatenated
        fieldname gets shortened, trims the desired fieldname by the appropriate amount so that the class value is 
        always the final characters of the fieldname string.  
    **Arguments:**
        * *fieldName* - the desired metric fieldname to which the class value will be appended
        * *classVal* - the class value as a string
        * *table* - the table to which the field will be added 
    **Returns:**
        * *validFieldName* - validated fieldname 
    '''
    testFieldName = fieldName + classVal
    validFieldName = arcpy.ValidateFieldName(testFieldName, table)
    if len(testFieldName)>len(validFieldName):
        trim = len(validFieldName) - len(testFieldName)
        testFieldName = fieldName[:trim] + classVal
        validFieldName = arcpy.ValidateFieldName(testFieldName, table)
    return validFieldName

