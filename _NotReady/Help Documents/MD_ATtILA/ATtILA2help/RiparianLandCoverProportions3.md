# Riparian Land Cover Proportions

Intermediate Files Retained

* **rlcp\_Buffer\[buffer distance\]\* vector** - A polygon feature class containing all Stream features buffered by the selected buffer distance within each reporting unit. The name of the intermediate feature class has the prefix "rlcp\_Buffer" followed by the buffer distance, then a number (e.g. rlcp\_Buffer1000, rlcp\_Buffer1001, rlcp\_Buffer500, etc.). The number suffix is added when the feature class is saved in order to give each successive feature class a unique name when the tool is executed more than once and results saved to the same output location.
* **rlcpTabArea\* table** - A table of areas corresponding to the values in the Land cover raster within each reporting unit. The name of the intermediate table has the prefix "rlcpTabArea" followed by a number (e.g. rlcpTabArea0, rlcpTabArea1, rlcpTabArea2, etc.). The number suffix is added when the table is saved in order to give each successive table a unique name when the tool is executed more than once and results saved to the same output location.

***
_Created with the Personal Edition of HelpNDoc: [News and information about help authoring tools and software](<https://www.helpauthoringsoftware.com>)_
