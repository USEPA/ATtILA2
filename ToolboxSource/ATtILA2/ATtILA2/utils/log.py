import os
import arcpy
from arcpy import env
from . import parameters
from ATtILA2.constants import globalConstants
from datetime import datetime
from ATtILA2.datetimeutil import DateTimer
from .messages import AddMsg
import pandas
from pandas import DataFrame
from pandas.api.types import is_numeric_dtype
from ATtILA2.utils import pandasutil



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
    
    # Because ATtILA outputs do not exist at the start of the log file creation
    # process, we use the ArcGIS project workspace as the starting point to determine
    # where to create the log file. In ArcGIS Pro, the default value for the Current 
    # Workspace environments is the project default geodatabase. This can be changed
    # via the Analysis -> Environments -> Current workspace. If the workspace is a 
    # geodatabase, the log file is created in the folder that contains the geodatabase.
    # If the workspace is a folder, the log file is created in that folder.
    
    odsc = arcpy.Describe(env.workspace)
    
    # determine where to create the log file
    if odsc.DataType == 'Folder':
        logPathName = os.path.join(env.workspace, logBaseName)
    else:
        logPathName = os.path.join(os.path.dirname(env.workspace), logBaseName)
    
    try:
        msg = 'Created log file: {0}\n'
        arcpy.AddMessage(msg.format(logPathName))
        reportFile = open(logPathName, 'a')
            
        return reportFile
    except:
        AddMsg('Unable to create log file. Continuing metric calculations.', 1)
        if reportFile:
            reportFile.close()
        
        return None


def logWriteOutputTableInfo(newTable, logFile, metricConst):
    
    logFile.write('\n')
    logFile.write('Table Field Attributes: NAME, ALIAS, TYPE, LENGTH, PRECISION, SCALE, MIN, MAX \n') # Do we also want MEAN?
    
    newFields = arcpy.ListFields(newTable)
    #fieldNames = [field.name for field in newFields]
    df = pandasutil.table_to_pd_df(newTable)
    #arcpy.AddMessage(df)
    for f, c  in zip(newFields, df):
        #if is_numeric_dtype(df[c]) and c not in ['OBJECTID', 'FID', 'ID']:
        if is_numeric_dtype(df[c]) and c not in metricConst.idFields: #maybr call NonNumericFields
            fMin = str(df[c].min())
            fMax = str(df[c].max())
        else: 
            fMin = "NA"
            fMax = "NA"

        logFile.write('FIELD: {0} ; {1} ; {2} ; {3} ; {4} ; {5}; {6}; {7} \n'.format(f.name, f.aliasName, f.type, f.length, f.precision, f.scale, fMin, fMax))     


def writeIntersectExtent(logFile, extentList):
    ''' Intersect the extent of input feature classes and write the WGS 84 projected coordinates of the bounding rectangle to the log file. '''
    
    projectedExtents = []
    
    # remove any potentially empty elements from the list
    def removeEmpty(variable):
        if variable not in ['#', '']:
            return True
        else:
            return False
    
    extentList = list(filter(removeEmpty, extentList))
    
    for f in extentList:
        desc = arcpy.Describe(f)
        fExtent = desc.extent
        
        inSR = desc.spatialReference
        logFile.write(f'INFO: Extent {desc.name} ({inSR.name}) = {fExtent.XMax}, {fExtent.YMax}, {fExtent.XMin}, {fExtent.YMin}\n')
        
        wgs84SR = arcpy.SpatialReference(4326)
        transformList = arcpy.ListTransformations(inSR, wgs84SR, fExtent)
        if len(transformList) == 0:
            # if no list is returned; no transformation is required
            transformMethod = ""
        else:
            # default to the first transformation method listed. ESRI documentation indicates this is typically the most suitable
            transformMethod = transformList[0]
        
        if transformMethod != "":
            prjExt = fExtent.projectAs(wgs84SR, transformMethod)
        else:
            prjExt = fExtent.projectAs(wgs84SR)
        
        projectedExtents.append(prjExt)
    
    # get the vertices of the minimum bounding rectangle
    intersectLLX = max([aExt.XMin for aExt in projectedExtents])
    intersectLLY = max([aExt.YMin for aExt in projectedExtents])
    intersectURX = min([aExt.XMax for aExt in projectedExtents])
    intersectURY = min([aExt.YMax for aExt in projectedExtents])
    
    logFile.write('\n')    
    logFile.write(f'ENVIRONMENT: Extent Intersection (WGS 1984) = {intersectURX}, {intersectURY}, {intersectLLX}, {intersectLLY}\n')


