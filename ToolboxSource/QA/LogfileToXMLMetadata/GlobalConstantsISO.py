# Global functions for .txt to xml conversion

class BaseConstants(): 
    specs = 'SPECS:'  # probably all of this can be simplified and cleaned, but easy for now to change output
    tool = 'TOOL:'
    params = 'PARAMETER:'
    FIELDS = 'FIELD:'
    fields =  'Field:'
    cell_size = 'Cell Size'
    start_time = 'Started:'
    end_time = 'Ended:'
    proc_steps = '[202'
    bounds = 'Extent Intersection'
    classes = 'CLASS'
    neighborhood = 'Neighborhood width'
    metrics = 'Report metrics'
    neighborhood = 'Neighborhood width'
    slope_thresh = 'Slope threshold'
    buff = 'Buffer_distance'
    outTable = "Output_table"
    statsType = "Statistics type"

    themekey_list = []
    placekey_list = ['City, State Abrv.', 'State']

    title = ''
    newlink = 'https://www.epa.gov/enviroatlas/attila-toolbox'
    abstract = ''
    purpose = ''

    overview = ('These layers describe land cover characteristics derived using the '
              '{0} tool from the ATtILA toolbox for ArcGIS Pro (v2.8). '
              'https://www.epa.gov/enviroatlas/attila-toolbox. ' 
              'A list of creation steps is included in the Processing Steps.') #.format(toolname)) THIS ONE NEEDS SORTING OUT

#Working on this with linkages, tomorrow try to get this working 

    links = ['link1', 'link2', 'link3', 'link4']
    HUC_12_defs = 'Federal Guidelines, Requirements, and Procedures for the National Watershed Boundary Dataset; Chapter 3 of Section A; Federal Standards, Book 11, Collection and Delineation of Spatial Data; Techniques and Methods 11-A3.'



#Landscape Charecteristics
class LCPConstants(BaseConstants): # Land Cover Proportions
    themekey_list = ['Census Block Groups', 'Communities', 'Demand for Ecosystem Services', 'Demographics', 'Ecosystem', 
    'Ecosystem Services', 'Environment', 'Hazards', 'Health', 'Human', 'Human Well-being', 'Land Cover', 'Land Cover Proportions']
    title = 'Land Cover Proportions'
    abstract = ("Calculates percentages of selected land cover types within reporting unit polygons and creates an output table"
                " This dataset was produced by the US EPA to support research and online mapping activities related to EnviroAtlas."
                " EnviroAtlas (https://www.epa.gov/enviroatlas) allows the user to interact with a web-based, easy-to-use, mapping application to view and analyze multiple ecosystem services for the contiguous United States." 
                " Additional descriptive information about each attribute in this dataset can be found in its associated EnviroAtlas Fact Sheet (https://www.epa.gov/enviroatlas/enviroatlas-fact-sheets)"
                )
    purpose = ("ATtILA is an easy to use Esri ArcGIS toolbox that calculates landscape and landscape/human interaction metrics, including many of those found in EnviroAtlas."
                " The overall goal of EnviroAtlas is to employ and develop the best available science to map indicators of ecosystem services production, demand, and drivers for the nation."
                )
class LCOSPConstants(BaseConstants): # Land Cover on Slope Proportions
    themekey_list = ['Census Block Groups', 'Communities', 'Demand for Ecosystem Services', 'Demographics', 'Ecosystem', 
    'Ecosystem Services', 'Environment', 'Land Cover', 'Slope', 'Land Cover on Slope']
    title = 'Land Cover on Slope Proportions'
    abstract = ("Calculates percentages of land cover types on slopes greater than a specified threshold value within reporting unit polygons and creates an output table."
                " This dataset was produced by the US EPA to support research and online mapping activities related to EnviroAtlas."
                " EnviroAtlas (https://www.epa.gov/enviroatlas) allows the user to interact with a web-based, easy-to-use, mapping application to view and analyze multiple ecosystem services for the contiguous United States." 
                " Additional descriptive information about each attribute in this dataset can be found in its associated EnviroAtlas Fact Sheet (https://www.epa.gov/enviroatlas/enviroatlas-fact-sheets)"
                )
    purpose = ("ATtILA is an easy to use Esri ArcGIS toolbox that calculates landscape and landscape/human interaction metrics, including many of those found in EnviroAtlas."
                " The overall goal of EnviroAtlas is to employ and develop the best available science to map indicators of ecosystem services production, demand, and drivers for the nation."
                )
