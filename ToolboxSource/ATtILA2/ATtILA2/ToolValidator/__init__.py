""" The ToolValidator classes is for ArcToolbox script tool dialog validation.
    
"""

import BaseValidators
from ATtILA2.constants import metricConstants
import pylet.lcc.constants as lccConstants
from ATtILA2.constants import fieldConstants


class lcsoToolValidator(BaseValidators.ProportionsValidator):
    """Tool Validator for LandCoverSlopeOverlap"""
    
    filterList = metricConstants.lcsoOptionalFilter
    overrideAttributeName = lccConstants.XmlAttributeLcsoField
    fieldPrefix = fieldConstants.lcsoFieldPrefix
    fieldSuffix = fieldConstants.lcsoFieldSuffix
    
    
class lcpToolValidator(BaseValidators.ProportionsValidator):
    """ ToolValidator for LandCoverProportions """
    
    filterList = metricConstants.lcpOptionalFilter
    overrideAttributeName = lccConstants.XmlAttributeLcsoField
    fieldPrefix = fieldConstants.lcpFieldPrefix
    fieldSuffix = fieldConstants.lcpFieldSuffix     

class lcccToolValidator(BaseValidators.CoefficientValidator):
    """ ToolValidator for Coefficient Calculations """