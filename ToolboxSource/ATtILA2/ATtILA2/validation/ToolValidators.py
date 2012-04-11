

""" The ToolValidator classes is for ArcToolbox script tool dialog validation.
    
"""

from ATtILA2.validation.Validators import ProportionsValidator
from ATtILA2.metrics import constants as metricConstants
import pylet.lcc.constants as lccConstants
import ATtILA2.metrics.fields as outFields


class lcsoToolValidator(ProportionsValidator):
    """Tool Validator for LandCoverSlopeOverlap"""
    
    filterList = metricConstants.lcsoOptionalFilter
    overrideAttributeName = lccConstants.XmlAttributeLcsoField
    fieldPrefix = outFields.lcsoFieldPrefix
    fieldSuffix = outFields.lcsoFieldSuffix
    
    
class lcpToolValidator(ProportionsValidator):
    """ ToolValidator for LandCoverProportions """
    
    filterList = metricConstants.lcpOptionalFilter
    overrideAttributeName = lccConstants.XmlAttributeLcsoField
    fieldPrefix = outFields.lcpFieldPrefix
    fieldSuffix = outFields.lcpFieldSuffix     

