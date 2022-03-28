# Core and Edge Metrics

Summary&nbsp;

Calculates the edge-to-area ratio within each reporting unit for selected land cover classes and creates an output table. Edge width is provided by the user.

&nbsp;

Usage

* This tool processes all polygons in the **Reporting unit feature** regardless of selections set. The ability to limit land cover calculations to only selected reporting unit polygons is not supported in this release.
- ***NOTE:** This tool is resource-intensive in terms of both processing time and disk space#8202;**.** Processing time varies depending on the extent and resolution of the input* **Land cover grid**#8202;*, the number of reporting units, and the number of classes selected for processing. To minimize processing time, consider creating a new* **Reporting unit feature** *layer that does not include unwanted reporting units. Also select only the land cover classes in the* **Report metrics for these classes** *parameter that are important for analysis. This tool creates multiple interim rasters during processing which may consume considerable disk space in the Scratch Workspace. If the Scratch Workspace resides on a disk with limited disk space, the tool may fail during processing. To prevent this, consider changing the Scratch Workspace in Environments \> Workspace \> Scratch Workspace to a location with sufficient available disk space, or free up disk space on the disk in which the current Scratch Workspace resides to accommodate the interim rasters.*
* ***NOTE:** To ensure desired results, the* **Land cover grid** *must be in a projected coordinate systems with linear units of measure. *
* The **Reporting unit feature** is a zone dataset.&nbsp;
  * A zone is defined as all areas in the input that have the same value. The areas do not have to be contiguous. The term "value" in this definition refers to the unique values in the **Reporting unit ID field**. Therefore, all polygons with the same reporting unit ID are treated as a single zone.&nbsp;
  * When more than one polygon has the same reporting unit ID, the areas for each polygon are combined and metrics are reported as a single record in the **Output table**.
- As the **Reporting unit feature** is a vector dataset, ArcGIS will perform a vector to raster conversion during processing.
* &nbsp;
  * The **Reporting unit feature** must not contain overlapping polygons. When overlapping polygons exist, the vector to raster conversion assigns the value of the top-most polygon to any overlapping area, thereby erasing the areas of underlying zones and resulting in flawed metric calculations.
  * Use the [Identify Overlapping Polygons](<IdentifyOverlappingPolygons.md>) utility to determine if overlapping polygons exist and parse the reporting unit feature layer into two or more feature classes or shapefiles in which no features overlap.
  * To better control the vector to raster conversion, the tool defaults the **Snap raster** and the **Processing cell size** to that of the **Land cover grid**. These may be changed from within the tool.
  * If the extent of the **Reporting unit feature** is smaller than that of the **Land cover grid**, the user may wish to check the **Reduce land cover grid to smallest recommended size** option. This creates a temporary land cover raster with the processing extent equal to that of the **Reporting unit feature** to avoid unnecessary processing.
- The **Land cover classification scheme** must correspond to the **Land cover grid**.&nbsp;
  - Schemes for common land cover datasets are included with ATtILA for ArcGIS. Supplied schemes may be designated as either "ALL" or "LAND" (e.g. NLCD 2001 ALL vs. NLCD 2001 LAND). Schemes designated as "ALL" include all land cover classes in reporting unit area calculations, while those designated as "LAND" include only terrestrial land cover classes, with non-terrestrial land cover classes such as water and snow/ice excluded. More information about each of the classification schemes supplied with ATtILA for ArcGIS may be found in [Supplied Land Cover Classification Schemas](<SuppliedLandCoverClassificationS.md>).
* &nbsp;
  * In addition to the common land cover schemes, the tool permits a user-defined land cover classification scheme to be used by specifying a **Land cover classification file** (.xml). Refer to [Land Cover Classification](<LandCoverClassification.md>) for more information.
  * ***NOTE:** When a classification scheme with excluded land cover classes is selected, the areas of the excluded classes are disregarded in metric calculations. For example, when selecting a "LAND" classification scheme, the tool will process individual land cover classes and calculate metrics based on the total terrestrial area they occupy within the reporting unit, rather than the percent of the total area within the reporting unit. *
- **Edge width** must be an integer value measuring the number of grid cells. For example, if the **Land cover grid** is at 30-meter cell resolution, an **Edge width** of five (5) would result in a width of (30 X 5) = 150 meters.
* Final output is written to the location specified in the **Output table** parameter. The **Output table** may be saved as a File Geodatabase Table, a dBASE Table, or an INFO Table.
- &nbsp;
  - ***NOTE:** For most consistent results, it is highly recommended that tool output be saved to a file geodatabase.*
  - When saving as a File Geodatabase Table, no extension is necessary for the **Output table** name. The output location must be a file geodatabase.
  - When saving as a dBASE Table, include the .dbf extension in the **Output table** name. dBASE tables may not be saved in a file geodatabase.
  - When saving as an INFO Table, no extension is necessary for the **Output table** name. INFO tables may not be saved in a file geodatabase. A new directory in the output directory called "info" is automatically created in which the INFO tables are stored. INFO tables have limited portability, so it is recommended that output not be saved as an INFO Table if data sharing is important.
- The user may elect to [Add Quality Assurance Fields](<CoreandEdgeMetrics2.md>) and/or [Retain Intermediate Layers Generated During Metric Processing](<CoreandEdgeMetrics1.md>).
  - Choosing to Retain Intermediate Layers saves the intermediate products to one of the following locations:
