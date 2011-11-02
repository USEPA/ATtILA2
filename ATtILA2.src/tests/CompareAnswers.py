'''
Created on Nov 1, 2011

@author: Donald Ebert
'''

import arcpy

QAtable = arcpy.GetParameterAsText(0)
QAIDfield = arcpy.GetParameterAsText(1)
TableToCheck = arcpy.GetParameterAsText(2)
CheckIDfield = arcpy.GetParameterAsText(3)
FieldsToCheck = arcpy.GetParameterAsText(4)


arcpy.JoinField_management(QAtable, QAIDfield, TableToCheck, CheckIDfield, FieldsToCheck)