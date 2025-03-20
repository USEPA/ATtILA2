''' These classes are for inheritance by ToolValidator classes

    These classes shouldn't be used directly as ToolValidators.
    Create a new ToolValidator class that inherits one of these classes.
'''

import arcpy
import os
from xml.dom.minidom import parse
from glob import glob 
from ATtILA2.constants import globalConstants
from ATtILA2.constants import validatorConstants
from  ..utils.lcc import constants as lccConstants
from ..utils.lcc import LandCoverClassification, LandCoverCoefficient
from math import modf
# from future.backports.test.pystone import TRUE, FALSE
    
class ProportionsValidator(object):
    """ Class for inheritance by ToolValidator Only
    
        This currently serves the following tools:
            Land Cover on Slope Proportions
            Land Cover Proportions
    

        
        Description of ArcToolbox parameters:
        -------------------------------------
        
        inTableIndex:  Two consecutive parameters
        1. Table(reporting units)
        2. Field(dropdown):  Obtained from="<Table>"
           
        inRasterIndex:  One parameter
        1. Raster Layer
        
        startIndex:  Three consecutive parameters 
        1. String: default  
        2. File: filter=lccFileExtension
        3. String:  MultiValue=Yes; 
        
        outTableIndex: Index of output table parameter
        1. table: required, output
        
        processingCellSizeIndex:  Index of optional processing cell size parameter
        1. Analysis cell size
        
        snapRasterIndex:  Index of optional snap raster parameter
        1. Raster Layer
        
        optionalFieldsIndex:  index of optional fields parameter
        1. String: Properties: MultiValue=Yes
        
    
    """
    
    # Indexes of input parameters
    inTableIndex = 0 
    inRasterIndex = 0  
    startIndex = 0  
    processingCellSizeIndex = 0
    outTableIndex = 0 
    snapRasterIndex = 0 
    optionalFieldsIndex = 0 
    
    # Indexes of secondary input parameters
    inRaster2Index = 0
    inIntegerRasterIndex = 0
    inMultiFeatureIndex = 0
    inVector2Index = 0
    inAnyRasterOrPolyIndex = 0
    inIntRasterOrPolyIndex = 0
    inputFields2Index = 0
    inDistanceIndex = 0
    inIntegerDistanceIndex = 0
    inWholeNumIndex = 0
    inPositiveIntegerIndex = 0
    inPositiveInteger2Index = 0
    inLinearUnitIndex = 0
    checkbox1Index = 0
    checkbox2Index = 0
    checkboxInParameters = {}
    outWorkspaceIndex = 0
    outRasterIndex = 0
    validNumberIndex = 0
    inPositiveNumberIndex = 0
    inZeroAndAboveIntegerIndex = 0
    integerPercentageIndex = 0
        
    # Additional local variables
    srcDirName = ""
    
    # Metric Specific
    filterList = []
    overrideAttributeName = ""
    fieldPrefix = ""
    fieldSuffix = ""
    metricShortName = ""
    
    def __init__(self):
        """ ESRI - Initialize ToolValidator class"""
 
        # Load metric constants        
        self.inputIdFieldTypes = validatorConstants.inputIdFieldTypes
        self.lccSchemeUserOption = validatorConstants.userOption
        self.metricAddDescription = globalConstants.metricAddDescription      
        self.metricDescription = validatorConstants.metricDescription
        self.noFeaturesMessage = validatorConstants.noFeaturesMessage
        self.noSpatialReferenceMessage = validatorConstants.noSpatialReferenceMessage
        self.noProjectionInOutputCS = validatorConstants.noProjectionInOutputCS
        self.noSpatialReferenceMessageMulti = validatorConstants.noSpatialReferenceMessageMulti
        self.nonIntegerGridMessage = validatorConstants.nonIntegerGridMessage
        self.greaterThanZeroMessage = validatorConstants.greaterThanZeroMessage
        self.greaterThanZeroIntegerMessage = validatorConstants.greaterThanZeroIntegerMessage
        self.zeroOrGreaterNumberMessage = validatorConstants.zeroOrGreaterNumberMessage
        self.zeroOrGreaterIntegerMessage = validatorConstants.zeroOrGreaterIntegerMessage
        self.integerGridOrPolgonMessage = validatorConstants.integerGridOrPolgonMessage
        self.polygonOrIntegerGridMessage = validatorConstants.polygonOrIntegerGridMessage
        self.invalidTableNameMessage = validatorConstants.invalidTableNameMessage
        self.invalidNumberMessage = validatorConstants.invalidNumberMessage
        self.invalidExtensionMessage = validatorConstants.invalidExtensionMessage
        self.integerPercentageMessage = validatorConstants.integerPercentageMessage
        self.noSpatialAnalystMessage = validatorConstants.noSpatialAnalystMessage
        
        # Load global constants
        self.optionalFieldsName = validatorConstants.optionalFieldsName
        self.qaCheckDescription = globalConstants.qaCheckDescription

        
        # Load LCC constants
        self.lccFileDirName = lccConstants.PredefinedFileDirName       
        self.lccFileExtension = lccConstants.XmlFileExtension
        self.idAttributeName = lccConstants.XmlAttributeId
        self.nameAttributeName = lccConstants.XmlAttributeName
        self.classElementName = lccConstants.XmlElementClass
        self.filterAttributeName = lccConstants.XmlAttributeFilter
        
        # Set relative indexes
        self.lccFilePathIndex = self.startIndex + 1
        self.lccClassesIndex = self.startIndex + 2
        self.inputFieldsIndex = self.inTableIndex + 1
        
        # Assign parameters to local variables
        self.parameters = arcpy.GetParameterInfo()
        self.inputTableParameter = self.parameters[self.inTableIndex]
        self.inputFieldsParameter = self.parameters[self.inputFieldsIndex]
        self.lccSchemeParameter =  self.parameters[self.startIndex]
        self.lccFilePathParameter = self.parameters[self.lccFilePathIndex]
        self.lccClassesParameter = self.parameters[self.lccClassesIndex]
        self.processingCellSizeParameter = self.parameters[self.processingCellSizeIndex]
        self.inRasterParameter = self.parameters[self.inRasterIndex]
        self.outTableParameter = self.parameters[self.outTableIndex]
        self.snapRasterParameter = self.parameters[self.snapRasterIndex]
        self.optionsParameter = self.parameters[self.optionalFieldsIndex]
        
        # Assign secondary input parameters to local variables
        if self.inRaster2Index:
            self.inRaster2Parameter = self.parameters[self.inRaster2Index]
            
        if self.inIntegerRasterIndex:
            self.inIntegerRasterParameter = self.parameters[self.inIntegerRasterIndex]
            
        if self.inMultiFeatureIndex:
            self.inMultiFeatureParameter = self.parameters[self.inMultiFeatureIndex]
            
        if self.inVector2Index:
            self.inVector2Parameter = self.parameters[self.inVector2Index]
            
        if self.inDistanceIndex:
            self.inDistanceParameter = self.parameters[self.inDistanceIndex]
            
        if self.inIntegerDistanceIndex:
            self.inIntegerDistanceParameter = self.parameters[self.inIntegerDistanceIndex]
            
        if self.inWholeNumIndex:
            self.inWholeNumParameter = self.parameters[self.inWholeNumIndex]
            
        if self.inPositiveIntegerIndex:
            self.inPositiveIntegerParameter = self.parameters[self.inPositiveIntegerIndex]
            
        if self.inPositiveInteger2Index:
            self.inPositiveInteger2Parameter = self.parameters[self.inPositiveInteger2Index]
            
        if self.validNumberIndex:
            self.validNumberParameter = self.parameters[self.validNumberIndex]
            
        if self.inLinearUnitIndex:
            self.inLinearUnitParameter = self.parameters[self.inLinearUnitIndex]

        if self.checkbox1Index:
            self.checkbox1Parameter = self.parameters[self.checkbox1Index]
            
        if self.checkbox2Index:
            self.checkbox2Parameter = self.parameters[self.checkbox2Index]
            
        if self.inIntRasterOrPolyIndex:
            self.inIntRasterOrPolyParameter = self.parameters[self.inIntRasterOrPolyIndex]
            
        if self.inAnyRasterOrPolyIndex:
            self.inAnyRasterOrPolyParameter = self.parameters[self.inAnyRasterOrPolyIndex]
            
        if self.inputFields2Index:
            self.inputFields2Parameter = self.parameters[self.inputFields2Index]
            
        if self.outWorkspaceIndex:
            self.outWorkspaceParameter = self.parameters[self.outWorkspaceIndex]
            
        if self.outRasterIndex:
            self.outRasterParameter = self.parameters[self.outRasterIndex]
            
        if self.inPositiveNumberIndex:
            self.inPositiveNumberParameter = self.parameters[self.inPositiveNumberIndex]
        
        if self.inZeroAndAboveIntegerIndex:
            self.inZeroAndAboveIntegerParameter = self.parameters[self.inZeroAndAboveIntegerIndex]
        
        if self.integerPercentageIndex:
            self.integerPercentageParameter = self.parameters[self.integerPercentageIndex]

               
        # Additional local variables
        self.currentFilePath = ""
        self.ruFilePath = ""
        self.initialized = False


    def initializeParameters(self):
        """ ESRI - Initialize parameters"""
        
        # disable dependent input fields until optional check boxes are selected    
        if self.checkboxInParameters:
            for val in self.checkboxInParameters.values():
                for indx in val:
                    self.parameters[indx].enabled = False 
        
        # Populate predefined LCC dropdown
        self.lccFileDirSearch = os.path.join(self.srcDirName, self.lccFileDirName, "*" + self.lccFileExtension)
        
        filterList = []
        self.lccLookup = {}
                
        for lccPath in glob(self.lccFileDirSearch):
            lccSchemeName = os.path.basename(lccPath).rstrip(self.lccFileExtension)
            filterList.append(lccSchemeName)
            self.lccLookup[lccSchemeName] = lccPath
            
        self.lccSchemeParameter.filter.list = filterList + [self.lccSchemeUserOption]
        self.lccFilePathParameter.enabled = False
        self.lccClassesParameter.enabled = False
                
        # Move parameters to optional section
        self.optionsParameter.category = self.optionalFieldsName
        
        # Set options filter
        self.optionsParameter.filter.list = self.filterList
        
        self.initialized = True
        
        
    def updateParameters(self):
        """ ESRI - Modify the values and properties of parameters before internal validation is performed.  
        
            This method is called whenever a parameter has been changed.
        
        """
        #arcpy.AddMessage("\n\n\updateParameters 0\n\n\n");
        if not self.initialized:
            self.initializeParameters()

        self.updateInputLccParameters()
        self.updateInputFieldsParameter()
        self.updateOutputTableParameter()
        
        # if checkboxes are provided, use the indexes specified in the tool's validation script to identify the 
        # parameter locations of any additional needed inputs for that checkbox and enable those parameters
        if self.checkbox1Index:
            cboxListeners = list(self.checkboxInParameters.values())[0]
            self.updateCheckboxParameters(self.checkbox1Parameter, cboxListeners)

        if self.checkbox2Index:
            #cboxListeners = self.checkboxInParameters.values()[1]
            cboxListeners = list(self.checkboxInParameters.values())[1]
            self.updateCheckboxParameters(self.checkbox2Parameter, cboxListeners)


    def updateCheckboxParameters(self, checkboxParameter, cboxListeners):
        if checkboxParameter.value:
            for indx in cboxListeners:
                self.parameters[indx].enabled = True


    def updateOutputTableParameter(self):
        """ Update an output table parameter
        
        **Description:**
            
            Removes .shp that is automatically generated for output table parameters and replaces it with .dbf
        
        """
       
        if self.outTableParameter.value:
            outTablePath = str(self.outTableParameter.value)
            self.outTableParameter.value  = outTablePath.replace('.shp', '.dbf')

    
    def updateInputLccParameters(self):
        """ Update Land Cover Classification Parameters 
        
            These parameters include LCC file path and list of classes with checkboxes.
        
        """
        
        # Converts None to "None", so must do a check
        lccSchemeName = ""
        if self.lccSchemeParameter.value:
            lccSchemeName = str(self.lccSchemeParameter.value)

        # User defined LCC Scheme
        lccFilePath = ""
        if  lccSchemeName == self.lccSchemeUserOption:
            lccFilePath = str(self.lccFilePathParameter.value)      
            self.lccFilePathParameter.enabled = True
            
        # Pre-defined  LCC Scheme  
        elif lccSchemeName:
            lccFilePath = self.lccLookup[lccSchemeName]
            
            # Delete user defined file path in dialog
            self.lccFilePathParameter.value = lccFilePath
            self.lccFilePathParameter.enabled = False

        
        # Get list of LCC names with description
        classNames = []
        if lccFilePath and self.currentFilePath != lccFilePath and os.path.isfile(lccFilePath):
            self.currentFilePath = lccFilePath
            classNames = self.getLccList(lccFilePath)
  
        # Populate checkboxes with LCC name and description
        if classNames:
            self.lccClassesParameter.enabled = True
        else:
            self.lccClassesParameter.enabled = False  
            self.lccClassesParameter.value = ""
        
        # Prevent the changing of the classification scheme from causing dialog errors when metrics are already checked    
        if not self.lccSchemeParameter.hasBeenValidated:
            self.lccClassesParameter.value = ""
            
        self.lccClassesParameter.filter.list = classNames
        
        
    def getLccList(self, lccFilePath):
        classNames = []
        lccDocument = parse(lccFilePath)
        classNodes = lccDocument.getElementsByTagName(self.classElementName)
        

        message = self.metricDescription
        for classNode in classNodes:
            
            # ignore class without value as descendant(child, child of child, etc.)
            if not classNode.getElementsByTagName(lccConstants.XmlElementValue):
                continue
            
            # Check filter, skip class if short metric name found (semi-colon delimiter)
            filterValue = classNode.getAttribute(self.filterAttributeName)
            shortNames = filterValue.split(";")
            if self.metricShortName in shortNames:
                continue
            
            classId = classNode.getAttribute(self.idAttributeName)
            name = classNode.getAttribute(self.nameAttributeName)     
            
            # Check for field override, ie NINDEX, UINDEX
            fieldName = classNode.getAttribute(self.overrideAttributeName)
            if not fieldName:
                fieldName = self.fieldPrefix + classId + self.fieldSuffix
            
            className = message.format(classId, fieldName, name)
            classNames.append(className)   
            
        return classNames
        
        
    def updateInputFieldsParameter(self):
        """  Set selected input field to first field of specified type
            
             Specified types comes from self.inputIdFieldTypes set in __init__()
             
        """
        
        fieldTypes = set(self.inputIdFieldTypes)
        tablePath = self.inputTableParameter.value
        fieldName = self.inputFieldsParameter.value
        
        # Proceed only if table path exists, but field name hasn't been set
        if tablePath and not fieldName:
            try:
                fields = arcpy.ListFields(tablePath)
                
                for field in fields:
                    if field.type in fieldTypes:
                        self.inputFieldsParameter.value = field.name
                        break
                    
                if not self.inputFieldsParameter.value:
                    for field in fields:
                        if field.type == "OID":
                            self.inputFieldsParameter.value = field.name
                            break
                        
            except:
                pass
                
        
    def updateMessages(self):
        """ ESRI - Modify the messages created by internal validation for each tool parameter.  
        
            This method is called after internal validation.
            
        """
        
        if self.spatialNeeded and arcpy.CheckExtension("Spatial") != "Available":
            self.parameters[0].setErrorMessage(self.noSpatialAnalystMessage)
            # for self.p in self.parameters:
            #     self.p.setErrorMessage(self.noSpatialAnalystMessage)


        # Set lcc file parameter required only if user-defined is set
        if self.lccSchemeParameter.value != self.lccSchemeUserOption:
            self.lccFilePathParameter.clearMessage()
            
        # Clear required on disabled lcc class selection
        if not self.lccClassesParameter.enabled:
            self.lccClassesParameter.clearMessage()
        
        # Remove required on optional fields
        self.optionsParameter.clearMessage()
        
        # Set optional raster options if env is set
        if not self.processingCellSizeParameter.value:
            try:
                envCellSize = int(arcpy.env.cellSize)
            except:
                envCellSize = None
            if envCellSize:
                self.processingCellSizeParameter.value = envCellSize
                
        # Set optional snap raster if env is set
        if not self.snapRasterParameter.value:
            self.snapRasterParameter.value = arcpy.env.snapRaster
            
        # Check if input raster is defined
        if self.inRasterParameter.value:
           
            if hasattr(self.inRasterParameter.value, "dataSource"):
                self.inRasterParameter.value = str(self.inRasterParameter.value.dataSource)
                self.parameters[self.inRasterIndex].value = self.inRasterParameter.value
            # Check for is input raster layer has spatial reference
            #self.spRefCheck(self.inRasterParameter)
            if arcpy.Describe(self.inRasterParameter.value).spatialReference.name.lower() == "unknown":
                self.inRasterParameter.setErrorMessage(self.noSpatialReferenceMessage)
            
            # Check if input raster is an integer grid
            inRaster = arcpy.Raster(str(self.inRasterParameter.value))
            if not inRaster.isInteger:
                self.inRasterParameter.setErrorMessage(self.nonIntegerGridMessage)
            
            # Update Processing cell size if empty
            if not self.processingCellSizeParameter.value and not self.processingCellSizeParameter.hasError():
                cellSize = arcpy.Raster(str(self.inRasterParameter.value)).meanCellWidth #get from metadata
                self.processingCellSizeParameter.value = cellSize
            
            # Update Snap Raster Parameter if it is empty
            if not self.snapRasterParameter.value and not self.inRasterParameter.hasError():
                self.snapRasterParameter.value = str(self.inRasterParameter.value)
            
        # Check input features
        if self.inputTableParameter.value and not self.inputTableParameter.hasError():
        
        #    # Check for empty input features
        #    if not arcpy.SearchCursor(self.inputTableParameter.value).next():
        #        self.inputTableParameter.setErrorMessage(self.noFeaturesMessage)
            
            # Check for if input feature layer has spatial reference
            # # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
            if hasattr(self.inputTableParameter.value, "dataSource"):
                if arcpy.Describe(self.inputTableParameter.value.dataSource).spatialReference.name.lower() == "unknown":
                    self.inputTableParameter.setErrorMessage(self.noSpatialReferenceMessage)
            else:
                if arcpy.Describe(self.inputTableParameter.value).spatialReference.name.lower() == "unknown":
                    self.inputTableParameter.setErrorMessage(self.noSpatialReferenceMessage)

        # Check if processingCellSize is a value greater than zero          
        if self.processingCellSizeParameter.value:
            try:
                cellSizeValue = arcpy.Raster(str(self.processingCellSizeParameter.value)).meanCellWidth
            except:
                cellSizeValue = self.processingCellSizeParameter.value
            if float(str(cellSizeValue)) <= 0:
                self.processingCellSizeParameter.setErrorMessage(self.greaterThanZeroMessage)
        
        # Check if output table has a valid filename; it contains no invalid characters, has no extension other than '.dbf' 
        # if the output location is in a folder, and has no extension if the output is to be placed in a geodatabase.
        if self.outTableParameter.value:
            self.outTableName = self.outTableParameter.valueAsText
        
            # get the directory path and the filename
            self.outWorkspace = os.path.split(self.outTableName)[0]
            self.tableFilename = os.path.split(self.outTableName)[1]
            
            # break the filename into its root and extension
            self.fileRoot = os.path.splitext(self.tableFilename)[0]
            self.fileExt = os.path.splitext(self.tableFilename)[1]
            
            # substitue valid characters into the filename root if any invalid characters are present
            self.validFileRoot = arcpy.ValidateTableName(self.fileRoot,self.outWorkspace)
            
            # alert the user if invalid characters are present in the output table name.
            if self.fileRoot != self.validFileRoot:
                self.outTableParameter.setErrorMessage(self.invalidTableNameMessage)
                
            else: # check on file extensions. None are allowed in geodatabases and only ".dbf" is allowed in folders.
                self.workspaceExt = os.path.splitext(self.outWorkspace)[1]
                
                # if the workspace is a geodatabase
                if self.workspaceExt.upper() == ".GDB":
                    if self.fileExt:
                        # alert user that file names cannot contain an extension in a GDB
                        self.outTableParameter.setErrorMessage(self.invalidExtensionMessage)               
                else:                    
                    # get the list of acceptable filename extentions for folder locations
                    self.tableExtensions = globalConstants.tableExtensions
                    
                    if self.fileExt not in self.tableExtensions:
                        self.outTableParameter.setErrorMessage("Output tables in folders must have the '.dbf' extension.")
        
            
        # CHECK ON SECONDARY INPUTS IF PROVIDED
        
        # if optional check box is unselected, clear the parameter message area and value area    
        if self.checkboxInParameters:
            for val in self.checkboxInParameters.values():
                for indx in val:
                    if not self.parameters[indx].enabled:
                        self.parameters[indx].clearMessage()
                        self.parameters[indx].value = ''
        
        # Check if a secondary input raster is indicated - use if raster can be either integer or float
        if self.inRaster2Index:
            # if provided, check if input raster2 is defined
            if self.inRaster2Parameter.value:
                # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inRaster2Parameter.value, "dataSource"):
                    if arcpy.Describe(self.inRaster2Parameter.value.dataSource).spatialReference.name.lower() == "unknown":
                        self.inRaster2Parameter.setErrorMessage(self.noSpatialReferenceMessage)
                else:
                    if arcpy.Describe(self.inRaster2Parameter.value).spatialReference.name.lower() == "unknown":
                        self.inRaster2Parameter.setErrorMessage(self.noSpatialReferenceMessage)
                        
        # Check if a secondary input integer raster is defined - use if raster has to be an integer type
        if self.inIntegerRasterIndex:
            # if provided, check if input integer raster is defined
            if self.inIntegerRasterParameter.value:
                # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inIntegerRasterParameter.value, "dataSource"):
                    if arcpy.Describe(self.inIntegerRasterParameter.value.dataSource).spatialReference.name.lower() == "unknown":
                        self.inIntegerRasterParameter.setErrorMessage(self.noSpatialReferenceMessage)
                else:
                    if arcpy.Describe(self.inIntegerRasterParameter.value).spatialReference.name.lower() == "unknown":
                        self.inIntegerRasterParameter.setErrorMessage(self.noSpatialReferenceMessage)
            
            # Check if input raster is an integer grid
            inIntegerRaster = arcpy.Raster(str(self.inIntegerRasterParameter.value))
            if not inIntegerRaster.isInteger:
                self.inIntegerRasterParameter.setErrorMessage(self.nonIntegerGridMessage)
                
        # Check if a secondary multiple input feature is indicated            
        if self.inMultiFeatureIndex:
            # if provided, get the valueTable and process each entry
            if self.inMultiFeatureParameter.value:
                multiFeatures = self.inMultiFeatureParameter.value
                rowCount = multiFeatures.rowCount
                for row in range(0, rowCount):
                    value = multiFeatures.getValue(row, 0)
                    if value:
                        # check to see if it has a spatial reference
                        d = arcpy.Describe(value)
                        if d.spatialReference.name.lower() == "unknown":
                            self.inMultiFeatureParameter.setErrorMessage(self.noSpatialReferenceMessageMulti)
                            
        # Check if a secondary vector input feature is indicated
        if self.inVector2Index:
            # if provided, check if input vector2 is defined
            if self.inVector2Parameter.value:
                # query for a dataSource attribue, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inVector2Parameter.value, "dataSource"):
                    if arcpy.Describe(self.inVector2Parameter.value.dataSource).spatialReference.name.lower() == "unknown":
                        self.inVector2Parameter.setErrorMessage(self.noSpatialReferenceMessage)
                else:
                    if arcpy.Describe(self.inVector2Parameter.value).spatialReference.name.lower() == "unknown":
                        self.inVector2Parameter.setErrorMessage(self.noSpatialReferenceMessage) 

        # Check if a secondary AnyRasterOrPoly dataset input feature is indicated. Use this for requiring a raster or polygon dataset.
        if self.inAnyRasterOrPolyIndex:
            # if provided, check if input geodataset1 is defined
            if self.inAnyRasterOrPolyParameter.value:
                # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inAnyRasterOrPolyParameter.value, "dataSource"):
                    desc = arcpy.Describe(self.inAnyRasterOrPolyParameter.value.dataSource)
                else:
                    desc = arcpy.Describe(self.inAnyRasterOrPolyParameter.value)

                if desc.spatialReference.name.lower() == "unknown":
                    self.inAnyRasterOrPolyParameter.setErrorMessage(self.noSpatialReferenceMessage) 
                
                if desc.datasetType == "RasterDataset":
                    # Check if input raster is an integer grid
                    inRaster = arcpy.Raster(str(self.inAnyRasterOrPolyParameter.value))
                    if inRaster.isInteger:
                        try:
                            self.inputFields2Parameter.clearMessage()
                            self.inputFields2Parameter.value = "Value"
                        except:
                            pass
                        #self.inAnyRasterOrPolyParameter.setErrorMessage(self.integerGridOrPolgonMessage)
                    else:
                        try:
                            self.inputFields2Parameter.value = ''
                        except:
                            pass
                elif desc.shapeType.lower() != "polygon":
                        self.inAnyRasterOrPolyParameter.setErrorMessage(self.polygonOrIntegerGridMessage) 
                        
        # Check if a secondary intRasterOrPoly input feature is indicated. Use this for requiring an integer raster or polygon dataset.
        if self.inIntRasterOrPolyIndex:
            # if provided, check if input geodataset is defined
            if self.inIntRasterOrPolyParameter.value:
                # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inIntRasterOrPolyParameter.value, "dataSource"):
                    desc = arcpy.Describe(self.inIntRasterOrPolyParameter.value.dataSource)
                else:
                    desc = arcpy.Describe(self.inIntRasterOrPolyParameter.value)

                if desc.spatialReference.name.lower() == "unknown":
                    self.inIntRasterOrPolyParameter.setErrorMessage(self.noSpatialReferenceMessage) 
                
                if desc.datasetType == "RasterDataset":
                    # Check if input raster is an integer grid
                    inRaster = arcpy.Raster(str(self.inIntRasterOrPolyParameter.value))
                    if not inRaster.isInteger:
                        self.inIntRasterOrPolyParameter.setErrorMessage(self.integerGridOrPolgonMessage)

                else:
                    if desc.shapeType.lower() != "polygon":
                        self.inIntRasterOrPolyParameter.setErrorMessage(self.polygonOrIntegerGridMessage) 
                                                
        # Check if distance input (e.g., buffer width, edge width) is a value greater than zero            
        if self.inDistanceIndex:
            if not self.inDistanceParameter.enabled:
                self.inDistanceParameter.clearMessage()
            else:
                if self.inDistanceParameter.value:
                    distanceValue = self.inDistanceParameter.value
                    # use the split function so this routine can be used for both long and linear unit data types
                    strDistance = str(distanceValue).split()[0]
                    if float(strDistance) <= 0.0:
                        self.inDistanceParameter.setErrorMessage(self.greaterThanZeroMessage)
                else:
                    # need the else condition as a 0 value won't trigger the if clause 
                    self.inDistanceParameter.setErrorMessage(self.greaterThanZeroMessage)
                
        # Check if distance input (e.g., buffer width, edge width) is a positive number and an integer            
        if self.inIntegerDistanceIndex:
            if not self.inIntegerDistanceParameter.enabled:
                self.inIntegerDistanceParameter.clearMessage()
            else:
                if self.inIntegerDistanceParameter.value:
                    integerDistanceValue = self.inIntegerDistanceParameter.value
                    # use the split function so this routine can be used for both long and linear unit data types
                    strIntegerDistance = str(integerDistanceValue).split()[0]
                    integerDistance = float(strIntegerDistance)
                    valModulus = modf(integerDistance)
                    if valModulus[0] != 0 or valModulus[1] < 1.0:
                        self.inIntegerDistanceParameter.setErrorMessage(self.greaterThanZeroIntegerMessage)    
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.inIntegerDistanceParameter.setErrorMessage(self.greaterThanZeroIntegerMessage)
                
        # Check if distance input (e.g., maximum separation) is a positive number or zero           
        if self.inWholeNumIndex:
            if not self.inWholeNumParameter.enabled:
                self.inWholeNumParameter.clearMessage()
            else:
                if self.inWholeNumParameter.value:
                    wholeNumValue = self.inWholeNumParameter.value
                    if wholeNumValue < 0.0:
                        self.inWholeNumParameter.setErrorMessage(self.zeroOrGreaterNumberMessage)
        
        # Check if number input (e.g., slope threshold) is a positive integer including zero           
        if self.inZeroAndAboveIntegerIndex:
            if not self.inZeroAndAboveIntegerParameter.enabled:
                self.inZeroAndAboveIntegerParameter.clearMessage()
            else:
                if self.inZeroAndAboveIntegerParameter.value:
                    zeroAndAboveValue = self.inZeroAndAboveIntegerParameter.value
                    valModulus = modf(zeroAndAboveValue)
                    if valModulus[0] != 0 or valModulus[1] < 1.0:
                        self.inZeroAndAboveIntegerParameter.setErrorMessage(self.zeroOrGreaterIntegerMessage) 
                    
        # Check if number input (e.g., number of cells) is a positive integer greater than zero       
        if self.inPositiveIntegerIndex:
            # This parameter can be linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.inPositiveIntegerParameter.enabled:
                self.inPositiveIntegerParameter.clearMessage()
            else:
                if self.inPositiveIntegerParameter.value:
                    positiveIntValue = self.inPositiveIntegerParameter.value
                    valModulus = modf(positiveIntValue)
                    if valModulus[0] != 0 or valModulus[1] < 1.0:
                        self.inPositiveIntegerParameter.setErrorMessage(self.greaterThanZeroIntegerMessage)    
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.inPositiveIntegerParameter.setErrorMessage(self.greaterThanZeroIntegerMessage)
                    
        # Check if number input (e.g., number of cells) is a positive integer greater than zero 
        if self.inPositiveInteger2Index:
            # This parameter can be linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.inPositiveInteger2Parameter.enabled:
                self.inPositiveInteger2Parameter.clearMessage()
            else:
                if self.inPositiveInteger2Parameter.value:
                    positiveInt2Value = self.inPositiveInteger2Parameter.value
                    val2Modulus = modf(positiveInt2Value)
                    if val2Modulus[0] != 0 or val2Modulus[1] < 1.0:
                        self.inPositiveInteger2Parameter.setErrorMessage(self.greaterThanZeroIntegerMessage)  
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.inPositiveInteger2Parameter.setErrorMessage(self.greaterThanZeroIntegerMessage)

        # Check if number input (e.g., cell size) is a positive number greater than zero        
        if self.inPositiveNumberIndex:
            # This parameter can be linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.inPositiveNumberParameter.enabled:
                self.inPositiveNumberParameter.clearMessage()
            else:
                if self.inPositiveNumberParameter.value:
                    positiveValue = self.inPositiveNumberParameter.value
                    if positiveValue <= 0.0:
                        self.inPositiveNumberParameter.setErrorMessage(self.greaterThanZeroMessage)  
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.inPositiveNumberParameter.setErrorMessage(self.greaterThanZeroMessage)
        
        # Check if number input (e.g., burn in value) is in the set of invalid numbers (i.e., 0 to 100)
        if self.validNumberIndex:
            # This parameter is often linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.validNumberParameter.enabled:
                self.validNumberParameter.clearMessage()
            else:
                if self.validNumberParameter.value:
                    invalidNumbers = set((range(101)))
                    enteredValue = self.validNumberParameter.value
                    if enteredValue in invalidNumbers:
                        self.validNumberParameter.setErrorMessage(self.invalidNumberMessage)
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.validNumberParameter.setErrorMessage(self.invalidNumberMessage)   

        # Check if number input (e.g., percent view threshold) is in the set of valid numbers (i.e., 1 to 100)
        if self.integerPercentageIndex:
            # This parameter is often linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.integerPercentageParameter.enabled:
                self.integerPercentageParameter.clearMessage()
            else:
                if self.integerPercentageParameter.value:
                    validIntegers = set((range(1,101)))
                    pctValue = self.integerPercentageParameter.value
                    if pctValue not in validIntegers:
                        self.integerPercentageParameter.setErrorMessage(self.integerPercentageMessage)
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.integerPercentageParameter.setErrorMessage(self.integerPercentageMessage)
                
        # Check if distance input (e.g., buffer width, edge width) is a positive number greater than zero
        if self.inLinearUnitIndex:
            # This parameter can be linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.inLinearUnitParameter.enabled:
                self.inLinearUnitParameter.clearMessage()
            else:
                if self.inLinearUnitParameter.value:
                    linearUnitValue = self.inLinearUnitParameter.value
                    # use the split function so this routine can be used for both long and linear unit data types
                    strLinearUnit = str(linearUnitValue).split()[0]
                    if float(strLinearUnit) <= 0.0:
                        self.inLinearUnitParameter.setErrorMessage(self.greaterThanZeroMessage)

        # # Check if a secondary raster output is indicated
        # if self.outRasterIndex:
        #     # if provided, check if the output raster name is valid in a geodatabase
        #     if self.outRasterParameter.value:  
        #         self.outRasterName = self.outRasterParameter.valueAsText
        #
        #         # get the directory path and the filename
        #         self.outWorkspace = os.path.split(self.outRasterName)[0]
        #         self.rasterFilename = os.path.split(self.outRasterName)[1]
        #
        #         # break the filename into its root and extension, if one exists
        #         self.fileExt = os.path.splitext(self.rasterFilename)[1]
        #         self.fileRoot = os.path.splitext(self.rasterFilename)[0]
        #
        #         # check if the workspace is a geodatabase
        #         self.workspaceExt = os.path.splitext(self.outWorkspace)[1]
        #
        #         if self.workspaceExt and self.fileExt:
        #             # alert user that raster names cannot contain an extension in a GDB
        #             self.outRasterParameter.setErrorMessage(self.invalidExtensionMessage)
        #         else:
        #
        #             # substitue valid characters into the filename root, if necessary 
        #             self.validFileRoot = arcpy.ValidateTableName(self.fileRoot,self.outWorkspace)
        #
        #             # get the list of acceptable raster filename extentions
        #             self.rasterExtensions = globalConstants.rasterExtensions
        #
        #             # assemble the new filename with any valid character substitutions
        #             if self.fileExt: # a filename extension was provided
        #                 if self.fileExt in self.rasterExtensions:
        #                     self.validFilename = self.validFileRoot + self.fileExt
        #                     self.validRasterName = os.path.join(self.outWorkspace,self.validFilename)
        #                 else: 
        #                     # drop extension from filename, causing the filename comparison below to fail
        #                     self.validRasterName = os.path.join(self.outWorkspace,self.validFileRoot)
        #             else: # a filename extension was omitted
        #                 self.validRasterName = os.path.join(self.outWorkspace,self.validFileRoot)
        #
        #             # if the validated raster name is different than the input raster name, then the
        #             # input raster name contains invalid characters or symbols
        #             if self.outRasterName != self.validRasterName:
        #                 self.outRasterParameter.setErrorMessage(self.invalidTableNameMessage)     
  
        # Check if a secondary raster output is indicated      
        if self.outRasterIndex:
            # Check if output raster has a valid filename; it contains no invalid characters, has no extension other than 
            # those found in globalConstants.rasterExtensions if the output location is in a folder, and has no extension 
            # if the output is to be placed in a geodatabase.
            if self.outRasterParameter.value:
                self.outRasterName = self.outRasterParameter.valueAsText
            
                # get the directory path and the filename
                self.outRasterWorkspace = os.path.split(self.outRasterName)[0]
                self.rasterFilename = os.path.split(self.outRasterName)[1]
                
                # break the filename into its root and extension
                self.rasterFileRoot = os.path.splitext(self.rasterFilename)[0]
                self.rasterFileExt = os.path.splitext(self.rasterFilename)[1]
                
                # substitue valid characters into the filename root if any invalid characters are present
                self.validRasterFileRoot = arcpy.ValidateTableName(self.rasterFileRoot,self.outRasterWorkspace)
                
                # alert the user if invalid characters are present in the output table name.
                if self.rasterFileRoot != self.validRasterFileRoot:
                    self.outRasterParameter.setErrorMessage(self.invalidTableNameMessage)
                    
                elif self.rasterFileExt: # check on file extensions. None are allowed in geodatabases and only certain extensions are allowed in folders.
                    self.rasterWorkspaceExt = os.path.splitext(self.outRasterWorkspace)[1]
                    
                    # if the workspace is a geodatabase
                    if self.rasterWorkspaceExt.upper() == ".GDB":
                        # alert user that file names cannot contain an extension in a GDB
                        self.outRasterParameter.setErrorMessage(self.invalidExtensionMessage)               
                    else:                    
                        # get the list of acceptable filename extentions for folder locations
                        # self.rasterExtensions = globalConstants.rasterExtensions
                        self.rasterExtensions = [".img", ".tif"]
                        
                        if self.rasterFileExt not in self.rasterExtensions:
                            self.outRasterParameter.setErrorMessage("Valid extensions for rasters in folders for this tool are: %s." % str(self.rasterExtensions))           
                                  
            
