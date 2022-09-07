# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 15:31:33 2022

@author: awatson
"""

import nibabel as nib
from skimage import io, img_as_uint, img_as_float32
import numpy as np

file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_rawdata.nii"
# file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_avg_dwi.nii"
# file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_tensor.nii"


# #Background? Bone?
# file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_a0.nii"
# file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_M0_rigid.nii"

# #Invert of background, bone?
# file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_fa.nii"

# #Nothing interesting?
# file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_adc.nii"
# file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_MTR_rigid.nii"


fileObj = nib.load(file)

data = fileObj.get_fdata()

data = data.astype('uint16')

if len(data.shape) == 4:
    # Create a mean image accross the last axis
    data = img_as_float32(data)
    data = img_as_uint(np.mean(data,axis=-1))




