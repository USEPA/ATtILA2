''' Output Fields

    Constants and helper functions associated with creating output metric fields.
    
'''

import os
import sys
import lcc

# Land Cover Proportions(lcp)
lcpMetricName = "LandCoverProportions"
lcpFieldPrefix = "p"
lcpOverlapName = "LC_OVERLAP"

# Riparian Proportions(rp)
rpMetricName = "RiparianProportions"
rpFieldPrefix = "r"
rpOverlapName = "R_OVERLAP"

# Field type defaults
defaultDecimalFieldType = "FLOAT"
defaultIntegerFieldType = "SHORT"


# Required field parameter info
fieldParameters = {lcpMetricName:[lcpFieldPrefix,"", defaultDecimalFieldType, 6, 1],
                   rpMetricName:[rpFieldPrefix,"", defaultDecimalFieldType, 6, 1]}

# Optional field parameter info
optionalFieldParameters = {lcpMetricName:[[lcpOverlapName, defaultIntegerFieldType, 6, 0]],
                           rpMetricName:[[rpOverlapName, defaultIntegerFieldType, 6, 0]]}


# field Override keys
fieldOverrideKeys = {lcpMetricName: lcc.constants.XmlAttributeLcpField,
                     rpMetricName: lcc.constants.XmlAttributeRpField}


def getFieldParametersFromFilePath(filePath=None, delimiter="_"):
    """ Parses full file path to look up required field parameters
        
        No arguments are required.  If filePath is not given, it uses sys.argv[0] (full path to executed script)
        
        filePath:  full file path from which basename is split by delimiter, first item in split is used
        delimiter: character(s) by which basename is split
        
    """
    
    if not filePath:
        filePath = sys.argv[0]
    
    key = getKeyFromFilePath(filePath, delimiter)
    
    return fieldParameters[key]
        
        
def getOptionalFieldParametersFromFilePath(filePath=None, delimiter="_"):
    """ Parses full file path to look up optional field parameters
        
        No arguments are required.  If filePath is not given, it uses sys.argv[0] (full path to executed script)
        
        filePath:  full file path from which basename is split by delimiter, first item in split is used
        delimiter: character(s) by which basename is split
        
    """
    
    if not filePath:
        filePath = sys.argv[0]
    
    key = getKeyFromFilePath(filePath, delimiter)
    
    return optionalFieldParameters[key]


def getFieldOverrideKeyFromFilePath(filePath=None, delimiter="_"):
    """ Parse full file path to look up Field Override Key
    
        No arguments are required.  If filePath is not given, it uses sys.argv[0] (full path to executed script)
        
        filePath:  full file path from which basename is split by delimiter, first item in split is used
        delimiter: character(s) by which basename is split

    """
    
    if not filePath:
        filePath = sys.argv[0]
    
    key = getKeyFromFilePath(filePath, delimiter)
    
    return fieldOverrideKeys[key]


def getKeyFromFilePath(filePath, delimiter):
    """ Parses full file path to return embedded key.
    
        Expected format:  <key><delimiter>anything
    """

    return os.path.basename(filePath).split(delimiter)[0]


