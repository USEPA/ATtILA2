"""
    ToolValidator is for tool dialog validation, cut and paste the following into the Validation tab of tool properties:
    
import os
import sys
tbxPath = __file__.split("#")[0]
srcDirName = os.path.basename(tbxPath).rstrip(".tbx").split("__")[0] + ".src"  # <toolbox_name>__anything.tbx -> <toolbox_name>.src
tbxParentDirPath =  os.path.dirname(tbxPath)
srcDirPath = os.path.join(tbxParentDirPath, srcDirName)
sys.path.append(srcDirPath)
from esdlepy.metrics.validation.LandCoverProportions import ToolValidator


"""


import arcpy
import os
from xml.dom.minidom import parse
from glob import glob 
import __main__

    
class ToolValidator:
    """ Class for validating set of three LCC parameters 
        
        Two consecutive parameters
        1. Table(reporting units):  Properties: default (self.inTableIndex)
        2. Field(dropdown):  Properties: linked to Table
        
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
        self.optionalFieldsIndex = 9 # index of optional fields parameter

        ###############################################
        
        self.inputIdFieldTypes = ["SmallInteger", "Integer", "String"]
        self.lccSchemeUserOption = "User Defined"
        self.optionalFieldsName = "Optional Fields"
        self.qaCheckDescription = "QACHECK  -  Quality Assurance Checks"
        self.metricAddDescription = "METRICADD  -  Area for all land cover classes"
        self.srcDirName = "ATtILA2.src"
        self.lccFileDirName = r"LandCoverClassifications"
        self.lccFileExtension = "lcc"
        self.idAttributeName = "id"
        self.nameAttributeName = "name"
        self.classElementName = "class"
        self.overrideAttributeName = "lcpField"
        self.fieldPrefix = "p"
        self.metricDescription = "{0}  [{1}]  {2}"
        self.srcFolderSuffix = ".src"


        self.parameters = arcpy.GetParameterInfo()
        self.lccFilePathIndex = self.startIndex + 1
        self.lccClassesIndex = self.startIndex + 2
        self.inputFieldsIndex = self.inTableIndex + 1
        self.currentFilePath = ""
        self.ruFilePath = ""
        self.inputTableParameter = self.parameters[self.inTableIndex]
        self.inputFieldsParameter = self.parameters[self.inputFieldsIndex]
        self.lccSchemeParameter =  self.parameters[self.startIndex]
        self.lccFilePathParameter = self.parameters[self.lccFilePathIndex]
        self.lccClassesParameter = self.parameters[self.lccClassesIndex]
        self.optionalFieldsParameter = self.parameters[self.optionalFieldsIndex]
        self.initialized = False


    def initializeParameters(self):
        """ """
        self.inputTableParameter.value = ""
        # Populate predefined LCC dropdown
        parentDir = os.path.dirname( __main__.__file__.split("#")[0])
        self.srcDirPath = os.path.join(parentDir, self.srcDirName, )
        self.lccFileDirSearch = os.path.join(self.srcDirPath, self.lccFileDirName, "*." + self.lccFileExtension)
        
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



        