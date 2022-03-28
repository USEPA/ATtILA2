# Riparian Characteristics

Riparian zones, i.e., the areas adjacent to streams and associated waterbodies, provide critical habitat areas and play an important role in determining or preserving surface water quality.&nbsp; While all of the land area within a watershed may contribute pollutants via runoff, the effect of more distant (from stream) areas may be mitigated along the transport path. However, there is little or no mitigation of nutrient or soil runoff from stream side areas.&nbsp; Thus these buffer areas along streams may have a greater impact upon water quality.&nbsp; Conversely, conservation of riparian buffers may help to preserve good water quality.

&nbsp;

The Riparian Characteristics toolset consists of three metrics. Two of the metrics in this toolset are directly related to riparian characteristics:

* &nbsp;
  * [**Riparian Land Cover Proportions**](<RiparianLandCoverProportions.md>) is similar to the Land Cover Proportions metric in the Landscape Characteristics toolset except that the results are calculated only for the buffer area around streams instead of over the whole reporting unit.&nbsp; Required inputs include a polygon reporting unit feature, a land cover grid, and one or more vector/polygon stream features.&nbsp; The width of the buffer is defined by the user; typical values include a distance equal to the land cover grid cell size (or a multiple thereof) or a value from a legal definition of riparian zone.&nbsp; A land cover classification scheme is also required; several popular classification schemes are supplied (see section Supplied Land Cover Classification Schemes) or, optionally, the user may define a custom classification scheme.
  * [**Stream Density Metrics**](<StreamDensityMetrics.md>) produces an output table, calculated as total stream length divided by total reporting unit area, with an option to calculate density separately by stream order.&nbsp; Required inputs are a polygon reporting unit feature and a vector stream feature.

&nbsp;

The third metric contained in this toolset is not designed exclusively for riparian characteristics, but is included here as it uses the buffer concept employed in the Riparian Land Cover Proportions metric:

* &nbsp;
  * [**Sample Point Land Cover Proportions**](<SamplePointLandCoverProportions.md>) produces an output table of the land cover proportions within a user-specified distance around a point or set of points.&nbsp; Required inputs include a polygon reporting unit feature, a land cover grid, and feature containing the point(s) of interest.&nbsp; Other required inputs include a buffer distance and a land cover classification scheme, as described above. One use of this metric is to determine the land cover proportions within the immediate area surrounding a sampling point.&nbsp; For example, using this metric on a set of water quality sampling station locations and a reporting unit consisting of the catchment areas to those sampling points will provide an output of land cover proportions within an upslope "wedge" of the sampling points; the downslope remainder of the buffer circle is eliminated because it falls outside the reporting unit.

***
_Created with the Personal Edition of HelpNDoc: [Easy CHM and documentation editor](<https://www.helpndoc.com>)_
