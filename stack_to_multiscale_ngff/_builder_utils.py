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
from skimage import io


class _builder_utils:

    def scale_name(self,res):
        name = os.path.join(self.out_location,'scale{}'.format(res))
        return name

    @staticmethod
    def read_image(fileName):
        return io.imread(fileName)

    def imagePyramidNum_converge_isotropic(self):
        '''
        Map of pyramids accross a single 3D color

        Output is used to guide subsequent multiscales that are produced

        This version of the function attempts to move resolution towards
        iostropic rather than just 2x downsample

        The current version only allows 2x or 1x (ie. no) downsample
        Thus, some volumes will never reach isotropic.

        This method of approaching isotropic resolution should make
        visualizing volumes that are sampled very sparsely in 1 dimension
        a better experience.

        CURRENT: Assumes that (y,x) have the same resolution. Z is independant
        FUTURE: Allow all resolutions to be independant and choose the best downsample method

        Downsampling factors are integers (2x steps), required by the
        shard-aligned dask coarsen used to compute each level.
        '''
        out_shape = self.shape_3d
        chunk = self.origionalChunkSize[2:]
        final_chunk_size = self.finalChunkSize[2:]
        resolution = self.geometry[2:]

        # pyramidMap = {res_lev:[shape,chunk_size,resolution,downsamp_factor]}
        pyramidMap = {0:[out_shape,chunk,resolution,(1,1,1)]}

        # Make sure chunks are adjusted in the approriate way
        # ie getting bigger or smaller with each level
        # Assuming (z,y,x): z will change by fac of 4, y,x by fac of 2
        chunk_change = []
        for idx,s,f in zip((0,1,2),chunk,final_chunk_size):
            if idx == 0:
                fac = 2
            else:
                fac = 1
            if s > f:
                chunk_change.append(0.5 * fac)
            elif s < f:
                chunk_change.append(2 * fac)
            elif s == f:
                chunk_change.append(1)

        chunk_change = tuple(chunk_change)
        print(chunk_change)

        current_pyramid_level = 0
        print((out_shape,chunk))

        while True:
            current_pyramid_level += 1

            # Determine downsampling requiremnts
            previous_shape = pyramidMap[current_pyramid_level-1][0]
            previous_resolution = np.array(pyramidMap[current_pyramid_level-1][2])

            # Determine which resolutions are below
            ratio_of_max = previous_resolution / previous_resolution.max()
            ratio_below_half = ratio_of_max <= 0.5
            ratio_below_one = ratio_of_max < 1
            down_samp = []
            res = []
            for idx,below_half,below_one in zip((0,1,2),ratio_below_half,ratio_below_one):
                if all(ratio_of_max == 1) or all(np.logical_and(ratio_of_max<=1, ratio_of_max>0.5)):
                    new_samp = 2
                    new_res = previous_resolution[idx] * 2
                elif below_one:
                    if below_half:
                        new_samp = 2
                        new_res = previous_resolution[idx] * 2
                    else:
                        # Integer downsampling factors are required by the
                        # shard-aligned coarsen: round up to the next 2x step
                        new_samp = math.ceil(1 / ratio_of_max[idx])
                        new_res = previous_resolution[idx] * new_samp
                else:
                    new_samp = 1
                    new_res = previous_resolution[idx]
                down_samp.append(new_samp)
                res.append(new_res)
            print(down_samp)
            print(res)

            # Shapes must match the padded coarsen result: ceil(n / factor)
            out_shape = np.array(previous_shape) / np.array(down_samp)
            out_shape = np.ceil(out_shape)
            out_shape = tuple(out_shape.astype(int))

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
            if self.directToFinalChunks:
                chunk = final_chunk_size

            pyramidMap[current_pyramid_level] = [out_shape,chunk,tuple(res),tuple(down_samp)]

            print((out_shape,chunk))

            # stop if any shape dimension is below 1 then delete pyramid level
            if any([x<2 for x in out_shape]):
                del pyramidMap[current_pyramid_level]
                break

        pyramidMap_dict = {}
        keys = ['shape','chunk','resolution','downsamp']
        for key, value in pyramidMap.items():
            pyramidMap_dict[key] = {}
            for nk, ii in zip(keys, value):
                pyramidMap_dict[key][nk] = ii

        print(pyramidMap_dict)
        return pyramidMap_dict

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
