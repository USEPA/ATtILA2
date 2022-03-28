# XML Declaration

XML Declaration

| \<?xml version='1.0' encoding='utf-8'?\> \<lccSchema xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="lcc" xsi:noNamespaceSchemaLocation="XSD\_FILE\_PATH"\> \<metadata\> \<name\>\</name\> \<description\>\</description\> \</metadata\> \<coefficients\> \<coefficient Id="" Name="" fieldName="" method="" /\> \</coefficients\> \<values\> \<value Id="" Name="" excluded=""\> \<coefficient Id="" value="" /\> \</value\> \</values\> \<classes\> \<class Id="" Name="" filter=""\> \<value Id="" /\> \</class\> \</classes\> \</lccSchema\> |
| --- |


*Basic structure of ATtILA's Land Cover Classification schema XML document with the XML declaration statement highlighted.*

&nbsp;

The first line of the LCC XML document is an XML declaration statement. It is not required, but if it is included, it must be the first line of the document. No other character or blank space can precede the declaration statement. The declaration statement allows an XML parser to obtain a basic understanding about how the text document is encoded.

***
_Created with the Personal Edition of HelpNDoc: [Free HTML Help documentation generator](<https://www.helpndoc.com>)_
