from . import globalConstants as gc

class baseMetricConstants():
    """  """
    name = ''
    shortName = ''
    toolFUNC = ''
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
    parameterLabels = []
    spatialNeeded = True
    scriptOpening = gc.metricScriptOpening
    idFields = gc.idFields
    
class caemConstants(baseMetricConstants):
    name = "CoreAndEdgeMetrics"
    shortName = "caem"
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
    fieldPrefix = ""
    fieldSuffix = "_E2A"
    overlapName = "CAEM_OVER"
    totalAreaName = "CAEM_TOTA"
    effectiveAreaName = "CAEM_EFFA"
    excludedAreaName = "CAEM_EXCA"
    optionalFilter = [gc.qaCheckDescription, gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultPercentFieldType, 6, 1]
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
    coreField = ["", coreSuffix, gc.defaultPercentFieldType, 6, 1]
    edgeField = ["", edgeSuffix, gc.defaultPercentFieldType, 6, 1]
    additionalFields = [coreField, edgeField]
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inLandCoverGrid, 
        gc._lccName, 
        gc.lccFilePath, 
        gc.metricsToRun,
        gc.inEdgeWidth, 
        gc.outTable, 
        gc.processingCellSize, 
        gc.snapRaster, 
        gc.optionalFieldGroups, 
        gc.clipLCGrid
        ]

class cwcrConstants(baseMetricConstants):
    name = "CreateWalkabilityCostRaster"
    shortName = "cwcr"
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
    prefix = ""
    optionalFilter = [gc.intermediateDescription, gc.logDescription]
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inWalkFeatures, 
        gc.inImpassableFeatures, 
        gc.maxTravelDist, 
        gc.walkValue, 
        gc.baseValue,
        gc.outRaster, 
        gc.cellSize, 
        gc.snapRaster, 
        gc.optionalFieldGroups
        ]

class flcpConstants(baseMetricConstants):
    name = "FloodplainLandCoverProportions"
    shortName = "flcp"
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
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
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultPercentFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15],
        [totaPctName, gc.defaultPercentFieldType, 6, 1],
        [pctBufferName, gc.defaultPercentFieldType, 6, 1]
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName
    fpTabAreaName = f"{shortName}_TabAreaFP_"
    landcoverGridName = f"{shortName}_Landcover_"
    zoneByRUName = f"{shortName}_FldplnByRU_"
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inLandCoverGrid, 
        gc._lccName, 
        gc.lccFilePath,
        gc.metricsToRun, 
        gc.inFloodplainGeodataset, 
        gc.outTable, 
        gc.processingCellSize, 
        gc.snapRaster, 
        gc.optionalFieldGroups, 
        gc.clipLCGrid
        ]
    
class flcvConstants(baseMetricConstants):
    name = "FacilityLandCoverViews"
    shortName = "flcv"
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
    fieldSuffix = "_Low"
    fieldPrefix = ""
    overlapName = "FLCV_OVER"
    totalAreaName = "FLCV_TOTA"
    effectiveAreaName = "FLCV_EFFA"
    excludedAreaName = "FLCV_EXCA"
    optionalFilter = [gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultPercentFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15]
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName
    lcpFieldSuffix = ""
    lcpFieldPrefix = "p"
    lcpFieldParameters = [lcpFieldPrefix, lcpFieldSuffix, gc.defaultPercentFieldType, 6, 1]
    belowFieldSuffix = "_Below"
    aboveFieldSuffix = "_Above"
    facilityCopyName = f"{shortName}_Facility"
    facilityWithRUIDName = f"{shortName}_FacilityRUID"
    viewBufferName = f"{shortName}_ViewBuffer"
    lcpTableName = f"{shortName}_ViewLCP"
    lcpTableWithRUID = f"{shortName}_ViewLCP_RUID"
    statsResultTable = f"{shortName}_ViewStats"
    facilityCountFieldName = "FAC_Count"
    facilityCountField = [facilityCountFieldName,"LONG",None, 10]
    singleFields = [facilityCountField]
    highSuffix = "_High"
    additionalSuffixes = [highSuffix]
    highField = ["", highSuffix, gc.defaultIntegerFieldType, 6, 0]
    additionalFields = [highField]
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inLandCoverGrid, 
        gc._lccName, 
        gc.lccFilePath,
        gc.metricsToRun, 
        gc.inFacilityFeature, 
        gc.viewRadius, 
        gc.viewThreshold, 
        gc.outTable, 
        gc.processingCellSize, 
        gc.snapRaster, 
        gc.optionalFieldGroups
        ]
    
