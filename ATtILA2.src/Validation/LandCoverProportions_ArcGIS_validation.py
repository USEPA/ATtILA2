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
        from xml.dom.minidom import parse
        self.os = os
        self.parse = parse
        self.params = arcpy.GetParameterInfo()
        self.currentFilePath = ""

    def initializeParameters(self):
        """Refine the properties of a tool's parameters.  This method is
        called when the tool is opened."""       

        return

    def updateParameters(self):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parmater
        has been changed."""
        
        lccFilePath = str(self.params[3].value)
        if not lccFilePath is None and self.currentFilePath != lccFilePath and self.os.path.isfile(lccFilePath):
            self.currentFilePath = lccFilePath
            lccDocument = self.parse(lccFilePath)
            classNodes = lccDocument.getElementsByTagName("class")
            
            idAttributeName = "id"
            nameAttributeName = "name"
            metricDescription = "{0}  ({1})"
            classNames = []
            for classNode in classNodes:
                
                id = classNode.getAttribute(idAttributeName)
                name = classNode.getAttribute(nameAttributeName)     
                
                className = metricDescription.format(id, name)
                classNames.append(className) 
                
            self.params[4].filter.list = classNames

        
        return

    def updateMessages(self):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        
        return

