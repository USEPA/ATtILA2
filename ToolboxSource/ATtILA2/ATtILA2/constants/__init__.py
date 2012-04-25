import metricConstants as mc
import applicationConstants as ac
import ATtILA2
import sys

def getMetricContantsFromFilePath(filePath=None, delimiter="_"):
    """ Parses full file path to look up constants
        
        No arguments are required.  If filePath is not given, it uses sys.argv[0] (full path to executed script)
        
        filePath:  full file path from which basename is split by delimiter, first item in split is used
        delimiter: character(s) by which basename is split
        
    """
    
    if not filePath:
        filePath = sys.argv[0]
    
    key = ATtILA2.utils.files.getKeyFromFilePath(filePath, delimiter)
    
    if key == mc.rpConstants.name:
        return mc.rpConstants()
    
    if key == mc.lcospConstants.name:
        return mc.lcospConstants
    
    if key == mc.lcpConstants.name:
        return mc.lcpConstants





