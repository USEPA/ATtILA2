""" Road Density Metrics

    This script is associated with an ArcToolbox script tool.
    
"""


import sys
from ATtILA2 import metric
from pylet.arcpyutil import parameters
import arcpy

def main(_argv):
    
    # Script arguments
    inputArguments = parameters.getParametersAsText([0, 2, 3, 7])
    
    inputArguments = []
    for i in range(0,arcpy.GetArgumentCount()):
        inputArguments.append(arcpy.GetParameter(i))

    metric.runRoadDensityCalculator(*inputArguments)

if __name__ == "__main__":
    main(sys.argv)