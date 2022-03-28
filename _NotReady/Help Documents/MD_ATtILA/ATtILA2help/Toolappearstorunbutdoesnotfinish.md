# Tool appears to run but does not finish

If one of ATtILA for ArcGIS's tools 'hangs' (i.e., you enter all the necessary tool inputs and click OK, but the tool never finishes):

&nbsp;

* Open Windows Task Manager and select the hung ArcGIS application in the Applications Tab - Click End Task
* Reopen the ArcGIS application where the problem occurred
* Right-click on the tool and open it's properties
* Check under the source tab to be sure that the 'Run Python script in process' box is checked

&nbsp;

&nbsp; &nbsp; ![Image](<lib/ATtILA%20Tool%20Properties%20Source.png>)

&nbsp;

That should solve the problem.&nbsp;

&nbsp;

To relaunch the tool with all it's previously set parameters, checkboxes, and options, do the following:

&nbsp;&nbsp;

* Open the 'Not Run' shortcut menu in the Geoprocessing \> [Results Window](<http://resources.arcgis.com/en/help/main/10.1/index.html#//002100000013000000> "target=\"\_blank\"")
* Right-click on the tool execution that failed
* Select 'Re-Run'

&nbsp;


***
_Created with the Personal Edition of HelpNDoc: [Free EBook and documentation generator](<https://www.helpndoc.com>)_
