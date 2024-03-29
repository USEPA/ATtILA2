from . import globalConstants as gc

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
    additionalFields = []
    pctBufferName = ''

class caemConstants(baseMetricConstants):
    name = "CoreAndEdgeMetrics"
    shortName = "caem"
    fieldPrefix = ""
    fieldSuffix = "_E2A"
    overlapName = "CAEM_OVER"
    totalAreaName = "CAEM_TOTA"
    effectiveAreaName = "CAEM_EFFA"
    excludedAreaName = "CAEM_EXCA"
    optionalFilter = [gc.qaCheckDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15]                                        
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName
    coreSuffix = "_COR"
    edgeSuffix = "_EDG"
    additionalSuffixes = [coreSuffix, edgeSuffix]
    coreField = ["", coreSuffix, gc.defaultDecimalFieldType, 6, 1]
    edgeField = ["", edgeSuffix, gc.defaultDecimalFieldType, 6, 1]
    additionalFields = [coreField, edgeField]

class flcpConstants(baseMetricConstants):
    name = "FloodplainLandCoverProportions"
    shortName = "flcp"
    fieldSuffix = ""
    fieldPrefix = "f"
    overlapName = "FLCP_OVER"
    totalAreaName = "FLCP_TOTA"
    effectiveAreaName = "FLCP_EFFA"
    excludedAreaName = "FLCP_EXCA"
    pctBufferSuffix = ""
    pctBufferBase = "%sEFFA" % fieldPrefix
    pctBufferName = "%s%s" % (pctBufferBase, pctBufferSuffix)
    totaPctSuffix = ""
    totaPctBase = "%sTOTA" % fieldPrefix
    totaPctName = "%s%s" % (totaPctBase, totaPctSuffix)
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15],
        [totaPctName, gc.defaultDecimalFieldType, 6, 1],
        [pctBufferName, gc.defaultDecimalFieldType, 6, 1]
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName
    fpTabAreaName = shortName+"_TabAreaFP"
    landcoverGridName = shortName+"_Landcover"
    zoneByRUName = shortName+"_FldplnByRU"
    
class flcvConstants(baseMetricConstants):
    name = "FacilityLandCoverViews"
    shortName = "flcv"
    fieldSuffix = "_Low"
    fieldPrefix = ""
    overlapName = "FLCV_OVER"
    totalAreaName = "FLCV_TOTA"
    effectiveAreaName = "FLCV_EFFA"
    excludedAreaName = "FLCV_EXCA"
    optionalFilter = [gc.intermediateDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15]
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName
    lcpFieldSuffix = ""
    lcpFieldPrefix = "p"
    lcpFieldParameters = [lcpFieldPrefix, lcpFieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    belowFieldSuffix = "_Below"
    aboveFieldSuffix = "_Above"
    facilityCopyName = shortName+"_Facility"
    facilityWithRUIDName = shortName+"_FacilityRUID"
    viewBufferName = shortName+"_ViewBuffer"
    lcpTableName = shortName+"_ViewLCP"
    lcpTableWithRUID = shortName+"_ViewLCP_RUID"
    statsResultTable = shortName+"_ViewStats"
    facilityCountFieldName = "FAC_Count"
    facilityCountField = [facilityCountFieldName,"LONG",None, 10]
    singleFields = [facilityCountField]
    highSuffix = "_High"
    additionalSuffixes = [highSuffix]
    highField = ["", highSuffix, gc.defaultDecimalFieldType, 6, 1]
    additionalFields = [highField]
    
class idConstants(baseMetricConstants):
    name = "IntersectionDensity"
    shortName = "id"
    fieldPrefix = ""
    fieldSuffix = "IntDen"
    overlapName = ""
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.intermediateDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultDecimalFieldType, 6, 1] 
    fieldOverrideKey = ""
    prjRoadName = "Prj"
    intersectDensityGridName = shortName+"_IntDen"
    mergedRoadName = "Merged"
    unsplitRoadName = "UnSplit"
    roadIntersectName = "Intersections"
    gidrRoadLayer = shortName+"_Road"
    singlepartRoadName = "SglPrt"
    dummyFieldName = shortName+"_dummy"    

