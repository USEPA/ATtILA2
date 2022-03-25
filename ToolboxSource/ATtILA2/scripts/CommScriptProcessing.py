""" Land Cover Proportion Metrics

	This script is associated with an ArcToolbox script tool.
	
"""

import os
import sys

from arcgis.features import GeoAccessor, GeoSeriesAccessor
import pandas
import numpy

from pathlib import Path
from ATtILA2 import metric
from ATtILA2.utils import parameters



def addTableToMap(tbl):
	## to do:  wrap in try/except function to make sure in arc and a map exists.
	Project = arcpy.mp.ArcGISProject("CURRENT")
	Map = Project.listMaps()[0]	
	Map.addTable(arcpy.mp.Table(tbl))
	
def addLayerToMap(lyr):
	## to do:  wrap in try/except function to make sure in arc and a map exists.
	Project = arcpy.mp.ArcGISProject("CURRENT")
	Map = Project.listMaps()[0]	
	Map.addDataFromPath(lyr)
	
def EALandCoverPC(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, inPopField, outWorkspace):
	_lccName = 'MULC Blended Levels LAND'
	lccFilePath = os.path.join(lccPath, _lccName + '.xml')
	
	metricsToRun = """mfor  -  [pmfor]  Trees/Forest, Orchards, and Woody Wetlands';'
					  imp  -  [pimp]  Impervious Surface';'
					  green  -  [pgreen]  All Vegetative Areas';'
					  ag  -  [pag]  Agriculture';'
					  wet  -  [pwet]  Wetlands"""
	outTable = os.path.join(outWorkspace, '{0}_LC'.format(output_prefix))
	perCapitaYN = 'true'
	processingCellSize = inLandCoverGrid
	snapRaster = inLandCoverGrid
	optionalFieldGroups = ''

	## -- Run land cover proportions per capita--
	metric.runLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, outTable, 'true', inReportingUnitFeature, inPopField, processingCellSize, snapRaster, optionalFieldGroups)	
					
					
	# if sum of lc stats = 0 then that lc class isn't represented in the dataset. For EA results should be NAN not 0
	f = pandas.DataFrame.spatial.from_table(outTable)
	f.loc[:,f.sum(axis=0)==0] = -888888
		
	# update ATtILA field names to legacy EnviroAtlas field names 
	field_change = { 
	'pmfor': 'MFor_P', 'pimp':'Imp_P', 'pgreen': 'Green_P', 'pag': 'Ag_P',
	'pwet': 'Wet_P', 'mfor_PC': 'MFor_PC', 'imp_PC': 'Imp_PC', 
	'green_PC': 'Green_PC', 'ag_PC': 'Ag_PC', 'wet_PC': 'Wet_PC',
	'mfor_M2': 'MFor_M', 'imp_M2': 'Imp_M', 'green_M2': 'Green_M',
	'ag_M2': 'Ag_M', 'wet_M2': 'Wet_M'}
	f.rename(field_change, axis='columns', inplace=True)
	
	# save table
	f.spatial.to_table(outTable)
	
	addTableToMap(outTable)
	
def EAWaterView(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, inCensusRaster, outWorkspace):
	_lccName = 'MULC Blended Levels ALL'
	lccFilePath = os.path.join(lccPath, _lccName + '.xml')
	
	metricsToRun = 'wtr  -  [pwtr]  Water'
	viewRadius = '50'
	minPatchSize = '300'
	
	outTable = os.path.join(outWorkspace, '{0}_WVs'.format(output_prefix))
	processingCellSize = inLandCoverGrid
	snapRaster = inLandCoverGrid
	optionalFieldGroups = ''
	
	metric.runPopulationLandCoverViews(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, viewRadius, minPatchSize, inCensusRaster, outTable, processingCellSize, 
				 snapRaster, optionalFieldGroups)
	
	# update ATtILA field names to legacy EnviroAtlas field names 
	f = pandas.DataFrame.spatial.from_table(outTable)
	field_change = {'wtr_WVPOP50': 'WVW_Pop', 'wtr_WVPCT50':'WVW_Pct'}
	f.rename(field_change, axis='columns', inplace=True)
	f = f[['bgrp', 'WVW_Pop', 'WVW_Pct']].reset_index()
	
	# save table
	f.spatial.to_table(outTable)
	
	addTableToMap(outTable)
	
	
	
