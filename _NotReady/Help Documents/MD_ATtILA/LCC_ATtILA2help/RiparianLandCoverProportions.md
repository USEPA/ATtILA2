# Riparian Land Cover Proportions

Summary&nbsp;

Calculates the percentages of selected land cover types within the area adjacent to input features in each reporting unit and creates an output table. Input features may be lines or polygons. Adjacency is determined by a buffer distance specified by the user.

&nbsp;

Usage

* This tool processes all polygons in the **Reporting unit feature** regardless of selections set. The ability to limit land cover calculations to only selected reporting unit polygons is not supported in this release.
- This tool is designed to use a vector line or polygon dataset that represents streams, but any vector line or polygon dataset may be used. Caution should be exercised when interpreting results, particularly when using datasets that do not represent streams.
* ***NOTE:** To ensure desired results, the* **Reporting unit feature** *and* **Stream features** *must be in projected coordinate systems with linear units of measure. *
- The **Reporting unit feature** is a zone dataset.&nbsp;
  - A zone is defined as all areas in the input that have the same value. The areas do not have to be contiguous. The term "value" in this definition refers to the unique values in the **Reporting unit ID field**. Therefore, all polygons with the same reporting unit ID are treated as a single zone.&nbsp;
  - When more than one polygon has the same reporting unit ID, the areas for each polygon are combined and metrics are reported as a single record in the **Output table**.
  - ***NOTE:** ArcGIS software has been improved over the years to analyze larger and larger datasets. However, limits do exist and large datasets can still cause problems. The Riparian Land Cover Proportions calculator can fail if an input **Reporting unit feature** contains a large number of reporting units and/or the reporting units cover a significantly large geographical area. Often this type of failure will manifest itself in a [Failed to execute (Intersect)*](<FailedtoexecuteIntersect.md>) *error. See [Failed to execute (Intersect)*](<FailedtoexecuteIntersect.md>) *for possible workarounds.*
* The tool extracts the **Reporting unit feature** polygons that overlay the **Stream features** buffers using an Intersect and Query. This results in an intermediate polygon feature class containing multipart features of all buffer areas in each reporting unit. The tool then performs a vector to raster conversion of the multipart features to create zones for each reporting unit.
- &nbsp;
  - The **Reporting unit feature** must not contain overlapping polygons. When overlapping polygons exist, the vector to raster conversion assigns the value of the top-most polygon to any overlapping area, thereby erasing the areas of underlying zones and resulting in flawed metric calculations.
  - Use the [Identify Overlapping Polygons](<IdentifyOverlappingPolygons.md>) utility to determine if overlapping polygons exist and parse the reporting unit feature layer into two or more feature classes or shapefiles in which no features overlap.
  - To better control the vector to raster conversion, the tool defaults the **Snap raster** and the **Processing cell size** to that of the **Land cover grid**. These may be changed from within the tool.
  - If a disparity exists between the extents of the **Reporting unit feature** and the **Land cover grid**, the user may wish to set the Extent in Environment Settings \> Processing Extent to the smaller of the two to avoid unnecessary processing.
* The **Land cover classification scheme** must correspond to the **Land cover grid**.&nbsp;
  * Schemes for common land cover datasets are included with ATtILA for ArcGIS. Supplied schemes may be designated as either "ALL" or "LAND" (e.g. NLCD 2001 ALL vs. NLCD 2001 LAND). Schemes designated as "ALL" include all land cover classes in the metric calculations, while those designated as "LAND" include only terrestrial land cover classes, with non-terrestrial land cover classes such as water and snow/ice excluded. More information about each of the classification schemes supplied with ATtILA for ArcGIS may be found in [Supplied Land Cover Classification Schemas](<SuppliedLandCoverClassificationS.md>).
- &nbsp;
  - In addition to the common land cover schemes, the tool permits a user-defined land cover classification scheme to be used by specifying a **Land cover classification file** (.xml). Refer to [Land Cover Classification](<LandCoverClassification.md>) for more information.
  - ***NOTE:** When a classification scheme with excluded land cover classes is selected, the areas of the excluded classes are disregarded in metric calculations. For example, when selecting a "LAND" classification scheme, the tool will process individual land cover classes and calculate metrics based on the total terrestrial area they occupy within the reporting unit, rather than the percent of the total area within the reporting unit. *
* **Stream features** may be one or more vector line or polygon datasets. The **Buffer distance** specifies the distance around the input features for which buffer zones are created.
  * When **Stream features** is a line dataset, the buffer occurs on both sides of each line.
  * When **Stream features** is a polygon dataset, the tool treats the polygon perimeters as lines. The buffer occurs on both sides of each polygon perimeter.
- Final output is written to the location specified in the **Output table** parameter. The **Output table** may be saved as a File Geodatabase Table, a dBASE Table, or an INFO Table.
* &nbsp;
  * ***NOTE:** For most consistent results, it is highly recommended that tool output be saved to a file geodatabase.*
  * When saving as a File Geodatabase Table, no extension is necessary for the **Output table** name. The output location must be a file geodatabase.
  * When saving as a dBASE Table, include the .dbf extension in the **Output table** name. dBASE tables may not be saved in a file geodatabase.
  * When saving as an INFO Table, no extension is necessary for the **Output table** name. INFO tables may not be saved in a file geodatabase. A new directory in the output directory called "info" is automatically created in which the INFO tables are stored. INFO tables have limited portability, so it is recommended that output not be saved as an INFO Table if data sharing is important.
