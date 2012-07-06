'''
Output validation module
begins with a byte comparison of the test file against the reference file
if test fails, performs further tests to identify differences

Created July 2012

@author: thultgren
'''

import filecmp
import arcpy

def compare(refFile, testFile):
    # This is a byte comparison of the two files, if it succeeds, it's safe to assume the files are identical
    result = filecmp.cmp(refFile, testFile, False)
    
    if result:
        return "Validation was successful"
    else:
        refDesc = arcpy.Describe(refFile)
        testDesc = arcpy.Describe(testFile)
        # Test to see if the files are different data types (i.e. dBase vs Infotable)
        if not refDesc.dataType == testDesc.dataType:
            return "Validation failed, the output was the incorrect data type, please try again with a " + refDesc.dataType
        else:
            refFieldNames = [x.name for x in refDesc.fields]
            testFieldNames = [x.name for x in testDesc.fields]
            extraFields = [x for x in testFieldNames if x not in refFieldNames]
            missingFields = [y for y in refFieldNames if y not in testFieldNames]
            # Test to see if all the fields match
            if missingFields or extraFields:
                message = "Validation failed, "
                if missingFields: 
                    message += "Output was missing these fields (" + ", ".join(missingFields) + ")\n"
                if extraFields:
                    message += "Output had these extra fields (" +  ", ".join(extraFields) + ")"
                return  message
            else:
                refCur = arcpy.SearchCursor(refFile)
                testCur = arcpy.SearchCursor(testFile)
                # Start testing table values, break on first difference
                for refRow, testRow in zip(refCur,testCur):
                    for field in refDesc.fields:
                        if not refRow.getValue(field.name) == testRow.getValue(field.name):
                            return "Validation failed, an error was found in row: " + \
                                str(refRow.getValue(refDesc.OIDFieldName)) + ", column: " + field.name
     
    return "Validation failed, cause unknown"                       