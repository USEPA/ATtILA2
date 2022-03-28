# Failed to execute (Intersect)

This error been detected when executing the [Riparian Land Cover Proportions](<RiparianLandCoverProportions.md>) tool. Please report any additional instances of this error to: [LEBProjects@epa.gov](<mailto:LEBProjects@epa.gov?subject=ATtILA>) and include “ATtILA” in the subject line.

&nbsp;

&nbsp; &nbsp; ![Image](<lib/NewItem5.png>)

&nbsp;

This problem appears to occur when the input reporting unit feature consists of a large number of reporting units and/or covers a large geographic area. When the ArcGIS software tries to tile the data to process the dataset, the tiling process appears to fails, usually during the reassembly stage. This is an inconsistent error. Sometimes when the metric run is reattempted, using the exact same inputs, the metric run will finish.&nbsp;

&nbsp;

If the metric run fails a second or third time, we recommend using the selection tool and selecting approximately half of the input reporting unit features, exporting the selected reporting units into a new dataset, and reattempting the metric run with the new dataset as the input reporting unit theme. &nbsp;

&nbsp;

Continue the reduction process until the metric run runs to completion or until a single reporting unit remains.

&nbsp;

If the metric run fails with only one reporting unit feature as the input reporting unit theme, it is likely that there is an error in one of the other input datasets within the confines of the recalcitrant reporting unit. Close inspection of the other input datasets in this area may reveal the problem (e.g. poor digitization of input data as in nodes not being used at line intersections).


***
_Created with the Personal Edition of HelpNDoc: [Free EPub and documentation generator](<https://www.helpndoc.com>)_