def writeEnvironments(logFile, snapRaster, processingCellSize, extentList=None):
    ''' Write select analysis environment settings to a log file.
    
    **Description:**

        The following analysis environment settings are recorded: 
        
        The M Flag, Z Flag, and Parallel Processing Factor settings are always captured in the log file. 
        
        If provided, the Snap Raster and the Processing Cell Size settings are also recorded. 
        
        If an extentList of datasets is provided, each dataset's spatial reference name and the
        bounding coordinates of its spatial extent will be written to the log file as well as the bounding 
        coordinates in the WGS 84 spatial reference coordinate system of the intersection of all extents.
        
    **Arguments:**
    
        * *logFile* - CatalogPath and name of the text log file
        * *snapRaster* - CatalogPath and name of a raster dataset as a string. Can be None
        * *processingCellSize* - the processing cell size as a string. Can be None
        * *extentList* - List of datasets. Can be None
        
    **Returns:**

        * N/A
    
    '''
    
    logFile.write('\n')
    
    try:
        if extentList:
            writeIntersectExtent(logFile, extentList)
        else:
            envExtent = env.extent
            ocs = env.outputCoordinateSystem
            
            logFile.write(f'INFO: Extent env ({ocs.name}) = {envExtent.XMax}, {envExtent.YMax}, {envExtent.XMin}, {envExtent.YMin}\n')
            
            wgs84SR = arcpy.SpatialReference(4326)
            transformList = arcpy.ListTransformations(ocs, wgs84SR, envExtent)
            if len(transformList) == 0:
                # if no list is returned; no transformation is required
                transformMethod = ""
            else:
                # default to the first transformation method listed. ESRI documentation indicates this is typically the most suitable
                transformMethod = transformList[0]
            
            if transformMethod != "":
                prjExt = envExtent.projectAs(wgs84SR, transformMethod)
            else:
                prjExt = envExtent.projectAs(wgs84SR)
            
            logFile.write('\n')    
            logFile.write(f'ENVIRONMENT: Extent Intersection (WGS 1984) = {prjExt.XMax}, {prjExt.YMax}, {prjExt.XMin}, {prjExt.YMin}\n')

                                        
    except:
        logFile.write('ENVIRONMENT: Intersect Extent error encountered\n')


    if snapRaster:
        logFile.write(f'ENVIRONMENT: Snap Raster = {env.snapRaster}\n')
    if processingCellSize:
        logFile.write(f'ENVIRONMENT: Cell Size = {env.cellSize}\n')
    logFile.write(f'ENVIRONMENT: Output M Flag = {env.outputMFlag}\n')
    logFile.write(f'ENVIRONMENT: Output Z Flag = {env.outputZFlag}\n')
    logFile.write(f'ENVIRONMENT: Parallel Processing Factor = {env.parallelProcessingFactor}\n')
    
    logFile.write('\n')
    

def logWriteClassValues(logFile, metricsBaseNameList, lccObj, metricConst):
    ''' Write grid values for selected metric classes to log file. '''
    
    if metricConst.shortName in globalConstants.allGridValuesTools:
        pass
    else:
        lccClassesDict = lccObj.classes
        excludedValuesList = lccObj.values.getExcludedValueIds()
        
        #logFile.write('\n')
        for mBaseName in metricsBaseNameList:
            # get the grid codes for this specified metric
            metricGridCodesList = lccClassesDict[mBaseName].uniqueValueIds
            logFile.write('CLASS: {0} = {1}\n'.format(mBaseName, str(list(metricGridCodesList))))
        
        if len(excludedValuesList) > 0:
            # logFile.write('\n')
            logFile.write('CLASS: Excluded = {0}\n'.format(str(list(excludedValuesList))))
        
        logFile.write('\n')


