# Core and Edge Metrics

Intermediate Files Retained

* **caem\_Raster\[class name\]\[edge width\]\* raster** - Rasters created for each class selected in the "Report metrics for these classes" parameter of the tool, with reclassed values corresponding to the following scheme: 1 - Excluded, 2 - Other, 3 - Edge, 4 - Core. The names of the intermediate rasters have the prefix "caem\_Raster" followed by the land cover class abbreviation, the edge width, and another number (e.g. caem\_Rasterfor30, caem\_Rasterwtlt30, caem\_Rasterfor31, etc.). The final number in the file name is added when the raster is saved in order to give each raster a unique name when the tool is executed more than once with results saved to the same output location.
* **caem\_TabArea\[class name\]\[edge width\]\* table** - A table of areas corresponding to the values in the caem\_Raster\* within each reporting unit. The name of the intermediate table has the prefix "caem\_TabArea" followed by the land cover class abbreviation, the edge width, and another number (e.g. caem\_TabAreafor30, caem\_TabAreawtlt30, caem\_TabAreafor31, etc.). The suffix corresponds to the suffix in the caem\_Raster\*, and, like the raster suffix, is added to give each table a unique name when multiple classes are selected in the tool and when the tool is executed more than once with results saved to the same output location.

***
_Created with the Personal Edition of HelpNDoc: [Easy CHM and documentation editor](<https://www.helpndoc.com>)_