class idConstants(baseMetricConstants):
    name = "IntersectionDensity"
    shortName = "id"
    toolFUNC = f'arcpy.ATtILA.{shortName.upper()}'
    scriptOpening = gc.basicScriptOpening
    fieldPrefix = ""
    fieldSuffix = "IntDen"
    overlapName = ""
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultPercentFieldType, 6, 1] 
    fieldOverrideKey = ""
    prjRoadName = "Prj"
    intersectDensityGridName = f"{shortName}_IntDen"
    mergedRoadName = "Merged"
    unsplitRoadName = "UnSplit"
    roadIntersectName = "Intersections"
    gidrRoadLayer = f"{shortName}_Road"
    singlepartRoadName = "SglPrt"
    dummyFieldName = f"{shortName}_dummy"
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inLineFeature, 
        gc.mergeLines, 
        gc.mergeField, 
        gc.mergeDistance, 
        gc.outputCS, 
        gc.cellSize, 
        gc.searchRadius, 
        gc.areaUnits, 
        gc.outRaster, 
        gc.optionalFieldGroups
        ]    

class lcccConstants(baseMetricConstants):
    name = "LandCoverCoefficientCalculator"
    shortName = "lccc"
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
    fieldPrefix = ""
    fieldSuffix = ""
    overlapName = "LCCC_OVER"
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.qaCheckDescription, gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultDecimalFieldType, 7, 2]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6]
        ]    
    # Output field names are fixed. Field name override option is not available to the user.   
    fieldOverrideKey = ""
    perUnitAreaMetrics = ("NITROGEN", "PHOSPHORUS")
    percentageMetrics = ("IMPERVIOUS")
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inLandCoverGrid, 
        gc._lccName,
        gc.lccFilePath, 
        gc.metricsToRun, 
        gc.outTable, 
        gc.processingCellSize, 
        gc.snapRaster,
        gc.optionalFieldGroups
        ]

class lcdConstants(baseMetricConstants):
    name = "LandCoverDiversity"
    shortName = "lcd"
    toolFUNC = f'arcpy.ATtILA.{shortName.upper()}'
    scriptOpening = gc.basicScriptOpening
    fieldPrefix = ""
    fieldSuffix = ""
    overlapName = "LCD_OVER"
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.qaCheckDescription, gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultDecimalFieldType, 8, 4]
    qaCheckFieldParameters = [
                              [overlapName, gc.defaultIntegerFieldType, 6]
                              ]
    # Output field names are fixed. Field name override option is not available to the user.
    fieldOverrideKey = ""
    fixedMetricsToRun = 'H  -  Shannon Weiner;H_Prime  -  Standardized Shannon Weiner;C  -  Simpson;S  -  Simple'
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inLandCoverGrid, 
        gc.outTable, 
        gc.processingCellSize, 
        gc.snapRaster, 
        gc.optionalFieldGroups
        ]

class lcospConstants(baseMetricConstants):
    name = "LandCoverOnSlopeProportions"
    shortName = "lcosp"
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
    fieldSuffix = "_SL"
    fieldPrefix = ""
    overlapName = "LCOSP_OVER"
    totalAreaName = "LCOSP_TOTA"
    effectiveAreaName = "LCOSP_EFFA"
    excludedAreaName = "LCOSP_EXCA"
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultPercentFieldType,6,1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15]
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inLandCoverGrid, 
        gc._lccName, 
        gc.lccFilePath,
        gc.metricsToRun, 
        gc.inSlopeGrid, 
        gc.inSlopeThresholdValue, 
        gc.outTable, 
        gc.processingCellSize,
        gc.snapRaster, 
        gc.optionalFieldGroups, 
        gc.clipLCGrid
        ]

