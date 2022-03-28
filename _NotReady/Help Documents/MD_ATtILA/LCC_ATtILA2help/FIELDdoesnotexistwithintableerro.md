# {FIELD} does not exist within table error

When running the Road Density Metrics or the Stream Density Metrics tool, an error may occur indicating that a field does not exists:

&nbsp;

![Image](<lib/trouble\_ORDER%20Field%20Not%20Found.png>)

&nbsp;

This error may be caused by problems with the field used to classify the different road or stream features (Road class field or Stream order field, respectively).

&nbsp;

If an input feature layer contains a reserved keyword such as ORDER as a field name, that field name is altered slightly by ArcGIS when the input feature layer is copied. ATtILA for ArcGIS copies several of the input feature layers while processing selected metrics. This can result in ATtILA for ArcGIS being unable to located the specified field in the copied dataset. For more guidelines on the naming of fields, search on "Fundamentals of adding and deleting fields" in the ArcGIS help documentation.

***
_Created with the Personal Edition of HelpNDoc: [Produce electronic books easily](<https://www.helpndoc.com/create-epub-ebooks>)_
