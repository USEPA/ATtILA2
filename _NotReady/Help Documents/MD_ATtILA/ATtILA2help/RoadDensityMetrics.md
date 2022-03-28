# Road Density Metrics

Summary&nbsp;

Calculates metrics based on input vector line dataset(s) for each reporting unit polygon and creates an output table.&nbsp;

Default metrics include total length (km) and line density (km/km²) by reporting unit. Also included in the default metrics is percent impervious surface within each reporting unit, the calculation of which assumes that the input vector line dataset represents roads.&nbsp;

In addition to the default metrics, the tool allows for several optional metrics to be calculated:

* Length and density metrics by Road feature class within each reporting unit. Classes are designated based on values in a specified field in the Road feature layer.
* Metrics that involve spatial relationships between the Road feature and a second linear feature (Stream feature). The user may select to calculate the following:
  * Metrics that measure the frequency of intersections between the Road feature lines and the Stream feature lines in each reporting unit. Measurements by Road feature class are also available.
  * Metrics that measure the length of the Road feature lines within a specified buffer distance from Stream feature lines within each reporting unit. Measurements by Road feature class are also available.
  * Both.

&nbsp;

Usage

* This tool processes all polygons in the **Reporting unit feature** regardless of selections set. The ability to limit land cover calculations to only selected reporting unit polygons is not supported in this release.
- This tool is designed to use vector line datasets that represent roads and streams, but any vector line dataset may be used. Caution should be exercised when interpreting results, particularly when using line datasets that do not represent roads and/or streams.
* ***NOTE:** To ensure desired results, the* **Reporting unit feature**#8202;*,* **Road feature**#8202;*, and* **Stream feature** *must be in projected coordinate systems with linear units of measure. *
* The **Reporting unit feature** must be a polygon feature class or shapefile.
- The optional **Road class field** may be used to create metrics for different classes of **Road feature** lines. The **Road class field** may be any field that differentiates category of **Road feature** lines and does not necessarily need to represent road class.
- Values in the optional **Road class field** have restrictions. They may not contain spaces or special characters such as hyphens, parentheses, brackets, and symbols such as #, $, %, and \&. Essentially, the values in this field are acceptable if they consist only of alphanumeric characters or an underscore. The values in these fields are used to create class-specific metric fields for the three metrics (RDKM, RDDENS, and RDTIA) in the **Output table**. If any of the values in the **Road class field** violate these character restrictions, consider using a different class field or creating a new one that corresponds to the restrictions.&nbsp;
- If a **Road class field** is specified, the tool creates the new field names by appending the **Road class field** characters to the metric field names. Since field name length is dependent on the output table type (i.e., dBase, INFO, or geodatabase) care should be used so that the length of the final output field name does not exceed the maximum allowable field name limit for the desired output table. When the limit is exceeded, the **Road class field** characters may replace the characters at the end of these field names.
  - Example: Two road classes exist in the **Road feature** and a dBASE output table type is specified (maximum field length = 10 characters). The **Road class field** designates these as "A31" and "B45100". When the tool is run with default settings (e.g. no options are selected), six output fields are created in the **Output table**, which are named as follows (class characters underlined for emphasis):
    - A31: RDKMA31 (7 characters), RDDENSA31 (9 characters), RDTIAA31 (8 characters)
    - B45100: RDKMB45100 (10 characters), RDDEB45100 (10 characters), RDTIB45100 (10 characters)
  - ***NOTE:**&nbsp; If the **Road class field** characters replace too many of the characters in the metric field names, duplicate field names will be created.*
- When the optional **STXRD** (stream-road crossing) and/or **RNS** (roads near streams) are checked, the tool allows the user to select a **Stream feature**. When **RNS** is checked, the user is also allowed to enter a **Buffer distance** from the **Stream feature** lines.
- Final output is written to the location specified in the **Output table** parameter. The **Output table** may be saved as a File Geodatabase Table, a dBASE Table, or an INFO Table.
* &nbsp;
  * ***NOTE:** For most consistent results, it is highly recommended that tool output be saved to a file geodatabase.*
  * When saving as a File Geodatabase Table, no extension is necessary for the **Output table** name. The output location must be a file geodatabase.
  * When saving as a dBASE Table, include the .dbf extension in the **Output table** name. dBASE tables may not be saved in a file geodatabase.
  * When saving as an INFO Table, no extension is necessary for the **Output table** name. INFO tables may not be saved in a file geodatabase. A new directory in the output directory called "info" is automatically created in which the INFO tables are stored. INFO tables have limited portability, so it is recommended that output not be saved as an INFO Table if data sharing is important.
* The user may elect to [Retain Intermediate Layers Generated During Metric Processing](<RoadDensityMetrics1.md>).
  * Choosing to Retain Intermediate Layers saves the intermediate products to one of the following locations:
- &nbsp;
  - &nbsp;
    - When output is saved as a File Geodatabase Table, intermediate products are placed in the same file geodatabase.
    - When ouput is saved as a dBASE Table or an INFO Table, a file geodatabase named "attilaScratchWorkspace" is automatically generated in the same output location specified for the **Output table.** Intermediate products are placed in the attilaScratchWorkspace file geodatabase.
