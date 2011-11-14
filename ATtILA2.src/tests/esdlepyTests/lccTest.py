#Created on Nov 9, 2011
#Michael A. Jackson, jackson.michael@epa.gov

''' Testing for esdlepy.lcc subpackage

'''

import sys
from glob import glob
import esdlepy

thisFilePath = sys.argv[0]
testFilePath = glob(thisFilePath.split("tests")[0] + esdlepy.lcc.constants.PredefinedFileDirName + "\\*.lcc")[0]

lccObj = esdlepy.lcc.LandCoverClassification(testFilePath)

print "METADATA"
print "  name:", lccObj.metadata.name
print "  description:", lccObj.metadata.description

print

print "VALUES"
for key, value in lccObj.values.items():
    print "  {0:8}{1:8}  {2:40}{3:10}  {4}".format(key, value.valueId, value.name, value.excluded, value.attributes)

print

print "ALL CLASSES"
for classId, landCoverClass in lccObj.classes.items():
    print "  classId:{0:8}classId:{1:8}name:{2:40}{3}{4}{5}".format(classId, landCoverClass.classId, landCoverClass.name, landCoverClass.uniqueValueIds, landCoverClass.uniqueClassIds, landCoverClass.attributes)

print

print "UNIQUE VALUES IN CLASSES"
print lccObj.classes.getUniqueValueIds()

print

print "INCLUDED/EXCLUDED VALUES"
print "included:", lccObj.values.getIncludedValueIds()
print "excluded:", lccObj.values.getExcludedValueIds()

print

print "UNIQUE VALUES IN OBJECT"
print "Top level unique value IDs without excludes:", lccObj.getUniqueValueIds()
print "Top level unique value IDs with excludes:", lccObj.getUniqueValueIdsWithExcludes()

print