# XML

\<?xml version='1.0' encoding='UTF-8'?\>

\<lccSchema xmlns="lcc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="LCCSchema\_v2.xsd"\>

&nbsp; &nbsp; \<metadata\>

&nbsp; &nbsp; &nbsp; &nbsp; \<name\>C-CAP ALL\</name\>

&nbsp; &nbsp; &nbsp; &nbsp; \<description\>C-CAP ALL Land Cover Classification Schema. No raster values except those representing NODATA are excluded from the calculation of reporting unit effective area (i.e., effective area equals the total raster area within a reporting unit). Coefficient values for impervious area calculations are based on those reported in Caraco et al. (1998). Those supplied for the nitrogen loading and phosphorous loading estimates were obtained from Reckhow et al. (1980). As coefficient values can vary considerably for a given land cover type across locations, all provided values should be evaluated critically before use and altered when necessary. Complete literature citations are provided in the ATtILA for ArcGIS help file.\</description\>

&nbsp; &nbsp; \</metadata\>

&nbsp; &nbsp; \<\!-- &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* The coefficients node contains coefficients to be assigned to values.

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* REQUIRED ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; \* Id - text, unique identifier

&nbsp; &nbsp; &nbsp; &nbsp; \* Name - text, word or phrase describing coefficient

&nbsp; &nbsp; &nbsp; &nbsp; \* fieldName - text, name of field to be created for output

&nbsp; &nbsp; &nbsp; &nbsp; \* method - text, "P" or "A", designates "P"ercentage or per unit "A"rea calculation routine

&nbsp;&nbsp; &nbsp; --\>

&nbsp; &nbsp; \<coefficients\>

&nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" Name="Percent Cover Total Impervious Area" fieldName="PCTIA" method="P" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" Name="Estimated Nitrogen Loading Based on Land Cover" fieldName="N\_Load" method="A" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" Name="Estimated Phosphorus Loading Based on Land Cover" fieldName="P\_Load" method="A" /\>

&nbsp; &nbsp; \</coefficients\>

&nbsp; &nbsp; \<\!-- &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* The values node defines the full set of values that can exist in a land cover raster.

&nbsp;&nbsp; &nbsp; &nbsp; &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* REQUIRED ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; \* Id - integer, raster code

&nbsp; &nbsp; &nbsp; &nbsp; \*

&nbsp; &nbsp; &nbsp; &nbsp; \* OPTIONAL ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; \* Name - text, word or phrase describing value

&nbsp; &nbsp; &nbsp; &nbsp; \* excluded - boolean, "true" or "false" or "1" or "0"

&nbsp; &nbsp; &nbsp; &nbsp; \*&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - used to exclude values from effective area calculations

&nbsp; &nbsp; &nbsp; &nbsp; \*&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - excluded=false is the default&nbsp;

&nbsp;&nbsp; &nbsp; &nbsp; &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* A value element can optionally contain one or more coefficient elements

&nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* REQUIRED COEFFICIENT ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; \* Id - text, must match an Id attribute from a coefficients node element

&nbsp; &nbsp; &nbsp; &nbsp; \* value - decimal, weighting/calculation factor

&nbsp;&nbsp; &nbsp; --\>

