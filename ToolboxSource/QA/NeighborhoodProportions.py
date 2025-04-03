import traceback, time, arcpy, os, sys, csv, subprocess
import arcpy
import itertools
from arcpy.sa import *
from setupParameters import *
from inputDictionaries import *

#setup ATtILA
arcpy.ImportToolbox(setup.ATtILA_pth) #Nov06 is the toolbox with the new arcpy.env.workspace error message related to the logfile
from ATtILA2 import metric
from ATtILA2.utils import parameters 
from ATtILA2.utils.messages import loopProgress, AddMsg 
from ATtILA2.datetimeutil import DateTimer 
arcpy.AddMessage(' ***Current working directory: {0} ***'.format(os.getcwd()))

arcpy.env.overwriteOutput = 1 #Overwrite outputs
arcpy.CheckOutExtension("Spatial")

toolAbbv = 'NP'
fileName = f'{toolAbbv}{OUTS.fileName}'
toolPath = f'{toolAbbv}{OUTS.toolPath}'
outGDB = f'{toolAbbv}{OUTS.outGDB}'

# Create output workspaces
Output_GDB_pth = os.path.join(setup.outFolder, outGDB)

if not arcpy.Exists(Output_GDB_pth):
  arcpy.management.CreateFileGDB(setup.outFolder, outGDB)

arcpy.AddMessage('Setting up output geodatabase environments')

arcpy.env.workspace = Output_GDB_pth

#Define ATtILA metric
def runATtILA(paramDict, iteration): 
  arcpy.AddMessage(f"\n\n***Starting {toolAbbv}: run {iteration+1} of {len(paramCombosList)}***\n")
  arcpy.AddMessage(f"Test inputs: {paramDict}\n")
  metric.runNeighborhoodProportions(
                              toolPath,
                              paramDict["inLandCoverGrid"],
                              setup._lccName,
                              setup.lccFilePath,
                              paramDict["metricsToRun"],
                              paramDict["Neighborhood_width"],
                              paramDict["Burn_in_areas_of_excluded_values"],
                              paramDict["Burn_in_value"],
                              paramDict["Minimum_visible_patch_size"],
                              paramDict["Create_zone_raster"],
                              paramDict["Zone_proportion_bins"], 
                              paramDict["Overwrite_existing_outputs"],
                              Output_GDB_pth,
                              paramDict["optionalFieldGroups"])

#Build list of possible combinations
paramCombosList = list(itertools.product(*NP_options.testInputs.values()))

failedList = [] #failed list to store failed parameter set dictionaries
loopProgress = loopProgress(len(paramCombosList))
arcpy.AddMessage(f"Testing {len(paramCombosList)} parameter combinations")


for iteration, params in enumerate(paramCombosList): 
  paramDict = dict(zip(NP_options.testInputs.keys(), params))

  try: 
    runATtILA(paramDict, iteration)
  except: 
    AddMsg(f"exception occured using {paramDict}")
    failedList.append(paramDict)
    loopProgress.update()
    continue
  
if failedList == []: 
  arcpy.AddMessage("No errors found")
else: 
  arcpy.AddMessage('\n***Failed Parameter Sets***\n')
  for dictionary in failedList:
    arcpy.AddMessage(dictionary)
    arcpy.AddMessage('')