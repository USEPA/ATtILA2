""" Global, application level variables

"""
titleATtILA = "ATtILA"
attilaVersion = "3.0"
descriptionDelim = "  -  "
areaFieldParameters = ["_A","DOUBLE",15,0]
tbxFileSuffix = ".tbx"
tbxFileDelim = "__"
tbxSriptToolDelim = "#"
qaCheckName = "QAFIELDS"
metricAddName = "AREAFIELDS"
intermediateName = "INTERMEDIATES"
logName = "LOGFILE"
logFileExtension = "%Y%m%d_%H-%M-%S.txt"
qaCheckDescription = "{0}{1}Add Quality Assurance Fields".format(qaCheckName, descriptionDelim)
metricAddDescription = "{0}{1}Add Area Fields for All Land Cover Classes".format(metricAddName, descriptionDelim)
intermediateDescription = "{0}{1}Retain Intermediate Layers Generated During Metric Calculation".format(intermediateName, descriptionDelim)
logDescription = "{0}{1}Record Process Steps Generated During Metric Calculation".format(logName, descriptionDelim)
defaultDecimalFieldType = "FLOAT"
defaultIntegerFieldType = "SHORT"
defaultAreaFieldType = "DOUBLE"
fieldOverrideName = "Field"
metricNameTooLong = "Provided metric name too long for output location. Truncated {0} to {1} "
tabulateAreaTableAbbv = "_TabArea"
ruTabulateAreaTableAbbv = "_TabAreaRU"
scratchGDBFilename = "attilaScratchWorkspace.gdb"
allGridValuesTools = ["lccc", "lcd"]
# These are the extensions Esri recognizes as rasters. They may not all be acceptable when saving a calculated grid. Tools
# such as Intersection Density can only save its output with ".img", or ".tif" extensions when saving to a folder. An 
# extension in this case, however, is not required and may be omitted. No extensions are permitted inside a geodatabase.
rasterExtensions = [".bil",
                    ".bip",
                    ".bmp",
                    ".bsq",
                    ".dat",
                    ".gif",
                    ".img",
                    ".jpg",
                    ".jp2",
                    ".png",
                    ".tif"]
tableExtensions = [".dbf"]

# parameterLabels for Log File
inReportingUnitFeature = "Reporting unit feature"
reportingUnitIdField = "Reporting unit ID field"
inLandCoverGrid = "Land cover grid"
_lccName = "Land cover classification scheme"
lccFilePath = "Land cover classification file"
metricsToRun = "Report metrics for these classes"
outTable = "Output table"
perCapitaYN = "PER CAPITA"
inCensusDataset = "Population raster or polygon feature"
inPopField = "Population field"
processingCellSize = "Processing cell size"
snapRaster = "Snap raster"
optionalFieldGroups = "Select options"
inEdgeWidth = "Edge width"
clipLCGrid = "Reduce land cover grid to smallest recommended size"
inFloodplainGeodataset = "Floodplain raster or polygon feature"
inFacilityFeature = "Facility feature"
viewRadius = "View radius"
viewThreshold = "View threshold"
inLineFeature = "Road feature"
mergeLines = "Merge divided roads"
mergeField = "Merge field"
mergeDistance = "Merge distance"
outputCS = "Output Coordinate System"
cellSize = "Density raster cell size"
searchRadius = "Density raster search radius"
areaUnits = "Density raster area units"
outRaster = "Output raster"
inSlopeGrid = "Slope grid"
inSlopeThresholdValue = "Slope threshold"
inNeighborhoodSize = "Neighborhood width"
burnIn = "Burn in areas of excluded values"
burnInValue = "Burn in value"
minPatchSize = "Minimum patch size for burn in"
createZones = "Create zone raster"
zoneBin_str = "Zone proportion bins"
overWrite = "Overwrite existing outputs"
outWorkspace = "Output workspace"
inCensusFeature = "Census feature"
popChangeYN = "POPCHG"
inCensusFeature2 = "Census T2 feature"
inPopField2 = "Population T2 field"
inFloodplainDataset = "Floodplain raster or polygon feature"
inPatchSize = "Minimum patch size"
inMaxSeparation = "Maximum separation"
mdcpYN = "MDCP"
minPatchSize = "Minimum visible patch size"
inCensusRaster = "Population raster"
inStreamFeatures = "Stream features"
inBufferDistance = "Buffer distance"
enforceBoundary = "Enforce reporting unit boundaries"
inRoadFeature = "Road feature"
roadClassField = "Road class field"
streamRoadCrossings = "STXRD"
roadsNearStreams = "RNS"
inStreamFeature = "Stream feature"
strmOrderField = "Stream order field"
inPointFeatures = "Sample point features"
ruLinkField = "Reporting unit link field"

paramLabelDict = {
    "inReportingUnitFeature": "Reporting unit feature",
    "reportingUnitIdField": "Reporting unit ID field",
    "inLandCoverGrid": "Land cover grid",
    "_lccName": "Land cover classification scheme",
    "lccFilePath": "Land cover classification file",
    "metricsToRun": "Report metrics for these classes",
    "outTable": "Output table",
    "perCapitaYN": "PER CAPITA",
    "inCensusDataset": "Population raster or polygon feature",
    "inPopField": "Population field",
    "processingCellSize": "Processing cell size",
    "snapRaster": "Snap raster",
    "optionalFieldGroups": "Select options",
    "inEdgeWidth": "Edge width",
    "clipLCGrid": "Reduce land cover grid to smallest recommended size",
    "inFloodplainGeodataset": "Floodplain raster or polygon feature",
    "inFacilityFeature": "Facility feature",
    "viewRadius": "View radius",
    "viewThreshold": "View threshold",
    "inLineFeature": "Road feature",
    "mergeLines": "Merge divided roads",
    "mergeField": "Merge field",
    "mergeDistance": "Merge distance",
    "outputCS": "Output Coordinate System",
    "cellSize": "Density raster cell size",
    "searchRadius": "Density raster search radius",
    "areaUnits": "Density raster area units",
    "outRaster": "Output raster",
    "inSlopeGrid": "Slope grid",
    "inSlopeThresholdValue": "Slope threshold",
    "inNeighborhoodSize": "Neighborhood width",
    "burnIn": "Burn in areas of excluded values",
    "burnInValue": "Burn in value",
    "minPatchSize": "Minimum patch size for burn in",
    "createZones": "Create zone raster",
    "zoneBin_str": "Zone proportion bins",
    "overWrite": "Overwrite existing outputs",
    "outWorkspace": "Output workspace",
    "inCensusFeature": "Census feature",
    "popChangeYN": "POPCHG",
    "inCensusFeature2": "Census T2 feature",
    "inPopField2": "Population T2 field",
    "inFloodplainDataset": "Floodplain raster or polygon feature",
    "inPatchSize": "Minimum patch size",
    "inMaxSeparation": "Maximum separation",
    "mdcpYN": "MDCP",
    "minPatchSize": "Minimum visible patch size",
    "inCensusRaster": "Population raster",
    "inStreamFeatures": "Stream features",
    "inBufferDistance": "Buffer distance",
    "enforceBoundary": "Enforce reporting unit boundaries",
    "inRoadFeature": "Road feature",
    "roadClassField": "Road class field",
    "streamRoadCrossings": "STXRD",
    "roadsNearStreams": "RNS",
    "inStreamFeature": "Stream feature",
    "strmOrderField": "Stream order field",
    "inPointFeatures": "Sample point features",
    "ruLinkField": "Reporting unit link field"
    }