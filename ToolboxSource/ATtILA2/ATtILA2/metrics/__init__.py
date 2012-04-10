import constants
import fields
import os


def getKeyFromFilePath(filePath, delimiter="_"):
    """ Parses full file path to return embedded key.
    
        Expected format:  <key><delimiter>anything
    """

    return os.path.basename(filePath).split(delimiter)[0]