class CoefficientValidator(ProportionsValidator):
    """ Class for inheritance by ToolValidator Only """

    def getLccList(self, lccFilePath):
        lccList = []
        lccDoc = LandCoverClassification(lccFilePath)
        message = self.metricDescription
        for coefficient in lccDoc.coefficients.values():
            assert isinstance(coefficient, LandCoverCoefficient)
            line = message.format(coefficient.coefId, coefficient.fieldName, coefficient.name)
            lccList.append(line)
            
        return lccList
    
    
class NoLccFileValidator(object):
    """ Class for inheritance by ToolValidator Only
    
        This currently serves the following tools:
            Road Density Metrics
    

        
        Description of ArcToolbox parameters:
        -------------------------------------
        
        inTableIndex:  Two consecutive parameters
        1. Table(reporting units)
        2. Field(dropdown):  Obtained from="<Table>"
                 
        outTableIndex: Index of output table parameter
        1. table: required, output
        
        optionalFieldsIndex:  index of optional fields parameter
        1. String: Properties: MultiValue=Yes
        
    
    """
    
    
    # Indexes of input parameters
    inTableIndex = 0 
    outTableIndex = 0 
    processingCellSizeIndex = 0
    snapRasterIndex = 0 
    optionalFieldsIndex = 0 
    
    # Indexes of secondary input parameters
    inRasterIndex = 0
    inRaster2Index = 0
    inIntegerRasterIndex = 0
    inMultiFeatureIndex = 0
    inVector2Index = 0
    inVector3Index = 0
    inAnyRasterOrPolyIndex = 0
    inIntRasterOrPolyIndex = 0
    inIntRasterOrVectorIndex = 0
    inputFields2Index = 0
    inIntRasterOrVectorFieldsIndex = 0
    inDistanceIndex = 0
    inZeroDistanceIndex = 0
    inIntegerDistanceIndex = 0
    inWholeNumIndex = 0
    inPositiveIntegerIndex = 0
    inPositiveInteger2Index = 0
    inLinearUnitIndex = 0
    checkbox1Index = 0
    checkbox2Index = 0
    checkboxInParameters = {}
    outWorkspaceIndex = 0
    outRasterIndex = 0
    validNumberIndex = 0
    inPositiveNumberIndex = 0
    inZeroAndAboveIntegerIndex = 0
    integerPercentageIndex = 0
    
    # Additional local variables
    srcDirName = ""
    
    # Metric Specific
    filterList = []
    
    def __init__(self):
        """ ESRI - Initialize ToolValidator class"""
        
        # Load metric constants        
        self.inputIdFieldTypes = validatorConstants.inputIdFieldTypes
        self.noFeaturesMessage = validatorConstants.noFeaturesMessage
        self.noSpatialReferenceMessage = validatorConstants.noSpatialReferenceMessage
        self.noSpatialReferenceMessageMulti = validatorConstants.noSpatialReferenceMessageMulti
        self.nonIntegerGridMessage = validatorConstants.nonIntegerGridMessage
        self.greaterThanZeroMessage = validatorConstants.greaterThanZeroMessage
        self.greaterThanZeroIntegerMessage = validatorConstants.greaterThanZeroIntegerMessage
        self.zeroOrGreaterNumberMessage = validatorConstants.zeroOrGreaterNumberMessage
        self.zeroOrGreaterIntegerMessage = validatorConstants.zeroOrGreaterIntegerMessage
        self.integerGridOrPolgonMessage = validatorConstants.integerGridOrPolgonMessage
        self.polygonOrIntegerGridMessage = validatorConstants.polygonOrIntegerGridMessage
        self.invalidTableNameMessage = validatorConstants.invalidTableNameMessage
        self.invalidNumberMessage = validatorConstants.invalidNumberMessage
        self.invalidExtensionMessage = validatorConstants.invalidExtensionMessage
        self.integerPercentageMessage = validatorConstants.integerPercentageMessage
        self.integerGridOrVectorMessage = validatorConstants.integerGridOrVectorMessage
        self.vectorOrIntegerGridMessage = validatorConstants.vectorOrIntegerGridMessage
        self.noSpatialAnalystMessage = validatorConstants.noSpatialAnalystMessage
        
        # Load global constants
        self.optionalFieldsName = validatorConstants.optionalFieldsName
        
        # Set relative indexes
        self.inputFieldsIndex = self.inTableIndex + 1
        
        # Assign parameters to local variables
        self.parameters = arcpy.GetParameterInfo()
        self.inputTableParameter = self.parameters[self.inTableIndex]
        self.inputFieldsParameter = self.parameters[self.inputFieldsIndex]
        if self.outTableIndex > 0:
            self.outTableParameter = self.parameters[self.outTableIndex]
        self.optionsParameter = self.parameters[self.optionalFieldsIndex]
        
        # Assign secondary input parameters to local variables
        if self.inRasterIndex:
            self.inRasterParameter = self.parameters[self.inRasterIndex]
            
        if self.inRaster2Index:
            self.inRaster2Parameter = self.parameters[self.inRaster2Index]
            
        if self.inIntegerRasterIndex:
            self.inIntegerRasterParameter = self.parameters[self.inIntegerRasterIndex]
            
        if self.processingCellSizeIndex:
            self.processingCellSizeParameter = self.parameters[self.processingCellSizeIndex]
            
        if self.snapRasterIndex:
            self.snapRasterParameter = self.parameters[self.snapRasterIndex]
        
        if self.inMultiFeatureIndex:
            self.inMultiFeatureParameter = self.parameters[self.inMultiFeatureIndex]
            
        if self.inVector2Index:
            self.inVector2Parameter = self.parameters[self.inVector2Index]
            
        if self.inVector3Index:
            self.inVector3Parameter = self.parameters[self.inVector3Index]
            
        if self.inDistanceIndex:
            self.inDistanceParameter = self.parameters[self.inDistanceIndex]
        
        if self.inZeroDistanceIndex:
            self.inZeroDistanceParameter = self.parameters[self.inZeroDistanceIndex]
            
        if self.inIntegerDistanceIndex:
            self.inIntegerDistanceParameter = self.parameters[self.inIntegerDistanceIndex]

        if self.inWholeNumIndex:
            self.inWholeNumParameter = self.parameters[self.inWholeNumIndex]
            
        if self.inPositiveIntegerIndex:
            self.inPositiveIntegerParameter = self.parameters[self.inPositiveIntegerIndex]
            
        if self.inPositiveInteger2Index:
            self.inPositiveInteger2Parameter = self.parameters[self.inPositiveInteger2Index]
            
        if self.validNumberIndex:
            self.validNumberParameter = self.parameters[self.validNumberIndex]
        
        if self.inLinearUnitIndex:
            self.inLinearUnitParameter = self.parameters[self.inLinearUnitIndex]
               
        if self.checkbox1Index:
            self.checkbox1Parameter = self.parameters[self.checkbox1Index]
            
        if self.checkbox2Index:
            self.checkbox2Parameter = self.parameters[self.checkbox2Index]
            
        if self.inIntRasterOrPolyIndex:
            self.inIntRasterOrPolyParameter = self.parameters[self.inIntRasterOrPolyIndex]
        
        if self.inIntRasterOrVectorIndex:
            self.inIntRasterOrVectorParameter = self.parameters[self.inIntRasterOrVectorIndex]
            
        if self.inAnyRasterOrPolyIndex:
            self.inAnyRasterOrPolyParameter = self.parameters[self.inAnyRasterOrPolyIndex]
            
        if self.inputFields2Index:
            self.inputFields2Parameter = self.parameters[self.inputFields2Index]
        
        if self.inIntRasterOrVectorFieldsIndex:
            self.inIntRasterOrVectorFieldsParameter = self.parameters[self.inIntRasterOrVectorFieldsIndex]
        
        if self.outWorkspaceIndex:
            self.outWorkspaceParameter = self.parameters[self.outWorkspaceIndex]
            
        if self.outRasterIndex:
            self.outRasterParameter = self.parameters[self.outRasterIndex]
            
        if self.inPositiveNumberIndex:
            self.inPositiveNumberParameter = self.parameters[self.inPositiveNumberIndex]
            
        if self.inZeroAndAboveIntegerIndex:
            self.inZeroAndAboveIntegerParameter = self.parameters[self.inZeroAndAboveIntegerIndex]
        
        if self.integerPercentageIndex:
            self.integerPercentageParameter = self.parameters[self.integerPercentageIndex]
 
        # Additional local variables
        self.currentFilePath = ""
        self.ruFilePath = ""
        self.initialized = False


    def initializeParameters(self):
        """ ESRI - Initialize parameters"""
        
        # disable dependent input fields until optional check boxes are selected    
        if self.checkboxInParameters:
            for val in self.checkboxInParameters.values():
                for indx in val:
                    self.parameters[indx].enabled = False  
        
        # Move parameters to optional section
        self.optionsParameter.category = self.optionalFieldsName
        
        # Set options filter
        self.optionsParameter.filter.list = self.filterList
    
        self.initialized = True
        
        
    def updateParameters(self):
        """ ESRI - Modify the values and properties of parameters before internal validation is performed.  
        
            This method is called whenever a parameter has been changed.
        
        """
       
        if not self.initialized:
            self.initializeParameters()

        self.updateInputFieldsParameter()
        self.updateOutputTableParameter()

        # if checkboxes are provided, use the indexes specified in the tool's validation script to identify the 
        # parameter locations of any additional needed inputs for that checkbox and enable those parameters
        if self.checkbox1Index:
            #cboxListeners = self.checkboxInParameters.values()[0]
            cboxListeners = list(self.checkboxInParameters.values())[0]
            self.updateCheckboxParameters(self.checkbox1Parameter, cboxListeners)

        if self.checkbox2Index:
            #cboxListeners = self.checkboxInParameters.values()[1]
            cboxListeners = list(self.checkboxInParameters.values())[1]
            self.updateCheckboxParameters(self.checkbox2Parameter, cboxListeners)

    def updateCheckboxParameters(self, checkboxParameter, cboxListeners):
        if checkboxParameter.value:
            for indx in cboxListeners:
                self.parameters[indx].enabled = True

    def updateOutputTableParameter(self):
        """ Update an output table parameter
        
        **Description:**
            
            Removes .shp that is automatically generated for output table parameters and replaces it with .dbf
        
        """
       
        if self.outTableIndex > 0: #tools without an outTable have the index set to a negative number
            if self.outTableParameter.value:
                outTablePath = str(self.outTableParameter.value)
                self.outTableParameter.value  = outTablePath.replace('.shp', '.dbf')

    
              
        
    def updateInputFieldsParameter(self):
        """  Set selected input field to first field of specified type
            
             Specified types comes from self.inputIdFieldTypes set in __init__()
             
        """
        
        fieldTypes = set(self.inputIdFieldTypes)
        tablePath = self.inputTableParameter.value
        fieldName = self.inputFieldsParameter.value
        
        # Proceed only if table path exists, but field name hasn't been set
        if tablePath and not fieldName:
            try:
                fields = arcpy.ListFields(tablePath)
                
                for field in fields:
                    if field.type in fieldTypes:
                        self.inputFieldsParameter.value = field.name
                        break
                    
                if not self.inputFieldsParameter.value:
                    for field in fields:
                        if field.type == "OID":
                            self.inputFieldsParameter.value = field.name
                            break
                        
            except:
                pass
                
        
    def updateMessages(self):
        """ ESRI - Modify the messages created by internal validation for each tool parameter.  
        
            This method is called after internal validation.
            
        """
        
        if self.spatialNeeded and arcpy.CheckExtension("Spatial") != "Available":
            self.parameters[0].setErrorMessage(self.noSpatialAnalystMessage)
        
        # Remove required on optional fields
        self.optionsParameter.clearMessage()
                                 
        # Check input features
        if self.inputTableParameter.value and not self.inputTableParameter.hasError():
        
        #    # Check for empty input features
        #    if arcpy.SearchCursor(self.inputTableParameter.value).next():
        #        self.inputTableParameter.setErrorMessage(self.noFeaturesMessage)
            
            # Check for if input feature layer has spatial reference
            # # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
            if hasattr(self.inputTableParameter.value, "dataSource"):
                if arcpy.Describe(self.inputTableParameter.value.dataSource).spatialReference.name.lower() == "unknown":
                    self.inputTableParameter.setErrorMessage(self.noSpatialReferenceMessage)
            else:
                if arcpy.Describe(self.inputTableParameter.value).spatialReference.name.lower() == "unknown":
                    self.inputTableParameter.setErrorMessage(self.noSpatialReferenceMessage)
        
        if self.outTableIndex > 0: #tools without an outTable have the index set to a negative number   
            # Check if output table has a valid filename; it contains no invalid characters, has no extension other than '.dbf' 
            # if the output location is in a folder, and has no extension if the output is to be placed in a geodatabase.
            if self.outTableParameter.value:
                self.outTableName = self.outTableParameter.valueAsText
            
                # get the directory path and the filename
                self.outWorkspace = os.path.split(self.outTableName)[0]
                self.tableFilename = os.path.split(self.outTableName)[1]
                
                # break the filename into its root and extension
                self.fileRoot = os.path.splitext(self.tableFilename)[0]
                self.fileExt = os.path.splitext(self.tableFilename)[1]
                
                # substitue valid characters into the filename root if any invalid characters are present
                self.validFileRoot = arcpy.ValidateTableName(self.fileRoot,self.outWorkspace)
                
                # alert the user if invalid characters are present in the output table name.
                if self.fileRoot != self.validFileRoot:
                    # self.outTableParameter.setErrorMessage(self.invalidTableNameMessage)
                    self.outTableParameter.setErrorMessage(self.integerPercentageMessage)
                    
                else: # check on file extensions. None are allowed in geodatabases and only ".dbf" is allowed in folders.
                    self.workspaceExt = os.path.splitext(self.outWorkspace)[1]
                    
                    # if the workspace is a geodatabase
                    if self.workspaceExt.upper() == ".GDB":
                        if self.fileExt:
                            # alert user that file names cannot contain an extension in a GDB
                            self.outTableParameter.setErrorMessage(self.invalidExtensionMessage)               
                    else:                    
                        # get the list of acceptable filename extentions for folder locations
                        self.tableExtensions = globalConstants.tableExtensions
                        
                        if self.fileExt not in self.tableExtensions:
                            self.outTableParameter.setErrorMessage("Output tables in folders must have the '.dbf' extension.")     
        
        
        # CHECK ON SECONDARY INPUTS IF PROVIDED
        
        # if optional check box is unselected, clear the parameter message area and value area    
        if self.checkboxInParameters:
            for val in self.checkboxInParameters.values():
                for indx in val:
                    if not self.parameters[indx].enabled:
                        self.parameters[indx].clearMessage()
                        self.parameters[indx].value = ''
                        
        # Check if a raster is needed for metric calculations
        if self.inRasterIndex:
            if self.inRasterParameter.value:
                if hasattr(self.inRasterParameter.value, "dataSource"):
                    self.inRasterParameter.value = str(self.inRasterParameter.value.dataSource)
                    self.parameters[self.inRasterIndex].value = self.inRasterParameter.value
                # Check for is input raster layer has spatial reference
                #self.spRefCheck(self.inRasterParameter)
                if arcpy.Describe(self.inRasterParameter.value).spatialReference.name.lower() == "unknown":
                    self.inRasterParameter.setErrorMessage(self.noSpatialReferenceMessage)
            
                # Check if input raster is an integer grid
                inRaster = arcpy.Raster(str(self.inRasterParameter.value))
                if not inRaster.isInteger:
                    self.inRasterParameter.setErrorMessage(self.nonIntegerGridMessage)
            
                # Update Processing cell size if empty
                if not self.processingCellSizeParameter.value and not self.processingCellSizeParameter.hasError():
                    cellSize = arcpy.Raster(str(self.inRasterParameter.value)).meanCellWidth #get from metadata
                    self.processingCellSizeParameter.value = cellSize
            
                # Update Snap Raster Parameter if it is empty
                if not self.snapRasterParameter.value and not self.inRasterParameter.hasError():
                    self.snapRasterParameter.value = str(self.inRasterParameter.value)
                
        # Check if a secondary input raster is indicated - use if raster can be either integer or float
        if self.inRaster2Index:
            # if provided, check if input raster2 is defined
            if self.inRaster2Parameter.value:
                # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inRaster2Parameter.value, "dataSource"):
                    if arcpy.Describe(self.inRaster2Parameter.value.dataSource).spatialReference.name.lower() == "unknown":
                        self.inRaster2Parameter.setErrorMessage(self.noSpatialReferenceMessage)
                else:
                    if arcpy.Describe(self.inRaster2Parameter.value).spatialReference.name.lower() == "unknown":
                        self.inRaster2Parameter.setErrorMessage(self.noSpatialReferenceMessage)
        
        # Check if a secondary input integer raster is defined - use if raster has to be an integer type
        if self.inIntegerRasterIndex:
            # if provided, check if input integer raster is defined
            if self.inIntegerRasterParameter.value:
                # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inIntegerRasterParameter.value, "dataSource"):
                    if arcpy.Describe(self.inIntegerRasterParameter.value.dataSource).spatialReference.name.lower() == "unknown":
                        self.inIntegerRasterParameter.setErrorMessage(self.noSpatialReferenceMessage)
                else:
                    if arcpy.Describe(self.inIntegerRasterParameter.value).spatialReference.name.lower() == "unknown":
                        self.inIntegerRasterParameter.setErrorMessage(self.noSpatialReferenceMessage)
            
            # Check if input raster is an integer grid
            inIntegerRaster = arcpy.Raster(str(self.inIntegerRasterParameter.value))
            if not inIntegerRaster.isInteger:
                self.inIntegerRasterParameter.setErrorMessage(self.nonIntegerGridMessage)
        
        # Check if a secondary multiple input feature is indicated            
        if self.inMultiFeatureIndex:
            # if provided, get the valueTable and process each entry
            if self.inMultiFeatureParameter.value:
                multiFeatures = self.inMultiFeatureParameter.value
                rowCount = multiFeatures.rowCount
                for row in range(0, rowCount):
                    value = multiFeatures.getValue(row, 0)
                    if value:
                        # check to see if it has a spatial reference
                        d = arcpy.Describe(value)
                        if d.spatialReference.name.lower() == "unknown":
                            self.inMultiFeatureParameter.setErrorMessage(self.noSpatialReferenceMessageMulti)
                            
        # Check if a secondary vector input feature is indicated
        if self.inVector2Index:
            # check if input vector2 is defined
            if self.inVector2Parameter.value:
                # query for a dataSource attribue, if one exists, it is a lyr file. Get the lyr's data source to do a Decribe
                if hasattr(self.inVector2Parameter.value, "dataSource"):
                    if arcpy.Describe(self.inVector2Parameter.value.dataSource).spatialReference.name.lower() == "unknown":
                        self.inVector2Parameter.setErrorMessage(self.noSpatialReferenceMessage)
                else:
                    if arcpy.Describe(self.inVector2Parameter.value).spatialReference.name.lower() == "unknown":
                        self.inVector2Parameter.setErrorMessage(self.noSpatialReferenceMessage) 
                        
        # Check if a tertiary vector input feature is indicated
        if self.inVector3Index:
            # check if input vector3 is defined
            if self.inVector3Parameter.value:
                # query for a dataSource attribue, if one exists, it is a lyr file. Get the lyr's data source to do a Decribe
                if hasattr(self.inVector3Parameter.value, "dataSource"):
                    if arcpy.Describe(self.inVector3Parameter.value.dataSource).spatialReference.name.lower() == "unknown":
                        self.inVector3Parameter.setErrorMessage(self.noSpatialReferenceMessage)
                else:
                    if arcpy.Describe(self.inVector3Parameter.value).spatialReference.name.lower() == "unknown":
                        self.inVector3Parameter.setErrorMessage(self.noSpatialReferenceMessage)

        # Check if a secondary AnyRasterOrPoly dataset input feature is indicated. Use this for requiring a raster or polygon dataset.
        if self.inAnyRasterOrPolyIndex:
            # if provided, check if input geodataset1 is defined
            if self.inAnyRasterOrPolyParameter.value:
                # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inAnyRasterOrPolyParameter.value, "dataSource"):
                    desc = arcpy.Describe(self.inAnyRasterOrPolyParameter.value.dataSource)
                else:
                    desc = arcpy.Describe(self.inAnyRasterOrPolyParameter.value)

                if desc.spatialReference.name.lower() == "unknown":
                    self.inAnyRasterOrPolyParameter.setErrorMessage(self.noSpatialReferenceMessage) 
                
                if desc.datasetType == "RasterDataset":
                    # Check if input raster is an integer grid
                    inRaster = arcpy.Raster(str(self.inAnyRasterOrPolyParameter.value))
                    if inRaster.isInteger:
                        try:
                            self.inputFields2Parameter.clearMessage()
                            self.inputFields2Parameter.value = "Value"
                        except:
                            pass
                        #self.inAnyRasterOrPolyParameter.setErrorMessage(self.integerGridOrPolgonMessage)
                    else:
                        try:
                            self.inputFields2Parameter.value = ''
                        except:
                            pass
                elif desc.shapeType.lower() != "polygon":
                        self.inAnyRasterOrPolyParameter.setErrorMessage(self.polygonOrIntegerGridMessage)
                        
        # Check if a secondary intRasterOrPoly input feature is indicated. Use this for requiring an integer raster or polygon dataset.
        if self.inIntRasterOrPolyIndex:
            # if provided, check if input geodataset is defined
            if self.inIntRasterOrPolyParameter.value:
                # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inIntRasterOrPolyParameter.value, "dataSource"):
                    desc = arcpy.Describe(self.inIntRasterOrPolyParameter.value.dataSource)
                else:
                    desc = arcpy.Describe(self.inIntRasterOrPolyParameter.value)

                if desc.spatialReference.name.lower() == "unknown":
                    self.inIntRasterOrPolyParameter.setErrorMessage(self.noSpatialReferenceMessage) 
                
                if desc.datasetType == "RasterDataset":
                    # Check if input raster is an integer grid
                    inRaster = arcpy.Raster(str(self.inIntRasterOrPolyParameter.value))
                    if not inRaster.isInteger:
                        self.inIntRasterOrPolyParameter.setErrorMessage(self.integerGridOrPolgonMessage)

                else:
                    if desc.shapeType.lower() != "polygon":
                        self.inIntRasterOrPolyParameter.setErrorMessage(self.polygonOrIntegerGridMessage)                        

        # Check if a secondary intRasterOrVector input feature is indicated. Use this for requiring an integer raster or vector dataset.
        if self.inIntRasterOrVectorIndex:
            # if provided, check if input geodataset is defined
            if self.inIntRasterOrVectorParameter.value:
                # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inIntRasterOrVectorParameter.value, "dataSource"):
                    desc = arcpy.Describe(self.inIntRasterOrVectorParameter.value.dataSource)
                else:
                    desc = arcpy.Describe(self.inIntRasterOrVectorParameter.value)
                
                if desc.spatialReference.name.lower() == "unknown":
                    self.inIntRasterOrVectorParameter.setErrorMessage(self.noSpatialReferenceMessage) 
                
                if desc.datasetType == "RasterDataset":
                    # Check if input raster is an integer grid
                    inRaster = arcpy.Raster(str(self.inIntRasterOrVectorParameter.value))
                    if inRaster.isInteger:
                        self.inIntRasterOrVectorFieldsParameter.clearMessage()
                        self.inIntRasterOrVectorFieldsParameter.value = ""
                        self.inIntRasterOrVectorFieldsParameter.value = "Value"
                    else:
                        self.inIntRasterOrVectorParameter.setErrorMessage(self.integerGridOrVectorMessage)
                
                else:
                    acceptedVectors = ["polygon", "polyline", "point"]
                    if desc.shapeType.lower() not in acceptedVectors:
                        self.inIntRasterOrVectorParameter.setErrorMessage(self.vectorOrIntegerGridMessage)
                    
                    # ### check to see if the id field has any values
                    # if self.inIntRasterOrVectorParameter.value:
                    #     self.tableName = self.inIntRasterOrVectorParameter.valueAsText
                    #     self.fieldName = self.inIntRasterOrVectorFieldsParameter.valueAsText
                    #
                    #     # get the directory path and the filename
                    #     self.aWorkspace = os.path.split(self.tableName)[0]
                    #     self.aTableFilename = os.path.split(self.tableName)[1]
                    #
                    #     self.whereClause = f"{self.fieldName} IS NOT NULL"
                    #     if not arcpy.SearchCursor(self.tableName, self.whereClause).next():
                    #         self.inIntRasterOrVectorFieldsParameter.setErrorMessage(self.noFeaturesMessage)
        
        # Check if processingCellSize is a value greater than zero   
        if self.processingCellSizeIndex:        
            if self.processingCellSizeParameter.value:
                try:
                    cellSizeValue = arcpy.Raster(str(self.processingCellSizeParameter.value)).meanCellWidth
                except:
                    cellSizeValue = self.processingCellSizeParameter.value
                if float(str(cellSizeValue)) <= 0:
                    self.processingCellSizeParameter.setErrorMessage(self.greaterThanZeroMessage)
                        
        # Check if distance input (e.g., buffer width, edge width) is a value greater than zero            
        if self.inDistanceIndex:
            if not self.inDistanceParameter.enabled:
                self.inDistanceParameter.clearMessage()
            else:
                if self.inDistanceParameter.value:
                    distanceValue = self.inDistanceParameter.value
                    # use the split function so this routine can be used for both long and linear unit data types
                    strDistance = str(distanceValue).split()[0]
                    if float(strDistance) <= 0.0:
                        self.inDistanceParameter.setErrorMessage(self.greaterThanZeroMessage)
                else:
                    # need the else condition as a 0 value won't trigger the if clause 
                    self.inDistanceParameter.setErrorMessage(self.greaterThanZeroMessage)
        
        # Check if linear distance input (e.g., buffer width, edge width) is a value greater than or equal to zero            
        if self.inZeroDistanceIndex:
            if not self.inZeroDistanceParameter.enabled:
                self.inZeroDistanceParameter.clearMessage()
            else:
                if self.inZeroDistanceParameter.value:
                    distanceValue = self.inZeroDistanceParameter.value
                    # use the split function so this routine can be used for both long and linear unit data types
                    strNumber = str(distanceValue).split()[0]
                    if float(strNumber) < 0.0:
                        self.inZeroDistanceParameter.setErrorMessage(self.zeroOrGreaterNumberMessage)

        # Check if distance input (e.g., buffer width, edge width) is a positive number and an integer            
        if self.inIntegerDistanceIndex:
            if not self.inIntegerDistanceParameter.enabled:
                self.inIntegerDistanceParameter.clearMessage()
            else:
                if self.inIntegerDistanceParameter.value:
                    integerDistanceValue = self.inIntegerDistanceParameter.value
                    # use the split function so this routine can be used for both long and linear unit data types
                    strIntegerDistance = str(integerDistanceValue).split()[0]
                    integerDistance = float(strIntegerDistance)
                    valModulus = modf(integerDistance)
                    if valModulus[0] != 0 or valModulus[1] < 1.0:
                        self.inIntegerDistanceParameter.setErrorMessage(self.greaterThanZeroIntegerMessage)    
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.inIntegerDistanceParameter.setErrorMessage(self.greaterThanZeroIntegerMessage)

        # Check if distance input (e.g., maximum separation) is a positive number or zero           
        if self.inWholeNumIndex:
            if not self.inWholeNumParameter.enabled:
                self.inWholeNumParameter.clearMessage()
            else:
                if self.inWholeNumParameter.value:
                    wholeNumValue = self.inWholeNumParameter.value
                    if wholeNumValue < 0.0:
                        self.inWholeNumParameter.setErrorMessage(self.zeroOrGreaterNumberMessage)
        
        # Check if number input (e.g., slope threshold) is a positive integer including zero           
        if self.inZeroAndAboveIntegerIndex:
            if not self.inZeroAndAboveIntegerParameter.enabled:
                self.inZeroAndAboveIntegerParameter.clearMessage()
            else:
                if self.inZeroAndAboveIntegerParameter.value:
                    zeroAndAboveValue = self.inZeroAndAboveIntegerParameter.value
                    valModulus = modf(zeroAndAboveValue)
                    if valModulus[0] != 0 or valModulus[1] < 1.0:
                        self.inZeroAndAboveIntegerParameter.setErrorMessage(self.zeroOrGreaterIntegerMessage) 

        # Check if number input (e.g., number of cells) is a positive integer greater than zero       
        if self.inPositiveIntegerIndex:
            # This parameter can be linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.inPositiveIntegerParameter.enabled:
                self.inPositiveIntegerParameter.clearMessage()
            else:
                if self.inPositiveIntegerParameter.value:
                    positiveIntValue = self.inPositiveIntegerParameter.value
                    valModulus = modf(positiveIntValue)
                    if valModulus[0] != 0 or valModulus[1] < 1.0:
                        self.inPositiveIntegerParameter.setErrorMessage(self.greaterThanZeroIntegerMessage)    
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.inPositiveIntegerParameter.setErrorMessage(self.greaterThanZeroIntegerMessage)
                    
        # Check if number input (e.g., number of cells) is a positive integer greater than zero 
        if self.inPositiveInteger2Index:
            # This parameter can be linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.inPositiveInteger2Parameter.enabled:
                self.inPositiveInteger2Parameter.clearMessage()
            else:
                if self.inPositiveInteger2Parameter.value:
                    positiveInt2Value = self.inPositiveInteger2Parameter.value
                    val2Modulus = modf(positiveInt2Value)
                    if val2Modulus[0] != 0 or val2Modulus[1] < 1.0:
                        self.inPositiveInteger2Parameter.setErrorMessage(self.greaterThanZeroIntegerMessage)  
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.inPositiveInteger2Parameter.setErrorMessage(self.greaterThanZeroIntegerMessage)
                
        # Check if number input (e.g., cell size) is a positive number greater than zero        
        if self.inPositiveNumberIndex:
            # This parameter can be linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.inPositiveNumberParameter.enabled:
                self.inPositiveNumberParameter.clearMessage()
            else:
                if self.inPositiveNumberParameter.value:
                    positiveValue = self.inPositiveNumberParameter.value
                    if positiveValue <= 0.0:
                        self.inPositiveNumberParameter.setErrorMessage(self.greaterThanZeroMessage)  
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.inPositiveNumberParameter.setErrorMessage(self.greaterThanZeroMessage)
        
        # Check if number input (e.g., burn in value) is in the set of invalid numbers (i.e., 0 to 100)
        if self.validNumberIndex:
            # This parameter is often linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.validNumberParameter.enabled:
                self.validNumberParameter.clearMessage()
            else:
                if self.validNumberParameter.value:
                    invalidNumbers = set((range(101)))
                    enteredValue = self.validNumberParameter.value
                    if enteredValue in invalidNumbers:
                        self.validNumberParameter.setErrorMessage(self.invalidNumberMessage)
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.validNumberParameter.setErrorMessage(self.invalidNumberMessage)
        
        # Check if number input (e.g., percent view threshold) is in the set of valid numbers (i.e., 1 to 100)
        if self.integerPercentageIndex:
            # This parameter is often linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.integerPercentageParameter.enabled:
                self.integerPercentageParameter.clearMessage()
            else:
                if self.integerPercentageParameter.value:
                    validIntegers = set((range(1,101)))
                    pctValue = self.integerPercentageParameter.value
                    if pctValue not in validIntegers:
                        self.integerPercentageParameter.setErrorMessage(self.integerPercentageMessage)
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.integerPercentageParameter.setErrorMessage(self.integerPercentageMessage)                    
        
        # Check if distance input (e.g., buffer width, edge width) is a positive number greater than zero
        if self.inLinearUnitIndex:
            # This parameter can be linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.inLinearUnitParameter.enabled:
                self.inLinearUnitParameter.clearMessage()
            else:
                if self.inLinearUnitParameter.value:
                    linearUnitValue = self.inLinearUnitParameter.value
                    # use the split function so this routine can be used for both long and linear unit data types
                    strLinearUnit = str(linearUnitValue).split()[0]
                    if float(strLinearUnit) <= 0.0:
                        self.inLinearUnitParameter.setErrorMessage(self.greaterThanZeroMessage)

        # Check if a secondary raster output is indicated      
        if self.outRasterIndex:
            # Check if output raster has a valid filename; it contains no invalid characters, has no extension other than 
            # those found in globalConstants.rasterExtensions if the output location is in a folder, and has no extension 
            # if the output is to be placed in a geodatabase.
            if self.outRasterParameter.value:
                self.outRasterName = self.outRasterParameter.valueAsText
            
                # get the directory path and the filename
                self.outRasterWorkspace = os.path.split(self.outRasterName)[0]
                self.rasterFilename = os.path.split(self.outRasterName)[1]
                
                # break the filename into its root and extension
                self.rasterFileRoot = os.path.splitext(self.rasterFilename)[0]
                self.rasterFileExt = os.path.splitext(self.rasterFilename)[1]
                
                # substitue valid characters into the filename root if any invalid characters are present
                self.validRasterFileRoot = arcpy.ValidateTableName(self.rasterFileRoot,self.outRasterWorkspace)
                
                # alert the user if invalid characters are present in the output table name.
                if self.rasterFileRoot != self.validRasterFileRoot:
                    self.outRasterParameter.setErrorMessage(self.invalidTableNameMessage)
                    
                elif self.rasterFileExt: # check on file extensions. None are allowed in geodatabases and only certain extensions are allowed in folders.
                    self.rasterWorkspaceExt = os.path.splitext(self.outRasterWorkspace)[1]
                    
                    # if the workspace is a geodatabase
                    if self.rasterWorkspaceExt.upper() == ".GDB":
                        # alert user that file names cannot contain an extension in a GDB
                        self.outRasterParameter.setErrorMessage(self.invalidExtensionMessage)               
                    else:                    
                        # get the list of acceptable filename extentions for folder locations
                        # self.rasterExtensions = globalConstants.rasterExtensions
                        self.rasterExtensions = [".img", ".tif"]
                        
                        if self.rasterFileExt not in self.rasterExtensions:
                            self.outRasterParameter.setErrorMessage("Valid extensions for rasters in folders for this tool are: %s." % str(self.rasterExtensions))           

                    
