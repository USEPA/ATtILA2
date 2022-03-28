# Land Cover Coefficient Calculator

Summary&nbsp;

Calculates metrics based on coefficient values (multipliers) associated with specific land cover classes within each reporting unit polygon and creates an output table.

Within the reporting unit polygons, the area of each land cover class present is multiplied by its supplied coefficient. The products for each land cover class are summed to produce a value for each coefficient type.

In this version of ATtILA for ArcGIS, this tool produces three metrics: percent impervious area, nitrogen loading (kg/ha/yr), and phosphorus loading (kg/ha/yr).

&nbsp;

Usage

* This tool processes all polygons in the **Reporting unit feature** regardless of selections set. The ability to limit land cover calculations to only selected reporting unit polygons is not supported in this release.
* ***NOTE:** To ensure desired results, the* **Land cover grid** *must be in a projected coordinate system with linear units of measure. *
* Three coefficients for which metrics are calculated are included in this tool: IMPERVIOUS, NITROGEN, and PHOSPHORUS. Coefficient values are stored in the **Land cover classification file**. For more information on how coefficients are coded into the **Land cover classification file**, please refer to the [Coefficients Element](<CoefficientsElement.md>) and [Values Element](<ValuesElement.md>) sections of [ATtILA's LCC XML Document](<ATtILAsLCCXMLDocument.md>). To view specific coefficient values associated with supplied land cover schemes, refer to the particular scheme in [Supplied Land Cover Classification Schemas](<SuppliedLandCoverClassificationS.md>). To view and optionally edit coefficient values in a **Land cover classification file**, use either the [Create or Modify Land Cover Classification](<CreateorModifyLandCoverClassific.md>) tool or a text editor.
  * IMPERVIOUS coefficient - Represents an estimate of the percent impervious area for each land cover class. For example, many land cover classification schemes contain multiple "developed" land cover classes based on the intensity of development. Generally, high-intensity developed areas (e.g. city centers) contain a greater proportion of impervious surfaces per unit area than low-intensity developed areas (e.g. rural residential). Hence, a high-intensity developed land cover class should be assigned a higher coefficient value (perhaps 0.9 for 90% impervious) than that of a medium- or low-intensity developed land cover class (the coefficient values of which perhaps range from 0.7 to 0.25 for 70% to 25% impervious). Generally, percent impervious area in land cover classes other than developed is very low or zero.
  * NITROGEN coefficient - Represents an estimate of the amount of nitrogen output (stream loading) in kilograms per hectare per year for each land cover class. Nitrogen loading is generally found to be highest in land cover classes that are primarily human-use oriented (agricultural and developed land); hence ATtILA for ArcGIS assigns a higher nitrogen loading coefficient value to these classes as compared to natural land cover classes. Considering only the various natural land cover classes, nitrogen loading is generally found to be highest in classes with high vegetative biomass per unit area (forest) and ATtILA for ArcGIS assigns a higher nitrogen loading coefficient value than those of other natural land cover classes with lower biomass per unit area.
  * PHOSPHORUS coefficient - Represents an estimate of the amount of phosphorus output (stream loading) in kilograms per hectare per year for each land cover class. Phosphorus loading follows a similar pattern as nitrogen loading--it is found to be highest in human-use oriented land cover classes to which ATtILA for ArcGIS assigns higher phosphorus loading coefficient values versus natural land cover classes. Again, as with nitrogen loading, within the various natural land cover classes ATtILA for ArcGIS assigns the highest phosphorus loading coefficient values to classes with high vegetative biomass per unit area (forest), with coefficient values decreasing with diminishing biomass per unit area.
* Reporting unit metrics are based on the coefficient values as coded into the **Land cover classification file** for each land cover class. These metrics are calculated in the following manner:&nbsp;
  * IMPERVIOUS - The percent impervious metric uses a percent area method to calculate values. For each land cover class, the area within each reporting unit is multiplied by the impervious coefficient associated with that class, resulting in a product for each class. Products for all land cover classes are summed to produce the percent impervious area metric for each reporting unit.
    * ***NOTE:*** *The percent area method expects coefficient values to be expressed as decimal values between 1 and 0 (e.g., 0.9 for 90%).*
    * ***NOTE:** The output calculated value is supplied as a percentage.*
  * NITROGEN - The nitrogen loading metric uses a per-unit-area method to calculate values. For each land cover class, the area within each reporting unit is converted to hectares then multiplied by the nitrogen coefficient associated with that class, resulting in a product for each class. Products for all land cover classes are summed, then divided by the total number of hectares within the reporting unit to provide an average nitrogen loading value across each reporting unit in kilograms per hectare per year.&nbsp;
  * PHOSPHORUS - The phosphorus loading metric uses a per-unit-area method to calculate values. For each land cover class, the area within each reporting unit is converted to hectares then multiplied by the phosphorus coefficient associated with that class, resulting in a product for each class. Products for all land cover classes are summed, then divided by the total number of hectares within the reporting unit to provide an average phosphorus loading value across each reporting unit in kilograms per hectare per year.
* The **Reporting unit feature** is a zone dataset.&nbsp;
  * A zone is defined as all areas in the input that have the same value. The areas do not have to be contiguous. The term "value" in this definition refers to the unique values in the **Reporting unit ID field**. Therefore, all polygons with the same reporting unit ID are treated as a single zone.&nbsp;
  * When more than one polygon has the same reporting unit ID, the areas for each polygon are combined and metrics are reported as a single record in the **Output table**.
- As the **Reporting unit feature** is a vector dataset, ArcGIS will perform a vector to raster conversion during processing.
* &nbsp;
  * The **Reporting unit feature** must not contain overlapping polygons. When overlapping polygons exist, the vector to raster conversion assigns the value of the top-most polygon to any overlapping area, thereby erasing the areas of underlying zones and resulting in flawed metric calculations.
  * Use the [Identify Overlapping Polygons](<IdentifyOverlappingPolygons.md>) utility to determine if overlapping polygons exist and parse the reporting unit feature layer into two or more feature classes or shapefiles in which no features overlap.
  * To better control the vector to raster conversion, the tool defaults the **Snap raster** and the **Processing cell size** to that of the **Land cover grid**. These may be changed from within the tool.
  * If a disparity exists between the extents of the **Reporting unit feature** and the **Land cover grid**, the user may wish to set the Extent in Environment Settings \> Processing Extent to the smaller of the two to avoid unnecessary processing.
- The **Land cover classification scheme** must correspond to the **Land cover grid**.&nbsp;
  - Schemes for common land cover datasets are included with ATtILA for ArcGIS. Supplied schemes may be designated as either "ALL" or "LAND" (e.g. NLCD 2001 ALL vs. NLCD 2001 LAND). Schemes designated as "ALL" include all land cover classes in reporting unit area calculations, while those designated as "LAND" include only terrestrial land cover classes, with non-terrestrial land cover classes such as water and snow/ice excluded. More information about each of the classification schemes supplied with ATtILA for ArcGIS may be found in [Supplied Land Cover Classification Schemas](<SuppliedLandCoverClassificationS.md>).
* &nbsp;
  * In addition to the common land cover schemes, the tool permits a user-defined land cover classification scheme to be used by specifying a **Land cover classification file** (.xml). Refer to [Land Cover Classification](<LandCoverClassification.md>) for more information.
  * ***NOTE:** When a classification scheme with excluded land cover classes is selected, the areas of the excluded classes are disregarded in metric calculations. For example, when selecting a "LAND" classification scheme, the tool will process individual land cover classes and calculate metrics based on the total terrestrial area they occupy within the reporting unit, rather than the percent of the total area within the reporting unit. *
* Final output is written to the location specified in the **Output table** parameter. The **Output table** may be saved as a File Geodatabase Table, a dBASE Table, or an INFO Table.
- &nbsp;
  - ***NOTE:** For most consistent results, it is highly recommended that tool output be saved to a file geodatabase.*
  - When saving as a File Geodatabase Table, no extension is necessary for the **Output table** name. The output location must be a file geodatabase.
  - When saving as a dBASE Table, include the .dbf extension in the **Output table** name. dBASE tables may not be saved in a file geodatabase.
  - When saving as an INFO Table, no extension is necessary for the **Output table** name. INFO tables may not be saved in a file geodatabase. A new directory in the output directory called "info" is automatically created in which the INFO tables are stored. INFO tables have limited portability, so it is recommended that output not be saved as an INFO Table if data sharing is important. &nbsp;
* The user may elect to [Add Quality Assurance Fields](<LandCoverCoefficientCalculator2.md>), and/or [Retain Intermediate Layers Generated During Metric Processing](<LandCoverCoefficientCalculator1.md>).
- &nbsp;
  - Choosing to Retain Intermediate Layers saves the intermediate products to one of the following locations:
* &nbsp;
  * &nbsp;
    * When output is saved as a File Geodatabase Table, intermediate products are placed in the same file geodatabase.
    * When ouput is saved as a dBASE Table or an INFO Table, a file geodatabase named "attilaScratchWorkspace" is automatically generated in the same output location specified for the **Output table.** Intermediate products are placed in the attilaScratchWorkspace file geodatabase.
* Field names in the **Output table** are as follows:
  * PCTIA - The percent impervious area metric for the reporting unit.
  * N\_Load - The average annual nitrogen load per hectare for the reporting unit (kg/ha/yr).
  * P\_Load - The average annual phosphorus load per hectare for the reporting unit (kg/ha/yr).
  * ***NOTE:** Field names are obtained from the fieldName attribute in each coefficient element in the specified **Land cover classification file** (See the [Coefficients Element*](<CoefficientsElement.md>) *in [ATtILA's LCC XML Document*](<ATtILAsLCCXMLDocument.md>)*). Output field names can be changed by [editing*](<CreateorModifyLandCoverClassific.md>) *the **Land cover classification file**.*

&nbsp;

Syntax&nbsp;

LCCC (Reporting\_unit\_feature, Reporting\_unit\_ID\_field, Land\_cover\_grid, Land\_cover\_classification\_scheme, Land\_cover\_classification\_file, Report\_metrics\_for\_these\_coefficients, Output\_table, {Processing\_cell\_size}, {Snap\_raster}, Select\_options)&nbsp;

| Parameter | Explanation | Data Type |
| --- | --- | --- |
| Reporting\_unit\_feature | The vector polygon dataset that defines the reporting units. | Feature Layer |
| Reporting\_unit\_ID\_field | The field in the Reporting unit feature layer that contains the unique ID for each reporting unit.&nbsp; It may be an integer or a string data type. | Field |
| Land\_cover\_grid | The raster dataset representing land cover classes to be summarized within each Reporting unit feature. The grid input must be an integer raster layer. | Raster Layer |
| Land\_cover\_classification\_scheme | The land cover classification schemes included in ATtILA and a User Defined option. The default schemes correspond to common input land cover datasets. Two schemes are supplied for each dataset included in ATtILA: {DATASET NAME} ALL - includes all land cover types in the grid with no exclusions. {DATASET NAME} LAND - excludes non-terrestrial land cover types. | String |
| Land\_cover\_classification\_file | The full pathname to the user-defined .xml file for custom or non-standard land cover classification schemes. Pathname is automatically filled when a default scheme is selected. | File |
| Report\_metrics\_for\_these\_coefficients | A list of the coefficents available for processing. Check the box to calculate metrics for each coefficient desired within the reporting units. | String |
| Output\_table | The output reporting unit metrics table to be created. It is recommended that the Output table be saved within a file geodatabase. | Table |
| Processing\_cell\_size (optional) | The Processing cell size for the zonal operation. The default Processing cell size is the cell size of the input raster land cover data.&nbsp; Optionally, the user may select a different cell size. | Analysis cell size |
| Snap\_raster (optional) | The raster that the cell alignment of the Land cover grid and rasterized Reporting unit feature layer will be matched to during processing. The default Snap raster is the Land cover grid. | Raster Layer |
| Select\_options | Two tool options are available to provide additional information: Add Quality Assurance Fields -&nbsp; Adds area fields to the Output table to facilitate quality assurance checking. Retain Intermediate Layers Generated During Metric Calculation - Saves the intermediate table and/or raster that is normally deleted after processing is complete. | Multiple Value |


&nbsp;

Environments

Current Workspace, Scratch Workspace, Output Coordinates same as input, Processing extent min of inputs,
***
_Created with the Personal Edition of HelpNDoc: [Free CHM Help documentation generator](<https://www.helpndoc.com>)_
