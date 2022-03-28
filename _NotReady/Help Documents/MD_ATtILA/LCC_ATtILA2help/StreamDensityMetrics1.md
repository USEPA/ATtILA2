# Stream Density Metrics

Intermediate Files Retained

* **tempReportingUnitFeature\* vector** - A polygon feature class containing reporting units with a new area field in km². The name of the intermediate feature class has the prefix "tempReportingUnitFeature" followed by a number (e.g. tempReportingUnitFeature0, tempReportingUnitFeature1, tempReportingUnitFeature2, etc.). The number suffix is added when the feature class is saved in order to give each successive feature class a unique name when the tool is executed more than once and the results saved to the same output location.
* **StrByRU\* vector** - A line feature class with Stream features intersected with reporting units. The name of the intermediate feature class has the prefix "StrByRU" followed by a number (e.g. StrByRU0, StrByRU1, StrByRU2, etc.). The number suffix is added when the feature class is saved in order to give each successive feature class a unique name when the tool is executed more than once and the results saved to the same output location.

***
_Created with the Personal Edition of HelpNDoc: [Free iPhone documentation generator](<https://www.helpndoc.com/feature-tour/iphone-website-generation>)_
