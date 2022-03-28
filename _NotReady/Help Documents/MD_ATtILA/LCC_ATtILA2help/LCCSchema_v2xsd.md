# LCCSchema_v2.xsd

\<?xml version="1.0" encoding="utf-8"?\>

\<xs:schema attributeFormDefault="unqualified" elementFormDefault="qualified" xmlns:xs="http://www.w3.org/2001/XMLSchema"

&nbsp;&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; targetNamespace="lcc" xmlns="lcc" xmlns:k="lcc"\>

&nbsp; \<xs:element name="lccSchema"\>

&nbsp; &nbsp; \<xs:complexType\>

&nbsp; &nbsp; &nbsp; \<xs:sequence\>

&nbsp; &nbsp; &nbsp; &nbsp; \<xs:element name="metadata"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:sequence\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:element type="xs:string" name="name"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:element type="xs:string" name="description"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:sequence\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; \</xs:element\>

&nbsp; &nbsp; &nbsp; &nbsp; \<xs:element name="coefficients"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:annotation\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:documentation\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* The coefficients node contains coefficients to be assigned to values.

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* REQUIRED ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* Id - text, unique identifier

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* Name - text, word or phrase describing coefficient

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* fieldName - text, name of field to be created for output

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* method - text, "P" or "A", designates "P"ercentage or per unit "A"rea calculation routine

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:documentation\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:annotation\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:sequence\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:element name="coefficient" maxOccurs="unbounded" minOccurs="0"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:attribute name="Id" use="required"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:simpleType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:restriction base="xs:string"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:enumeration value="NITROGEN"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:enumeration value="PHOSPHORUS"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:enumeration value="IMPERVIOUS"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:restriction\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:simpleType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:attribute\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:attribute type="xs:string" name="Name" use="required"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:attribute name="method" use="required"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:simpleType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:restriction base="xs:string"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:enumeration value="A"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:enumeration value="P"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:restriction\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:simpleType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:attribute\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:attribute name="fieldName" use="required"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:simpleType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:restriction base="xs:string"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:minLength value="1"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:restriction\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:simpleType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:attribute\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:element\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:sequence\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; \</xs:element\>

&nbsp; &nbsp; &nbsp; &nbsp; \<xs:element name="values"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:annotation\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:documentation\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* The values node defines the full set of values that can exist in a land cover raster.

&nbsp;&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* REQUIRED ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* Id - integer, raster code

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \*

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* OPTIONAL ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* Name - text, word or phrase describing value

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* excluded - boolean, "true" or "false" or "1" or "0"

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \*&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - used to exclude values from effective area calculations

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \*&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - excluded=false is the default&nbsp;

&nbsp;&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* A value element can optionally contain one or more coefficient elements

&nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* REQUIRED COEFFICIENT ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* Id - text, must match an Id attribute from a coefficients node element

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* value - decimal, weighting/calculation factor

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:documentation\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:annotation\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:sequence\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:element name="value" maxOccurs="unbounded" minOccurs="0"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:sequence\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:element name="coefficient" maxOccurs="unbounded" minOccurs="0"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:simpleContent\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:extension base="xs:string"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:attribute name="Id" use="required"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:attribute type="xs:decimal" name="value" use="required"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:extension\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:simpleContent\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:element\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:sequence\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:attribute type="xs:int" name="Id" use="required"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:attribute type="xs:string" name="Name" use="optional"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:attribute type="xs:boolean" name="excluded" use="optional"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:unique name="uniqueCoefficient"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:selector xpath="coefficient"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:field xpath="@Id"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:unique\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:element\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:sequence\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; \</xs:element\>

&nbsp; &nbsp; &nbsp; &nbsp; \<xs:element name="classes"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:annotation\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:documentation\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* The classes node contains values from a land cover raster grouped into one or more classes.

&nbsp;&nbsp; &nbsp; &nbsp; &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* REQUIRED ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* Id - text, unique identifier, also used for automated generation of output field name

