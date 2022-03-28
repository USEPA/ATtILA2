# XML Validation

XML Validation

Validation ensures that any self-edited LCC XML document is both properly formatted as an XML document, and that all elements necessary for ATtILA for ArcGIS are present and correctly populated.

&nbsp;

Validation is not necessary for any LCC XML documents created with the [External LCC Editor](<ExternalLCCEditor.md>) or for any of the [Supplied Land Cover Classification Schemas](<SuppliedLandCoverClassificationS.md>) that came with ATtILA for ArcGIS.&nbsp; If you have used the [External LCC Editor](<ExternalLCCEditor.md>) to create your LCC XML document, you may skip this section.

&nbsp;

**Validation is only recommended for LCC XML documents constructed outside of the [External LCC Editor**](<ExternalLCCEditor.md>).&nbsp; If you have created a self-edited LCC XML file, please continue reading.

&nbsp;

To perform validations, it is necessary to have either an XML editor/validator installed on your computer or by having access to the Internet and to one of several websites that provide validation service. If you do not currently have access to an XML program, an internet search using the phrase, "validation of XML", will locate several options.

&nbsp;

While many programs/websites are available, the procedure for conducting syntax checks and validations are similar between them. We will describe the steps used within the Notepad++ v6.6.3 free source code editor. Notepad++ is available for download from [https://notepad-plus-plus.org](<https://notepad-plus-plus.org/> "target=\"\_blank\"").

&nbsp;

To use Notepad++ for validation,&nbsp; the XML plugin must be installed. To install the plugin, go to the Plugins dropdown menu and select Show Plugin Manager from the Plugin Manager menu item.&nbsp;

![Image](<lib/XML%20Plugins%20Menu.png>)

&nbsp;

Once the Plugin Manager dialog box opens, select the Available tab and then click on XML Tools. Select Install. After installation is complete, close the Plugin Manager dialog.

![Image](<lib/NotePad%20Plugin%20Manager.png>)

&nbsp;

The XML Tools item will now be available from the Plugins dropdown menu.

![Image](<lib/XML%20Tools%20Menu.png>)

&nbsp;

&nbsp;

XML Validation - Step One

Validation is typically a two step process. The first step ensures that the XML document follows standard formatting rules. Some standard rules include:

&nbsp;

* &nbsp;
  * each start-tag must have a matching end-tag. The end-tag can be either a non-empty element, "\<tag\>&nbsp; &nbsp; \</tag\>", or an empty element, "\<tag&nbsp; &nbsp; /\>"
  * attribute values must be quoted
  * attribute names must be unique, but XML is case-sensitive so "name" is different from "Name" which is different from "NAME"
  * comments and processing commands cannot appear inside tags

&nbsp;

Checking of XML syntax rules is rather straightforward. Once your XML LCC documented is loaded into Notepad++, select "Check XML syntax now" from the XML Tools plugin menu.

![Image](<lib/XML%20Tools%20Menu2.png>)

&nbsp;

If all is correct, a message similar to the one below should appear indicating that no errors were detected, and you can proceed to step two.

![Image](<lib/XML%20No%20Syntax%20Error.png>)

&nbsp;

If an error does exist, an error dialog will appear, and the error must be located and corrected before continuing. A couple examples of error messages are provided below.

&nbsp; &nbsp; ![Image](<lib/XML%20Tools%20Parsing%20Error.png>)&nbsp; &nbsp; ![Image](<lib/XML%20Tools%20Parsing%20Error%202.png>)

&nbsp;

Using the information from the error message will often quickly lead to the problem area in the text, but in certain cases, such as in our first example error message, locating and correcting the cause of the error requires a careful examination of the entire XML document. If the errors are not readily apparent, forgo manually editing your LCC XML document, and perform your final edits in the [External LCC Editor](<ExternalLCCEditor.md>).

&nbsp;

Once all syntax errors have been corrected, you can proceed to step two.

&nbsp;

XML Validation - Step Two

The second step of the validation process is ensuring that all XML elements necessary for ATtILA for ArcGIS are present and correctly populated. ATtILA for ArcGIS requires several customized elements and attributes to also be in the XML document (see [ATtILA's LCC XML Document](<ATtILAsLCCXMLDocument.md>)). If these items are missing or their content rules are not followed, ATtILA for ArcGIS may fail to operate or, worse yet, produce incorrect results.

&nbsp;

To assist with this step of the validation, an XML Schema Definition (XSD) file has been provided for the ATtILA for ArcGIS user. An XSD is a type of file that is used to formally describe the elements of an XML document, and to constrain and verify their contents. The XSD provided for ATtILA for ArcGIS specifically controls which elements and attributes are permitted in the LCC XML document, the contents of those items, their order, and whether or not the items are required or optional.

&nbsp;

&nbsp;ATtILA for ArcGIS's XSD file is located in the ToolboxSource \> LandCoverClassifications folder in the ATtILA 10\_0 toolbox destination folder ([see Installing ATtILA](<InstallingATtILA.md>)). It is named, "LCCSchema\_v2.xsd". A copy of its contents can be found in the appendix ([LCCSchema\_v2.xsd](<LCCSchema\_v2xsd.md>)).

&nbsp;

You perform the validation step in much the same way as checking the XML's syntax, but you select "Validate now" from the XML Tools plugin menu instead.

&nbsp;

If you have placed a reference to the XSD file in the [root element of the LCC XML document](<RootElementlccSchema.md>), the XML editor should be able to locate the XSD file and perform the validation checks. If the XSD file is not found in the referenced location or if there is an error in the [root element](<RootElementlccSchema.md>), the following error message may appear:

&nbsp; &nbsp; ![Image](<lib/XML%20Tools%20Schema%20Not%20Found.png>)

&nbsp;

If the LCC XML document does not contain a reference to an XSD file in its [root element](<RootElementlccSchema.md>), Notepad++ will open a "Select file..." dialog allowing you to locate the XSD file yourself.

&nbsp; &nbsp; ![Image](<lib/XML%20Tools%20Select%20XSD.png>)

&nbsp;

Again, the ATtILA for ArcGIS XSD file is located in the ToolboxSource \> LandCoverClassifications folder in the ATtILA 10\_0 toolbox destination folder ([see Installing ATtILA](<InstallingATtILA.md>)). It is named, "LCCSchema\_v2.xsd", and a copy of its contents can be found in the appendix ([LCCSchema\_v2.xsd](<LCCSchema\_v2xsd.md>)).

&nbsp;

If all goes well, an "XML is valid" statement will appear.

&nbsp; &nbsp; ![Image](<lib/XML%20Tools%20Schema%20Valid.png>)

&nbsp;

If any problems are encountered, Notepad++ will alert you with an Information dialog describing the problem. The descriptions tend to be detailed, but the exact location of the troublesome element in the LCC XML document may be difficult to locate (see example errors below).

&nbsp; &nbsp; ![Image](<lib/XML%20Tools%20Schema%20Error%201.png>)

&nbsp;

&nbsp; &nbsp; ![Image](<lib/XML%20Tool%20Schema%20Error%202.png>)

&nbsp;

&nbsp; &nbsp; ![Image](<lib/NewItem4.png>)

&nbsp;

Once validation steps one and two are performed without error reports, your LCC XML document should be ready for use with ATtILA for ArcGIS. If any problems do occur during tool execution, please reread the section, [ATtILA's LCC XML Document](<ATtILAsLCCXMLDocument.md>), and amend your file as necessary. As mentioned above, if the errors are not readily apparent, forgo manually editing your LCC XML document, and perform your final edits in the [External LCC Editor](<ExternalLCCEditor.md>).

***
_Created with the Personal Edition of HelpNDoc: [Full-featured Help generator](<https://www.helpndoc.com/feature-tour>)_
