'''
Input and output parameters for all metric tests.  
Created July, 2012

@author: thultgren
'''

#  Parameters for all tools
inReportingUnitFeature = "testData\\blkgrp2000.shp"
reportingUnitIdField = "BKG_KEY"
inLandCoverGrid = "testData\\nlcd00"
_lccName = 'NLCD 2001'
lccFilePath = '..\\..\\..\\LandCoverClassifications\\NLCD 2001.lcc'
#metricsToRun = "'nat  -  [NINDEX]  All natural land use';'wtle  -  [pwtle]  Emergent Herbaceous Wetland';'shrb  -  [pshrb]  Shrubland';'hrbt  -  [phrbt]  All Herbaceous';'hrbg  -  [phrbg]  Grassland, Herbaceous';'hrbo  -  [phrbo]  Herbaceous Other';'bart  -  [pbart]  Barren';'unat  -  [UINDEX]  All human land use';'devt  -  [pdevt]  All Developed';'devo  -  [pdevo]  Developed, Open Space';'devl  -  [pdevl]  Developed, Low Intensity';'devm  -  [pdevm]  Developed, Medium Intensity';'devh  -  [pdevh]  Developed, High Intensity';'agt  -  [pagt]  All Agriculture';'agp  -  [pagp]  Pasture';'agc  -  [pagc]  Cultivated Crops'"
metricsToRun = "'nat  -  [NINDEX]  All natural land use';'for  -  [pfor]  Forest';'wtlt  -  [pwtlt]  All Wetlands';'wtlw  -  [pwtlw]  Woody Wetland';'wtle  -  [pwtle]  Emergent Herbaceous Wetland';'shrb  -  [pshrb]  Shrubland';'hrbt  -  [phrbt]  All Herbaceous';'hrbg  -  [phrbg]  Grassland, Herbaceous';'hrbo  -  [phrbo]  Herbaceous Other';'bart  -  [pbart]  Barren';'unat  -  [UINDEX]  All human land use';'devt  -  [pdevt]  All Developed';'devo  -  [pdevo]  Developed, Open Space';'devl  -  [pdevl]  Developed, Low Intensity';'devm  -  [pdevm]  Developed, Medium Intensity';'devh  -  [pdevh]  Developed, High Intensity';'agt  -  [pagt]  All Agriculture';'agp  -  [pagp]  Pasture';'agc  -  [pagc]  Cultivated Crops'"
outTable = 'testOutput\\TestOutput.dbf'
processingCellSize = '30' 
snapRaster = 'testData\\nlcd00'
optionalFieldGroups = "'QAFIELDS  -  Add Quality Assurance Fields';'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'"

# Parameters for LandCoverProportions
refLandCoverOutput = 'testData\\TestOutput.dbf' # Reference output data

# Parameters for LandCoverOnSlopeProportionsTest
refLandCoverOnSlopeOutput = 'testData\\TestOutput.dbf' # Reference output data
inSlopeGrid = ''
inSlopeThresholdValue = ''



