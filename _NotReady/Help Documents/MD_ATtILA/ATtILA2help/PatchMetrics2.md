# Patch Metrics

Fields Added

* **PM\_OVER** - The percent overlap between the Reporting unit feature layer and the Land cover grid for each reporting unit.
* **PM\_TOTA** - The total raster zonal area for each reporting unit (zone) after the Reporting unit feature layer has been rasterized.&nbsp;
* **PM\_EFFA** - The effective raster area of each reporting unit (zone) after excluded classes have been removed.&nbsp;
* **PM\_EXCA** - The raster area of the excluded classes within each reporting unit (zone) based on exclusions in the Land cover classification scheme.
* **\[class\]\_PWN**&nbsp; - The number of patches of the selected class **with** a neighboring patch within the reporting unit (e.g. "for\_PWN" is the number of patches of the "Forest" class in the NLCD **with** at least one neighboring patch).
  * ***NOTE:** This value should equal the number of patches recorded in the \[class\]\_NUM field except for reporting units where the number of patches = 1 or 0.* Reporting units with only one patch will have a zero value recorded in this field. Those with no patches will have a value of -9999.
* **\[class\]\_PWON** - The number of patches of the selected class **without** a neighboring patch within the reporting unit (e.g. "for\_PWON" is the number of patches of the "Forest" class in the NLCD **without** a neighboring patch).
  * ***NOTE:** This value should be 0 for all reporting units with two or more patches recorded in the \[class\]\_NUM field,1 where only a single patch is reported, and -9999 for reporting units with no patches.*

***
_Created with the Personal Edition of HelpNDoc: [Easy EPub and documentation editor](<https://www.helpndoc.com>)_
