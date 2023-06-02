# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 21:11:13 2022

@author: awatson
"""

import zarr
import os
import psutil
import glob
from numcodecs import Blosc
from natsort import natsorted

# Import local functions
from stack_to_multiscale_ngff._builder_image_utils import tiff_manager


# file = r'C:\code\testData\191817_05308_CH1.tif'
# file = r'H:\globus\pitt\bil\fMOST RAW\CH1\182725_03717_CH1.tif'


## Import mix-in classes
from stack_to_multiscale_ngff._builder_img_processing import _builder_downsample
from stack_to_multiscale_ngff._builder_utils import _builder_utils
from stack_to_multiscale_ngff._builder_ome_zarr_utils import _builder_ome_zarr_utils
from stack_to_multiscale_ngff._builder_image_utils import _builder_image_utils
from stack_to_multiscale_ngff._builder_multiscale_generator import _builder_multiscale_generator
# from stack_to_multiscale_ngff._builder_colors import _builder_colors

class builder(_builder_downsample,
            _builder_utils,
            _builder_ome_zarr_utils,
            _builder_image_utils,
            _builder_multiscale_generator):
    '''
    A mix-in class for builder.py
    '''
    def __init__(
            self,in_location,out_location,fileType='tif',
            geometry=(1,1,1),origionalChunkSize=(1,1,1,1024,1024),finalChunkSize=(1,1,64,64,64),
            cpu_cores=os.cpu_count(), sim_jobs=4, mem=int((psutil.virtual_memory().free/1024**3)*.8),
            compressor=Blosc(cname='zstd', clevel=5, shuffle=Blosc.SHUFFLE),
            zarr_store_type=zarr.storage.NestedDirectoryStore, tmp_dir='/local',
            verbose=False, performance_report=False, progress=False,
            verify_zarr_write=False, omero_dict={},
            skip=False,
            downSampType='mean',
            directToFinalChunks=False
            ):
                
        self.in_location = in_location
        self.out_location = out_location
        self.fileType = fileType
        self.geometry = tuple(geometry)
        self.origionalChunkSize = tuple(origionalChunkSize)
        self.finalChunkSize = tuple(finalChunkSize)
        self.cpu_cores = cpu_cores
        self.sim_jobs = sim_jobs
        self.workers = int(self.cpu_cores / self.sim_jobs)
        self.mem = mem
        self.compressor = compressor
        self.zarr_store_type = zarr_store_type
        self.tmp_dir = tmp_dir
        self.verbose = verbose
        self.performance_report = performance_report
        self.progress = progress
        self.verify_zarr_write = verify_zarr_write
        self.omero_dict = omero_dict
        self.skip = skip
        self.downSampType = downSampType
        self.directToFinalChunks = directToFinalChunks
        
        self.res0_chunk_limit_GB = self.mem / self.cpu_cores / 4 #Fudge factor for maximizing data being processed with available memory during res0 conversion phase
        self.res_chunk_limit_GB = self.mem / self.cpu_cores / 24 #Fudge factor for maximizing data being processed with available memory during downsample phase
        
        # Makes store location and initial group
        # do not make a class attribute because it may not pickle when computing over dask

        store = self.get_store_from_path(self.out_location) # location: _builder_utils

        # Sanity check that we can open the store
        store = zarr.open(store)
        del store
        
        ##  LIST ALL FILES TO BE CONVERTED  ##
        filesList = []
        if isinstance(self.in_location, str) and os.path.splitext(self.in_location)[-1] == '.nii':
            filesList.append(self.nifti_unpacker(self.in_location))

        elif isinstance(self.in_location, str) and self.fileType == 'jp2':
            filesList = self.jp2_unpacker(natsorted(glob.glob(os.path.join(self.in_location,'*.{}'.format(self.fileType)))))
        
        elif isinstance(self.in_location,(list,tuple)):
            # Can designate each directory with image files
            for ii in self.in_location:
                filesList.append(natsorted(glob.glob(os.path.join(ii,'*.{}'.format(self.fileType)))))
        else:
            # Will find nested directories with image files
            ## Assume files are laid out as "color_dir/images"
            for ii in natsorted(glob.glob(os.path.join(self.in_location,'*'))):
                filesList.append(natsorted(glob.glob(os.path.join(ii,'*.{}'.format(self.fileType)))))
        
        # print(filesList)
        
        self.filesList = filesList
        self.Channels = len(self.filesList)
        self.TimePoints = 1
        # print(self.Channels)
        # print(self.filesList)
        
        
        if self.fileType == '.tif' or self.fileType == '.tiff':
            testImage = tiff_manager(self.filesList[0][0])
        else:
            testImage = self.read_image(self.filesList[0][0])
        self.dtype = testImage.dtype
        self.ndim = testImage.ndim
        self.shape_3d = (len(self.filesList[0]),*testImage.shape)
        
        self.shape = (self.TimePoints, self.Channels, *self.shape_3d)
        
        # self.pyramidMap = self.imagePyramidNum()
        self.pyramidMap = self.imagePyramidNum_converge_isotropic()
        
        self.build_zattrs()
            
    







