import os
import sys
import arcpy
import glob 
import runpy
from setupParameters import *

currentDir = os.getcwd()
parentDir = os.path.dirname(os.path.dirname(os.path.dirname(currentDir))) #Navigate three levels above
arcpy.AddMessage(parentDir)
ATtILA_pth = os.path.join(parentDir, 'ATtILA v3.tbx')

setup.ATtILA_pth = ATtILA_pth
setup.inGDB = sys.argv[1]
setup.outFolder = sys.argv[2]

#Initiate classes
setup = setup()
points = points()
lines = lines()
polygons = polygons()
rasters = rasters()

arcpy.env.overwriteOutput = 1 
arcpy.CheckOutExtension("Spatial")

def main(_argv):
    inputStrings = sys.argv[3].split(";")
    for item in inputStrings:
        string = item.strip("'")
        script = string.replace(" ", "") + ".py"
        if os.path.exists(script): 
            arcpy.AddMessage(f"{script} quality assurance (QA) test script found. Initializing run")
            runpy.run_path(script)
        else: 
            arcpy.AddWarning("Script not found")
    arcpy.AddMessage(f"\n\nQA scripts completed for {inputStrings}. For more details refer to logfiles located in {sys.argv[2]}.")

if __name__ == "__main__": 
    main(sys.argv)
