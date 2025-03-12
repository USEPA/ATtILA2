from parameters import *
class LCP_options: 
    testInputs = {
        'inReportingUnitFeature' : [polygons.Watersheds], 
        'reportingUnitIdField' : ['HUC_12'], 
        'inLandCoverGrid' : [rasters.NLCD_2016], 
        'metricsToRun' : ["tun  -  [ptun]  Tundra';'wtlw  -  [pwtlw]  Woody Wetland';'UI  -  [UINDEX]  All Human Land Use",
                          "agr  -  [pagr]  Agriculture"],
        'perCapitaYN' : ['false', 'true'],
        'inCensusDataset' : [polygons.Census2010],
        'inPopField' : ['Pop'], 
        'processingCellSize' : ['30'], 
        'optionalFieldGroups' : [ " ",
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                                 "'QAFIELDS  -  Add Quality Assurance Fields'",
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'", 
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                                 "'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'",
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"]
    }
class CAEM_options: 
    testInputs = {
        'inReportingUnitFeature' : [polygons.Watersheds], 
        'reportingUnitIdField' : ['HUC_12'], 
        'inLandCoverGrid' : [rasters.NLCD_2016],
        'metricsToRun' : ["for  -  [for_E2A]  Forest';'devm  -  [devm_E2A]  Medium Intensity Developed';'NI  -  [NI_E2A]  All Natural Land Use"],
        'Edge_width' : ['5','50'], 
        'processingCellSize' : ['30'],
        'optionalFieldGroups' : [ " ",
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                                 "'QAFIELDS  -  Add Quality Assurance Fields'",
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'", 
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                                 "'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'",
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"],
        'ReduceLandGridToSmallSize' : ['false','true']
    }   
class LCD_options: 
    testInputs = {
        'inReportingUnitFeature' : [polygons.Census2010], 
        'reportingUnitIdField' : ['COUNTY'], 
        'inLandCoverGrid' : [rasters.NLCD_2016],
        'processingCellSize' : ['30'],
        'optionalFieldGroups' : [ " ",
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                                 "'QAFIELDS  -  Add Quality Assurance Fields'",
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'", 
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                                 "'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'",
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"]
    }
class LCOSP_options: 
    testInputs = {
        'inReportingUnitFeature' : [polygons.Watersheds], 
        'reportingUnitIdField' : ['HUC_12'], 
        'inLandCoverGrid' : [rasters.NLCD_2016],
        'metricsToRun' : ["agr  -  [agr_SL]  Agriculture';'NI  -  [NI_SL]  All Natural Land Use';'for  -  [for_SL]  Forest';'dev  -  [dev_SL]  Developed"],
        'Slope_grid' : [rasters.Slope], 
        'Slope_threshold': ['40'], 
        'processingCellSize' : ['30'],
        'optionalFieldGroups' : [
                                " ", #1
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", #2
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", #3
                                "'QAFIELDS  -  Add Quality Assurance Fields'", #4
                                "'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #5
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'" #6
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", #7
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #8
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'", #9
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #10
                                "'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'; 'QAFIELDS  -  Add Quality Assurance Fields'", #11
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'", #12
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #13
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #14
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields; AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #15
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'" #16
                                ], 
        'Reduce_land_cover_grid_to_smallest_recommended_size' : ['false','true']
    }
class NP_options:
    testInputs = {
        'inLandCoverGrid' : [rasters.NLCD_2016],
        'metricsToRun' : ["NI  -  [NI_Prox]  All Natural Land Use';'agr  -  [agr_Prox]  Agriculture';'for  -  [for_Prox]  Forest"],
        'Neighborhood_width': ["20"],
        'Burn_in_areas_of_excluded_values': ['true', 'false'], 
        'Burn_in_value': ["-99999"], 
        'Minimum_visible_patch_size': ["5"], 
        'Create_zone_raster': ['true', 'false'],
        'Zone_proportion_bins': ["10"], 
        'Overwrite_existing_outputs': ['true', 'false'], 
        'optionalFieldGroups': [ " ",
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                                 ]    
    }
class PM_options:
    testInputs = {
        'inReportingUnitFeature' : [polygons.Watersheds],
        'reportingUnitIdField' : ['HUC_12'], 
        'inLandCoverGrid' : [rasters.NLCD_2016], 
        'metricsToRun' : ["for  -  [for_PLGP]  Forest';'UI  -  [UI_PLGP]  All Human Land Use';'agr  -  [agr_PLGP]  Agriculture';'dev  -  [dev_PLGP]  Developed"],
        'Minimum_patch_size': ["10"], 
        'Maximum_separation' : ["5"], 
        'MDCP': ["false", "true"], 
        'processingCellSize' : ['30'],
        'optionalFieldGroups' : [ " ",
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                                 "'QAFIELDS  -  Add Quality Assurance Fields'",
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'", 
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                                 "'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'",
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"],
        'ReduceLandGridToSmallSize' : ['false','true']
    }
class FLCV_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'], 
    'inLandCoverGrid' : [rasters.NLCD_2016],
    'metricsToRun' : ["for  -  [for_Low]  Forest';'dev  -  [dev_Low]  Developed';'UI  -  [UI_Low]  All Human Land Use"],
    'Facility_feature': [points.SampleSites], 
    'View_radius': ["60 Meters"], 
    'View_threshold': ["15"], 
    'processingCellSize' : ['30'],
    'optionalFieldGroups': [ " ",
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                            "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]   
    }
class ID_options: 
    testInputs = {
    'Road_feature': [lines.Roads], 
    'Merge_divided_roads': ['false', 'true'], 
    'Merge_field': [""], 
    'Merge_distance': ["10 Meters"], 
    'Output_Coordinate_System': ["PROJCS['Albers_Conical_Equal_Area',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['false_easting',0.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-96.0],PARAMETER['standard_parallel_1',29.5],PARAMETER['standard_parallel_2',45.5],PARAMETER['latitude_of_origin',23.0],UNIT['Meter',1.0]]"], 
    'Density_raster_cell_size': ["10"], 
    'Density_raster_search_radius': ["1500"], 
    'Density_raster_area_units': ["SQUARE KILOMETERS"], 
    'optionalFieldGroups': [" ",
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                            "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
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
    'optionalFieldGroups' : [ " ",
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                                 "'QAFIELDS  -  Add Quality Assurance Fields'",
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'", 
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                                 "'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'",
                                 "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'; 'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"]
    }
class PAAA_options: 
    testInputs = {
        'Park_feature' : [polygons.Parks], 
        'Dissolve_parks': ["true", "false"], 
        'Cost_surface_raster' : [rasters.Walkable_Cost_Surface], 
        'Population_feature' : [rasters.Population_Raster, polygons.Census2010], 
        'Population_field': ["Pop"], 
        'Maximum_travel_distance': ["5"], 
        'Expand_area_served' : ["10"], 
        'processingCellSize' : ["30"],
        'optionalFieldGroups' : [" ",
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                            "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    }  
class PDM_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'], 
    'Census_feature' : [polygons.Census2010], 
    'Population_field' : ['Pop'], 
    'POPCHG' : ["false", "true"], 
    'Census_T2_feature': [polygons.Census2020], 
    'Population_T2_field' : ['P0010001'], 
    'optionalFieldGroups' : [" ",
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                            "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    }
class PIFM_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'Population_feature' : [rasters.Population_Raster, polygons.Census2010], 
    'Population_field' : ['Pop'],
    'FLoodplain_feature' : [rasters.Floodplain_NLCD, polygons.Floodplain_Polygons], 
    'optionalFieldGroups' : [" ",
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                            "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    
     }
class PLCV_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'], 
    'inLandCoverGrid' : [rasters.NLCD_2016], 
    'metricsToRun' : ["for  -  [for_PV_C]  Forest';'agr  -  [agr_PV_C]  Agriculture';'dev  -  [dev_PV_C]  Developed"], 
    'View_radius' : ["60"], 
    'Minimum_visible_patch_size' : ["5"], 
    'Population_raster' : [rasters.Population_Raster], 
    'processingCellSize' : ["30"],
    'optionalFieldGroups' : [" ",
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                            "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    }
class PWZM_options: 
    testInputs = [{
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'Population_feature' : [rasters.Population_Raster, polygons.Census2010], 
    'Population_field' : ['Pop'],
    'Zone_feature' : [polygons.WaterPolygons], 
    'Buffer_distance' : ["1 Kilometers"],
    'Group_by_zone' : ["true", "false"],
    'Zone_ID_field' : ["fcode"],
    'optionalFieldGroups' : [" ",
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                            "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    
     },  
     {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'Population_feature' : [rasters.Population_Raster, polygons.Census2010], 
    'Population_field' : ['Pop'],
    'Zone_feature' : [rasters.Floodplain_Raster], 
    'Buffer_distance' : ["1 Kilometers"],
    'Group_by_zone' : ["true", "false"],
    'Zone_ID_field' : ["Value"],
    'optionalFieldGroups' : [" ",
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                            "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    
     }]
class RD_options:
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'Road_feature' : [lines.Roads], 
    'Road_class_field' : ["", "FUNC_CLASS"],
    'STXRD' : ["true", "false"], 
    'RNS' : ["true", "false"], 
    'Stream_feature' : [lines.StreamLines], 
    'Buffer_distance' : ["20 Meters"], 
    'optionalFieldGroups' : [" ",
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                            "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    }
class FLCP_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'inLandCoverGrid' : [rasters.NLCD_2016],
    'metricsToRun' : ["wtl  -  [fwtl]  Wetland';'dev  -  [fdev]  Developed';'agr  -  [fagr]  Agriculture"], 
    'Floodplain_feature' : [polygons.Floodplain_Polygons, rasters.Floodplain_Raster], 
    'processingCellSize' : ['30'],
    'optionalFieldGroups' : [
                                " ", #1
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", #2
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", #3
                                "'QAFIELDS  -  Add Quality Assurance Fields'", #4
                                "'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #5
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'" #6
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", #7
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #8
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'", #9
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #10
                                "'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'; 'QAFIELDS  -  Add Quality Assurance Fields'", #11
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'", #12
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #13
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #14
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields; AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #15
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'" #16
                                ], 
    'Reduce_land_cover_grid_to_smallest_recommended_size' : ['false','true']
    }
class RLCP_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'inLandCoverGrid' : [rasters.NLCD_2016],
    'metricsToRun' : ["UI  -  [rUI]  All Human Land Use';'agr  -  [ragr]  Agriculture';'for  -  [rfor]  Forest"],
    'Stream_features' : [("{0};{1};{2}".format(lines.StreamLines, polygons.StreamPolygons, polygons.WaterPolygons)), polygons.StreamPolygons, lines.StreamLines], 
    'Buffer_distance' : ["45 Meters"], 
    'Enforce_reporting_unit_boundaries' : ["true", "false"], 
    'processingCellSize' : ['30'],
    'optionalFieldGroups' : [
                                " ", #1
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", #2
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", #3
                                "'QAFIELDS  -  Add Quality Assurance Fields'", #4
                                "'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #5
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'" #6
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", #7
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #8
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'", #9
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #10
                                "'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'; 'QAFIELDS  -  Add Quality Assurance Fields'", #11
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'", #12
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #13
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #14
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields; AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #15
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'" #16
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
    'Buffer_distance' : ["30 Meters"], 
    'Enforce_reporting_unit_boundaries' : ["true", "false"], 
    'processingCellSize' : ['30'],
    'optionalFieldGroups' : [
                                " ", #1
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", #2
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", #3
                                "'QAFIELDS  -  Add Quality Assurance Fields'", #4
                                "'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #5
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'" #6
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", #7
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #8
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation';'QAFIELDS  -  Add Quality Assurance Fields'", #9
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #10
                                "'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'; 'QAFIELDS  -  Add Quality Assurance Fields'", #11
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'", #12
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #13
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #14
                                "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields; AREAFIELDS  -  Add Area Fields for All Land Cover Classes'", #15
                                "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'; 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'; 'QAFIELDS  -  Add Quality Assurance Fields'; 'AREAFIELDS  -  Add Area Fields for All Land Cover Classes'" #16
                                ]
    }
class SDM_options: 
    testInputs = {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'Stream_feature' : [lines.WaterLines],
    'Stream_order_field' : ["streamorde", ""],
    'optionalFieldGroups' : [" ",
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                            "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    }
class PRFEA_options: 
    testInputs = {
    'Version' : ["NAVTEQ 2011", "NAVTEQ 2019", "ESRI StreetMap"], 
    'Walkable_roads' : ["","true"],
    'Intersection_density_roads' : ["","true"],
    'Interstates_arterials_and_collectors' : ["","true"], 
    'All_roads' : ["","true"],  
    'optionalFieldGroups' : [" ",
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"] 
    }
class CWCR_options: 
    testInputs = {
        'Walkable_features' : [lines.Roads_Walkable], 
        'Impassable_features' : [("{0};{1}".format(lines.StreamLines, polygons.StreamPolygons)), lines.Roads_NonWalkable], 
        'Maximum_travel_distance':["300"], 
        'Walk_value' : ["1"], 
        'Base_value' : ["2"], 
        'Density_raster_cell_size' : ["30"], 
        'Snap_raster' : [rasters.NLCD_2016], 
        'optionalFieldGroups' : [" ",
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'", 
                            "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'", 
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation';'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    }
class IOP_options: 
    testInputs = {
        'Input_polygon_features' : [polygons.Floodplain_Polygons, polygons.Parks],
        'Check_for_overlaps_only' : ["true", "false"]
    }
class SZS_options: 
    testInputs = [{
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'Input_value_raster' : [rasters.NLCD_2016], 
    'Statistics_type' : ["MINORITY;MAJORITY_COUNT;MINORITY_COUNT;RANGE"], 
    'Field_prefix' : ["SZSTest1"],
    'optionalFieldGroups' : [" ",
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"
                            ]
     },  
     {
    'inReportingUnitFeature' : [polygons.Watersheds],
    'reportingUnitIdField' : ['HUC_12'],
    'Input_value_raster' : [rasters.DASY_Population], 
    'Statistics_type' : ["ALL;MIN;MAX;RANGE;MEAN;STD;SUM;PCT90"],
    'Zone_feature' : ["ALL;MIN;MAX;RANGE;MEAN;STD;SUM;PCT90"], 
    'Field_prefix' : ["SZSTest2"],
    'optionalFieldGroups' : [" ",
                            "'LOGFILE  -  Record Process Steps Taken During Metric Calculation'"
                            ]
     }]
class PNHD_options: 
    testInputs = {
        'Single_or_multiple_files' : ["Multiple geodatabases", "Single geodatabase", "Multiple shapefiles", "Single shapefile"],
        'Geodatabase_file' : [setup.NHD_H_0509_HUC4], 
        'Geodatabase_folder' : [setup.NHD_HR_multi], 
        'Geodatase_file_filter' : ["NHD_H_*"], 
        'Single_shapefile_folder' : [setup.NHD_Shapefile_folder], 
        'Multiple_shapefiles_folder': [setup.NHD_plus],
        'Shapefile_folder_filter' : ["NHD*"], 
        'optionalFieldGroups' : [" ",
                            "'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'"
                            ]
    }
