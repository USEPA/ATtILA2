# Failed to execute (TabulateArea)

When running a tool that uses a Land cover grid (Land Cover Coefficient Calculator, Core and Edge Metrics, Land Cover Diversity, Land Cover on Slope Proportions, Land Cover Proportions, Riparian Land Cover Proportions, and Sample Point Land Cover Proportions), an error may occur indicating that TabulateArea failed to execute:

&nbsp;

![Image](<lib/ATtILA%20Failed%20to%20execute%20TabulateArea.png>)

&nbsp;

The issue is that raster geoprocessing tools convert other formats to GRID format internally, then perform the analysis, then re-convert the GRID back out to the desired format.&nbsp; The limit is reached at the conversion to the GRID format; GRID's have an upper limit of 2.1 billion cells in their INFO table.&nbsp; The only workaround for this is breaking your data down into smaller chunks before running the tabulate area tool or by selecting a larger processing cell size.&nbsp; The larger processing cell size may allow the process to finish, but the output results will be of a more generalized nature.

***
_Created with the Personal Edition of HelpNDoc: [Easily create PDF Help documents](<https://www.helpndoc.com/feature-tour>)_
