'''
Created on Nov 18, 2011

@author: mjacks07

Constants specific to metric tools  
'''

# Common
noFeaturesMessage = "Dataset exists, but there are no features (zero rows)"
inputIdFieldTypes = ["SmallInteger", "Integer", "String"]
userOption = "User Defined"
optionalFieldsName = "Optional Fields"
descriptionDelim = "  "
qaCheckName = "QACHECK"
metricAddName = "METRICADD"
qaCheckDescription = "{0}{1}-  Quality Assurance Checks".format(qaCheckName, descriptionDelim)
metricAddDescription = "{0}{1}-  Area for all land cover classes".format(metricAddName, descriptionDelim)
srcFolderSuffix = ".src"
tbxFileSuffix = ".tbx"
tbxFileDelim = "__"
tbxSriptToolDelim = "#"

# Land Cover Proportions
lcpMetricDescription = "{0}" + descriptionDelim + "[{1}]  {2}"