def logWriteParameters(logFile, parametersList, labelsList, metricConst):
    ''' Write tool parameter inputs to log file. '''
    
    # Begin the Parameters section with a formated script that captures all of the parameters used for
    # the current tool run. The formating will include all of the necessary import statements, the variable 
    # assignments, and the command to launch the tool
    
    logFile.write('SCRIPT START:\n')
    
    # to neatly format the script with the variables listed in a comma-delimited column under the tool function
    # line, we need to know how far to indent the variables. Construct a string of spaces to pad the left side of the
    # variable entry beyond the tool function opening (e.g. 'arcpy.ATtILA.PAAA' = 17 spaces, 'metric.runLandCoverProportions' = 30 spaces).
    # add one more space to account for the parentheses enclosing the variables.
    numSpaces = len(metricConst.toolFUNC) + 1
    padding = ' ' * numSpaces
    
    # set up a list to capture the tool parameters in the format: parameter = 'value'
    toolParameters = []
    
    # set up a list to capture the parameters as variables in the format: padding+variable+','
    toolVariables = []
    
    # construct the parameter variable lines. The labelsList for each tool is found in metricConstants. 
    # The parametersList for each tool is found in metric.py
    for l, p in zip(labelsList, parametersList):
        l = l.replace(' ','_') # replace any spaces with underscores
        p = p.replace('\\','\\\\') # replace any single slash characters with a double slash
        p = p.replace('"',"'") # replace any double-quotes with single-quotes. Useful when a parameter contains internal double-quotes such as a geographic projection. See Intersection Density
        if l == 'Select_options':
            if p[0] != "'": # when a tool is run from a script, the Select options parameter string will already be quoted. Don't double quote
                p = (f"'{p}'") # place the options string in a quoted string

        # the variable, toolPath, is included in all labelsLists by convention
        # tools that use a Land Cover Classification XML file need to have that variable put into the script section
        # these tools begin with 'metric.run' toolFUNC versus the 'arcpy.ATtILA' toolFUNC. toolFUNC is found in metricConstants
        # toolPath needs to be excluded for the 'arcpy.ATtILA' tools
        if metricConst.toolFUNC.startswith("metric"):
            toolParameters.append(f'{l} = "{p}"')
            toolVariables.append(f'{padding}{l}')
        elif l != 'toolPath':
            toolParameters.append(f'{l} = "{p}"')
            toolVariables.append(f'{padding}{l}')
    
    # take the list of tool parameter strings, and join them together into a single line-separated string
    variableAssignmentString = '\n'.join(toolParameters)
    
    # take the list of tool variables, and join them together into a single line-separated string with a comma at the end of each line
    variableCommaString = ',\n'.join(toolVariables)
    
    # Write the constructed script
    logFile.write(metricConst.scriptOpening)
    
    logFile.write(f'{variableAssignmentString} \n\n')
    
    logFile.write(f'{metricConst.toolFUNC}(\n{variableCommaString}\n{padding}) \n\n')
    
    logFile.write('SCRIPT END:\n\n')
    
    
    # Finish the Parameters section with a list of tool parameters formatted as:
    # 'PARAMETER: label = value' (e.g., PARAMETER: Reporting unit feature = Watersheds)
    for l, p in zip(labelsList, parametersList):
        if p:
            p = p.replace("'"," ")
            # strip off any directory path information from the filename
            x = p.rfind('\\')
            if x != -1: p = p[x+1:]
            
            if l != globalConstants.toolScriptPath: # do not include toolPath in the PARAMETERS section
                logFile.write(f'PARAMETER: {l} = {p}\n')
    
    logFile.write('\n')


def arcpyLog(function, arguments, fxStr, logFile, logOnly=True):
    """ Performs an ArcPy function and writes its syntax as a string to tool history/details and/or a log file.
    
    **Description:**

        Performs an ArcPy operation given the ArcPy function and a tuple of its arguments. The full syntax
        of the ArcPy command is written to the tool details pane and/or a log file if one is provided. If the 
        tuple contains only one argument, the argument must end in a comma (e.g., (inReportingUnitFeature,))
        
    **Arguments:**
    
        * *function* - the ArcPy function without enclosing quotation marks (e.g., arcpy.gp.TabulateArea_sa)
        * *arguments* - a tuple of function arguments
                        If the tuple has only one value (i.e., only one argument), a comma after the value 
                        is necessary in order for Python to handle it as a tuple instead of a string (e.g., (inValue,)) 
                        This is official Python syntax
        * *fxStr* - the ArcPy function as a string
        * *logFile* - CatalogPath and name of the text log file. It can be None
        * *logOnly* - Boolean. If False then messages will be written to the tool's view details pane and to the
                      log file if the optional LOG FILE is selected
        
    **Returns:**

        * results of ArcPy function or None if one is not produced
        
    """
    
    # perform the arcpy operation
    result = function(*arguments)
    
    if logFile: # record processing step if the user choose LOGFILE in the Additional options
        # parse the arguments tuple into a comma-delimited string enclosed in parentheses
        paramStr = '(' + ', '.join([str(item) for item in arguments]) + ')'
        
        if logOnly: # write the arcpy function only to the log file
            logFile.write('{0}   [CMD] {1}{2}\n'.format(timer.now(), fxStr, paramStr))
        else: # write the ArcPy function with its arguments to the Tool Details pane and to a log file
            AddMsg('{0} {1}{2}'.format(timer.now(), fxStr, paramStr), 0, logFile)
    
    return result