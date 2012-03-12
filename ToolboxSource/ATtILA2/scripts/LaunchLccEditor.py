# LaunchLccEditor_ArcGIS
# Michael A. Jackson, jackson.michael@epa.gov, majgis@gmail.com
# 2011-10-04
""" Launch the Land Cover Classification (LCC) Editor

    Launches the external editor for .lcc files from a toolbox tool
    The editor is started in a separate process, remaining open when ArcGIS is closed.
    
    The extra python script is used as a work-around for UserAccountControl dialog showing
    behind geoprocessing window when launched directly.
    
    No Arguments.
"""
import sys
import os

def main(argv):
      

    exeName = "LandCoverClassificationEditor.pyw" 

    os.startfile(exeName)
    
if __name__ == "__main__":
    main(sys.argv)