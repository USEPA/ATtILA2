# Values Element

Values Element

| \<?xml version='1.0' encoding='utf-8'?\> \<lccSchema xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="lcc" xsi:noNamespaceSchemaLocation="XSD\_FILE\_PATH"\> \<metadata\> \<name\>\</name\> \<description\>\</description\> \</metadata\> \<coefficients\> \<coefficient Id="" Name="" fieldName="" method="" /\> \</coefficients\> \<values\> \<value Id="" Name="" excluded=""\> \<coefficient Id="" value="" /\> \</value\> \</values\> \<classes\> \<class Id="" Name="" filter=""\> \<value Id="" /\> \</class\> \</classes\> \</lccSchema\> |
| --- |


*Basic structure of ATtILA's Land Cover Classification schema XML document with the Values element highlighted.*

&nbsp;

The Values element defines the set of values that can exist in a land cover raster. This element is required by ATtILA for ArcGIS to parse the XML document, but it can be empty (i.e., it does not have to contain any \<value\> elements).&nbsp; Value elements are only necessary in two cases:&nbsp;

&nbsp;

1. &nbsp;
   1. if the user wants to exclude the area occupied by a given grid value when determining a reporting unit's effective area (e.g., basing metric calculations on the land area in a reporting unit vs. the total area of the reporting unit), or
   1. if the user is planning to calculate any metrics with the [Land Cover Coefficient Calculator](<LandCoverCoefficientCalculator.md>). In this case \<value\> elements should be added where coefficient weights are known (e.g., the nitrogen loading coefficient for a particular agriculture type).

&nbsp;

***NOTE:** Although values are not necessary in the XML document, if one is using the LCC Editor to construct an LCC XML document, you will be required to have value elements defined in order to assign values to a class element (see [Classes Element*](<ClassesElement.md>)*).*

&nbsp;

If any \<value\> element is provided, it must have the **Id** attribute. The attributes, ***Name*** and ***excluded***, are allowed, but are not necessary. Properties for the \<value\> element attributes are:

&nbsp;

* &nbsp;
  * **Id** - integer
  * ***Name** - text (optional, can be the empty string, "")*
  * ***excluded** - boolean (optional, "true" or "false" or "1" or "0")*

&nbsp;

Example Values element with two \<value\> elements:

| \<values\> \<value Id="11" Name="Open Water" excluded="true" /\> \<value Id="41" Name="Deciduous Forest" /\> \</values\> |
| --- |


&nbsp;

Id Attribute

**Id** is an integer value representing a grid code that may be found in a land cover raster.&nbsp; Values included in the LCC XML document can span the range of expected values of a particular land cover dataset (e.g., NLCD, CCAP, GAP), but all of the values provided in the document do not have to exist in the actual land cover layer. This is often the case when a national-level land cover coding schema is selected by the user, but the input land cover raster has been clipped to a regional study area.

&nbsp;

A potentially more important issue is when all the values located in a land cover raster are not accounted for in the LCC XML document. ATtILA for ArcGIS will examine all of the values provided in the LCC XML document from both the Values section of the document and those provided in the [Classes Element](<ClassesElement.md>) section and compare them to those found in the land cover raster.&nbsp; Any values in the grid not found in the LCC XML document will be reported to the user with a warning message in the Geoprocessing \> Results window. The user can then determine if the reported values were accidentally omitted from the LCC XML document or incorrectly recorded. A report of missing values may also indicate that the wrong LCC Schema was selected for the input raster layer, or that the wrong raster layer was input for the selected LCC Schema.

&nbsp;

Name Attribute (optional)

***Name*** is a text string of any length used to supply a more detailed description of the grid code and/or provide other useful information regarding the value.&nbsp; The ***Name*** attribute may be an empty string (e.g., Name="").

&nbsp;

excluded Attribute (optional)

The attribute, ***excluded***, is used to identify grid codes whose area is to be excluded from the reporting unit's effective area calculation. Effective area can be thought of as the area of interest within a reporting unit that the user wishes to use for percentage based metric calculations.&nbsp; For example, the user may be interested in basing their metric calculations on just the land area in a reporting unit versus the overall total area of the reporting unit.&nbsp; To make the effective area equal to that of the land area, the user would set the ***excluded*** attribute of any water related grid value to "true".&nbsp;

&nbsp;

