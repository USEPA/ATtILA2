''' Output Fields

    Constants and helper functions associated with creating output metric fields.
    
    (Formerly called OutFields.py)
'''

import os
import sys
from pylet import lcc

# Land Cover Proportions(lcp)
lcpMetricName = "LandCoverProportions"
lcpFieldPrefix = "p"
lcpOverlapName = "LCP_OVRLP"
lcpTotalAreaName = "LCP_TOT_A"
lcpEffectiveAreaName = "LCP_EFF_A"
lcpExcludedAreaName = "LCP_EXC_A"

# Riparian Proportions(rp)
rpMetricName = "RiparianProportions"
rpFieldPrefix = "r"
rpOverlapName = "R_OVERLAP"

# Land Cover Slope Overlap (lcso)
lcsoMetricName = "LandCoverSlopeOverlap"
lcsoFieldSuffix = "SL"
lcsoOverlapName = "SL_OVRLP"
lcsoTotalAreaName = "SL+TOT_A"
lcsoEffectiveAreaName = "SL_EFF_A"
lcsoExcludedAreaName = "SL_EXC_A"

# Field type defaults
defaultDecimalFieldType = "FLOAT"
defaultIntegerFieldType = "SHORT"
defaultAreaFieldType = "DOUBLE"


# Required field parameter info
fieldParameters = {lcpMetricName:[lcpFieldPrefix,"", defaultDecimalFieldType, 6, 1],
                   lcsoMetricName:["",lcsoFieldSuffix,defaultDecimalFieldType,6,1],
                   rpMetricName:[rpFieldPrefix,"", defaultDecimalFieldType, 6, 1]}

# Optional field parameter info
qaCheckFieldParameters = {lcpMetricName:[[lcpOverlapName, defaultIntegerFieldType, 6],
                                        [lcpTotalAreaName, defaultAreaFieldType, 15],
                                        [lcpEffectiveAreaName, defaultAreaFieldType, 15],
                                        [lcpExcludedAreaName, defaultAreaFieldType, 15]],
                         lcsoMetricName:[[lcsoOverlapName, defaultIntegerFieldType, 6],
                                         [lcsoTotalAreaName, defaultAreaFieldType, 15],
                                         [lcsoEffectiveAreaName, defaultAreaFieldType, 15],
                                         [lcsoExcludedAreaName, defaultAreaFieldType, 15]],
                           rpMetricName:[[rpOverlapName, defaultIntegerFieldType, 6]]}


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
        
        
def getQACheckFieldParametersFromFilePath(filePath=None, delimiter="_"):
    """ Parses full file path to look up optional field parameters
        
        No arguments are required.  If filePath is not given, it uses sys.argv[0] (full path to executed script)
        
        filePath:  full file path from which basename is split by delimiter, first item in split is used
        delimiter: character(s) by which basename is split
        
    """
    
    if not filePath:
        filePath = sys.argv[0]
    
    key = getKeyFromFilePath(filePath, delimiter)
    
    return qaCheckFieldParameters[key]


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