def EATreeView(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, inCensusRaster, outWorkspace):
	
	_lccName = 'MULC Blended Levels ALL'
	lccFilePath = os.path.join(lccPath, _lccName + '.xml')
	
	metricsToRun = """mfor  -  [pmfor]  Trees/Forest, Orchards, and Woody Wetlands"""
	viewRadius = '50'
	minPatchSize = '1'
	outTable = os.path.join(outWorkspace, '{0}_TreeVs'.format(output_prefix))
	processingCellSize = inLandCoverGrid
	snapRaster = inLandCoverGrid
	optionalFieldGroups = ''
	
	metric.runPopulationLandCoverViews(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName,				lccFilePath, metricsToRun, viewRadius, minPatchSize, inCensusRaster, outTable, processingCellSize, 
				 snapRaster, optionalFieldGroups)			
	
	
	# update ATtILA field names to legacy EnviroAtlas field names 
	f = pandas.DataFrame.spatial.from_table(outTable)
	field_change = {'mfor_WOVPOP50': 'WVT_Pop', 'mfor_WOVPCT50':'WVT_Pct'}
	f.rename(field_change, axis='columns', inplace=True)
	f = f[['bgrp', 'WVT_Pop', 'WVT_Pct']].reset_index()
	
	# save table
	f.spatial.to_table(outTable)
	
	addTableToMap(outTable)


def EAGreenProx(inReportingUnitFeature, inLandCoverGrid, outWorkspace):
	
	_lccName = 'MULC Blended Levels LAND'
	lccFilePath = os.path.join(lccPath, _lccName + '.xml')
	
	metricsToRun = 'green  -  [pgreen]  All Vegetative Areas'
	inNeighborhoodSize = 251
	burnIn = 'true'
	burnInValue = '1'
	minPatchSiz = '300'
	createZones = ''
	zoneBin_str = ''
	overWrite = 1
	optionalFieldGroups = ''
	
	
	
	metric.runNeighborhoodProportions(inLandCoverGrid, _lccName, lccFilePath, metricsToRun,
						  inNeighborhoodSize, burnIn, burnInValue, minPatchSiz, 
						  createZones, zoneBin_str, overWrite,
						  outWorkspace, optionalFieldGroups)
	
	

def EAImpProx(inReportingUnitFeature, inLandCoverGrid, outWorkspace):
	
	_lccName = 'MULC Blended Levels LAND'
	lccFilePath = os.path.join(lccPath, _lccName + '.xml')
	
	metricsToRun = 'imp  -  [pimp]  Impervious Surface'
	inNeighborhoodSize = 1001
	burnIn = 'true'
	burnInValue = '-99999'
	minPatchSiz = '300'
	createZones = ''
	zoneBin_str = ''
	overWrite = 1
	optionalFieldGroups = ''
	
	
	metric.runNeighborhoodProportions(inLandCoverGrid, _lccName, lccFilePath, metricsToRun,
						  inNeighborhoodSize, burnIn, burnInValue, minPatchSiz, 
						  createZones, zoneBin_str, overWrite,
						  outWorkspace, optionalFieldGroups)

