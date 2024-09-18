""" The ToolValidator classes is for ArcToolbox script tool dialog validation.

        1) ProportionsValidator Tools
        2) CoefficientValidator Tools
        3) NoLccFileValidator Tools
        4) NoReportingUnitValidator Tools       
    
"""

from . import BaseValidators
from ATtILA2.constants import metricConstants
from  ATtILA2.utils.lcc import constants as lccConstants
from ATtILA2.constants.metricConstants import *


'''ProportionsValidator Tools'''

class caemToolValidator(BaseValidators.ProportionsValidator):
    """ ToolValidator for CoreAndEdgeMetrics """
    
    filterList = caemConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeCaemField
    fieldPrefix = caemConstants.fieldPrefix
    fieldSuffix = caemConstants.fieldSuffix    
    metricShortName = caemConstants.shortName
    spatialNeeded = caemConstants.spatialNeeded

class flcpToolValidator(BaseValidators.ProportionsValidator):
    """ToolValidator for FloodplainLandCoverProportion"""
      
    filterList = flcpConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeFlcpField
    fieldPrefix = flcpConstants.fieldPrefix
    fieldSuffix = flcpConstants.fieldSuffix
    metricShortName = flcpConstants.shortName 
    spatialNeeded = flcpConstants.spatialNeeded
    
class flcvToolValidator(BaseValidators.ProportionsValidator):
    """ToolValidator for Facility Land Cover Views"""
      
    filterList = flcvConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeFlcvField
    fieldPrefix = flcvConstants.fieldPrefix
    fieldSuffix = flcvConstants.fieldSuffix
    metricShortName = flcvConstants.shortName 
    spatialNeeded = flcvConstants.spatialNeeded
    
class lcospToolValidator(BaseValidators.ProportionsValidator):
    """ToolValidator for LandCoverSlopeOverlap"""
    
    filterList = lcospConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeLcospField
    fieldPrefix = lcospConstants.fieldPrefix
    fieldSuffix = lcospConstants.fieldSuffix
    metricShortName = lcospConstants.shortName
    spatialNeeded = lcospConstants.spatialNeeded
    
class lcpORIGINALToolValidator(BaseValidators.ProportionsValidator):
    """ ToolValidator for LandCoverProportions """
    
    filterList = lcpConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeLcpField
    fieldPrefix = lcpConstants.fieldPrefix
    fieldSuffix = lcpConstants.fieldSuffix    
    metricShortName = lcpConstants.shortName 
    spatialNeeded = lcpConstants.spatialNeeded
    
class lcpToolValidator(BaseValidators.ProportionsValidator):
    """ ToolValidator for LandCoverProportions """
    
    filterList = lcpConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeLcpField
    fieldPrefix = lcpConstants.fieldPrefix
    fieldSuffix = lcpConstants.fieldSuffix    
    metricShortName = lcpConstants.shortName 
    spatialNeeded = lcpConstants.spatialNeeded

class pmToolValidator(BaseValidators.ProportionsValidator):
    """ ToolValidator for PatchMetrics """
    
    filterList = pmConstants.optionalFilter
#    overrideAttributeName = lccConstants.XmlAttributePmField
    fieldPrefix = pmConstants.fieldPrefix
    fieldSuffix = pmConstants.fieldSuffix
    metricShortName = pmConstants.shortName
    spatialNeeded = pmConstants.spatialNeeded
    
class plcvToolValidator(BaseValidators.ProportionsValidator):
    filterList = plcvConstants.optionalFilter
#    overrideAttributeName = pwpvConstants.XmlAttributePwpvField
    fieldPrefix = plcvConstants.fieldPrefix
    fieldSuffix = plcvConstants.fieldSuffix    
    metricShortName = plcvConstants.shortName
    spatialNeeded = plcvConstants.spatialNeeded

class rlcpToolValidator(BaseValidators.ProportionsValidator):
    """ ToolValidator for RiparianLandCoverProportions"""
    
    filterList = rlcpConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeRlcpField
    fieldPrefix = rlcpConstants.fieldPrefix
    fieldSuffix = rlcpConstants.fieldSuffix
    metricShortName = rlcpConstants.shortName
    spatialNeeded = rlcpConstants.spatialNeeded
    