* The user may elect to [Add Quality Assurance Fields](<RiparianLandCoverProportions1.md>), [Add Area Fields](<RiparianLandCoverProportions2.md>) and/or [Retain Intermediate Layers Generated During Metric Processing](<RiparianLandCoverProportions3.md>).
  * Choosing to Retain Intermediate Layers saves the intermediate products to one of the following locations:
- &nbsp;
  - &nbsp;
    - When output is saved as a File Geodatabase Table, intermediate products are placed in the same file geodatabase.
    - When ouput is saved as a dBASE Table or an INFO Table, a file geodatabase named "attilaScratchWorkspace" is automatically generated in the same output location specified for the **Output table.** Intermediate products are placed in the attilaScratchWorkspace file geodatabase.
- Output field names are taken from the class element's rlcpField attribute in the specified **Land cover classification file**. If the rlcpField attribute is not provided, the following naming scheme applies (Refer to [Classes Element](<ClassesElement.md>) in [ATtILA's LCC XML Document](<ATtILAsLCCXMLDocument.md>) for general information, or the individual **Land cover classification file** for details):&nbsp;
  - r\[class\]\[buffer distance\] - The percent of the total buffered area in the reporting unit occupied by the land cover class. For example, values in a field named "rfor100" would represent the percent of land occupied by the NLCD "Forest" class within all 100-meter buffers in the reporting unit.
  - ***NOTE:** The output field name for each class is shown as the second item next to the class's check box in **Report metrics for these classes.***
  - ***NOTE:** Output field names can be altered by [editing*](<CreateorModifyLandCoverClassific.md>) *the **Land cover classification file**.*

&nbsp;

Syntax&nbsp;

RLCP (Reporting\_unit\_feature, Reporting\_unit\_ID\_field, Land\_cover\_grid, Land\_cover\_classification\_scheme, Land\_cover\_classification\_file, Report\_metrics\_for\_these\_classes, Stream\_features, Buffer\_distance, Output\_table, Processing\_cell\_size, Snap\_raster, Select\_options)&nbsp;

| Parameter | Explanation | Data Type |
| --- | --- | --- |
| Reporting\_unit\_feature | The vector polygon dataset that defines the reporting units. | Feature Layer |
| Reporting\_unit\_ID\_field | The field in the Reporting unit feature layer that contains the unique ID for each reporting unit.&nbsp; It may be an integer or a string data type. | Field |
| Land\_cover\_grid | The raster dataset representing land cover classes to be summarized within each Reporting unit feature. The grid input must be an integer raster layer. | Raster Layer |
| Land\_cover\_classification\_scheme | The land cover classification schemes included in ATtILA and a User Defined option. The default schemes correspond to common input land cover datasets. Two schemes are supplied for each dataset included in ATtILA: {DATASET NAME} ALL - includes all land cover types in the grid with no exclusions. {DATASET NAME} LAND - excludes non-terrestrial land cover types. | String |
| Land\_cover\_classification\_file | The full pathname to the user-defined .xml file for custom or non-standard land cover classification schemes. Pathname is automatically filled when a default scheme is selected. | File |
| Report\_metrics\_for\_these\_classes | A list of the land cover classes and metric combinations for processing. Check the box to calculate metrics for each land cover class and/or combination class desired within the reporting units. | Multiple Value |
| Stream\_features | The vector line and/or polygon dataset(s) that provide the basis for the buffer zones. Land cover metrics are calculated for the area within the buffer zones. | Feature layer |
| Buffer\_distance | The distance around the Stream features which comprises the buffer zones. &nbsp; The value must be an integer. If the distance linear units are not specified or are entered as Unknown, the linear unit of the input features' spatial reference is used. | Linear unit |
| Output\_table | The output reporting unit metrics table to be created. It is recommended that the Output table be saved within a file geodatabase. | Table |
| Processing\_cell\_size (optional) | The Processing cell size for the zonal operation. The default Processing cell size is the cell size of the input raster land cover data.&nbsp; Optionally, the user may select a different cell size. | Analysis cell size |
| Snap\_raster (optional) | The raster that the cell alignment of the Land cover grid and rasterized Reporting unit feature layer will be matched to during processing. The default Snap raster is the Land cover grid. | Raster Layer |
| Select\_options | Three tool options are available to provide additional information: Add Quality Assurance Fields -&nbsp; Adds area fields to the Output table to facilitate quality assurance checking. Add Area Fields for All Land Cover Classes - Adds fields to the Output table that includes the areas of each land cover class and combination class selected. Retain Intermediate Layers Generated During Metric Calculation - Saves the intermediate table and/or raster that is normally deleted after processing is complete. | Multiple Value |


&nbsp;

Credits&nbsp;

&nbsp;

Environments

Current Workspace, Scratch Workspace, Output Coordinates same as input, Processing extent min of inputs,
***
_Created with the Personal Edition of HelpNDoc: [Free Qt Help documentation generator](<https://www.helpndoc.com>)_