class lcpORIGINALConstants(baseMetricConstants):
    name = "LandCoverProportions"
    shortName = "lcp"
    fieldPrefix = "p"
    fieldSuffix = ""
    overlapName = "LCP_OVER"
    totalAreaName = "LCP_TOTA"
    effectiveAreaName = "LCP_EFFA"
    excludedAreaName = "LCP_EXCA"
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription, gc.logDescription]
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
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
    fieldPrefix = "p"
    fieldSuffix = ""
    overlapName = f"{shortName.upper()}_OVER"
    totalAreaName = f"{shortName.upper()}_TOTA"
    effectiveAreaName = f"{shortName.upper()}_EFFA"
    excludedAreaName = f"{shortName.upper()}_EXCA"
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultPercentFieldType, 6, 1]
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
    valueCountTableName = f"{shortName}_populationCnt_"   
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inLandCoverGrid, 
        gc._lccName, 
        gc.lccFilePath,
        gc.metricsToRun, 
        gc.outTable, 
        gc.perCapitaYN, 
        gc.inCensusDataset, 
        gc.inPopField, 
        gc.processingCellSize, 
        gc.snapRaster, 
        gc.optionalFieldGroups
        ]

class npConstants(baseMetricConstants):
    name = "NeighborhoodProportions"
    shortName = "np"
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
    fieldPrefix = ""
    fieldSuffix = "_Prox"
    overlapName = ""
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultPercentFieldType, 6, 1] 
    fieldOverrideKey = ""
    burnInGridName = "BurnIn"
    proxPolygonOutputName = "_ProxPoly"
    proxZoneRaserOutName = "_Zone"
    proxRasterOutName = "_Prox"
    proxFocalSumOutName = "_Cnt"
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inLandCoverGrid, 
        gc._lccName, 
        gc.lccFilePath, 
        gc.metricsToRun, 
        gc.inNeighborhoodSize,
        gc.burnIn, 
        gc.burnInValue, 
        gc.minPatchSize, 
        gc.createZones, 
        gc.zoneBin_str, 
        gc.overWrite,
        gc.outWorkspace, 
        gc.optionalFieldGroups
        ]
    
class nrlcpConstants(baseMetricConstants):
    name = "NearRoadLandCoverProportions"
    shortName = "nrlcp"
    optionalFilter = [gc.intermediateDescription, gc.logDescription]    
    
class paaaConstants(baseMetricConstants):
    name = "PedestrianAccessAndAvailability"
    shortName = "paaa"
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
    optionalFilter = [gc.intermediateDescription, gc.logDescription]
    accessCountFieldName = "Pop_Access"
    accessCountField = [accessCountFieldName,gc.defaultDecimalFieldType,None, 15]
    countPerAreaFieldName = "SQM_Avail"
    countPerAreaField = [countPerAreaFieldName,gc.defaultDecimalFieldType,None,15]
    parkCalculationFields = [accessCountField, countPerAreaField]
    calcFieldNames = [accessCountFieldName, countPerAreaFieldName]
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inParkFeature, 
        gc.dissolveParkYN, 
        gc.inCostSurface, 
        gc.inCensusDataset, 
        gc.inPopField,
        gc.maxTravelDist, 
        gc.expandAreaDist,
        gc.outRaster,
        gc.processingCellSize, 
        gc.snapRaster, 
        gc.optionalFieldGroups
        ]
    
    
class pdmConstants(baseMetricConstants):
    name = "PopulationDensityMetrics"
    shortName = "pdm"
    toolFUNC = f'arcpy.ATtILA.{shortName.upper()}'
    scriptOpening = gc.basicScriptOpening
    fieldPrefix = ""
    fieldSuffix = ""
    overlapName = ""
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = []
    fieldOverrideKey = ""
    areaFieldname = "AREAKM2"
    populationDensityFieldName = "POPDENS"
    populationChangeFieldName = "POPCHG"
    intersectOutputName = f"{shortName}_intersectOutput"
    summaryTableName = f"{shortName}_summaryTable"
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inCensusFeature, 
        gc.inPopField, 
        gc.outTable,
        gc.popChangeYN, 
        gc.inCensusFeature2, 
        gc.inPopField2, 
        gc.optionalFieldGroups
        ]
    spatialNeeded = False
    
