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
from stack_to_multiscale_ngff.tiff_manager import tiff_manager


# file = r'C:\code\testData\191817_05308_CH1.tif'
# file = r'H:\globus\pitt\bil\fMOST RAW\CH1\182725_03717_CH1.tif'


## Import mix-in classes
from stack_to_multiscale_ngff._builder_utils import _builder_utils
from stack_to_multiscale_ngff._builder_ome_zarr_utils import _builder_ome_zarr_utils
from stack_to_multiscale_ngff._builder_image_utils import _builder_image_utils
from stack_to_multiscale_ngff._builder_multiscale_generator import _builder_multiscale_generator

class builder(_builder_utils,
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
            compressor=None,
            ngff_version=0.6, shard_shape=None, tmp_dir='/local',
            verbose=False, performance_report=False, progress=False,
            omero_dict={},
            skip=False,
            downSampType='mean',
            directToFinalChunks=False,
            buildTmpCopyDestination=False,
            multi_scale_compressor=None
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
        assert ngff_version in (0.4, 0.5, 0.6), 'ngff_version must be 0.4, 0.5 or 0.6'
        self.ngff_version = ngff_version
        # NGFF 0.4 is stored as zarr v2; NGFF 0.5 and 0.6 are stored as zarr v3
        self.zarr_format = 2 if ngff_version == 0.4 else 3
        self.shard_shape = tuple(shard_shape) if shard_shape is not None else None
        self.tmp_dir = tmp_dir
        self.verbose = verbose
        self.performance_report = performance_report
        self.progress = progress
        self.omero_dict = omero_dict
        self.skip = skip
        self.downSampType = downSampType
        self.directToFinalChunks = directToFinalChunks
        self.buildTmpCopyDestination = buildTmpCopyDestination

        # Default compressor depends on the output zarr format
        if compressor is None:
            if self.zarr_format == 3:
                from zarr.codecs import BloscCodec
                compressor = BloscCodec(cname='zstd', clevel=5, shuffle='bitshuffle')
            else:
                compressor = Blosc(cname='zstd', clevel=5, shuffle=Blosc.BITSHUFFLE)
        self.compressor = compressor

        # Hack to build zarr in tmp location then copy to finalLocation (finalLocation is the original out_location)
        self.finalLocation = self.out_location
        if self.buildTmpCopyDestination:
            # Change out_location to tmp location so that build happens here.
            self.out_location = os.path.join(self.tmp_dir,'build_location',os.path.split(self.out_location)[-1])
        
        # Option to have a different compressor for multiscales defaults to self.compressor
        if multi_scale_compressor is None:
            self.multi_scale_compressor = self.compressor
        else:
            self.multi_scale_compressor = multi_scale_compressor

        self.res0_chunk_limit_GB = self.mem / self.cpu_cores / 8 #Fudge factor for maximizing data being processed with available memory during res0 conversion phase
        self.res_chunk_limit_GB = self.mem / self.cpu_cores / 24 #Fudge factor for maximizing data being processed with available memory during downsample phase

        # Default shard shape: 4x the largest chunk along z and the largest
        # chunk along y/x. Keeps shard size reasonable while ensuring the
        # shard is a multiple of every level's chunk shape.
        if self.shard_shape is None and self.zarr_format == 3:
            max_chunk = [max(self.origionalChunkSize[d], self.finalChunkSize[d]) for d in (2, 3, 4)]
            self.shard_shape = (1, 1, max_chunk[0] * 4, max_chunk[1], max_chunk[2])
        self._validate_shard_shape()

        ##  Create the root group  ##
        # do not make a class attribute because it may not pickle when computing over dask
        try:
            zarr.open_group(self.out_location, mode='w-', zarr_format=self.zarr_format)
        except FileExistsError:
            if self.skip:
                zarr.open_group(self.out_location, mode='r+', zarr_format=self.zarr_format)
            else:
                raise FileExistsError(
                    'Output location already exists: {}. Use -sk/--skip to resume an existing '
                    'conversion or remove the output directory.'.format(self.out_location))
        
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

        elif len(glob.glob(os.path.join(self.in_location,'*.{}'.format(self.fileType)))) > 0:
            filesList.append(
                natsorted(glob.glob(os.path.join(self.in_location, '*.{}'.format(self.fileType))))
            )

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

        # OME-Zarr metadata is published only after all resolution levels
        # finish writing (see builder.py). Aborted output is not advertised
        # as a complete multiscale image.

    def _validate_shard_shape(self):
        '''
        Ensure the shard shape is usable for sharded zarr v3 output:
        5 integers (TCZYX), 1 along time and channel, and a multiple of the
        largest chunk size used across resolution levels along each spatial axis.
        '''
        if self.shard_shape is None:
            return
        if len(self.shard_shape) != 5:
            raise ValueError('shard_shape must be 5 integers for axes (TCZYX), got {}'.format(self.shard_shape))
        for dim in (0, 1):
            if self.shard_shape[dim] != 1:
                raise ValueError('Shard size along time (T) and channel (C) axes must be 1, got {}'.format(self.shard_shape[dim]))
        for dim in (2, 3, 4):
            max_chunk = max(self.origionalChunkSize[dim], self.finalChunkSize[dim])
            if self.shard_shape[dim] % max_chunk != 0:
                raise ValueError(
                    'Shard size {} along axis {} must be a multiple of the largest chunk size {} '
                    'used across resolution levels'.format(self.shard_shape[dim], 'zyx'[dim - 2], max_chunk))
            
    







