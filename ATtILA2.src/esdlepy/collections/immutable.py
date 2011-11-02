''' Collections which are immutable(unchangeable) after initial creation

    Created on Nov 1, 2011
    
    @author: mjacks07, Michael Jackson, jackson.michael@epa.gov, majgis@gmail.com
    
'''

class tuct(object):
    """ The tuct class. An immutable dictionary (TUple + diCT).
    
        dictionary:  Can only be created from an existing dictionary
    
        Reference:
            http://code.activestate.com/recipes/498072-implementing-an-immutable-dictionary/
    """
    
    def __init__(self, dictionary):
        
        if isinstance(dictionary, dict):
            self.__data = dictionary
        else:
            self.__data = {}
               
    def __repr__(self):
        return repr(self.__data)
    
    def __cmp__(self, dictionary):
        if isinstance(dictionary, tuct):
            return cmp(self.__data, dictionary.__data)
        else:
            return cmp(self.__data, dictionary)
    
    def __len__(self):
        return len(self.__data)
    
    def __getitem__(self, key):
        return self.__data[key]
    
    def copy(self):
        """ Return a shallow copy of the tuct."""
        if self.__class__ is tuct:
            return tuct(self.__data.copy())
        import copy
        __data = self.__data
        try:
            self.__data = {}
            c = copy.copy(self)
        finally:
            self.__data = __data
        c.update(self)
        return c
    
    def keys(self):
        """Return a copy of the tuct's list of keys."""
        return self.__data.keys()
    
    def items(self):
        """ Return a copy of the tuct's list of (key, value) pairs."""
        return self.__data.items()
        
    def iteritems(self):
        """ Return an iterator over the tuct's (key, value) pairs."""
        return self.__data.iteritems()
        
    def iterkeys(self):
        """ Return an iterator over the tuct's keys."""
        return self.__data.iterkeys()
    
    def itervalues(self):
        """ Return an iterator over the tuct's values."""
        return self.__data.itervalues()
    
    def values(self):
        """ Return a copy of the tuct's list of values."""
        return self.__data.values()
        
    def has_key(self, key):
        """ Test for the presence of key in the tuct."""
        return self.__data.has_key(key)
    
    def get(self, key, failobj=None):
        """ Return the value for key if key is in the tuct, else default.
        
            If default is not given, it defaults to None, so that this method never raises a KeyError.
        """
        if not self.has_key(key):
            return failobj
        return self[key]
        
    def __contains__(self, key):
        return key in self.__data
    
    @classmethod
    def fromkeys(cls, iterable, value=None):
        """ Create a new dictionary with keys from iterable and values set to value.
        
            fromkeys() is a class method that returns a new tuct. 
            value defaults to None.
        """
        d = cls()
        for key in iterable:
            d[key] = value
        return d