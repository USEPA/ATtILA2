"""
This tool is more challenging than others to automate.
The group by zone feature needs a zone ID field. 
This defaults to 'value' if a raster is inputted as the zone. 
If a polygon is inputted the zone ID field field must be.
This is addressed through PWZM_options1 and PWZM_options2. 
PWZM_options1 tests for a polygon zone and PWZM_options2 tests a raster zone.

"""
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

toolAbbv = 'PWZM'
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
  outTable = os.path.join(Output_GDB_pth, f"{fileName}{iteration+1}")
  arcpy.AddMessage(f"\n\n***Starting {toolAbbv}: run {iteration+1} of {len(paramCombosList)}***\n")
  arcpy.AddMessage(f"Test inputs: {paramDict}\n\n")
  metric.runPopulationWithinZoneMetrics(
                  toolPath,
                  paramDict["inReportingUnitFeature"],
                  paramDict["reportingUnitIdField"],
                  paramDict["Population_feature"],
                  paramDict["Population_field"],
                  paramDict["Zone_feature"],
                  paramDict["Buffer_distance"], 
                  paramDict["Group_by_zone"], 
                  paramDict["Zone_ID_field"], 
                  outTable, 
                  paramDict["optionalFieldGroups"]
                  )

for Dict_iteration, dictionary in enumerate(PWZM_options.testInputs): 
  paramCombosList = list(itertools.product(*dictionary.values()))
  arcpy.AddMessage(f"\nStarting parameter combination dictionary {Dict_iteration+1}\n")
  arcpy.AddMessage("*********************************************************")
  arcpy.AddMessage(f"Testing {len(paramCombosList)} parameter combinations")
  failedList = [] #failed list to store failed parameter set dictionaries
  Progress = loopProgress(len(paramCombosList)) #This should not be LoopProgress = loopProgress(len(paramCombosList)). Creates a reassignment error if it needs to be rewritten in this nested structure.  

  for iteration, params in enumerate(paramCombosList): 
    paramDict = dict(zip(dictionary.keys(), params))
    try: 
      runATtILA(paramDict, iteration)
    except: 
      AddMsg(f"exception occured using {paramDict}")
      failedList.append(paramDict)
      Progress.update()
      continue
  
  if failedList == []: 
    arcpy.AddMessage("No errors found")
  else: 
    arcpy.AddMessage('\n***Failed Parameter Sets***\n')
    for dictionary in failedList:
      arcpy.AddMessage(dictionary)
      arcpy.AddMessage('')
  
  arcpy.AddMessage(f"\n{len(failedList)} Errors found in parameter combination dictionary {Dict_iteration+1}. Continuing to the next parameter combination set\n")

arcpy.AddMessage(f"Finished all combination sets")