class NoReportingUnitValidator(object):
    """ Class for inheritance by ToolValidator Only
    
        This currently serves the following tools:
            Land Cover on Slope Proportions
            Land Cover Proportions
    

        
        Description of ArcToolbox parameters:
        -------------------------------------
        
        inTableIndex:  Vector Feature input that occupies parameter 0
           
        inRasterIndex:  One parameter
        1. Raster Layer
        
        startIndex:  Three consecutive parameters 
        1. String: default  
        2. File: filter=lccFileExtension
        3. String:  MultiValue=Yes; 
        
        outTableIndex: Index of output table parameter
        1. table: required, output
        
        processingCellSizeIndex:  Index of optional processing cell size parameter
        1. Analysis cell size
        
        snapRasterIndex:  Index of optional snap raster parameter
        1. Raster Layer
        
        optionalFieldsIndex:  index of optional fields parameter
        1. String: Properties: MultiValue=Yes
        
    
    """
    
    # Indexes of input parameters
    inTableIndex = 0 
    inRasterIndex = 0  
    startIndex = 0  
    processingCellSizeIndex = 0
    outTableIndex = 0 
    snapRasterIndex = 0 
    optionalFieldsIndex = 0
    
    # Indexes of secondary input parameters
    inRaster2Index = 0
    inIntegerRasterIndex = 0
    inMultiFeatureIndex = 0
    inVector2Index = 0
    inAnyRasterOrPolyIndex = 0
    inIntRasterOrPolyIndex = 0
    inputFields2Index = 0
    inDistanceIndex = 0
    inIntegerDistanceIndex = 0
    inDistance2Index = 0
    inWholeNumIndex = 0
    inPositiveIntegerIndex = 0
    inPositiveInteger2Index = 0
    inLinearUnitIndex = 0
    checkbox1Index = 0
    checkbox2Index = 0
    checkboxInParameters = {}
    outWorkspaceIndex = 0
    outRasterIndex = 0
    validNumberIndex = 0
    inPositiveNumberIndex = 0
    inZeroAndAboveIntegerIndex = 0
    integerPercentageIndex = 0
    menu1Index = 0
    menuInParameters = {}
        
    # Additional local variables
    srcDirName = ""
    
    # Metric Specific
    filterList = []
    overrideAttributeName = ""
    fieldPrefix = ""
    fieldSuffix = ""
    metricShortName = ""
    
    def __init__(self):
        """ ESRI - Initialize ToolValidator class"""
 
        # Load metric constants        
        self.inputIdFieldTypes = validatorConstants.inputIdFieldTypes
        self.lccSchemeUserOption = validatorConstants.userOption
        self.metricAddDescription = globalConstants.metricAddDescription      
        self.metricDescription = validatorConstants.metricDescription
        self.noFeaturesMessage = validatorConstants.noFeaturesMessage
        self.noSpatialReferenceMessage = validatorConstants.noSpatialReferenceMessage
        self.noProjectionInOutputCS = validatorConstants.noProjectionInOutputCS
        self.noSpatialReferenceMessageMulti = validatorConstants.noSpatialReferenceMessageMulti
        self.nonIntegerGridMessage = validatorConstants.nonIntegerGridMessage
        self.greaterThanZeroMessage = validatorConstants.greaterThanZeroMessage
        self.greaterThanZeroIntegerMessage = validatorConstants.greaterThanZeroIntegerMessage
        self.zeroOrGreaterNumberMessage = validatorConstants.zeroOrGreaterNumberMessage
        self.zeroOrGreaterIntegerMessage = validatorConstants.zeroOrGreaterIntegerMessage
        self.integerGridOrPolgonMessage = validatorConstants.integerGridOrPolgonMessage
        self.polygonOrIntegerGridMessage = validatorConstants.polygonOrIntegerGridMessage
        self.invalidTableNameMessage = validatorConstants.invalidTableNameMessage
        self.invalidNumberMessage = validatorConstants.invalidNumberMessage
        self.invalidExtensionMessage = validatorConstants.invalidExtensionMessage
        self.integerPercentageMessage = validatorConstants.integerPercentageMessage
        self.noSpatialAnalystMessage = validatorConstants.noSpatialAnalystMessage
        
        # Load global constants
        self.optionalFieldsName = validatorConstants.optionalFieldsName
