# LandCoverProportions_ArcGIS_validation
# Michael A. Jackson, jackson.michael@epa.gov, majgis@gmail.com
# 
# 

class ToolValidator:
    """Class for validating a tool's parameter values and controlling
      the behavior of the tool's dialog.
    """

    def __init__(self):
        """Setup arcpy and the list of tool parameters."""
        import arcpy
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        """Refine the properties of a tool's parameters.  This method is
        called when the tool is opened."""
        
        
        return

    def updateParameters(self):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parmater
        has been changed."""
    
        return

    def updateMessages(self):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        
        return
