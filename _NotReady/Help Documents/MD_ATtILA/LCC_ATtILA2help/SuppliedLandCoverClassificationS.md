# Supplied Land Cover Classification Schemas

An attempt has been made to standardize the land cover classification compiled metric fields among the NLCD1992, NLCD2001 and C-CAP data sets.&nbsp; Slightly different land cover classification schemes were used for each of these, although in some cases the only real difference is in the nomenclature.&nbsp; For example, NLCD1992 describes three urban classes as low density residential, high density residential, and commercial/industrial.&nbsp; Later NLCD outputs and C-CAP describe the three urban classes as low intensity developed, medium intensity developed, and high intensity developed.&nbsp; In the standard land cover classifications provided here, the latter terminology was adopted, primarily to aid the user in making comparisons among these data sets.&nbsp; The Developed metric for each consists of these three urban descriptions plus urban grasslands.

In a few cases, it was not possible to complete standardization.&nbsp; The NLCD1992 data contains separate descriptions of natural and man-made barren lands, while the later NLCD and C-CAP data do not make this distinction.&nbsp; Therefore, the user must be cautious in making comparisons or drawing conclusions based on the barren metric.

Supplied schemes may be designated as either "ALL" or "LAND" (e.g. NLCD 2001 ALL vs. NLCD 2001 LAND). Schemes designated as "ALL" include all land cover classes in reporting unit area calculations, while those designated as "LAND" include only terrestrial land cover classes, with non-terrestrial land cover classes such as water and snow/ice excluded.

When a classification scheme with excluded land cover classes is selected, the areas of the excluded classes are disregarded in metric calculations. This means, when selecting a "LAND" classification scheme, the tool will process individual land cover classes and calculate metrics based on the total terrestrial area they occupy within the reporting unit, rather than the percent of the total area within the reporting unit. Thus, when using a "LAND" classification scheme, a calculated output value of 70% forest in say the Land Cover Proportions tool means that 70% of the land area in the reporting unit is covered by forest.

***
_Created with the Personal Edition of HelpNDoc: [Easy EBook and documentation generator](<https://www.helpndoc.com>)_
