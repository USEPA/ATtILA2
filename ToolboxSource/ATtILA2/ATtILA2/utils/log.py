import os
import arcpy
from arcpy import env
from . import parameters
from ATtILA2.constants import globalConstants
from datetime import datetime
from ATtILA2.datetimeutil import DateTimer
from .messages import AddMsg

timer = DateTimer()

def setupLogFile(optionalFieldGroups, metricConst, parametersList, outDataset, toolPath=None):
    import platform
    
    processed = parameters.splitItemsAndStripDescriptions(optionalFieldGroups, globalConstants.descriptionDelim)    
    
    if globalConstants.logName in processed:
        # capture current date and time
        logTimeStamp = datetime.now().strftime(globalConstants.logFileExtension)
        # create the log file in the appropriate folder
        logFile = createLogFile(outDataset, logTimeStamp)
        
        if logFile:
            # start the log file by capturing ATtILA, ArcGIS, and System information
            infoATtILA = '{0} v{1}'.format(globalConstants.titleATtILA, globalConstants.attilaVersion)
            arcInstall = arcpy.GetInstallInfo()
            infoArcGIS = '{0} {1} License={2} Build={3}'.format(arcInstall['ProductName'], arcInstall['Version'], arcInstall['LicenseLevel'], arcInstall['BuildNumber'])
            infoSystem = platform.platform()
            logFile.write('SPECS: {0} ; {1} ; {2}\n\n'.format(infoATtILA, infoArcGIS, infoSystem))
            
            logFile.write('TOOL: {0} ; {1} ; {2}\n\n'.format(metricConst.name, metricConst.shortName.upper(), toolPath))
            
            # populate the log file by capturing the tool's parameters.
            labelsList = metricConst.parameterLabels
            logWriteParameters(logFile, parametersList, labelsList, metricConst)
    else:
        logFile = None
    
    return logFile


def createLogFile(inDataset, dateTimeStamp):
    """ Create log file to capture tool processing steps. """
    
    inBaseName = os.path.basename(inDataset)
    inRootName = os.path.splitext(inBaseName)[0]
    logBaseName = ('{0}_{1}').format(inRootName, dateTimeStamp)
    
    odsc = arcpy.Describe(env.workspace)
    
    # determine where to create the log file
    if odsc.DataType == "Folder":
        logPathName = os.path.join(env.workspace, logBaseName)
    else:
        logPathName = os.path.join(os.path.dirname(env.workspace), logBaseName)
    
    try:
        msg = "Created log file: {0}\n"
        arcpy.AddMessage(msg.format(logPathName))
        reportFile = open(logPathName, 'a')
            
        return reportFile
    except:
        AddMsg("Unable to create log file. Continuing metric calculations.", 1)
        if reportFile:
            reportFile.close()
        
        return None


def logWriteOutputTableInfo(newTable, logFile):
    
    logFile.write("\n")
    logFile.write("Table Field Attributes: NAME, ALIAS, TYPE, LENGTH, PRECISION, SCALE \n")
    
    newFields = arcpy.ListFields(newTable)
    
    for f in newFields:
        logFile.write("FIELD: {0} ; {1} ; {2} ; {3} ; {4} ; {5} \n".format(f.name, f.aliasName, f.type, f.length, f.precision, f.scale))
    
    # # This section of code will write the field NAME, TYPE, MIN Value, and MAX Value to the log file. It is time consumptive.
    #
    # import pandas
    # from arcgis.features import GeoAccessor, GeoSeriesAccessor
    #
    # stat_Fields = arcpy.ListFields(newTable)[2:]  # if we start at position 2 we’ll drop OBJECTID and RU ID Field
    # in_fields  = ';'.join([f.name for f in stat_Fields]) 
    # outTables = "ALL ATtILA_TmpStats"
    #
    # arcpy.management.FieldStatisticsToTable(newTable,
    #                                         in_fields,
    #                                         env.workspace,
    #                                         outTables,
    #                                         None,
    #                                         "ALIAS Alias;FIELDNAME FieldName;FIELDTYPE FieldType;MAXIMUM Maximum;MINIMUM Minimum"
    #                                         )
    #
    # outTable = "ATtILA_TmpStats"
    # sdf = pandas.DataFrame.spatial.from_table(outTable)
    # out_columns = ['FieldName', 'FieldType', 'Minimum', 'Maximum']
    #
    # logFile.write("\n")
    # logFile.write(sdf[out_columns].to_csv(index=None, header=None))
    #
    # if arcpy.Exists(outTable):
    #     arcpy.Delete_management(outTable)

        

def logWriteClassValues(logFile, metricsBaseNameList, lccObj, metricConst):
    ''' Write grid values for selected metric classes to log file. '''
    
    if metricConst.shortName in globalConstants.allGridValuesTools:
        pass
    else:
        lccClassesDict = lccObj.classes
        excludedValuesList = lccObj.values.getExcludedValueIds()
        
        logFile.write("\n")
        for mBaseName in metricsBaseNameList:
            # get the grid codes for this specified metric
            metricGridCodesList = lccClassesDict[mBaseName].uniqueValueIds
            logFile.write('CLASS: {0} = {1}\n'.format(mBaseName, str(list(metricGridCodesList))))
        
        if len(excludedValuesList) > 0:
            logFile.write('CLASS: Excluded = {0}\n'.format(str(list(excludedValuesList))))
        
        logFile.write("\n")


def logWriteParameters(logFile, parametersList, labelsList, metricConst):
    ''' Write tool parameter inputs to log file. '''
    
    logFile.write('''
    import arcpy
    from arcpy.sa import *
    arcpy.ImportToolbox("<toolbox path and filename>")
    from ATtILA2 import metric
    
    ''')
    toolParameters = []
    for l, p in zip(labelsList, parametersList):
        l = l.replace(" ","_")
        p = p.replace("\\","\\\\")
        if l == "Select_options":
            p = ("'{0}'".format(p))

        toolParameters.append('{0}="{1}"'.format(l,p))
    
    outString = ", \n    ".join(toolParameters)    
    logFile.write("{0}(\n    {1}\n    ) \n\n".format(metricConst.metricFUNC, outString))
    
    for l, p in zip(labelsList, parametersList):
        if p:
            logFile.write('PARAMETER: {0} = {1}\n'.format(l, p.replace("'"," ")))
    
    logFile.write("\n")


def logArcpy(commandStr, paramsTuple, logFile):

    paramStr = "(" + ", ".join([str(item) for item in paramsTuple]) + ")"
    
    # AddMsg("{0} {1}{2}".format(timer.now(), commandStr, paramStr), 0, logFile)
    AddMsg("    {0}{1}".format(commandStr, paramStr), 0, logFile)