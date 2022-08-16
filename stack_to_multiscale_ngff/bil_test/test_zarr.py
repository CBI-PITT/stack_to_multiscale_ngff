# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 20:57:49 2022

@author: alpha
"""

import zarr
import numpy as np
import sys

path = r'C:\code\stack_to_multiscale_ngff\stack_to_multiscale_ngff'
if path not in sys.path:
    sys.path.append(path)
    
from stack_to_multiscale_ngff.h5_shard_store import H5_Shard_Store as h5s


root = 'c:/code/testZarr'

root = r'Z:\testData\test_zarr'

