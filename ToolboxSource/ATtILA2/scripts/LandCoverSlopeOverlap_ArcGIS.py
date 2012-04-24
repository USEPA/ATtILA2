""" Land Cover on Slope Proportion Metrics

    This script is associated with an ArcToolbox script tool.

"""


import sys
from ATtILA2 import metrics
from pylet.arcpyutil import parameters


def main(argv):
    
    # Script arguments
    inputArguments = parameters.getParametersAsText([0])
    
    metrics.common.landCoverOnSlopeProportions(*inputArguments)

    
if __name__ == "__main__":
    main(sys.argv)