&nbsp; &nbsp; \<values\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="0" Name="Background" excluded="true"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="1" Name="Unclassified"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="2" Name="High Intensity Developed"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.9" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="5.5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="1.2" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="3" Name="Medium Intensity Developed"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.6" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="5.5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="1.2" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="4" Name="Low Intensity Developed"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.4" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="5.5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="1.2" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="5" Name="Open Space Developed"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.1" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="6" Name="Cultivated Crop"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="5.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.9" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="7" Name="Pasture/Hay"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="5.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.9" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="8" Name="Grassland"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.3" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.06" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="9" Name="Deciduous Forest"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="2.5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.25" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="10" Name="Evergreen Forest"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="2.5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.25" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="11" Name="Mixed Forest"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="2.5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.25" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="12" Name="Scrub/Shrub"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.4" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.04" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="13" Name="Palustrine Forested Wetland"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="2.5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.25" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="14" Name="Palustrine Scrub/Shrub Wetland"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.4" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.04" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="15" Name="Palustrine Emergent Wetland"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.3" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.06" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="16" Name="Estuarine Forested Wetland"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="2.5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.25" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="17" Name="Estuarine Scrub/Shrub Wetland"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.4" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.04" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="18" Name="Estuarine Emergent Wetland"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.3" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.06" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="19" Name="Unconsolidated Shore"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="20" Name="Barren Land"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="21" Name="Open Water"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="22" Name="Palustrine Aquatic Bed"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="23" Name="Estuarine Aquatic Bed"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="24" Name="Tundra"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.3" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.06" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="25" Name="Perennial Ice/Snow"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; \</values\>

&nbsp; &nbsp; \<\!--&nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* The classes node contains values from a land cover raster grouped into one or more classes.

&nbsp;&nbsp; &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* REQUIRED ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; \* Id - text, unique identifier, also used for automated generation of output field name

&nbsp;&nbsp; &nbsp; &nbsp; &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* OPTIONAL ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; \* Name - text, word or phrase describing class

&nbsp; &nbsp; &nbsp; &nbsp; \* filter - text, a string of one or more tool name abbreviations separated by a ";"

&nbsp; &nbsp; &nbsp; &nbsp; \*&nbsp; &nbsp; &nbsp; &nbsp; - possible abbreviations are: lcp, rlcp, lcosp, splcp, and caem

&nbsp; &nbsp; &nbsp; &nbsp; \*&nbsp; &nbsp; &nbsp; &nbsp; - used to exclude the class from the selectable classes in the tool's GUI

&nbsp; &nbsp; &nbsp; &nbsp; \* xxxxField - text, overrides ATtILA-generated field name for output

&nbsp; &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - where xxxx equals a tool name abbreviation

&nbsp; &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - possible abbreviations are: lcp, rlcp, lcosp, splcp, and caem

&nbsp; &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - a separate xxxxField attribute can exist for each tool

&nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* A class can contain either values or classes but not both types.

&nbsp; &nbsp; &nbsp; &nbsp; \* Value elements contain only an Id attribute which refers to a value in a raster.

&nbsp; &nbsp; &nbsp; &nbsp; \* Values tagged as excluded="true" in the values node should not be included in any class.

&nbsp;&nbsp; &nbsp; --\>

&nbsp; &nbsp; \<classes\>

&nbsp; &nbsp; &nbsp; &nbsp; \<class Id="NI" Name="All Natural Land Use" filter="" lcpField="NINDEX"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="hrb" Name="Herbaceous" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="8" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="for" Name="Forest" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="9" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="10" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="11" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="shb" Name="Shrubland" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="12" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="wtl" Name="Wetland" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="wtlw" Name="Woody Wetland" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="13" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="14" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="16" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="17" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="wtle" Name="Emergent Wetland" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="15" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="18" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="bar" Name="Barren" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="19" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="20" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="wtr" Name="Water" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="21" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="22" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="23" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="25" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="tun" Name="Tundra" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="24" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; \<class Id="UI" Name="All Human Land Use" filter="" lcpField="UINDEX"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="dev" Name="Developed" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="devh" Name="High Intensity Developed" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="2" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="devm" Name="Medium Intensity Developed" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="3" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="devl" Name="Low Intensity Developed" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="4" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="devo" Name="Open Space Developed" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="agr" Name="Agriculture" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="agrc" Name="Cultivated Crop" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="6" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="agrp" Name="Pasture/Hay" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="7" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; \<class Id="UC" Name="Unclassified" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="1" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; \</classes\>

\</lccSchema\>

***
_Created with the Personal Edition of HelpNDoc: [Generate Kindle eBooks with ease](<https://www.helpndoc.com/feature-tour/create-ebooks-for-amazon-kindle>)_
