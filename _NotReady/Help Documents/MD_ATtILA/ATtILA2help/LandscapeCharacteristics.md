# Landscape Characteristics

Natural land cover and anthropogenic land use have a profound effect on landscapes and environmental stressors.&nbsp; For example, cutting down forests reduces uptakes of nitrogen and other nutrients, disrupts habitats for various fauna, and exposes soils to increased runoff.&nbsp; Erosion may be further accelerated if the exposed area is on a slope.&nbsp; The proportions of various land cover/use types within a watershed can provide information about the expected condition of surface waters and aquatic habitats within that watershed.

&nbsp;

The Landscape Characteristics toolset consists of five metric tools:

* &nbsp;
  * [**Core and Edge Metrics**](<CoreandEdgeMetrics.md>) requires a reporting unit polygon layer and a land cover raster with an accompanying land cover classification scheme. Core and edge area metrics are commonly generated for forest cover (providing an indication of forest health) and for habitat suitability studies, but may be calculated for any land cover class or group of classes.&nbsp;
  * [**Land Cover Diversity**](<LandCoverDiversity.md>) requires a reporting unit polygon layer and a land cover raster. Diversity is an indicator of landscape composition and fragmentation. These indicators are influenced by two components − richness (number of different patch types present) and evenness (distribution of area among patch types). There are four diversity metrics available. H and H' are Shannon−Weiner diversity and Standardized Shannon−Weiner diversity, respectively, C is the Simpson index and S is simple diversity. More information on these, including the algorithms, is provided in the tool-specific section of this manual.
  * [**Land Cover on Slope Proportions**](<LandCoveronSlopeProportions.md>) requires a reporting unit polygon layer, a land cover raster with an accompanying land cover classification scheme, and a slope raster. This tool produces a table of the percent of specified land cover types on slopes within each reporting unit. The slope raster may contain values in either percent or degrees. This tool is commonly used to calculate the amount of agriculture on steep slopes as an indicator of water quality. Steep slopes lead to higher runoff of water, soil and fertilizer and are susceptible to erosion.
  * [**Land Cover Proportions**](<LandCoverProportions.md>) requires a reporting unit polygon layer and a land cover raster with an accompanying land cover classification scheme. This tool produces a table of the percent of specified land cover types within each reporting unit. This metric is the foundation for many landscape analyses, including assessment of condition.
  * [**Patch Metrics**](<PatchMetrics.md>) requires a reporting unit polygon layer and a land cover raster with an accompanying land cover classification scheme. This tool calculates number of patches, size of largest patch, average patch size, patch density, and proportion of largest patch area to total patch area. Optionally, Mean Distance to Closest Patch may also be reported.&nbsp; Patch metrics are commonly generated for forest cover for fragmentation studies, but may be calculated for any land cover class or group of classes.

***
_Created with the Personal Edition of HelpNDoc: [Easily create PDF Help documents](<https://www.helpndoc.com/feature-tour>)_
