#!/usr/bin/env python3.8
# title           :change_png.py
# description     :Script to change images in a given directory from JPG to PNG and redistribute
# author          :Reeve Lambert
# Rev date        :4/3/2022
# version         :0.1
# notes           :Scikit-image is used for a significant portion of the image processing and
# python_version  :3.8
# ==============================================================================
import numpy as np
import os
import shutil
import datetime
import csv
import math as m
import time
import random
import glob
# import matplotlib.pyplot as plt
from skimage import img_as_float64 as flt  # https://scikit-image.org/docs/stable/api/skimage.html
from skimage import img_as_ubyte as ubt  # https://scikit-image.org/docs/stable/api/skimage.html
from skimage.io import imsave as imgsave  # https://scikit-image.org/docs/dev/api/skimage.io.html
from skimage.io import imread as imgread  # https://scikit-image.org/docs/dev/api/skimage.io.html
import skimage.transform as stf  # https://scikit-image.org/docs/dev/api/skimage.transform.html
import skimage.util as sutil  # https://scikit-image.org/docs/dev/api/skimage.util.html
import skimage.filters as sfilt  # https://scikit-image.org/docs/stable/api/skimage.filters.html
import skimage.color as scol  # https://scikit-image.org/docs/dev/api/skimage.color.html
import skimage.exposure as sexp  # https://scikit-image.org/docs/dev/api/skimage.exposure.html

"""This script/file will format and condition data as is desired for CNN training. Users will input a raw data directory
and an output directory, desired image format outputs, and naming convention, etc."""

def convert_to_RGB(gray, flip):
    """This function will take a grayscale uint8 mask from the annotation program and quickly make it an RGB (3-D) +
    mask that can be used in training of neural networks.

    Input:
        gray - a greyscale image that is a hxw image
    output:
        rgb_image - teh converted RGB image that is still in B&W

    """
    colors = [[255, 255, 255], [0, 0, 255], [0, 255, 0], [255, 0, 0], [255, 255, 0], [255, 0, 255], [0, 255, 255]]
    classes = ["water", "shore/bank", "bridge", "boat", "trees", "sky", "log/debree"]
    greyscales = [255, 26, 51, 76, 102, 128, 153]

    wh = gray.shape  # get the size of the input
    h = wh[0]  # pull out the height of the image
    w = wh[1]  # pull out the width of the image
    if flip:
        rgb_image = np.zeros((wh[0], wh[1], 3), dtype=np.uint8) # create empty RGB array

        for i in range(0,h-1):
            for j in range(0,w-1):
                id = None
                if gray[i, j] == greyscales[0]:
                    rgb_image[i, j, 0:3] = colors[0]
                elif gray[i, j] == greyscales[1]:
                    rgb_image[i, j, 0:3] = colors[1]
                elif gray[i, j] == greyscales[2]:
                    rgb_image[i, j, 0:3] = colors[2]
                elif gray[i, j] == greyscales[3]:
                    rgb_image[i, j, 0:3] = colors[3]
                elif gray[i, j] == greyscales[4]:
                    rgb_image[i, j, 0:3] = colors[4]
                elif gray[i, j] == greyscales[5]:
                    rgb_image[i, j, 0:3] = colors[5]
                elif gray[i, j] == greyscales[6]:
                    rgb_image[i, j, 0:3] = colors[6]
                else:
                    if i < 5 or j < 5 or i > (h-5) or j > (w-5):
                        z=1
                        # do nothing, dont have time
                    else:  # give nearest value max component
                        temp = gray[i-5:i+5, j-5:j+5]
                        unique, counts = np.unique(temp, return_counts=True)
                        index = np.where(counts == max(counts))
                        z = len(index[0])
                        if z > 1: # if there is a tie for most pixels
                            index = index[0][z-1]
                        q = int(unique[index])
                        try:
                            id = greyscales.index(q)
                            rgb_image[i, j, 0:3] = colors[id]
                        except:
                            arr = np.asarray(greyscales)
                            id = (np.abs(arr - unique[index])).argmin()
                            # now update RGB
                            rgb_image[i, j, 0:3] = colors[id]
    else:
        rgb_image = gray
        for i in range(0,h-1):
            for j in range(0,w-1):
                id = None
                if gray[i, j] not in greyscales:
                    if i < 5 or j < 5 or i > (h-5) or j > (w-5):
                        z=1
                        # do nothing, dont have time
                    else:  # give nearest value max component
                        temp = gray[i-5:i+5, j-5:j+5]
                        unique, counts = np.unique(temp, return_counts=True)
                        index = np.where(counts == max(counts))
                        z = len(index[0])
                        if z > 1: # if there is a tie for most pixels
                            index = index[0][z-1]
                        q = int(unique[index])
                        try:
                            id = greyscales.index(q)
                            rgb_image[i, j] = greyscales[id]
                        except:
                            arr = np.asarray(greyscales)
                            id = (np.abs(arr - unique[index])).argmin()
                            # now update RGB
                            rgb_image[i, j] = greyscales[id]
    return rgb_image