def EASchoolViews(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, inFacilityFeature, scratchWorkspace, outWorkspace, outFileName):
	_lccName = 'MULC Blended Levels LAND'
	lccFilePath = os.path.join(lccPath, _lccName + '.xml')
	
	metricsToRun = 'green  -  [pgreen]  All Vegetative Areas'
	viewRadius = '100 Meters'
	viewThreshold = '1'
	outTable = os.path.join(scratchWorkspace, outFileName)
	processingCellSize = inLandCoverGrid
	snapRaster = inLandCoverGrid
	optionalFieldGroups = ''
	
	metric.runFacilityLandCoverViews(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath,
					 metricsToRun, inFacilityFeature, viewRadius, viewThreshold, outTable, processingCellSize, 
					 snapRaster, optionalFieldGroups)
	
	bg_df = pandas.DataFrame.spatial.from_featureclass(inReportingUnitFeature)
	bg_df = bg_df[[reportingUnitIdField]]
	
	sch_df = pandas.DataFrame.spatial.from_table(outTable)
	bg_df = bg_df.merge(sch_df, how='left', on=reportingUnitIdField)
	
	bg_df['Low_green1'] = bg_df['Low_green1'].fillna(-99999)
	bg_df['FAC_Count'] = bg_df['FAC_Count'].fillna(0)
	
	field_change = {}
	if outFileName == 'DayCare':
		field_change = { 'FAC_Count': 'Day_Count', 'green_fLow':'Day_Low'}
	elif outFileName == 'K12':
		field_change = { 'FAC_Count': 'K12_Count', 'green_fLow':'K12_Low'}
	bg_df.rename(field_change, axis='columns', inplace=True)
		
	outTable = os.path.join(outWorkspace, '{0}_{1}'.format(output_prefix, outFileName))
	bg_df.spatial.to_table(outTable)
		
	addTableToMap(outTable)

