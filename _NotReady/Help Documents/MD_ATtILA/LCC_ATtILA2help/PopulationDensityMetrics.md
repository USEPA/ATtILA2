# Population Density Metrics

Summary&nbsp;

Calculates population count and density (people per km²) for each reporting unit polygon and creates an output table.&nbsp;

In addition to the default metrics, the tool optionally calculates population change over time.

&nbsp;

Usage

* This tool processes all polygons in the **Reporting unit feature** regardless of selections set. The ability to limit land cover calculations to only selected reporting unit polygons is not supported in this release.
* ***NOTE:** To ensure desired results, the* **Reporting unit feature**#8202;*,* **Census feature**#8202;*, and* **Census T2 feature** *must be in projected coordinate systems with linear units of measure. *
* The **Reporting unit feature** must be a polygon feature class or shapefile.
* This tool assumes that population is distributed evenly throughout each **Census feature** polygon. The tool apportions population by area weighting. For example, if 50% of a **Census feature** polygon is within a reporting unit, the tool will assign 50% of the value in the polygon's **Population field** to that reporting unit. Caution should be exercised when **Census feature** polygons do not have even population distributions as this could result in an overweighting or underweighting of population when the tool performs the apportionment. Generally, greater accuracy will be achieved if the **Census feature** polygons are smaller than the smallest **Reporting unit feature** polygons.
- When the optional **POPCHG** (population change) is checked, the tool allows the user to select a **Census T2 feature** and a corresponding **Population T2 field**.&nbsp;
  - For best results, the **Census T2 feature** should contain polygons at a similar scale to that of the **Census feature** (e.g. if **Census feature** represents census block groups, then **Census T2 feature** should also represent census block groups rather than census tracts or some other census geography).
  - **Census T2 feature** may be the same feature layer as used for **Census feature**.
- Final output is written to the location specified in the **Output table** parameter. The **Output table** may be saved as a File Geodatabase Table, a dBASE Table, or an INFO Table.
* &nbsp;
  * ***NOTE:** For most consistent results, it is highly recommended that tool output be saved to a file geodatabase.*
  * When saving as a File Geodatabase Table, no extension is necessary for the **Output table** name. The output location must be a file geodatabase.
  * When saving as a dBASE Table, include the .dbf extension in the **Output table** name. dBASE tables may not be saved in a file geodatabase.
  * When saving as an INFO Table, no extension is necessary for the **Output table** name. INFO tables may not be saved in a file geodatabase. A new directory in the output directory called "info" is automatically created in which the INFO tables are stored. INFO tables have limited portability, so it is recommended that output not be saved as an INFO Table if data sharing is important.
* The user may elect to [Retain Intermediate Layers Generated During Metric Processing](<PopulationDensityMetrics1.md>).
  * Choosing to Retain Intermediate Layers saves the intermediate products to one of the following locations:
- &nbsp;
  - &nbsp;
    - When output is saved as a File Geodatabase Table, intermediate products are placed in the same file geodatabase.
    - When ouput is saved as a dBASE Table or an INFO Table, a file geodatabase named "attilaScratchWorkspace" is automatically generated in the same output location specified for the **Output table.** Intermediate products are placed in the attilaScratchWorkspace file geodatabase.
- Field names in the **Output table** follow this naming scheme:
  - For default tool settings (e.g. no optional settings selected):
    - AREAKM2 - The area of the reporting unit in km².
    - popCount (ALIAS: SUM\_intPop) - The estimated total population within the reporting unit derived by area weighting the population values within each **Census feature** polygon that intersects with the reporting unit and summing the area-weighted values.
    - POPDENS - The estimated population density in persons per km² within the reporting unit derived by dividing popCount by AREAKM2.
  - When the **POPCHG** option is selected:
    - popCount\_1 (ALIAS: SUM\_intPop) - The estimated total population within the reporting unit derived by area weighting the population values within each **Census feature** polygon (Time 1) that intersects with the reporting unit and summing the area-weighted values.
    - POPDENS\_1 - The estimated population density in persons per km² within the reporting unit derived by dividing popCount\_1 by AREAKM2.
    - popCount\_2 (ALIAS: SUM\_intPop) - The estimated total population within the reporting unit derived by area weighting the population values within each **Census T2 feature** polygon (Time 2) that intersects with the reporting unit and summing the area-weighted values.
    - POPDENS\_2 - The estimated population density in persons per km² within the reporting unit derived by dividing popCount\_2 by AREAKM2.
    - POPCHG - The estimate percent change in population from Time 1 to Time 2.

&nbsp;

Syntax&nbsp;

PDM (Reporting\_unit\_feature, Reporting\_unit\_ID\_field, Census\_feature, Population\_field, Output\_table, POPCHG, Census\_T2\_feature, Population\_T2\_field, Select\_options)&nbsp;

| Parameter | Explanation | Data Type |
| --- | --- | --- |
| Reporting\_unit\_feature | The vector polygon dataset that defines the reporting units. | Feature Layer |
| Reporting\_unit\_ID\_field | The field in the Reporting unit feature layer that contains the unique ID for each reporting unit.&nbsp; It may be an integer or a string data type. | Field |
| Census\_feature | The vector polygon dataset that contains population data. | Feature Layer |
| Population\_field | The field in the Census feature layer that contains population data. | Field |
| Output\_table | The output reporting unit metrics table to be created. It is recommended that the Output table be saved within a file geodatabase. | Table |
| POPCHG (optional) | Specifies whether population change over time (POPCHG) metrics will be included in the output table. false - No POPCHG metrics will not be included. This is the default. true - POPCHG metrics will be included. | Boolean |
| Census\_T2\_feature | The optional vector polygon dataset (Census time 2) that contains population data for the comparison date. It may be the same feature layer as Census feature. | Feature Layer |
| Population\_T2\_field | The field in the Census feature layer that contains population data for the comparison date. | Field |
| Select\_options | One tool option is available to provide additional information: Retain Intermediate Layers Generated During Metric Calculation - Saves the intermediate table and/or raster that is normally deleted after processing is complete. | Multiple Value |


&nbsp;

Environments

Current Workspace, Scratch Workspace, Output Coordinates same as input, Processing extent min of inputs,
***
_Created with the Personal Edition of HelpNDoc: [Produce online help for Qt applications](<https://www.helpndoc.com/feature-tour/create-help-files-for-the-qt-help-framework>)_
