# Values Window

**Values Window**

The Values Window consists of three buttons and a table:

&nbsp;

1. &nbsp;
   1. Add Value - Enter new values into the table
   1. Remove Value - Remove values from the table
   1. Remove Exclusion - Remove all exclusions set

&nbsp;

![Image](<lib/LCC%20Editor%20Values%20Window%20Numbered.png>)

&nbsp;

&nbsp;

**Add Value**

Values are entered into the Values Table by pressing the Add Value button. Here, the user may then enter the following:

&nbsp;

* &nbsp;
  * Value (required) - The integer value of the land cover class in the Land cover grid.
  * Description (required) - A text description of the land cover value.
  * X - A checkbox that determines whether the land cover value will be excluded from ATtILA for ArcGIS metric calculations. This is frequently checked when the user elects to exclude open water and perennial snow/ice values out of calculations, but may be used on any value.
  * IMPERVIOUS - Numerical coefficient that estimates the percent of impervious surfaces that is generally found within the land cover type. This coefficient is frequently used with developed land cover types. ***NOTE:** The coefficient should be entered as a decimal value rather than a percentage. *
  * NITROGEN - Numerical coefficient that estimates the amount of nitrogen output (stream loading) in kilograms per hectare per year that is generally found within the land cover type. This coefficient is frequently used with developed and agricultural land cover types.
  * PHOSPHORUS - Numerical coefficient that estimates the amount of phosphorus output (stream loading) in kilograms per hectare per year that is generally found within the land cover type. This coefficient is frequently used with developed and agricultural land cover types.

&nbsp;

The Add Row button may be clicked to add one or more additional values, if needed. Once the desired number of values have been added, they should be reviewed for accuracy. Edits may be made directly in the fields, or entire values may be deleted by clicking on the value to be deleted, then clicking the Remove Selected Row button. Once satisfied with the entries, click the OK button to add the new values to the Values table.

&nbsp;

***NOTE:** Once in the Values table, the Value cannot be modified. However, the Description, eXclusion or Coefficients may be modified from the table.*

&nbsp;

&nbsp; &nbsp; ![Image](<lib/LCC%20Editor%20Add%20Value%20Dialog.png>)

&nbsp;

&nbsp;

**Remove Value**

To delete a single value from the Values table, click on the value to be deleted in the table, then click the Remove Value button. To remove multiple values, click the Remove Value button *without* selecting a value. The Remove Value dialog will appear. Select multiple values by holding the Shift key while selecting the values with the mouse, and then click OK to delete.

&nbsp;&nbsp; &nbsp;

![Image](<lib/LCC%20Editor%20Remove%20Value%20Dialog.png>)

&nbsp;

**Deselect Exclusion**

To remove all exclusions set on the values in the Values table, click the Deselect Exclusions button. To reset exclusions, simply click the X checkbox for each value to be excluded.


***
_Created with the Personal Edition of HelpNDoc: [Write EPub books for the iPad](<https://www.helpndoc.com/create-epub-ebooks>)_
