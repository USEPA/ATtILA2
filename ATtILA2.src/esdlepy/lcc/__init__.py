
from xml.dom.minidom import parse
import os
import sys
import constants
from win32com.client import Constants
from glob import glob
from collections import defaultdict

class LandCoverMetadata:
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
        
    def clear(self):
        """ Set to empty """
        
        self.name = None
        self.description = None



class LandCoverClass:
    """ An object that holds all the properties associated with a single land cover class."""
    
    classId=None
    name=None
    lcpField=None
    impervious=None
    nitrogen=None
    phosphorus=None
    valueIds=()
    classIds=()
    
    def __init__(self, classNode=None):
        """ Initialize a LandCoverClass Object
        
            classNode(optional): XML class node object
        """        
        
        if not classNode is None:
            self.loadLccClassNode(classNode)
            
        
    def loadLccClassNode(self, classNode):
        """ Load a Land Cover Class XML Node """       
 
        self.classId = classNode.getAttribute(constants.XmlAttributeId)
        self.name = classNode.getAttribute(constants.XmlAttributeName) 
        
        #TODO:  How to handle non-mandatory values    
        self.lcpField = classNode.getAttribute(constants.XmlAttributeLcpField)
        self.impervious = classNode.getAttribute(constants.XmlAttributeImpervious)
        self.nitrogen = classNode.getAttribute(constants.XmlAttributeNitrogen) 
        self.phosphorus = classNode.getAttribute(constants.XmlAttributePhosphorus) 
        
        #TODO: DUMMY VALUES!!!!!!!!!!!!!!
        self.valueIds=(1,2,3)
        self.classIds=("for", "wetl", "ng")
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        
    def clear(self):
        """ Set to empty """
        
        self.classId=None
        self.name=None
        self.lcpField=None
        self.impervious=None
        self.nitrogen=None
        self.phosphorus=None
        self.valueIds=()
        self.classIds=()
 

class LandCoverValue: 
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

        self.valueId = valueNode.getAttribute(constants.XmlAttributeId)
        self.name = valueNode.getAttribute(constants.XmlAttributeName)
        
        nodata = valueNode.getAttribute(constants.XmlAttributeNodata)
    
        if nodata:
            try:
                self.excluded = bool(nodata)
            except:
                self.excluded = self.defaultNodataValue
        else:
            self.excluded = self.defaultNodataValue
        
    def clear(self):
        """Set to empty"""
        
        self.valueId = None
        self.name = None
        self.excluded = None
        

class LandCoverClassification:
    """ An object holding all the details about a land cover classification"""
    
    classes = {}
    values = {}
    metadata = LandCoverMetadata()
    
    def __init__(self, lccFilePath=None):
        """ Initialize a LandCoverClassification Object
        
            lccFilePath(optional): Land Cover Classification (.lcc) XML file
        """
        
        if not lccFilePath is None:
            self.loadFromFilePath(lccFilePath)

    def loadFromFilePath(self, lccFilePath):
        """Loads a new Land Cover Classification (.lcc) File """
        
        self.clear()
        self.lccFilePath = lccFilePath
        lccDocument = parse(lccFilePath)
        
        # Load Classes
        classNodes = lccDocument.getElementsByTagName(constants.XmlElementClass)
        for classNode in classNodes:
            
            classId = classNode.getAttribute(constants.XmlAttributeId)
            self.classes[classId] = LandCoverClass(classNode)

        # Load Values
        valuesNode = lccDocument.getElementsByTagName(constants.XmlElementValues)[0]
        valueNodes = valuesNode.getElementsByTagName(constants.XmlElementValue)
        for valueNode in valueNodes:
            
            valueId = valueNode.getAttribute(constants.XmlAttributeId)
            landCoverValue = LandCoverValue(valueNode)
            self.values[valueId] = landCoverValue
    
        # Load Metadata
        metadataNode = lccDocument.getElementsByTagName(constants.XmlElementMetadata)[0]
        self.metadata = LandCoverMetadata(metadataNode)
    
    def clear(self):
        """ Set current state to empty """

        self.classes.clear()
        self.values.clear()
        self.metadata = None
        


#unit testing    
if __name__ == "__main__":
    thisFilePath = sys.argv[0]
    testFilePath = glob(thisFilePath.split("esdlepy")[0] + constants.PredefinedFileDirName + "\\*.lcc")[0]
    
    lccObj = LandCoverClassification(testFilePath)
    
    print "METADATA"
    print "  name:", lccObj.metadata.name
    print "  description:", lccObj.metadata.description
    lccObj.metadata.clear()
    
    print
    
    print "VALUES"
    for key,value in lccObj.values.items():
        print "  {0:8}{1:8}{2:40}{3:10}".format(key, value.valueId, value.name, value.excluded)
    lccObj.values.clear()
    
    print
    
    print "ALL CLASSES"
    for key, value in lccObj.classes.items():
        print "  {0:8}{1:8}{2:40}{3:10}{4:8}{5:8}{6:8}{7:8}{8:8}".format(key, value.classId, value.name, value.lcpField, value.impervious, value.nitrogen, value.phosphorus, value.valueIds, value.classIds)

    
    
    