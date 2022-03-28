# Sample Point Land Cover Proportions

Intermediate Files Retained

* **splcp\_Buffer\[buffer distance\]\* vector** - A polygon feature class containing all Sample point features buffered by the selected buffer distance within each reporting unit. The name of the intermediate feature class has the prefix "splcp\_Buffer" followed by the buffer distance, then a number (e.g. splcp\_Buffer1000, splcp\_Buffer1001, splcp\_Buffer500, etc.). The number suffix is added when the feature class is saved in order to give each successive feature class a unique name when the tool is executed more than once and results saved to the same output location.
* **splcpTabArea\* table** - A table of areas corresponding to the values in the Land cover raster within each reporting unit. The name of the intermediate table has the prefix "splcpTabArea" followed by a number (e.g. splcpTabArea0, splcpTabArea1, splcpTabArea2, etc.). The number suffix is added when the table is saved in order to give each successive table a unique name when the tool is executed more than once and results saved to the same output location.

***
_Created with the Personal Edition of HelpNDoc: [Generate EPub eBooks with ease](<https://www.helpndoc.com/create-epub-ebooks>)_
