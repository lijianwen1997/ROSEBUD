# Extract and Annotate Images
Use this to convert raw videos to masked images.

## Setup and Requirements

Required Python libraries: openCV, numpy

Folder with the raw videos. If the folder also containes further folders, the images can be saved in these folders during the saving process.

**Set up variables at the top of the script:**
Copy the path for the folder with the videos into video_file as seen in the explorer.
Copy the file name of the video including extension into video_file.
Optional: Change the starting frame to begin the conversion from a certain frame.

If the file is found, the video will open stating with the selected start frame.

## Main Display (Video Scrubbing)

Displays the raw extracted frame from the video. The frame number is shown in the top right. The annotator is mostly interacted with using keypresses. See options for the main display below:

**Scrubbing in the video by keypresses**
* 'backspace'   Go back       1 frame
* 'l'           Go back      10 frames
* 'L'           Go back     100 frames
* 'space'       Go forward    1 frame
* 'n'           Go forward   10 frames
* 'N'           Go forward  100 frame

**Functions**

* 's'           Saving: Select a folder to save the raw image into.
* 'q'           Quit the converter. This will end the script.
* 'e'           Editing: Create masks for the displayed frame by entering **Edit Mode**

## Edit Mode (Creating masks)

Annotate zones by creating polygons enclosing them.
...



