""" Utilitites specific to area

"""


def getMetricPercentAreaAndSum(metricGridCodesList, tabAreaDict, effectiveAreaSum):
    """ Calculates the percentage of the reporting unit effective area occupied by the metric class codes and their total area
    
        DESCRIPTION
        -----------
        Retrieves stored area figures for each grid code associated with selected metric and sums them.
        That number, divided by the total effective area within the reporting unit and multiplied by 100, gives the
        percentage of the effective reporting unit that is occupied by the metric class. Both the percentage and the 
        final area sum are returned.
        
        PARAMETERS
        ----------
        metricGridCodesList: list of all grid values assigned to a metric class in the lcc file (e.g., [41, 42, 43] for the forest class)
        tabAreaDict: dictionary with the area value of each grid code in a reporting unit keyed to the grid code
        effectiveAreaSum: sum of the area of all grid cells in the reporting unit with codes not tagged as excluded in the lcc file
        
        RETURNS
        -------
        Tuple:
            float 1 - the percentage of the reporting unit effective area that is occupied by the metric class codes
            float 2 - the sum of the area of metric class codes
        
    """
    
    metricAreaSum = 0                         
    for aValueID in metricGridCodesList:
        metricAreaSum += tabAreaDict.get(aValueID, 0) #add 0 if the lcc defined value is not found in the grid
    
    if effectiveAreaSum > 0:
        metricPercentArea = (metricAreaSum / effectiveAreaSum) * 100
    else: # all values found in reporting unit are in the excluded set
        metricPercentArea = 0
        
    return metricPercentArea, metricAreaSum