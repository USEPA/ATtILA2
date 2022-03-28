# Coefficients Element

Coefficients Element

| \<?xml version='1.0' encoding='utf-8'?\> \<lccSchema xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="lcc" xsi:noNamespaceSchemaLocation="XSD\_FILE\_PATH"\> \<metadata\> \<name\>\</name\> \<description\>\</description\> \</metadata\> \<coefficients\> \<coefficient Id="" Name="" fieldName="" method="" /\> \</coefficients\> \<values\> \<value Id="" Name="" excluded=""\> \<coefficient Id="" value="" /\> \</value\> \</values\> \<classes\> \<class Id="" Name="" filter=""\> \<value Id="" /\> \</class\> \</classes\> \</lccSchema\> |
| --- |


*Basic structure of ATtILA's Land Cover Classification schema XML document with the Coefficients element highlighted.*

&nbsp;

The Coefficients element is used to identify and to parameterize the coefficient-based metrics available in the [Land Cover Coefficient Calculator](<LandCoverCoefficientCalculator.md>) tool. This element is required by ATtILA for ArcGIS to parse the LCC XML document, but it can be empty (i.e., it does not have to contain any \<coefficient\> elements).

&nbsp;

***NOTE:** If no \<coefficient\> element is in the XML document when the user attempts to use the [Land Cover Coefficient Calculator*](<LandCoverCoefficientCalculator.md>) *tool, the tool dialog will not populate the "Report metrics for these coefficients" input box when a "Land cover classification scheme" is selected. Despite the missing information, the user is still able to click the OK button to begin the calculation run, but the run will result in an error.*

&nbsp;

If any \<coefficient\> element is provided, it needs to contain the following attributes:

&nbsp;

* &nbsp;
  * **Id** - text, unique identifier
  * **Name** - text, description of coefficient metric
  * **fieldName** - text, name of field to be created for output
  * **method** - text, either "P" or "A"

&nbsp;

Example Coefficients element with three \<coefficient\> elements:

| &nbsp; &nbsp; \<coefficients\> &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="IMPERVIOUS" Name="Percent Cover Total Impervious Area" fieldName="PCTIA" method="P" /\> &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="NITROGEN" Name="Estimated Nitrogen Loading Based on Land Cover" fieldName="N\_Load" method="A" /\> &nbsp; &nbsp; &nbsp; &nbsp; \<coefficient Id="PHOSPHORUS" Name="Estimated Phosphorus Loading Based on Land Cover" fieldName="P\_Load" method="A" /\> &nbsp; &nbsp; \</coefficients\> |
| --- |


&nbsp;

Each coefficient represented by a \<coefficient\> element in the LCC XML document appears in the "Report metrics for these coefficients" parameter in the [Land Cover Coefficient Calculator](<LandCoverCoefficientCalculator.md>) tool dialog and is individually selectable (see below). The element's attributes are listed next to the check box as follows: **Id** - \[**fieldName**\] **Name**

&nbsp; &nbsp; ![Image](<lib/ATtILA%20LCCC%20Dialog.png>)

&nbsp;

Id Attribute

**Id** is a text string of any length that supplies the short name for a coefficient. In this version of ATtILA for ArcGIS, the text string is restricted to 'NITROGEN', 'PHOSPHORUS', or 'IMPERVIOUS'. In a future release, the user will be able to use any string for the **Id** attribute. See the **method** attribute discussion below for more details.

&nbsp;

Name Attribute

**Name** is a text string of any length used to supply a more detailed description of the coefficient and/or provide additional details regarding the metrics that result from tool calculations using the coefficient. It can also be an empty string (e.g., Name="").

&nbsp;

fieldName Attribute

**fieldName** is a text string used to customize the name of the coefficient in the output table field. The length of the text string is dependent on the output table type selected in the [Land Cover Coefficient Calculator](<LandCoverCoefficientCalculator.md>) tool as follows:

&nbsp;

* &nbsp;
  * dBase table - field names are restricted to 10 characters in length.
  * INFO table - field names are restricted to16 characters in length.
  * geodatabase table - field names are restricted to 64 characters in length.&nbsp;

&nbsp;

ATtILA for ArcGIS will truncate field names that are longer than those allowed, and check to see if the truncated field name is already in the output table. If the truncated field name already exists, the text string is truncated further to allow a numerical value to be appended to the field name to create a unique field name. When this occurs, a warning message is added to the Geoprocessing \> Results window informing the user of the changes to the fieldName's text string in the output table.

&nbsp;

In addition to size limitations, the **fieldName** attribute string must conform to the field naming conventions dictated by the different database systems (dBASE, INFO, or geodatabase). In general, try to restrict field names to just alphanumeric characters and underscores. Use of spaces and special characters should be avoided, as well as beginning a field name with a number or an underscore. Also, avoid using field names that contain words that are considered reserved keywords, such as date, day, month, order, table, text, user, when, where, year, and zone. For more guidelines on the naming of fields, search on "Fundamentals of adding and deleting fields" in the ArcGIS help documentation.

&nbsp;

method Attribute

***CAUTION:** In this version of ATtILA for ArcGIS, the **method** attribute is dummy attribute, and exists only as a placeholder.* &nbsp;

In future releases, the **method** attribute will be used to pass an appropriate calculation routine for the coefficent to the [Land Cover Coefficient Calculator](<LandCoverCoefficientCalculator.md>) tool. When implemented, the method element will be restricted to two choices:

&nbsp;

* &nbsp;
  * "A" - the tool will use a "Per Unit Area" calculation routine to calculate metrics associated with the coefficient.
  * "P" - the tool will use a "Percent Area" calculation routine to calculate metrics associated with the coefficient.

&nbsp;

More information on the different calculation routines can be found on the [Land Cover Coefficient Calculator](<LandCoverCoefficientCalculator.md>) page.

&nbsp;

**XML Note**

XML is case-sensitive and care should be used when editing the LCC XML documents using a text editor. Wherever possible, element and attribute names for the document have been defined using lowercase characters. The only current exceptions are the attributes "**Id**" and "**Name**" in the Coefficients, Values, and Classes elements. If editing an LCC XML document outside of the [External LCC Editor](<ExternalLCCEditor.md>), these attributes should be capitalized wherever they appear.

&nbsp;

You may notice that in the Metadata element, the \<name\> element is lowercase. The distinction here is that "name" in the Metadata element pertains to an *element*, and that the capitalization rule only applies to an element's *attributes*.

***
_Created with the Personal Edition of HelpNDoc: [Free EPub producer](<https://www.helpndoc.com/create-epub-ebooks>)_