class splcpToolValidator(BaseValidators.ProportionsValidator):
    """ ToolValidator for SamplePointLandCoverProportions"""
    
    filterList = splcpConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeSplcpField
    fieldPrefix = splcpConstants.fieldPrefix
    fieldSuffix = splcpConstants.fieldSuffix
    metricShortName = splcpConstants.shortName
    spatialNeeded = splcpConstants.spatialNeeded



'''CoefficientValidator Tools'''
        
class lcccToolValidator(BaseValidators.CoefficientValidator):
    """ ToolValidator for Coefficient Calculations """
    filterList = lcccConstants.optionalFilter
    overrideAttributeName = lccConstants.XmlAttributeLcpField
    fieldPrefix = lcccConstants.fieldPrefix
    fieldSuffix = lcccConstants.fieldSuffix    
    metricShortName = lcccConstants.shortName  
    spatialNeeded = lcccConstants.spatialNeeded

    

'''NoLccFileValidator Tools'''
    
class lcdToolValidator(BaseValidators.NoLccFileValidator):
    """ ToolValidator for LandCoverDiversity """
    
    filterList = lcdConstants.optionalFilter
    fieldPrefix = lcdConstants.fieldPrefix
    fieldSuffix = lcdConstants.fieldSuffix
    metricShortName = lcdConstants.shortName
    spatialNeeded = lcdConstants.spatialNeeded

class paaaToolValidator(BaseValidators.NoLccFileValidator):
    """ ToolValidator for Pedestrian Access Metrics """
    
    filterList = paaaConstants.optionalFilter
    metricShortName = paaaConstants.shortName
    spatialNeeded = paaaConstants.spatialNeeded
   
    
class pdmToolValidator(BaseValidators.NoLccFileValidator):
    """ ToolValidator for PopulationDensityMetrics """
    
    filterList = pdmConstants.optionalFilter
    fieldPrefix = pdmConstants.fieldPrefix
    fieldSuffix = pdmConstants.fieldSuffix
    metricShortName = pdmConstants.shortName
    spatialNeeded = pdmConstants.spatialNeeded
    
class pifmToolValidator(BaseValidators.NoLccFileValidator):
    """ ToolValidator for PopulationInFloodplainMetrics """
    
    filterList = pifmConstants.optionalFilter
    fieldPrefix = pifmConstants.fieldPrefix
    fieldSuffix = pdmConstants.fieldSuffix
    metricShortName = pifmConstants.shortName
    spatialNeeded = pifmConstants.spatialNeeded

class pwzmToolValidator(BaseValidators.NoLccFileValidator):
    """ ToolValidator for PopulationWithinZones """
    
    filterList = pwzmConstants.optionalFilter
    fieldPrefix = pwzmConstants.fieldPrefix
    fieldSuffix = pwzmConstants.fieldSuffix
    metricShortName = pwzmConstants.shortName
    spatialNeeded = pwzmConstants.spatialNeeded
    
class rdmToolValidator(BaseValidators.NoLccFileValidator):
    """ ToolValidator for RoadDensityMetrics """
    
    filterList = rdmConstants.optionalFilter
    fieldPrefix = rdmConstants.fieldPrefix
    fieldSuffix = rdmConstants.fieldSuffix    
    metricShortName = rdmConstants.shortName 
    spatialNeeded = rdmConstants.spatialNeeded



'''NoReportingUnitValidator Tools'''    

class idToolValidator(BaseValidators.NoReportingUnitValidator):
    """ ToolValidator for GenerateIntersectionDensityRaster Utility """
    
    filterList = idConstants.optionalFilter
    metricShortName = idConstants.shortName
    spatialNeeded = idConstants.spatialNeeded
    
# class idoToolValidator(BaseValidators.NoReportingUnitValidator):
#     """ ToolValidator for GenerateIntersectionDensityRaster Utility """
#
#     filterList = idConstants.optionalFilter
#     metricShortName = idConstants.shortName

class npToolValidator(BaseValidators.NoReportingUnitValidator):
    """ ToolValidator for Neighborhood Proportions """
    
    filterList = npConstants.optionalFilter
    fieldSuffix = npConstants.fieldSuffix
    metricShortName = npConstants.shortName
    spatialNeeded = npConstants.spatialNeeded
    
class nrlcpToolValidator(BaseValidators.NoReportingUnitValidator):
    """ ToolValidator for Near Road Land Cover Proportions """
    
    filterList = nrlcpConstants.optionalFilter
    metricShortName = nrlcpConstants.shortName
    spatialNeeded = nrlcpConstants.spatialNeeded


