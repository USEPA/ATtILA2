import globalConstants as gc


class baseMetricConstants():
    """  """
    name = ''
    shortName = ''
    fieldPrefix = ''
    fieldSuffix = ''
    overlapName = ''
    totalAreaName = ''
    effectiveAreaName = ''
    excludedAreaName = ''
    optionalFilter = []
    fieldParameters = []
    qaCheckFieldParameters = []    
    fieldOverrideKey = ''

class lcpConstants(baseMetricConstants):
    name = "LandCoverProportions"
    shortName = "lcp"
    fieldPrefix = "p"
    fieldSuffix = ""
    overlapName = "LCP_OVRLP"
    totalAreaName = "LCP_TOT_A"
    effectiveAreaName = "LCP_EFF_A"
    excludedAreaName = "LCP_EXC_A"
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15]
        ]   
    fieldOverrideKey = shortName + gc.fieldOverrideName
    
class lcospConstants(baseMetricConstants):
    name = "LandCoverOnSlopeProportions"
    shortName = "lcosp"
    fieldSuffix = "SL"
    fieldPrefix = ""
    overlapName = "SL_OVRLP"
    totalAreaName = "SL_TOT_A"
    effectiveAreaName = "SL_EFF_A"
    excludedAreaName = "SL_EXC_A"
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType,6,1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15]
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName

class lcccConstants(baseMetricConstants):
    name = "LandCoverCoefficientCalculator"
    shortName = "lccc"
    fieldPrefix = ""
    fieldSuffix = ""
    overlapName = "LCCC_OVRLP"
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.qaCheckDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultDecimalFieldType, 7, 2]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6]
        ]    
    fieldOverrideKey = shortName + gc.fieldOverrideName
    perUnitAreaMetrics = ("NITROGEN", "PHOSPHORUS")
    percentageMetrics = ("IMPERVIOUS")
    

class rlcpConstants(baseMetricConstants):
    name = "RiparianLandCoverProportions"
    shortName = "rlcp"
    fieldPrefix = "r"
    fieldSuffix = ""
    overlapName = "R_OVERLAP"
    totalAreaName = "RLCP_TOT_A"
    effectiveAreaName = "RLCP_EFF_A"
    excludedAreaName = "RLCP_EXC_A"
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15]                                        
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName

class splcpConstants(baseMetricConstants):
    name = "SamplePointLandCoverProportions"
    shortName = "splcp"
    fieldPrefix = "s"
    fieldSuffix = ""
    overlapName = "SP_OVERLAP"
    totalAreaName = "SPLCP_TOTA"
    effectiveAreaName = "SPLCP_EFFA"
    excludedAreaName = "SPLCP_EXCA"
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15]                                        
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName
    
class caeamConstants(baseMetricConstants):
    name = "CoreAndEdgeAreaMetrics"
    shortName = "caeam"
    fieldPrefix = "e"
    fieldSuffix = ""
    overlapName = "CE_OVERLAP"
    totalAreaName = "CAEAM_TOT_A"
    effectiveAreaName = "CAEAM_EFF_A"
    excludedAreaName = "CAEAM_EXC_A"
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15]                                        
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName


