# External LCC Editor

Summary

The Land Cover Classification Editor provides a user-friendly interface to create or edit a Land Cover Classification XML file for use in ATtILA for ArcGIS.

&nbsp;

Land Cover Classification Editor

To start editing, click the Create or Modify Land Cover Classification (.xml) File tool in the ATtILA Toolbox.

&nbsp;

![Image](<lib/ModifyLCC.png>)

&nbsp;

The tool will open with the message "This tool has no parameters." Simply click OK to open the LCC Editor graphical user interface.

&nbsp;

![Image](<lib/ModifyLCC2.png>)

&nbsp;

&nbsp;

Land Cover Classification Editor Sections

The LCC Editor consists of four windows ([VALUES](<ValuesWindow.md>), [COEFFICIENTS](<CoefficientsWindow.md>), [METADATA](<MetadataWindow.md>), and [CLASSES](<ClassesWindow.md>)), with buttons to edit information within the windows. In addition, the Editor contains menu dropdowns with commands to manipulate the LCC XML file and the appearance of the LCC Editor, and an icon toolbar below the menu dropdowns that also controls the Editor's appearance.

&nbsp;

![Image](<lib/lcc-editor1.png>)&nbsp;

&nbsp;

&nbsp;

Menu Items

**File**

The File menu contains file utilities necessary for manipulation of the XML files:

&nbsp;

* &nbsp;
  * &nbsp;
    * New - Clears the Editor for a new file or for a clean start.
    * Open - Opens an existing XML file.
    * Open Recent - Allows for quick navigation to the five most recent XML files viewed.
    * Restore AutoSave - Restores an auto-saved version of the current work. AutoSave occurs every five seconds; select to restore the last saved version of the file.
    * Save - Saves the existing work in the LCC editor to a new XML file if none exists, or to the opened file name.
    * Save As - Saves the existing work in the LCC editor with a new file name.
    * Quit - Closes the Editor

&nbsp;

**View**

The View menu allows the user to turn on or off the three dockable windows on the left side of the tool: Values, Coefficients, and Metadata.

&nbsp;

* &nbsp;
  * &nbsp;
    * Show/Hide Values Window Dock - Toggles the Values Window on or off.
    * Show/Hide Coefficients Window Dock - Toggles the Coefficients Window on or off.
    * Show/Hide Metadata Window Dock - Toggles the Metadata Window on or off.

&nbsp;

The Icon Toolbar provides the same functionality.

&nbsp;

The windows may also be viewed as tabs by clicking on the title bar of a window, holding the mouse button and dragging the window onto another window, then releasing the mouse button. To untab, click the title bar of the window and drag to an open location (the other windows will "move" out of the way).

&nbsp;

Double-clicking on the title bar of a window will pop it out from the editor.

&nbsp;

**Import**

Reserved for future use.

&nbsp;

**Help**

The Help menu provides access to the ATtILA for ArcGIS help document and provides information about the editor.

&nbsp;

* &nbsp;
  * LCCEditor Help - Opens the ATtILA for ArcGIS help document.
  * About LCCEditor - Provides system information about the editor.

&nbsp;

&nbsp;

Icon Toolbar

![Image](<lib/LCC%20Icon%20Toolbar.png>)

&nbsp;

The Icon Toolbar provides the same functionality as View.

&nbsp;

* &nbsp;
  * Show/Hide Values - Toggles the [Values Window](<ValuesWindow.md>) on or off.
  * Show/Hide Metadata - Toggles the [Metadata Window](<MetadataWindow.md>) on or off.
  * Show/Hide Coefficients - Toggles the [Coefficients Window](<CoefficientsWindow.md>) on or off.

&nbsp;

&nbsp;

Entering and Editing Data

Information is entered into the [Values window](<ValuesWindow.md>), the [Metadata window](<MetadataWindow.md>) and the [Classes window](<ClassesWindow.md>). In this version of ATtILA for ArcGIS, the [Coefficients window](<CoefficientsWindow.md>) is uneditable. Future versions will allow for editing within the Coefficients window.

&nbsp;

The general workflow is as follows with additional detail in the specific table sections:

1. &nbsp;
   1. Raster values, their descriptions, and their properties (exclusion and coefficient values) are entered in the Values table.
   1. Classes are created in the Classes tree. Classes may be comprised of a single land cover type, multiple land cover types grouped together, or groups of groups.
   1. Items from the Values table are added to the appropriate section(s) in the Classes tree.
   1. Metadata containing the name and description of the Land Cover Classification are added to the Metadata section.


***
_Created with the Personal Edition of HelpNDoc: [Free EPub producer](<https://www.helpndoc.com/create-epub-ebooks>)_
