# Unable to Determine Conversion Factor

Unable to Determine Conversion Factor

This error is triggered when ATtILA for ArcGIS is unable to determine the conversion factor necessary to convert output linear units to metric units. The following two possible scenario's have been identified when this may occur.

&nbsp;

&#49;) Output Coordinates are not set to a system defined with angular units of Decimal Degrees.

Please be sure that the Environment Settings \> Output Coordinates are not set to a system defined with angular units of Decimal Degrees. If an Environment Settings \> Output Coordinates is not set, please be sure to select an 'Input reporting unit feature' that does not have a spatial reference defined with angular units of decimal degrees.&nbsp;

&nbsp;

&#50;) Output Coordinates unit name is not found in the look up tables used by ATtILA for ArcGIS for metric conversions

It is also possible for this error to occur if the linear units name defined in the Output Coordinates, if one is set, or the linear units property of the&nbsp; 'Input reporting unit feature', if an Output Coordinates is not set, is not found in ATtILA for ArcGIS's look up table for metric conversion factors. Please compare your linear units with those found in the list of [Conversion Factors](<ConversionFactors.md>) located in the appendix. If the linear units name is not found, it will be necessary to change the Output Coordinates in the Environment Settings to one found in the look table or to project the 'Input reporting unit feature' to a projection with a linear units property known to ATtILA for ArcGIS.

&nbsp;


***
_Created with the Personal Edition of HelpNDoc: [Easily create EPub books](<https://www.helpndoc.com/feature-tour>)_
