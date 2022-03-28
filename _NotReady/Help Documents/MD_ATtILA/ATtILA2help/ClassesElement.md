# Classes Element

Classes Element

| \<?xml version='1.0' encoding='utf-8'?\> \<lccSchema xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="lcc" xsi:noNamespaceSchemaLocation="XSD\_FILE\_PATH"\> \<metadata\> \<name\>\</name\> \<description\>\</description\> \</metadata\> \<coefficients\> \<coefficient Id="" Name="" fieldName="" method="" /\> \</coefficients\> \<values\> \<value Id="" Name="" excluded=""\> \<coefficient Id="" value="" /\> \</value\> \</values\> \<classes\> \<class Id="" Name="" filter=""\> \<value Id="" /\> \</class\> \</classes\> \</lccSchema\> |
| --- |


*Basic structure of ATtILA's Land Cover Classification schema XML document with the Classes element highlighted.*

&nbsp;

The \<classes\> element contains values from a land cover raster grouped into one or more \<class\> elements.&nbsp; The \<classes\> element is required by ATtILA for ArcGIS to parse the XML document, and it must contain at least one \<class\> element. Any provided \<class\> element needs to contain an **Id** attribute. The attributes, ***Name***, ***filter***, and ***xxxField*** (where ***xxxx*** equals a tool name abbreviation), are allowed, but are not necessary. Properties for the \<class\> element attributes are:

&nbsp;

* &nbsp;
  * **Id** - text, unique identifier
  * ***Name** - text (optional, can be the empty string, "")*
  * ***filter** -&nbsp; text, a string of one or more tool name abbreviations ([caem*](<CoreandEdgeMetrics.md>)*, [lcosp*](<LandCoveronSlopeProportions.md>)*, [lcp*](<LandCoverProportions.md>)*, [pm*](<PatchMetrics.md>)*, [rlcp*](<RiparianLandCoverProportions.md>)*, or [splcp*](<SamplePointLandCoverProportions.md>)*) separated by a ";" (optional, can be the empty string, "")*
  * ***xxxxField** - text, where xxxx equals a tool name abbreviation ([lcosp*](<LandCoveronSlopeProportions.md>)*, [lcp,*](<LandCoverProportions.md>) [*rlcp*](<RiparianLandCoverProportions.md>)*, or [splcp*](<SamplePointLandCoverProportions.md>)*). A separate xxxxField attribute can exist for each tool (optional, can be the empty string, "")*

&nbsp;

A \<class\> element can contain either \<value\> elements or additional \<class\> elements but not both types. A \<class\> element contained within another \<class\> element is known as a child class. The containing \<class\> element is the parent class.&nbsp; A \<value\> element within a \<class\> element has only one attribute:

&nbsp;

* &nbsp;
  * **Id** - integer, corresponds to a land cover/land use grid value

&nbsp;

Example Classes element with one \<class\> element:

| \<classes\> \<class Id="nat" Name="All natural land use" filter="" lcpField="NINDEX"\> \<value Id="41" /\> \<value Id="42" /\> \<value Id="43" /\> \<value Id="51" /\> \<value Id="52" /\> \</class\> \</classes\> |
| --- |


&nbsp;

Example Classes element with one parent \<class\> element and two child classes:

| \<classes\> \<class Id="nat" Name="All natural land use" lcpField="NINDEX"\> \<class Id="for" Name="Forest"\> \<value Id="41" /\> \<value Id="42" /\> \<value Id="43" /\> \</class\> \<class Id="shrb" Name="Shrubland"\> \<value Id="51" /\> \<value Id="52" /\> \</class\> \</class\> \</classes\> |
| --- |


&nbsp;

***NOTE:** When a \<class\> element (parent class) has additional \<class\> elements nested within it (child classes), the \<value\> elements from all child classes are combined to define the parent class. For example, if a class, "nat", contains two classes, "for" and "shrb", and "for" is comprised of values 41, 42, and 43 and "shrb" is defined as values 51 and 52, "nat" would be defined as having values 41, 42, 43, 51, and 52.*