#        self.qaCheckDescription = globalConstants.qaCheckDescription

        # Load LCC constants
        self.lccFileDirName = lccConstants.PredefinedFileDirName       
        self.lccFileExtension = lccConstants.XmlFileExtension
        self.idAttributeName = lccConstants.XmlAttributeId
        self.nameAttributeName = lccConstants.XmlAttributeName
        self.classElementName = lccConstants.XmlElementClass
        self.filterAttributeName = lccConstants.XmlAttributeFilter
        
        # Set relative indexes
        self.lccFilePathIndex = self.startIndex + 1
        self.lccClassesIndex = self.startIndex + 2
#        self.inputFieldsIndex = self.inTableIndex + 1
        
        # Assign parameters to local variables
        self.parameters = arcpy.GetParameterInfo()
        self.inputTableParameter = self.parameters[self.inTableIndex]
#        self.inputFieldsParameter = self.parameters[self.inputFieldsIndex]
        self.lccSchemeParameter =  self.parameters[self.startIndex]
        self.lccFilePathParameter = self.parameters[self.lccFilePathIndex]
        self.lccClassesParameter = self.parameters[self.lccClassesIndex]
        self.processingCellSizeParameter = self.parameters[self.processingCellSizeIndex]
        self.inRasterParameter = self.parameters[self.inRasterIndex]
        if self.outTableIndex != -1: # Tools without an output table should have a value of -1 for the outTableIndex
            self.outTableParameter = self.parameters[self.outTableIndex]
        self.snapRasterParameter = self.parameters[self.snapRasterIndex]
        self.optionsParameter = self.parameters[self.optionalFieldsIndex]
        
        # Assign secondary input parameters to local variables
        if self.inRaster2Index:
            self.inRaster2Parameter = self.parameters[self.inRaster2Index]
            
        if self.inIntegerRasterIndex:
            self.inIntegerRasterParameter = self.parameters[self.inIntegerRasterIndex]
            
        if self.inMultiFeatureIndex:
            self.inMultiFeatureParameter = self.parameters[self.inMultiFeatureIndex]
            
        if self.inVector2Index:
            self.inVector2Parameter = self.parameters[self.inVector2Index]
            
        if self.inDistanceIndex:
            self.inDistanceParameter = self.parameters[self.inDistanceIndex]
            
        if self.inIntegerDistanceIndex:
            self.inIntegerDistanceParameter = self.parameters[self.inIntegerDistanceIndex]
            
        if self.inDistance2Index:
            self.inDistance2Parameter = self.parameters[self.inDistance2Index]
            
        if self.inWholeNumIndex:
            self.inWholeNumParameter = self.parameters[self.inWholeNumIndex]
            
        if self.inPositiveIntegerIndex:
            self.inPositiveIntegerParameter = self.parameters[self.inPositiveIntegerIndex]
            
        if self.inPositiveInteger2Index:
            self.inPositiveInteger2Parameter = self.parameters[self.inPositiveInteger2Index]

        if self.validNumberIndex:
            self.validNumberParameter = self.parameters[self.validNumberIndex]
        
        if self.inLinearUnitIndex:
            self.inLinearUnitParameter = self.parameters[self.inLinearUnitIndex]

        if self.checkbox1Index:
            self.checkbox1Parameter = self.parameters[self.checkbox1Index]
            
        if self.checkbox2Index:
            self.checkbox2Parameter = self.parameters[self.checkbox2Index]
            
        if self.inIntRasterOrPolyIndex:
            self.inIntRasterOrPolyParameter = self.parameters[self.inIntRasterOrPolyIndex]
            
        if self.inAnyRasterOrPolyIndex:
            self.inAnyRasterOrPolyParameter = self.parameters[self.inAnyRasterOrPolyIndex]
            
        if self.inputFields2Index:
            self.inputFields2Parameter = self.parameters[self.inputFields2Index]
            
        if self.outWorkspaceIndex:
            self.outWorkspaceParameter = self.parameters[self.outWorkspaceIndex]
            
        if self.outRasterIndex:
            self.outRasterParameter = self.parameters[self.outRasterIndex]
            
        if self.inPositiveNumberIndex:
            self.inPositiveNumberParameter = self.parameters[self.inPositiveNumberIndex]
            
        if self.inZeroAndAboveIntegerIndex:
            self.inZeroAndAboveIntegerParameter = self.parameters[self.inZeroAndAboveIntegerIndex]
        
        if self.integerPercentageIndex:
            self.integerPercentageParameter = self.parameters[self.integerPercentageIndex]
            
        if self.menu1Index:
            self.menu1Parameter = self.parameters[self.menu1Index]

               
        # Additional local variables
        self.currentFilePath = ""
        self.ruFilePath = ""
        self.initialized = False


    def initializeParameters(self):
        """ ESRI - Initialize parameters"""
        
        # disable dependent input fields until optional check boxes are selected    
        if self.checkboxInParameters:
            for val in self.checkboxInParameters.values():
                for indx in val:
                    self.parameters[indx].enabled = False 
                    
        if self.menuInParameters:
            for val in list(self.menuInParameters.values()):
                for indx in val:
                    self.parameters[indx].enabled = False 
            
        
        # Populate predefined LCC dropdown
        self.lccFileDirSearch = os.path.join(self.srcDirName, self.lccFileDirName, "*" + self.lccFileExtension)
        
        filterList = []
        self.lccLookup = {}
                
        for lccPath in glob(self.lccFileDirSearch):
            lccSchemeName = os.path.basename(lccPath).rstrip(self.lccFileExtension)
            filterList.append(lccSchemeName)
            self.lccLookup[lccSchemeName] = lccPath
            
        self.lccSchemeParameter.filter.list = filterList + [self.lccSchemeUserOption]
        self.lccFilePathParameter.enabled = False
        self.lccClassesParameter.enabled = False
                
        # Move parameters to optional section
        self.optionsParameter.category = self.optionalFieldsName
        
        # Set options filter
        self.optionsParameter.filter.list = self.filterList
        
        self.initialized = True
        
        
    def updateParameters(self):
        """ ESRI - Modify the values and properties of parameters before internal validation is performed.  
        
            This method is called whenever a parameter has been changed.
        
        """
        #arcpy.AddMessage("\n\n\updateParameters 0\n\n\n");
        if not self.initialized:
            self.initializeParameters()

        self.updateInputLccParameters()
