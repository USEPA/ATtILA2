"""
    ToolValidator is for tool dialog validation, cut and paste the following into the Validation tab of tool properties:
    
    
import os
import sys
tbxPath = __file__.split("#")[0]
srcDirName = os.path.basename(tbxPath).rstrip(".tbx").split("__")[0] + ".src"  # <toolbox_name>__anything.tbx -> <toolbox_name>.src
tbxParentDirPath =  os.path.dirname(tbxPath)
srcDirPath = os.path.join(tbxParentDirPath, srcDirName)
sys.path.append(srcDirPath)
import esdlepy

class ToolValidator (esdlepy.metrics.validation.LandCoverProportions.ToolValidator):
    "" Class for validating set of three LCC parameters 
        
        inTableIndex:  Two consecutive parameters
        1. Table(reporting units):  Properties: default (self.inTableIndex)
        2. Field(dropdown):  Properties: linked to Table
        
        startIndex:  Three consecutive parameters 
        1. String: Properties: default  POPULATED: file names and lccSchemeUserOption  (self.startIndex)
        2. File: Properties: filter=lccFileExtension
        3. String:  MultiValue=Yes; 
        
        optionalFieldsIndex:  single parameter 
        1. String: Properties: MultiValue=Yes
        
    ""
    
    ###############################################
    # Keep updated
    
    inTableIndex = 0 # start index of input reporting units (one parameter follows)
    startIndex = 3 # start index of predefined dropdown (two parameters follow)
    optionalFieldsIndex = 9 # index of optional fields parameter

    ###############################################
"""


import arcpy
import os
from xml.dom.minidom import parse
from glob import glob 
import __main__
from esdlepy.metrics import constants as metricConstants
from esdlepy.lcc import constants as lccConstants
from esdlepy import outFields
    
class ToolValidator:
    """ Class for validating set of three LCC parameters 
        
        inTableIndex:  Two consecutive parameters
        1. Table(reporting units):  Properties: default (self.inTableIndex)
        2. Field(dropdown):  Properties: linked to Table
        
        startIndex:  Three consecutive parameters 
        1. String: Properties: default  POPULATED: file names and lccSchemeUserOption  (self.startIndex)
        2. File: Properties: filter=lccFileExtension
        3. String:  MultiValue=Yes; 
        
        optionalFieldsIndex:  single parameter 
        1. String: Properties: MultiValue=Yes
        
    """
    
    ###############################################
    # Keep updated
    
    inTableIndex = 0 # start index of input reporting units (one parameter follows)
    startIndex = 3 # start index of predefined dropdown (two parameters follow)
    optionalFieldsIndex = 9 # index of optional fields parameter
    inRasterIndex = 2 # index of input raster
    processingCellSizeIndex = 7 # index of optional processing cell size parameter
    snapRasterIndex = 8 # index of optional snap raster parameter
    
    ###############################################
    

    def __init__(self):
        """ """
                

        
        self.inputIdFieldTypes = metricConstants.inputIdFieldTypes
        self.lccSchemeUserOption = metricConstants.userOption
        self.optionalFieldsName = metricConstants.optionalFieldsName
        self.qaCheckDescription = metricConstants.qaCheckDescription
        self.metricAddDescription = metricConstants.metricAddDescription
        
        tbxPath =  __main__.__file__.split(metricConstants.tbxSriptToolDelim)[0]
        self.parentDir = os.path.dirname(tbxPath)
        self.srcDirName = os.path.basename(tbxPath).rstrip(metricConstants.tbxFileSuffix).split(metricConstants.tbxFileDelim)[0] + metricConstants.srcFolderSuffix
        self.lccFileDirName = lccConstants.PredefinedFileDirName
        
        self.lccFileExtension = lccConstants.XmlFileExtension
        self.idAttributeName = lccConstants.XmlAttributeId
        self.nameAttributeName = lccConstants.XmlAttributeName
        self.classElementName = lccConstants.XmlElementClass
        self.overrideAttributeName = lccConstants.XmlAttributeLcpField
        self.metricDescription = metricConstants.lcpMetricDescription

        self.fieldPrefix = outFields.lcpFieldPrefix

        self.parameters = arcpy.GetParameterInfo()
        self.lccFilePathIndex = self.startIndex + 1
        self.lccClassesIndex = self.startIndex + 2
        self.inputFieldsIndex = self.inTableIndex + 1
        self.currentFilePath = ""
        self.ruFilePath = ""
        
        # Required Parameters
        self.inputTableParameter = self.parameters[self.inTableIndex]
        self.inputFieldsParameter = self.parameters[self.inputFieldsIndex]
        self.lccSchemeParameter =  self.parameters[self.startIndex]
        self.lccFilePathParameter = self.parameters[self.lccFilePathIndex]
        self.lccClassesParameter = self.parameters[self.lccClassesIndex]
        self.processingCellSizeParameter = self.parameters[self.processingCellSizeIndex]
        
        self.inRasterParameter = self.parameters[self.inRasterIndex]
        self.snapRasterParameter = self.parameters[self.snapRasterIndex]
        self.optionalFieldsParameter = self.parameters[self.optionalFieldsIndex]
        
        self.initialized = False


    def initializeParameters(self):
        """ """
        self.inputTableParameter.value = ""
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
        self.initialized=True
        
        # push optional fields to collapsed region
        self.optionalFieldsParameter.category = self.optionalFieldsName
        
        # set optional fields filter
        filterList = [self.qaCheckDescription, self.metricAddDescription]
        self.optionalFieldsParameter.filter.list = filterList
        
    def updateParameters(self):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
    
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
                    fieldName = self.fieldPrefix + classId
                
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
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        
        # Set lcc file parameter required only if user-defined is set
        if self.lccSchemeParameter.value != self.lccSchemeUserOption:
            self.lccFilePathParameter.clearMessage()
            
        # Clear required on disabled lcc class selection
        if not self.lccClassesParameter.enabled:
            self.lccClassesParameter.clearMessage()
        
        # Remove required on optional fields
        self.optionalFieldsParameter.clearMessage()

        # Check if input raster is defined
        if self.inRasterParameter.value:
            
            # Update Processing cell size if empty
            if not self.processingCellSizeParameter.value and not self.processingCellSizeParameter.hasError():
                cellSize = 30 #get from metadata
                self.processingCellSizeParameter.value = cellSize
            
            # Update Snap Raster Parameter if it is empty
            if not self.snapRasterParameter.value and not self.inRasterParameter.hasError():
                self.snapRasterParameter.value = str(self.inRasterParameter.value)


        