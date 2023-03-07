# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 12:46:17 2023

@author: awatson
"""

'''
Store mix-in classes for image processing methods

These classes are designed to be inherited by the builder class (builder.py)
'''

import numpy as np
from itertools import product
from skimage import img_as_float32
import math
import zarr

class _builder_downsample:

    def fast_downsample(self, from_path, to_path, info, minmax=False, idx=None,
                           store=zarr.storage.NestedDirectoryStore, verify=True,
                        down_sample_ratio=(2,2,2)):
        '''
        Helper function that handles downsampling 3D data in across 3 dimensions.
        down_sample_ratio: tuple that determines how each axis will be downsampled. Currently only 1 or 2 are supported
        1 = no downsample, 2 = 2x downsample

        An option to verify that the downsampled data were written is on by default. This will slow the creation
        process, but in high-parallel environment chunks sometimes do not get written properly causing data loss
        that cascades into lower resolution levels when writing a multscale series. If the chunk was not written
        properly, the process will be repeated until successful.
        '''

        zstore = self.get_store_from_path(from_path)

        zarray = zarr.open(zstore)

        working = zarray[
                  info['t'],
                  info['c'],
                  info['z'][0][0]:info['z'][0][1],
                  info['y'][0][0]:info['y'][0][1],
                  info['x'][0][0]:info['x'][0][1]
                  ]

        while len(working.shape) > 3:
            working = working[0]

        del zarray
        del zstore

        working = self.dtype_convert(working)
        # Calculate min/max of input data
        if minmax:
            min, max = working.min(), working.max()

        # Ensure all arrays are padded with 2X mirrored pixels
        if self.downSampType == 'mean' or self.downSampType == 'max':
            working = self.pad_3d_2x(working, info, final_pad=2)

        # Run proper downsampling method
        if self.downSampType == 'mean':
            working = self.local_mean_downsample(working,down_sample_ratio=down_sample_ratio)
        elif self.downSampType == 'max':
            working = self.local_max_downsample(working,down_sample_ratio=down_sample_ratio)



        down_sample_trim = []
        for ii in down_sample_ratio:
            if ii == 1:
                down_sample_trim.append(2)
            elif ii == 2:
                down_sample_trim.append(1)
            else:
                raise NotImplementedError('Only 2X and 1X down sample are supported at this time')
        down_sample_trim = tuple(down_sample_trim)

        while True:
            zstore = self.get_store_from_path(to_path)

            zarray = zarr.open(zstore)
            # Write array trimmed of 1 value along all edges
            zarray[
            info['t'],
            info['c'],
            (info['z'][0][0] + info['z'][1][0]) // down_sample_ratio[0]:(info['z'][0][1] - info['z'][1][1]) // down_sample_ratio[0],
            # Compensate for overlap in new array
            (info['y'][0][0] + info['y'][1][0]) // down_sample_ratio[1]:(info['y'][0][1] - info['y'][1][1]) // down_sample_ratio[1],
            # Compensate for overlap in new array
            (info['x'][0][0] + info['x'][1][0]) // down_sample_ratio[2]:(info['x'][0][1] - info['x'][1][1]) // down_sample_ratio[2]
            # Compensate for overlap in new array
            ] = working[
                down_sample_trim[0]:-down_sample_trim[0],
                down_sample_trim[1]:-down_sample_trim[1],
                down_sample_trim[2]:-down_sample_trim[2]
                ]

            # Immediately verify that the array was written is correctly
            if verify:
                print('Verifying Location {}'.format(info))
                del zarray
                zarray = zarr.open(zstore, 'r')
                correct = np.ndarray.all(
                    zarray[
                    info['t'],
                    info['c'],
                    (info['z'][0][0] + info['z'][1][0]) // down_sample_ratio[0]:(info['z'][0][1] - info['z'][1][1]) // down_sample_ratio[0],
                    # Compensate for overlap in new array
                    (info['y'][0][0] + info['y'][1][0]) // down_sample_ratio[1]:(info['y'][0][1] - info['y'][1][1]) // down_sample_ratio[1],
                    # Compensate for overlap in new array
                    (info['x'][0][0] + info['x'][1][0]) // down_sample_ratio[2]:(info['x'][0][1] - info['x'][1][1]) // down_sample_ratio[2]
                    # Compensate for overlap in new array
                    ] == working[
                        down_sample_trim[0]:-down_sample_trim[0],
                        down_sample_trim[1]:-down_sample_trim[1],
                        down_sample_trim[2]:-down_sample_trim[2]
                        ]
                )
            else:
                # To bypass the immediate verification
                correct = True

            del zarray
            del zstore

            if correct:
                print('SUCCESS : {}'.format(info))
                break
            else:
                print('FAILURE : RETRY {}'.format(info))

        if correct and minmax:
            return idx, (min, max, info['c'])
        if correct and not minmax:
            return idx,
        if not correct:
            print('Not Correct')
            return False,
        return False,

    def local_mean_downsample(self, image,down_sample_ratio=(2,2,2)):
        image = img_as_float32(image)
        canvas = np.zeros(
            (image.shape[0] // down_sample_ratio[0],
             image.shape[1] // down_sample_ratio[1],
             image.shape[2] // down_sample_ratio[2]),
            dtype=np.dtype('float32')
        )

        # print(canvas.shape)
        for z, y, x in product(range(down_sample_ratio[0]), range(down_sample_ratio[1]), range(down_sample_ratio[2])):
            tmp = image[
                  z::down_sample_ratio[0],
                  y::down_sample_ratio[1],
                  x::down_sample_ratio[2]
                  ][0:canvas.shape[0] - 1, 0:canvas.shape[1] - 1, 0:canvas.shape[2] - 1]
            canvas[0:tmp.shape[0], 0:tmp.shape[1], 0:tmp.shape[2]] += tmp

        canvas /= math.prod(down_sample_ratio)
        return self.dtype_convert(canvas)

    def local_max_downsample(self, image,down_sample_ratio=(2,2,2)):
        # image = img_as_float32(image)
        canvas = np.zeros(
            (image.shape[0] // down_sample_ratio[0],
             image.shape[1] // down_sample_ratio[1],
             image.shape[2] // down_sample_ratio[2]),
            dtype=image.dtype
        )

        canvas_tmp = canvas.copy()

        # print(canvas.shape)
        for z, y, x in product(range(down_sample_ratio[0]), range(down_sample_ratio[1]), range(down_sample_ratio[2])):
            tmp = image[
                  z::down_sample_ratio[0],
                  y::down_sample_ratio[1],
                  x::down_sample_ratio[2]
                  ][0:canvas.shape[0] - 1, 0:canvas.shape[1] - 1, 0:canvas.shape[2] - 1]
            canvas_tmp[0:tmp.shape[0], 0:tmp.shape[1], 0:tmp.shape[2]] = tmp

        np.maximum(canvas, canvas_tmp, out=canvas)
        return self.dtype_convert(canvas)

    def fast_2d_downsample(self, from_path, to_path, info, minmax=False, idx=None,
                           store=zarr.storage.NestedDirectoryStore, verify=True):
        '''
        Helper function that handles downsampling 3D data in accross only 2 dimensions.  ie (z,y,x) will downsample in only (y,x)
        data from 1 zarr array to another zarr array

        An option to verify that the downsampled data were written is on by default. This will slow the creation
        process, but in high-parallel environment chunks sometimes do not get written properly causing data loss
        that cascades into lower resolution levels when writing a multscale series. If the chunk was not written
        properly, the process will be repeated until successful.
        '''

        # while True:
        zstore = self.get_store_from_path(from_path)
        # if store == H5_Shard_Store:
        #     zstore = store(from_path, verbose=self.verbose,verify_write=self.verify_zarr_write,alternative_lock_file_path=self.tmp_dir)
        #     # zstore = H5_Shard_Store(from_path, verbose=self.verbose)
        # else:
        #     zstore = store(from_path)

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
            min, max = working.min(), working.max()

        if self.downSampType == 'mean' or self.downSampType == 'max':
            working = self.pad_3d_2x(working, info, final_pad=2)

        # Run proper downsampling method
        if self.downSampType == 'mean':
            working = self.local_mean_2d_downsample_2x(working)
        elif self.downSampType == 'max': # NOT WORKING YET FOR 2D
            working = self.local_mean_2d_downsample_2x(working)

        while True:
            # print('Preparing to write')
            zstore = self.get_store_from_path(to_path)
            # if store == H5_Shard_Store:
            #     zstore = store(to_path, verbose=self.verbose,verify_write=self.verify_zarr_write,alternative_lock_file_path=self.tmp_dir)
            #     # zstore = H5Store(to_path, verbose=self.verbose)
            # else:
            #     zstore = store(to_path)

            zarray = zarr.open(zstore)
            # print(zarray.shape)
            # print('Writing Location {}'.format(info))
            # Write array trimmed of 1 value along all edges
            zarray[
            info['t'],
            info['c'],
            (info['z'][0][0] + info['z'][1][0]):(info['z'][0][1] - info['z'][1][1]),
            # Compensate for overlap in new array
            (info['y'][0][0] + info['y'][1][0]) // 2:(info['y'][0][1] - info['y'][1][1]) // 2,
            # Compensate for overlap in new array
            (info['x'][0][0] + info['x'][1][0]) // 2:(info['x'][0][1] - info['x'][1][1]) // 2
            # Compensate for overlap in new array
            ] = working[2:-2, 1:-1, 1:-1]

            # Imediately verify that the array was written is correctly
            if verify:
                print('Verifying Location {}'.format(info))
                del zarray
                zarray = zarr.open(zstore, 'r')
                correct = np.ndarray.all(
                    zarray[
                    info['t'],
                    info['c'],
                    (info['z'][0][0] + info['z'][1][0]):(info['z'][0][1] - info['z'][1][1]),
                    # Compensate for overlap in new array
                    (info['y'][0][0] + info['y'][1][0]) // 2:(info['y'][0][1] - info['y'][1][1]) // 2,
                    # Compensate for overlap in new array
                    (info['x'][0][0] + info['x'][1][0]) // 2:(info['x'][0][1] - info['x'][1][1]) // 2
                    # Compensate for overlap in new array
                    ] == working[2:-2, 1:-1, 1:-1]
                )
            else:
                # To bypass the immediate verification
                correct = True

            del zarray
            del zstore

            if correct:
                print('SUCCESS : {}'.format(info))
                break
            else:
                print('FAILURE : RETRY {}'.format(info))

        if correct and minmax:
            return idx, (min, max, info['c'])
        if correct and not minmax:
            return idx,
        if not correct:
            print('Not Correct')
            return False,
        return False,

    def local_mean_2d_downsample_2x(self, image):
        # dtype = image.dtype
        # print(image.shape)
        image = img_as_float32(image)
        canvas = np.zeros(
            (image.shape[0],
             image.shape[1] // 2,
             image.shape[2] // 2),
            dtype=np.dtype('float32')
        )

        for idx,xy in enumerate(image):

            for y, x in product(range(2), range(2)):
                tmp = xy[y::2, x::2][0:canvas.shape[1] - 1, 0:canvas.shape[2] - 1]
                # print(tmp.shape)
                canvas[idx,0:tmp.shape[0], 0:tmp.shape[1]] += tmp

        canvas /= 4
        return self.dtype_convert(canvas)

    def fast_3d_downsample(self,from_path,to_path,info,minmax=False,idx=None,store=zarr.storage.NestedDirectoryStore,verify=True):
        '''
        Helper function that handles downsampling 3D data from 1 zarr array to another zarr array
        
        An option to verify that the downsampled data were written is on by default. This will slow the creation
        process, but in high-parallel environment chunks sometimes do not get written properly causing data loss
        that cascades into lower resolution levels when writing a multscale series. If the chunk was not written
        properly, the process will be repeated until successful.
        '''
        
        # while True:
        zstore = self.get_store_from_path(from_path)
        # if store == H5_Shard_Store:
        #     zstore = store(from_path, verbose=self.verbose,verify_write=self.verify_zarr_write,alternative_lock_file_path=self.tmp_dir)
        #     # zstore = H5_Shard_Store(from_path, verbose=self.verbose)
        # else:
        #     zstore = store(from_path)
        
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
        
        if self.downSampType == 'mean' or self.downSampType == 'max':
            working = self.pad_3d_2x(working,info,final_pad=2)
        
        # Run proper downsampling method
        if self.downSampType == 'mean':
            working = self.local_mean_3d_downsample_2x(working)
        elif self.downSampType == 'max':
            working = self.local_max_3d_downsample_2x(working)
        
            
        while True:
            # print('Preparing to write')
            zstore = self.get_store_from_path(to_path)
            # if store == H5_Shard_Store:
            #     zstore = store(to_path, verbose=self.verbose,verify_write=self.verify_zarr_write,alternative_lock_file_path=self.tmp_dir)
            #     # zstore = H5Store(to_path, verbose=self.verbose)
            # else:
            #     zstore = store(to_path)
            
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
            
            #Imediately verify that the array was written is correctly
            if verify:
                print('Verifying Location {}'.format(info))
                del zarray
                zarray = zarr.open(zstore,'r')
                correct = np.ndarray.all(
                    zarray[
                    info['t'],
                    info['c'],
                    (info['z'][0][0]+info['z'][1][0])//2:(info['z'][0][1]-info['z'][1][1])//2, #Compensate for overlap in new array
                    (info['y'][0][0]+info['y'][1][0])//2:(info['y'][0][1]-info['y'][1][1])//2, #Compensate for overlap in new array
                    (info['x'][0][0]+info['x'][1][0])//2:(info['x'][0][1]-info['x'][1][1])//2  #Compensate for overlap in new array
                    ] == working[1:-1,1:-1,1:-1]
                    )
            else:
                # To bypass the immediate verification
                correct = True
            
            del zarray
            del zstore
        
            if correct:
                print('SUCCESS : {}'.format(info))
                break
            else:
                print('FAILURE : RETRY {}'.format(info))
        
        if correct and minmax:
            return idx,(min,max,info['c'])
        if correct and not minmax:
            return idx,
        if not correct:
            print('Not Correct')
            return False,
        return False,
    
    def determine_chunks_size_for_downsample(self,res):
        
        new_chunks = (self.pyramidMap[res]['chunk'])
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
    
    def local_max_3d_downsample_2x(self,image):
        canvas = np.zeros(
            (image.shape[0]//2,
            image.shape[1]//2,
            image.shape[2]//2),
            dtype = image.dtype
            )
        
        canvas_tmp = canvas.copy()
        
        # print(canvas.shape)
        for z,y,x in product(range(2),range(2),range(2)):
            tmp = image[z::2,y::2,x::2][0:canvas.shape[0]-1,0:canvas.shape[1]-1,0:canvas.shape[2]-1]
            # print(tmp.shape)
            canvas_tmp[0:tmp.shape[0],0:tmp.shape[1],0:tmp.shape[2]] = tmp
            np.maximum(canvas,canvas_tmp,out=canvas)
            
        return self.dtype_convert(canvas)