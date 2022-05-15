# ROSEBUD
This github repository contains all images and masks pertaining to the River Obstacle Segmentation 
Enroute By USV Dataset (ROSEBUD) Fluvial Dataset. The dataset contains annotated images for training supervised networks on the task of recognizing and segmenting fluvial scnenes. In total there are 549 
images split across two sub-sets of data detailed below. Across each subset there are two sub directories

- HD - All images and masks are 1920 x 1440 
- SD - All images and masks are 512 x 384 

Within each of the above sub-directories there are 7 folders sorting the available masks and images.
Images and masks can be paired by their trailing number, so image_### matches all masks_###. Multiple types of masks are provided for ease of use with various existing segmentation networks.

- **images** - Folder contains all RGB images extracted from recorded video 

![image](https://github.com/Reeve-Lambert/ROSEBUD/blob/main/Sugar_Creek_Images/SD/images/253.png)
- **int_class_binary_water_masks** - folder contains greyscale (width x height) masks of images where each pixel has an integer
value of 1 for pixels that contain water, and 0 that contain non-water entities. These masks can be used
for the water recognition task

![image](https://github.com/Reeve-Lambert/ROSEBUD/blob/main/Sugar_Creek_Images/SD/intclass_binary_water_masks/253.png)
- **uint8_binary_water_masks** - folder contains greyscale (width x height) masks of images where each
pixel is given a value of 255 or 0 for pixels representing water and non-water respectivley. These masks can 
be used in the water recognition task

![image](https://github.com/Reeve-Lambert/ROSEBUD/blob/main/Sugar_Creek_Images/SD/uint8_binary_water_masks/253.png)
- **rgb_binary_water_masks** - folder contains RGB (width x height x 3) masks of images where each pixel in the image
is given a value of white [255,255,255] ([r,g,b]) for each pixel that represents water, and a value of black [0,0,0] 
([r,b,g]) for each pixel that represents an non-water.

![image](https://github.com/Reeve-Lambert/ROSEBUD/blob/main/Sugar_Creek_Images/SD/rgb_binary_water_masks/253.png)
- **rgb_fluvial_masks** - folder contains RGB (width x height x 3) masks of fluvial scenes that can be used towards full
recognition of fluvial scenes. These images spereate the scene into more categores than just water and non water. 
the masks seperate the image into 7 distinct classes:
  - Water - [255,255,255]
  - Shore/bank of river/creek - [0,0,255]
  - Bridges - [0, 255, 0]
  - Boats/cars/people - [255,0,0]
  - Trees and other foliage - [255, 255, 0]
  - sky/clouds - [255, 0, 255]
  - Debris within the river and on the shore - [0, 255, 255]

![image](https://github.com/Reeve-Lambert/ROSEBUD/blob/main/Sugar_Creek_Images/SD/rgb_fluvial_masks/253.png)
- **uint8_fluvial_masks** - folder contains greyscale (width x height) masks of fluvial scenes that can be used towards full
recognition of fluvial scenes. These images spereate the scene into more categores than just water and non water. 
the masks seperate the image into 7 distinct classes:
  - Water - [255]
  - Shore/bank of river/creek - [26]
  - Bridges - [51]
  - Boats/cars/people - [76]
  - Trees and other foliage - [102]
  - sky/clouds - [128]
  - Debris within the river and on the shore - [153]

![image](https://github.com/Reeve-Lambert/ROSEBUD/blob/main/Sugar_Creek_Images/SD/uint8_fluvial_masks/253.png)
- **Mask_Overlay** - folder contains rgb fluvial scenes mapped onto the image for visualization of how the two line up.
the image is masked with overlays as:
  - Water - clear overlay
  - shore/bank of river/creek - red overlay
  - Bridges - green overlay
  - Boats/cars/people - blue overlay
  - Trees, foliage, and background buildings - cyan overlay
  - sky/clouds - fusia overlay
  - Debris within the river and on the shore - yellow overlay

![image](https://github.com/Reeve-Lambert/ROSEBUD/blob/main/Sugar_Creek_Images/SD/mask_overlay/253.png)

### Wabash River Images
249 images were obtained from video recorded on a GoPro Hero 4 on Purdue's Mahmoudian labs' [BREAM ASV] (https://ieeexplore.ieee.org/document/9389236) during
an autonomous traversal of the Wabash River in Tippacanoe County, Indiana in July of 2021. The images encompass the river milage
between Davis Ferry and Shamrock parks. Many bridges and other boats are present within this subset, but due to the high
water level at the time of data collection few obstacles are present in the river and thus images.


![image](https://github.com/Reeve-Lambert/ROSEBUD/blob/main/Wabash_Images/SD/mask_overlay/163.png)
### Sugar Creek Images
300 images were collected from a canoe on a GoPro Hero 4 on September of 2021 during a manned traversal of Sugar Creek 
in the state of Indiana. The impages in this subset contain many compelx features and shapes from the twisiting and winding sandbars
and debris within the creek at the time of traversal.

![image](https://github.com/Reeve-Lambert/ROSEBUD/blob/main/Sugar_Creek_Images/SD/mask_overlay/223.png)

### Forward Progress
Currently image artifacts are present in the fluvial RGB and greyscale images. These show up as black pixels in the RGB image, 
and as off gray pixels in the greyscale fluvial mask. This encompasses less than 10 percent of total pixels and is a remnant
of the image processing done by CV2 in rgb. In the future this will be resolved to provide higher quality masks for fluvial image
learning. This issue is not present in the water - nonwater masks.