#        self.updateInputFieldsParameter()
        self.updateOutputTableParameter()
        
        if self.menu1Index:
            menuKey = self.menu1Parameter.value
            
            for val in list(self.menuInParameters.values()):
                for indx in val:
                    if indx in self.menuInParameters[menuKey]:
                        self.parameters[indx].enabled = True
                    else:
                        self.parameters[indx].enabled = False

        
        # if checkboxes are provided, use the indexes specified in the tool's validation script to identify the 
        # parameter locations of any additional needed inputs for that checkbox and enable those parameters
        if self.checkbox1Index:
            cboxListeners = list(self.checkboxInParameters.values())[0]
            self.updateCheckboxParameters(self.checkbox1Parameter, cboxListeners)

        if self.checkbox2Index:
            #cboxListeners = self.checkboxInParameters.values()[1]
            cboxListeners = list(self.checkboxInParameters.values())[1]
            self.updateCheckboxParameters(self.checkbox2Parameter, cboxListeners)
                
            
    def updateCheckboxParameters(self, checkboxParameter, cboxListeners):
        if checkboxParameter.value:
            for indx in cboxListeners:
                self.parameters[indx].enabled = True


    def updateOutputTableParameter(self):
        """ Update an output table parameter
        
        **Description:**
            
            Removes .shp that is automatically generated for output table parameters and replaces it with .dbf
        
        """
        # Tools without an output table should have a value of -1 for the outTableIndex
        if self.outTableIndex != -1:
            if self.outTableParameter.value:
                    outTablePath = str(self.outTableParameter.value)
                    self.outTableParameter.value  = outTablePath.replace('.shp', '.dbf')

    
    def updateInputLccParameters(self):
        """ Update Land Cover Classification Parameters 
        
            These parameters include LCC file path and list of classes with checkboxes.
        
        """
        
        # Converts None to "None", so must do a check
        lccSchemeName = ""
        if self.lccSchemeParameter.value:
            lccSchemeName = str(self.lccSchemeParameter.value)

        # User defined LCC Scheme
        lccFilePath = ""
        if  lccSchemeName == self.lccSchemeUserOption:
            lccFilePath = str(self.lccFilePathParameter.value)      
            self.lccFilePathParameter.enabled = True
            
        # Pre-defined  LCC Scheme  
        elif lccSchemeName:
            lccFilePath = self.lccLookup[lccSchemeName]
            
            # Delete user defined file path in dialog
            self.lccFilePathParameter.value = lccFilePath
            self.lccFilePathParameter.enabled = False

        
        # Get list of LCC names with description
        classNames = []
        if lccFilePath and self.currentFilePath != lccFilePath and os.path.isfile(lccFilePath):
            self.currentFilePath = lccFilePath
            classNames = self.getLccList(lccFilePath)
  
        # Populate checkboxes with LCC name and description
        if classNames:
            self.lccClassesParameter.enabled = True
        else:
            self.lccClassesParameter.enabled = False  
            self.lccClassesParameter.value = ""
        
        # Prevent the changing of the classification scheme from causing dialog errors when metrics are already checked    
        if not self.lccSchemeParameter.hasBeenValidated:
            self.lccClassesParameter.value = ""
            
        self.lccClassesParameter.filter.list = classNames
        
        
    def getLccList(self, lccFilePath):
        classNames = []
        lccDocument = parse(lccFilePath)
        classNodes = lccDocument.getElementsByTagName(self.classElementName)
        

        message = self.metricDescription
        for classNode in classNodes:
            
            # ignore class without value as descendant(child, child of child, etc.)
            if not classNode.getElementsByTagName(lccConstants.XmlElementValue):
                continue
            
            # Check filter, skip class if short metric name found (semi-colon delimiter)
            filterValue = classNode.getAttribute(self.filterAttributeName)
            shortNames = filterValue.split(";")
            if self.metricShortName in shortNames:
                continue
            
            classId = classNode.getAttribute(self.idAttributeName)
            name = classNode.getAttribute(self.nameAttributeName)     
            
            # Check for field override, ie NINDEX, UINDEX
            fieldName = classNode.getAttribute(self.overrideAttributeName)
            if not fieldName:
                fieldName = self.fieldPrefix + classId + self.fieldSuffix
            
            className = message.format(classId, fieldName, name)
            classNames.append(className)   
            
        return classNames
        
        
