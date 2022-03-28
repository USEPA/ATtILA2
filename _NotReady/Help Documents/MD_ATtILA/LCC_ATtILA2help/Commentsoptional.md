# Comments (optional)

Comments (optional)

XML documents can contain commented characters for notes and brief descriptions of sections. Comments are delimited by \<\!-- and end with the first occurrence of --\>.

&nbsp;

The [Supplied Land Cover Classification schemas](<SuppliedLandCoverClassificationS.md>) that come with ATtILA for ArcGIS come with a standardized set of comments (see below). They provide information to the user regarding the contents of the following elements: \<coefficients\>, \<values\>, and \<classes\>. These standardized comments are also inserted when LCC XML documents are created with the [External LCC Editor](<ExternalLCCEditor.md>). Although comments are supplied by the program, they are unnecessary for the functioning of the XML document, and can be deleted. Any LCC XML document created by the user outside of the [External LCC Editor](<ExternalLCCEditor.md>) can omit comments.

&nbsp;

&nbsp;

| &nbsp; \<\!-- &nbsp; &nbsp; &nbsp; &nbsp; \* The coefficients node contains coefficients to be assigned to values. &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* REQUIRED ATTRIBUTES &nbsp; &nbsp; &nbsp; \* Id - text, unique identifier &nbsp; &nbsp; &nbsp; \* Name - text, word or phrase describing coefficient &nbsp; &nbsp; &nbsp; \* fieldName - text, name of field to be created for output &nbsp; &nbsp; &nbsp; \* apMethod - text, "P" or "A", designates "P"ercentage or per unit "A"rea calculation routine&nbsp; &nbsp; --\> |
| --- |


&nbsp;

&nbsp;

&nbsp;

| &nbsp; \<\!-- &nbsp; &nbsp; &nbsp; &nbsp; \* The values node defines the full set of values that can exist in a land cover raster.&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* REQUIRED ATTRIBUTES &nbsp; &nbsp; &nbsp; \* Id - integer, raster code &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; \* OPTIONAL ATTRIBUTES &nbsp; &nbsp; &nbsp; \* Name - text, word or phrase describing value &nbsp; &nbsp; &nbsp; \* excluded - boolean, "true" or "false" or "1" or "0" &nbsp; &nbsp; &nbsp; \*&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - used to exclude values from effective area calculations &nbsp; &nbsp; &nbsp; \*&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - excluded=false is the default &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* A value element can optionally contain one or more coefficient elements&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* REQUIRED COEFFICIENT ATTRIBUTES &nbsp; &nbsp; &nbsp; \* Id - text, must match an Id attribute from a coefficients node element &nbsp; &nbsp; &nbsp; \* value - decimal, weighting/calculation factor&nbsp; &nbsp; --\> |
| --- |


&nbsp;

&nbsp;

&nbsp;

| &nbsp; \<\!--&nbsp; &nbsp; &nbsp; &nbsp; \* The classes node contains values from a land cover raster grouped into one or more classes.&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* REQUIRED ATTRIBUTES &nbsp; &nbsp; &nbsp; \* Id - text, unique identifier, also used for automated generation of output field name&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; \* OPTIONAL ATTRIBUTES &nbsp; &nbsp; &nbsp; \* Name - text, word or phrase describing class &nbsp; &nbsp; &nbsp; \* filter - text, a string of one or more tool name abbreviations separated by a ";" &nbsp; &nbsp; &nbsp; \*&nbsp; &nbsp; &nbsp; &nbsp; - possible abbreviations are: lcp, rlcp, lcosp, splcp, and caeam &nbsp; &nbsp; &nbsp; \*&nbsp; &nbsp; &nbsp; &nbsp; - used to exclude the class from the selectable classes in the tool's GUI &nbsp; &nbsp; &nbsp; \* xxxxField - text, overrides ATtILA-generated field name for output &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - where xxxx equals a tool name abbreviation &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - possible abbreviations are: lcp, rlcp, lcosp, splcp, and caeam &nbsp; &nbsp; &nbsp; \* &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; - a separate xxxxField attribute can exist for each tool&nbsp; &nbsp; &nbsp; &nbsp; \* A class can contain either values or classes but not both types. &nbsp; &nbsp; &nbsp; \* Value elements contain only an Id attribute which refers to a value in a raster. &nbsp; &nbsp; &nbsp; \* Values tagged as excluded="true" in the values node should not be included in any class.&nbsp; &nbsp; --\> |
| --- |



***
_Created with the Personal Edition of HelpNDoc: [Free CHM Help documentation generator](<https://www.helpndoc.com>)_
