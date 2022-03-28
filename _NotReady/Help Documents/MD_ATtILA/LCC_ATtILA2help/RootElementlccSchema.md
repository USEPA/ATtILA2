# Root Element: lccSchema

Root Element: lccSchema

| \<?xml version='1.0' encoding='utf-8'?\> \<lccSchema xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="lcc" xsi:noNamespaceSchemaLocation="XSD\_FILE\_PATH"\> \<metadata\> \<name\>\</name\> \<description\>\</description\> \</metadata\> \<coefficients\> \<coefficient Id="" Name="" fieldName="" method="" /\> \</coefficients\> \<values\> \<value Id="" Name="" excluded=""\> \<coefficient Id="" value="" /\> \</value\> \</values\> \<classes\> \<class Id="" Name="" filter=""\> \<value Id="" /\> \</class\> \</classes\> \</lccSchema\> |
| --- |


*Basic structure of ATtILA's Land Cover Classification schema XML document with the lccSchema root element highlighted.*

&nbsp;

The \<lccSchema\> tag is the root element of the LCC XML document. All other elements in the LCC XML document are contained within this element. XML documents are limited to one root element.&nbsp;

&nbsp;

The XML root element can also contain information specific to the location and name of an XML Schema Document (XSD). The XSD document is used for validating the form and contents of the XML file. Information about the XSD document is optional.

&nbsp;

The XSD information, if included, appears in the following form:

| \<root xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="lcc" xsi:noNamespaceSchemaLocation="XSD\_FILE\_PATH"\> |
| --- |


where XSD\_FILE\_PATH is the relative or absolute path of the XML schema file. When the XML file is located in the same folder as the designated XSD file, the XSD\_FILE\_PATH is simply the name of the XSD file.

&nbsp;

The XSD file prepared for validating ATtILA's XML documents is named LCCSchema.xsd.&nbsp; It is located in the ToolboxSource \> LandCoverClassifications folder in the ATtILA for ArcGIS toolbox destination folder ([see Installing ATtILA](<InstallingATtILA.md>)).

&nbsp;

You can include the following line as your root element if you place your custom XML document in the same folder as the XSD file:

| \<lccSchema xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="lcc" xsi:noNamespaceSchemaLocation="LCCSchema\_v2.xsd"\> |
| --- |



***
_Created with the Personal Edition of HelpNDoc: [Easily create PDF Help documents](<https://www.helpndoc.com/feature-tour>)_