class pifmConstants(baseMetricConstants):
    name = "PopulationInFloodplainMetrics"
    shortName = "pifm"
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
    fieldPrefix = ["RU_", "FP_"]
    fieldSuffix = ["_RU", "_FP"]
    overlapName = ""
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.intermediateDescription, gc.logDescription]
    fieldParameters = ["", "", gc.defaultDecimalFieldType, 6, 1]
    qaCheckFieldParameters = []
    fieldOverrideKey = ""
    populationProportionFieldName = "FP_POP_P"
    # populationCountFieldNames = ["RU_POP_C", "FP_POP_C"]
    populationCountFieldNames = ["RU_POP", "FP_POP_C"]
    popCntTableName = f"{shortName}_populationCnt"
    floodplainPopName = f"{shortName}_populationFP_"
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inCensusDataset, 
        gc.inPopField, 
        gc.inFloodplainDataset, 
        gc.outTable, 
        gc.optionalFieldGroups
        ]

class pmConstants(baseMetricConstants):
    name = "PatchMetrics"
    shortName = "pm"
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
    fieldPrefix = ""
    fieldSuffix = "_PLGP"
    overlapName = "PM_OVER"
    totalAreaName = "PM_TOTA"
    effectiveAreaName = "PM_EFFA"
    excludedAreaName = "PM_EXCA"
    optionalFilter = [gc.qaCheckDescription, gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultPercentFieldType, 6, 1]
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
    mdnSuffix = "_MDN"
    densSuffix = "_DENS"
    lrgSuffix = "_LRG"
    mdcpSuffix = "_MDCP"
    additionalSuffixes = [numSuffix, avgSuffix, mdnSuffix, densSuffix, lrgSuffix, mdcpSuffix]
    # numField = ["", numSuffix, gc.defaultIntegerFieldType, 6, 0]
    numField = ["", numSuffix, 'LONG', 7, 0]
    avgField = ["", avgSuffix, gc.defaultAreaFieldType, 15, 1]
    mdnField = ["", mdnSuffix, gc.defaultAreaFieldType, 15, 1]
    # densField = ["", densSuffix, gc.defaultDecimalFieldType, 10, 1]
    densField = ["", densSuffix, gc.defaultAreaFieldType, 15, 1]
    lrgField = ["", lrgSuffix, gc.defaultAreaFieldType, 15, 1]
    # mdcpField = ["", mdcpSuffix, gc.defaultDecimalFieldType, 10, 1]
    mdcpField = ["", mdcpSuffix, gc.defaultAreaFieldType, 15, 1]
    additionalFields = [numField, avgField, mdnField, densField, lrgField]
    mdcpFields = [mdcpField]
    rastertoPoly = "PatchPoly"
    rastertoPoint = "PatchCentroids"
    polyDissolve = "PatchPoly_Diss"
    nearTable = "_NearTable_"
    classValue = 3
    excludedValue = -9999
    otherValue = 0
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inLandCoverGrid, 
        gc._lccName, 
        gc.lccFilePath, 
        gc.metricsToRun,
        gc.inPatchSize, 
        gc.inMaxSeparation, 
        gc.outTable, 
        gc.mdcpYN, 
        gc.processingCellSize, 
        gc.snapRaster, 
        gc.optionalFieldGroups, 
        gc.clipLCGrid
        ]
    
