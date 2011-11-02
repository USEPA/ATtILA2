class ToolValidator:
    """ Class for validating set of three LCC parameters 
        
        Three consecutive parameters 
        1. String: Properties: default  POPULATED: file names and lccSchemeUserOption
        2. File: Properties: filter=lccFileExtension
        3. String:  MultiValue=Yes; 
    """

    def __init__(self):
        """ """        
        
        ###############################################
        # Keep updated
        self.startIndex = 3
        self.lccSchemeUserOption = "User Defined"
        self.lccFileDirName = "LandCoverClassifications"
        self.lccFileExtension = "lcc"
        ###############################################
        
        import arcpy
        import os
        from xml.dom.minidom import parse
        from glob import glob 
        import sys
        
        self.sys = sys
        self.os = os
        self.parse = parse
        self.glob = glob
        self.parameters = arcpy.GetParameterInfo()
        self.lccFilePathIndex = self.startIndex + 1
        self.lccClassesIndex = self.startIndex + 2
        self.currentFilePath = ""
        self.lccSchemeParameter =  self.parameters[self.startIndex]
        self.lccFilePathParameter = self.parameters[self.lccFilePathIndex]
        self.lccClassesParameter = self.parameters[self.lccClassesIndex]


    def initializeParameters(self):
        """ """    
        
        # Populate predefined LCC dropdown
        self.srcDir = __file__.split("#")[0].replace("\\tests\\TestsToolbox.tbx", "").replace(".tbx",".src")
        self.lccFileDirSearch = self.os.path.join(self.srcDir, self.lccFileDirName, "*." + self.lccFileExtension)
        
        filterList = []
        self.lccLookup = {}
        for lccPath in self.glob(self.lccFileDirSearch):
            lccSchemeName = self.os.path.basename(lccPath).rstrip("." + self.lccFileExtension)
            filterList.append(lccSchemeName)
            self.lccLookup[lccSchemeName] = lccPath
            
        self.lccSchemeParameter.filter.list = filterList + [self.lccSchemeUserOption]
        
        self.lccFilePathParameter.enabled = False
        self.lccClassesParameter.enabled = False
  

    def updateParameters(self):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        self.initializeParameters()
        
        # Converts None to "None", so must do a check
        lccSchemeName = ""
        if self.lccSchemeParameter.value:
            lccSchemeName = str(self.lccSchemeParameter.value)

        
        lccFilePath = ""
        # User defined LCC Scheme
        if  lccSchemeName == self.lccSchemeUserOption:
            lccFilePath = str(self.lccFilePathParameter.value)
            self.lccFilePathParameter.enabled = True
            
        # Pre-defined  LCC Scheme  
        elif lccSchemeName:
            lccFilePath = self.lccLookup[lccSchemeName]
        
            # Delete user defined file path in dialog
            self.lccFilePathParameter.value = ""
            self.lccFilePathParameter.enabled = False
        
        # Get list of LCC names with description
        classNames = []
        if lccFilePath and self.currentFilePath != lccFilePath and self.os.path.isfile(lccFilePath):
            self.currentFilePath = lccFilePath
            lccDocument = self.parse(lccFilePath)
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
        
        

    def updateMessages(self):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        
        # Set lcc file parameter required only if user-defined is set
        if self.lccSchemeParameter.value != self.lccSchemeUserOption:
            self.lccFilePathParameter.clearMessage()
            
        # Clear required on disabled lcc class selection
        if not self.lccClassesParameter.enabled:
            self.lccClassesParameter.clearMessage()
        
        