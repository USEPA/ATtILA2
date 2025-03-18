from parameters import *
class LCP_options: 
    testInputs = {
        'inReportingUnitFeature' : [polygons.Watersheds], 
        'reportingUnitIdField' : ['HUC_12'], 
        'inLandCoverGrid' : [rasters.NLCD_2016], 
        'metricsToRun' : ["tun  -  [ptun]  Tundra';'wtlw  -  [pwtlw]  Woody Wetland';'UI  -  [UINDEX]  All Human Land Use",
                          "agr  -  [pagr]  Agriculture"],
        'perCapitaYN' : ['true'],
        'inCensusDataset' : [polygons.Census2010],
        'inPopField' : ['Pop'], 
        'processingCellSize' : ['30'], 
        'optionalFieldGroups' : [ "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"]
    }
class CAEM_options: 
    testInputs = {
        'inReportingUnitFeature' : [polygons.Watersheds], 
        'reportingUnitIdField' : ['HUC_12'], 
        'inLandCoverGrid' : [rasters.NLCD_2016],
        'metricsToRun' : ["for  -  [for_E2A]  Forest';'devm  -  [devm_E2A]  Medium Intensity Developed';'NI  -  [NI_E2A]  All Natural Land Use"],
        'Edge_width' : ['5'], 
        'processingCellSize' : ['30'],
        'optionalFieldGroups' : ["'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"],
        'ReduceLandGridToSmallSize' : ['true']
    }   
class LCD_options: 
    testInputs = {
        'inReportingUnitFeature' : [polygons.Census2010], 
        'reportingUnitIdField' : ['COUNTY'], 
        'inLandCoverGrid' : [rasters.NLCD_2016],
        'processingCellSize' : ['30'],
        'optionalFieldGroups' : ["'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"]
    }
class LCOSP_options: 
    testInputs = {
        'inReportingUnitFeature' : [polygons.Watersheds], 
        'reportingUnitIdField' : ['HUC_12'], 
        'inLandCoverGrid' : [rasters.NLCD_2016],
        'metricsToRun' : ["agr  -  [agr_SL]  Agriculture';'NI  -  [NI_SL]  All Natural Land Use';'for  -  [for_SL]  Forest';'dev  -  [dev_SL]  Developed"],
        'Slope_grid' : [rasters.Slope], 
        'Slope_threshold': ['3'], 
        'processingCellSize' : ['30'],
        'optionalFieldGroups' : ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'"], 
        'Reduce_land_cover_grid_to_smallest_recommended_size' : ['false']
    }
class NP_options:
    testInputs = {
        'inLandCoverGrid' : [rasters.NLCD_2016],
        'metricsToRun' : ["NI  -  [NI_Prox]  All Natural Land Use"],
        'Neighborhood_width': ["20"],
        'Burn_in_areas_of_excluded_values': ['true', 'false'], 
        'Burn_in_value': ["-99999"], 
        'Minimum_visible_patch_size': ["5"], 
        'Create_zone_raster': ['true'],
        'Zone_proportion_bins': ["10"], 
        'Overwrite_existing_outputs': ['true'], 
        'optionalFieldGroups': [ "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"]    
    }
class PM_options:
    testInputs = {
        'inReportingUnitFeature' : [polygons.Watersheds],
        'reportingUnitIdField' : ['HUC_12'], 
        'inLandCoverGrid' : [rasters.NLCD_2016], 
        'metricsToRun' : ["for  -  [for_PLGP]  Forest"],
        'Minimum_patch_size': ["10"], 
        'Maximum_separation' : ["5"], 
        'MDCP': ["true"], 
        'processingCellSize' : ['30'],
        'optionalFieldGroups' : ["'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"],
        'ReduceLandGridToSmallSize' : ['true']
    }
