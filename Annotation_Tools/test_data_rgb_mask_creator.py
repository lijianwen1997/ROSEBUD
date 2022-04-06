#!/usr/bin/env python3.8
# title           :test_data_Class_int_creator.py
# description     :Script to uniformly condition ROSEBUD uint8 output masks to a class mask on scale [0 or 1] for water nonwater
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


#####################################################################################
### Repo Location on machine for output -- CHANGE THESE THINGS###
#####################################################################################
# conversion to SD
repo_dir = "/home/reeve/Git_Repos/ROSEBUD"
masks_to_aug_dir = "/Sugar_Creek_Images/HD/uint8_binary_water_masks/"
highlevel1 = "/Sugar_Creek_Images/HD"

# conversion to other HD
highlevel2 = "/Sugar_Creek_Images/SD"

# output directories
mask_dir = repo_dir + masks_to_aug_dir
mask_out_dir = repo_dir + highlevel2 + "/rgb_binary_water_masks/"
mask2_out_dir = repo_dir + highlevel1 + "/rgb_binary_water_masks/"
#####################################################################################
im_wid = 384  # image width in pixels desired for training
im_hg = 512  # image width in pixels desired for training
masklist = sorted(os.listdir(mask_dir))  # list of masks in the mask directory
img_number = 0  # counter for the number of images that are output



def mastr1325_correct(mask):
    """This function will correct the annotated data provided with the mastr1325 dataset and correct them for the
    segmentation of only water
    Input:
        mask = 384 x 512 np array with values of 0,1,2, or 4 giving pixel-wise annotations of:
            > 0 = Obstacles and Environment
            > 1 = Water
            > 2 = Sky
            > 4 = Ignore Reagion/Unknown Category
    Output:
        mask = 384x512 np array of [0,255] 8bit greyscale image values representing the masked image
            > values represent likelihood of water with 0 to 255 scaled to 0 to 100%"""
    mask[mask != 1] = 0  # set all non water pixels (values) to 0 probability of water
    mask[mask == 1] = 255  # set all water pixels (values) to 1 probability of water
    return mask


def reverse_mask(mask):
    """This function will correct the annotated data provided with the mastr1325 dataset and correct them for the
    segmentation of only water
    Input:
        mask = 384 x 512 np array with values of 0,1,2, or 4 giving pixelf.img_out_dir = self.repo_dir + self.highlevel2 + "/images"-wise annotations of:
            > 0 = Obstacles and Environment
            > 1 = Water
            > 2 = Sky
            > 4 = Ignore Reagion/Unknown Category
    Output:
        mask = 384x512 np array of [0,255] 8bit greyscale image values representing the masked image
            > values represent likelihood of water with 0 to 255 scaled to 0 to 100%"""
    mask[mask != 0] = 1  # set all water pixels (values) to 1 probability of water
    return mask

def convert_to_RGB(gray):
    """This function will take a grayscale uint8 image and quickly make it an RGB (3-D) image that can be
    used in training of neural networks. This works with 0-255 coloration and 0-1 scales... But only for
    binary to tertiary masks:

    Input:
        gray - a greyscale image that is a hxw image
    output:
        rgb_image - teh converted RGB image that is still in B&W

    """
    wh = gray.shape  # get the size of the input
    h = wh[0]  # pull out the height of the image
    w = wh[1]  # pull out the width of the image
    rgb_image = np.zeros((wh[0], wh[1], 3), dtype=np.uint8) # create empty RGB array
    rgb_image[0:h, 0:w, 0] = gray[0:h, 0:w]  # set the r Channel
    rgb_image[0:h, 0:w, 1] = gray[0:h, 0:w]  # set the g Channel
    rgb_image[0:h, 0:w, 2] = gray[0:h, 0:w]  # set the b Channel

    return rgb_image

# End global function decleration
# =================================================================================================
# Begin main script


if __name__ == '__main__':
    loop_num = 1  # initialize the loop counter
    num_images = len(masklist)  # Get the number of images that are being augmented
    # gen_and_split = True
    # if gen_and_split:
    for a in masklist:  # for each image listed
        name = a.split('.')
        x = name[0]  # pull out the name of the image
        orig_mask = imgread(mask_dir + a)  # read in the current masked image that corresponds to cur_image

        # Correct mask if from mastr1325 dataset
        if orig_mask.shape == (384, 512):  # if the mask has the exact resolution of the mastr1325 dataset
            orig_mask = mastr1325_correct(orig_mask)  # coorect the mask
        # Transform the image to desired resolution
        new_mask = stf.resize(orig_mask, (im_wid, im_hg))  # change res. of mask to correct CNN size

        # convert base resized imagaes to 8bit
        new_mask = ubt(new_mask)  # convert to 8bit (0,255)
        orig_mask = ubt(orig_mask)   # convert to 8bit (0,255)


        imgsave(mask_out_dir + x + '.png', convert_to_RGB(new_mask))  # write the resized image
        imgsave(mask2_out_dir + x + '.png', convert_to_RGB(orig_mask))  # write the original image

        print("Image Number " + str(loop_num) + "/" + str(num_images) + " Completed -->" +
              str(round(100*loop_num/num_images, 3)) + " % complete")

        loop_num += 1  # increase the loop number
