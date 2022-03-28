# ATtILA's LCC XML Document

ATtILA for ArcGIS LCC XML Document

ATtILA for ArcGIS Land Cover Classification (LCC) schema documents require a precise XML structure that consists of the following:

* &nbsp;
  * [XML declaration statement](<XMLDeclaration.md>)
  * [Root element (lccSchema)](<RootElementlccSchema.md>)
  * [Metadata element](<MetadataElement.md>)
  * [Coefficients element](<CoefficientsElement.md>)
  * [Values element](<ValuesElement.md>)
  * [Classes element](<ClassesElement.md>)
  * [Comments](<Commentsoptional.md>)

Detailed descriptions, applications, and possible restrictions for each element are provided their respective sections in this document.&nbsp;

&nbsp;

| \<?xml version='1.0' encoding='utf-8'?\> \<lccSchema xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="lcc" xsi:noNamespaceSchemaLocation="XSD\_FILE\_PATH"\> \<metadata\> \<name\>\</name\> \<description\>\</description\> \</metadata\> \<coefficients\> \<coefficient Id="" Name="" fieldName="" method="" /\> \</coefficients\> \<values\> \<value Id="" Name="" excluded=""\> \<coefficient Id="" value="" /\> \</value\> \</values\> \<classes\> \<class Id="" Name="" filter=""\> \<value Id="" /\> \</class\> \</classes\> \</lccSchema\> |
| --- |


*Basic structure of ATtILA's Land Cover Classification schema XML document.*

&nbsp;

It is recommended that users create or edit LCC schema XML documents using the [External LCC Editor](<ExternalLCCEditor.md>) that accompanies ATtILA for ArcGIS to reduce the possibility of introducing errors. However, LCC XML documents may also be created or edited using any standard text editor and the syntax guidelines provided in each section.

Regardless of how a user chooses to create their LCC XML documents, it is strongly recommended that they first become acquainted with the details on LCC XML formatting that are provided in this section. This will give the user a better understanding of how ATtILA for ArcGIS interacts with the land cover grid and will provide a background for understanding how ATtILA for ArcGIS may be customized for user-specific needs.

&nbsp;

XML Fundamentals, Well-Formed Document

An XML document is composed of text content marked up with tags describing the data. These tags look similar to HTML mark-up tags, but unlike HTML, the tags are customized to define what an item is (i.e., a book, a person, a telephone number, etc.) and particular attributes of each defined item (i.e. the book's title, a person's first and last name, whether the telephone number is for a home, business, or mobile device, etc.). In order for an application to correctly parse an XML document into its various pieces, the XML document must be "well-formed"; in other words, it must follow certain rules.

When using the [External LCC Editor](<ExternalLCCEditor.md>) in ATtILA for ArcGIS to modify or create an LCC XML document, the resulting output document will be well-formed with regard to the ATtILA for ArcGIS application. When editing the LCC XML document with a text editor, these general XML rules must be observed:

&nbsp;

* &nbsp;
  * Each start-tag must have a matching end-tag. The end-tag can be either a non-empty elemen, (e.g.&nbsp; "**\<tag\>&nbsp; &nbsp; \</tag\>**"), or an empty element (e.g. "**\<tag&nbsp; &nbsp; /\>**").
  * Attribute values must be quoted.
  * Attribute names must be unique, and XML is case-sensitive: "**name**" is different from "**Name**" which is different from "**NAME**".
  * Comments and processing commands cannot appear inside tags.

&nbsp;

When editing an LCC XML document with a text editor, it is important to check the document for formatting errors and, more importantly, for any violations to the rules and restrictions ATtILA for ArcGIS places on document elements and attributes. The [XML Validation](<XMLValidation.md>) section of this document provides instructions for performing these checks.

The [Supplied Land Cover Classification Schemas](<SuppliedLandCoverClassificationS.md>) that accompany ATtILA for ArcGIS may be useful to review while reading through the following sections. What may initially appear to be complex, hard to decipher documents will become easier to interpret with the background information provided herein.

&nbsp;

LCC XML Document Storage

The [Supplied Land Cover Classification Schemas](<SuppliedLandCoverClassificationS.md>) that accompany ATtILA for ArcGIS are stored in the ToolboxSource \> LandCoverClassifications folder in the ATtILA for ArcGIS toolbox destination folder (see Installing ATtILA). LCC XML documents stored here automatically populate the "Land cover classification scheme" dropdown in each ATtILA tool that requires a land cover classification file ([Core and Edge Metrics](<CoreandEdgeMetrics.md>), [Land Cover on Slopes Proportions](<LandCoveronSlopeProportions.md>), [Land Cover Proportions](<LandCoverProportions.md>), [Riparian Land Cover Proportions](<RiparianLandCoverProportions.md>), and [Sample Point Land Cover Proportions](<SamplePointLandCoverProportions.md>))..

Customized LCC XML documents can exist anywhere on a local or network computer. Each tool that requires an LCC XML document includes a parameter for navigating to the local or network path at which the XML file is stored. However, users may find it more convenient to access their customized LCC XML documents from the "Land cover classification scheme" dropdown in the ATtILA tools, particularly for frequently-used customized LCC XML documents. To facilitate this, store the customized XML files in the ToolboxSource \> LandCoverClassifications folder as indicated above.


***
_Created with the Personal Edition of HelpNDoc: [Benefits of a Help Authoring Tool](<https://www.helpauthoringsoftware.com>)_