class FLCV_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'], 
    'inLandCoverGrid' : [rasters.NLCD_2016],
    'metricsToRun' : ["for  -  [for_Low]  Forest"],
    'Facility_feature': [points.SampleSites], 
    'View_radius': ["250 Meters"], 
    'View_threshold': ["5"], 
    'processingCellSize' : ['30'],
    'optionalFieldGroups': ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]   
    }
class ID_options: 
    testInputs = {
    'Road_feature': [lines.Roads], 
    'Merge_divided_roads': ['false'], 
    'Merge_field': [""], 
    'Merge_distance': ["10 Meters"], 
    'Output_Coordinate_System': ["PROJCS['Albers_Conical_Equal_Area',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['false_easting',0.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-96.0],PARAMETER['standard_parallel_1',29.5],PARAMETER['standard_parallel_2',45.5],PARAMETER['latitude_of_origin',23.0],UNIT['Meter',1.0]]"], 
    'Density_raster_cell_size': ["10"], 
    'Density_raster_search_radius': ["750"], 
    'Density_raster_area_units': ["SQUARE KILOMETERS"], 
    'optionalFieldGroups': ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]   
    }
class LCCC_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'], 
    'inLandCoverGrid' : [rasters.NLCD_2016],
    'metricsToRun' : ["IMPERVIOUS  -  [PCTIA]  Percent Cover Total Impervious Area';'NITROGEN  -  [N_Load]  Estimated Nitrogen Loading Based on Land Cover';'PHOSPHORUS  -  [P_Load]  Estimated Phosphorus Loading Based on Land Cover", 
                      "PHOSPHORUS  -  [P_Load]  Estimated Phosphorus Loading Based on Land Cover"],
    'processingCellSize' : ['30'],
    'optionalFieldGroups' : [ "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"]
    }
class PAAA_options: 
    testInputs = {
        'Park_feature' : [polygons.ThreeParks], 
        'Dissolve_parks': ["false"], 
        'Cost_surface_raster' : [rasters.Walkable_Cost_Surface], 
        'Population_feature' : [rasters.Population_Raster], 
        'Population_field': ["Pop"], 
        'Maximum_travel_distance': ["800"], 
        'Expand_area_served' : ["8"], 
        'processingCellSize' : ["30"],
        'optionalFieldGroups' : ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"]
    }  
class PDM_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'], 
    'Census_feature' : [polygons.Census2010], 
    'Population_field' : ['Pop'], 
    'POPCHG' : ["true"], 
    'Census_T2_feature': [polygons.Census2020], 
    'Population_T2_field' : ['P0010001'], 
    'optionalFieldGroups' : ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"]
    }
class PIFM_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'Population_feature' : [polygons.Census2010], 
    'Population_field' : ['Pop'],
    'FLoodplain_feature' : [rasters.Floodplain_Raster], 
    'optionalFieldGroups' : ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"]
    
     }
class PLCV_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'], 
    'inLandCoverGrid' : [rasters.NLCD_2016], 
    'metricsToRun' : ["for  -  [for_PV_C]  Forest';'agr  -  [agr_PV_C]  Agriculture';'dev  -  [dev_PV_C]  Developed"], 
    'View_radius' : ["9"], 
    'Minimum_visible_patch_size' : ["4"], 
    'Population_raster' : [rasters.Population_Raster], 
    'processingCellSize' : ["30"],
    'optionalFieldGroups' : ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    }
class PWZM_options: 
    testInputs = [{
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'Population_feature' : [rasters.Population_Raster], 
    'Population_field' : ['Pop'],
    'Zone_feature' : [polygons.WaterPolygons], 
    'Buffer_distance' : ["1 Kilometers"],
    'Group_by_zone' : ["false"],
    'Zone_ID_field' : ["fcode"],
    'optionalFieldGroups' : ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    
     }]
class RD_options:
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'Road_feature' : [lines.Roads], 
    'Road_class_field' : [""],
    'STXRD' : ["true"], 
    'RNS' : ["true"], 
    'Stream_feature' : [lines.StreamLines], 
    'Buffer_distance' : ["60 Meters"], 
    'optionalFieldGroups' : ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    }