def EAFloodplainPrep(inReportingUnitFeature, inFloodplainDataset, scratchWorkspace, hazard='1PCT ANNUAL CHANCE FLOOD HAZARD'):
	
	dictFEMA = {
		'_ ': 'UNKNOWN',
		'A99_ ':'1PCT ANNUAL CHANCE FLOOD HAZARD',
		'A_ ':'1PCT ANNUAL CHANCE FLOOD HAZARD',
		'AE_ ':'1PCT ANNUAL CHANCE FLOOD HAZARD',
		'AH_ ':'1PCT ANNUAL CHANCE FLOOD HAZARD',
		'AO_ ':'1PCT ANNUAL CHANCE FLOOD HAZARD',
		'D_ ':'AREA OF UNDETERMINED FLOOD HAZARD',
		'V_ ':'1PCT ANNUAL CHANCE FLOOD HAZARD',
		'VE_ ':'1PCT ANNUAL CHANCE FLOOD HAZARD',
		'A_1 PCT ANNUAL CHANCE FLOOD HAZARD CONTAINED IN CHANNEL': 'AREA OF MINIMAL FLOOD HAZARD',
		'A_ADMINISTRATIVE FLOODWAY':'REGULATORY FLOODWAY',
		'AE_1 PCT ANNUAL CHANCE FLOOD HAZARD CONTAINED IN CHANNEL':'1PCT ANNUAL CHANCE FLOOD HAZARD',
		'AE_1 PCT ANNUAL CHANCE FLOOD HAZARD CONTAINED IN STRUCTURE':'1PCT ANNUAL CHANCE FLOOD HAZARD',
		'AE_1 PCT CONTAINED IN STRUCTURE, FLOODWAY': 'REGULATORY FLOODWAY',
		'AE_1 PCT CONTAINED IN STRUCTURE, COMMUNITY ENCROACHMENT': 'REGULATORY FLOODWAY',
		'AE_ADMINISTRATIVE FLOODWAY':'ADMINISTRATIVE FLOODWAY',
		'AE_AREA OF SPECIAL CONSIDERATION':'SPECIAL FLOODWAY',
		'AE_COLORADO RIVER FLOODWAY':'SPECIAL FLOODWAY',
		'AE_AE': 'AREA OF MINIMAL FLOOD HAZARD',
		'AE_FLOODWAY':'REGULATORY FLOODWAY',
		'AE_FLOODWAY CONTAINED IN CHANNEL':'REGULATORY FLOODWAY',
		'AE_FLOODWAY CONTAINED IN STRUCTURE':'REGULATORY FLOODWAY',
		'AE_COMMUNITY ENCROACHMENT AREA': 'FLOODWAY',
		'AE_STATE ENCROACHMENT AREA': 'AREA OF MINIMAL FLOOD HAZARD',
		'AO_FLOODWAY': 'FLOODWAY',
		'NP_ ': 'UNKNOWN',
		'X_1 PCT FUTURE CONDITIONS, FLOODWAY':'FUTURE CONDITIONS 1PCT ANNUAL CHANCE FLOOD HAZARD',
		'AH_FLOODWAY':'FLOODWAY',
		'VE_RIVERINE FLOODWAY SHOWN IN COASTAL ZONE':'REGULATORY FLOODWAY',
		'X_0.2 PCT ANNUAL CHANCE FLOOD HAZARD':'0.2PCT ANNUAL CHANCE FLOOD HAZARD',
		'X_0.2 PCT ANNUAL CHANCE FLOOD HAZARD CONTAINED IN CHANNEL':'0.2PCT ANNUAL CHANCE FLOOD HAZARD',
		'X_0.2 PCT ANNUAL CHANCE FLOOD HAZARD CONTAINED IN STRUCTURE': 'AREA OF MINIMAL FLOOD HAZARD',
		'X_1 PCT DEPTH LESS THAN 1 FOOT':'OUTSIDE OF ANNUAL CHANCE FLOOD HAZARD',
		'X_AREA OF MINIMAL FLOOD HAZARD':'AREA OF MINIMAL FLOOD HAZARD',
		'X_AREA WITH REDUCED FLOOD RISK DUE TO LEVEE':'AREA WITH REDUCED RISK DUE TO LEVEE',
		'X_1 PCT DRAINAGE AREA LESS THAN 1 SQUARE MILE': 'AREA OF MINIMAL FLOOD HAZARD',
		'X_1 PCT FUTURE CONDITIONS':'FUTURE CONDITIONS 1PCT ANNUAL CHANCE FLOOD HAZARD',
		'X_1 PCT FUTURE CONDITIONS, COMMUNITY ENCROACHMENT': 'COMMUNITY ENCROACHMENT',
		'X_1 PCT CONTAINED IN STRUCTURE, COMMUNITY ENCROACHMENT': '1 PCT CONTAINED IN STRUCTURE, COMMUNITY ENCROACHMENT',
		'X_1 PCT CONTAINED IN STRUCTURE, FLOODWAY': '1 PCT CONTAINED IN STRUCTURE, FLOODWAY',
		'X_1 PCT FUTURE IN STRUCTURE, FLOODWAY': '1 PCT FUTURE IN STRUCTURE, FLOODWAY',
		'X_1 PCT FUTURE IN STRUCTURE, COMMUNITY ENCROACHMENT': '1 PCT FUTURE IN STRUCTURE, COMMUNITY ENCROACHMENT',
		'X_1 PCT FUTURE CONDITIONS CONTAINED IN STRUCTURE': 'AREA OF MINIMAL FLOOD HAZARD',
		'X_AREA OF SPECIAL CONSIDERATION': 'AREA OF SPECIAL CONSIDERATION',
		'AREA NOT INCLUDED_ ':'AREA NOT INCLUDED',
		'OPEN WATER_ ':'OPEN WATER'
		}
		
	# femaLayer = arcpy.MakeFeatureLayer_management("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer/0", 
												 # 'temp_fema')
		
	##Clip to boundary
	temp_dissolve = r"in_memory\temp_dissolve"
	arcpy.Dissolve_management(inReportingUnitFeature, temp_dissolve)
	
	## project and clip 
	temp_flood = os.path.join(scratchWorkspace, 'temp_flood')
	arcpy.Clip_analysis(inFloodplainDataset, temp_dissolve, temp_flood)
	out_flood = os.path.join(scratchWorkspace, 'temp_flood_proj')
	arcpy.Project_management(temp_flood, out_flood, arcpy.Describe(inReportingUnitFeature).SpatialReference)
	
	
	df = pandas.DataFrame.spatial.from_featureclass(out_flood)
	df['ZONE_SUBTY'].fillna(' ', inplace=True)
	df['FLDSUBTY'] = df['FLD_ZONE'] + '_' + df['ZONE_SUBTY']
	df['FLDSUBTY'] = df["FLDSUBTY"].apply(lambda x: dictFEMA.get(x))
	df['VALUE'] = df['FLDSUBTY'].apply(lambda x: 25 if x == hazard else 1)
	
	df[df['FLDSUBTY'] == hazard][['OBJECTID', 'FLDSUBTY', 'VALUE', 'SHAPE']].spatial.to_featureclass(out_flood)
	
	## select floodplain and export
	# df['VALUE'] = df['esri_symbology'].apply(lambda x: 25 if x == '1% Annual Chance Flood Hazard' else 1)
	# df[df.VALUE == 1][['OBJECTID', 'FLD_ZONE', 'ZONE_SUBTY', 'VALUE', 'SHAPE']].spatial.to_featureclass(out_flood)
	
	valField = 'VALUE'
	outRaster = os.path.join(scratchWorkspace, 'flood_raster')
	cellSize = 1
	arcpy.FeatureToRaster_conversion(out_flood, valField, outRaster, cellSize)
	
	## To do
	## use Estimated floodplains as values as well 
	
	
