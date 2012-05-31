''' Tasks specific to setting up and restoring environments.
'''
import arcpy
from arcpy import env
from pylet import arcpyutil

from ATtILA2.constants import globalConstants

_tempEnvironment0 = ""
_tempEnvironment1 = ""
_tempEnvironment2 = ""


def standardSetup(snapRaster, processingCellSize, fallBackDirectory, itemDescriptionPairList=[]):
    """ Standard setup for executing metrics. """
    

    
    # Check out any necessary licenses
    arcpy.CheckOutExtension("spatial")
    
    # get current snap environment to restore at end of script
    _tempEnvironment0 = env.snapRaster
    _tempEnvironment1 = env.workspace
    _tempEnvironment2 = env.cellSize
    
    # set the snap raster environment so the rasterized polygon theme aligns with land cover grid cell boundaries
    env.snapRaster = snapRaster
    env.workspace = arcpyutil.environment.getWorkspaceForIntermediates(fallBackDirectory)
    env.cellSize = processingCellSize
    
    itemTuples = []
    for itemDescriptionPair in itemDescriptionPairList:
        processed = arcpyutil.parameters.splitItemsAndStripDescriptions(itemDescriptionPair, globalConstants.descriptionDelim)
        itemTuples.append(processed)
        
        if globalConstants.intermediateName in processed:
            msg = "\nIntermediates are stored in this directory: {0}\n"
            arcpy.AddMessage(msg.format(env.workspace))    
    
    return itemTuples

    
def standardRestore():
    """ Standard restore for executing metrics. """
    
    # restore the environments
    env.snapRaster = _tempEnvironment0
    env.workspace = _tempEnvironment1
    env.cellSize = _tempEnvironment2
    
    # return the spatial analyst license    
    try:
        arcpy.CheckInExtension("spatial")
    except:
        pass
    

def standardGridChecks(inLandCoverGrid, lccObj):
    """ Standard checks for input grids. """
    
    # warn user if input land cover grid has values not defined in LCC file
    rows = arcpy.SearchCursor(inLandCoverGrid) 

    gridValues = []    
    for row in rows:
        gridValues.append(row.getValue("VALUE"))
    
    undefinedValues = [aVal for aVal in gridValues if aVal not in lccObj.getUniqueValueIdsWithExcludes()]     
    if undefinedValues:
        arcpy.AddWarning("Following Grid Values undefined in LCC file: %s - Please refer to the %s documentation regarding undefined values." % 
                         (undefinedValues, globalConstants.titleATtILA))
        
def getIdOutField(inFeature, inField):
    """ Processes the InputField. If field is an OID type, alters the output field type and name """
    inField = arcpyutil.fields.getFieldByName(inFeature, inField)
    
    if inField.type == "OID":
        newField = arcpy.Field()
        newField.type = "Integer" 
        newField.name = inField.name+"_ID"
        newField.precision = inField.precision
        newField.scale = inField.scale
    else:
        newField = inField
        
    return (newField)

def getGeometryConversionFactor(inReportingUnitFeature, dimension):
    """ Determines the output coordinate system linear unit name. Returns conversion to square meters factor. """
    
    # check for output coordinate system setting in the arc environment
    if arcpy.env.outputCoordinateSystem:
        # output coordinate system is set. get it's linear units to use for area conversions
        linearUnits = arcpy.env.outputCoordinateSystem.linearUnitName
    else:
        # no output coordinate system set. get the output linear units for the input reporting unit theme.
        # warning: only use this theme if it is the first theme specified in ensuing geoprocessing tools
        desc = arcpy.Describe(inReportingUnitFeature)
        linearUnits = desc.spatialReference.linearUnitName
        
    if dimension.upper() == 'LENGTH':
        conversionFactor = arcpyutil.conversion.factorToMeters(linearUnits)
    elif dimension.upper() == 'AREA':
        conversionFactor = arcpyutil.conversion.factorToSquareMeters(linearUnits)
    else:
        conversionFactor = 0

    arcpy.AddMessage('linear units = %s and conversion factor = %s' % (linearUnits, conversionFactor))
    return conversionFactor