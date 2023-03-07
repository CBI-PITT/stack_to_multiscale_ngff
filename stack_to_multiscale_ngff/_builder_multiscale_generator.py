# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 12:46:17 2023

@author: awatson
"""

'''
Store mix-in classes for utilities

These classes are designed to be inherited by the builder class (builder.py)
'''

import os
import random
import zarr
from dask.delayed import delayed
import dask.array as da
from distributed import Client, progress, performance_report

# Project specific imports 
from stack_to_multiscale_ngff._builder_image_utils import tiff_manager_3d
from stack_to_multiscale_ngff import utils

class _builder_multiscale_generator:
    
    def write_resolution_series(self):
        '''
        Make downsampled versions of dataset based on pyramidMap
        Requies that a dask.distribuited client be passed for parallel processing
        '''
        for res in range(len(self.pyramidMap)):
            with Client(n_workers=self.workers,threads_per_worker=self.sim_jobs) as client:
                self.write_resolution(res,client)
    
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
    
    
    def down_samp(self,res,client):
        
        out_location = self.scale_name(res)
        parent_location = self.scale_name(res-1)
        
        print('Getting Parent Zarr as Dask Array')
        parent_array = self.open_store(res-1)
        print(parent_array.shape)
        new_array_store = self.get_store(res)
        
        new_shape = (self.TimePoints, self.Channels, *self.pyramidMap[res]['shape'])
        print(new_shape)
        # new_chunks = (1, 1, 16, 512, 4096)
        new_chunks = (1, 1, *self.pyramidMap[res]['chunk'])
        print(new_chunks)
        
        
        
        new_array = zarr.zeros(new_shape, chunks=new_chunks, store=new_array_store, overwrite=True, compressor=self.compressor,dtype=self.dtype)
        print('new_array, {}, {}'.format(new_array.shape,new_array.chunks))
        
        # if self.pyramidMap[res]['downsamp'] == (2,2,2):
        #     dsamp_algo = self.fast_3d_downsample
        # elif self.pyramidMap[res]['downsamp'] == (1,2,2):
        #     dsamp_algo = self.fast_2d_downsample
        # else:
        #     raise TypeError('Only 3D <2,2,2> and 2D <1,2,2> down samples for axes (z,y,x) are currently supported')
        dsamp_algo = self.fast_downsample

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
                                working = delayed(dsamp_algo)(parent_location,out_location,info,minmax=True,idx=idx,store=self.zarr_store_type,down_sample_ratio=self.pyramidMap[res]['downsamp'])
                            else:
                                working = delayed(dsamp_algo)(parent_location,out_location,info,minmax=False,idx=idx,store=self.zarr_store_type,down_sample_ratio=self.pyramidMap[res]['downsamp'])
                            print('{},{},{},{},{}'.format(t,c,z,y,x))
                            to_run.append(working)
                            idx_reference.append((idx,(parent_location,out_location,info)))
                            idx+=1
            
        random.seed(42)
        random.shuffle(to_run)
        random.seed(42)
        random.shuffle(idx_reference)
        print('Computing {} chunks'.format(len(to_run)))
        
        if self.performance_report:
            with performance_report(filename=os.path.join(self.out_location,'performance_res_{}.html'.format(res))):
                future = self.compute_batch(to_run,round(self.cpu_cores*1.25),client)
        else:
            future = self.compute_batch(to_run,round(self.cpu_cores*1.25),client)
        
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
                    working = delayed(dsamp_algo)(ii[1][0],ii[1][1],ii[1][2],minmax=True,idx=ii[0],store=self.zarr_store_type)
                else:
                    working = delayed(dsamp_algo)(ii[1][0],ii[1][1],ii[1][2],minmax=False,idx=ii[0],store=self.zarr_store_type)
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