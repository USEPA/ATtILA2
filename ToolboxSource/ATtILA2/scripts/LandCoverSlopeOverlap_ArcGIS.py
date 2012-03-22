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
from arcpy.sa import *
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
    Input_slope_grid = arcpy.GetParameterAsText(6)
    Input_slope_threshold_value = arcpy.GetParameterAsText(7)
    Output_table = arcpy.GetParameterAsText(8)
    Processing_cell_size = arcpy.GetParameterAsText(9)
    Snap_raster = arcpy.GetParameterAsText(10)
    Optional_field_groups = arcpy.GetParameterAsText(11)
    
    # the variables row and rows are initially set to None, so that they can
    # be deleted in the finally block regardless of where (or if) script fails
    outTable_row, outTable_rows = None, None
    tabAreaTable_row, tabAreaTable_rows = None, None
    
    # get current snap environment to restore at end of script
    tempEnvironment0 = env.snapRaster
    # set the snap raster environment so the AG on Steep Slopes grid aligns with land cover grid cell boundaries
    env.snapRaster = Snap_raster
    env.cellSize = Processing_cell_size
    
    
    try:
        # XML Land Cover Coding file loaded into memory
        lccObj = lcc.LandCoverClassification(lccFilePath)
        # Get the lccObj values dictionary to determine if a grid code is to be included in the effective reporting unit area calculation
        lccValuesDict = lccObj.values
        # get the frozenset of excluded values (i.e., values not to use when calculating the reporting unit effective area)
        excludedValues = lccValuesDict.getExcludedValueIds()
        
        # Generate the slope X land cover gird where areas below the threshold slope are
        # set to the value 'Maximum Land Cover Class Value + 1'.
        LCGrid = Raster(Input_land_cover_grid)
        SLPGrid = Raster(Input_slope_grid)
        AreaBelowThresholdValue = int(LCGrid.maximum + 1)
        where_clause = "VALUE >= "+Input_slope_threshold_value
        SLPxLCGrid = Con(SLPGrid, LCGrid, AreaBelowThresholdValue, where_clause)

        # if certain land cover codes are tagged as 'excluded = TRUE', generate grid where land cover codes are 
        # preserved for areas coincident with steep slopes, areas below the slope threshold are coded with the 
        # AreaBelowThresholdValue except for where the land cover code is included in the excluded values list.
        # In that case, the excluded land cover values are maintained in the low slope areas.
        
        if excludedValues:
            # build a whereClause string (e.g. "VALUE = 11 or VALUE = 12") to identify where on the land cover grid excluded values occur
            whereExcludedClause = "VALUE = " + " or VALUE = ".join([str(item) for item in excludedValues])

            SLPxLCGrid = Con(LCGrid, LCGrid, SLPxLCGrid, whereExcludedClause)
            
        # save the file if intermediate products outputs are checked
        SLPxLCGrid.save(arcpy.CreateUniqueName("slxlc"))

        
        
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
        

def ParseCheckboxSelections(selectionsString):
    """ Returns a list of the items selected by the user.
        The expected input is a string with the following format: 'item<two spaces>description';'item<two spaces>description';'item...'
        e.g., the string, 'for  [pfor] Forest';'wetl  [pwetl]  wetland', becomes the list, ['for','wetl']
    """
    return map((lambda splitItemAndDesc: splitItemAndDesc.split('  ')[0]), selectionsString.replace("'","").split(';'))
    
    
if __name__ == "__main__":
    main(sys.argv)