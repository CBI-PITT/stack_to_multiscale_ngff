# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 12:46:17 2023

@author: awatson
"""

'''
Store mix-in classes for utilities

These classes are designed to be inherited by the builder class (builder.py)
'''

import numpy as np
import os
import math
import time
import zarr
from skimage import io, img_as_uint, img_as_ubyte, img_as_float32, img_as_float64

class _builder_utils:
    
    
    def open_store(self,res):
        return zarr.open(self.get_store(res))
    
    def get_store(self,res):
        return self.get_store_from_path(self.scale_name(res))
    
    def get_store_from_path(self,path):
        try:
            if self.zarr_store_type == H5_Shard_Store:
                store = self.zarr_store_type(path,verbose=self.verbose,verify_write=self.verify_zarr_write,alternative_lock_file_path=self.tmp_dir)
            else:
                store = self.zarr_store_type(path)
        except:
            store = self.zarr_store_type(path)
        
        return store
    
    def scale_name(self,res):
        name = os.path.join(self.out_location,'scale{}'.format(res))
        print(name)
        return name
    
    @staticmethod
    def read_image(fileName):
        return io.imread(fileName)
        
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
    
    @staticmethod
    def compute_batch(list_of_delayed,batch_size,client):
        
        processing = []
        finished = []
        total_to_process = len(list_of_delayed)
        idx = 0
        while len(list_of_delayed) > 0:
            a = list_of_delayed.pop()
            a = client.compute(a)
            processing.append(a)
            del a
            idx += 1
            print('Computing {} of {}'.format(idx,total_to_process))
            
            while len(processing) >= batch_size or (len(processing) > 0 and len(list_of_delayed) == 0):
                test = [x.status == 'finished' for x in processing]
                finished_new = [p for p,t in zip(processing,test) if t]
                processing = [p for p,t in zip(processing,test) if not t]
                finished_new = client.gather(finished_new)
                finished = finished + finished_new
                del finished_new
                time.sleep(0.1)
        return finished
    
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
    
    def imagePyramidNum(self):
        '''
        Map of pyramids accross a single 3D color
        
        Output is used to guide subsequent multiscales that are produced
        '''
        out_shape = self.shape_3d
        chunk = self.origionalChunkSize[2:]
        final_chunk_size = self.finalChunkSize[2:]
        
        pyramidMap = {0:[out_shape,chunk]}
        
        # Make sure chunks are adjusted in the approriate way
        # ie getting bigger or smaller with each level
        chunk_change = []
        for s,f in zip(chunk,final_chunk_size):
            if s > f:
                chunk_change.append(0.5)
            elif s < f:
                chunk_change.append(2)
            elif s == f:
                chunk_change.append(1)
        
        chunk_change = tuple(chunk_change)
        print(chunk_change)
        # chunk_change = (4,0.5,0.5)
        # chunk_change = (2,2,2)
        
        
        
        current_pyramid_level = 0
        print((out_shape,chunk))
        
        last_level = False
        while True:
            current_pyramid_level += 1
            out_shape = tuple([x//2 for x in out_shape])
            chunk = (
                chunk_change[0]*pyramidMap[current_pyramid_level-1][1][0],
                chunk_change[1]*pyramidMap[current_pyramid_level-1][1][1],
                chunk_change[2]*pyramidMap[current_pyramid_level-1][1][2]
                )
            chunk = [int(x) for x in chunk]
            
            
            tmpChunk = []
            for idx,c in enumerate(chunk_change):
                if c > 1:
                    tmpChunk.append(
                        chunk[idx] if chunk[idx] <= final_chunk_size[idx] else final_chunk_size[idx]
                        )
                elif c < 1:
                    tmpChunk.append(
                        chunk[idx] if chunk[idx] >= final_chunk_size[idx] else final_chunk_size[idx]
                        )
                elif c == 1:
                    tmpChunk.append(
                        chunk[idx]
                        )
            chunk = tuple(tmpChunk)
            
            pyramidMap[current_pyramid_level] = [out_shape,chunk]
                
            print((out_shape,chunk))
            
            # stop if any shape dimension is below 1 then delete pyramid level            
            if any([x<2 for x in out_shape]):
                del pyramidMap[current_pyramid_level]
                break
            
            # Ensure that at least 1 more resolution level is formed to benefit low resolution viewers
            if any([c>s for c,s in zip(chunk,out_shape)]):
                if last_level:
                    break
                else:
                    last_level = True
        
        print(pyramidMap)
        return pyramidMap
    
    
    
    
    
    
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
    
