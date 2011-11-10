""" Land Cover Classification(LCC) 
    In memory objects reflecting Land Cover Classification information stored in XML(.lcc) file.
    
"""


from xml.dom import minidom
import os
import sys
import constants
from win32com.client import Constants
from glob import glob
from collections import defaultdict
from xml.dom.minidom import NamedNodeMap


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
    
    classId = None
    name = None
    
    attributes = dict() # all xml attributes for class
        
    uniqueValueIds=frozenset()
    uniqueClassIds=frozenset()
    
    __parentLccObj = None
    
    def __init__(self, classNode=None, parentLccObj=None):
        """ Initialize a LandCoverClass Object
        
            classNode(optional): XML class node object
        """        
        
        self.__parentLccObj = parentLccObj
        
        if not classNode is None:
            self.loadLccClassNode(classNode)
            
        
    def loadLccClassNode(self, classNode):
        """ Load a Land Cover Class XML Node """       
 
        # Load specific attributes as object properties
        self.classId = classNode.getAttribute(constants.XmlAttributeId)
        self.name = classNode.getAttribute(constants.XmlAttributeName)   
        if not self.name:
            self.name = ""
            
        # Loop through all child classes to accumulate unique classIds
        tempClassIds = set()
        for landCoverClass in classNode.getElementsByTagName(constants.XmlElementClass):
            classId = str(landCoverClass.getAttribute(constants.XmlAttributeId))
            tempClassIds.add(classId)
        self.uniqueClassIds = frozenset(tempClassIds)
        
        # Loop through all value nodes, in root and in children, to accumulate unique valueIds
        tempValueIds = set()
        parentLccObj = self.__parentLccObj
        includedValueIds = parentLccObj.values.getIncludedValueIds()

        for landCoverValue in classNode.getElementsByTagName(constants.XmlElementValue):
            valueId = int(landCoverValue.getAttribute(constants.XmlAttributeId))
            
            # Values defined as "excluded" are not included here
            if valueId in includedValueIds:
                tempValueIds.add(valueId)
        
        self.uniqueValueIds = frozenset(tempValueIds)
            
        #Load all attributes into dictionary
        self.attributes = {}
        for attributeName, attributeValue in classNode.attributes.items():
            self.attributes[str(attributeName)] = str(attributeValue)
        
class LandCoverValue(object): 
    """ An object that holds all the properties associated with a single land cover value.""" 
    
    valueId = None
    name = None
    excluded = None
    attributes = {}
    
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
            
        #Load all attributes into dictionary
        self.attributes = {}
        for attributeName, attributeValue in valueNode.attributes.items():
            self.attributes[str(attributeName)] = str(attributeValue)

class LandCoverValues(dict):
    """ A container for LandCoverValue objects
    
        Inherits from dict.
        Methods added:  
          getExcludedValueIds 
          getIncludedValueIds
    """     
    
    __excludedValueIds = None
    __includedValueIds = None
    
    def getExcludedValueIds(self):
        """ Returns frozenset containing all valueIds to be excluded(user defined NoData)."""
        
        if self.__excludedValueIds is None:
            
            self.__updateValueIds()

        return self.__excludedValueIds


    def getIncludedValueIds(self):
        """ Returns frozenset containing all valueIds"""
        
        if self.__includedValueIds is None:
            
            self.__updateValueIds()

        
        return self.__includedValueIds
    
    
    def __updateValueIds(self):
        """ Updates internal frozen sets with included/excluded valueIds """

        excludedValueIds = []
        includedValueIds = []
        
        # Loop through all LCObjects in this container
        for valueId, landCoverValueObj in self.iteritems():

            #Excluded values
            if landCoverValueObj.excluded:
                excludedValueIds.append(valueId)
            
            #Included values
            else:
                includedValueIds.append(valueId)

        self.__excludedValueIds = frozenset(excludedValueIds)
        self.__includedValueIds = frozenset(includedValueIds)        
        
        
class LandCoverClasses(dict):
    """ A container for LandCoverClass objects
     
        Inherits from dict. The getUniqueValueIds method
        is added to return all the unique value IDs defined in all classes.
    """

    __uniqueValues = None

    def getUniqueValueIds(self):
        """ Returns frozenset containing all unique value IDs defined in all classes
            
            valueIds defined as excluded in the values section are not included here
        """
        
        if self.__uniqueValues is None:
            
            # Assemble all values found in all classes, repeats are allowed
            tempValues = []
            for _classId, landCoverClassObj in self.iteritems():
                tempValues.extend(landCoverClassObj.uniqueValueIds)

            # repeats purged on conversion to frozenset
            self.__uniqueValues = frozenset(tempValues)
            
        return self.__uniqueValues
            

class LandCoverClassification(object):
    """ An object holding all the details about a land cover classification(lcc)"""
    
    classes = LandCoverClasses()
    values = LandCoverValues()
    metadata = LandCoverMetadata()
    
    __uniqueValueIds = None
    __uniqueValueIdsWithExcludes = None
    
    def __init__(self, lccFilePath=None):
        """ Initialize a LandCoverClassification Object
        
            lccFilePath(optional): Land Cover Classification (.lcc) XML file
        """
        if not lccFilePath is None:
            self.loadFromFilePath(lccFilePath)


    def loadFromFilePath(self, lccFilePath):
        """ Load a new Land Cover Classification (.lcc) File """
        
        # Flush cashed objects, dependent of previous file
        self.__uniqueValueIds = None
        self.__uniqueValueIdsWithExcludes = None
        
        self.lccFilePath = lccFilePath
        lccDocument = minidom.parse(lccFilePath)
        
        # Load Values
        valuesNode = lccDocument.getElementsByTagName(constants.XmlElementValues)[0]
        valueNodes = valuesNode.getElementsByTagName(constants.XmlElementValue)
        tempValues = LandCoverValues()
        for valueNode in valueNodes:
            valueId = int(valueNode.getAttribute(constants.XmlAttributeId))
            landCoverValue = LandCoverValue(valueNode)
            tempValues[valueId] = landCoverValue
        self.values = tempValues        
        
        # Load Classes
        classNodes = lccDocument.getElementsByTagName(constants.XmlElementClass)
        tempClasses = LandCoverClasses() 
        for classNode in classNodes:
            classId = classNode.getAttribute(constants.XmlAttributeId)
            tempClasses[classId] = LandCoverClass(classNode, self) # passing this lccObj as parent
        self.classes = tempClasses
        
        # Load Metadata
        metadataNode = lccDocument.getElementsByTagName(constants.XmlElementMetadata)[0]
        self.metadata = LandCoverMetadata(metadataNode)        

    
    def getUniqueValueIds(self):
        """  A frozenset of all unique values in the lcc file, from both the values and classes, which are not defined excluded. """
        
        if self.__uniqueValueIds is None:
            
            valueIdsInClasses = self.values.getIncludedValueIds()
            valueIdsInValues = self.classes.getUniqueValueIds()
            
            valueIds = list(valueIdsInClasses) + list(valueIdsInValues)
            
            self.__uniqueValueIds = frozenset(valueIds)
            
        return self.__uniqueValueIds


    def getUniqueValueIdsWithExcludes(self):
        """ A frozenset of all unique values in the lcc file, from both the values and classes, excluded values ARE included"""

        if self.__uniqueValueIdsWithExcludes is None:
            
            includedValueIds = list(self.getUniqueValueIds())
            excludedValueIds = list(self.values.getExcludedValueIds())
            
            self.__uniqueValueIdsWithExcludes = frozenset(includedValueIds + excludedValueIds)
        
        return self.__uniqueValueIdsWithExcludes
    

    
    