"""Intitialize the desired direcetories outputs, formats, etc"""
#####################################################################################
### Repo Location on machine for output -- CHANGE THESE THINGS###
#####################################################################################
# conversion to SD
repo_dir = "/home/reeve/Git_Repos/ROSEBUD/Sugar_Creek_Images/"
images_to_convert = "HD/images/"
masks1_to_Convert = "HD/mask_overlay/"
masks2_to_Convert = "HD/uint8_fluvial_masks/"


# conversion to other HD
png_out = "HD/images/"
pngmasks1 = "HD/rgb_fluvial_masks/"
pngmasks2 = "HD/uint8_fluvial_masks/"
img_out = "SD/images/"
masks1_out = "SD/rgb_fluvial_masks/"
masks2_out = "SD/uint8_fluvial_masks/"
overlay_out = "SD/mask_overlay/"
#####################################################################################
# directories of input data
raw_dir = repo_dir + images_to_convert
mask1_dir = repo_dir + masks1_to_Convert
mask2_dir = repo_dir + masks2_to_Convert

# directories of processed output data
img1_out_dir = repo_dir + png_out
img2_out_dir = repo_dir + img_out
mask1_out_dir = repo_dir + pngmasks1
mask2_out_dir = repo_dir + pngmasks2
mask3_out_dir = repo_dir + masks1_out
mask4_out_dir = repo_dir + masks2_out

overlay_out_sd = repo_dir + overlay_out


##########################################################################
## image - backwards values ####
im_wid = 384  # image width in pixels desired for training
im_hg = 512  # image width in pixels desired for training
hd_wd = 1440  # hd image width
hd_hg = 1920  # image height
#########################################################################

imlist = sorted(os.listdir(raw_dir))  # list of images in the currrent directory
mask1list = sorted(os.listdir(mask1_dir))  # list of masks in the mask directory
mask2list = sorted(os.listdir(mask2_dir))  # list of masks in the mask directory
num_images = len(imlist)  # Get the number of images that are being augmented


# # For each image to be renamed
# loop_num = 0
# for a in imlist:  # for each image listed
#     name = a.split('.')
#     x = name[0]  #pull out the name of the image
#     # load the image
#     orig_img = imgread(raw_dir + a)  # read in the current raw image within the data
#     # Transform the image to desired resolution
#     cur_img = stf.resize(orig_img, (im_wid, im_hg))  # change res. of image to correct CNN siz
#     imgsave(img1_out_dir + x + '.png', orig_img)  # Write the orig output image
#     imgsave(img2_out_dir + x + '.png', cur_img)  # write the resized image
#
#     loop_num+=1
#     print("Image Number " + str(loop_num) + "/" + str(num_images) + " Completed -->" +
#           str(round(100*loop_num/num_images, 3)) + " % complete")
# loop_num = 0
# # For each overlay to be renamed
# for a in mask1list:  # for each image listed
#     name = a.split('.')
#     x = name[0]  # pull out the name of the image
#     # load the image
#     orig_img = imgread(mask1_dir + a)  # read in the current raw image within the data
#     # Transform the image to desired resolution
#     cur_img = stf.resize(orig_img, (im_wid, im_hg))  # change res. of image to correct CNN siz
#     imgsave(mask1_dir + x + '.png', orig_img)  # Write the resized output image
#     imgsave(overlay_out_sd + x + '.png', cur_img)  # Write the resized output image
#     loop_num += 1
#     print("overlay Number " + str(loop_num) + "/" + str(num_images) + " Completed -->" +
#           str(round(100 * loop_num / num_images, 3)) + " % complete")
loop_num = 0
# For each fluvial mask to be renamed
for a in mask2list:  # for each image listed
    name = a.split('.')
    x = name[0]  #pull out the name of the image
    # load the image
    orig_mask = convert_to_RGB(imgread(mask2_dir + a), False)  # read in the current raw image within the data
    # Transform the image to desired resolution
    cur_mask = stf.resize(orig_mask, (im_wid, im_hg))  # change res. of image to correct CNN siz


    # Convert Greyscale Masks to RGB masks
    orig_rgb = convert_to_RGB(orig_mask, True)
    cur_rgb = stf.resize(orig_rgb, (im_wid, im_hg))  # change res. of image to correct CNN siz

    # Write converted RGB Masks
    temp = x.split('_')
    y = temp[len(temp)-1]
    imgsave(mask1_out_dir + "rgb_fluvial_mask_" + y + '.png', orig_rgb)    # Write the orig output image
    imgsave(mask3_out_dir + "rgb_fluvial_mask_" + y + '.png', cur_rgb)    # Write the resized output image

    # Write the orig output image
    imgsave(mask2_out_dir + x + '.png', orig_mask)
    # Write the resized output image
    imgsave(mask4_out_dir + x + '.png', cur_mask)
    loop_num += 1
    print("mask Number " + str(loop_num) + "/" + str(num_images) + " Completed -->" +
          str(round(100 * loop_num / num_images, 3)) + " % complete")

