""" Land Cover Classification(LCC) 


"""
from xml.dom import minidom
import os
import sys
import constants
from win32com.client import Constants
from glob import glob
from collections import defaultdict

class LandCoverMetadata(object):
    """An object that holds all the metadata properties associated with a single LCC document"""
    
    name=None
    description=None
    
    def __init__(self, metadataNode=None):
        """ Initialize a LandCoverMetadata Object"""
    
        if not metadataNode is None:
            self.loadLccMetadataNode(metadataNode)

    def loadLccMetadataNode(self, metadataNode):
        """  Load a Land Cover Metadata XML Node"""
        
        self.name = metadataNode.getElementsByTagName(constants.XmlAttributeName)[0].firstChild.nodeValue
        self.description = metadataNode.getElementsByTagName(constants.XmlAttributeDescription)[0].firstChild.nodeValue
        

class LandCoverClass(object):
    """ An object that holds all the properties associated with a single land cover class.
    
        Values may be duplicated in child classes, only unique valueIds will be reported.
        Classes may be duplicated, only unique classIds will be reported.
    """
    
    classId=None
    name=None
    lcpField=None
    impervious=None
    nitrogen=None
    phosphorus=None
    uniqueValueIds=frozenset()
    uniqueClassIds=frozenset()
    
    def __init__(self, classNode=None):
        """ Initialize a LandCoverClass Object
        
            classNode(optional): XML class node object
        """        
        
        if not classNode is None:
            self.loadLccClassNode(classNode)
            
        
    def loadLccClassNode(self, classNode):
        """ Load a Land Cover Class XML Node """       
 
        # Load attributes
        self.classId = classNode.getAttribute(constants.XmlAttributeId)
        self.name = classNode.getAttribute(constants.XmlAttributeName)   
        self.lcpField = classNode.getAttribute(constants.XmlAttributeLcpField)
        
        #TODO: Convert to float
        self.impervious = classNode.getAttribute(constants.XmlAttributeImpervious)
        self.nitrogen = classNode.getAttribute(constants.XmlAttributeNitrogen) 
        self.phosphorus = classNode.getAttribute(constants.XmlAttributePhosphorus) 
        
        # Loop through all child classes to accumulate unique classIds
        tempClassIds = set()
        for landCoverClass in classNode.getElementsByTagName(constants.XmlElementClass):
            classId = str(landCoverClass.getAttribute(constants.XmlAttributeId))
            tempClassIds.add(classId)
        self.uniqueClassIds = frozenset(tempClassIds)
        
        # Loop through all value nodes, in root and in children, to accumulate unique valueIds
        tempValueIds = set()
        for landCoverValue in classNode.getElementsByTagName(constants.XmlElementValue):
            valueId = int(landCoverValue.getAttribute(constants.XmlAttributeId))
            tempValueIds.add(valueId)
        self.uniqueValueIds = frozenset(tempValueIds)
        
        
class LandCoverValue(object): 
    """ An object that holds all the properties associated with a single land cover value.""" 
    
    valueId=None
    name=None
    excluded=None
    
    def __init__(self, valueNode=None):
        """ Initialize a LandCoverValue Object
        
            valueNode(optional):  XML value node object
        """
        self.defaultNodataValue = False
        
        if not valueNode is None:
            self.loadLccValueNode(valueNode)
    
    
    def loadLccValueNode(self, valueNode):
        """ Load a Land Cover Value XML Node"""

        self.valueId = int(valueNode.getAttribute(constants.XmlAttributeId))
        self.name = valueNode.getAttribute(constants.XmlAttributeName)
        
        nodata = valueNode.getAttribute(constants.XmlAttributeNodata)
    
        if nodata:
            try:
                self.excluded = bool(nodata)
            except:
                self.excluded = self.defaultNodataValue
        else:
            self.excluded = self.defaultNodataValue
        

class LandCoverClasses(dict):
    """ A container for LandCoverClass objects
     
        Inherits from dict. The getUniqueValueIds method
        is added to return all the unique value IDs defined in all classes.
    """

    __uniqueValues = None
        
    def getUniqueValueIds(self):
        """Returns frozenset containing all unique value IDs defined in all classes"""
        
        # Fetch unique vlaues
        if self.__uniqueValues is None:
            
            tempValues = []
            for _classId, landCoverObj in self.iteritems():
                tempValues.extend(landCoverObj.uniqueValueIds)
                
            self.__uniqueValues = frozenset(tempValues)
            
        return self.__uniqueValues
            

class LandCoverClassification(object):
    """ An object holding all the details about a land cover classification"""
    
    classes = LandCoverClasses()
    values = {}
    metadata = LandCoverMetadata()
    
    def __init__(self, lccFilePath=None):
        """ Initialize a LandCoverClassification Object
        
            lccFilePath(optional): Land Cover Classification (.lcc) XML file
        """
        if not lccFilePath is None:
            self.loadFromFilePath(lccFilePath)


    def loadFromFilePath(self, lccFilePath):
        """ Load a new Land Cover Classification (.lcc) File """
        
        self.lccFilePath = lccFilePath
        lccDocument = minidom.parse(lccFilePath)
        
        # Load Classes
        classNodes = lccDocument.getElementsByTagName(constants.XmlElementClass)
        tempClasses = LandCoverClasses()
        for classNode in classNodes:
            classId = classNode.getAttribute(constants.XmlAttributeId)
            tempClasses[classId] = LandCoverClass(classNode)
        self.classes = tempClasses
        
        # Load Values
        valuesNode = lccDocument.getElementsByTagName(constants.XmlElementValues)[0]
        valueNodes = valuesNode.getElementsByTagName(constants.XmlElementValue)
        tempValues = {}
        for valueNode in valueNodes:
            valueId = int(valueNode.getAttribute(constants.XmlAttributeId))
            landCoverValue = LandCoverValue(valueNode)
            tempValues[valueId] = landCoverValue
        self.values = tempValues
        
        # Load Metadata
        metadataNode = lccDocument.getElementsByTagName(constants.XmlElementMetadata)[0]
        self.metadata = LandCoverMetadata(metadataNode)        


#unit testing    
if __name__ == "__main__":
    thisFilePath = sys.argv[0]
    testFilePath = glob(thisFilePath.split("esdlepy")[0] + constants.PredefinedFileDirName + "\\*.lcc")[0]
    
    lccObj = LandCoverClassification(testFilePath)
    
    print "METADATA"
    print "  name:", lccObj.metadata.name
    print "  description:", lccObj.metadata.description
    
    print
    
    print "VALUES"
    for key, value in lccObj.values.items():
        print "  {0:8}{1:8}  {2:40}{3:10}".format(key, value.valueId, value.name, value.excluded)
    
    print
    
    print "ALL CLASSES"
    for classId, landCoverClass in lccObj.classes.items():
        print "  classId:{0:8}classId:{1:8}name:{2:40}lcpField:{3:10}impervious:{4:8}nitrogen:{5:8}phosphorus:{6:8}{7}{8}".format(classId, landCoverClass.classId, landCoverClass.name, landCoverClass.lcpField, landCoverClass.impervious, landCoverClass.nitrogen, landCoverClass.phosphorus, landCoverClass.uniqueValueIds, landCoverClass.uniqueClassIds)

    print
    
    print "UNIQUE VALUES"
    print lccObj.classes.getUniqueValueIds()
    
    
    