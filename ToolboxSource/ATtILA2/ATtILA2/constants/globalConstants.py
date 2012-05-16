""" Global, application level variables

"""

tbxSourceFolderName = "ToolboxSource"
noFeaturesMessage = "Dataset exists, but there are no features (zero rows)"
inputIdFieldTypes = ["SmallInteger", "Integer", "String"]
userOption = "User Defined"
optionalFieldsName = "Additional Options"
descriptionDelim = "  -  "
areaFieldParameters = ["_A","DOUBLE",15,0]
srcFolderSuffix = ".src"
tbxFileSuffix = ".tbx"
tbxFileDelim = "__"
tbxSriptToolDelim = "#"
metricDescription = "{0}" + descriptionDelim + "[{1}]  {2}"
qaCheckName = "QAFIELDS"
metricAddName = "AREAFIELDS"
intermediateName = "INTERMEDIATES"
qaCheckDescription = "{0}{1}Add Quality Assurance Fields".format(qaCheckName, descriptionDelim)
metricAddDescription = "{0}{1}Add Area Fields for All Land Cover Classes".format(metricAddName, descriptionDelim)
intermediateDescription = "{0}{1}Retain Intermediate Layers Generated During Metric Calculation".format(intermediateName, descriptionDelim)
defaultDecimalFieldType = "FLOAT"
defaultIntegerFieldType = "SHORT"
defaultAreaFieldType = "DOUBLE"
fieldOverrideName = "Field"
metricNameTooLong = "Provided metric name too long for output location. Truncated {0} to {1} "