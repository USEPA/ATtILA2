'''
Created on Nov 1, 2011

@author: Donald Ebert

Description: Computes the difference between values from two selected fields in two different tables
'''

import arcpy
#from arcpy import env

try:
    #env.qualifiedFieldNames = False
    
    QATable = arcpy.GetParameterAsText(0)
    QAIDfield = arcpy.GetParameterAsText(1)
    QAValueField = arcpy.GetParameterAsText(2)
    TableToCheck = arcpy.GetParameterAsText(3)
    CheckIDfield = arcpy.GetParameterAsText(4)
    FieldToCheck = arcpy.GetParameterAsText(5)
    diffFieldname = arcpy.GetParameterAsText(6)
    
    # abort if join table is same as input table
    if QATable == TableToCheck:
        raise Exception("Table check error.") 
        

    arcpy.MakeTableView_management(TableToCheck, "CheckTableView")
    arcpy.MakeTableView_management(QATable, "QATableView")
    
    arcpy.JoinField_management("CheckTableView", CheckIDfield, "QATableView", QAIDfield, [FieldToCheck])
    
    theFields = arcpy.ListFields("CheckTableView")
    joinedFieldname = theFields[-1].name
    
    arcpy.AddField_management(TableToCheck, diffFieldname, "FLOAT", 6, 3)
         
    expression = "!"+FieldToCheck+"! - !"+joinedFieldname+"!"
    arcpy.CalculateField_management("CheckTableView", diffFieldname, expression, "PYTHON")
    
#except SameTableError:
#    arcpy.AddError("Input table and join table are identical. Cannot joint a table to itself. Terminating.")
     
except arcpy.ExecuteError:
    arcpy.AddError(arcpy.GetMessages(2))
    
except Exception, e:
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