# Excluded Values in Class Definitions

Excluded Values in Class Definitions

This warning message is triggered when a value is marked as excluded = "true" in the [Values Element](<ValuesElement.md>) section of the LCC XML document, but is also included in one or more class definitions in the [Classes Element](<ClassesElement.md>) section. The warning message will also provide the class name that contains the value tagged as excluded.

&nbsp;

The value attribute, ***excluded,*** (see [Values Element](<ValuesElement.md>) in [ATtILA's LCC XML Document](<ATtILAsLCCXMLDocument.md>)) is used to identify grid codes whose area is to be excluded from the reporting unit's effective area calculation. Effective area can be thought of as the area of interest within a reporting unit that the user wishes to use for percentage based metric calculations.&nbsp; For example, the user may be interested in basing their metric calculations on just the land area in a reporting unit versus the overall total area of the reporting unit.&nbsp; To make the effective area equal to that of the land area, the user would set the ***excluded*** attribute of any water related grid value to "true".&nbsp;

&nbsp;

Values attributed as excluded = "true" included in any class definition in the [Classes Element](<ClassesElement.md>) section of the LCC XML document create an ambiguous situation for ATtILA for ArcGIS. When this occurs,&nbsp; ATtILA for ArcGIS will ignore the area of that excluded value when summing up the area of the selected class for metric calculations, as well as ignoring its area in the calculation of the effective area.

&nbsp;

The following example illustrates the point.&nbsp;

&nbsp;

Assume a land cover raster layer contains four land cover types, values 1, 2, 3, and 4 with value 1 attributed as excluded = "true". Only one class has been defined named "Forest", and consists of values 1 and 2. For our example, the different land cover types have the following areas within a reporting unit:

&nbsp;

value 1 = 100 square meters

value 2 = 200 square meters

value 3 = 300 square meters

value 4 = 400 square meters&nbsp;

&nbsp;

If the [Land Cover Proportions](<LandCoverProportions.md>) tool is run, the output for pForest will be calculated as follows:

&nbsp;

pForest = (Area of Forest / Effective Area of Reporting Unit) \* 100

&nbsp;

If value 1 was not attributed as excluded = "true", then the calculations would be as follows:

&nbsp;

pForest = ((Area of value 1 + Area of value 2) / (Area of value 1 +Area of value 2 + Area of value 3 + Area of value 4))

pForest = ((100 sq m + 200 sq m) / (100 sq m + 200 sq m + 300 sq m + 400 sq m)) \* 100

pForest = (300 sq m / 1000 sq m) \* 100

pForest = 30

&nbsp;

But if value 1 is attributed as excluded = "true", then the calculations will adjust to the following:

&nbsp;

pForest = ((Area of value 2) / (Area of value 2 + Area of value 3 + Area of value 4))

pForest = ((200 sq m) / (200 sq m + 300 sq m + 400 sq m)) \* 100

pForest = (200 sq m / 900 sq m) \* 100

pForest = 22.22

&nbsp;

***NOTE:** If all values assigned to the class are tagged as excluded, the output metric is calculated as 0%.*


***
_Created with the Personal Edition of HelpNDoc: [Free CHM Help documentation generator](<https://www.helpndoc.com>)_
