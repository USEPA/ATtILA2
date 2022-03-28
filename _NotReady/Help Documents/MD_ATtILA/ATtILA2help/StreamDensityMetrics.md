# Stream Density Metrics

Summary&nbsp;

Calculates density metrics based on input vector line dataset(s) for each reporting unit polygon and creates an output table. Default metrics include area of the reporting unit (km²), total length (km) and line density (km/km²) within the reporting unit.

In addition to the default metrics, length and density metrics can be calculated by stream order. Stream order is designated based on values in a specified field in the Stream feature layer.

&nbsp;

Usage

* This tool processes all polygons in the **Reporting unit feature** regardless of selections set. The ability to limit land cover calculations to only selected reporting unit polygons is not supported in this release.
- This tool is designed to use a vector line dataset that represent streams, but any vector line dataset may be used. Caution should be exercised when interpreting results, particularly when using line datasets that do not represent streams.
* ***NOTE:** To ensure desired results, the* **Reporting unit feature** *and* **Stream feature** *must be in projected coordinate systems with linear units of measure. *
- The **Reporting unit feature** must be a polygon feature class or shapefile.
* The optional **Stream order field** may be used to create density metrics for different classes of **Stream feature** lines. The **Stream order field** may be any field that differentiates classes of **Stream feature** lines and does not necessarily need to represent stream order.
* Values in the **Stream order field** have restrictions. They may may not contain spaces or special characters such as hyphens, parentheses, brackets, and symbols such as #, $, %, and \&. Essentially, the values in this field are acceptable if they consist only of alphanumeric characters or an underscore. The values in these fields are used to create class-specific metric fields for the two metrics (aliases: STRMKM and STRMDENS) in the **Output table**. If any of the values in the **Stream order field** violate these character restrictions, consider using a different class field or creating a new one that corresponds to the restrictions.
* If a **Stream order field** is specified, the tool creates the new field names by appending the **Stream order field** characters to the metric field names. Since field name length is dependent on the output table type (i.e., dBase, INFO, or geodatabase) care should be used so that the length of the final output field name does not exceed the maximum allowable field name limit for the desired output table. When the limit is exceeded, the **Stream order field** characters may replace the characters at the end of these field names.
  * Example 1: The selected **Stream order field** uses an integer to designate the stream order, and contains only second- and third-order streams (field values "2" or "3"). When the tool is run, four output fields are created in the **Output table** which are named as follows (**Stream order field** characters underlined for emphasis):
    * &#50;: STRMKM2 (7 characters), STRMDENS2 (9 characters)
    * &#51;: STRMKM3 (7 characters), STRMDENS3 (9 characters)
  * Example 2: The selected **Stream order field** uses alphanumeric characters to designate stream feature types (field values "C6" or "F558"). When the tool is run, four output fields are created in the **Output table** which are named as follows (**Stream order field** characters underlined for emphasis):
    * C6: STRMKMC6 (10 characters), STRMDENSC6 (10 characters)
    * F558: STRMKMF558 (10 characters), STRMDEF558 (10 characters) &nbsp; &nbsp;
  * ***NOTE:**&nbsp; If the **Stream order field** characters replace too many of the characters in the metric field names, duplicate field names will be created.*

&nbsp;

* ***NOTE:** Do not use 'ORDER' as the **Stream order field** name as it is considered a reserved keyword in several database management systems, and its use may cause the Stream Density Metrics tool to fail.*
- Final output is written to the location specified in the **Output table** parameter. The **Output table** may be saved as a File Geodatabase Table, a dBASE Table, or an INFO Table.
* &nbsp;
  * ***NOTE:** For most consistent results, It is highly recommended that tool output be saved to a file geodatabase.*
  * When saving as a File Geodatabase Table, no extension is necessary for the **Output table** name. The output location must be a file geodatabase.
  * When saving as a dBASE Table, include the .dbf extension in the **Output table** name. dBASE tables may not be saved in a file geodatabase.
  * When saving as an INFO Table, no extension is necessary for the **Output table** name. INFO tables may not be saved in a file geodatabase. A new directory in the output directory called "info" is automatically created in which the INFO tables are stored. INFO tables have limited portability, so it is recommended that output not be saved as an INFO Table if data sharing is important.
* The user may elect to [Retain Intermediate Layers Generated During Metric Processing](<StreamDensityMetrics1.md>).
  * Choosing to Retain Intermediate Layers saves the intermediate products to one of the following locations:
- &nbsp;
  - &nbsp;
    - When output is saved as a File Geodatabase Table, intermediate products are placed in the same file geodatabase.
    - When ouput is saved as a dBASE Table or an INFO Table, a file geodatabase named "attilaScratchWorkspace" is automatically generated in the same output location specified for the **Output table.** Intermediate products are placed in the attilaScratchWorkspace file geodatabase.
- Field names in the **Output table** follow this naming scheme:
  - For default tool settings (e.g. no optional settings selected):
    - AREAKM2 - The area of the reporting unit in km².
    - STRMKM - The total length of **Stream feature** lines in km within the reporting unit.
    - STRMDENS - The density of **Stream feature** lines in km/km² within the reporting unit.
  - When the option to report metrics by **Stream order field** is selected, separate fields are generated for each metric/class combination. For example, if the **Stream order field** contains five classes of streams, then five STRMDENS metrics will appear in the **Output table**--one for each stream class. Each of these fields appears in the **Output table** by the field aliases listed below. To view the field names with the appended classes rather than the aliases, open the table, select the Table Options dropdown, and uncheck Show Field Aliases:
    - STRMKM - The total length of **Stream feature** lines for each class in the **Stream order field** within the reporting unit.
    - STRMDENS - The density of **Stream feature** lines for each class in the **Stream order field** within the reporting unit.

&nbsp;

Syntax&nbsp;

SDM (Reporting\_unit\_feature, Reporting\_unit\_ID\_field, Stream\_feature, Output\_table, {Stream\_order\_field}, {Select\_options})

| Parameter | Explanation | Data Type |
| --- | --- | --- |
| Reporting\_unit\_feature | The vector polygon dataset that defines the reporting units. | Feature Layer |
| Reporting\_unit\_ID\_field | The field in the Reporting unit feature layer that contains the unique ID for each reporting unit.&nbsp; It may be an integer or a string data type. | Field |
| Stream\_feature | The vector line dataset representing streams. | Feature Layer |
| Output\_table | The output reporting unit metrics table to be created. It is recommended that the Output table be saved either within a file geodatabase, or in a folder as a dBASE file with a .dbf extension. | Table |
| Stream\_order\_field (Optional) | The field in the Stream feature layer that contains the stream order for each feature. It may be an integer or a string data type. The values in this field must not contain spaces or special characters. As order code values are appended to output field names, care should be taken not to exceed the limit for field name size set by output table type. | Field |
| Select\_options (Optional) | One tool option is available to provide additional information: Retain Intermediate Layers Generated During Metric Calculation - Saves the intermediate table and/or raster that is normally deleted after processing is complete. | Multiple Value |


&nbsp;

Credits&nbsp;

&nbsp;

Environments

Current Workspace, Scratch Workspace, Output Coordinates same as input, Processing extent min of inputs,
***
_Created with the Personal Edition of HelpNDoc: [Free Qt Help documentation generator](<https://www.helpndoc.com>)_
