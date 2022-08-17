# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 20:57:49 2022

@author: alpha
"""

import zarr
import numpy as np
import sys
from numcodecs import Blosc


path = r'C:\code\stack_to_multiscale_ngff\stack_to_multiscale_ngff'
if path not in sys.path:
    sys.path.append(path)
    
from stack_to_multiscale_ngff.h5_shard_store import H5_Shard_Store as h5s


root = 'c:/code/testZarr'

root = r'Z:\testData\test_zarr'

store = h5s(root,verbose=1)

z = zarr.open(store)

compressor=Blosc(cname='zstd', clevel=9, shuffle=Blosc.BITSHUFFLE)

store = h5s(root + '/scale0',verbose=1)

zarr.zeros(shape=(10,10,10),chunks=(2,2,2),dtype=np.dtype('uint16'),compressor=compressor, store=store)


array[:] = np.arange(1000).reshape((10,10,10))


