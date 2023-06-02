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


        working = working[
                down_sample_trim[0]:-down_sample_trim[0],
                down_sample_trim[1]:-down_sample_trim[1],
                down_sample_trim[2]:-down_sample_trim[2]
                ]

        trimmed_slice = np.s_[
                        info['t'],
                        info['c'],
                        (info['z'][0][0] + info['z'][1][0]) // down_sample_ratio[0]:(info['z'][0][1] - info['z'][1][
                            1]) // down_sample_ratio[0],
                        # Compensate for overlap in new array
                        (info['y'][0][0] + info['y'][1][0]) // down_sample_ratio[1]:(info['y'][0][1] - info['y'][1][
                            1]) // down_sample_ratio[1],
                        # Compensate for overlap in new array
                        (info['x'][0][0] + info['x'][1][0]) // down_sample_ratio[2]:(info['x'][0][1] - info['x'][1][
                            1]) // down_sample_ratio[2]
                        # Compensate for overlap in new array
        ]

        failure = 0
        correct = False
        while not correct:
            try:
                zstore = self.get_store_from_path(to_path)

                zarray = zarr.open(zstore)

                compressor_lossy = self.is_compressor_lossy(zarray.compressor)  # _builder_utils

                # if compressor_lossy:
                #     to_compare = zarray[trimmed_slice]
                # Write array trimmed of 1 value along all edges
                zarray[trimmed_slice] = working

                del zarray
                del zstore

                # Immediately verify that the array was written is correctly
                if verify:
                    # print('Verifying Location {}'.format(info))
                    zstore = self.get_store_from_path(to_path)
                    zarray = zarr.open(zstore, 'r')

                    # compressor_lossy = self.is_compressor_lossy(zarray.compressor) #_builder_utils

                    if compressor_lossy:
                        # print('lossy')
                        ## Skip verification of lossy.  Not sure how to verify the data because its not
                        ## obvious how to know the new values. The below method works early then fails as the array fills in
                        ## probably because there are adjacent values in the array that unpredictatbly alter
                        ## the outcome of the lossy compression.  The below method is also wasteful of CPU cycle, requiring
                        ## compression to be done 2x.
                        # if np.ndarray.all(to_compare == zarray[trimmed_slice]):
                        #     correct = True
                        # else:
                        #     print('NOT CORRECT')
                        # # print('comparing lossy')
                        working_zarray = zarr.zeros(zarray.shape,chunks=zarray.chunks,dtype=zarray.dtype, compressor=zarray.compressor)
                        working_zarray[trimmed_slice] = working
                        correct = np.ndarray.all(
                            zarray[trimmed_slice] == working_zarray[trimmed_slice]
                        )
                    else:
                        correct = np.ndarray.all(
                            zarray[trimmed_slice] == working
                        )
                else:
                    # To bypass the immediate verification
                    correct = True

                del zarray
                del zstore

                if correct:
                    pass
                    # print('SUCCESS : {}'.format(info))
                    # break
                else:
                    failure += 1
                    # print('FAILURE : RETRY {}'.format(info))
                    print('FAILURE Verify {} - Retrying'.format(failure))
                    if failure >= 2:
                        break
            except:
                print('EXCEPTION')
                return False,

        if correct and minmax:
            # print(idx)
            # print((min, max, info['c']))
            return idx, (min, max, info['c'])
        if correct and not minmax:
            # print(idx)
            return idx,
        if not correct:
            # print('Not Correct')
            return False,
        return False,

    def local_mean_downsample(self, image,down_sample_ratio=(2,2,2)):
        '''
                Inputs:
                image: 3D numpy array
                down_sample_ratio: (tuple,list) specifying down sampling along axes (z,y,x) at 2x or 1x (none)

                Output:
                3D numpy array that has been down sampled using a local mean function at ratios 1x or 2x according to the 'down_sample_ratio'
        '''
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
                  ][0:canvas.shape[0], 0:canvas.shape[1], 0:canvas.shape[2]]
            canvas[0:tmp.shape[0], 0:tmp.shape[1], 0:tmp.shape[2]] += tmp

        canvas /= math.prod(down_sample_ratio)
        return self.dtype_convert(canvas)

    def local_max_downsample(self, image,down_sample_ratio=(2,2,2)):
        '''
                Inputs:
                image: 3D numpy array
                down_sample_ratio: (tuple,list) specifying down sampling along axes (z,y,x) at 2x or 1x (none)

                Output:
                3D numpy array that has been down sampled using a local max function at ratios 1x or 2x according to the 'down_sample_ratio'
        '''
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
                  ][0:canvas.shape[0], 0:canvas.shape[1], 0:canvas.shape[2]]

            canvas_tmp[0:tmp.shape[0], 0:tmp.shape[1], 0:tmp.shape[2]] = tmp
            np.maximum(canvas, canvas_tmp, out=canvas)
        return self.dtype_convert(canvas)
    
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
