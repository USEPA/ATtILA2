# LandCoverSlopeOverlap_ArcGIS.py
# Michael A. Jackson, jackson.michael@epa.gov, majgis@gmail.com
# Donald W. Ebert, ebert.donald@epa.gov
# 2012-03-15
""" Land Cover Slope Overlap Metrics

    DESCRIPTION
    
    ARGUMENTS
    
    REQUIREMENTS
    Spatial Analyst Extension

"""

import arcpy, os, sys
from arcpy import env
from pylet import lcc
from ATtILA2.metrics import fields as outFields

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

def main(argv):
    """ Start Here """
    # Script arguments
    Input_reporting_unit_feature_object = arcpy.GetParameter(0)
    Reporting_unit_ID_field = arcpy.GetParameterAsText(1)
    Input_land_cover_grid = arcpy.GetParameterAsText(2)
    lccFilePath = arcpy.GetParameterAsText(4)
    Metrics_to_run = arcpy.GetParameterAsText(5)
    Output_table = arcpy.GetParameterAsText(6)
    Processing_cell_size = arcpy.GetParameterAsText(7)
    Snap_raster = arcpy.GetParameterAsText(8)
    Optional_field_groups = arcpy.GetParameterAsText(9)
    
    # the variables row and rows are initially set to None, so that they can
    # be deleted in the finally block regardless of where (or if) script fails
    outTable_row, outTable_rows = None, None
    tabAreaTable_row, tabAreaTable_rows = None, None
    
    # get current snap environment to restore at end of script
    tempEnvironment0 = env.snapRaster
    
    
    try:
        print "hello world"
        
        
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        
    except:
        import traceback
        # get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        
        # Concatenate information together concerning the error into a message string
        
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
    
        # Return python error messages for use in script tool
        
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)
        
    finally:
        # delete cursor and row objects to remove locks on the data
        if outTable_row: del outTable_row
        if outTable_rows: del outTable_rows
        if tabAreaTable_rows: del tabAreaTable_rows
        if tabAreaTable_row: del tabAreaTable_row
            
        # restore the environments
        env.snapRaster = tempEnvironment0
        
        # return the spatial analyst license    
        arcpy.CheckInExtension("spatial")
        
        print "Finished."
    
    
if __name__ == "__main__":
    main(sys.argv)