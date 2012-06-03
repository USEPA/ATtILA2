''' These classes are for inheritance by ToolValidator classes

    These classes shouldn't be used directly as ToolValidators.
    Create a new ToolValidator class that inherits one of these classes.
'''

import arcpy
import os
from xml.dom.minidom import parse
from glob import glob 
import __main__
from ATtILA2.constants import globalConstants
from ATtILA2.constants import validatorConstants
import pylet.lcc.constants as lccConstants
from pylet.lcc import LandCoverClassification, LandCoverCoefficient
    
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
    inRaster3Index = 0
    
    # Additional local variables
    srcDirName = validatorConstants.tbxSourceFolderName
    
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
        self.nonIntegerGridMessage = validatorConstants.nonIntegerGridMessage
        
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
        
        # Assign parameters to secondary local variables
        if self.inRaster2Index:
            self.inRaster2Parameter = self.parameters[self.inRaster2Index]
        
        # Additional local variables
        self.currentFilePath = ""
        self.ruFilePath = ""
        self.initialized = False


    def initializeParameters(self):
        """ ESRI - Initialize parameters"""

        # Populate predefined LCC dropdown
        parentDir = os.path.dirname( __main__.__file__.split("#")[0])
        self.srcDirPath = os.path.join(parentDir, self.srcDirName, )
        self.lccFileDirSearch = os.path.join(self.srcDirPath, self.lccFileDirName, "*" + self.lccFileExtension)
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
        
        if not self.initialized:
            self.initializeParameters()

        self.updateInputLccParameters()
        self.updateInputFieldsParameter()
        self.updateOutputTableParameter()


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
#        if self.lccClassesParameter.hasBeenValidated and self.lccClassesParameter.altered:
#            self.lccClassesParameter.value = ""
            
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
            
            # Check for is input raster layer has spatial reference
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
        
            # Check for empty input features
            if not arcpy.SearchCursor(self.inputTableParameter.value).next():
                self.inputTableParameter.setErrorMessage(self.noFeaturesMessage)
            
            # Check for if input feature layer has spatial reference
            # use arcpy.Exists to check if input parameter is a lyr file.
            if arcpy.Exists(self.inputTableParameter.value):
                # not a lyr file
                if arcpy.Describe(self.inputTableParameter.value).spatialReference.name.lower() == "unknown":
                    self.inputTableParameter.setErrorMessage(self.noSpatialReferenceMessage)
            else:
                # lyr file. Use .dataSource to get the path to the actual data file
                if arcpy.Describe(self.inputTableParameter.value.dataSource).spatialReference.name.lower() == "unknown":
                    self.inputTableParameter.setErrorMessage(self.noSpatialReferenceMessage)

            
        # CHECK ON SECONDARY INPUTS IF PROVIDED
        
        # Check if a second input raster is provided
        if self.inRaster2Index:
            # if provided, check if input raster2 is defined
            if self.inRaster2Parameter.value:
            
                # Check for is input raster layer has spatial reference
                if arcpy.Describe(self.inRaster2Parameter.value).spatialReference.name.lower() == "unknown":
                    self.inRaster2Parameter.setErrorMessage(self.noSpatialReferenceMessage)
                
    
            
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
