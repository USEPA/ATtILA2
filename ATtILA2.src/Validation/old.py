# LandCoverProportions_ArcGIS_validation
# Michael A. Jackson, jackson.michael@epa.gov, majgis@gmail.com
# 2011-10-05
# 

class ToolValidator:
    """Class for validating a tool's parameter values and controlling
      the behavior of the tool's dialog.
    """

    def __init__(self):
        """Setup arcpy and the list of tool parameters."""
        
        import arcpy
        import os
        import sys
        from xml.dom.minidom import parse
        from glob import glob
        self.sys = sys
        self.os = os
        self.parse = parse
        self.glob = glob
        self.parameters = arcpy.GetParameterInfo()

        ###############################################
        # Must Be Updated If Parameter Order Changes
        self.lccSchemeIndex = 3
        self.lccFilePathIndex = 4
        self.lccClassesIndex = 5
        ###############################################
        # Constants visible in tool
        self.lccSchemeUserOption = "User Defined"
        self.lccFileDirName = "LandCoverClassifications"  
        self.lccFileExtension = ".lcc"     
        ###############################################
        
        self.srcDir = __file__.split("#")[0].replace(".tbx",".src")
        self.currentFilePath = ""
        self.parametersNotInitialized = True
        
        
    def initializeParameters(self):
        """Refine the properties of a tool's parameters.  This method is
        called when the tool is opened."""       
        
        self.lccSchemeParameter =  self.parameters[self.lccSchemeIndex]
        self.lccFilePathParameter = self.parameters[self.lccFilePathIndex]
        self.lccClassesParameter = self.parameters[self.lccClassesIndex]
        
        # Populate predefined LCC dropdown
        lccFileDirSearch = self.os.path.join(self.srcDir, self.lccFileDirName, "*")
        self.lccSchemeParameter.filter.list = [lccName.rstrip(self.lccFileExtension) for lccName in self.glob(lccFileDirSearch)]
        
        self.parametersNotInitialized = False

    def updateParameters(self):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        
        if self.parametersNotInitialized:
            self.initializeParameters()
        
        lccFilePath = str(self.lccFilePathParameter.value)
        if not lccFilePath is None and self.currentFilePath != lccFilePath and self.os.path.isfile(lccFilePath):
            self.currentFilePath = lccFilePath
            lccDocument = self.parse(lccFilePath)
            classNodes = lccDocument.getElementsByTagName("class")
            
            idAttributeName = "id"
            nameAttributeName = "name"
            metricDescription = "{0}  ({1})"
            classNames = []
            for classNode in classNodes:
                
                classId = classNode.getAttribute(idAttributeName)
                name = classNode.getAttribute(nameAttributeName)     
                
                className = metricDescription.format(classId, name)
                classNames.append(className) 
                
            self.lccClassesParameter.filter.list = classNames

        
        return

    def updateMessages(self):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        
        return        
