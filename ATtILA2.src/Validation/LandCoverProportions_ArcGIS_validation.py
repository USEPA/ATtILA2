# LandCoverProportions_ArcGIS_validation
# Michael A. Jackson, jackson.michael@epa.gov, majgis@gmail.com
# 2011-10-11
#
# Cut and paste this class into the ArcToolbox Script Tool Dialog
#
# Please do not add code here.  Add code in the library

class ToolValidator:
    """ Validates tool parameter values and controls dialog behavior."""

    def __init__(self):
        """Unpredictable behavior, do not use"""
        self.initialized = None
        # Put initialization code in "initialize" method
        
    def initializeParameters(self):
        """Unpredictable behavior, no not use"""        
        # Put initialization code in "initialize" method
        
    def initialize(self):
        """ Initialization """
        
        ###############################################
        # Update If Parameter Order Changes
        parameterStartIndex = 3
        ###############################################
        
        import sys
        self.sys = sys
        
        # Import a relative package
        self.srcDir = __file__.split("#")[0].replace(".tbx",".src")
        sys.path.append(self.srcDir)
        from esdlepy.lcc.toolValidators import threeParameters
        
        # Load functionality for this validator from the library
        threeParameters.loadToolValidator(self, parameterStartIndex)
            
        self.initialized = True
            
    def updateParameters(self):
        """ Modify the values and properties of parameters.
        
            Called before internal validation is performed.  
            Called whenever a parameter has been changed.
        """

        if self.initialized is None:
            self.initialize()

    def updateMessages(self):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        
        return  