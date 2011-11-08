''' Output Fields

    Constants and helper functions associated with creating output metric fields.
    
'''

import os
import sys

# Required field parameter info
fieldParameters = {"LandCoverProportions":["p","", "FLOAT", 6, 1],
                   "RiparianProportions":[]}

# Optional field parameter info
optionalFieldParameters = {"LandCoverProportions":[["LC_OVERLAP", "FLOAT", 6, 1]],
                           "RiparianProportions":[["R_OVERLAP", "FLOAT", 6, 1]]}


def getFieldParametersFromFilePath(filePath=None, delimiter="_"):
    """ Parses full file path to look up required field parameters
        
        No arguments are required.  If filePath is not given, it uses sys.argv[0] (the full path to executed script)
        
        filePath:  full file path from which basename is split by delimiter, first item in split is used
        delimiter: character(s) by which basename is split
        
    """
    
    if not filePath:
        filePath = sys.argv[0]
    
    key = os.path.basename(filePath).split(delimiter)[0]
    
    return fieldParameters[key]
        
        
def getOptionalFieldParametersFromFilePath(filePath=None, delimiter="_"):
    """ Parses full file path to look up optional field parameters
        
        No arguments are required.  If filePath is not given, it uses sys.argv[0] (the full path to executed script)
        
        filePath:  full file path from which basename is split by delimiter, first item in split is used
        delimiter: character(s) by which basename is split
        
    """
    
    if not filePath:
        filePath = sys.argv[0]
    
    key = os.path.basename(filePath).split(delimiter)[0]
    
    return optionalFieldParameters[key]

