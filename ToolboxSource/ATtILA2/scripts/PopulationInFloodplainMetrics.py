""" Population In Floodplain Metrics

    This script is associated with an ArcToolbox script tool.
    
"""


import sys
from ATtILA2 import metric
from ATtILA2.utils import parameters


def main(_argv):
    
    # Script arguments
    inputArguments = parameters.getParametersAsText([0, 2, 4])
    
    tbxPath = __file__.split("#")[0]
    inputArguments.insert(0, tbxPath)
    
    metric.runPopulationInFloodplainMetrics(*inputArguments)
    
if __name__ == "__main__":
    main(sys.argv)
    