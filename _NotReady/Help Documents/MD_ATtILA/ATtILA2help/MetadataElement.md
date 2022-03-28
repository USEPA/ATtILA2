# Metadata Element

Metadata Element

| \<?xml version='1.0' encoding='utf-8'?\> \<lccSchema xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="lcc" xsi:noNamespaceSchemaLocation="XSD\_FILE\_PATH"\> \<metadata\> \<name\>\</name\> \<description\>\</description\> \</metadata\> \<coefficients\> \<coefficient Id="" Name="" fieldName="" method="" /\> \</coefficients\> \<values\> \<value Id="" Name="" excluded=""\> \<coefficient Id="" value="" /\> \</value\> \</values\> \<classes\> \<class Id="" Name="" filter=""\> \<value Id="" /\> \</class\> \</classes\> \</lccSchema\> |
| --- |


*Basic structure of ATtILA's Land Cover Classification schema XML document with the Metadata element highlighted.*

&nbsp;

The Metadata element contains the name of the coding schema along with a brief description.&nbsp; ATtILA for ArcGIS requires the Metadata element to be present when it parses the the XML document, and it cannot be empty. The Metadata element must contain the following two elements:

&nbsp;

* &nbsp;
  * **name** - text, land cover coding schema name
  * **description** - text,&nbsp; description of land cover coding schema

&nbsp;

Example Metadata element:

| \<metadata\> \<name\>NLCD 2001\</name\> \<description\>National Land Cover Database 2001\</description\> \</metadata\> |
| --- |


&nbsp;

The information contained in the Metadata element is for informational purposes only. It is displayed in the [External LCC Editor](<ExternalLCCEditor.md>)'s Metadata window, and only there. The entries for the name and description attributes can be as long or as short as the user desires.

&nbsp;

**XML Note**

XML is case-sensitive and care should be used when editing the LCC XML documents using a text editor. Wherever possible, element and attribute names for the document have been defined using lowercase characters. The only current exceptions are the attributes "**Id**" and "**Name**" in the Coefficients, Values, and Classes elements. If editing an LCC XML document outside of the [External LCC Editor](<ExternalLCCEditor.md>), these attributes should be capitalized wherever they appear.

&nbsp;

You may notice that in the Metadata element, the \<name\> element is lowercase. The distinction here is that "name" in the Metadata element pertains to an *element*, and that the capitalization rule only applies to an element's *attributes*.

***
_Created with the Personal Edition of HelpNDoc: [Easy EPub and documentation editor](<https://www.helpndoc.com>)_
