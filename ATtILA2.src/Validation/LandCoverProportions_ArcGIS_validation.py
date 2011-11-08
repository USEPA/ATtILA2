import arcpy
import os
from xml.dom.minidom import parse
from glob import glob 

class ToolValidator:
    """ Class for validating set of three LCC parameters 
        
        Two consecutive parameters
        1. Table:  Properties: default (self.inTableIndex)
        2. Field:  Properties: linked to Table
        
        Three consecutive parameters 
        1. String: Properties: default  POPULATED: file names and lccSchemeUserOption  (self.startIndex)
        2. File: Properties: filter=lccFileExtension
        3. String:  MultiValue=Yes; 
    """

    def __init__(self):
        """ """        
        
        ###############################################
        # Keep updated
        self.inTableIndex = 0 # start index of fields dropdown
        self.startIndex = 3 # start index of predefined dropdown (two parameters should follow)
        self.lccSchemeUserOption = "User Defined"
        self.lccFileDirName = "LandCoverClassifications"
        self.lccFileExtension = "lcc"
        ###############################################

        self.parameters = arcpy.GetParameterInfo()
        self.lccFilePathIndex = self.startIndex + 1
        self.lccClassesIndex = self.startIndex + 2
        self.inputFieldsIndex = self.inTableIndex + 1
        self.currentFilePath = ""
        self.inputTableParameter = self.parameters[self.fieldsIndex]
        self.inputFieldsParameter = self.parameters[self.inputFieldsIndex]
        self.lccSchemeParameter =  self.parameters[self.startIndex]
        self.lccFilePathParameter = self.parameters[self.lccFilePathIndex]
        self.lccClassesParameter = self.parameters[self.lccClassesIndex]
        self.initialized = False


    def initializeParameters(self):
        """ """    
                
        # Populate predefined LCC dropdown
        self.srcDir = __file__.split("#")[0].replace(".tbx",".src")
        self.lccFileDirSearch = os.path.join(self.srcDir, self.lccFileDirName, "*." + self.lccFileExtension)
        
        filterList = []
        self.lccLookup = {}
        for lccPath in glob(self.lccFileDirSearch):
            lccSchemeName = os.path.basename(lccPath).rstrip("." + self.lccFileExtension)
            filterList.append(lccSchemeName)
            self.lccLookup[lccSchemeName] = lccPath
            
        self.lccSchemeParameter.filter.list = filterList + [self.lccSchemeUserOption]
        
        self.lccFilePathParameter.enabled = False
        self.lccClassesParameter.enabled = False
        self.initialized=True
  

    def updateParameters(self):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
    
        if not self.initialized:
            self.initializeParameters()
            
        self.updateInputFieldsParameter()
        
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
            classNodes = lccDocument.getElementsByTagName("class")
            
            idAttributeName = "id"
            nameAttributeName = "name"
            metricDescription = "{0}  ({1})"
            
            for classNode in classNodes:
                
                classId = classNode.getAttribute(idAttributeName)
                name = classNode.getAttribute(nameAttributeName)     
                
                className = metricDescription.format(classId, name)
                classNames.append(className)    
                
        # Populate checkboxes with LCC name and description   
        if classNames:
            self.lccClassesParameter.enabled = True
        else:
            self.lccClassesParameter.enabled = False  
            self.lccClassesParameter.value = ""
        self.lccClassesParameter.filter.list = classNames
        
        
    def updateInputFieldsParameter(self):
        """  Set """
        fieldTypes = set(["SmallInteger", "Integer", "String"])
        tablePath = self.inputTableParameter.value
        
        if tablePath:
            fields = arcpy.ListFields(tablePath)
            
            for field in fields:
                if field.type in fieldTypes:
                    self.inputFieldsParameter.value = field.name
                    break
                    
                
        
    def updateMessages(self):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        
        # Set lcc file parameter required only if user-defined is set
        if self.lccSchemeParameter.value != self.lccSchemeUserOption:
            self.lccFilePathParameter.clearMessage()
            
        # Clear required on disabled lcc class selection
        if not self.lccClassesParameter.enabled:
            self.lccClassesParameter.clearMessage()
        
        