class plcvConstants(baseMetricConstants):
    name = "PopulationLandCoverViews"
    shortName = "plcv"
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
    fieldPrefix = ""
    mvFieldPrefix = ""
    fieldSuffix = "_PV_C"
    wovFieldSuffix = "_MV_C"
    overlapName = ""
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultIntegerFieldType, 10, 0]
    qaCheckFieldParameters = []
    # This metric is comprised of several output fields. Fieldname override option 
    # is not available to the user  
    fieldOverrideKey = ""
    pctSuffix = "_PV_P"
    wovPctSuffix = "_MV_P"
    additionalSuffixes = [pctSuffix]
    cntField = [fieldPrefix, pctSuffix, gc.defaultDecimalFieldType, 6, 1]
    additionalFields = [cntField]
    valueCountFieldNames =["RU_POP"]
    valueCountTableName = f"{shortName}_populationCnt"
    viewRasterOutputName = "_ViewArea"
    viewPolygonOutputName = "_ViewAreaPoly"
    areaPopRasterOutputName = "_ViewPopulation"
    areaValueCountTableName = "_ViewPopulationByRU"
    valueWhenNULL = 0
    patchGridName = "_ViewPatch"
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inLandCoverGrid, 
        gc._lccName, 
        gc.lccFilePath,
        gc.metricsToRun, 
        gc.viewRadius, 
        gc.minPatchSize, 
        gc.inCensusRaster, 
        gc.outTable, 
        gc.processingCellSize, 
        gc.snapRaster, 
        gc.optionalFieldGroups
        ]
    
class pnfeaConstants(baseMetricConstants):
    #prefix = "NAVTEQ"
    prefix = ""
    outNameRoadsWalkable = prefix+"_RdsWalkable"
    outNameRoadsIntDens = prefix+"_RdsIntDens"
    outNameRoadsIAC = prefix+"_RdsIAC"
    value0_LANES = prefix + "_RdsIAC_0Lanes"
    optionalFilter = [gc.logDescription]
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = []
    spatialNeeded = False