* &nbsp;
  * &nbsp;
    * When output is saved as a File Geodatabase Table, intermediate products are placed in the same file geodatabase.
    * When ouput is saved as a dBASE Table or an INFO Table, a file geodatabase named "attilaScratchWorkspace" is automatically generated in the same output location specified for the **Output table.** Intermediate products are placed in the attilaScratchWorkspace file geodatabase.
* Output field names are taken from the class element's caemField attribute in the specified **Land cover classification file**. If the caemField attribute is not provided, the following naming scheme applies (Refer to [Classes Element](<ClassesElement.md>) in [ATtILA's LCC XML Document](<ATtILAsLCCXMLDocument.md>) for general information, or the individual **Land cover classification file** for details):&nbsp;
  * \[class\]\_E2A\[edge width\] - The edge-to-area ratio for the land cover class within the reporting unit (e.g. "for\_E2A5" is the name of the field for the edge-to-area ratio metric for the NLCD "Forest" class when a five-cell edge width is used).
  * ***NOTE:** The output field name for each class is shown as the second item next to the class's check box in **Report metrics for these classes.***
  * ***NOTE:** Output field names can be altered by [editing*](<CreateorModifyLandCoverClassific.md>) *the **Land cover classification file**.*
* To describe the amounts of core and edge within each reporting unit for each selected land cover class, two ancillary fields are provided in the **Output table**. These field names follow a naming scheme which involves class abbreviations. Refer to the Classes section of [ATtILA's LCC XML Document](<ATtILAsLCCXMLDocument.md>) for general information, or the individual **Land cover classification file** for details. The ancillary field names in this **Output table** are as follows:
  * \[class\]\_COR\[edge width\] - The percent of the reporting unit comprised of core cells for the land cover class (e.g. "nat\_COR7" is the name of the field for the percent core metric for the NLCD "All natural land use" class when a seven-cell edge width is used).
  * \[class\]\_EDG\[edge width\] - The percent of the reporting unit comprised of edge cells for the land cover class (e.g. "hrbt\_EDG3" is the name of the field for the percent edge metric for the NLCD "All Herbaceous" class when a three-cell edge width is used).

&nbsp;

Syntax&nbsp;

CAEM (Reporting\_unit\_feature, Reporting\_unit\_ID\_field, Land\_cover\_grid, Land\_cover\_classification\_scheme, Land\_cover\_classification\_file, Report\_metrics\_for\_these\_classes, Edge\_width, Output\_table, Processing\_cell\_size, Snap\_raster, Select\_options)&nbsp;

| Parameter | Explanation | Data Type |
| --- | --- | --- |
| Reporting\_unit\_feature | The vector polygon dataset that defines the reporting units. | Feature Layer |
| Reporting\_unit\_ID\_field | The field in the Reporting unit feature layer that contains the unique ID for each reporting unit.&nbsp; It may be an integer or a string data type. | Field |
| Land\_cover\_grid | The raster dataset representing land cover classes upon which core and edge area metrics will be derived within each Reporting unit feature. The class input must be an integer raster layer. | Raster Layer |
| Land\_cover\_classification\_scheme | The land cover classification schemes included in ATtILA and a User Defined option. The default schemes correspond to common input land cover datasets. Two schemes are supplied for each dataset included in ATtILA: {DATASET NAME} ALL - includes all land cover types in the grid with no exclusions. {DATASET NAME} LAND - excludes non-terrestrial land cover types. | String |
| Land\_cover\_classification\_file | The full pathname to the user-defined .xml file for custom or non-standard land cover classification schemes. Pathname is automatically filled when a default scheme is selected. | File |
| Report\_metrics\_for\_these\_classes | A list of the land cover classes and metric combinations for processing. Check the box to calculate metrics for each land cover class and/or combination class desired within the reporting units. | String |
| Edge\_width | The width of the edge, measured in number of grid cells.&nbsp; The input must be an integer value. | Long |
| Output\_table | The output reporting unit metrics table to be created. It is recommended that the Output table be saved within a file geodatabase. | Table |
| Processing\_cell\_size (optional) | The Processing cell size for the zonal operation. The default Processing cell size is the cell size of the input raster land cover data.&nbsp; Optionally, the user may select a different cell size. | Analysis cell size |
| Snap\_raster (optional) | The raster that the cell alignment of the Land cover grid and rasterized Reporting unit feature layer will be matched to during processing. The default Snap raster is the Land cover grid. | Raster Layer |
| Reduce\_land\_cover\_grid\_to\_smallest\_recommended\_size (optional) | Specifies whether the Land cover grid extent will be clipped to that of the Reporting unit feature layer during processing. false - The Land cover grid will not be clipped. This is the default. true - The Land cover grid will be clipped. This option may save processing time if the Land cover grid extent is larger than the extent of the Reporting unit feature layer. | Boolean |
| Select\_options | Three tool options are available to provide additional information: Add Quality Assurance Fields -&nbsp; Adds area fields to the Output table to facilitate quality assurance checking. Add Area Fields for All Land Cover Classes - Adds fields to the Output table that includes the areas of each land cover class and combination class selected. Retain Intermediate Layers Generated During Metric Calculation - Saves the intermediate table and/or raster that is normally deleted after processing is complete. | Multiple Value |


&nbsp;

Credits&nbsp;

There are no credits for this item.

&nbsp;

Environments

Current Workspace, Scratch Workspace, Output Coordinates same as input, Processing extent min of inputs,
***
_Created with the Personal Edition of HelpNDoc: [Easily create CHM Help documents](<https://www.helpndoc.com/feature-tour>)_
