import os
import sys
tbxPath = __file__.split("#")[0]
sourceName = "ToolboxSource" 
tbxParentDirPath =  os.path.dirname(tbxPath)
srcDirPath = os.path.join(tbxParentDirPath, sourceName)
sys.path.append(srcDirPath)
import ATtILA2
from ATtILA2.constants import validatorConstants
from ATtILA2.constants import globalConstants
import arcpy

class ToolValidator:
    """Class for validating a tool's parameter values and controlling
    the behavior of the tool's dialog."""

    def __init__(self):
        """Setup the list of tool parameters."""
        self.params = arcpy.GetParameterInfo()
        self.inLineParameter = self.params[0]
        self.mergeFieldParameter = self.params[2]
        self.checkboxParameter = self.params[1]
        self.mergeDistanceParameter = self.params[3]
        self.outPutCS = self.params[4]
        self.inCellSizeParameter = self.params[5]
        self.inSearchRadiusParameter = self.params[6]
        self.outRasterParameter = self.params[8]
        self.initialized = False
        self.noSpatialReferenceMessage = validatorConstants.noSpatialReferenceMessage
        self.noProjectionInOutputCS = validatorConstants.noProjectionInOutputCS
        self.invalidTableNameMessage = validatorConstants.invalidTableNameMessage
        self.invalidExtensionMessage = validatorConstants.invalidExtensionMessage
        self.nonPositiveNumberMessage = validatorConstants.nonPositiveNumberMessage
    
    def initializeParameters(self):
        """Refine the properties of a tool's parameters.  This method is
        called when the tool is opened."""
        # self.params[1].enabled = True
        # self.initialized = True
        return

    def updateParameters(self):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parmater
        has been changed."""
        if self.checkboxParameter.value:
            self.mergeFieldParameter.enabled = True
            self.mergeDistanceParameter.enabled = True
            if not self.mergeDistanceParameter.value:
                self.mergeDistanceParameter.value = '30 Meters'
        else:
            self.mergeFieldParameter.enabled = False
            self.mergeDistanceParameter.enabled = False
        return

    def updateMessages(self):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        # if optional check box is unselected, clear the parameter message area and value area
        if not self.mergeFieldParameter.enabled:
            self.mergeFieldParameter.clearMessage()
            self.mergeFieldParameter.value = '' 
        
        if not self.mergeDistanceParameter.enabled:
            self.mergeDistanceParameter.clearMessage()
            self.mergeDistanceParameter.value = '' 
        else: # Check if merge distance parameter is a positive number
            if self.mergeDistanceParameter.value:
                mergeDistanceValue = self.mergeDistanceParameter.value
                strDistance = str(mergeDistanceValue).split()[0]
                if float(strDistance) <= 0.0:
                    self.mergeDistanceParameter.setErrorMessage(self.nonPositiveNumberMessage)
            else: # an entered value of '0' will not present as TRUE and trigger the conditional
                self.mergeDistanceParameter.setErrorMessage(self.nonPositiveNumberMessage)

        
        # Check input features
        if self.inLineParameter.value and not self.inLineParameter.hasError():
            # Check for if input feature layer has spatial reference
            # # query for a dataSource attribute, if one exists, it is a lyr file. Get the lyr's data source to do a Describe
            if hasattr(self.inLineParameter.value, "dataSource"):
                if arcpy.Describe(self.inLineParameter.value.dataSource).spatialReference.name.lower() == "unknown":
                    self.inLineParameter.setErrorMessage(self.noSpatialReferenceMessage)
            else:
                if arcpy.Describe(self.inLineParameter.value).spatialReference.name.lower() == "unknown":
                    self.inLineParameter.setErrorMessage(self.noSpatialReferenceMessage)
        if self.outPutCS.value and not self.outPutCS.hasError():
            if not "PROJECTION[" in  self.outPutCS.valueAsText:
                self.outPutCS.setErrorMessage(self.noProjectionInOutputCS)
        
        # Check if cell size parameter is a positive number           
        if self.inCellSizeParameter.value:
            cellsizeValue = self.inCellSizeParameter.value
            if cellsizeValue <= 0.0:
                self.inCellSizeParameter.setErrorMessage(self.nonPositiveNumberMessage)
        else: # an entered value of '0' will not present as TRUE and trigger the conditional
            self.inCellSizeParameter.setErrorMessage(self.nonPositiveNumberMessage)
            
        # Check if search radius parameter is a positive number           
        if self.inSearchRadiusParameter.value:
            radiusValue = self.inSearchRadiusParameter.value
            if radiusValue <= 0.0:
                self.inSearchRadiusParameter.setErrorMessage(self.nonPositiveNumberMessage)
        else: # an entered value of '0' will not present as TRUE and trigger the conditional
            self.inSearchRadiusParameter.setErrorMessage(self.nonPositiveNumberMessage)
        
        #check if the output raster name is valid in a geodatabase
        if self.outRasterParameter.value:  
            self.outRasterName = self.outRasterParameter.valueAsText
        
            # get the directory path and the filename
            self.outWorkspace = os.path.split(self.outRasterName)[0]
            self.rasterFilename = os.path.split(self.outRasterName)[1]
        
            # break the filename into its root and extension, if one exists
            self.fileExt = os.path.splitext(self.rasterFilename)[1]
            self.fileRoot = os.path.splitext(self.rasterFilename)[0]
        
            # check if the workspace is a geodatabase
            self.workspaceExt = os.path.splitext(self.outWorkspace)[1]
        
            if self.workspaceExt and self.fileExt:
                # alert user that raster names cannot contain an extension in a GDB
                self.outRasterParameter.setErrorMessage(self.invalidExtensionMessage)
            else:
        
                # substitue valid characters into the filename root, if necessary 
                self.validFileRoot = arcpy.ValidateTableName(self.fileRoot,self.outWorkspace)

                # get the list of acceptable raster filename extentions
                self.rasterExtensions = globalConstants.rasterExtensions

                # assemble the new filename with any valid character substitutions
                if self.fileExt: # a filename extension was provided
                    if self.fileExt in self.rasterExtensions:
                        self.validFilename = self.validFileRoot + self.fileExt
                        self.validRasterName = os.path.join(self.outWorkspace,self.validFilename)
                    else: 
                        # drop extension from filename, causing the filename comparison below to fail
                        self.validRasterName = os.path.join(self.outWorkspace,self.validFileRoot)
                else: # a filename extension was omitted
                    self.validRasterName = os.path.join(self.outWorkspace,self.validFileRoot)
            
                # if the validated raster name is different than the input raster name, then the
                # input raster name contains invalid characters or symbols
                if self.outRasterName != self.validRasterName:
                    self.outRasterParameter.setErrorMessage(self.invalidTableNameMessage)              

        return