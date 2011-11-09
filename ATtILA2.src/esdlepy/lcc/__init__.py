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
    __parent = None
    
    def __init__(self, parent=None):
        
        self.__parent = parent
        
        
    def getUniqueValueIds(self):
        """ Returns frozenset containing all unique value IDs defined in all classes
            
            valueIds defined as excluded in the values section are not included here
        """
        
        if self.__uniqueValues is None:
            
            # Assemble all values found in all classes, repeats are allowed
            # ValueIds for values defined as excluded in values section are not included here
            parentLccObj = self.__parent    
            includedValueIds = parentLccObj.values.getIncludedValueIds()
            tempValues = []
            for _classId, landCoverClassObj in self.iteritems():
                for valueId in landCoverClassObj.uniqueValueIds:
                    if valueId in includedValueIds:
                        tempValues.append(valueId)

            # repeats purged on conversion to frozenset
            self.__uniqueValues = frozenset(tempValues)
            
        return self.__uniqueValues
            

class LandCoverClassification(object):
    """ An object holding all the details about a land cover classification(lcc)"""
    
    classes = LandCoverClasses()
    values = LandCoverValues()
    metadata = LandCoverMetadata()
    
    __uniqueValueIds = None
    
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
        tempClasses = LandCoverClasses(self) # passing lccObj as parent
        for classNode in classNodes:
            classId = classNode.getAttribute(constants.XmlAttributeId)
            tempClasses[classId] = LandCoverClass(classNode)
        self.classes = tempClasses
        
        # Load Values
        valuesNode = lccDocument.getElementsByTagName(constants.XmlElementValues)[0]
        valueNodes = valuesNode.getElementsByTagName(constants.XmlElementValue)
        tempValues = LandCoverValues()
        for valueNode in valueNodes:
            valueId = int(valueNode.getAttribute(constants.XmlAttributeId))
            landCoverValue = LandCoverValue(valueNode)
            tempValues[valueId] = landCoverValue
        self.values = tempValues
        
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





if __name__ == "__main__":
    
    
    #unit testing    
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
    
    print "UNIQUE VALUES IN CLASSES"
    print lccObj.classes.getUniqueValueIds()
    
    print
    
    print "INCLUDED/EXCLUDED VALUES"
    print "included:", lccObj.values.getIncludedValueIds()
    print "excluded:", lccObj.values.getExcludedValueIds()
    
    print
    
    print "UNIQUE VALUES IN OBJECT"
    print "Top level unique value IDs:", lccObj.getUniqueValueIds()
    