class prfeaConstants(baseMetricConstants): #Process All Streets (NAVTEQ 2011, NAVTEQ 2019, ESRI StreetMap)
    name = "ProcessRoadsforEnviroAtlasAnalyses"
    shortName = "prfea"
    toolFUNC = f'arcpy.ATtILA.{shortName.upper()}'
    scriptOpening = gc.basicScriptOpening
    prefix = ""
    optionalFilter = [gc.logDescription]
    outNameRoadsWalkable = "_RdsWalkable" 
    outNameRoadsIntDens = "_RdsIntDens"
    outNameRoadsIAC = "_RdsIAC"
    value0_LANES = "IAC_Lanes" 
     
    typeCodesString = "'AIRPORT',"\
                      "'AMUSEMENT PARK',"\
                      "'BEACH',"\
                      "'CEMETERY',"\
                      "'HOSPITAL',"\
                      "'INDUSTRIAL COMPLEX',"\
                      "'MILITARY BASE',"\
                      "'RAILYARD',"\
                      "'SHOPPING CENTRE',"\
                      "'GOLF COURSE'" 
    
    typeCodesNumeric = ('509998', #Beach
                        '900108', #Military Base
                        '1900403', #Airports
                        '2000123', #Golf Course
                        '2000124', #Shopping Center
                        '2000200', #Industrial Complex
                        '2000408', #Hospital
                        '2000420', #Cemetery
                        '2000460', #Amusement Park
                        '9997007' #Railyard
                        )
    
    # StreetMap
    landUseSetSM = " Or FEATURE_TYPE = ".join(typeCodesNumeric)
    landUseSetSMShp = " Or FEATURE_TY = ".join(typeCodesNumeric)
        
    # NAVTEQ 2019 
    Streets_linkfield = 'Link_ID'
    Link_linkfield = 'LINK_ID'
    landUseSetNAV19 = " Or FEATURE_TYPE = ".join(typeCodesNumeric)
    landUseSetNAV19Shp = " Or FEATURE_TY = ".join(typeCodesNumeric)
    
    # NAVTEQ 2011 
    # empty
    
    requiredDict = {
        "ESRI StreetMap": ["\\Streets", "\\MapLandArea\\MapLandArea"],
        "NAVTEQ 2019": ["\\RoutingApplication\\Streets", "\\MapFacilityArea", "\\MapLanduseArea", "\\link"],
        "NAVTEQ 2011": ["\\Streets", "\\LandUseA", "\\LandUseB"]
        }
    
    walkSelectDict = {
        "ESRI StreetMap": "SpeedCat < 4 Or FuncClass < 3 Or RestrictPedestrians = 'Y' Or FerryType <> 'H' Or Ramp = 'Y' Or ContrAcc = 'Y' Or Tollway = 'Y'",
        "NAVTEQ 2019": "SpeedCat < 4 Or FuncClass < 3 Or RestrictPedestrians = 'Y' Or FerryType <> 'H' Or Ramp = 'Y' Or ContrAcc = 'Y' Or Tollway = 'Y'",
        "NAVTEQ 2011": "FUNC_CLASS IN ('1','2') Or FERRY_TYPE <> 'H' Or SPEED_CAT IN ('1', '2', '3') Or AR_PEDEST = 'N' Or RAMP = 'Y' Or CONTRACC = 'Y' Or TOLLWAY ='Y'"
        }
    
    walkMsgDict = {
        "ESRI StreetMap": "Selecting and removing features where FuncClass < 3; SpeedCat < 4; RestrictPedestrians = 'Y'; FerryType <> 'H'; Ramp = 'Y'; ContrAcc = 'Y'; TollWay = 'Y'",
        "NAVTEQ 2019": "Selecting and removing features where FuncClass < 3; SpeedCat < 4; RestrictPedestrians = 'Y'; FerryType <> 'H'; Ramp = 'Y'; ContrAcc = 'Y'; TollWay = 'Y'",
        "NAVTEQ 2011": "Selecting and removing features where FUNC_CLASS < 3; SPEED_CAT < 4; AR_PEDEST = 'N'; FERRY_TRYPE <> 'H'; RAMP = 'Y'; CONTRACC = 'Y'; TOLLWAY = 'Y'"
        }
    
    laneFieldDict = {
        "ESRI StreetMap": ['FROM_REF_NUM_LANES','TO_REF_NUM_LANES'],
        "NAVTEQ 2019": ['FROM_REF_NUM_LANES','TO_REF_NUM_LANES'],
        "NAVTEQ 2011": ['TO_LANES', 'FROM_LANES'],
        "ESRI StreetMap.shp": ['FROM_REF_N','TO_REF_NUM'],
        "NAVTEQ 2019.shp": ['FROM_REF_N','TO_REF_NUM'],
        "NAVTEQ 2011.shp": ['TO_LANES', 'FROM_LANES']
        }
    
    dirTravelDict = {
        "ESRI StreetMap": "DirTravel = 'B'",
        "NAVTEQ 2019": "DirTravel = 'B'",
        "NAVTEQ 2011": "DIR_TRAVEL = 'B'"
        }
    
    unnamedStreetsDict = {
        "ESRI StreetMap": f"StreetName = '' And (FEATURE_TYPE = {landUseSetSM})",
        "NAVTEQ 2019": f"StreetName = '' And (FEATURE_TYPE = {landUseSetNAV19})",
        "NAVTEQ 2011": f"FEAT_TYPE IN ({typeCodesString}) And ST_NAME = ''",
        "ESRI StreetMap.shp": f"StreetName = '' And (FEATURE_TY = {landUseSetSMShp})",
        "NAVTEQ 2019.shp": f"StreetNa_1 = '' And (FEATURE_TY = {landUseSetNAV19Shp})",
        "NAVTEQ 2011.shp": f"FEAT_TYPE IN ({typeCodesString}) And ST_NAME = ''"
        }
    
    speedCatDict = {
        "ESRI StreetMap": "SpeedCat = 8",
        "NAVTEQ 2019": "SpeedCat = 8",
        "NAVTEQ 2011": "SPEED_CAT IN ('8')"
        }

    parameterLabels = [
        gc.toolScriptPath,
        gc.versionName,
        gc.inStreetsgdb,
        gc.chkWalkableYN,
        gc.chkIntDensYN,
        gc.chkIACYN,
        gc.outWorkspace,
        gc.fnPrefix,
        gc.optionalFieldGroups
        ]
    
class pnhd24kConstants(baseMetricConstants):
    prefix = ""
    optionalFilter = [gc.logDescription]
    spatialNeeded = False