class lcccConstants(baseMetricConstants):
    name = "LandCoverCoefficientCalculator"
    shortName = "lccc"
    fieldPrefix = ""
    fieldSuffix = ""
    overlapName = "LCCC_OVER"
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.qaCheckDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultDecimalFieldType, 7, 2]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6]
        ]    
    # Output field names are fixed. Field name override option is not available to the user.   
    fieldOverrideKey = ""
    perUnitAreaMetrics = ("NITROGEN", "PHOSPHORUS")
    percentageMetrics = ("IMPERVIOUS")

class lcdConstants(baseMetricConstants):
    name = "LandCoverDiversity"
    shortName = "lcd"
    fieldPrefix = ""
    fieldSuffix = ""
    overlapName = "LCD_OVER"
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.qaCheckDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultDecimalFieldType, 8, 4]
    qaCheckFieldParameters = [
                              [overlapName, gc.defaultIntegerFieldType, 6]
                              ]
    # Output field names are fixed. Field name override option is not available to the user.
    fieldOverrideKey = ""
    fixedMetricsToRun = 'H  -  Shannon Weiner;H_Prime  -  Standardized Shannon Weiner;C  -  Simpson;S  -  Simple'

class lcospConstants(baseMetricConstants):
    name = "LandCoverOnSlopeProportions"
    shortName = "lcosp"
    fieldSuffix = "_SL"
    fieldPrefix = ""
    overlapName = "LCOSP_OVER"
    totalAreaName = "LCOSP_TOTA"
    effectiveAreaName = "LCOSP_EFFA"
    excludedAreaName = "LCOSP_EXCA"
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType,6,1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15]
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName

class lcpORIGINALConstants(baseMetricConstants):
    name = "LandCoverProportions"
    shortName = "lcp"
    fieldPrefix = "p"
    fieldSuffix = ""
    overlapName = "LCP_OVER"
    totalAreaName = "LCP_TOTA"
    effectiveAreaName = "LCP_EFFA"
    excludedAreaName = "LCP_EXCA"
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15]
        ]   
    fieldOverrideKey = shortName + gc.fieldOverrideName
    
class lcpConstants(baseMetricConstants):
    name = "LandCoverProportions"
    shortName = "lcp"
    fieldPrefix = "p"
    fieldSuffix = ""
    overlapName = shortName+"_OVER"
    totalAreaName = shortName+"_TOTA"
    effectiveAreaName = shortName+"_EFFA"
    excludedAreaName = shortName+"_EXCA"
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15]
        ]   
    fieldOverrideKey = shortName + gc.fieldOverrideName
    perCapitaSuffix = "_PC"
    meterSquaredSuffix = "_M2"
    additionalSuffixes = [perCapitaSuffix, meterSquaredSuffix]
    perCapitaField = ["", perCapitaSuffix, "LONG", 10, 0]
    meterSquaredField = ["", meterSquaredSuffix, gc.defaultAreaFieldType, 15, 0]
    additionalFields = [perCapitaField, meterSquaredField]
    valueCountFieldNames =["RU_POP_C"]
    valueCountTableName = shortName+"_populationCnt"   

class npConstants(baseMetricConstants):
    name = "NeighborhoodProportions"
    shortName = "np"
    fieldPrefix = ""
    fieldSuffix = "_Prox"
    overlapName = ""
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.intermediateDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultDecimalFieldType, 6, 1] 
    fieldOverrideKey = ""
    burnInGridName = "BurnIn"
    proxPolygonOutputName = "_ProxPoly"
    proxZoneRaserOutName = "_Zone"
    proxRasterOutName = "_Prox"
    proxFocalSumOutName = "_Cnt"
    
class nrlcpConstants(baseMetricConstants):
    name = "NearRoadLandCoverProportions"
    shortName = "nrlcp"
    optionalFilter = [gc.intermediateDescription]    
    
