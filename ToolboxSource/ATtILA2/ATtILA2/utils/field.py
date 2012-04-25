""" Utilities specific to fields

"""

def ProcessTabAreaValueFields(TabAreaValueFields, TabAreaValues, tabAreaDict, tabAreaTableRow, excludedValues):
    """ Processes the 'VALUE_' fields in a supplied row object for exclusion/inclusion status in metric area/percentage 
    calculations. 
    
    **Description:**
    
        1. Go through each 'VALUE_' field in the TabulateArea table one row at a time and put the area value
           for each grid code into a dictionary with the grid code as the key.
        2. Determine if the area for the grid code is to be included into the reporting unit effective area sum.
        3. Keep a running total of effective and excluded area within the reporting unit. Added together, these 
           area sums provide the total grid area present in the reporting unit. That value is used to calculate
           the amount of overlap between the reporting unit polygon and the underlying land cover grid.
           
    **Arguments:**

        * *TabAreaValueFields* - a list of the 'VALUE_' fieldnames from a TabulateArea generated table
        * *TabAreaValues* - a list of integer grid code values generated from the 'VALUE_' fieldnames
        * *tabAreaDict* - an empty dictionary to be populated with a key:value pair of gridcode:area
        * *tabAreaTableRow* - the current row object from TabluateArea output table arcpy SearchCursor
        * *excludedValues* - a frozenset of values not to use when calculating the reporting unit effective area.
        
    **Returns:**

        * dictionary - dictionary with the area value of each grid code in a reporting unit keyed to the grid code
        * float - sum of the area within the reporting unit to be included in the percentage calculations
        * float - sum of the area within the reporting unit to be excluded from percentage calculations
            
    """
    
    excludedAreaSum = 0  #area of reporting unit not used in metric calculations e.g., water area
    effectiveAreaSum = 0  #effective area of the reporting unit e.g., land area

    for i, aFld in enumerate(TabAreaValueFields):
        # store the grid code and it's area value into the dictionary
        valKey = TabAreaValues[i]
        valArea = tabAreaTableRow.getValue(aFld.name)
        tabAreaDict[valKey] = valArea

        #add the area of each grid value to the appropriate area sum i.e., effective or excluded area
        if valKey in excludedValues:
            excludedAreaSum += valArea
        else:
            effectiveAreaSum += valArea               
                       
    return (tabAreaDict, effectiveAreaSum, excludedAreaSum)