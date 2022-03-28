# XML

\<?xml version='1.0' encoding='UTF-8'?\>

\<lccSchema xmlns="lcc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="LCCSchema\_v3.xsd"\>

&nbsp; &nbsp; \<metadata\>

&nbsp; &nbsp; &nbsp; &nbsp; \<name\>NLCD 2001 LAND\</name\>

&nbsp; &nbsp; &nbsp; &nbsp; \<description\>National Land Cover Database 2001 LAND Land Cover Classification Schema. Water-related raster values are tagged as EXCLUDED. Excluded values are ignored when calculating the effective area of a reporting unit. Percentage metrics are based on the effective area of a reporting unit, not the total area. Coefficient values for impervious area calculations are based on those reported in Caraco et al. (1998). Those supplied for the nitrogen loading and phosphorous loading estimates were obtained from Reckhow et al. (1980). As coefficient values can vary considerably for a given land cover type across locations, all provided values should be evaluated critically before use and altered when necessary. Complete literature citations are provided in the ATtILA for ArcGIS help file.\</description\>

&nbsp; &nbsp; \</metadata\>

&nbsp; &nbsp; \<\!-- &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* The coefficients node contains coefficients to be assigned to values.

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* REQUIRED ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; \* Id - text, unique identifier

&nbsp; &nbsp; &nbsp; &nbsp; \* Name - text, word or phrase describing coefficient

&nbsp; &nbsp; &nbsp; &nbsp; \* fieldName - text, name of field to be created for output

&nbsp; &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - must conform to the field naming conventions dictated by the output database system

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

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="11" Name="Open Water" excluded="true"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="12" Name="Perennial Ice/Snow" excluded="true"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="21" Name="Open Space Developed"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.1" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="22" Name="Low Intensity Developed"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.4" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="5.5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="1.2" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="23" Name="Medium Intensity Developed"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.6" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="5.5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="1.2" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="24" Name="High Intensity Developed"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.9" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="5.5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="1.2" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="31" Name="Barren Land (Rock/Sand/Clay)"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="41" Name="Deciduous Forest"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="2.5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.25" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="42" Name="Evergreen Forest"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="2.5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.25" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="43" Name="Mixed Forest"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="2.5" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.25" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="51" Name="Dwarf Scrub"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.4" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.04" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="52" Name="Scrub/Shrub"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.4" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.04" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="71" Name="Grassland"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.3" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.06" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="72" Name="Sedge/Herbaceous"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.3" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.06" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="73" Name="Lichen"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.3" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.06" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="74" Name="Moss"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.3" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.06" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="81" Name="Pasture/Hay"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="5.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.9" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="82" Name="Cultivated Crop"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="5.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.9" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="90" Name="Woody Wetland"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; &nbsp; &nbsp; \<value Id="95" Name="Emergent Herbaceous Wetland"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" value="0.02" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" value="0.0" /\>

&nbsp; &nbsp; &nbsp; &nbsp; \</value\>

&nbsp; &nbsp; \</values\>

&nbsp; &nbsp; \<\!--&nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* The classes node contains values from a land cover raster grouped into one or more classes.

&nbsp;&nbsp; &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* REQUIRED ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; \* Id - text, unique identifier, also used for automated generation of output field name

&nbsp; \*&nbsp; &nbsp; - must conform to the field naming conventions dictated by the output database system

&nbsp;&nbsp; &nbsp; &nbsp; &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* OPTIONAL ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; \* Name - text, word or phrase describing class

&nbsp; &nbsp; &nbsp; &nbsp; \* filter - text, a string of one or more tool name abbreviations separated by a ";"

&nbsp; &nbsp; &nbsp; &nbsp; \*&nbsp; &nbsp; &nbsp; &nbsp; - possible abbreviations are: lcp, rlcp, lcosp, splcp, caem, and pm

&nbsp; &nbsp; &nbsp; &nbsp; \*&nbsp; &nbsp; &nbsp; &nbsp; - used to exclude the class from the selectable classes in the tool's GUI

&nbsp; &nbsp; &nbsp; &nbsp; \* xxxxField - text, overrides ATtILA-generated field name for output

&nbsp; &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - where xxxx equals a tool name abbreviation

&nbsp; &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - possible abbreviations are: lcp, rlcp, lcosp, and splcp

&nbsp; &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - a separate xxxxField attribute can exist for each tool

&nbsp; &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - must conform to the field naming conventions dictated by the output database system

&nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; \* A class can contain either values or classes but not both types.

&nbsp; &nbsp; &nbsp; &nbsp; \* Value elements contain only an Id attribute which refers to a value in a raster.

&nbsp; &nbsp; &nbsp; &nbsp; \* Values tagged as excluded="true" in the values node should not be included in any class.

&nbsp;&nbsp; &nbsp; --\>

&nbsp; &nbsp; \<classes\>

&nbsp; &nbsp; &nbsp; &nbsp; \<class Id="NI" Name="All Natural Land Use" filter="" lcpField="NINDEX"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="bar" Name="Barren" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="31" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="for" Name="Forest" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="41" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="42" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="43" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="tun" Name="Tundra" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="51" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="72" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="73" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="74" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="shb" Name="Shrubland" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="52" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="hrb" Name="Herbaceous" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="71" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="wtl" Name="Wetland" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="wtlw" Name="Woody Wetland" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="90" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="wtle" Name="Emergent Wetland" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="95" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; \<class Id="UI" Name="All Human Land Use" filter="" lcpField="UINDEX"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="dev" Name="Developed" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="devo" Name="Open Space Developed" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="21" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="devl" Name="Low Intensity Developed" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="22" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="devm" Name="Medium Intensity Developed" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="23" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="devh" Name="High Intensity Devloped" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="24" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="agr" Name="Agriculture" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="agrp" Name="Pasture/Hay" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="81" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<class Id="agrc" Name="Cultivated Crop" filter=""\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<value Id="82" /\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; &nbsp; &nbsp; \</class\>

&nbsp; &nbsp; \</classes\>

\</lccSchema\>

***
_Created with the Personal Edition of HelpNDoc: [Free EPub and documentation generator](<https://www.helpndoc.com>)_