class pwzmConstants(baseMetricConstants):
    name = "PopulationWithinZoneMetrics"
    shortName = "pwzm"
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
    fieldPrefix = ["RU_", "FP_"]
    fieldSuffix = ["_RU", "_FP"]
    optionalFilter = [gc.intermediateDescription, gc.logDescription]
    fieldParameters = ["", "", gc.defaultPercentFieldType, 6, 1]
    qaCheckFieldParameters = []
    fieldOverrideKey = ""
    populationProportionFieldName = "ZN_POP_P"
    populationCountFieldNames = ["RU_POP", "ZN_POP_C"]
    popCntTableName = f"{shortName}_populationCnt_"
    zonePopName = f"{shortName}_populationZN_"
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inCensusDataset, 
        gc.inPopField, 
        gc.inZoneDataset,
        gc.inBufferDistance, 
        gc.groupByZoneYN,
        gc.zoneIdField,
        gc.outTable, 
        gc.optionalFieldGroups
        ]

class rlcpConstants(baseMetricConstants):
    name = "RiparianLandCoverProportions"
    shortName = "rlcp"
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
    fieldPrefix = "r"
    fieldSuffix = ""
    overlapName = "RLCP_OVER"
    totalAreaName = "RLCP_TOTA"
    effectiveAreaName = "RLCP_EFFA"
    excludedAreaName = "RLCP_EXCA"
    pctBufferSuffix = ""
    pctBufferBase = f"{fieldPrefix}EFFA"
    pctBufferName = f"{pctBufferBase}{pctBufferSuffix}"
    totaPctSuffix = ""
    totaPctBase = f"{fieldPrefix}TOTA"
    totaPctName = f"{totaPctBase}{totaPctSuffix}"
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultPercentFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15],
        [totaPctName, gc.defaultPercentFieldType, 6, 1],
        [pctBufferName, gc.defaultPercentFieldType, 6, 1]                                        
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inLandCoverGrid, 
        gc._lccName, 
        gc.lccFilePath,
        gc.metricsToRun, 
        gc.inStreamFeatures, 
        gc.inBufferDistance, 
        gc.enforceBoundary, 
        gc.outTable, 
        gc.processingCellSize, 
        gc.snapRaster,
        gc.optionalFieldGroups
        ]
    
class rdmConstants(baseMetricConstants):
    name = "RoadDensityMetrics"
    shortName = "rdm"
    toolFUNC = f'arcpy.ATtILA.{shortName.upper()}'
    scriptOpening = gc.basicScriptOpening
    fieldPrefix = ""
    fieldSuffix = ""
    overlapName = ""
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultPercentFieldType, 6, 1]
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
    roadsByReportingUnitName = [f"{shortName}_RdsByRU_","FeatureClass"]
    streamsByReportingUnitName = [f"{shortName}_StrByRU_","FeatureClass"]
    roadStreamMultiPoints = [f"{shortName}_RdsXStrMP_","FeatureClass"]
    roadStreamIntersects = [f"{shortName}_PtsOfXing_","FeatureClass"]
    roadStreamSummary = [f"{shortName}_RdsXStrTbl_","Dataset"]
    streamBuffers = [f"{shortName}_StrBuffers_","FeatureClass"]
    roadsNearStreams = [f"{shortName}_RdsNrStrms_","FeatureClass"]
    tmp1RNS = [f"{shortName}_TmpRdsInBuffer_","FeatureClass"]
    tmp2RNS = [f"{shortName}_TmpRdsWithRUID_","FeatureClass"]
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inRoadFeature, 
        gc.outTable, 
        gc.roadClassField,
        gc.streamRoadCrossings, 
        gc.roadsNearStreams, 
        gc.inStreamFeature, 
        gc.inBufferDistance, 
        gc.optionalFieldGroups
        ]
    spatialNeeded = False