&nbsp;

***NOTE:** Empty \<class\> elements are ignored by ATtILA for ArcGIS.*

&nbsp;

***NOTE:** if a value is marked as excluded = "true" in the [Values Element*](<ValuesElement.md>) *section, but is included in a class definition, ATtILA for ArcGIS will ignore the area of that excluded value when summing up the area of the selected class for metric calculations. If all values assigned to the class are tagged as excluded, the output metric is calculated as 0%.*

&nbsp;

Each \<class\> element in the LCC XML document will appear as a selectable metric in the "Report metrics for these classes" input parameter area for tools that utilize the LCC XML document (i.e., [caem](<CoreandEdgeMetrics.md>), [lcosp](<LandCoveronSlopeProportions.md>), [lcp](<LandCoverProportions.md>), [pm](<PatchMetrics.md>), [rlcp](<RiparianLandCoverProportions.md>), and [splcp](<SamplePointLandCoverProportions.md>)). An example for [lcp](<LandCoverProportions.md>) is shown below using the supplied land cover classification schema for the [NLCD 2001 dataset](<NLCD2001ALL.md>).

![Image](<lib/ATtILA%20LCP%20NLCD2001.png>)

&nbsp;

In the above example, the \<class\> element's attributes are listed next to its check box in the following order and format:&nbsp;

&nbsp;

* **Id** - \[***xxxxField*** or auto-generated field name\] ***Name***

&nbsp;

Id Attribute

**Id** is a text string used to identify the defined set of raster grid values as a group (i.e., class) for analysis. In addition, the class **Id** attribute is used as a base to auto-generate output metric field names when no ***xxxxField*** class attribute is provided (see below) or if the ***xxxxField*** attribute is an empty string. Each ATtILA for ArcGIS tool has a predefined prefix and/or suffix which it will use in conjunction with the **Id** attribute string to auto-generate field names. See the help section for each individual tool ([caem](<CoreandEdgeMetrics.md>), [lcosp](<LandCoveronSlopeProportions.md>), [lcp](<LandCoverProportions.md>), [pm](<PatchMetrics.md>), [rlcp](<RiparianLandCoverProportions.md>), and [splcp](<SamplePointLandCoverProportions.md>)) to learn more.

&nbsp;

xxxxField Attribute (optional)

The attribute, ***xxxxField***, where xxxx equals a tool name abbreviation, is a text string used as the default output field name. Only the tools [lcosp](<LandCoveronSlopeProportions.md>), [lcp](<LandCoverProportions.md>), [rlcp](<RiparianLandCoverProportions.md>), and [splcp](<SamplePointLandCoverProportions.md>) can make use of the ***xxxxField*** attribute#8202;***.*** If no ***xxxxField*** attribute is provided or if the ***xxxxField*** attribute contains an empty string, ATtILA for ArcGIS will auto-generate an output field name using the class **Id** attribute as a base (see above). A separate ***xxxxField*** attribute can exist in the \<class\> element for each applicable tool (e.g.,&nbsp; \<class Id="nat" Name="All natural land use" filter="" lcpField="NINDEX" rlcpField="RNatural"\>).

&nbsp;

***CAUTION**: The **Id** attribute, if used for output field naming, or the **xxxxField** attribute, if provided, must be unique among the different \<class\> elements or identical field names can be generated between classes. If duplicate field names are present, only one is added to the output table. During metric runs, all previous values calculated for that field will be overwritten by the last metric processed with the duplicate field name.*

&nbsp;

***CAUTION:** Field name size is limited by the Output table type: dBASE table field names can be 10 characters in length, INFO table field names can be 16 characters in length, and File Geodatabase table field names can be 64 characters in length. *

