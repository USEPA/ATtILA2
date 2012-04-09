'''
Created on Nov 18, 2011

@author: mjacks07

Constants specific to metric tools  
'''

# Common
tbxSourceFolderName = "ToolboxSource"
noFeaturesMessage = "Dataset exists, but there are no features (zero rows)"
inputIdFieldTypes = ["SmallInteger", "Integer", "String"]
userOption = "User Defined"
optionalFieldsName = "Additional Options"
descriptionDelim = "  -  "
qaCheckName = "QAFIELDS"
metricAddName = "AREAFIELDS"
areaFieldParameters = ["_A","DOUBLE",15,0]
qaCheckDescription = "{0}{1}Add Quality Assurance Fields".format(qaCheckName, descriptionDelim)
metricAddDescription = "{0}{1}Add Area Fields for All Land Cover Classes".format(metricAddName, descriptionDelim)
srcFolderSuffix = ".src"
tbxFileSuffix = ".tbx"
tbxFileDelim = "__"
tbxSriptToolDelim = "#"

# Land Cover Proportions
lcpMetricDescription = "{0}" + descriptionDelim + "[{1}]  {2}"
