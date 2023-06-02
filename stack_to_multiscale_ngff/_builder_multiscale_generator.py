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
import time
import math
from itertools import product
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

        # During creation of res 1, the min and max is calculated for res 0 if values
        # for omero window were not specified in the commandline
        # These values are added to zattrs omero:channels
        # out is a list of tuple (min,max,channel)

        # out = self.down_samp_by_chunk_no_overlap(res, client, minmax=False)

        minmax = False
        where_to_calculate_min_max = 2
        if len(self.pyramidMap) == 2 and res == 1:
            minmax = True
        elif res == len(self.pyramidMap) // where_to_calculate_min_max:
            minmax = True
        elif len(self.pyramidMap) // where_to_calculate_min_max == 0:
            minmax = True


        results = self.down_samp_by_chunk_no_overlap(res, client, minmax=minmax)

        if minmax and self.omero_dict['channels']['window'] is None:
            self.min = []
            self.max = []
            for ch in range(self.Channels):
                print('Sorting Min/Max')
                # Sort by channel
                tmp = [x[-1] for x in results if x[-1][-1] == ch]
                print(tmp)
                # Append vlues to list in channel order
                self.min.append( min([x[0] for x in tmp]) )
                self.max.append( max([x[1] for x in tmp]) )
            print('Setting OMERO Window')
            self.set_omero_window()


        ## Old Method
        # if res == 1 and self.omero_dict['channels']['window'] is None:
        #     out = self.down_samp(res, client,minmax=True)
        #     self.min = []
        #     self.max = []
        #     for ch in range(self.Channels):
        #         # Sort by channel
        #         tmp = [x[-1] for x in out if x[-1][-1] == ch]
        #         # Append vlues to list in channel order
        #         self.min.append( min([x[0] for x in tmp]) )
        #         self.max.append( max([x[1] for x in tmp]) )
        #     self.set_omero_window()
        # else:
        #     out = self.down_samp(res, client, minmax=False)
    
    
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

    # def write_resolution_0(self, client):
    #
    #     '''
    #     Attempt to do single operation res 0 and res 1
    #     NOT WORKING NEED TO FIGURE CUT CHUNK ALIGNMENT AND COMPUTE
    #     '''
    #
    #     print('Building Virtual Stack')
    #     stack = []
    #     for color in self.filesList:
    #
    #         s = self.organize_by_groups(color, self.origionalChunkSize[2])
    #         # test_image = tiff_manager(s[0][0]) #2D manager
    #         # chunk_depth = (test_image.shape[1]//4) - (test_image.shape[1]//4)%storage_chunks[3]
    #         # chunk_depth = self.determine_read_depth(self.origionalChunkSize,
    #         #                                         num_workers=self.sim_jobs,
    #         #                                         z_plane_shape=test_image.shape,
    #         #                                         chunk_limit_GB=self.res0_chunk_limit_GB)
    #         test_image = tiff_manager_3d(s[0])
    #         # optimum_chunks = utils.optimize_chunk_shape_3d(test_image.shape,test_image.chunks,test_image.dtype,self.res0_chunk_limit_GB)
    #         optimum_chunks = utils.optimize_chunk_shape_3d_2(test_image.shape, test_image.chunks,
    #                                                          self.origionalChunkSize[2:], test_image.dtype,
    #                                                          self.res0_chunk_limit_GB)
    #         test_image.chunks = optimum_chunks
    #         # ## TESTING PURPOSES ONLY
    #         # test_image.chunks = (test_image.chunks[0],test_image.chunks[1]//2,test_image.chunks[2]*2)
    #         print(test_image.shape)
    #         print(test_image.chunks)
    #
    #         s = [test_image.clone_manager_new_file_list(x) for x in s]
    #         print(len(s))
    #         for ii in s:
    #             print(ii.chunks)
    #             print(len(ii.fileList))
    #
    #         stack.append(s)
    #
    #     # print(s[-3].chunks)
    #     print('From_array')
    #     print(s[0].dtype)
    #     stack = tiff_manager_3d_to_5d(stack)
    #
    #     print(stack)
    #
    #     # Create fullres zarr
    #     store = self.get_store(0)
    #
    #     z = zarr.zeros(stack.shape, chunks=self.origionalChunkSize, store=store, overwrite=True,
    #                    compressor=self.compressor, dtype=stack.dtype)
    #
    #     # Create res 1 zarr
    #     storeds = self.get_store(1)
    #
    #     ds = zarr.zeros(self.pyramidMap[1]['shape'], chunks=self.pyramidMap[1]['chunk'], store=storeds, overwrite=True,
    #                    compressor=self.compressor, dtype=stack.dtype)
    #
    #     down_sample_ratio = self.pyramidMap[1]['downsamp']
    #     align_chunks_for_ds = [x//y for x,y in zip(stack.chunks[2:],down_sample_ratio)]
    #     align_chunks_for_ds = [x if x<y else y for x,y in zip(align_chunks_for_ds,ds.shape[2:])]
    #
    #     slices = self.chunk_slice_generator_for_downsample((stack.shape,stack.chunks), (ds.shape,align_chunks_for_ds),
    #                                                        down_sample_ratio=down_sample_ratio, length=True)
    #     total_slices = len(tuple(slices))
    #     slices = self.chunk_slice_generator_for_downsample((stack.shape, stack.chunks), (ds.shape, align_chunks_for_ds),
    #                                                        down_sample_ratio=down_sample_ratio, length=True)
    #
    #     num = 0
    #     processing = []
    #     start = time.time()
    #     final_results = []
    #     for from_slice, to_slice in slices:
    #         # print(from_slice)
    #         # print(to_slice)
    #         num += 1
    #         if num % 100 == 1:
    #             mins_per_chunk = (time.time() - start) / num / 60
    #             mins_remaining = (total_slices - num) * mins_per_chunk
    #             mins_remaining = round(mins_remaining, 2)
    #             print(f'Computing chunks {num} of {total_slices} : {mins_remaining} mins remaining', end='\r')
    #         else:
    #             print(f'Computing chunks {num} of {total_slices} : {mins_remaining} mins remaining', end='\r')
    #         tmp = delayed(self.downsample_by_chunk)(res - 1, res, down_sample_ratio, from_slice, to_slice,
    #                                                 minmax=minmax)
    #         tmp = client.compute(tmp)
    #         processing.append(tmp)
    #         del tmp
    #         results, processing = self.compute_govenor(processing, num_at_once=round(self.cpu_cores * 4),
    #                                                    complete=False, keep_results=minmax)
    #
    #         final_results = final_results + results
    #
    #     results, processing = self.compute_govenor(processing, num_at_once=round(self.cpu_cores * 4), complete=True,
    #                                                keep_results=minmax)
    #     final_results = final_results + results
    #
    #     if minmax:
    #         print('                                                                                      ', end='\r')
    #         print('Gathering Results')
    #         final_results = client.gather(final_results)
    #         # return final_results
    #
    #     return final_results
    
    def down_samp(self,res,client,minmax=False):
        
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

        # Other downsample methods could be substituted here
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

    ##############################################################################################################
    '''
    Functions below are newer downsample control for chunk-by-chunk method
    '''
    ##############################################################################################################


    def downsample_by_chunk(self, from_res, to_res, down_sample_ratio, from_slice, to_slice, minmax=False):

        '''
        Slices are for dims (t,c,z,y,x), downsamp only works on 3 dims
        '''

        # Run proper downsampling method
        if self.downSampType == 'mean':
            dsamp_method = self.local_mean_downsample
        elif self.downSampType == 'max':
            dsamp_method = self.local_max_downsample
        # print(self.downSampType)
        # dsamp_method = self.local_mean_downsample

        from_array = self.open_store(from_res)
        to_array = self.open_store(to_res)

        data = from_array[from_slice]

        # Calculate min/max of input data
        if minmax:
            min, max = data.min(), data.max()

        data = data[0,0]
        data = dsamp_method(data,down_sample_ratio=down_sample_ratio)
        data = data[None, None, ...]
        to_array[to_slice] = data
        if minmax:
            return True, (min, max, from_slice[1].start)
        else:
            return True,


    # def chunk_increase_to_limit_3d(self,image_shape,starting_chunks,chunk_limit_in_GB):
    #
    #     # Determine chunk values to start at
    #     z = starting_chunks[0] if starting_chunks[0] < image_shape[0] else image_shape[0]
    #     y = starting_chunks[1] if starting_chunks[1] < image_shape[1] else image_shape[1]
    #     x = starting_chunks[2] if starting_chunks[2] < image_shape[2] else image_shape[2]
    #
    #     previous_chunks = (z,y,x)
    #     current_chunks = (z,y,x)
    #
    #     # Iterate 1 axis at a time increasing chunk size by increase_rate until the chunk_limit_in_MB is reached
    #     idx=0
    #     while True:
    #         print(f'First chunks to try {current_chunks}')
    #         if utils.get_size_GB(current_chunks,self.dtype) >= chunk_limit_in_GB:
    #             current_chunks = previous_chunks
    #             print(f'Final chunk to process {current_chunks}')
    #             break
    #         else:
    #             previous_chunks = current_chunks
    #
    #         if idx%3 == 0:
    #             z = z + starting_chunks[0] if starting_chunks[0] < image_shape[0] else image_shape[0]
    #         if idx%3 == 1:
    #             y = y + starting_chunks[1] if starting_chunks[1] < image_shape[1] else image_shape[1]
    #         if idx%3 == 2:
    #             x = x + starting_chunks[2] if starting_chunks[2] < image_shape[2] else image_shape[2]
    #
    #         current_chunks = (z,y,x)
    #         idx+=1
    #
    #     return current_chunks


    def chunk_increase_to_limit_3d(self,image_shape,starting_chunks,chunk_limit_in_GB):

        # Determine chunk values to start at
        z = starting_chunks[0] if starting_chunks[0] < image_shape[0] else image_shape[0]
        y = starting_chunks[1] if starting_chunks[1] < image_shape[1] else image_shape[1]
        x = starting_chunks[2] if starting_chunks[2] < image_shape[2] else image_shape[2]

        previous_chunks = (z,y,x)
        current_chunks = (z,y,x)

        # Iterate 1 axis at a time increasing chunk size by increase_rate until the chunk_limit_in_MB is reached
        while True:
            print(f'Current chunk to try {current_chunks}')
            if utils.get_size_GB(current_chunks,self.dtype) >= chunk_limit_in_GB:
                current_chunks = previous_chunks
                print(f'Final chunk to process {current_chunks}')
                break
            else:
                previous_chunks = current_chunks

            if z < image_shape[0]:
                z = z + starting_chunks[0] if starting_chunks[0] < image_shape[0] else image_shape[0]
            elif y < image_shape[1]:
                y = y + starting_chunks[1] if starting_chunks[1] < image_shape[1] else image_shape[1]
            elif x < image_shape[2]:
                x = x + starting_chunks[2] if starting_chunks[2] < image_shape[2] else image_shape[2]
            else:
                break

            current_chunks = (z,y,x)

        return current_chunks

    # def chunk_increase_to_limit_3d(self,image_shape,starting_chunks,chunk_limit_in_GB):
    #
    #     # Determine chunk values to start at
    #     z = starting_chunks[0] if starting_chunks[0] < image_shape[0] else image_shape[0]
    #     y = starting_chunks[1] if starting_chunks[1] < image_shape[1] else image_shape[1]
    #     x = starting_chunks[2] if starting_chunks[2] < image_shape[2] else image_shape[2]
    #
    #     previous_chunks = (z,y,x)
    #     current_chunks = (z,y,x)
    #
    #     rank_dict = {}
    #     idx = 0
    #     for axis,chunk_size in enumerate((z,y,x), current_chunks):
    #         if chunk_size == min(current_chunks):
    #             rank_dict[0] = (axis,chunk_size)
    #         elif chunk_size == max(current_chunks):
    #             rank_dict[2] = (axis,chunk_size)
    #         else:
    #             rank_dict[1] = (axis, chunk_size)
    #
    #     # Iterate 1 axis at a time increasing by chunk size along the smallest chunk axis
    #     while True:
    #         print(f'First chunks to try {current_chunks}')
    #         if utils.get_size_GB(current_chunks,self.dtype) >= chunk_limit_in_GB:
    #             current_chunks = previous_chunks
    #             print(f'Final chunk to process {current_chunks}')
    #             break
    #         else:
    #             previous_chunks = current_chunks
    #
    #         if
    #         if z < image_shape[0]:
    #             z = z + starting_chunks[0] if starting_chunks[0] < image_shape[0] else image_shape[0]
    #         elif y < image_shape[1]:
    #             y = y + starting_chunks[1] if starting_chunks[1] < image_shape[1] else image_shape[1]
    #         elif x < image_shape[2]:
    #             x = x + starting_chunks[2] if starting_chunks[2] < image_shape[2] else image_shape[2]
    #
    #         current_chunks = (z,y,x)
    #
    #     return current_chunks


    def chunk_slice_generator_for_downsample(self,from_array, to_array, down_sample_ratio=(2, 2, 2), length=False):
        '''
        Generate slice for each chunk in array for shape and chunksize
        Also generate slices for each chunk for an array of 2x size in each dim.

        from_array:
            array-like obj with .chunksize or .chunks and .shape
            OR
            tuple of tuples ((),()) where index [0] == shape, index [1] == chunks
        to_array:
            array-like obj with .chunksize or .chunks and .shape
            OR
            tuple of tuples ((),()) where index [0] == shape, index [1] == chunks

        Assume dims are (t,c,z,y,x)
        downsample ratio is a tuple if int (z,y,x)
        '''
        if isinstance(to_array, tuple):
            chunksize = to_array[1]
            shape = to_array[0]
        else:
            try:
                chunksize = to_array.chunksize
            except:
                chunksize = to_array.chunks
            shape = to_array.shape

        if isinstance(from_array, tuple):
            from_chunksize = from_array[1]
            from_shape = from_array[0]
        else:
            try:
                from_chunksize = from_array.chunksize
            except:
                from_chunksize = from_array.chunks
            from_shape = from_array.shape

        # Chunks are calculated for to_array
        # optimum_chunks = self.chunk_increase_to_limit_3d(shape[2:],chunksize[2:],self.res_chunk_limit_GB // math.prod(down_sample_ratio) // 1)
        optimum_chunks = self.chunk_increase_to_limit_3d(shape[2:], chunksize[2:],
                                                         self.res_chunk_limit_GB)

        chunksize = list(chunksize[:2]) + list(optimum_chunks)
        print(f'Chunksize for processing downsampled array: {chunksize}')
        # chunk_multiply = 2
        # chunksize = list(chunksize[:2]) + [x*chunk_multiply for x in chunksize[-3:]]

        chunks = [x // y for x, y in zip(shape, chunksize)]
        chunk_mod = [x % y > 0 for x, y in zip(shape, chunksize)]
        chunks = [x + 1 if y else x for x, y in zip(chunks, chunk_mod)]

        reverse_chunks = chunks[::-1]
        reverse_chunksize = chunksize[::-1]
        reverse_shape = shape[::-1]
        reverse_from_shape = from_shape[::-1]

        # Tuple of 3 values
        reverse_downsample_ratio = down_sample_ratio[::-1]

        if length:
            yield from product(*map(range, reverse_chunks))
        else:
            for a in product(*map(range, reverse_chunks)):
                start = [x * y for x, y in zip(a, reverse_chunksize)]
                stop = [(x + 1) * y for x, y in zip(a, reverse_chunksize)]
                stop = [x if x < y else y for x, y in zip(stop, reverse_shape)]

                to_slices = [slice(x, y) for x, y in zip(start, stop)]
                # print(to_slices)

                start = [x * y for x,y in zip(start[:-2],reverse_downsample_ratio)] + start[-2:]
                stop = [x * y for x,y in zip(stop[:-2],reverse_downsample_ratio)] + stop[-2:]
                stop = [x if x < y else y for x, y in zip(stop, reverse_from_shape)]
                from_slices = [slice(x, y) for x, y in zip(start, stop)]
                # print(slices[::-1])
                yield tuple(from_slices[::-1]), tuple(to_slices[::-1])

    # @staticmethod
    # def compute_govenor(processing, num_at_once=70, complete=False):
    #     while len(processing) >= num_at_once:
    #         processing = [x for x in processing if x.status != 'finished']
    #         time.sleep(0.1)
    #     if complete:
    #         while len(processing) > 0:
    #             time.sleep(0.1)
    #             print(f'{len(processing)} remaining')
    #             processing = [x for x in processing if x.status != 'finished']
    #     return processing

    @staticmethod
    def compute_govenor(processing, num_at_once=70, complete=False, keep_results=False):
        results = []
        while len(processing) >= num_at_once:
            still_running = [x.status != 'finished' for x in processing]

            # Partition completed from processing
            if keep_results:
                results_tmp = [x for x,y in zip(processing,still_running) if not y]
                results = results + results_tmp
                del results_tmp
            processing = [x for x,y in zip(processing,still_running) if y]

            time.sleep(0.1)

        if complete:
            while len(processing) > 0:
                print('                                                                                      ',
                      end='\r')
                print(f'{len(processing)} remaining', end='\r')
                still_running = [x.status != 'finished' for x in processing]

                # Partition completed from processing
                if keep_results:
                    results_tmp = [x for x, y in zip(processing, still_running) if not y]
                    results = results + results_tmp
                    del results_tmp
                processing = [x for x, y in zip(processing, still_running) if y]

                time.sleep(0.1)
        return results, processing

    def down_samp_by_chunk_no_overlap(self, res, client, minmax=False):

        # out_location = self.scale_name(res)
        # parent_location = self.scale_name(res - 1)

        print('Getting Parent Zarr as Dask Array')
        parent_array = self.open_store(res - 1)
        print(parent_array.shape)
        new_array_store = self.get_store(res)

        new_shape = (self.TimePoints, self.Channels, *self.pyramidMap[res]['shape'])
        print(new_shape)
        # new_chunks = (1, 1, 16, 512, 4096)
        new_chunks = (1, 1, *self.pyramidMap[res]['chunk'])
        print(new_chunks)

        new_array = zarr.zeros(new_shape, chunks=new_chunks, store=new_array_store, overwrite=True,
                               compressor=self.compressor, dtype=self.dtype)
        print('new_array, {}, {}'.format(new_array.shape, new_array.chunks))

        from_array_shape_chunks = (
            (self.TimePoints,self.Channels,*self.pyramidMap[res-1]['shape']),
            (1,1,*self.pyramidMap[res-1]['chunk'])
        )
        to_array_shape_chunks = (
            (self.TimePoints,self.Channels,*self.pyramidMap[res]['shape']),
            (1,1,*self.pyramidMap[res]['chunk'])
        )

        down_sample_ratio = self.pyramidMap[res]['downsamp']

        slices = self.chunk_slice_generator_for_downsample(from_array_shape_chunks, to_array_shape_chunks,
                                                      down_sample_ratio=down_sample_ratio, length=True)
        total_slices = len(tuple(slices))
        slices = self.chunk_slice_generator_for_downsample(from_array_shape_chunks, to_array_shape_chunks,
                                                      down_sample_ratio=down_sample_ratio, length=False)
        num = 0
        processing = []
        start = time.time()

        final_results = []
        for from_slice, to_slice in slices:
            # print(from_slice)
            # print(to_slice)
            num+=1
            if num % 100 == 1:
                mins_per_chunk = (time.time() - start) / num / 60
                mins_remaining = (total_slices - num) * mins_per_chunk
                mins_remaining = round(mins_remaining, 2)
                print(f'Computing chunks {num} of {total_slices} : {mins_remaining} mins remaining', end='\r')
            else:
                print(f'Computing chunks {num} of {total_slices} : {mins_remaining} mins remaining', end='\r')
            tmp = delayed(self.downsample_by_chunk)(res-1, res, down_sample_ratio, from_slice, to_slice, minmax=minmax)
            tmp = client.compute(tmp)
            processing.append(tmp)
            del tmp
            results, processing = self.compute_govenor(processing, num_at_once=round(self.cpu_cores*4), complete=False, keep_results=minmax)

            final_results = final_results + results

        results, processing = self.compute_govenor(processing, num_at_once=round(self.cpu_cores*4), complete=True, keep_results=minmax)
        final_results = final_results + results

        if minmax:
            print('                                                                                      ',end='\r')
            print('Gathering Results')
            final_results = client.gather(final_results)
            # return final_results

        return final_results

