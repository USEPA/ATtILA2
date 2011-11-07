'''
Created on Nov 1, 2011

@author: Donald Ebert
'''

import arcpy

QAtable = arcpy.GetParameterAsText(0)
QAIDfield = arcpy.GetParameterAsText(1)
QAValueField = arcpy.GetParameterAsText(2)
TableToCheck = arcpy.GetParameterAsText(3)
CheckIDfield = arcpy.GetParameterAsText(4)
FieldToCheck = arcpy.GetParameterAsText(5)


arcpy.JoinField_management(QAtable, QAIDfield, TableToCheck, CheckIDfield, [FieldToCheck])