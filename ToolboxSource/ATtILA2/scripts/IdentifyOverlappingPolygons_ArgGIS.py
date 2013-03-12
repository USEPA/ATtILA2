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

def main(_argv):
    #Script arguments
    inputArguments = parameters.getParametersAsText([0])
    result, OID, overlapDict = polygons.findOverlaps(*inputArguments)
    overlapList = result
    #If there are overlaps the find unique groups of nonoverlapping polygons
    if result:
        arcpy.AddWarning("Warning your layer includes overlapping polygons! Calculating split")
        #Find groups of polygons that don't overlap
        nonoverlapGroupDict = polygons.findNonOverlapGroups(overlapDict)

        #If overlaps exists creat new layers with no overlaps(creates new intermediate layer)
        polygons.createNonOverlapLayers(overlapList, nonoverlapGroupDict, OID, *inputArguments)
    else:
        arcpy.AddMessage("No overlaps Found")

    ##    #For each layer in flist add them to ArcMap
    ##    # Add the feature layer to ArcMap - keep in mind this is just a temporary layer.  It is actually a subset of the input layer
    ##    for f in flist:
    ##        mxd = arcpy.mapping.MapDocument("Current")
    ##        df = arcpy.mapping.ListDataFrames(mxd, "Layers") [0]
    ##        addlayer = arcpy.mapping.Layer(f)
    ##        arcpy.mapping.AddLayer(df, addlayer, "BOTTOM")
   
if __name__ == "__main__":
    main(sys.argv)