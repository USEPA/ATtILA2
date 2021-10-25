""" Near Road Land Cover Proportions

    This script is associated with an ArcToolbox script tool.

"""


import sys
from ATtILA2 import metric
from ATtILA2.utils import parameters


def main(_argv):
    
    # Script arguments
    inputArguments = parameters.getParametersAsText([0, 1])
    
    metric.runNearRoadLandCoverProportions(*inputArguments)
    
    
if __name__ == "__main__":
    main(sys.argv)