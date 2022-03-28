# Background Processing error

When running a tool in which the output and intermediate files are directed to be saved to a file geodatabase, the following Background Processing error may occur:

&nbsp;

![Image](<lib/ATtILA%20Background%20Processing%20Error.png>)

&nbsp;

This error may be due to an incompletely deleted file geodatabase, such as the attilaScratchWorkspace.gdb. This occurs periodically when the attilaScratchWorkspace.gdb is deleted using ArcCatalog. While the geodatabase may be successfully deleted and no longer appear in the ArcCatalog interface, some folders and files may linger.

&nbsp;

To correct this, simply open Windows Explorer, navigate to the disk location where the file geodatabase formerly resided, and delete the lingering geodatabase folder and its contents.

***
_Created with the Personal Edition of HelpNDoc: [Free iPhone documentation generator](<https://www.helpndoc.com/feature-tour/iphone-website-generation>)_
