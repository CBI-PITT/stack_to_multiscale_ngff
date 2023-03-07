# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 12:46:17 2023

@author: awatson
"""

'''
Store mix-in classes for utilities

These classes are designed to be inherited by the builder class (builder.py)
'''

from distribuited import Client
from contextlib import contextmanager
import os

class _builder_utils:
    
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
    
    def write_local_res(self,res):
        with Client(n_workers=self.sim_jobs,threads_per_worker=os.cpu_count()//self.sim_jobs) as client:
            self.write_resolution(res,client)




def block_location_extracter(block_info=None):
    '''
    Takes block_info from dask.array.map_blocks and returns list of tuples
    which indicates the index in the first input array.
    '''
    return block_info[0]['array-location']

####################################################################################################################
####################################################################################################################
####################################################################################################################


'''OLD DOWNSAMPLE METHODS THAT CAN PROBABLY BE DELETED'''


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
    elif self.downSampType == 'max':  # NOT WORKING YET FOR 2D
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

    for idx, xy in enumerate(image):

        for y, x in product(range(2), range(2)):
            tmp = xy[y::2, x::2][0:canvas.shape[1] - 1, 0:canvas.shape[2] - 1]
            # print(tmp.shape)
            canvas[idx, 0:tmp.shape[0], 0:tmp.shape[1]] += tmp

    canvas /= 4
    return self.dtype_convert(canvas)


def fast_3d_downsample(self, from_path, to_path, info, minmax=False, idx=None, store=zarr.storage.NestedDirectoryStore,
                       verify=True):
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
        min, max = working.min(), working.max()

    if self.downSampType == 'mean' or self.downSampType == 'max':
        working = self.pad_3d_2x(working, info, final_pad=2)

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
        (info['z'][0][0] + info['z'][1][0]) // 2:(info['z'][0][1] - info['z'][1][1]) // 2,
        # Compensate for overlap in new array
        (info['y'][0][0] + info['y'][1][0]) // 2:(info['y'][0][1] - info['y'][1][1]) // 2,
        # Compensate for overlap in new array
        (info['x'][0][0] + info['x'][1][0]) // 2:(info['x'][0][1] - info['x'][1][1]) // 2
        # Compensate for overlap in new array
        ] = working[1:-1, 1:-1, 1:-1]

        # Imediately verify that the array was written is correctly
        if verify:
            print('Verifying Location {}'.format(info))
            del zarray
            zarray = zarr.open(zstore, 'r')
            correct = np.ndarray.all(
                zarray[
                info['t'],
                info['c'],
                (info['z'][0][0] + info['z'][1][0]) // 2:(info['z'][0][1] - info['z'][1][1]) // 2,
                # Compensate for overlap in new array
                (info['y'][0][0] + info['y'][1][0]) // 2:(info['y'][0][1] - info['y'][1][1]) // 2,
                # Compensate for overlap in new array
                (info['x'][0][0] + info['x'][1][0]) // 2:(info['x'][0][1] - info['x'][1][1]) // 2
                # Compensate for overlap in new array
                ] == working[1:-1, 1:-1, 1:-1]
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

    def local_mean_3d_downsample_2x(self, image):
        # dtype = image.dtype
        # print(image.shape)
        image = img_as_float32(image)
        canvas = np.zeros(
            (image.shape[0] // 2,
             image.shape[1] // 2,
             image.shape[2] // 2),
            dtype=np.dtype('float32')
        )
        # print(canvas.shape)
        for z, y, x in product(range(2), range(2), range(2)):
            tmp = image[z::2, y::2, x::2][0:canvas.shape[0] - 1, 0:canvas.shape[1] - 1, 0:canvas.shape[2] - 1]
            # print(tmp.shape)
            canvas[0:tmp.shape[0], 0:tmp.shape[1], 0:tmp.shape[2]] += tmp

        canvas /= 8
        return self.dtype_convert(canvas)

    def local_max_3d_downsample_2x(self, image):
        canvas = np.zeros(
            (image.shape[0] // 2,
             image.shape[1] // 2,
             image.shape[2] // 2),
            dtype=image.dtype
        )

        canvas_tmp = canvas.copy()

        # print(canvas.shape)
        for z, y, x in product(range(2), range(2), range(2)):
            tmp = image[z::2, y::2, x::2][0:canvas.shape[0] - 1, 0:canvas.shape[1] - 1, 0:canvas.shape[2] - 1]
            # print(tmp.shape)
            canvas_tmp[0:tmp.shape[0], 0:tmp.shape[1], 0:tmp.shape[2]] = tmp
            np.maximum(canvas, canvas_tmp, out=canvas)

        return self.dtype_convert(canvas)

'''END OF OLD DOWNSAMPLE METHODS'''

####################################################################################################################
####################################################################################################################
####################################################################################################################