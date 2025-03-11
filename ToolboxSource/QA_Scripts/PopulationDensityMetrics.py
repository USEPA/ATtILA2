import traceback, time, arcpy, os, sys, csv, subprocess
import arcpy
import itertools
from arcpy.sa import *
from parameters import *
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

# Create output workspaces
Output_GDB_pth = os.path.join(setup.outFolder, PDM.outGDB)

if not arcpy.Exists(Output_GDB_pth):
  arcpy.management.CreateFileGDB(setup.outFolder, PDM.outGDB)

arcpy.AddMessage('Setting up output geodatabase environments')

arcpy.env.workspace = Output_GDB_pth

#Define ATtILA metric
def runATtILA(paramDict, iteration): 
  outTable = os.path.join(Output_GDB_pth, f"{PDM.fileName}{iteration+1}")
  arcpy.AddMessage(f"***Starting {PDM.base}: run {iteration+1} of {len(paramCombosList)}***")
  metric.runPopulationDensityCalculator(
                  PDM.toolPath,
                  paramDict["inReportingUnitFeature"],
                  paramDict["reportingUnitIdField"],
                  paramDict["Census_feature"],
                  paramDict["Population_field"],
                  outTable,
                  paramDict["POPCHG"],
                  paramDict["Census_T2_feature"], 
                  paramDict["Population_T2_field"], 
                  paramDict["optionalFieldGroups"])

#Build list of possible combinations
paramCombosList = list(itertools.product(*PDM_options.testInputs.values()))

failedList = [] #failed list to store failed parameter set dictionaries
loopProgress = loopProgress(len(paramCombosList))
print(f"Testing {len(paramCombosList)} parameter combinations\n")


for iteration, params in enumerate(paramCombosList): 
  paramDict = dict(zip(PDM_options.testInputs.keys(), params))

  try: 
    runATtILA(paramDict, iteration)
  except: 
    AddMsg(f"exception occured using {paramDict}")
    failedList.append(paramDict)
    loopProgress.update()
    continue
  
if failedList == []: 
  print("No errors found")
else: 
  print('\n***Failed Parameter Sets***\n')
  for dictionary in failedList:
    print(dictionary)
    print('')