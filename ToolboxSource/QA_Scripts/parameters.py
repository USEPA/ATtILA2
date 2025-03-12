import os

inGDB = None # Change path to input data geodatabase

class setup: 
    ATtILA_pth = None # Path to ATtILA.tbx
    inGDB = inGDB
    outFolder = None # Folder where output Geodatabases and logfiles will be written here
    _lccName = 'NLCD LAND'
    lccFilePath = None # Path to lccFile
    NAVTEQ_2011 = None # Path to NAVTEQ 2011 test data
    NAVTEQ_2019 = None # Path to NAVTEQ 2019 test data
    ESRI_StreetMaps = None # Path to ESRI StreetMaps test data
    NHD_HR_multi = None # Path to multiple NHD gdb's
    NHD_H_0509_HUC4 = None # Path to HUC 0509 NHD gdb
    NHD_plus = None # Path to NHD plus dataset for multiple shapefiles NHD test
    NHD_Shapefile_folder = None # Path to single shapefile NHD folder
class points:
    Daycares = os.path.join(inGDB, "Daycares")
    SampleSites = os.path.join(inGDB, "SampleSites")
class lines: 
    Roads = os.path.join(inGDB, "Roads")
    Roads_NonWalkable = os.path.join(inGDB, "Roads_NonWalkable")
    Roads_Walkable = os.path.join(inGDB, "Roads_Walkable")
    StreamLines = os.path.join(inGDB, "Stream_Lines")
    WaterLines = os.path.join(inGDB, "Water_Lines")
class polygons: 
    Blockgroups = os.path.join(inGDB, "Blockgroups")
    Blockgroups_Fresno = os.path.join(inGDB, "Blockgroups_Fresno")
    Census2010 = os.path.join(inGDB, "Census2010")
    Census2020 = os.path.join(inGDB, "Census2020")
    MockLakes = os.path.join(inGDB, "Mock_Lakes")
    Parks = os.path.join(inGDB, "Parks")
    Population = os.path.join(inGDB, "Population")
    StreamPolygons = os.path.join(inGDB, "Stream_Polygons")
    ThreeParks = os.path.join(inGDB, "ThreeParks")
    WaterPolygons = os.path.join(inGDB, "Water_Polygons")
    Watersheds = os.path.join(inGDB, "Watersheds")
    Floodplain_Polygons = os.path.join(inGDB, "Floodplain_Polygons")
class rasters: 
    DASY_Population = os.path.join(inGDB, "DASY_Population")
    DASY_Population_Fresno = os.path.join(inGDB, "DASY_Population_Fresno")
    Floodplain_NLCD = os.path.join(inGDB, "Floodplain_NLCD")
    Floodplain_Raster = os.path.join(inGDB, "Floodplain_Raster")
    MULC_2017 =  os.path.join(inGDB, "MULC_2017")
    NLCD_2016 = os.path.join(inGDB, "NLCD_2016")
    NLCD_Subset = os.path.join(inGDB, "NLCD_Subset")
    nonzeroFloodplain = os.path.join(inGDB, "nonzeroFloodplain")
    Population_Raster = os.path.join(inGDB, "Population_Raster")
    Slope = os.path.join(inGDB, "Slope")
    Walkable_Cost_Surface = os.path.join(inGDB, "Walkable_Cost_Surface")
class OUTS: 
    fileName = '_'
    toolPath = ' Testing'
    outGDB = '_Test.gdb'
