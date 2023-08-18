# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 09:46:38 2021

@author: alpha
"""

import os, glob, time, sys, shutil
import dask

import numcodecs
import zarr.storage
from numcodecs import Blosc
try:
    from imagecodecs.numcodecs import JpegXl as Jpegxl
    numcodecs.register_codec(Jpegxl)
    # print('Imported JpegXl')
except:
    pass
try:
    from imagecodecs.numcodecs import Jpegxl
    numcodecs.register_codec(Jpegxl)
    # print('Imported Jpegxl')
except:
    pass
# from imagecodecs.numcodecs import Jpegxl
# numcodecs.register_codec(Jpegxl)

# ## Fix to deal with fussy
# from PIL import Image, ImageFile
# Image.MAX_IMAGE_PIXELS = 2000000000
# ImageFile.LOAD_TRUNCATED_IMAGES = False

# Import the main class that orchestrates building the multiscale ome-zarr
from stack_to_multiscale_ngff._builder_init import builder

# Import custom zarr store types
# from stack_to_multiscale_ngff.archived_nested_store import Archived_Nested_Store
from zarr_stores.archived_nested_store import Archived_Nested_Store
# from stack_to_multiscale_ngff.h5_nested_store4 import H5_Nested_Store
from zarr_stores.h5_nested_store import H5_Nested_Store

# Import local functions
from stack_to_multiscale_ngff.arg_parser import parser
# from Z:\cbiPythonTools\bil_api\converters\H5_zarr_store3 import H5Store

# Note that attempts to determine the amount of free mem does not work for SLURM allocation
# This parameter must be set manually when submitting jobs to reduce the risk of overrunning
# RAM allocation




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
    downSampleType = args.downSampleType[0]
    assert downSampleType in ['mean','max'], 'Only local mean and local max downsampling is available'

    ## Below will enable inputs for information included in .zattrs omero metadata
    #Nothing is required and when left bank will be generated automatically based on the data being converted

    name = args.name[0] if args.name != [] else None
    defaultZ = args.defaultZ[0] if args.defaultZ != [] else None

    #Expects a list of labels for each channel ex. ['autofluorescence','tyrosine_hydroxylase','cFOS']
    channelLabels = args.channelLabels if args.channelLabels != [] else None
    if channelLabels is not None:
        tmp = {}
        for idx,ii in enumerate(channelLabels):
            tmp[idx] = ii
        channelLabels = tmp
        del tmp

    #Expects a list of integers that defines the START STOP MIN MAX for the LUT representation of each channel (must be sets of 4 integers)
    windowLabels = args.windowLabels if args.windowLabels != [] else None
    # Output a dict where each key is the channel and each item is a dict with values 'start' 'stop' 'min' 'max'
    if windowLabels is not None:
        assert len(windowLabels) % 4 == 0, 'Window label values must be in sets of 4 representing START STOP MIN MAX integers for each channel'
        new_labels = []
        for idx,ii in enumerate(windowLabels):
            if idx % 4 == 0:
                channel = {}
                channel['start'] = ii
            elif idx % 4 == 1:
                channel['end'] = ii
            elif idx % 4 == 2:
                channel['min'] = ii
            elif idx % 4 == 3:
                channel['max'] = ii
                new_labels.append(channel)
        windowLabels = {}
        for idx, ii in enumerate(new_labels):
            windowLabels[idx] = ii

        if channelLabels is not None:
            assert len(channelLabels) == len(windowLabels), f'Window labels must be provided for each channel: There are {len(channelLabels)} channels and {len(windowLabels)} window labels'

    #'Color for each channel: by default colors are repeatedly assigned as [green, red, purple, blue,...]'
    # Color names can be found in the _builder_colors file
    colors = args.colors if args.colors != [] else None
    if colors is not None:
        if windowLabels is not None: assert len(colors) == len(windowLabels), 'The number of Windows Labels values must be equal to the number of colors'
        if channelLabels is not None: assert len(colors) == len(channelLabels), 'The number of Channel Labels values must be equal to the number of colors'
        from stack_to_multiscale_ngff._builder_colors import colors as color_tablet
        tmp = {}
        for idx,ii in enumerate(colors):
            tmp[idx] = color_tablet[ii][-1]
        colors = tmp
        del tmp

    # Build a dict to communicate OMERO metadata to the builder class
    omero = {}
    omero['channels'] = {}
    omero['channels']['color'] = colors
    omero['channels']['label'] = channelLabels
    omero['channels']['window'] = windowLabels
    omero['name'] = name
    omero['rdefs'] = {}
    omero['rdefs']['defaultZ'] = defaultZ

    compressor = None
    if args.compression[0].lower() == '':
        pass
    elif args.compression[0].lower() == 'zstd':
        assert args.clevel[0] >= 0 and args.clevel[0] <= 9, 'Compression Level must be between 0-9 for zstd'
        compressor = Blosc(cname='zstd', clevel=args.clevel[0], shuffle=Blosc.BITSHUFFLE)
    elif args.compression[0].lower() == 'jpegxl':
        if args.lossy:
            assert args.clevel[0] >= 50 and args.clevel[0] <= 100, 'Compression Level must be between 50-100 for lossy jpegxl'
            compressor = Jpegxl(level=args.clevel[0], lossless=False)
        else:
            compressor = Jpegxl(lossless=True)

    if out_location.lower().endswith('.ome.zarr'):
        zarr_store_type = zarr.storage.NestedDirectoryStore
    elif out_location.lower().endswith('.omehans'):
        zarr_store_type = H5_Nested_Store
    else:
        zarr_store_type = zarr.storage.NestedDirectoryStore

    #Initialize builder class
    mr = builder(in_location, out_location, fileType=fileType,
            geometry=scale,origionalChunkSize=origionalChunkSize, finalChunkSize=finalChunkSize,
            cpu_cores=cpu, mem=mem, tmp_dir=tmp_dir,verbose=verbose,compressor=compressor,
            zarr_store_type=zarr_store_type,
            verify_zarr_write=verify_zarr_write, omero_dict=omero,
                 skip=skip, downSampType=downSampleType, directToFinalChunks=args.directToFinalChunks)

    if args.stopBuild:
        try:
            with dask.config.set({'temporary_directory': mr.tmp_dir, #<<-Chance dask working directory
                                  'logging.distributed': 'error'}):  #<<-Disable WARNING messages that are often not helpful (remove for debugging)

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
                # with Client(n_workers=workers,threads_per_worker=threads) as client:

                mr.write_resolution_series()

            if mr.zarr_store_type == Archived_Nested_Store or mr.zarr_store_type == H5_Nested_Store:
                for r in reversed(list(range(len(mr.pyramidMap)))):
                    mr.get_store(r).consolidate()

        finally:
            #Cleanup
            countKeyboardInterrupt = 0
            countException = 0
            print('Cleaning up tmp dir and orphaned lock files')
            while True:
                try:
                    #Remove any existing files in the temp_dir
                    filelist = glob.glob(os.path.join(mr.tmp_dir, "**/*"), recursive=True)
                    for f in filelist:
                        try:
                            if os.path.isfile(f):
                                os.remove(f)
                            elif os.path.isdir(f):
                                shutil.rmtree(f)
                        except Exception:
                            pass

                    #Remove any .lock files in the output directory (recursive)
                    lockList = glob.glob(os.path.join(mr.out_location, "**/*.lock"), recursive=True)
                    for f in lockList:
                        try:
                            if os.path.isfile(f):
                                os.remove(f)
                            elif os.path.isdir(f):
                                shutil.rmtree(f)
                        except Exception:
                            pass
                    break
                except KeyboardInterrupt:
                    countKeyboardInterrupt += 1
                    if countKeyboardInterrupt == 4:
                        break
                    pass
                except Exception:
                    countException += 1
                    if countException == 100:
                        break
                    pass


            stop = time.time()
            print((stop - start)/60/60)
        
        sys.exit(0)
    
## https://download.brainimagelibrary.org/2b/da/2bdaf9e66a246844/mouseID_405429-182725/
## /bil/data/2b/da/2bdaf9e66a246844/mouseID_405429-182725/

    