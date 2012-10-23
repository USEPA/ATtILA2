""" The ToolValidator classes is for ArcToolbox script tool dialog validation.
    
"""

import BaseValidators
from ATtILA2.constants import metricConstants
import pylet.lcc.constants as lccConstants
from ATtILA2.constants.metricConstants import *

class lcospToolValidator(BaseValidators.ProportionsValidator):
    """Tool Validator for LandCoverSlopeOverlap"""
    
    filterList = lcospConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeLcospField
    fieldPrefix = lcospConstants.fieldPrefix
    fieldSuffix = lcospConstants.fieldSuffix
    metricShortName = lcospConstants.shortName
    
    
class lcpToolValidator(BaseValidators.ProportionsValidator):
    """ ToolValidator for LandCoverProportions """
    
    filterList = lcpConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeLcpField
    fieldPrefix = lcpConstants.fieldPrefix
    fieldSuffix = lcpConstants.fieldSuffix    
    metricShortName = lcpConstants.shortName 

class lcccToolValidator(BaseValidators.CoefficientValidator):
    """ ToolValidator for Coefficient Calculations """
    
    filterList = lcccConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeLcpField
    fieldPrefix = lcccConstants.fieldPrefix
    fieldSuffix = lcccConstants.fieldSuffix    
    metricShortName = lcccConstants.shortName 
    
class rlcpToolValidator(BaseValidators.ProportionsValidator):
    """ ToolValidator for RiparianLandCoverProportions"""
    
    filterList = rlcpConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeRlcpField
    fieldPrefix = rlcpConstants.fieldPrefix
    fieldSuffix = rlcpConstants.fieldSuffix
    metricShortName = rlcpConstants.shortName
    
class splcpToolValidator(BaseValidators.ProportionsValidator):
    """ ToolValidator for RiparianLandCoverProportions"""
    
    filterList = splcpConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeSplcpField
    fieldPrefix = splcpConstants.fieldPrefix
    fieldSuffix = splcpConstants.fieldSuffix
    metricShortName = splcpConstants.shortName
    