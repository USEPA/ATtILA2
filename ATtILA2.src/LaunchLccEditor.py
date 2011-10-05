# LaunchLccEditor_ArcGIS
# Michael A. Jackson, jackson.michael@epa.gov, majgis@gmail.com
# 2011-10-04
""" Launch the Land Cover Classification (LCC) Editor

    Launches the external editor for .lcc files from a toolbox tool
    The editor is started in a separate process, remaining open when ArcGIS is closed.
    
    No Arguments.
"""
import sys
import os

def main(argv):
    
    exeRelativePath = r"\bin\LandCoverClassificationEditor.exe"
    thisFilePath = argv[0]
    thisDirPath = os.path.dirname(thisFilePath)
    exeFullPath = thisDirPath + "\\" + exeRelativePath

    os.startfile(exeFullPath)

    
if __name__ == "__main__":
    main(sys.argv)