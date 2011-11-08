'''
Created on Nov 1, 2011

@author: Donald Ebert
'''

import arcpy
import os
from arcpy import env

QAtable = arcpy.GetParameterAsText(0)
QAIDfield = arcpy.GetParameterAsText(1)
QAValueField = arcpy.GetParameterAsText(2)
TableToCheck = arcpy.GetParameterAsText(3)
CheckIDfield = arcpy.GetParameterAsText(4)
FieldToCheck = arcpy.GetParameterAsText(5)

try:
    env.qualifiedFieldNames = False
    
    QAtable = arcpy.GetParameterAsText(0)
    QAIDfield = arcpy.GetParameterAsText(1)
    QAValueField = arcpy.GetParameterAsText(2)
    TableToCheck = arcpy.GetParameterAsText(3)
    CheckIDfield = arcpy.GetParameterAsText(4)
    FieldToCheck = arcpy.GetParameterAsText(5)

    # Get the new field name and validate it.
    diffFieldName = arcpy.GetParameterAsText(6)    
    #diffFieldName = arcpy.ValidateFieldName(diffFieldName, os.path.dirname(TableToCheck))
    arcpy.AddField_management(TableToCheck, diffFieldName, "FLOAT", 6, 3)
    arcpy.JoinField_management(TableToCheck, CheckIDfield, QAtable, QAIDfield)
    
    
    
    arcpy.RemoveJoin_management(TableToCheck, QAtable)
    
except arcpy.ExecuteError:
    arcpy.AddError(arcpy.GetMessages(2))
    
except:
    # get the traceback object
    import sys
    import traceback
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    
    # Concatenate information together concerning the error into a message string
    
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"

    # Return python error messages for use in script tool
    
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)