# LandCoverProportions_ArcGIS_validation
# Michael A. Jackson, jackson.michael@epa.gov, majgis@gmail.com
# 2011-10-12
# 

def loadToolValidator(emptyToolValidator, startIndex): 
    """ Load all aspects of this ToolValidator Class
    
        emptyToolValidator: Another empty Toolvalidator class to upload identity to
        startIndex:  index of first of three, consecutive parameters

    """
    ToolValidator(emptyToolValidator, startIndex)


class ToolValidator:
    """ Class for validating set of three LCC parameters 
        
        Three consecutive parameters 
    
    """

    def __init__(self, emptyToolValidator=None, startIndex=0 ):
        """Setup arcpy and the list of tool parameters."""
        
        ###############################################
        # Must Be Updated If Parameter Order Changes
        self.startIndex = 0
        ###############################################
        
        import arcpy
        import os
        import sys
        from xml.dom.minidom import parse
        from glob import glob        
        
        # Only executed when used from the library
        if emptyToolValidator:
            
            emptyToolValidator.initializeParameters = self.initializeParameters
            emptyToolValidator.updateParameters = self.updateParameters
            emptyToolValidator.updateMessages = self.updateMessages
            
            self = emptyToolValidator
            self.startIndex = startIndex

        # Only executed when used from toolbox (cut and paste)
        else:
            srcDir = __file__.split("#")[0].replace(".tbx",".src")
            sys.path.append(srcDir)
            
        from esdlepy import lcc #sys.path must be appended before import

        self.sys = sys
        self.os = os
        self.parse = parse
        self.glob = glob
        self.lcc = lcc     
        self.parameters = arcpy.GetParameterInfo()
        self.lccSchemeUserOption = "User Defined"
        self.lccFileDirName = "LandCoverClassifications"  
        self.lccFileExtension = ".lcc"     
        self.lccFilePathIndex = self.startIndex + 1
        self.lccClassesIndex = self.startIndex + 2
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