class pdmConstants(baseMetricConstants):
    name = "PopulationDensityMetrics"
    shortName = "pdm"
    fieldPrefix = ""
    fieldSuffix = ""
    overlapName = ""
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.intermediateDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = []
    fieldOverrideKey = ""
    areaFieldname = "AREAKM2"
    populationDensityFieldName = "POPDENS"
    populationChangeFieldName = "POPCHG"
    intersectOutputName = shortName+"_intersectOutput"
    summaryTableName = shortName+"_summaryTable"
    
class pifmConstants(baseMetricConstants):
    name = "PopulationInFloodplainMetrics"
    shortName = "pifm"
    fieldPrefix = ["RU_", "FP_"]
    fieldSuffix = ["_RU", "_FP"]
    overlapName = ""
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.intermediateDescription]
    fieldParameters = ["", "", gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = []
    fieldOverrideKey = ""
    populationProportionFieldName = "FP_POP_P"
    # populationCountFieldNames = ["RU_POP_C", "FP_POP_C"]
    populationCountFieldNames = ["RU_POP", "FP_POP_C"]
    popCntTableName = shortName+"_populationCnt"
    floodplainPopName = shortName+"_populationFP"

class pmConstants(baseMetricConstants):
    name = "PatchMetrics"
    shortName = "pm"
    fieldPrefix = ""
    fieldSuffix = "_PLGP"
    overlapName = "PM_OVER"
    totalAreaName = "PM_TOTA"
    effectiveAreaName = "PM_EFFA"
    excludedAreaName = "PM_EXCA"
    optionalFilter = [gc.qaCheckDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15]                                        
        ]
    # This metric is comprised of several output fields. Fieldname override option 
    # is not available to the user
    fieldOverrideKey = ""
    numSuffix = "_NUM"
    avgSuffix = "_AVG"
    densSuffix = "_DENS"
    lrgSuffix = "_LRG"
    mdcpSuffix = "_MDCP"
    additionalSuffixes = [numSuffix, avgSuffix, densSuffix, lrgSuffix, mdcpSuffix]
    numField = ["", numSuffix, gc.defaultIntegerFieldType, 6, 0]
    avgField = ["", avgSuffix, gc.defaultAreaFieldType, 15, 1]
    densField = ["", densSuffix, gc.defaultDecimalFieldType, 10, 1]
    lrgField = ["", lrgSuffix, gc.defaultAreaFieldType, 15, 1]
    mdcpField = ["", mdcpSuffix, gc.defaultDecimalFieldType, 10, 1]
    additionalFields = [numField, avgField, densField, lrgField]
    mdcpFields = [mdcpField]
    rastertoPoly = "PatchPoly"
    rastertoPoint = "PatchCentroids"
    polyDissolve = "PatchPoly_Diss"
    nearTable = "_NearTable"
    classValue = 3
    excludedValue = -9999
    otherValue = 0
    
class plcvConstants(baseMetricConstants):
    name = "PopulationLandCoverViews"
    shortName = "plcv"
    fieldPrefix = ""
    mvFieldPrefix = ""
    fieldSuffix = "_PV_C"
    wovFieldSuffix = "_MV_C"
    overlapName = ""
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.intermediateDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = []
    # This metric is comprised of several output fields. Fieldname override option 
    # is not available to the user  
    fieldOverrideKey = ""
    pctSuffix = "_PV_P"
    wovPctSuffix = "_MV_P"
    additionalSuffixes = [pctSuffix]
    cntField = [fieldPrefix, pctSuffix, "LONG", 10, 0]
    additionalFields = [cntField]
    valueCountFieldNames =["RU_POP"]
    valueCountTableName = shortName+"_populationCnt"
    viewRasterOutputName = "_ViewArea"
    viewPolygonOutputName = "_ViewAreaPoly"
    areaPopRasterOutputName = "_ViewPopulation"
    areaValueCountTableName = "_ViewPopulationByRU"
    valueWhenNULL = 0
    patchGridName = "_ViewPatch"
    
class pnfeaConstants(baseMetricConstants):
    #prefix = "NAVTEQ"
    prefix = ""
    outNameRoadsWalkable = prefix+"_RdsWalkable"
    outNameRoadsIntDens = prefix+"_RdsIntDens"
    outNameRoadsIAC = prefix+"_RdsIAC"
    value0_LANES = prefix + "_RdsIAC_0Lanes"
    
