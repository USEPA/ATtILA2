# Patch Metrics

Intermediate Files Retained

* **pm\_\[class name\]\_PatchRast\* raster** - Rasters created for each class selected in the **Report metrics for these classes** parameter of the tool, with values corresponding to the following scheme:&nbsp;
  * \-9999 - Excluded
  * &nbsp;0 - Other&nbsp;
  * &#49; - n, a unique number assigned to each distinct patch of the selected class&nbsp;

The names of the intermediate rasters have the prefix "pm\_" followed by the land cover class abbreviation, the suffix "\_PatchRast", and another number (e.g. pm\_wtl\_PatchRast0, pm\_wtl\_PatchRast1, pm\_wtl\_PatchRast2, etc.). The final number in the file name is added when the raster is saved in order to give each raster a unique name when the tool is executed more than once with results saved to the same output location.

The processes involved in creating this raster are as follows:

1. &nbsp;
   1. Reclass the input land cover grid so that cells representing the selected class = 3), cells with values marked as excluded = -9999, and all other land cover cells = 0.
   1. If a **Maximum separation** value is NOT provided:
      1. Assign unique values to each distinct clump of class cells by use of the regiongroup command. Use the eight neighbor rule to determine connectivity.
   1. If a **Maximum separation** value is provided:
      1. Create a single value class raster by setting to NULL cells in the reclassed raster with values less than 3.
      1. Use a euclidean distance operation on the class patch and NULL raster to buffer the classes out by the supplied maximum separation distance.
      1. Assign unique values to each distinct clump of class cells by use of the regiongroup command. Use the eight neighbor rule to determine connectivity.
      1. Trim the buffered regiongroup patches to the original boundaries of the patch clumps by use of the con statement and the reclass grid (if it's a patch in the reclass grid (value = 3) assign it the regiongroup number, else leave the other values (-9999, 0) alone).
   1. If a **Minimum patch size** value is provided:
      1. Eliminate all patches below the **Minimum patch size** (any regiongroup value with a value in the COUNT field less than the **Minimum patch size**, set its value to 0.
   1. Add the excluded class areas back to the raster if any are indicated.

The purpose of this intermediate raster product is to identify individual patches, non-patch areas, and excluded land cover cells for metric calculations.

* **pm\_\[class name\]\_PatchPoly\* vector** - A polygon feature class of all patches of \[class name\] derived from the pm\_\[class name\_PatchRast using the Raster to Polygon conversion operation. The Simplify polygons option was unchecked to force the polygon edges to conform to the cell boundaries of the input raster. The gridcode field contains the unique identifier for each distinct patch. The name of the intermediate feature class has the prefix "pm\_" followed by the land cover class abbreviation, the suffix "\_PatchPoly", and another number (e.g. pm\_wtl\_PatchPoly0, pm\_wtl\_PatchPoly1, pm\_wtl\_PatchPoly2, etc.). The final number in the file name is added when the feature class is saved in order to give each feature class a unique name when the tool is executed more than once with results saved to the same output location.
* **pm\_\[class name\]\_PatchPoly\_Diss\* vector** - A polygon feature class of all patches of \[class name\] after performing a Dissolve on the pm\_\[class name\_PatchPoly feature class using gridcode as the dissolve field. Gridcode is the unique identifier for each distinct patch. The name of the intermediate feature class has the prefix "pm\_" followed by the land cover class abbreviation, the suffix "\_PatchPoly\_Diss", and another number (e.g. pm\_wtl\_PatchPoly\_Diss0, pm\_wtl\_PatchPoly\_Diss1, pm\_wtl\_PatchPoly\_Diss2, etc.). The final number in the file name is added when the feature class is saved in order to give each feature class a unique name when the tool is executed more than once with results saved to the same output location.
- &nbsp;
  - ***NOTE:** Due to the complex pattern of some patches, the dissolve function may not create a single multipart polygon for each distinct patch. A quick check to see if duplicate values are found in the gridcode field by using either the Frequency tool or by the field Summarize... option.*
* **pm\_\[class name\]\_PatchCentroids\* vector** - A point feature class depicting the cell centroids of cells delimiting patches in the pm\_\[class name\]\_PatchRast\* raster with the unique patch identifier found in the grid\_code field. The name of the intermediate feature class has the prefix "pm\_" followed by the land cover class abbreviation, the suffix "\_PatchCentroids", and another number (e.g. pm\_wtl\_PatchCentroids0, pm\_wtl\_PatchCentroids1, pm\_wtl\_PatchCentroids2, etc.). The final number in the file name is added when the feature class is saved in order to give each feature class a unique name when the tool is executed more than once with results saved to the same output location.

***
_Created with the Personal Edition of HelpNDoc: [Easily create HTML Help documents](<https://www.helpndoc.com/feature-tour>)_