- Field names in the **Output table** follow this naming scheme:
  - For default tool settings (e.g. no optional settings selected):
    - AREAKM2 - The area of the reporting unit in km².
    - RDKM - The total length of **Road feature** lines in km within the reporting unit.
    - RDDENS - The density of **Road feature** lines in km/km² within the reporting unit.
    - RDTIA - An estimate of percent impervious area within the reporting unit. This metric uses road density as the independent variable in a linear regression model to estimate percent impervious surface (see May, et al., 1997). Due to the nature of the regression equation used, values below 1.8 km/km² are assigned a value of 0 for the percent impervious metric, while values above 11 km/km² are considered invalid and are reported as −1.
  - When the **STXRD** option is selected:
    - STRMKM - The total length of **Stream feature** lines in km within the reporting unit.
    - STRMDENS - The density of **Stream feature** lines in km/km² within the reporting unit.
    - XCNT (Alias FREQUENCY) - The count of intersections (crossings) between the **Road feature** lines and the **Stream feature** lines within the reporting unit.
    - STXRD - The density of stream-road crossings per stream km within the reporting unit.
  - When the **RNS** option is selected:
    - RNS\[buffer distance\] - The proportion of the total length of **Road feature** lines within the **Buffer distance** to the total length of **Stream feature** lines by reporting unit.
  - When the option to report metrics by **Road class field** is selected, separate fields are generated for each metric/class combination. For example, if the **Road class field** contains five classes of roads, then five RDDENS metrics will appear in the **Output table**--one for each road class. Each of these fields appears in the **Output table** by the field aliases listed below. To view the field names with the appended classes rather than the aliases, open the table, select the Table Options dropdown, and uncheck Show Field Aliases:
    - RDKM - The total length of **Road feature** lines for each class in the **Road class field** within the reporting unit.
    - RDDENS - The density of **Road feature** lines for each class in the **Road class field** within the reporting unit.
    - RDTIA - An estimate of the percent impervious area within the reporting unit contributed by each class.
    - FREQUENCY - The count of intersections (crossings) between the **Road feature** lines and the **Stream feature** lines for each class within the reporting unit.
    - STXRD - The density of stream-road crossings for each class per stream km within the reporting unit.
    - RNS\[buffer distance\] - The proportion of the total length of **Road feature** lines within the **Buffer distance** to the total length of **Stream feature** lines in the reporting unit for each class.

&nbsp;

Syntax&nbsp;

RDM (Reporting\_unit\_feature, Reporting\_unit\_ID\_field, Road\_feature, Output\_table, {Road\_class\_field}, {STXRD}, {RNS}, Stream\_feature, Buffer\_distance, {Select\_options})&nbsp;

| Parameter | Explanation | Data Type |
| --- | --- | --- |
| Reporting\_unit\_feature | The vector polygon dataset that defines the reporting units. | Feature Layer |
| Reporting\_unit\_ID\_field | The field in the Reporting unit feature layer that contains the unique ID for each reporting unit.&nbsp; It may be an integer or a string data type. | Field |
| Road\_feature | The vector line dataset representing roads or other linear features to be measured. | Feature Layer |
| Output\_table | The output reporting unit metrics table to be created. It is recommended that the Output table be saved within a file geodatabase. | Table |
| Road\_class\_field (optional) | The field in the Road feature layer that distinguishes classes of linear features in order to calculate separate metrics for each class. It may be an integer or a string data type. The values in this field must not contain spaces or special characters. As class code values are appended to output field names, care should be taken not to exceed the limit for field name size set by output table type. | Field |
| STXRD (optional) | Specifies whether stream-road crossing (STXRD) metrics will be included in the output table. false - No STXRD metrics will not be included. This is the default. true - STXRD metrics will be included. These include the total number of stream-road crossings (field name: FREQUENCY) and the density of stream-road crossings per stream kilometer (field name: STXRD) in the reporting unit. | Boolean |
| RNS (optional) | Specifies whether the roads near streams (RNS) metric will be included in the output table. false - RNS metric will not be included. This is the default. true - RNS metric will be included. This metric is a measurement of the total length of roads within the buffer distance divided by the total length of stream in the reporting unit.&nbsp; | Boolean |
| Stream\_feature | The vector line dataset representing streams that is used to calculate the STXRD and/or RNS metrics. This dataset is required when the STXRD and/or RNS options are checked. | Feature Layer |
| Buffer\_distance | The distance around the Stream features in which buffer zones are created.&nbsp; The value must be an integer. If the distance linear units are not specified or are entered as Unknown, the linear unit of the input features' spatial reference is used. This parameter is required when the RNS option is checked. | Linear unit |
| Select\_options (optional) | One tool option is available to provide additional information: Retain Intermediate Layers Generated During Metric Calculation - Saves the intermediate table and/or raster that is normally deleted after processing is complete. | Multiple Value |


&nbsp;

Credits&nbsp;

May, C.W., Horner, R.R., Karr, J.R., Mar B.W., Welch, E.B. 1997. *Effects of urbanization on small streams in the Puget Sound Lowland Ecoregion*. Watershed Protection Techniques. 2:4. pp. 483−493.&nbsp;

&nbsp;

Environments

Current Workspace, Scratch Workspace, Output Coordinates same as input, Processing extent min of inputs

***
_Created with the Personal Edition of HelpNDoc: [Write eBooks for the Kindle](<https://www.helpndoc.com/feature-tour/create-ebooks-for-amazon-kindle>)_
