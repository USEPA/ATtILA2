# Land Cover Classification

Many ATtILA for ArcGIS tools require a Land Cover Classification (LCC) file as one of the input parameters. The LCC file dictates how the tools process the input Land cover grid based on properties of each land cover class. These properties are set within the LCC file:

&nbsp;

* &nbsp;
  * Defines the text description of land cover classes based on the raster integer value.
  * Determines the inclusion or exclusion of specific land cover classes in metric calculations (e.g. limiting calculations to only terrestrial land cover types via the exclusion of water and ice/snow classes).
  * Allows for the grouping of classes (e.g. deciduous, coniferous, and mixed forest classes may be grouped into a single "forest" class).
  * Allows for the assignment of coefficients associated with specific land cover classes to calculate coefficient-based metrics (e.g. impervious percent, nitrogen loading, and phosphorous loading).

&nbsp;

LCC files utilize XML formatting to define these properties for an associated Land cover grid. ATtILA for ArcGIS includes LCC files for some commonly-used Land cover datasets including the National Land Cover Database (NLCD) and the Coast Change Analysis Program (C-CAP). Descriptions of the LCC files that accompany ATtILA for ArcGIS are available in the [Supplied Land Cover Classification Schemas](<SuppliedLandCoverClassificationS.md>) section of this document. Details on the structure of the XML schema and its mandatory and optional elements may be found in [ATtILA's LCC XML Document](<ATtILAsLCCXMLDocument.md>).

&nbsp;

LCC files may be created or edited to allow users to customize the properties of the land cover classes to meet their objectives. As XML files, LCC files may be edited using any standard text editing program. However, it is recommended that LCC file editing be performed using the LCC Editor that accompanies ATtILA for ArcGIS. See [Create or Modify Land Cover Classification](<CreateorModifyLandCoverClassific.md>) for more information on this tool. No previous experience editing XML files is necessary to edit the XML using the LCC Editor, which provides an easy-to-use interface.

&nbsp;

***NOTE:** It is recommended that the LCC file contain entries for all values in the input Land cover grid. However, if the LCC file does not define properties for a Land cover grid value, ATtILA for ArcGIS will alert the user by providing a warning message indicating that a value occurring in the Land cover grid was not defined in the LCC file.*

***
_Created with the Personal Edition of HelpNDoc: [Generate Kindle eBooks with ease](<https://www.helpndoc.com/feature-tour/create-ebooks-for-amazon-kindle>)_