class FLCP_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'inLandCoverGrid' : [rasters.NLCD_2016],
    'metricsToRun' : ["wtl  -  [fwtl]  Wetland';'dev  -  [fdev]  Developed';'agr  -  [fagr]  Agriculture"], 
    'Floodplain_feature' : [rasters.Floodplain_Raster], 
    'processingCellSize' : ['30'],
    'optionalFieldGroups' : ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'" #16
                                ], 
    'Reduce_land_cover_grid_to_smallest_recommended_size' : ['false']
    }
class RLCP_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'inLandCoverGrid' : [rasters.NLCD_2016],
    'metricsToRun' : ["UI  -  [rUI]  All Human Land Use';'agr  -  [ragr]  Agriculture';'for  -  [rfor]  Forest"],
    'Stream_features' : [(f"{lines.StreamLines};{polygons.StreamPolygons};{polygons.WaterPolygons}")], 
    'Buffer_distance' : ["45 Meters"], 
    'Enforce_reporting_unit_boundaries' : ["true"], 
    'processingCellSize' : ['30'],
    'optionalFieldGroups' : ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'" #16
                                ]
    }
class SPLCP_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'inLandCoverGrid' : [rasters.NLCD_2016],
    'metricsToRun' : ["for  -  [sfor]  Forest';'dev  -  [sdev]  Developed';'agr  -  [sagr]  Agriculture"],
    'Sample_point_features' : [points.SampleSites], 
    'Reporting_unit_link_field' : ['HUC_12'], 
    'Buffer_distance' : ["500 Meters"], 
    'Enforce_reporting_unit_boundaries' : ["true"], 
    'processingCellSize' : ['30'],
    'optionalFieldGroups' : ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'" #16
                                ]
    }
class SDM_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'Stream_feature' : [lines.WaterLines],
    'Stream_order_field' : [""],
    'optionalFieldGroups' : ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    }
class PRFEA_options: 
    testInputs = {
    'Version' : ["ESRI StreetMap"], 
    'Walkable_roads' : ["true"],
    'Intersection_density_roads' : ["true"],
    'Interstates_arterials_and_collectors' : ["true"], 
    'All_roads' : ["true"],  
    'optionalFieldGroups' : ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"] 
    }
class CWCR_options: 
    testInputs = {
        'Walkable_features' : [lines.Roads_Walkable], 
        'Impassable_features' : [(f"{lines.StreamLines};{polygons.StreamPolygons}")], 
        'Maximum_travel_distance':["800"], 
        'Walk_value' : ["1"], 
        'Base_value' : ["10"], 
        'Density_raster_cell_size' : ["30"], 
        'Snap_raster' : [rasters.DASY_Population], 
        'optionalFieldGroups' : ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    }
class IOP_options: 
    testInputs = {
        'Input_polygon_features' : [polygons.Parks],
        'Check_for_overlaps_only' : ["true"]
    }
class SZS_options: 
    testInputs = [{
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'Input_value_raster' : [rasters.NLCD_2016], 
    'Statistics_type' : ["MINORITY;MAJORITY_COUNT;MINORITY_COUNT;RANGE"], 
    'Field_prefix' : ["SZSTest1"],
    'optionalFieldGroups' : ["'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"
                            ]
     }]
class PNHD_options: 
    testInputs = {
        'Single_or_multiple_files' : ["Single geodatabase"],
        'Geodatabase_file' : [setup.NHD_H_0509_HUC4], 
        'Geodatabase_folder' : [setup.NHD_HR_multi], 
        'Geodatase_file_filter' : ["NHD_H_*"], 
        'Single_shapefile_folder' : [setup.NHD_Shapefile_folder], 
        'Multiple_shapefiles_folder': [setup.NHD_plus],
        'Shapefile_folder_filter' : ["NHD*"], 
        'optionalFieldGroups' : [""
                            ]
    }
