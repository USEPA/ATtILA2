==================================================================================================
Analytical Tools Interface for Landscape Assessments for ArcGIS Pro (ATtILA for ArcGIS Pro) ReadMe
==================================================================================================

---------------
version 2.0
---------------

10-14-2022 

This file is intended to give a brief overview of what ATtILA is, how to install it, and where to find more information. For more detailed documentation, please see ATtILA's wiki located at https://github.com/USEPA/ATtILA2/wiki.

---------------
What is ATtILA?
---------------

ATtILA for ArcGIS Pro is an Esri ArcGIS toolbox that allows users to easily calculate many common landscape metrics. GIS expertise is not required, but some experience with ArcGIS is recommended. Three metric groups (toolsets) are currently included in ATtILA: Landscape Characteristics, People in the Landscape, and Riparian Characteristics, along with a Utilities section. ATtILA for ArcGIS Pro is written using the Python programming language and is designed to accommodate spatial data from a variety of sources.

---------------
License
---------------

MIT License  

Copyright (c) 2019 U.S. Federal Government (in countries where recognized)  

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:  

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---------------
EPA Disclaimer
---------------

This is a draft report distributed for review purposes only.  Please do not quote or cite.

When this document review is complete and the comments are incorporated, then the Notice will appear as follows:

“The United States Environmental Protection Agency (EPA) GitHub project code is provided on an "as is" basis and the user assumes responsibility for its use. EPA has relinquished control of the information and no longer has responsibility to protect the integrity , confidentiality, or availability of the information. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by EPA. The EPA seal and logo shall not be used in any manner to imply endorsement of any commercial product or activity by EPA or the United States Government.”

------------------
Installing ATtILA
------------------

This README provides basic information on installing ATtILA for ArcGIS Pro using the downloadable zip file available at https://www.epa.gov/enviroatlas/attila-toolbox. For more detailed instructions on installing and using custom toolboxes in ArcGIS Pro, please see 'Connect to a toolbox' in ArcGIS Pro's Online Help.  New users should read through this wiki at least once to familiarize themselves with potential pitfalls associated with spatial data, ArcGIS limitations, or ATtILA for ArcGIS Pro processes.

REQUIREMENTS:
-------------

ATtILA for ArcGIS Pro requires ArcGIS Pro 2.6 or later and the Spatial Analyst extension.  ATtILA for ArcGIS Pro has not yet been tested on ArcGIS 3.0 or later versions.

INSTALLATION:
------------

1. Download the ATtILA for ArcGIS distribution zip file to a safe location, such as a Downloads directory.

2. Extract the contents of the ATtILA.zip file to a location where you commonly store personal Toolboxes, such as your ArcGIS directory under MyDocuments.  Ensure the ATtILA tbx file and the ToolboxSource folder are at the same directory level. ATtILA's directory structure is illustrated below:

    |
    |--Destination Folder
    |    |--ATtILA tbx
    |    |--ToolboxSource\
    |         |--ATtILA2
    |              |--ATtILA2
    |                   |--constants
    |                   |--ToolValidator
    |                   |--utils
    |              |--scripts
    |                   |--bin
    |         |--LandCoverClassifications


3. Start ArcGIS Pro. Open Catalog View or Catalog Pane, and right click on Toolboxes. Click on Add Toolbox. 
    
4. Navigate to ATtILA tbx, select it and click OK.

5. Check to see if the toolbox installed correctly, i.e., open Toolbox to see tools contained within.
 
    |-ATtILA
    |    -Landscape Characteristics
    |        -Core and Edge Metrics
    |        -Land Cover Diversity
    |        -Land Cover on Slope Proportions
    |        -Land Cover Proportions
    |        -Neighborhood Proportions
    |        -Patch Metrics
    |    -People in the Landscape
    |        -Facility Land Cover Views
    |        -Intersection Density
    |        -Land Cover Coefficient Calculator
    |        -Population Density Metrics
    |        -Population in Floodplain Metrics
    |        -Population Land Cover Views
    |        -Road Density Metrics
    |    -Riparian Characteristics
    |        -Floodplain Land Cover Proportions
    |        -Riparian Land Cover Proportions
    |        -Sample Point Land Cover Proportions
    |        -Stream Density Metrics
    |    -Utilities
    |        -Create or Modify Land Cover Classification (.xml)
    |        -Identify Overlapping Polygons
    |        -Process NAVTEQ for EnviroAtlas Analyses
    |        -Process NHD for EnviroAtlas Analysis
	|    -Online Help
		

NOTE: To make the ATtILA for ArcGIS Pro toolbox available to all new projects, right-click on the toolbox and select 'Add to New Projects'. This will add a link to ATtILA for ArcGIS Pro toolbox in project favorites. For more details on accessing ATtILA this way, see 'Project favorites' in ArcGIS Pro's Online Help.

---------------
Contact
---------------

Please report bugs and forward comments to: https://ecomments.epa.gov/enviroatlas/ and include “ATtILA” in the subject line.

----------------
Credits
----------------

Python code for ATtILA was written by Don Ebert (EPA), Michael Jackson (EPA), Baohong Ji (EPA), and Torrin Hultgren (EPA), with special assistance from Ellen D'Amico (Dynamac Corporation), and Doug Browning (EPA Student Services Contractor).

David Gottlieb (EPA Student Services Contractor) wrote the code for the Land Cover Coding Editor.

The original ATtILA ArcView extension tool was written in Avenue code by Don Ebert and Tim Wade with assistance from Dennis Yankee (Tennessee Valley Authority, Public Power Institute) who wrote code for the PCTIA_RD metric.

The following programmers were not directly involved with the project, but gave permission for their code to be incorporated into the original ATtILA and we greatly appreciate their generosity:

- Laine, Jarko. 1998. Intersec Script, Novo.  
- Eichenlaub, Bill. 1998. Profiler Script (Version 1.0), National Park Service.  
- O’Malley, Kevin. 1999. Two Theme Analyst Extension.  
- DeLaune, Mike. 2003. XTools Extension, Oregon Department of Forestry.  
- Martin, Eugene. 1999. Spatial.AlignedGridExtract Script, University of Washington.  
- Fox, Timothy J. 1998. Nearest Feature Analysis Tool Script, USGS Upper Midwest Environmental Science Center.  
- Cosmas, Tom. 1999. Table.RenameField Script, New Jersey Department of Environmental Protection.  
- Schultz, Ron. 2003. Bearing extension.   
- Jenness, Jeff. 2005. Distance/Azimuth Tools (Version 1.4b), Jenness Enterprises.  

Tim Wade (EPA), Deborah Chaloud (EPA), Megan Culler (EPA Student Services Contractor), Steven Jett (Innovate!, Inc.), Barabara Rosenbaum (EPA), Caroline Erickson (EPA) and Bob Ohman (EPA Senior Environmental Employment Program) wrote the help files for the  many versions of ATtILA.  

Rose Marie Moore (EPA), Anne Neale (EPA), Jeremy Baynes (EPA), and Barbara Rosenbaum (EPA) gave assistance with overall planning and budgeting.  

Molly Jenkins (ORISE Participant) provided invaluable assistance with ATtILA's webpage and graphic design.

Jeremy Baynes (EPA), Barbara Rosenbaum (EPA), Anne Neale (EPA), Laura Jackson (EPA), Megan Culler (Student Services Contractor), Jessica Daniel (EPA), Wei-Lun Tsai (EPA), Allison Killea (Student Services Contractor), Talyor Minich (EPA), and Torrin Hultgren (EPA) provided insightful and useful feedback regarding the myriad decisions that arose during ATtILA's development.  