def EAFloodplainPop(inReportingUnitFeature, reportingUnitIdField, inCensusRaster, inFloodplainDataset, outWorkspace):
	
	inPopField = ''
	outTable = os.path.join(outWorkspace, '{0}_Flood'.format(output_prefix))
	optionalFieldGroups = ''
	
	metric.runPopulationInFloodplainMetrics(inReportingUnitFeature, reportingUnitIdField, inCensusRaster, inPopField, 
											inFloodplainDataset, outTable, optionalFieldGroups)

	addTableToMap(outTable)
	
def EARiparianBuffers(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, inFlowLineFeatures, inAreaFeatures, inWaterbodyFeatures, scratchWorkspace, outWorkspace):

	default_env = arcpy.env.workspace
	arcpy.env.workspace = scratchWorkspace
	distances = ['15','50']

	_lccName = 'MULC Blended Levels LAND'
	
	lccFilePath = os.path.join(lccPath, _lccName + '.xml')

	metricsToRun = 'for  -  [rfor]  Trees/Forest, and Woody Wetlands; veg  -  [rveg]  Natural Vegetation; imp  -  [rimp]  Impervious Surface'
	enforceBoundary = 'false'
	processingCellSize = '1'
	snapRaster = inLandCoverGrid
	#optionalFieldGroups = 'INTERMEDIATES  -  Retain Intermediate Layers Generated During Metric Calculation'
	optionalFieldGroups = 'QAFIELDS  -  Add Quality Assurance Fields'

	##################################################################################################
	## Prepare NHD
	## Buffer reporting unit area by 5km
	arcpy.Buffer_analysis(inReportingUnitFeature, 'bnd_5km', '5 Kilometers', dissolve_option='ALL')
	
	## Clip and project input features
	arcpy.Clip_analysis(inFlowLineFeatures, 'bnd_5km', 'inFlow_clip')
	arcpy.Project_management('inFlow_clip', 'inFlow_clip_prj', 'bnd_5km')
	
	arcpy.Clip_analysis(inAreaFeatures, 'bnd_5km', 'inArea_clip')
	arcpy.Project_management('inArea_clip', 'inArea_clip_prj', 'bnd_5km')
	
	arcpy.Clip_analysis(inWaterbodyFeatures, 'bnd_5km', 'inWaterbody_clip')
	arcpy.Project_management('inWaterbody_clip', 'inWaterbody_clip_prj', 'bnd_5km')
	
	
	arcpy.Select_analysis('inFlow_clip_prj', 'Flowline_SRC', '"FType" = 334 OR "FType" = 460')
	arcpy.Select_analysis('inFlow_clip_prj', 'Flowline_SRCAP','"FType" = 334 OR "FType" = 460 OR "FType" = 558')
	arcpy.Select_analysis('inArea_clip_prj', 'Area_WLRSR', '"FType" = 484 OR "FType" = 398 OR "FType" = 431 OR "FType" = 460')
	arcpy.Select_analysis('inWaterbody_clip_prj', 'Waterbody_RLPIM', '"FType" = 436 OR "FType" = 390 OR "FType" = 378')


	""" Make Layer Files to use the Select by Location Tool """
	arcpy.MakeFeatureLayer_management('Area_WLRSR', 'Area_Lyr')
	arcpy.MakeFeatureLayer_management('Waterbody_RLPIM', 'Waterbody_Lyr')
		
		
	""" Select hydrologically connected waterbodies and areas and save as new feature classes """
	for t in ['Area', 'Waterbody']:
		arcpy.SelectLayerByLocation_management (t + '_Lyr', 'INTERSECT', 'Flowline_SRCAP')
		arcpy.CopyFeatures_management(t + '_Lyr', t + '_Conn')
		
	# add small buffer to flowlines to convert to polygon
	arcpy.Buffer_analysis('Flowline_SRC', 'Flowline_SRC_1m', '0.01 Meters', 'FULL', 'ROUND', 'ALL')
	
	arcpy.Merge_management(['Flowline_SRC_1m', 'Waterbody_Lyr', 'Area_Lyr'], 'RB_')
	arcpy.Dissolve_management('RB_', 'RB_dissolve')
		
	inStreamFeatures = os.path.join(scratchWorkspace, 'RB_dissolve')
	## Finish Prepare NHD
	##################################################################################################
			
	## start with reporting unit features
	ru_df = pandas.DataFrame.spatial.from_featureclass(inReportingUnitFeature)
	ru_df = ru_df[[reportingUnitIdField]]


	# ## run at 15 and 50 meters
	for d in ['15', '50']:		
		inBufferDistance = '{0} Meters'.format(d)
		outTable = os.path.join(scratchWorkspace, 'RB_Alb_{0}'.format(d))
		metric.runRiparianLandCoverProportions(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, _lccName, lccFilePath, metricsToRun, inStreamFeatures, inBufferDistance, enforceBoundary, outTable, processingCellSize, snapRaster, optionalFieldGroups)
		
		df = pandas.DataFrame.spatial.from_table(outTable)
		ru_df = ru_df.merge(df, how='left', on=reportingUnitIdField)
				
		## fill n/a fields with -99999
		na_fields = ['rfor' + d,'rimp' + d,'rveg' + d]
		ru_df[na_fields] = ru_df[na_fields].fillna(-99999)
		
		# ## Change field names to match legacy EnviroAtlas field names
		field_change = {'rfor' + d: 'RB' + d + '_ForP', 
						'rimp' + d: 'RB' + d + '_ImpP', 
						'rveg' + d: 'RB' + d + '_VegP', 
						'RLCP_EFFA': 'RB' + d + '_LArea',
						'rBUFF' + d: 'RB' + d + '_LABGP'}
		ru_df.rename(field_change, axis='columns', inplace=True)
		ru_df.drop(columns = ['RLCP_EXCA', 'RLCP_OVER', 'RLCP_TOTA'], errors='ignore', inplace=True)

	ru_df.drop(columns=['OBJECTID_x', 'OBJECTID_y'], errors='ignore', inplace=True)
	outTable = os.path.join(outWorkspace, '{0}_RB'.format(output_prefix))
	ru_df.spatial.to_table(outTable)
	ru_df = None

	## Clean up intermediate files
	intermed_files = ['bnd_5km', 'inFlow_clip', 'inFlow_clip_prj',
					  'inArea_clip', 'inArea_clip_prj', 'inWaterbody_clip',
					  'inWaterbody_clip_prj', 'Flowline_SRC', 'Flowline_SRC_1m',
					  'Flowline_SRCAP', 'Area_WLRSR', 'Waterbody_RLPIM', 
					  'Area_Lyr', 'Waterbody_Lyr', 'RB_', 'RB_dissolve',
					  'Area_Conn', 'Waterbody_Conn', 'RB_Alb_15', 'RB_Alb_50']
	for f in intermed_files:
		arcpy.Delete_management(os.path.join(scratchWorkspace, f))
	
	addTableToMap(outTable)
											
