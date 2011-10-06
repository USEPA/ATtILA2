# LandCoverProportions_ArcGIS.py
# Michael A. Jackson, jackson.michael@epa.gov, majgis@gmail.com
# 2011-10-04
""" Land Cover Proportion Metrics

    DESCRIPTION
    
    ARGUMENTS

"""

import sys
import arcpy

def main(argv):
    """ Start Here """
    # Input reporting unit and reporting unit ID field 
    RUThm = arcpy.GetParameterAsText(0)
    RUIDFld = arcpy.GetParameterAsText(1)
    
    
if __name__ == "__main__":
    main(sys.argv)