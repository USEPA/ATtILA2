""" Identify Overlapping Polygons

    This script is associated with an ArcToolbox script tool.
"""

import sys
import arcpy
from pylet.arcpyutil import parameters
from pylet.arcpyutil import polygons
overlaplist = []
flist = []
nonoverlapGroupDict = {}

def checkOutputType(outputLoc):
    odsc = arcpy.Describe(outputLoc)
    # if output location is a folder then create a shapefile otherwise it will be a feature layer
    if odsc.DataType == "Folder":
        ext = ".shp"
    else:
        ext = ""
    return ext

def main(_argv):
    #Script arguments
    inputLayer = parameters.getParametersAsText([0])
    outputLoc = parameters.getParametersAsText([1])
    createOutput = parameters.getParametersAsText([2])
    result, OID, overlapDict = polygons.findOverlaps(inputLayer)
    overlapList = result
    #If there are overlaps the find unique groups of nonoverlapping polygons
    if result:
        arcpy.AddWarning("Warning your layer includes overlapping polygons! Calculating split")
        #Find groups of polygons that don't overlap
        nonoverlapGroupDict = polygons.findNonOverlapGroups(overlapDict)

        #If overlaps exists create new layers with no overlaps(creates new intermediate layer)
        ext = checkOutputType(outputLoc)
        polygons.createNonOverlapLayers(overlapList, nonoverlapGroupDict, OID, inputLayer, outputLoc, ext)
    else:
        arcpy.AddMessage("No overlaps Found")

   
if __name__ == "__main__":
    main(sys.argv)