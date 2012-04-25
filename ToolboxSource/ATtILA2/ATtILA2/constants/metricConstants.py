import sys
import applicationConstants as ac
import ATtILA2

class lcpConstants():
    name = "LandCoverProportions"
    shortName = "lcp"
    fieldPrefix = "p"
    fieldSuffix = ""
    overlapName = "LCP_OVRLP"
    totalAreaName = "LCP_TOT_A"
    effectiveAreaName = "LCP_EFF_A"
    excludedAreaName = "LCP_EXC_A"
    optionalFilter = [ac.qaCheckDescription, ac.metricAddDescription]
    fieldParameters = [fieldPrefix,"", ac.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, ac.defaultIntegerFieldType, 6],
        [totalAreaName, ac.defaultAreaFieldType, 15],
        [effectiveAreaName, ac.defaultAreaFieldType, 15],
        [excludedAreaName, ac.defaultAreaFieldType, 15]
        ],    
    fieldOverrideKey = shortName + ac.fieldOverrideName
    
class lcospConstants():
    name = "LandCoverOnSlopeProportions"
    shortName = "lcosp"
    fieldSuffix = "SL"
    fieldPrefix = ""
    overlapName = "SL_OVRLP"
    totalAreaName = "SL+TOT_A"
    effectiveAreaName = "SL_EFF_A"
    excludedAreaName = "SL_EXC_A"
    optionalFilter = [ac.qaCheckDescription, ac.metricAddDescription, ac.intermediateDescription]
    fieldParameters = [fieldSuffix, ac.defaultDecimalFieldType,6,1]
    qaCheckFieldParameters = [
        [overlapName, ac.defaultIntegerFieldType, 6],
        [totalAreaName, ac.defaultAreaFieldType, 15],
        [effectiveAreaName, ac.defaultAreaFieldType, 15],
        [excludedAreaName, ac.defaultAreaFieldType, 15]
        ]
    fieldOverrideKey = shortName + ac.fieldOverrideName

    
class rpConstants():
    name = "RiparianProportions"
    shortName = "rp"
    fieldPrefix = "r"
    fieldSuffix = ""
    overlapName = "R_OVERLAP"
    optionalFilter = [ac.qaCheckDescription, ac.metricAddDescription]
    fieldParameters = [fieldPrefix,"", ac.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, ac.defaultIntegerFieldType, 6]                                        
        ]
    fieldOverrideKey = shortName + ac.fieldOverrideName