class NPConstants(BaseConstants): # Neighborhood Proportions
    themekey_list = ['Census Block Groups', 'Communities', 'Demand for Ecosystem Services', 'Demographics', 'Ecosystem', 
    'Ecosystem Services', 'Environment', 'Hazards', 'Health', 'Human', 'Human Well-being', 'Land Cover', 'Neighborhood Proportions']
    title = 'Neighborhood Proportions'
    abstract = ("Calculates the area percentage of selected land cover classes within a given neighborhood." 
                " The neighborhood is square in shape. Its size is provided by the user." 
                )
    purpose = ("The purpose of this data is to show the density of land cover types and the gradients of change."
                " ATtILA is an easy to use Esri ArcGIS toolbox that calculates landscape and landscape/human interaction metrics, including many of those found in EnviroAtlas."
                " The overall goal of EnviroAtlas is to employ and develop the best available science to map indicators of ecosystem services production, demand, and drivers for the nation."
                )

#People in Landscape
class PIFMConstants(BaseConstants): # Population in Floodplain
    themekey_list = ['Census Block Groups', 'Communities', 'Demand for Ecosystem Services', 'Demographics', 'Ecosystem', 
    'Ecosystem Services', 'Environment', 'Hazards', 'Health', 'Human', 'Human Well-being', 'Land Cover', 'Risk',
    'Water', 'Flood', 'Floodplain']
    title = 'Population in Floodplain'
    abstract = ("This EnviroAtlas dataset describes the total counts and percentage of population, land area, and impervious surface in the 1% Annual Chance Flood Hazard area or 0.2% Annual Chance Flood Hazard area of each block group." 
                " The flood hazard area is defined by the National Flood Hazard Layer (NFHL) produced by the Federal Emergency Management Agency (FEMA, www.fema.gov). "
                " This dataset was produced by the US EPA to support research and online mapping activities related to EnviroAtlas." 
                " EnviroAtlas (https://www.epa.gov/enviroatlas) allows the user to interact with a web-based, easy-to-use, mapping application to view and analyze multiple ecosystem services for the contiguous United States." 
                " The dataset is available as downloadable data (https://edg.epa.gov/data/Public/ORD/EnviroAtlas) or as an EnviroAtlas map service." 
                " Additional descriptive information about each attribute in this dataset can be found in its associated EnviroAtlas Fact Sheet (https://www.epa.gov/enviroatlas/enviroatlas-fact-sheets)" 
                )
    purpose = ("The purpose of this dataset is to describe the population, land area, and impervious surfaces in the high-risk flood hazard area (i.e., 1% Annual Chance Flood Hazard or 0.2% Annual Chance Flood Hazard) within the EnviroAtlas Community."
                " The overall goal of EnviroAtlas is to employ and develop the best available science to map indicators of ecosystem services production, demand, and drivers for the nation."
                )
class RDMConstants(BaseConstants): # Road Density
    themekey_list = ['Census Block Groups', 'Communities', 'Demand for Ecosystem Services', 'Demographics', 'Ecosystem', 
    'Ecosystem Services', 'Environment', 'Human Impact', 'Road Density Metrics']
    title = 'Road Density Metrics'
    abstract = ("Calculates metrics based on input vector line dataset(s) for each reporting unit polygon and creates an output table.")
    purpose = ("The purpose of this data is to show the road density within the reporting unit metric."
                " ATtILA is an easy to use Esri ArcGIS toolbox that calculates landscape and landscape/human interaction metrics, including many of those found in EnviroAtlas."
                " The overall goal of EnviroAtlas is to employ and develop the best available science to map indicators of ecosystem services production, demand, and drivers for the nation."
                )

