# Land Cover on Slope Proportions

Intermediate Files Retained

* **lcosp\_\[Land cover grid name\]\* raster** - A land cover raster that is the result of checking the "Reduce land cover grid to smallest recommended size" optional checkbox in the tool dialog. This raster is created by limiting the Land cover grid to the extent of the Reporting unit feature layer. The name of the intermediate raster has the prefix "lcosp\_" followed by the name of the Land cover grid, then appended with a number (e.g. lcosp\_NLCD060, lcosp\_FLAGAP0, lcosp\_CCAP1, etc.). The number at the end of the intermediate raster name is added when the raster is saved in order to give each successive raster a unique name when the tool is executed more than once and the results are saved to the same output location.
* **lcosp\_RasterSL\[slope threshold\]\* raster** - A land cover raster resulting from the overlay between all Land cover grid cells and Slope grid cells that do not meet the Slope threshold. Land cover cells in overlay areas are reclassed with a new value that is outside of the range of valid class values as recognized by the Land cover classification file. The processes involved in creating this raster are as follows:
1) &nbsp;
   1) Examine the values in both the Land cover grid and the Land cover classification file to determine which has the highest high value.
   1) Calculate a new value by adding one (1) to the higher of the two high values. For example, if the high value in the input grid is 95 and the high value in the classification file is 99, the calculated value for cells meeting the Slope threshold is (99+1) = 100 in the new intermediate raster.
   1) Create a new raster that assigns this new value to all cells that are below the slope threshold. Retain all other land cover cell values.
   1) Name the intermediate raster "lcosp\_RasterSL\[slope threshold\]\*" where "\[slope threshold\]" is the input slope threshold and " \* " is a sequential number added when the raster is saved in order to give each successive raster a unique name when the tool is executed more than once and results saved to the same output location (e.g. lcospRaster0SL7, lcospRaster1SL7, lcospRaster0SL9, etc.).

The purpose of this intermediate raster product in the Land Cover on Slope Proportions tool is to exclude land cover cells that do not meet the threshold slope from metric calculations. The tool uses this raster to calculate the proportion of each reporting unit that is covered by each valid land cover type on slopes that meet or exceed the threshold slope.

* **lcospTabArea\* table** - A table of areas corresponding to the values in the intermediate raster within each reporting unit. Areas with reclassed values that do not meet the Slope threshold are included. The name of the intermediate table has the prefix "lcospTabArea" followed by a number (e.g. lcospTabArea0, lcospTabArea1, lcospTabArea2, etc.). As with the intermediate raster, the number at the end of the intermediate table name is added when saving to create a unique name.

***
_Created with the Personal Edition of HelpNDoc: [Full-featured Kindle eBooks generator](<https://www.helpndoc.com/feature-tour/create-ebooks-for-amazon-kindle>)_
