""" Variable constants for tool dialog validation routines

"""

from . import globalConstants as gc

tbxSourceFolderName = "ToolboxSource"

inputIdFieldTypes = ["SmallInteger", "Integer", "String"]
userOption = "User Defined"
optionalFieldsName = "Additional Options"
metricDescription = "{0}" + gc.descriptionDelim + "[{1}]  {2}"
noFeaturesMessage = "Dataset exists, but there are no features (zero rows)"
noSpatialReferenceMessage = "Dataset is missing spatial reference information. Please define projection before proceeding."
noProjectionInOutputCS = "The output coordinate system should be a projected system."
noSpatialReferenceMessageMulti = "One or more datasets is missing spatial reference information. \
Please define a projection for all input datasets before proceeding."
nonIntegerGridMessage = "Input requires an integer grid. Selected dataset not an integer grid."
nonPositiveNumberMessage = "Input requires a positive number. Please enter a value greater than zero before proceeding."
nonPositiveIntegerMessage = "Input requires a positive integer value. Please enter an integer greater than zero before proceeding."
polygonOrIntegerGridMessage = "Non-polygon dataset selected. Input requires a polygon dataset or an integer grid."
integerGridOrPolgonMessage = "Non-integer grid selected. Input requires an integer grid or polygon dataset."
invalidTableNameMessage = "Output raster name is invalid. It may contain invalid characters or symbols, such as ., *, ?, \
 ', <, >, |, and space or has an invalid starting character such as a number."
invalidNumberMessage = "Input requires that the number entered not be in the range 0 - 100. \
Please enter a value outside of this range before proceeding."