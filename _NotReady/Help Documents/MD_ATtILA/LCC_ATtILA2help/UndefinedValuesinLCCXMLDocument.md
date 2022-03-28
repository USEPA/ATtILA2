# Undefined Values in LCC XML Document

Undefined Values in the LCC XML Document

For tools in ATtILA for ArcGIS that utilize an [LCC XML document](<ATtILAsLCCXMLDocument.md>), (i.e., tools that utilize a land cover raster input) ATtILA for ArcGIS will examine all of the values found in that tool's selected land cover raster and compare them to those values supplied in the LCC XML document. The values in the LCC XML document are gathered from both the [Values Element](<ValuesElement.md>) section of the document and the [Classes Element](<ClassesElement.md>) section.&nbsp; Any values found in the grid but not found in the LCC XML document will be reported to the user with a warning message in the Geoprocessing \> Results window. The user can then determine if the reported values were either accidentally or purposely omitted from the LCC XML document or were possibly incorrectly transcribed. A report of missing values may also indicate that the wrong LCC Schema was selected for the input raster layer, or that the wrong raster layer was input for the selected LCC Schema.

&nbsp;

***NOTE: Not all values found in the land cover grid need to be included in the LCC XML document.** Only land cover values that are of interest to the user (e.g., values for forest or agriculture land cover types) need to be accounted for. If this is the case, and the LCC XML document was constructed to analyze only a subset of land cover classes from the land cover raster, then the warning message from ATtILA from ArcGIS is superfluous and can be ignored.*

***
_Created with the Personal Edition of HelpNDoc: [Easily create EBooks](<https://www.helpndoc.com/feature-tour>)_
