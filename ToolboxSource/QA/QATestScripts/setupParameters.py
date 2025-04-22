import os
import arcpy
currentDir = os.getcwd()
parentDir = os.path.dirname(currentDir) #Navigate two levels above

class setup: 
    ATtILA_pth = None # Path to ATtILA.tbx
    inGDB = None
    outFolder = None
    _lccName = 'NLCD LAND'
    lccFilePath = os.path.join(parentDir, "LandCoverClassifications\\NLCD LAND.xml")
    NAVTEQ_2011 = None # Path to NAVTEQ 2011 test data
    NAVTEQ_2019 = None # Path to NAVTEQ 2019 test data
    ESRI_StreetMaps = None # Path to ESRI StreetMaps test data
    NHD_HR_multi = None # Path to multiple NHD gdb's
    NHD_H_0509_HUC4 = None # Path to HUC 0509 NHD gdb
    NHD_plus = None # Path to NHD plus dataset for multiple shapefiles NHD test
    NHD_Shapefile_folder = None # Path to single shapefile NHD folder

class points:
    def __init__(self): 
        if setup.inGDB is None: 
            raise ValueError("setup.inGDB not set properly")
        
    @property    
    def Brownfields(self): 
        return os.path.join(setup.inGDB, "Brownfields")
    @property    
    def Contaminated_Sites(self): 
        return os.path.join(setup.inGDB, "Contaminated_Sites")
    @property    
    def EV_Charging_Stations(self): 
        return os.path.join(setup.inGDB, "EV_Charging_Stations")
    @property    
    def Gasoline_Service_Stations(self): 
        return os.path.join(setup.inGDB, "Gasoline_Service_Stations")
    @property
    def Post_Secondary_Schools(self): 
        return os.path.join(setup.inGDB, "Post_Secondary_Schools")
    @property
    def Public_Schools(self): 
        return os.path.join(setup.inGDB, "Public_Schools")
    @property
    def SampleSites(self): 
        return os.path.join(setup.inGDB, "SampleSites")
    
class lines: 
    @property   
    def Roads(self):
        return os.path.join(setup.inGDB, "Roads")
    @property 
    def Roads_NonWalkable(self):
        return os.path.join(setup.inGDB, "Roads_NonWalkable")
    @property 
    def Roads_Walkable(self):
        return os.path.join(setup.inGDB, "Roads_Walkable")
    @property
    def Runways(self): 
        return os.path.join(setup.inGDB, "Runways")
    @property 
    def Stream_Lines(self): 
        return os.path.join(setup.inGDB, "Stream_Lines")
    @property 
    def WaterLines(self): 
        return os.path.join(setup.inGDB, "Water_Lines")
    
class polygons: 
    @property 
    def Census2010(self):
        return os.path.join(setup.inGDB, "Census2010")
    @property 
    def Census2020(self): 
        return os.path.join(setup.inGDB, "Census2020")
    @property 
    def Floodplain_Polygons(self): 
        return os.path.join(setup.inGDB, "Floodplain_Polygons")
    @property 
    def Parks(self): 
        return os.path.join(setup.inGDB, "Parks")
    @property 
    def Railroads(self): 
        return os.path.join(setup.inGDB, "Railroads")
    @property 
    def Stream_Polygons(self):
        return os.path.join(setup.inGDB, "Stream_Polygons")
    @property 
    def ThreeParks(self):
        return os.path.join(setup.inGDB, "ThreeParks")
    @property 
    def Water_Polygons(self):
        return os.path.join(setup.inGDB, "Water_Polygons")
    @property 
    def Watersheds(self):
        return os.path.join(setup.inGDB, "Watersheds")
    
class rasters:
    @property
    def DASY_Population(self):
        return os.path.join(setup.inGDB, "DASY_Population")
    @property
    def Floodplain_Raster(self):
        return os.path.join(setup.inGDB, "Floodplain_Raster")
    @property
    def NLCD_2016(self):
        return os.path.join(setup.inGDB, "NLCD_2016")
    @property
    def Population_Raster(self): 
        return os.path.join(setup.inGDB, "Population_Raster")
    @property
    def Slope(self): 
        return os.path.join(setup.inGDB, "Slope")
    @property
    def Walkable_Cost_Surface(self):
        return os.path.join(setup.inGDB, "Walkable_Cost_Surface")
class OUTS: 
    fileName = '_'
    toolPath = ' Testing'
    outGDB = '_Test.gdb'