#     def updateInputFieldsParameter(self):
#         """  Set selected input field to first field of specified type
#             
#              Specified types comes from self.inputIdFieldTypes set in __init__()
#              
#         """
#         
#         fieldTypes = set(self.inputIdFieldTypes)
#         tablePath = self.inputTableParameter.value
#         fieldName = self.inputFieldsParameter.value
#         
#         # Proceed only if table path exists, but field name hasn't been set
#         if tablePath and not fieldName:
#             try:
#                 fields = arcpy.ListFields(tablePath)
#                 
#                 for field in fields:
#                     if field.type in fieldTypes:
#                         self.inputFieldsParameter.value = field.name
#                         break
#                     
#                 if not self.inputFieldsParameter.value:
#                     for field in fields:
#                         if field.type == "OID":
#                             self.inputFieldsParameter.value = field.name
#                             break
#                         
#             except:
#                 pass
                
        
    def updateMessages(self):
        """ ESRI - Modify the messages created by internal validation for each tool parameter.  
        
            This method is called after internal validation.
            
        """
        
        if self.spatialNeeded and arcpy.CheckExtension("Spatial") != "Available":
            self.parameters[0].setErrorMessage(self.noSpatialAnalystMessage)

        # Set lcc file parameter required only if user-defined is set
        if self.lccSchemeParameter.value != self.lccSchemeUserOption:
            self.lccFilePathParameter.clearMessage()
            
        # Clear required on disabled lcc class selection
        if not self.lccClassesParameter.enabled:
            self.lccClassesParameter.clearMessage()
        
        # Remove required on optional fields
        self.optionsParameter.clearMessage()
        
        # Set optional raster options if env is set
        if not self.processingCellSizeParameter.value:
            try:
                envCellSize = int(arcpy.env.cellSize)
            except:
                envCellSize = None
            if envCellSize:
                self.processingCellSizeParameter.value = envCellSize
                
        # Set optional snap raster if env is set
        if not self.snapRasterParameter.value:
            self.snapRasterParameter.value = arcpy.env.snapRaster
            
        # Check if input raster is defined
        if self.inRasterParameter.value:
           
            if hasattr(self.inRasterParameter.value, "dataSource"):
                self.inRasterParameter.value = str(self.inRasterParameter.value.dataSource)
                self.parameters[self.inRasterIndex].value = self.inRasterParameter.value
            # Check for is input raster layer has spatial reference
            #self.spRefCheck(self.inRasterParameter)
            if arcpy.Describe(self.inRasterParameter.value).spatialReference.name.lower() == "unknown":
                self.inRasterParameter.setErrorMessage(self.noSpatialReferenceMessage)
            
            # Check if input raster is an integer grid
            inRaster = arcpy.Raster(str(self.inRasterParameter.value))
            if not inRaster.isInteger:
                self.inRasterParameter.setErrorMessage(self.nonIntegerGridMessage)
            
            # Update Processing cell size if empty
            if not self.processingCellSizeParameter.value and not self.processingCellSizeParameter.hasError():
                cellSize = arcpy.Raster(str(self.inRasterParameter.value)).meanCellWidth #get from metadata
                self.processingCellSizeParameter.value = cellSize
            
            # Update Snap Raster Parameter if it is empty
            if not self.snapRasterParameter.value and not self.inRasterParameter.hasError():
                self.snapRasterParameter.value = str(self.inRasterParameter.value)
            
        # Check input features
        if self.inputTableParameter.value and not self.inputTableParameter.hasError():
         
            # Check for if input feature layer has spatial reference
            # # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
            if hasattr(self.inputTableParameter.value, "dataSource"):
                if arcpy.Describe(self.inputTableParameter.value.dataSource).spatialReference.name.lower() == "unknown":
                    self.inputTableParameter.setErrorMessage(self.noSpatialReferenceMessage)
            else:
                if arcpy.Describe(self.inputTableParameter.value).spatialReference.name.lower() == "unknown":
                    self.inputTableParameter.setErrorMessage(self.noSpatialReferenceMessage)

        # Check if processingCellSize is a value greater than zero          
        if self.processingCellSizeParameter.value:
            try:
                cellSizeValue = arcpy.Raster(str(self.processingCellSizeParameter.value)).meanCellWidth
            except:
                cellSizeValue = self.processingCellSizeParameter.value
            if float(str(cellSizeValue)) <= 0:
                self.processingCellSizeParameter.setErrorMessage(self.greaterThanZeroMessage) 
              
        # Check if output table has a valid filename; it contains no invalid characters, has no extension other than '.dbf' 
        # if the output location is in a folder, and has no extension if the output is to be placed in a geodatabase.
        # Tools without an output table should have a value of -1 for the outTableIndex 
        if self.outTableIndex != -1:
            if self.outTableParameter.value:
                self.outTableName = self.outTableParameter.valueAsText
            
                # get the directory path and the filename
                self.outWorkspace = os.path.split(self.outTableName)[0]
                self.tableFilename = os.path.split(self.outTableName)[1]
                
                # break the filename into its root and extension
                self.fileRoot = os.path.splitext(self.tableFilename)[0]
                self.fileExt = os.path.splitext(self.tableFilename)[1]
                
                # substitue valid characters into the filename root if any invalid characters are present
                self.validFileRoot = arcpy.ValidateTableName(self.fileRoot,self.outWorkspace)
                
                # alert the user if invalid characters are present in the output table name.
                if self.fileRoot != self.validFileRoot:
                    self.outTableParameter.setErrorMessage(self.invalidTableNameMessage)
                    
                else: # check on file extensions. None are allowed in geodatabases and only ".dbf" is allowed in folders.
                    self.workspaceExt = os.path.splitext(self.outWorkspace)[1]
                    
                    # if the workspace is a geodatabase
                    if self.workspaceExt.upper() == ".GDB":
                        if self.fileExt:
                            # alert user that file names cannot contain an extension in a GDB
                            self.outTableParameter.setErrorMessage(self.invalidExtensionMessage)               
                    else:                    
                        # get the list of acceptable filename extentions for folder locations
                        self.tableExtensions = globalConstants.tableExtensions
                        
                        if self.fileExt not in self.tableExtensions:
                            self.outTableParameter.setErrorMessage("Output tables in folders must have the '.dbf' extension.")
        
        
        # CHECK ON SECONDARY INPUTS IF PROVIDED
        
        # if optional check box is unselected, clear the parameter message area and value area    
        if self.checkboxInParameters:
            for val in self.checkboxInParameters.values():
                for indx in val:
                    if not self.parameters[indx].enabled:
                        self.parameters[indx].clearMessage()
                        self.parameters[indx].value = ''

        if self.menuInParameters:
            for val in list(self.menuInParameters.values()):
                for indx in val:
                    if not self.parameters[indx].enabled:
                        self.parameters[indx].clearMessage()
                        self.parameters[indx].value = ''
        
        # Check if a secondary input raster is indicated - use if raster can be either integer or float
        if self.inRaster2Index:
            # if provided, check if input raster2 is defined
            if self.inRaster2Parameter.value:
                # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inRaster2Parameter.value, "dataSource"):
                    if arcpy.Describe(self.inRaster2Parameter.value.dataSource).spatialReference.name.lower() == "unknown":
                        self.inRaster2Parameter.setErrorMessage(self.noSpatialReferenceMessage)
                else:
                    if arcpy.Describe(self.inRaster2Parameter.value).spatialReference.name.lower() == "unknown":
                        self.inRaster2Parameter.setErrorMessage(self.noSpatialReferenceMessage)
                        
        # Check if a secondary input integer raster is defined - use if raster has to be an integer type
        if self.inIntegerRasterIndex:
            # if provided, check if input integer raster is defined
            if self.inIntegerRasterParameter.value:
                # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inIntegerRasterParameter.value, "dataSource"):
                    if arcpy.Describe(self.inIntegerRasterParameter.value.dataSource).spatialReference.name.lower() == "unknown":
                        self.inIntegerRasterParameter.setErrorMessage(self.noSpatialReferenceMessage)
                else:
                    if arcpy.Describe(self.inIntegerRasterParameter.value).spatialReference.name.lower() == "unknown":
                        self.inIntegerRasterParameter.setErrorMessage(self.noSpatialReferenceMessage)
            
            # Check if input raster is an integer grid
            inIntegerRaster = arcpy.Raster(str(self.inIntegerRasterParameter.value))
            if not inIntegerRaster.isInteger:
                self.inIntegerRasterParameter.setErrorMessage(self.nonIntegerGridMessage)
                
        # Check if a secondary multiple input feature is indicated            
        if self.inMultiFeatureIndex:
            # if provided, get the valueTable and process each entry
            if self.inMultiFeatureParameter.value:
                multiFeatures = self.inMultiFeatureParameter.value
                rowCount = multiFeatures.rowCount
                for row in range(0, rowCount):
                    value = multiFeatures.getValue(row, 0)
                    if value:
                        # check to see if it has a spatial reference
                        d = arcpy.Describe(value)
                        if d.spatialReference.name.lower() == "unknown":
                            self.inMultiFeatureParameter.setErrorMessage(self.noSpatialReferenceMessageMulti)
                            
        # Check if a secondary vector input feature is indicated
        if self.inVector2Index:
            # if provided, check if input vector2 is defined
            if self.inVector2Parameter.value:
                # query for a dataSource attribue, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inVector2Parameter.value, "dataSource"):
                    if arcpy.Describe(self.inVector2Parameter.value.dataSource).spatialReference.name.lower() == "unknown":
                        self.inVector2Parameter.setErrorMessage(self.noSpatialReferenceMessage)
                else:
                    if arcpy.Describe(self.inVector2Parameter.value).spatialReference.name.lower() == "unknown":
                        self.inVector2Parameter.setErrorMessage(self.noSpatialReferenceMessage) 

        # Check if a secondary AnyRasterOrPoly dataset input feature is indicated. Use this for requiring a raster or polygon dataset.
        if self.inAnyRasterOrPolyIndex:
            # if provided, check if input geodataset1 is defined
            if self.inAnyRasterOrPolyParameter.value:
                # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inAnyRasterOrPolyParameter.value, "dataSource"):
                    desc = arcpy.Describe(self.inAnyRasterOrPolyParameter.value.dataSource)
                else:
                    desc = arcpy.Describe(self.inAnyRasterOrPolyParameter.value)

                if desc.spatialReference.name.lower() == "unknown":
                    self.inAnyRasterOrPolyParameter.setErrorMessage(self.noSpatialReferenceMessage) 
                
                if desc.datasetType == "RasterDataset":
                    # Check if input raster is an integer grid
                    inRaster = arcpy.Raster(str(self.inAnyRasterOrPolyParameter.value))
                    if inRaster.isInteger:
                        try:
                            self.inputFields2Parameter.clearMessage()
                            self.inputFields2Parameter.value = "Value"
                        except:
                            pass
                        #self.inAnyRasterOrPolyParameter.setErrorMessage(self.integerGridOrPolgonMessage)
                    else:
                        try:
                            self.inputFields2Parameter.value = ''
                        except:
                            pass
                elif desc.shapeType.lower() != "polygon":
                        self.inAnyRasterOrPolyParameter.setErrorMessage(self.polygonOrIntegerGridMessage) 
                        
        # Check if a secondary intRasterOrPoly input feature is indicated. Use this for requiring an integer raster or polygon dataset.
        if self.inIntRasterOrPolyIndex:
            # if provided, check if input geodataset is defined
            if self.inIntRasterOrPolyParameter.value:
                # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
                if hasattr(self.inIntRasterOrPolyParameter.value, "dataSource"):
                    desc = arcpy.Describe(self.inIntRasterOrPolyParameter.value.dataSource)
                else:
                    desc = arcpy.Describe(self.inIntRasterOrPolyParameter.value)

                if desc.spatialReference.name.lower() == "unknown":
                    self.inIntRasterOrPolyParameter.setErrorMessage(self.noSpatialReferenceMessage) 
                
                if desc.datasetType == "RasterDataset":
                    # Check if input raster is an integer grid
                    inRaster = arcpy.Raster(str(self.inIntRasterOrPolyParameter.value))
                    if not inRaster.isInteger:
                        self.inIntRasterOrPolyParameter.setErrorMessage(self.integerGridOrPolgonMessage)

                else:
                    if desc.shapeType.lower() != "polygon":
                        self.inIntRasterOrPolyParameter.setErrorMessage(self.polygonOrIntegerGridMessage) 
                                                
        # Check if distance input (e.g., buffer width, edge width) is a value greater than zero           
        if self.inDistanceIndex:
            # This parameter can be linked to a checkbox or a menu selection. If it is not checked or selected, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.inDistanceParameter.enabled:
                self.inDistanceParameter.clearMessage()
            else:
                if self.inDistanceParameter.value:
                    distanceValue = self.inDistanceParameter.value
                    # use the split function so this routine can be used for both long and linear unit data types
                    strDistance = str(distanceValue).split()[0]
                    if float(strDistance) <= 0.0:
                        self.inDistanceParameter.setErrorMessage(self.greaterThanZeroMessage)
                else:
                    # need the else condition as a 0 value won't trigger the if clause 
                    self.inDistanceParameter.setErrorMessage(self.greaterThanZeroMessage)
                    
        # Check if distance input (e.g., buffer width, edge width) is a positive number and an integer            
        if self.inIntegerDistanceIndex:
            if not self.inIntegerDistanceParameter.enabled:
                self.inIntegerDistanceParameter.clearMessage()
            else:
                if self.inIntegerDistanceParameter.value:
                    integerDistanceValue = self.inIntegerDistanceParameter.value
                    # use the split function so this routine can be used for both long and linear unit data types
                    strIntegerDistance = str(integerDistanceValue).split()[0]
                    integerDistance = float(strIntegerDistance)
                    valModulus = modf(integerDistance)
                    if valModulus[0] != 0 or valModulus[1] < 1.0:
                        self.inIntegerDistanceParameter.setErrorMessage(self.greaterThanZeroIntegerMessage)    
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.inIntegerDistanceParameter.setErrorMessage(self.greaterThanZeroIntegerMessage)
                
        # Check if second distance input (e.g., buffer width, edge width) is a positive number            
        if self.inDistance2Index:
            # This parameter can be linked to a checkbox or a menu selection. If it is not checked or selected, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.inDistance2Parameter.enabled:
                self.inDistance2Parameter.clearMessage()
            else:
                if self.inDistance2Parameter.value:
                    distanceValue = self.inDistance2Parameter.value
                    # use the split function so this routine can be used for both long and linear unit data types
                    strDistance = str(distanceValue).split()[0]
                    if float(strDistance) <= 0.0:
                        self.inDistance2Parameter.setErrorMessage(self.greaterThanZeroMessage)
                else:
                    # need the else condition as a 0 value won't trigger the if clause 
                    self.inDistance2Parameter.setErrorMessage(self.greaterThanZeroMessage)
                
        # Check if distance input (e.g., maximum separation) is a positive number or zero           
        if self.inWholeNumIndex:
            if not self.inWholeNumParameter.enabled:
                self.inWholeNumParameter.clearMessage()
            else:
                if self.inWholeNumParameter.value:
                    wholeNumValue = self.inWholeNumParameter.value
                    if wholeNumValue < 0.0:
                        self.inWholeNumParameter.setErrorMessage(self.zeroOrGreaterNumberMessage) 
        
        # Check if number input (e.g., slope threshold) is a positive integer including zero           
        if self.inZeroAndAboveIntegerIndex:
            if not self.inZeroAndAboveIntegerParameter.enabled:
                self.inZeroAndAboveIntegerParameter.clearMessage()
            else:
                if self.inZeroAndAboveIntegerParameter.value:
                    zeroAndAboveValue = self.inZeroAndAboveIntegerParameter.value
                    valModulus = modf(zeroAndAboveValue)
                    if valModulus[0] != 0 or valModulus[1] < 1.0:
                        self.inZeroAndAboveIntegerParameter.setErrorMessage(self.zeroOrGreaterIntegerMessage) 

        # Check if number input (e.g., number of cells) is a positive integer greater than zero       
        if self.inPositiveIntegerIndex:
            # This parameter can be linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.inPositiveIntegerParameter.enabled:
                self.inPositiveIntegerParameter.clearMessage()
            else:
                if self.inPositiveIntegerParameter.value:
                    positiveIntValue = self.inPositiveIntegerParameter.value
                    valModulus = modf(positiveIntValue)
                    if valModulus[0] != 0 or valModulus[1] < 1.0:
                        self.inPositiveIntegerParameter.setErrorMessage(self.greaterThanZeroIntegerMessage)    
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.inPositiveIntegerParameter.setErrorMessage(self.greaterThanZeroIntegerMessage)
                
        # Check if number input (e.g., number of cells) is a positive integer greater than zero 
        if self.inPositiveInteger2Index:
            # This parameter can be linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.inPositiveInteger2Parameter.enabled:
                self.inPositiveInteger2Parameter.clearMessage()
            else:
                if self.inPositiveInteger2Parameter.value:
                    positiveInt2Value = self.inPositiveInteger2Parameter.value
                    val2Modulus = modf(positiveInt2Value)
                    if val2Modulus[0] != 0 or val2Modulus[1] < 1.0:
                        self.inPositiveInteger2Parameter.setErrorMessage(self.greaterThanZeroIntegerMessage)  
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.inPositiveInteger2Parameter.setErrorMessage(self.greaterThanZeroIntegerMessage)

        # Check if number input (e.g., cell size) is a positive number greater than zero        
        if self.inPositiveNumberIndex:
            # This parameter can be linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.inPositiveNumberParameter.enabled:
                self.inPositiveNumberParameter.clearMessage()
            else:
                if self.inPositiveNumberParameter.value:
                    positiveValue = self.inPositiveNumberParameter.value
                    if positiveValue <= 0.0:
                        self.inPositiveNumberParameter.setErrorMessage(self.greaterThanZeroMessage)  
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.inPositiveNumberParameter.setErrorMessage(self.greaterThanZeroMessage)
        
        # Check if number input (e.g., burn in value) is in the set of invalid numbers (i.e., 0 to 100)
        if self.validNumberIndex:
            # This parameter is often linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.validNumberParameter.enabled:
                self.validNumberParameter.clearMessage()
            else:
                if self.validNumberParameter.value:
                    invalidNumbers = set((range(101)))
                    enteredValue = self.validNumberParameter.value
                    if enteredValue in invalidNumbers:
                        self.validNumberParameter.setErrorMessage(self.invalidNumberMessage)
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.validNumberParameter.setErrorMessage(self.invalidNumberMessage)                    
        
        # Check if number input (e.g., percent view threshold) is in the set of valid numbers (i.e., 1 to 100)
        if self.integerPercentageIndex:
            # This parameter is often linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.integerPercentageParameter.enabled:
                self.integerPercentageParameter.clearMessage()
            else:
                if self.integerPercentageParameter.value:
                    validIntegers = set((range(1,101)))
                    pctValue = self.integerPercentageParameter.value
                    if pctValue not in validIntegers:
                        self.integerPercentageParameter.setErrorMessage(self.integerPercentageMessage)
                else: # an entered value of '0' will not present as TRUE and trigger the conditional
                    self.integerPercentageParameter.setErrorMessage(self.integerPercentageMessage)
        
        # Check if distance input (e.g., buffer width, edge width) is a positive number greater than zero
        if self.inLinearUnitIndex:
            # This parameter can be linked to a checkbox. If it is not checked, this parameter is disabled
            # If it is disabled, do not perform the validation step
            if not self.inLinearUnitParameter.enabled:
                self.inLinearUnitParameter.clearMessage()
            else:
                if self.inLinearUnitParameter.value:
                    linearUnitValue = self.inLinearUnitParameter.value
                    # use the split function so this routine can be used for both long and linear unit data types
                    strLinearUnit = str(linearUnitValue).split()[0]
                    if float(strLinearUnit) <= 0.0:
                        self.inLinearUnitParameter.setErrorMessage(self.greaterThanZeroMessage)
                    
        # Check if a secondary raster output is indicated      
        if self.outRasterIndex:
            # Check if output raster has a valid filename; it contains no invalid characters, has no extension other than 
            # those found in globalConstants.rasterExtensions if the output location is in a folder, and has no extension 
            # if the output is to be placed in a geodatabase.
            if self.outRasterParameter.value:
                self.outRasterName = self.outRasterParameter.valueAsText
            
                # get the directory path and the filename
                self.outRasterWorkspace = os.path.split(self.outRasterName)[0]
                self.rasterFilename = os.path.split(self.outRasterName)[1]
                
                # break the filename into its root and extension
                self.rasterFileRoot = os.path.splitext(self.rasterFilename)[0]
                self.rasterFileExt = os.path.splitext(self.rasterFilename)[1]
                
                # substitue valid characters into the filename root if any invalid characters are present
                self.validRasterFileRoot = arcpy.ValidateTableName(self.rasterFileRoot,self.outRasterWorkspace)
                
                # alert the user if invalid characters are present in the output table name.
                if self.rasterFileRoot != self.validRasterFileRoot:
                    self.outRasterParameter.setErrorMessage(self.invalidTableNameMessage)
                    
                elif self.rasterFileExt: # check on file extensions. None are allowed in geodatabases and only certain extensions are allowed in folders.
                    self.rasterWorkspaceExt = os.path.splitext(self.outRasterWorkspace)[1]
                    
                    # if the workspace is a geodatabase
                    if self.rasterWorkspaceExt.upper() == ".GDB":
                        # alert user that file names cannot contain an extension in a GDB
                        self.outRasterParameter.setErrorMessage(self.invalidExtensionMessage)               
                    else:                    
                        # get the list of acceptable filename extentions for folder locations
                        # self.rasterExtensions = globalConstants.rasterExtensions
                        self.rasterExtensions = [".img", ".tif"]
                        
                        if self.rasterFileExt not in self.rasterExtensions:
                            self.outRasterParameter.setErrorMessage("Valid extensions for rasters in folders for this tool are: %s." % str(self.rasterExtensions))           
