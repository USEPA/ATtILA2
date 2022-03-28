# Identify Overlapping Polygons

Summary&nbsp;

Determines whether an input polygon feature layer contains overlapping polygons, and creates new non-overlapping feature layers.

&nbsp;

Usage

* ***NOTE:** Processing time for this tool varies depending on the number of polygons in the* **Input polygon features** layer. *To minimize processing time, consider creating a new* **Input polygon features** *layer that does not include unwanted polygons. This tool may create multiple polygon layers which will consume disk space in the **Output workspace**. If the **Output workspace** resides on a disk with limited disk space, the tool may fail during processing. To prevent this, consider changing the **Output workspace** to a location with sufficient available disk space, or free up disk space on the disk in which the current **Output workspace** resides to accommodate the new polygon layers.*
* This tool processes all polygons in the **Input polygon features** layer regardless of selections set. The ability to limit discovery of overlaps to only selected polygons is not supported in this release.
* When overlapping polygons are discovered in the **Input polygon features** layer, the tool creates new polygon layers. The number of new layers is based on the maximum number of overlaps for any individual polygon. For example, when one or more polygons in the **Input polygon features** layer are overlapped by, at most, one other polygon, the tool produces two new non-overlapping polygon layers. When one or more polygons are overlapped by two other polygons, the tool produces three new non-overlapping polygons layers, etc.
* When the **Check for overlaps only** option is enabled, no new layers are created. Therefore, the **Output workspace** is grayed out.

&nbsp;

Syntax&nbsp;

IOP (Input\_polygon\_features, Output\_workspace, Check\_for\_overlaps\_only)&nbsp;

| Parameter | Explanation | Data Type |
| --- | --- | --- |
| Input\_polygon\_features | The vector polygon dataset upon which the overlapping polygon check will be performed. | Feature Layer |
| Output\_workspace | The output location in which new polygon layers will be saved if overlapping polygons are present in the Input polygon features. If the Output workspace is a file folder, new layers will be saved as shapefiles. If the Output workspace is a geodatabase, new layers will be saved as geodatabase feature classes. | Workspace |
| Check\_for\_overlaps\_only (optional) | Specifies whether the process will result in new non-overlapping polygon layers. false - Non-overlapping polygon layers will be produced. This is the default. true - Non-overlapping polygon layers will not be produced. Instead, the tool will simply determine whether overlapping polygons exist in the Input polygon features layer, and, if so, the number of overlaps present. These results are reported in the tool results box. | Boolean |


&nbsp;

Credits&nbsp;

&nbsp;

Environments

Current Workspace, Scratch Workspace, Output Coordinates same as input, Processing extent min of inputs

***
_Created with the Personal Edition of HelpNDoc: [Full-featured multi-format Help generator](<https://www.helpndoc.com/help-authoring-tool>)_