#Riparian Charecteristics
class RLCPConstants(BaseConstants): # Riparian Land Cover Proportions
    themekey_list = ['Census Block Groups', 'Communities', 'Demand for Ecosystem Services', 'Demographics', 'Ecosystem', 
    'Ecosystem Services', 'Environment', 'Hazards', 'Health', 'Human', 'Riparian']
    title = 'Riparian Land Cover Proportions'
    abstract = ("This EnviroAtlas dataset describes the percentage of different land cover types within a buffer of hydrologically connected streams, rivers, and other water bodies within the Atlas Area."
                " This dataset was produced by the US EPA to support research and online mapping activities related to EnviroAtlas."
                " EnviroAtlas (https://www.epa.gov/enviroatlas) allows the user to interact with a web-based, easy-to-use, mapping application to view and analyze multiple ecosystem services for the contiguous United States." 
                " Additional descriptive information about each attribute in this dataset can be found in its associated EnviroAtlas Fact Sheet (https://www.epa.gov/enviroatlas/enviroatlas-fact-sheets)"
                )
    purpose = ("ATtILA is an easy to use Esri ArcGIS toolbox that calculates landscape and landscape/human interaction metrics, including many of those found in EnviroAtlas."
                " The overall goal of EnviroAtlas is to employ and develop the best available science to map indicators of ecosystem services production, demand, and drivers for the nation."
                )
class SDMConstants(BaseConstants): # Stream Density 
    themekey_list = ['Census Block Groups', 'Communities', 'Demand for Ecosystem Services', 'Demographics', 'Ecosystem', 
    'Ecosystem Services', 'Environment', 'Water', 'Stream Density Metrics']
    title = 'Stream Density Metrics'
    abstract = ("Calculates density metrics based on input vector line dataset(s) for each reporting unit polygon and creates an output table."
                " Default metrics include area of the reporting unit (km^2), total length (km) and line density (km/km^2) within the reporting unit."
                )
    purpose = ("The purpose of this data is to show the stream density within the reporting unit metric."
                " ATtILA is an easy to use Esri ArcGIS toolbox that calculates landscape and landscape/human interaction metrics, including many of those found in EnviroAtlas."
                " The overall goal of EnviroAtlas is to employ and develop the best available science to map indicators of ecosystem services production, demand, and drivers for the nation."
                )
    
class SZSConstants(BaseConstants):
    themekey_list = ['Utilities']
    title = 'Process Zonal Statistics'
    abstract = ("Summarizes the values of a raster within the zones of another dataset and reports the results as a table for the following statistics: {statsList}")
    purpose = ("ATtILA is an easy to use Esri ArcGIS toolbox that calculates landscape and landscape/human interaction metrics, including many of those found in EnviroAtlas."
                " The overall goal of EnviroAtlas is to employ and develop the best available science to map indicators of ecosystem services production, demand, and drivers for the nation."
                )
    
class PAAAConstants(BaseConstants): #These need updating
    themekey_list = ['Utilities']
    title = 'NEEDED'
    abstract = ("NEEDED")
    purpose = ("ATtILA is an easy to use Esri ArcGIS toolbox that calculates landscape and landscape/human interaction metrics, including many of those found in EnviroAtlas."
                " The overall goal of EnviroAtlas is to employ and develop the best available science to map indicators of ecosystem services production, demand, and drivers for the nation."
    )

class Unknown(BaseConstants): 
    themekey_list = ['NEEDED']
    title = 'NEEDED'
    abstract = ('NEEDED')
    purpose = ("NEEDED")