&nbsp;&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* OPTIONAL ATTRIBUTES

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* Name - text, word or phrase describing class

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* filter - text, a string of one or more tool name abbreviations separated by a ";"

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \*&nbsp; &nbsp; &nbsp; &nbsp; - possible abbreviations are: lcp, rlcp, lcosp, splcp, and caem

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \*&nbsp; &nbsp; &nbsp; &nbsp; - used to exclude the class from the selectable classes in the tool's GUI

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* xxxxField - text, overrides ATtILA-generated field name for output

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - where xxxx equals a tool name abbreviation

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - possible abbreviations are: lcp, rlcp, lcosp, splcp, and caem

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - a separate xxxxField attribute can exist for each tool

&nbsp;

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* A class can contain either values or classes but not both types.

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* Value elements contain only an Id attribute which refers to a value in a raster.

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* Values tagged as excluded="true" in the values node should not be included in any class.

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:documentation\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:annotation\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:sequence\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:element name="class" maxOccurs="unbounded" minOccurs="1" type="classType"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:sequence\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; \</xs:element\>

&nbsp; &nbsp; &nbsp; \</xs:sequence\>

&nbsp; &nbsp; \</xs:complexType\>

&nbsp; &nbsp; \<\!--\<xs:key name="coefficientKey"\>

&nbsp; &nbsp; &nbsp; \<xs:selector xpath="k:coefficients/k:coefficient"/\>

&nbsp; &nbsp; &nbsp; \<xs:field xpath="@Id"/\>

&nbsp; &nbsp; \</xs:key\>

&nbsp; &nbsp; \<xs:keyref name="coefficientKeyRef" refer="k:coefficientKey"\>

&nbsp; &nbsp; &nbsp; \<xs:selector xpath="k:values/k:value/k:coefficient"/\>

&nbsp; &nbsp; &nbsp; \<xs:field xpath="@Id"/\>

&nbsp; &nbsp; \</xs:keyref\>--\>

&nbsp; \</xs:element\>

&nbsp; \<xs:complexType name="classType"\>

&nbsp; &nbsp; \<xs:sequence\>

&nbsp; &nbsp; &nbsp; \<xs:choice minOccurs="1" maxOccurs="1"\>

&nbsp; &nbsp; &nbsp; &nbsp; \<xs:element name="class" maxOccurs="unbounded" minOccurs="0" type="classType"/\>

&nbsp; &nbsp; &nbsp; &nbsp; \<xs:element name="value" maxOccurs="unbounded" minOccurs="0"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:simpleContent\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:extension base="xs:string"\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \<xs:attribute type="xs:int" name="Id" use="required"/\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:extension\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:simpleContent\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:complexType\>

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \</xs:element\>

&nbsp; &nbsp; &nbsp; \</xs:choice\>

&nbsp; &nbsp; \</xs:sequence\>

&nbsp; &nbsp; \<xs:attribute type="xs:string" name="Id" use="required"/\>

&nbsp; &nbsp; \<xs:attribute type="xs:string" name="Name" use="optional"/\>

&nbsp; &nbsp; \<xs:attribute type="xs:string" name="lcpField" use="optional"/\>

&nbsp; &nbsp; \<xs:attribute type="xs:string" name="rlcpField" use="optional"/\>

&nbsp; &nbsp; \<xs:attribute type="xs:string" name="lcospField" use="optional"/\>

&nbsp; &nbsp; \<xs:attribute type="xs:string" name="splcpField" use="optional"/\>

&nbsp; &nbsp; \<xs:attribute type="xs:string" name="caemField" use="optional"/\>

&nbsp; &nbsp; \<xs:attribute type="xs:string" name="filter" use="optional"/\>

&nbsp; \</xs:complexType\>

\</xs:schema\>

***
_Created with the Personal Edition of HelpNDoc: [Produce Kindle eBooks easily](<https://www.helpndoc.com/feature-tour/create-ebooks-for-amazon-kindle>)_
