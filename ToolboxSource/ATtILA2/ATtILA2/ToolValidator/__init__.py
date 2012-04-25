""" The ToolValidator classes is for ArcToolbox script tool dialog validation.
    
"""

import BaseValidators
from ATtILA2.constants import metricConstants
import pylet.lcc.constants as lccConstants
from ATtILA2.constants.metricConstants import lcospConstants, lcpConstants

class lcospToolValidator(BaseValidators.ProportionsValidator):
    """Tool Validator for LandCoverSlopeOverlap"""
    
    filterList = lcospConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeLcsoField
    fieldPrefix = lcospConstants.fieldPrefix
    fieldSuffix = lcospConstants.fieldSuffix
    
    
class lcpToolValidator(BaseValidators.ProportionsValidator):
    """ ToolValidator for LandCoverProportions """
    
    filterList = lcpConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeLcsoField
    fieldPrefix = lcpConstants.fieldPrefix
    fieldSuffix = lcpConstants.fieldSuffix     

class lcccToolValidator(BaseValidators.CoefficientValidator):
    """ ToolValidator for Coefficient Calculations """