class pnhd24kConstants(baseMetricConstants):
    prefix = ""

class rlcpConstants(baseMetricConstants):
    name = "RiparianLandCoverProportions"
    shortName = "rlcp"
    fieldPrefix = "r"
    fieldSuffix = ""
    overlapName = "RLCP_OVER"
    totalAreaName = "RLCP_TOTA"
    effectiveAreaName = "RLCP_EFFA"
    excludedAreaName = "RLCP_EXCA"
    pctBufferSuffix = ""
    pctBufferBase = "%sEFFA" % fieldPrefix
    pctBufferName = "%s%s" % (pctBufferBase, pctBufferSuffix)
    totaPctSuffix = ""
    totaPctBase = "%sTOTA" % fieldPrefix
    totaPctName = "%s%s" % (totaPctBase, totaPctSuffix)
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15],
        [totaPctName, gc.defaultDecimalFieldType, 6, 1],
        [pctBufferName, gc.defaultDecimalFieldType, 6, 1]                                        
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName
    
class rdmConstants(baseMetricConstants):
    name = "RoadDensityMetrics"
    shortName = "rdm"
    fieldPrefix = ""
    fieldSuffix = ""
    overlapName = ""
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.intermediateDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = []
    fieldOverrideKey = ""
    areaFieldname = "AREAKM2"
    roadDensityFieldName = "RDDENS"
    roadLengthFieldName = "RDKM"
    streamDensityFieldName = "STRMDENS"
    streamLengthFieldName = "STRMKM"
    totalImperviousAreaFieldName = "RDTIA"
    streamRoadXingsCountFieldname = "XCNT"
    xingsPerKMFieldName = "STXRD"
    rnsFieldName = "RNS"
    roadsByReportingUnitName = [shortName+"_RdsByRU","FeatureClass"]
    streamsByReportingUnitName = [shortName+"_StrByRU","FeatureClass"]
    roadStreamMultiPoints = [shortName+"_RdsXStrMP","FeatureClass"]
    roadStreamIntersects = [shortName+"_PtsOfXing","FeatureClass"]
    roadStreamSummary = [shortName+"_RdsXStrTbl","Dataset"]
    streamBuffers = [shortName+"_StrBuffers","FeatureClass"]
    roadsNearStreams = [shortName+"_RdsNrStrms","FeatureClass"]
    tmp1RNS = [shortName+"_TmpRdsInBuffer","FeatureClass"]
    tmp2RNS = [shortName+"_TmpRdsWithRUID","FeatureClass"]

class sdmConstants(baseMetricConstants):
    name = "StreamDensityMetric"
    shortName = "sdm"
    fieldPrefix = ""
    fieldSuffix = ""
    overlapName = ""
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.intermediateDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = []
    fieldOverrideKey = ""
    areaFieldname = "AREAKM2"
    lineLengthFieldName = "STRMKM"
    lineDensityFieldName = "STRMDENS"
    linesByReportingUnitName = [shortName+"_StrByRU","FeatureClass"]

class splcpConstants(baseMetricConstants):
    name = "SamplePointLandCoverProportions"
    shortName = "splcp"
    fieldPrefix = "s"
    fieldSuffix = ""
    overlapName = "SPLCP_OVER"
    totalAreaName = "SPLCP_TOTA"
    effectiveAreaName = "SPLCP_EFFA"
    excludedAreaName = "SPLCP_EXCA"
    pctBufferSuffix = ""
    pctBufferBase = "%sEFFA" % fieldPrefix
    pctBufferName = "%s%s" % (pctBufferBase, pctBufferSuffix)
    totaPctSuffix = ""
    totaPctBase = "%sTOTA" % fieldPrefix
    totaPctName = "%s%s" % (totaPctBase, totaPctSuffix)
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15],
        [totaPctName, gc.defaultDecimalFieldType, 6, 1],
        [pctBufferName, gc.defaultDecimalFieldType, 6, 1]                                        
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName

    