def main(_argv):
	# Script arguments
	inputArguments = parameters.getParametersAsText([4, 6, 8, 9, 12])
	
	processesToRun = inputArguments[0]
	inReportingUnitFeature = inputArguments[1]
	reportingUnitIdField = inputArguments[2]
	inPopField = inputArguments[3]
	inLandCoverGrid = inputArguments[4]
	inCensusRaster = inputArguments[5]
	inFlowLineFeatures = inputArguments[6]
	inAreaFeatures = inputArguments[7]
	inWaterbodyFeatures = inputArguments[8]
	daycares = inputArguments[9]
	k12 = inputArguments[10]

	global output_prefix
	output_prefix = inputArguments[11]
	scratchWorkspace = inputArguments[12]
	outWorkspace = inputArguments[13]
	
	arcpy.AddMessage(inputArguments)
	
	global lccPath
	lccPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'LandCoverClassifications')
											 										 
	inFloodplainDataset = r'E:\CommScripts_Testing\Input\Input.gdb\S_Fld_Haz_Ar'
	
	# for process in processesToRun.split("';'"):
	processesToRun = processesToRun.split("';'")
	if 'Land Cover Characteristics' in processesToRun:
		arcpy.AddMessage('*** Start Land Cover Characteristics ***')
		EALandCoverPC(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, inPopField, outWorkspace)
	if 'Riparian Buffers' in processesToRun:
		arcpy.AddMessage('*** Start Riparian Buffers ***')
		EARiparianBuffers(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, inFlowLineFeatures, inAreaFeatures, inWaterbodyFeatures, scratchWorkspace, outWorkspace)
	if 'Greenspace Proximity' in processesToRun:
		arcpy.AddMessage('*** Start Greenspace Proximity ***')
		EAGreenProx(inReportingUnitFeature, inLandCoverGrid, outWorkspace)
	if 'Impervious Proximity' in processesToRun:
		arcpy.AddMessage('*** Start Impervious Proximity ***')
		EAImpProx(inReportingUnitFeature, inLandCoverGrid, outWorkspace)
	if 'Water Views' in processesToRun:
		arcpy.AddMessage('*** Start Water Views ***')
		EAWaterView(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, inCensusRaster, outWorkspace)
	if 'Tree Views' in processesToRun:
		arcpy.AddMessage('*** Start Tree Views ***')
		EATreeView(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, inCensusRaster, outWorkspace)
	if 'Near School' in processesToRun:
		arcpy.AddMessage('*** Start Near School ***')
		EASchoolViews(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, k12, scratchWorkspace, outWorkspace, 'K12')
	if 'Near Daycare' in processesToRun:
		arcpy.AddMessage('*** Start Near Daycare ***')
		EASchoolViews(inReportingUnitFeature, reportingUnitIdField, inLandCoverGrid, daycares, scratchWorkspace, outWorkspace, 'DayCare')
	
	
	
if __name__ == "__main__":

	main(sys.argv)
	



