# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 09:46:38 2021

@author: alpha
"""

import os, glob, zarr, time, math, sys, shutil, random
import numpy as np
import dask
from dask.delayed import delayed
import dask.array as da
from skimage import io, img_as_float32, img_as_float64, img_as_uint, img_as_ubyte
# from skimage.transform import rescale, downscale_local_mean
# from skimage.filters import gaussian
from numcodecs import Blosc
from distributed import Client, progress, performance_report
from contextlib import contextmanager
from itertools import product
import psutil

# import h5py
# import hdf5plugin


'''
WORKING FOR ALL RESOLUTION LEVELS 
Fails on big datasets due to dask getting bogged down
Working with sef-contained delayed frunction, but small number of threads makes it slow
2x downsamples only
'''

from stack_to_multiscale_ngff.h5_shard_store import H5_Shard_Store
from stack_to_multiscale_ngff.tiff_manager import tiff_manager, tiff_manager_3d
from stack_to_multiscale_ngff.arg_parser import parser
from stack_to_multiscale_ngff import utils
# from Z:\cbiPythonTools\bil_api\converters\H5_zarr_store3 import H5Store

# Note that attempts to determine the amount of free mem does not work for SLURM allocation
# This parameter must be set manually when submitting jobs to reduce the risk of overrunning
# RAM allocation

class builder:
    
    def __init__(
            self,in_location,out_location,fileType='tif',
            geometry=(1,0.35,0.35),origionalChunkSize=(1,1,4,1024,1024),finalChunkSize=(1,1,128,128,128),
            cpu_cores=os.cpu_count(), sim_jobs=4, mem=int((psutil.virtual_memory().free/1024**3)*.8),
            compressor=Blosc(cname='zstd', clevel=9, shuffle=Blosc.BITSHUFFLE),
            zarr_store_type=H5_Shard_Store, tmp_dir='/local',
            verbose=False, performance_report=True, progress=False,
            verify_zarr_write=False, skip=False
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
        self.skip = skip
        
        self.res0_chunk_limit_GB = self.mem / self.cpu_cores / 2 #Fudge factor for maximizing data being processed with available memory during res0 conversion phase
        self.res_chunk_limit_GB = self.mem / self.cpu_cores / 1.5 #Fudge factor for maximizing data being processed with available memory during downsample phase
        
        # Makes store location and initial group
        # do not make a class attribute because it may not pickle when computing over dask
        if self.zarr_store_type == H5_Shard_Store:
            store = self.zarr_store_type(self.out_location,verbose=self.verbose)
        else:
            store = self.zarr_store_type(self.out_location)
        store = zarr.open(store)
        del store
        
        
        
        # os.makedirs(self.out_location,exist_ok=True)
        
        ##  LIST ALL FILES TO BE CONVERTED  ##
        filesList = []
        if isinstance(self.in_location, str) and os.path.splitext(self.in_location)[-1] == '.nii':
            filesList.append(self.nifti_unpacker(self.in_location))
        
        elif isinstance(self.in_location,(list,tuple)):
            # Can designate each directory with image files
            for ii in self.in_location:
                filesList.append(sorted(glob.glob(os.path.join(ii,'*.{}'.format(self.fileType)))))
        else:
            # Will find nested directories with image files
            ## Assume files are laid out as "color_dir/images"
            for ii in sorted(glob.glob(os.path.join(self.in_location,'*'))):
                filesList.append(sorted(glob.glob(os.path.join(ii,'*.{}'.format(self.fileType)))))
        
        # print(filesList)
        
        self.filesList = filesList
        self.Channels = len(self.filesList)
        self.TimePoints = 1
        # print(self.Channels)
        # print(self.filesList)
        
        
        if self.fileType == '.tif' or self.fileType == '.tiff':
            testImage = tiff_manager(self.filesList[0][0])
        else:
            testImage = self.read_file(self.filesList[0][0])
        self.dtype = testImage.dtype
        self.ndim = testImage.ndim
        self.shape_3d = (len(self.filesList[0]),*testImage.shape)
        
        self.shape = (self.TimePoints, self.Channels, *self.shape_3d)
        
        self.pyramidMap = self.imagePyramidNum()
        
        self.build_zattrs()
        
    @staticmethod
    def organize_by_groups(a_list,group_len):

        new = []
        working = []
        idx = 0
        for aa in a_list:
            working.append(aa)
            idx += 1
            
            if idx == group_len:
                new.append(working)
                idx = 0
                working = []
        
        if working != []:
            new.append(working)
        return new

    def determine_read_depth(self,storage_chunks,num_workers,z_plane_shape,chunk_limit_GB=1,cpu_number=os.cpu_count()):
        chunk_depth = storage_chunks[3]
        current_chunks = (storage_chunks[0],storage_chunks[1],storage_chunks[2],chunk_depth,z_plane_shape[1])
        current_size = math.prod(current_chunks)/1024**3
        print(current_size)
        if self.dtype == np.dtype('uint8'):
            pass
        elif self.dtype == np.dtype('uint16'):
            current_size *=2
        elif self.dtype == np.dtype('float32'):
            current_size *=4
        elif self.dtype == float:
            current_size *=8
        
        print(current_size)
        if current_size >= chunk_limit_GB:
            print('Bigger than chunk limit {}'.format(current_size))
            return chunk_depth
        
        while current_size <= chunk_limit_GB:
            chunk_depth += storage_chunks[3]
            current_chunks = (storage_chunks[0],storage_chunks[1],storage_chunks[2],chunk_depth,z_plane_shape[1])
            current_size = math.prod(current_chunks)/1024**3
            if self.dtype == np.dtype('uint8'):
                pass
            elif self.dtype == np.dtype('uint16'):
                current_size *=2
            elif self.dtype == np.dtype('float32'):
                current_size *=4
            elif self.dtype == float:
                current_size *=8
            
            print('next step chunk limit {}'.format(current_size))
            if chunk_depth >= z_plane_shape[0]:
                chunk_depth = z_plane_shape[0]
                break
        return chunk_depth
            
    
    @contextmanager
    def dist_client(self):
        # Code to acquire resource, e.g.:
        self.client = Client()
        try:
            yield
        finally:
            # Code to release resource, e.g.:
            self.client.close()
            self.client = None

    
    @staticmethod
    def read_file(fileName):
        return io.imread(fileName)
    
    def write_local_res(self,res):
        with Client(n_workers=self.sim_jobs,threads_per_worker=os.cpu_count()//self.sim_jobs) as client:
            self.write_resolution(res,client)
        
        
    
    def imagePyramidNum(self):
        '''
        Map of pyramids accross a single 3D color
        '''
        out_shape = self.shape_3d
        chunk = self.origionalChunkSize[2:]
        
        pyramidMap = {0:[out_shape,chunk]}
        
        chunk_change = (4,0.5,0.5)
        final_chunk_size = self.finalChunkSize[2:]
        
        
        current_pyramid_level = 0
        print((out_shape,chunk))
        
        
        while True:
            current_pyramid_level += 1
            out_shape = tuple([x//2 for x in out_shape])
            chunk = (
                chunk_change[0]*pyramidMap[current_pyramid_level-1][1][0],
                chunk_change[1]*pyramidMap[current_pyramid_level-1][1][1],
                chunk_change[2]*pyramidMap[current_pyramid_level-1][1][2]
                )
            chunk = [int(x) for x in chunk]
            chunk = (
                chunk[0] if chunk[0] <= final_chunk_size[0] else final_chunk_size[0],
                chunk[1] if chunk[1] >= final_chunk_size[1] else final_chunk_size[1],
                chunk[2] if chunk[2] >= final_chunk_size[2] else final_chunk_size[2]
                )
            pyramidMap[current_pyramid_level] = [out_shape,chunk]
                
            print((out_shape,chunk))
            
            # if all([x<y for x,y in zip(out_shape,chunk)]):
            #     del pyramidMap[current_pyramid_level]
            #     break
            # if any([x<y for x,y in zip(out_shape,chunk)]):
            #     del pyramidMap[current_pyramid_level]
            #     break
            
            # stop if any shape dimension is below 1 then delete pyramid level
            if any([x<2 for x in out_shape]):
                del pyramidMap[current_pyramid_level]
                break
            
            # stop if an x or y dim is less than chunk shape
            if any([x<y for x,y in zip(out_shape[1:],chunk[1:])]):
                break
        
            
        # for key in pyramidMap:
        #     new_chunk = [chunk if chunk <= shape else shape for shape,chunk in zip(pyramidMap[key][0],pyramidMap[key][1])]
        #     pyramidMap[key][1] = new_chunk
        
        print(pyramidMap)
        return pyramidMap
    
    
    @staticmethod
    def regular_path(path):
        return path.replace('\\','/')
    
    def dtype_convert(self,data):
        
        if self.dtype == data.dtype:
            return data
        
        if self.dtype == np.dtype('uint16'):
            return img_as_uint(data)
        
        if self.dtype == np.dtype('ubyte'):
            return img_as_ubyte(data)
        
        if self.dtype == np.dtype('float32'):
            return img_as_float32(data)
        
        if self.dtype == np.dtype(float):
            return img_as_float64(data)
        
        raise TypeError("No Matching dtype : Conversion not possible")
        
    
    def write_resolution_series(self,client):
        '''
        Make downsampled versions of dataset based on pyramidMap
        Requies that a dask.distribuited client be passed for parallel processing
        '''
        for res in range(len(self.pyramidMap)):
            self.write_resolution(res,client)
            
    
    def open_store(self,res):
        return zarr.open(self.get_store(res))
    
    def get_store(self,res):
        if self.zarr_store_type == H5_Shard_Store:
            print('Getting H5Store')
            store = self.zarr_store_type(self.scale_name(res),verbose=self.verbose,verify_write=self.verify_zarr_write)
            # store = H5Store(self.scale_name(res),verbose=2)
        else:
            print('Getting Other Store')
            store = self.zarr_store_type(self.scale_name(res))
        return store
    
    def scale_name(self,res):
        name = os.path.join(self.out_location,'scale{}'.format(res))
        print(name)
        return name
    
    # @staticmethod
    # def smooth(image):
    #     working = img_as_float32(image)
    #     working = gaussian(working,0.5)
    #     working = img_as_uint(working)
    #     return working
        
    
    def write_resolution(self,res,client):
        
        if self.skip:
            if os.path.exists(self.scale_name(res)):
                print('Skipping Resolution Level {} because it already exists'.format(res))
                return
        if res == 0:
            self.write_resolution_0(client)
            return
        
        out = self.down_samp(res,client)
        # During creation of res 1, the min and max is calculated for res 0
        # out is a list of tuple (min,max,channel)
        if res == 1:
            self.min = []
            self.max = []
            for ch in range(self.Channels):
                # Sort by channel
                tmp = [x[-1] for x in out if x[-1][-1] == ch]
                # Append vlues to list in channel order
                self.min.append( min([x[0] for x in tmp]) )
                self.max.append( max([x[1] for x in tmp]) )
            self.set_omero_window()
    
    
    def write_resolution_0(self,client):
        
        print('Building Virtual Stack')
        stack = []
        for color in self.filesList:
            
            s = self.organize_by_groups(color,self.origionalChunkSize[2])
            # test_image = tiff_manager(s[0][0]) #2D manager
            # chunk_depth = (test_image.shape[1]//4) - (test_image.shape[1]//4)%storage_chunks[3]
            # chunk_depth = self.determine_read_depth(self.origionalChunkSize,
            #                                         num_workers=self.sim_jobs,
            #                                         z_plane_shape=test_image.shape,
            #                                         chunk_limit_GB=self.res0_chunk_limit_GB)
            test_image = tiff_manager_3d(s[0])
            # optimum_chunks = utils.optimize_chunk_shape_3d(test_image.shape,test_image.chunks,test_image.dtype,self.res0_chunk_limit_GB)
            optimum_chunks = utils.optimize_chunk_shape_3d_2(test_image.shape,test_image.chunks,self.origionalChunkSize[2:],test_image.dtype,self.res0_chunk_limit_GB)
            test_image.chunks = optimum_chunks
            # ## TESTING PURPOSES ONLY
            # test_image.chunks = (test_image.chunks[0],test_image.chunks[1]//2,test_image.chunks[2]*2)
            print(test_image.shape)
            print(test_image.chunks)
            
            s = [test_image.clone_manager_new_file_list(x) for x in s]
            print(len(s))
            for ii in s:
                print(ii.chunks)
                print(len(ii.fileList))
            # print(s[-3].chunks)
            print('From_array')
            print(s[0].dtype)
            s = [da.from_array(x,chunks=x.chunks,name=False,asarray=False) for x in s]
            # print(s)
            print(len(s))
            s = da.concatenate(s)
            # s = da.stack(s)
            print(s)
            stack.append(s)
        stack = da.stack(stack)
        stack = stack[None,...]
    
    
        print(stack)
        
        store = self.get_store(0)
        
        z = zarr.zeros(stack.shape, chunks=self.origionalChunkSize, store=store, overwrite=True, compressor=self.compressor,dtype=stack.dtype)
        
        # print(client.run(lambda: os.environ["HDF5_USE_FILE_LOCKING"]))
        if self.performance_report:
            with performance_report(filename=os.path.join(self.out_location,'performance_res_0.html')):
                to_store = da.store(stack,z,lock=False, compute=False)
                to_store = client.compute(to_store)
                if self.progress:
                    progress(to_store)
                to_store = client.gather(to_store)
        else:
            to_store = da.store(stack,z,lock=False, compute=False)
            to_store = client.compute(to_store)
            if self.progress:
                progress(to_store)
            to_store = client.gather(to_store)
    
    @staticmethod
    def overlap_helper(start_idx, max_shape, read_len, overlap):
        '''
        For any axis, provide:
            start_idx : start location
            max_shape : length of axis
            read_len : how long should the read be
            overlap : maximum overlap value
        
        output : two tuples indicating: 
            (start,stop) : index along axis
            (overlap_neg,overlap_pos) : overlaping depth with adjacent chunk
        '''
        #determine z_start
        overlap_neg = overlap
        while start_idx-overlap_neg < 0:
            overlap_neg -= 1
            if overlap_neg == 0:
                break
        start = start_idx-overlap_neg
        # print(start)
        #determine z_stop
        overlap_pos = 0
        if start_idx+read_len >= max_shape:
            stop = max_shape-1
        else:
            while start_idx+read_len+overlap_pos < max_shape-1:
                overlap_pos += 1
                if overlap_pos == overlap:
                    break
            stop = start_idx+read_len+overlap_pos
        # print(stop)
        
        # read_loc = [(t,t+1),(c,c+1),(zstart,zstop)]
        # print(read_loc)
        # trim_overlap = [overlap_neg,overlap_pos]
        return ( (start,stop), (overlap_neg,overlap_pos) )
    
    @staticmethod
    def pad_3d_2x(image,info,final_pad=2):
        
        '''
        Force an array to be padded with mirrored data to a specific size (default 2)
        an 'info' dictionary must be provided with keys: 'z','y','x' where the second
        value is a tuple describing the overlap alreday present on the array.  The 
        overlap values should be between 0 and the 'final_pad'    
        
        {'z':[(2364,8245),(0,1)]}
        '''
        
        for idx,axis in enumerate(['z','y','x']):
            # print(idx)
            overlap_neg, overlap_pos = info[axis][1]
            # print(overlap_neg, overlap_pos)
            if overlap_neg < final_pad:
                if idx == 0:
                    new = image[0:final_pad-overlap_neg]
                    new = new[::-1] # Mirror output
                    # print(idx,new.shape)
                elif idx == 1:
                    new = image[:,0:final_pad-overlap_neg]
                    new = new[:,::-1] # Mirror output
                    # print(idx,new.shape)
                elif idx == 2:
                    new = image[:,:,0:final_pad-overlap_neg]
                    new = new[:,:,::-1] # Mirror output
                image = np.concatenate((new,image),axis=idx)
                
            if overlap_pos < final_pad:
                if idx == 0:
                    new = image[-final_pad+overlap_pos:]
                    new = new[::-1] # Mirror output
                    # print(idx,new.shape)
                elif idx == 1:
                    new = image[:,-final_pad+overlap_pos:]
                    new = new[:,::-1] # Mirror output
                    # print(idx,new.shape)
                elif idx == 2:
                    new = image[:,:,-final_pad+overlap_pos:]
                    new = new[:,:,::-1] # Mirror output
                    # print(idx,new.shape)
                image = np.concatenate((image,new),axis=idx)
        
        return image
    
    
    def local_mean_3d_downsample_2x(self,image):
        # dtype = image.dtype
        # print(image.shape)
        image = img_as_float32(image)
        canvas = np.zeros(
            (image.shape[0]//2,
            image.shape[1]//2,
            image.shape[2]//2),
            dtype = np.dtype('float32')
            )
        # print(canvas.shape)
        for z,y,x in product(range(2),range(2),range(2)):
            tmp = image[z::2,y::2,x::2][0:canvas.shape[0]-1,0:canvas.shape[1]-1,0:canvas.shape[2]-1]
            # print(tmp.shape)
            canvas[0:tmp.shape[0],0:tmp.shape[1],0:tmp.shape[2]] += tmp
            
        canvas /= 8
        return self.dtype_convert(canvas)
    
    
    def fast_mean_3d_downsample(self,from_path,to_path,info,minmax=False,idx=None,store=H5_Shard_Store):
        
        while True:
            correct = False
            if store == H5_Shard_Store:
                zstore = store(from_path, verbose=self.verbose,verify_write=self.verify_zarr_write)
                # zstore = H5_Shard_Store(from_path, verbose=self.verbose)
            else:
                zstore = store(from_path)
            
            zarray = zarr.open(zstore)
            
            # print('Reading location {}'.format(info))
            working = zarray[
                info['t'],
                info['c'],
                info['z'][0][0]:info['z'][0][1],
                info['y'][0][0]:info['y'][0][1],
                info['x'][0][0]:info['x'][0][1]
                ]
            
            # print('Read shape {}'.format(working.shape))
            while len(working.shape) > 3:
                working = working[0]
            # print('Axes Removed shape {}'.format(working.shape))
            
            del zarray
            del zstore
            
            working = self.dtype_convert(working)
            # Calculate min/max of input data
            if minmax:
                min, max = working.min(),working.max()
            working = self.pad_3d_2x(working,info,final_pad=2)
            working = self.local_mean_3d_downsample_2x(working)
            
            
            # print('Preparing to write')
            if store == H5_Shard_Store:
                zstore = store(to_path, verbose=self.verbose,verify_write=self.verify_zarr_write)
                # zstore = H5Store(to_path, verbose=self.verbose)
            else:
                zstore = store(to_path)
            
            zarray = zarr.open(zstore)
            # print(zarray.shape)
            # print('Writing Location {}'.format(info))
            # Write array trimmed of 1 value along all edges
            zarray[
                info['t'],
                info['c'],
                (info['z'][0][0]+info['z'][1][0])//2:(info['z'][0][1]-info['z'][1][1])//2, #Compensate for overlap in new array
                (info['y'][0][0]+info['y'][1][0])//2:(info['y'][0][1]-info['y'][1][1])//2, #Compensate for overlap in new array
                (info['x'][0][0]+info['x'][1][0])//2:(info['x'][0][1]-info['x'][1][1])//2  #Compensate for overlap in new array
                ] = working[1:-1,1:-1,1:-1]
            
            # print('Verifying Location {}'.format(info))
            # Imediately verify that the array was written is correctly
            correct = np.ndarray.all(
                zarray[
                info['t'],
                info['c'],
                (info['z'][0][0]+info['z'][1][0])//2:(info['z'][0][1]-info['z'][1][1])//2, #Compensate for overlap in new array
                (info['y'][0][0]+info['y'][1][0])//2:(info['y'][0][1]-info['y'][1][1])//2, #Compensate for overlap in new array
                (info['x'][0][0]+info['x'][1][0])//2:(info['x'][0][1]-info['x'][1][1])//2  #Compensate for overlap in new array
                ] == working[1:-1,1:-1,1:-1]
                )
            
            del zarray
            del zstore
        
            if correct:
                print('SUCCESS : {}'.format(info))
                break
            else:
                print('FAILURE : {}'.format(info))
        
        if correct and minmax:
            return idx,(min,max,info['c'])
        if correct and not minmax:
            return idx,
        if not correct:
            print('Not Correct')
            return False,
        return False,
    
    
    def determine_chunks_size_for_downsample(self,res):
        
        new_chunks = (self.pyramidMap[res][1])
        single_chunk_size = math.prod(new_chunks)
        
        if self.dtype == np.dtype('uint8'):
            factor = 1
        elif self.dtype == np.dtype('uint16'):
            factor = 2
        elif self.dtype == np.dtype('float32'):
            factor = 4
        elif self.dtype == float:
            factor = 8
            
            
        z = y = x = 1
        chunk_size = overlap_size = 0
        while True:
            
            if (chunk_size + overlap_size)/1024**3*factor > self.res_chunk_limit_GB:
                break
            
            z+=1
            cz = new_chunks[0]*z
            cy = new_chunks[1]*y
            cx = new_chunks[2]*x
            
            chunk_size = math.prod((cz,cy,cx))
            overlap_size = 2*single_chunk_size*y*z + 2*single_chunk_size*x*z + 2*single_chunk_size*x*y
            
            if (chunk_size + overlap_size)/1024**3*factor > self.res_chunk_limit_GB:
                z-=1
                break
            
            y+=1
            cz = new_chunks[0]*z
            cy = new_chunks[1]*y
            cx = new_chunks[2]*x
            
            chunk_size = math.prod((cz,cy,cx))
            overlap_size = 2*single_chunk_size*y*z + 2*single_chunk_size*x*z + 2*single_chunk_size*x*y
            
            if (chunk_size + overlap_size)/1024**3*factor > self.res_chunk_limit_GB:
                y-=1
                break
            
            x+=1
            cz = new_chunks[0]*z
            cy = new_chunks[1]*y
            cx = new_chunks[2]*x
            
            chunk_size = math.prod((cz,cy,cx))
            overlap_size = 2*single_chunk_size*y*z + 2*single_chunk_size*x*z + 2*single_chunk_size*x*y
            
            if (chunk_size + overlap_size)/1024**3*factor > self.res_chunk_limit_GB:
                x-=1
                break
        
        return z,y,x
        
        
    
    def down_samp(self,res,client):
        
        out_location = self.scale_name(res)
        parent_location = self.scale_name(res-1)
        
        print('Getting Parent Zarr as Dask Array')
        parent_array = self.open_store(res-1)
        print(parent_array.shape)
        new_array_store = self.get_store(res)
        
        new_shape = (self.TimePoints, self.Channels, *self.pyramidMap[res][0])
        print(new_shape)
        # new_chunks = (1, 1, 16, 512, 4096)
        new_chunks = (1, 1, *self.pyramidMap[res][1])
        print(new_chunks)
        
        
        
        new_array = zarr.zeros(new_shape, chunks=new_chunks, store=new_array_store, overwrite=True, compressor=self.compressor,dtype=self.dtype)
        print('new_array, {}, {}'.format(new_array.shape,new_array.chunks))
        # z = zarr.zeros(stack.shape, chunks=self.origionalChunkSize, store=store, overwrite=True, compressor=self.compressor,dtype=stack.dtype)
        

        to_run = []
        # Currently hardcoded - works well for 32core, 512GB RAM
        # 4^3 is the break even point for surface area == volume
        # Higher numbers are better to limt io
        zz,yy,xx = self.determine_chunks_size_for_downsample(res)
        z_depth = new_chunks[-3] * zz
        y_depth = new_chunks[-2] * yy
        x_depth = new_chunks[-1] * xx
        # print(z_depth)
        idx = 0
        idx_reference=[]
        for t in range(self.TimePoints):
            for c in range(self.Channels):
                
                ## How to deal with overlap?
                overlap = 2
                for y in range(0,parent_array.shape[-2],y_depth):
                    y_info = self.overlap_helper(y, parent_array.shape[-2], y_depth, overlap)
                    for x in range(0,parent_array.shape[-1],x_depth):
                        x_info = self.overlap_helper(x, parent_array.shape[-1], x_depth, overlap)
                        for z in range(0,parent_array.shape[-3],z_depth):
                            z_info = self.overlap_helper(z, parent_array.shape[-3], z_depth, overlap)
                        
                            info = {
                                't':t,
                                'c':c,
                                'z':z_info,
                                'y':y_info,
                                'x':x_info
                                }
                            
                            # working = delayed(smooth_downsample)(parent_location,out_location,1,info,store=H5Store)
                            # working = delayed(local_mean_3d_downsample)(parent_location,out_location,info,store=H5Store)
                            if res == 1:
                                working = delayed(self.fast_mean_3d_downsample)(parent_location,out_location,info,minmax=True,idx=idx,store=self.zarr_store_type)
                            else:
                                working = delayed(self.fast_mean_3d_downsample)(parent_location,out_location,info,minmax=False,idx=idx,store=self.zarr_store_type)
                            print('{},{},{},{},{}'.format(t,c,z,y,x))
                            to_run.append(working)
                            idx_reference.append((idx,(parent_location,out_location,info)))
                            idx+=1
            
        random.seed(42)
        random.shuffle(to_run)
        random.seed(42)
        random.shuffle(idx_reference)
        
        if self.performance_report:
            with performance_report(filename=os.path.join(self.out_location,'performance_res_{}.html'.format(res))):
                future = client.compute(to_run)
                if self.progress:
                    progress(future)
                future = client.gather(future)
        else:
            future = client.compute(to_run)
            if self.progress:
                progress(future)
            future = client.gather(future)
        
        future_tmp = future
        
        while True:
            result_idx = [x[0] for x in future]
            reference_idx = [x[0] for x in idx_reference]
            print('Completed # {} : Queued # {}'.format(len(result_idx),len(reference_idx)))
            re_process = []
            for ii in reference_idx:
                if ii not in result_idx:
                    tmp = [x for x in idx_reference if x[0] == ii]
                    re_process.append(tmp[0])
                    print('Missing {}'.format(tmp[0]))
            if re_process == []:
                print('None missing: continuing')
                # x = input('Enter your name:')
                break
            
            idx_reference = []
            to_run = []
            for ii in re_process:
                if res == 1:
                    working = delayed(self.fast_mean_3d_downsample)(ii[1][0],ii[1][1],ii[1][2],minmax=True,idx=ii[0],store=self.zarr_store_type)
                else:
                    working = delayed(self.fast_mean_3d_downsample)(ii[1][0],ii[1][1],ii[1][2],minmax=False,idx=ii[0],store=self.zarr_store_type)
                to_run.append(working)
                idx_reference.append(ii)
            
            print(to_run)
            print('requing {} jobs'.format(len(to_run)))
            # x = input('Enter your name:')
            future = client.compute(to_run)
            if self.progress:
                progress(future)
            future = client.gather(future)
            
            future_tmp = future_tmp + future
            
        future = future_tmp
        future = [x for x in future if isinstance(x,tuple) and not isinstance(x[0],bool)]
        
        return future
    
    
    def build_zattrs(self):
        
        store = self.zarr_store_type(self.out_location,verbose=1)
        r = zarr.open(store)
        print(r)
        
        multiscales = {}
        multiscales["version"] = "0.5-dev"
        multiscales["name"] = "a dataset"
        multiscales["axes"] = [
            {"name": "t", "type": "time", "unit": "millisecond"},
            {"name": "c", "type": "channel"},
            {"name": "z", "type": "space", "unit": "micrometer"},
            {"name": "y", "type": "space", "unit": "micrometer"},
            {"name": "x", "type": "space", "unit": "micrometer"}
            ]


        # datasets = [] 
        # for res in self.pyramidMap:
        #     scale = {}
        #     scale["path"] = 'scale{}'.format(res)
        #     scale["coordinateTransformations"] = [{
        #         "type": "scale",
        #         "scale": [
        #             1, 1,
        #             round(self.geometry[2]*(res+1)**2,3),
        #             round(self.geometry[3]*(res+1)**2,3),
        #             round(self.geometry[4]*(res+1)**2,3)
        #             ]
        #         }]
            
        #     datasets.append(scale)
            
        datasets = [] 
        for res in self.pyramidMap:
            scale = {}
            scale["path"] = 'scale{}'.format(res)
            
            z=self.geometry[2]
            y=self.geometry[3]
            x=self.geometry[4]
            
            for _ in range(res):
                z *= 2
                y *= 2
                x *= 2
                
            scale["coordinateTransformations"] = [{
                "type": "scale",
                "scale": [
                    1, 1,
                    round(z,3),
                    round(y,3),
                    round(x,3)
                    ]
                }]
            
            datasets.append(scale)

        multiscales["datasets"] = datasets

        # coordinateTransformations = [{
        #                 # the time unit (0.1 milliseconds), which is the same for each scale level
        #                 "type": "scale",
        #                 "scale": [
        #                     1.0, 1.0, 
        #                     round(self.geometry[0],3),
        #                     round(self.geometry[1],3),
        #                     round(self.geometry[2],3)
        #                     ]
        #             }]

        # multiscales["coordinateTransformations"] = coordinateTransformations

        multiscales["type"] = 'mean'

        multiscales["metadata"] = {
                        "description": "local mean",
                        "any": "other",
                        "details": "here"
                    }

        
        r.attrs['multiscales'] = [multiscales]

        omero = {}
        omero['id'] = 1
        omero['name'] = "a dataset"
        omero['version'] = "0.5-dev"

        colors = [
            'FF0000', #red
            '00FF00', #green
            'FF00FF', #purple
            'FF00FF'  #blue
            ]
        colors = colors*self.Channels
        colors = colors[:self.Channels]

        channels = []
        for chn,clr in zip(range(self.Channels),colors):
            new = {}
            new["active"] = True
            new["coefficient"] = 1
            new["color"] = clr
            new["family"] = "linear"
            new['inverted'] = False
            new['label'] = "Channel{}".format(chn)
            
            if self.dtype==np.dtype('uint8'):
                end = mx = 255
            elif self.dtype==np.dtype('uint16'):
                end = mx = 65535
            elif self.dtype==float:
                end = mx = 1
            
            new['window'] = {
                "end": end, #Get max value of a low resolution series
                "max": mx, #base on dtype
                "min": 0, #base on dtype
                "start": 0 #Get min value of a low resolution series
                }
            
            channels.append(new)
            
        omero['channels'] = channels
        
        omero['rdefs'] = {
            "defaultT": 0,                    # First timepoint to show the user
            "defaultZ": self.shape[2]//2,     # First Z section to show the user
            "model": "color"                  # "color" or "greyscale"
            }
        
        r.attrs['omero'] = omero
        
        return
    
    def edit_omero_channels(self,channel_num,attr_name,new_value):
        store = self.zarr_store_type(self.out_location,verbose=1)
        r = zarr.open(store)
        
        omero = r.attrs['omero']
        
        channels = omero['channels']
        
        channels[channel_num][attr_name] = new_value
        
        omero['channels'] = channels
        
        r.attrs['omero'] = omero
        
    
    def get_omero_attr(self,attr_name):
        store = self.zarr_store_type(self.out_location,verbose=1)
        r = zarr.open(store)
        
        omero = r.attrs['omero']
        
        return omero[attr_name]
        
    # def edit_omero_channels(channel_num,attr_name,new_value):
    #     store = zarr.DirectoryStore(r'Z:\toTest\testZarr')
    #     r = zarr.open(store)
        
    #     omero = r.attrs['omero']
        
    #     channels = omero['channels']
        
    #     channels[channel_num][attr_name] = new_value
        
        
    #     r.attrs['omero'] = channels
    
    
    def set_omero_window(self):
        
        channels = self.get_omero_attr('channels')
        print(channels)
        for ch in range(self.Channels):
            #set in write_resolution()
            print(ch)
            channel_dict = channels[ch]
            print(channel_dict)
            window = channel_dict['window']
            print(window)
            window['start'] = self.min[ch]
            window['end'] = self.max[ch]
            print(window)
            self.edit_omero_channels(channel_num=ch,attr_name='window',new_value=window)
        
        
    def nifti_unpacker(self,file):
        
        import nibabel as nib
        from skimage import io, img_as_uint, img_as_float32
        import numpy as np

        # file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_rawdata.nii"
        # file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_avg_dwi.nii"

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
        
        data = data[::-1,::-1,::-1]
        tmp_img_dir = os.path.join(self.tmp_dir,'img')
        os.makedirs(tmp_img_dir,exist_ok=True)
        
        #Remove any existing files
        filelist = glob.glob(os.path.join(tmp_img_dir, "**/**"))
        for f in filelist:
            try:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)
            except Exception:
                pass
        
        for idx,ii in enumerate(data):
            idx = str(idx).zfill(4)
            fname = 'nii_layer_{}.tif'.format(idx)
            fname = os.path.join(tmp_img_dir,fname)
            print('Writing file {}'.format(fname))
            io.imsave(fname,ii)
        
        return sorted(glob.glob(os.path.join(tmp_img_dir, "*")))

        



if __name__ == '__main__':
    
    start = time.time()
    
    args = parser.parse_args()
    print(args)
    in_location = args.input
    if len(in_location) == 1:
        in_location = in_location[0]
    out_location = args.output[0]
    
    origionalChunkSize = args.origionalChunkSize
    finalChunkSize = args.finalChunkSize
    cpu = args.cpu[0]
    mem = args.mem[0]
    verbose = args.verbose
    tmp_dir = args.tmpLocation[0]
    fileType = args.fileType[0]
    scale = args.scale
    verify_zarr_write = args.verify_zarr_write
    skip = args.skip
    
    compressor = Blosc(cname='zstd', clevel=args.clevel[0], shuffle=Blosc.BITSHUFFLE)
    
    
    mr = builder(in_location, out_location, fileType=fileType, 
            geometry=scale,origionalChunkSize=origionalChunkSize, finalChunkSize=finalChunkSize,
            cpu_cores=cpu, mem=mem, tmp_dir=tmp_dir,verbose=verbose,compressor=compressor,
            verify_zarr_write=verify_zarr_write, skip=skip)
    
    

    
    
    # print(in_location)
    # print(out_location)
    # exit()
    
    # in_location = 'h:/globus/pitt/bil/TEST'
    
    # out_location = 'z:/testData/test_zarr'
    
    # in_location = '/CBI_Hive/globus/pitt/bil/TEST'
    
    # out_location = '/CBI_FastStore/testData/test_zarr2'
        
    
    # # mr = builder(in_location,out_location,tmp_dir='/bil/users/awatson/test_conv/tmp')
    # mr = builder(in_location,out_location,fileType=fileType,tmp_dir=tmp_dir,)
    
    
    # # 4 workers per core = 20 workers with lnode of 80 cores
    # # 4 Threads per workers
    with dask.config.set({'temporary_directory': mr.tmp_dir}):
            
        # with Client(n_workers=sim_jobs,threads_per_worker=os.cpu_count()//sim_jobs) as client:
        # with Client(n_workers=8,threads_per_worker=2) as client:
        workers = mr.workers
        threads = mr.sim_jobs
        # os.environ["DASK_DISTRIBUTED__COMM__TIMEOUTS__CONNECT"] = "60s"
        # os.environ["DASK_DISTRIBUTED__COMM__TIMEOUTS__TCP"] = "60s"
        # os.environ["DASK_DISTRIBUTED__DEPLOY__LOST_WORKER"] = "60s"
        
        #https://github.com/dask/distributed/blob/main/distributed/distributed.yaml#L129-L131
        os.environ["DISTRIBUTED__COMM__TIMEOUTS__CONNECT"] = "60s"
        os.environ["DISTRIBUTED__COMM__TIMEOUTS__TCP"] = "60s"
        os.environ["DISTRIBUTED__DEPLOY__LOST_WORKER"] = "60s"
        print('workers {}, threads {}, mem {}, chunk_size_limit {}'.format(workers, threads, mr.mem, mr.res0_chunk_limit_GB))
        # with Client(n_workers=workers,threads_per_worker=threads,memory_target_fraction=0.95,memory_limit='60GB') as client:
        with Client(n_workers=workers,threads_per_worker=threads) as client:
            
            mr.write_resolution_series(client)
            # mr.down_samp(1,client)
            
            # Need to take the min/max data collected during res1 creation and edit zattrs
    
    #Clean up
    #Remove any existing files
    filelist = glob.glob(os.path.join(mr.tmp_dir, "**/**"))
    for f in filelist:
        try:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f)
        except Exception:
            pass

    stop = time.time()
    print((stop - start)/60/60)
    
    sys.exit(0)
    
## https://download.brainimagelibrary.org/2b/da/2bdaf9e66a246844/mouseID_405429-182725/
## /bil/data/2b/da/2bdaf9e66a246844/mouseID_405429-182725/

    