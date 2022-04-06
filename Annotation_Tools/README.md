# Extract and Annotate Images
Use this to convert raw videos to masked images.

## Setup and Requirements

Required Python libraries: openCV, numpy, pymatting

At the top of the code there are two variables for the path to the root folder (folder with the video footage) and the video name (including extension). To seperate the masked images into different subsets, create folders inside the root folder. These will be imported and can be selected during the saving process for each finished image.
To start from a specific point in the video the start frame can be changed. To reedit a single frame change the file path to the image and the converter will open in Masking mode with all previous annotations. 

## Main (Video)

Displays the raw extracted frame from the video. The frame number is shown in the top right. If the frame has been edited and saved before this is displayed in the top left corner. Editing this frame again will give the option to start with the previous annotations.

**Scrubbing in the video by keypresses**
* 'backspace'       Go back       1 frame
* 'l'               Go back      10 frames
* 'L'               Go back     100 frames; using this multiple times might cause a short delay
* 'any other key'   Go forward    1 frame
* 'n'               Go forward   10 frames
* 'N'               Go forward  100 frames; using this multiple times might cause a short delay

**Functions**

* 's'           Saving: Save the frame without creating masks.
* 'q'           Quit the converter. Any unsaved data and templates will be lost.
* 'e'           Editing: Create masks for the displayed frame by entering **Masking Mode**

## Masking Mode

Annotate zones by creating polygons enclosing them and by using Alpha matting. Different objects can be seperated by using Zone Indexes, any area not covered will default to positive/ target. 

# Creating Polygons

* 'left click'  Add new Point to the Polygon 
* 'right click' Close the Polygon and fill it
* Snapping: Each snapping setting is turned on / off by the respective key.
    - 'h'   Create Points at the left or right side of the frame
    - 'v'   Create Points at the top or bottom of the frame
    - 'v+h' Vertical and horizontal Snapping can be combined to create points in the corners
    - 'g'   Select the closest Point in any previous Polygon (if any exist). This overwrites any enabled h/v snapping.
* 'number keys' Change Zone Index for drawing. See below for the Indexes.
* 'f'           Follow an existing Polygon
    - If the active Point is not on another Polygon, this creates a new Point at the closest extisting Point of any Polygon
    - If the active Point is on another Polygon, this creates a new Point on the next Point of the existing Polygon
    - Use 'Tab' to change the direction of traversing the existing Polygon
    - Use 'Tab' if the active Point belogs to multiple existing Polygons to switch between each of the options for the new Point
* 'backspace'   Delete the last Point and go back to the previous Point
* 'r'           Delete all Point of the current Polygon

# Other Functions

* 'e'   Enter **Edit Mode**
* 'q'   Exit Masking Mode, go back to **Scrubbing Mode**
* 'T'   Store all completed Polygons as the Template
* 't'   Paste from template
* 's'   Save finished mask
* 'r'   Delete last completed Polygon
* 'R'   Delete all Polygons
* 'm'   Activate Alpha Matting
* 'i'   Turn on / off the Indicator (circle around the active Point); The Indicator still appears when using certain Snapping Modes
* 'n'   Show normals for last completed Polygon; hit any Key to exit
* 'd'   Show Edge Detection; change thresholds with u/j for lower and i/k for upper. Exit with Enter/ Escape

## Edit Mode

All Edge points of the annotations are marked with circles. Click next to a point to select it. The point as well as the polygon it is part of will be marked. The selected Polygon will also be made active with the selected Point as the newest Point, so exiting Edit mode and hitting 'backspace' or 'r' will delete the selected Point/ selected Polygon.

* 'w,a,s,d'   Move point up, left, down, right by one pixel
* 'W,A,S,D'   Move point up, left, down, right by 10 pixel
* 'X'         Delete Point. If only one point remains the Polygon will be deleted
* 'I'         Insert a new Point
* 'Tab'       Switch between Polygons if active point is part of multiple Polygons
* 'n/l'       Go to next/ last Point of current Polygon
* 'backspace' Undo the last action (delete/ insert)
* 'esc'       Exit Edit Mode

## Task List

Scaling annotations based on image size
Export to COCO format