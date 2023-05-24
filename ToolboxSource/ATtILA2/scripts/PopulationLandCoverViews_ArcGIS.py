""" Population Land Cover Views Metrics

    This script is associated with an ArcToolbox script tool.
    
"""


import sys
from ATtILA2 import metric
from ATtILA2.utils import parameters

def main(_argv):
    
    # Script arguments
    inputArguments = parameters.getParametersAsText([0, 2, 8])
    
    tbxPath = __file__.split("#")[0]
    inputArguments.insert(0, tbxPath)
    
    metric.runPopulationLandCoverViews(*inputArguments)

if __name__ == "__main__":
    main(sys.argv)