* &nbsp;
  * *For **xxxxField** attribute strings: ATtILA for ArcGIS will truncate strings that are longer than those allowed, and check to see if the truncated field name is already in the output table. If the truncated field name already exists, the text string will be truncated further to allow a numerical value to be appended to the field name to create a unique entity. A warning message will then be added to the Geoprocessing \> Results window informing the user of what the provided **xxxxField** attribute text string was changed to for the output table.*
  * *For auto-generated field names: If the auto-generated field name is longer than what is allowed, ATtILA for ArcGIS will truncate the field name base (i.e., the class **Id** attribute string), keeping the metric's predefined prefix and/or suffix intact, to shorten the field name.&nbsp; If the truncated field name already exists in the output table, the base string will be truncated further to allow a numerical value to be appended to it to create a unique entity. A warning message will then be added to the Geoprocessing \> Results window informing the user of what the auto-generated field name was changed to before adding it to the output table.*

&nbsp;

***CAUTION:** In addition to size limitations, the **Id** attribute, if used for output field naming, or the **xxxxField** attribute, if provided, must conform to the field naming conventions dictated by the different database systems (dBASE, INFO, or geodatabase). In general, try to restrict field names to just alphanumeric characters and underscores. Use of spaces and special characters should be avoided, as well as beginning a field name with a number or an underscore. Also, avoid using field names that contain words that are considered reserved keywords, such as date, day, month, order, table, text, user, when, where, year, and zone. For more guidelines on the naming of fields, search on "Fundamentals of adding and deleting fields" in the ArcGIS help documentation.*

&nbsp;

***CAUTION:** If an invalid field name is provided in the **xxxxField** attribute, such as a string of spaces, the metric run will fail during execution, and an "Invalid field name" error message will appear in the Geoprocessing \> Results window.*

&nbsp;

Name Attribute (optional)

***Name***, is a text string of any length used to supply a more detailed description of the class and/or provide other useful information regarding it.&nbsp; The ***Name*** attribute may be an empty string (e.g., Name=""). The ***Name*** attribute is not used in metric calculations or output field naming routines.

&nbsp;

filter Attribute (optional)

The ***filter*** attribute is a string of one or more tool name abbreviations ([caem](<CoreandEdgeMetrics.md>), [lcosp](<LandCoveronSlopeProportions.md>), [lcp](<LandCoverProportions.md>), [pm](<PatchMetrics.md>), [rlcp](<RiparianLandCoverProportions.md>), and [splcp](<SamplePointLandCoverProportions.md>)) separated by a semi-colon. It is used to exclude a class from a tool's list of selectable classes in the "Report metrics for these classes" input parameter area. This can be done to reduce clutter within a tool's GUI (e.g., dropping all classes except those related to agriculture for the Land Cover on Slopes Proportions tool) or to prevent classes incongruous for the analysis from being selected (e.g., \<class Id="wetl" Name="All wetland land cover" filter="lcosp"\> will eliminate the wetl class from the Land Cover on Slopes Proportions tool).&nbsp;

&nbsp;

Value element - Id Attribute

The \<value\> element attribute, **Id**, is an integer value representing a grid code that may be found in a land cover raster. Groupings of \<value\> elements within a \<class\> element is dictated solely by the research needs of the user.

&nbsp;

**XML Note**

XML is case-sensitive and care should be used when editing the LCC XML documents using a text editor. Wherever possible, element and attribute names for the document have been defined using lowercase characters. The only current exceptions are the attributes "**Id**" and "**Name**" in the Coefficients, Values, and Classes elements. If editing an LCC XML document outside of the [External LCC Editor](<ExternalLCCEditor.md>), these attributes should be capitalized wherever they appear.

&nbsp;

You may notice that in the Metadata element, the \<name\> element is lowercase. The distinction here is that "name" in the Metadata element pertains to an *element*, and that the capitalization rule only applies to an element's *attributes*.

***
_Created with the Personal Edition of HelpNDoc: [Single source CHM, PDF, DOC and HTML Help creation](<https://www.helpndoc.com/help-authoring-tool>)_