class sdmConstants(baseMetricConstants):
    name = "StreamDensityMetric"
    shortName = "sdm"
    toolFUNC = f'arcpy.ATtILA.{shortName.upper()}'
    scriptOpening = gc.basicScriptOpening
    fieldPrefix = ""
    fieldSuffix = ""
    overlapName = ""
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultPercentFieldType, 6, 1]
    qaCheckFieldParameters = []
    fieldOverrideKey = ""
    areaFieldname = "AREAKM2"
    lineLengthFieldName = "STRMKM"
    lineDensityFieldName = "STRMDENS"
    linesByReportingUnitName = [f"{shortName}_StrByRU","FeatureClass_"]
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inLineFeature, 
        gc.outTable, 
        gc.strmOrderField, 
        gc.optionalFieldGroups
        ]
    spatialNeeded = False

class splcpConstants(baseMetricConstants):
    name = "SamplePointLandCoverProportions"
    shortName = "splcp"
    toolFUNC = f'metric.run{name}'
    scriptOpening = gc.metricScriptOpening
    fieldPrefix = "s"
    fieldSuffix = ""
    overlapName = "SPLCP_OVER"
    totalAreaName = "SPLCP_TOTA"
    effectiveAreaName = "SPLCP_EFFA"
    excludedAreaName = "SPLCP_EXCA"
    pctBufferSuffix = ""
    pctBufferBase = f"{fieldPrefix}EFFA"
    pctBufferName = f"{pctBufferBase}{pctBufferSuffix}"
    totaPctSuffix = ""
    totaPctBase = f"{fieldPrefix}TOTA"
    totaPctName = f"{totaPctBase}{totaPctSuffix}"
    optionalFilter = [gc.qaCheckDescription, gc.metricAddDescription, gc.intermediateDescription, gc.logDescription]
    fieldParameters = [fieldPrefix, fieldSuffix, gc.defaultPercentFieldType, 6, 1]
    qaCheckFieldParameters = [
        [overlapName, gc.defaultIntegerFieldType, 6],
        [totalAreaName, gc.defaultAreaFieldType, 15],
        [effectiveAreaName, gc.defaultAreaFieldType, 15],
        [excludedAreaName, gc.defaultAreaFieldType, 15],
        [totaPctName, gc.defaultPercentFieldType, 6, 1],
        [pctBufferName, gc.defaultPercentFieldType, 6, 1]                                        
        ]
    fieldOverrideKey = shortName + gc.fieldOverrideName
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.toolScriptPath,
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inLandCoverGrid, 
        gc._lccName, 
        gc.lccFilePath,
        gc.metricsToRun, 
        gc.inPointFeatures, 
        gc.ruLinkField, 
        gc.inBufferDistance, 
        gc.enforceBoundary, 
        gc.outTable, 
        gc.processingCellSize, 
        gc.snapRaster, 
        gc.optionalFieldGroups
        ]

class szsConstants(baseMetricConstants):
    name = "SelectZonalStatistics"
    shortName = "szs"
    toolFUNC = f'arcpy.ATtILA.{shortName.upper()}'
    scriptOpening = gc.basicScriptOpening
    fieldPrefix = ""
    fieldSuffix = ""
    qaName = "AREA_OVER"
    totalAreaName = ""
    effectiveAreaName = ""
    excludedAreaName = ""
    optionalFilter = [gc.logDescription]
    #fieldParameters = [fieldPrefix,fieldSuffix, gc.defaultDecimalFieldType, 8, 4]
    # Output field names are fixed. Field name override option is not available to the user.
    statsToRun = ''
    # copy tool's parameter variable names from metric.py arguments. Be sure there's a corresponding entry in global constants. Keep variable names uniform between tools.
    parameterLabels = [
        gc.inReportingUnitFeature, 
        gc.reportingUnitIdField, 
        gc.inValueRaster,
        gc.statisticsType,
        gc.outTable, 
        gc.fieldPrefix,
        gc.optionalFieldGroups]
    
    statisticsFieldNames = ["COUNT", "AREA", "MIN", "MAX", "RANGE", "MEAN", "STD", "SUM", "VARIETY", "MAJORITY", "MAJORITY_COUNT", "MAJORITY_PERCENT", 
                            "MINORITY", "MINORITY_COUNT", "MINORITY_PERCENT", "MEDIAN", "PCT90"]
    
    idFields = gc.idFields + ["ZONE_CODE"]
    
