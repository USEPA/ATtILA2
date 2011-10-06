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
      
    dirRelativePath = r"\bin"
    exeName = "LandCoverClassificationEditor.pyw" 
    thisFilePath = argv[0]
    thisDirPath = os.path.dirname(thisFilePath)
    exeDir = thisDirPath + dirRelativePath
    os.chdir(exeDir) 
    
    os.startfile(exeName)
    
if __name__ == "__main__":
    main(sys.argv)