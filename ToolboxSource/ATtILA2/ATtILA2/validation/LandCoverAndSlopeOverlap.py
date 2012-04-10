

""" The ToolValidator class is for tool dialog validation.

    Cut and paste the following into the Validation tab of tool properties in ArcCatalog:
    

    
import os
import sys
tbxPath = __file__.split("#")[0]
sourceName = "ToolboxSource" 
tbxParentDirPath =  os.path.dirname(tbxPath)
srcDirPath = os.path.join(tbxParentDirPath, sourceName)
sys.path.append(srcDirPath)
import ATtILA2

class ToolValidator (ATtILA2.validation.LandCoverAndSlopeOverlap.ToolValidator):
    " Class for validating parameters "
     
    ## Description of parameters 
    #    
    # inTableIndex:  Two consecutive parameters
    # 1. Table(reporting units)
    # 2. Field(dropdown):  Obtained from="<Table>"
    #    
    # inRasterIndex:  One parameter
    # 1. Raster Layer
    #
    # startIndex:  Three consecutive parameters 
    # 1. String: default  
    # 2. File: filter=lccFileExtension
    # 3. String:  MultiValue=Yes; 
    #    
    # processingCellSizeIndex:  Index of optional processing cell size parameter
    # 1. Analysis cell size
    #
    # snapRasterIndex:  Index of optional snap raster parameter
    # 1. Raster Layer
    #
    # optionalFieldsIndex:  index of optional fields parameter
    # 1. String: Properties: MultiValue=Yes
        
    
    ###############################################
    # Keep updated
    
    inTableIndex = 0
    inRasterIndex = 2
    startIndex = 3
    processingCellSizeIndex = 9 
    snapRasterIndex = 10 
    optionalFieldsIndex = 11 
    
    srcDirName = sourceName
    
    ###############################################
    
    
"""


import arcpy
import os
from xml.dom.minidom import parse
from glob import glob 
import __main__
from ATtILA2.metrics import constants as metricConstants
import pylet.lcc.constants as lccConstants
from ATtILA2.metrics import fields as outFields
    
class ToolValidator:
    """ Class for validating parameters """
    
    # Indexes of input parameters
    inTableIndex = 0 
    inRasterIndex = 2 
    startIndex = 3 
    processingCellSizeIndex = 9 
    snapRasterIndex = 10
    optionalFieldsIndex = 11
    
    # Additional local variables
    srcDirName = metricConstants.tbxSourceFolderName
    

    def __init__(self):
        """ Initialize ToolValidator class"""
        
        # Load metric constants        
        self.inputIdFieldTypes = metricConstants.inputIdFieldTypes
        self.lccSchemeUserOption = metricConstants.userOption
        self.optionalFieldsName = metricConstants.optionalFieldsName
        self.qaCheckDescription = metricConstants.qaCheckDescription
        self.metricAddDescription = metricConstants.metricAddDescription      
        self.metricDescription = metricConstants.metricDescription
        self.noFeaturesMessage = metricConstants.noFeaturesMessage
        self.filterList = metricConstants.lcsoOptionalFieldsFilter
        
        # Load LCC constants
        self.lccFileDirName = lccConstants.PredefinedFileDirName       
        self.lccFileExtension = lccConstants.XmlFileExtension
        self.idAttributeName = lccConstants.XmlAttributeId
        self.nameAttributeName = lccConstants.XmlAttributeName
        self.classElementName = lccConstants.XmlElementClass
        self.overrideAttributeName = lccConstants.XmlAttributeLcsoField

        # Load outFields constants
        self.fieldPrefix = outFields.lcsoFieldPrefix
        self.fieldSuffix = outFields.lcsoFieldSuffix
        
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
        self.snapRasterParameter = self.parameters[self.snapRasterIndex]
        self.optionsParameter = self.parameters[self.optionalFieldsIndex]
        
        # Additional local variables
        self.currentFilePath = ""
        self.ruFilePath = ""
        self.initialized = False

    def initializeParameters(self):
        """ Initialize parameters"""

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
        """ Modify the values and properties of parameters before internal validation is performed.  
        
            This method is called whenever a parameter has been changed.
        
        """
        
        if not self.initialized:
            self.initializeParameters()

        self.updateInputLccParameters()
        self.updateInputFieldsParameter()


    
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
            lccDocument = parse(lccFilePath)
            classNodes = lccDocument.getElementsByTagName(self.classElementName)
            

            message = self.metricDescription
            for classNode in classNodes:
                
                classId = classNode.getAttribute(self.idAttributeName)
                name = classNode.getAttribute(self.nameAttributeName)     
                
                # Check for field override, ie NINDEX, UINDEX
                fieldName = classNode.getAttribute(self.overrideAttributeName)
                if not fieldName:
                    fieldName = self.fieldPrefix + classId + self.fieldSuffix
                
                className = message.format(classId, fieldName, name)
                classNames.append(className)    
                
        # Populate checkboxes with LCC name and description   
        if classNames:
            self.lccClassesParameter.enabled = True
        else:
            self.lccClassesParameter.enabled = False  
            self.lccClassesParameter.value = ""
        self.lccClassesParameter.filter.list = classNames    
        
        
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
            except:
                pass
                
        
    def updateMessages(self):
        """ Modify the messages created by internal validation for each tool parameter.  
        
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
            
            # Update Processing cell size if empty
            if not self.processingCellSizeParameter.value and not self.processingCellSizeParameter.hasError():
                cellSize = arcpy.Raster(str(self.inRasterParameter.value)).meanCellWidth #get from metadata
                self.processingCellSizeParameter.value = cellSize
            
            # Update Snap Raster Parameter if it is empty
            if not self.snapRasterParameter.value and not self.inRasterParameter.hasError():
                self.snapRasterParameter.value = str(self.inRasterParameter.value)

        # Check for empty input features
        if self.inputTableParameter.value and not self.inputTableParameter.hasError() and not arcpy.SearchCursor(self.inputTableParameter.value).next():
            self.inputTableParameter.setErrorMessage(self.noFeaturesMessage)

    
        