# LandCoverProportions_ArcGIS.py
# Michael A. Jackson, jackson.michael@epa.gov, majgis@gmail.com
# 2011-10-04
""" Land Cover Proportion Metrics

    DESCRIPTION
    
    ARGUMENTS
    
    REQUIREMENTS
    Spatial Analyst Extension

"""

import sys
import arcpy

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

def main(argv):
    """ Start Here """
    # Script arguments
    Input_reporting_unit_feature = arcpy.GetParameterAsText(0)
    Reporting_unit_ID_field = arcpy.GetParameterAsText(1)
    Input_land_cover_grid = arcpy.GetParameterAsText(2)
    Land_cover_classification_file = arcpy.GetParameterAsText(3)
    Metrics_to_run = arcpy.GetParameterAsText(4)
    Output_table = arcpy.GetParameterAsText(5)
    
    
    # Preprocessing
    
    
    # Process: Tabulate Area
    try:
        tempEnvironment0 = arcpy.env.snapRaster
        arcpy.env.snapRaster = Snap_Raster
        arcpy.gp.TabulateArea_sa(Input_reporting_unit_feature, Reporting_unit_ID_field, Input_land_cover_grid, "Value", Output_table)
        arcpy.env.snapRaster = tempEnvironment0
        
        # get the value fields in tabarea table and sum
        
        
        for aMetric in Metrics_to_run:
            print ""
        
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        
    except:
        arcpy.AddError("Non-tool error occurred")
        
    finally:
        arcpy.env.snapRaster = tempEnvironment0
        arcpy.CheckInExtension("spatial")
    
if __name__ == "__main__":
    main(sys.argv)