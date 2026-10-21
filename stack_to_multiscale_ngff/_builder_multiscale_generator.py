# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 12:46:17 2023

@author: awatson
"""

'''
Store mix-in classes for utilities

These classes are designed to be inherited by the builder class (builder.py)

Writing strategy (shard-safe, massively parallel):

    one dask store task == one complete zarr shard == one unique write region.

Dask blocks are aligned to shard boundaries (zarr v3 sharded output) or chunk
boundaries (zarr v2 output), so concurrent workers always write distinct
regions and no locking is required. Parallelism comes from different workers
writing different shards simultaneously.
'''

import os
import math
import zarr
import numpy as np
import dask.array as da
from distributed import Client, progress, performance_report

# Project specific imports
from stack_to_multiscale_ngff.tiff_manager import tiff_manager_3d
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

        # During creation of one middle resolution, the min and max is calculated
        # for res 0 if values for omero window were not specified in the commandline
        # These values are added to omero:channels during metadata publication
        minmax = False
        where_to_calculate_min_max = 2
        if len(self.pyramidMap) == 2 and res == 1:
            minmax = True
        elif res == len(self.pyramidMap) // where_to_calculate_min_max:
            minmax = True
        elif len(self.pyramidMap) // where_to_calculate_min_max == 0:
            minmax = True

        results = self.down_sample_level(res, client, minmax=minmax)

        if minmax and self.omero_dict['channels']['window'] is None:
            self.min, self.max = results
            print('Setting OMERO Window')
            self.set_omero_window()


    def write_resolution_0(self,client):

        print('Building Virtual Stack')
        stack = []
        for color in self.filesList:

            s = self.organize_by_groups(color,self.origionalChunkSize[2])
            test_image = tiff_manager_3d(s[0])
            optimum_chunks = utils.optimize_chunk_shape_3d_2(test_image.shape,test_image.chunks,self.origionalChunkSize[2:],test_image.dtype,self.res0_chunk_limit_GB)
            test_image.chunks = optimum_chunks
            print('##########################')
            print(optimum_chunks)
            print('##########################')
            print(test_image.shape)
            print(test_image.chunks)

            s = [test_image.clone_manager_new_file_list(x) for x in s]
            print(len(s))
            for ii in s:
                print(ii.chunks)
                print(len(ii.fileList))
            print('From_array')
            print(s[0].dtype)
            s = [da.from_array(x,chunks=x.chunks,name=False,asarray=False) for x in s]
            print(len(s))
            s = da.concatenate(s)
            print(s)
            stack.append(s)
        stack = da.stack(stack)
        stack = stack[None,...]

        print(stack)

        compressor = self._level_compressor(0)
        self._store_array_to_level(0, stack, client, compressor)

    def down_sample_level(self, res, client, minmax=False):
        '''
        Compute one downsampled level from the previously *stored* level and
        write it with shard-aligned dask blocks.

        Downsampling is mean or max pooling with edge replication
        (non-divisible edges are padded by repeating the last voxel).
        For integer data, means use np.rint (nearest even).
        Each level is computed from the previous stored level to keep
        dependency graphs bounded and to avoid loading arrays in RAM.
        '''
        print('Getting Parent Zarr Array')
        parent = zarr.open_group(self.out_location, mode='r')['scale{}'.format(res - 1)]
        read_chunks = getattr(parent, 'shards', None)
        if read_chunks is None:
            read_chunks = parent.chunks
        source = da.from_array(parent, chunks=read_chunks)

        # Per channel min/max of the parent level, computed lazily on the cluster
        if minmax:
            mins = []
            maxs = []
            for ch in range(self.Channels):
                mins.append(float(source[:, ch].min().compute()))
                maxs.append(float(source[:, ch].max().compute()))

        down_sample_ratio = tuple(int(x) for x in self.pyramidMap[res]['downsamp'])

        # Pad edges so that every spatial axis is divisible by its downsample factor
        pad_width = tuple(
            (0, 0) if idx < 2 else (0, -int(n) % down_sample_ratio[idx - 2])
            for idx, n in enumerate(source.shape)
        )
        if any(right > 0 for _, right in pad_width):
            source = da.pad(source, pad_width, mode='edge')

        reduction = {idx: ratio for idx, ratio in zip((2, 3, 4), down_sample_ratio) if ratio > 1}

        if self.downSampType == 'mean':
            accumulation_dtype = np.float32 if self.dtype.itemsize <= 2 else np.float64
            reduced = da.coarsen(np.mean, source, reduction, trim_excess=False, dtype=accumulation_dtype)
            if self.dtype.kind in 'ui':
                reduced = da.rint(reduced)
        elif self.downSampType == 'max':
            reduced = da.coarsen(np.max, source, reduction, trim_excess=False, dtype=self.dtype)
        else:
            raise NotImplementedError("Only local 'mean' and 'max' downsampling is available")

        reduced = reduced.astype(self.dtype)
        new_shape = (self.TimePoints, self.Channels, *self.pyramidMap[res]['shape'])
        assert reduced.shape == new_shape, \
            'Downsampled shape {} does not match expected shape {}'.format(reduced.shape, new_shape)

        compressor = self._level_compressor(res)
        self._store_array_to_level(res, reduced, client, compressor)

        if minmax:
            return mins, maxs

    def _level_compressor(self, res):
        if res == 0:
            return self.compressor
        return self.multi_scale_compressor

    def _storage_shapes(self, res, shape):
        '''
        (inner chunks, shard shape) for a resolution level, clipped to the
        array shape. The shard shape defaults to 4x the largest chunk along z
        and the largest chunk along y/x (set in _builder_init).

        Returns (chunks, None) for zarr v2 output, which does not support sharding.
        '''
        chunk = self.pyramidMap[res]['chunk']
        chunk5 = (1, 1, *chunk)
        if self.shard_shape is not None:
            shard5 = tuple(self.shard_shape)
        else:
            shard5 = (1, 1, *(c * 4 for c in chunk))
        inner = tuple(min(n, c) for n, c in zip(shape, chunk5))
        if self.zarr_format == 2:
            return inner, None
        chunks_per_shard = tuple(s // c for s, c in zip(shard5, chunk5))
        outer = tuple(
            c * min(r, math.ceil(n / c))
            for n, c, r in zip(shape, inner, chunks_per_shard)
        )
        return inner, outer

    def _store_array_to_level(self, res, src, client, compressor):
        '''
        Create the zarr array for a resolution level and store src with dask
        blocks aligned to shard boundaries (zarr v3) or chunk boundaries (v2).

        The safety invariant is:
            one dask store task == one complete shard == one unique write region.
        This allows concurrent writes to DIFFERENT shards without global
        locking (lock=False is intentional and safe). Never run two
        independent writers simultaneously against the same output path.
        '''
        group = self.get_root_group()
        name = 'scale{}'.format(res)
        inner, outer = self._storage_shapes(res, src.shape)

        create_kwargs = {
            'shape': src.shape,
            'dtype': src.dtype,
            'chunks': inner,
            'compressors': [compressor] if compressor is not None else (),
            'overwrite': True,
        }
        block_shape = inner
        if self.zarr_format == 3:
            create_kwargs['shards'] = outer
            create_kwargs['dimension_names'] = ('t', 'c', 'z', 'y', 'x')
            block_shape = outer
        dest = group.create_array(name, **create_kwargs)

        # CRITICAL: align dask blocks to shards (v3) or chunks (v2).
        # A dask store task now owns one whole shard, with no overlap.
        shard_aligned = src.rechunk(block_shape)
        expected_blocks = tuple(
            tuple(min(s, n - start) for start in range(0, n, s))
            for n, s in zip(src.shape, block_shape)
        )
        if shard_aligned.chunks != expected_blocks:
            raise RuntimeError('Dask blocks do not align to zarr shard boundaries')

        n_shards = math.prod(len(parts) for parts in expected_blocks)
        bytes_per_block = math.prod(block_shape) * src.dtype.itemsize
        print(
            'Level {}: shape={}, chunks={}, shards={}, objects={}, '
            'uncompressed shard ~{:.1f} MiB'.format(
                res, tuple(src.shape), inner,
                block_shape if self.zarr_format == 3 else 'NA',
                n_shards, bytes_per_block / 2**20),
            flush=True,
        )

        # da.store makes ONE setitem task per source dask block.
        # Blocks are a partition of the array starting at index 0, each
        # corresponding to exactly one complete storage shard (or one
        # truncated shard on array edges). Concurrent workers ALWAYS write
        # distinct shard keys. Thus lock=False is intentional and safe.
        if self.performance_report:
            with performance_report(filename=os.path.join(self.out_location, 'performance_res_{}.html'.format(res))):
                to_store = da.store(shard_aligned, dest, lock=False, compute=False)
                to_store = client.compute(to_store)
                if self.progress:
                    progress(to_store)
                to_store = client.gather(to_store)
        else:
            to_store = da.store(shard_aligned, dest, lock=False, compute=False)
            to_store = client.compute(to_store)
            if self.progress:
                progress(to_store)
            to_store = client.gather(to_store)
        return dest