The default setting for the ***excluded*** attribute is excluded="false" (i.e.,&nbsp; if no ***excluded*** attribute is provided in the \<value\> element, the area associated with that grid value is not excluded from the reporting unit's effective area calculation).&nbsp; When all ***excluded*** attributes are tagged as 'false', the effective area is equal to the total overall area of the reporting unit.

&nbsp;

***CAUTION:** any value tagged as **excluded** = "true", should not be used in any \<class\> element definition within the LCC XML document. The \<class\> element is discussed in the [Classes Element*](<ClassesElement.md>) *section.*&nbsp;

&nbsp;

**Coefficient Elements within Value Elements**

A Value element can also contain one or more Coefficient elements.&nbsp; These Coefficient elements are optional unless the user is planning on generating metrics using the [Land Cover Coefficient Calculator](<LandCoverCoefficientCalculator.md>) tool.&nbsp; See the caution note below for more specifics on when \<coefficient\> elements must be supplied.&nbsp; If any \<coefficient\> element is provided, it needs to contain the following attributes:

&nbsp;

* &nbsp;
  * **Id** - text (Either 'NITROGEN', 'PHOSPHORUS', or 'IMPERVIOUS').&nbsp;
  * **value** - decimal

&nbsp;

Example Values element with one \<value\> element with two \<coefficient\> elements:

| \<coefficients\> \<coefficient Id="NITROGEN" Name="Estimated Nitrogen Loading Based on Land Cover" apField="A" fieldName="N\_Load" /\> \<coefficient Id="PHOSPHORUS" Name="Estimated Phosphorus Loading Based on Land Cover" apField="" fieldName="P\_Load" /\> \</coefficients\>&nbsp; \<values\> \<value Id="41" Name="Deciduous Forest"\> \<coefficient Id="NITROGEN" value="2.447" /\> \<coefficient Id="PHOSPHORUS" value="0.089" /\> \</value\> \</values\> |
| --- |


&nbsp;

Coefficient Element - Id Attribute

**Id** is a text string used to reference a \<coefficient\> element within the LCC XML document's [Coefficients Element](<CoefficientsElement.md>) section. This text string needs to match the **Id** attribute for that \<coefficient\> element exactly.&nbsp; At present, the text string for this attribute is restricted to equal either 'NITROGEN', 'PHOSPHORUS', or 'IMPERVIOUS'.&nbsp; In future releases of ATtILA for ArcGIS, we plan to allow the user to use any string for the this element's **Id** attribute as long as it matches an **Id** attribute found in a corresponding \<coefficient\> element. See the discussion on the attribute, **method**, in [Coefficients Element](<CoefficientsElement.md>) for more details on this.

&nbsp;

Coefficient Element - value Attribute

The attribute **value** is a decimal number representing the coefficient weighting factor assigned to a land cover/land use type. Values for NITROGEN and PHOSPHOROUS should be given in kg per hectare per year. Values for IMPERVIOUS should represent percentages.&nbsp;

&nbsp;

***CAUTION:**&nbsp; For any coefficient-based metric the user selects to calculate when running the [Land Cover Coefficient Calculator*](<LandCoverCoefficientCalculator.md>) *tool, that coefficient \<element\> must be present in all of the \<value\> elements provided in the \<values\> element. Not all values in the input land cover raster need to be accounted for in the LCC XML document when using the [Land Cover Coefficient Calculator*](<LandCoverCoefficientCalculator.md>) *tool, but if a value is included, its \<value\> element must contain the corresponding \<coefficient\> element for the desired metric.*

&nbsp;

**XML Note**

XML is case-sensitive and care should be used when editing the LCC XML documents using a text editor. Wherever possible, element and attribute names for the document have been defined using lowercase characters. The only current exceptions are the attributes "**Id**" and "**Name**" in the Coefficients, Values, and Classes elements. If editing an LCC XML document outside of the [External LCC Editor](<ExternalLCCEditor.md>), these attributes should be capitalized wherever they appear.

&nbsp;

You may notice that in the Metadata element, the \<name\> element is lowercase. The distinction here is that "name" in the Metadata element pertains to an *element*, and that the capitalization rule only applies to an element's *attributes*.

***
_Created with the Personal Edition of HelpNDoc: [Free Qt Help documentation generator](<https://www.helpndoc.com>)_
