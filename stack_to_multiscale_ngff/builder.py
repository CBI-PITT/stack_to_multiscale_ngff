# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 09:46:38 2021

@author: alpha
"""

import os, glob, time, sys, shutil
import dask
from numcodecs import Blosc

# ## Fix to deal with fussy
# from PIL import Image, ImageFile
# Image.MAX_IMAGE_PIXELS = 2000000000
# ImageFile.LOAD_TRUNCATED_IMAGES = False

# Import the main class that orchistrates building the multscale ome-zarr
from stack_to_multiscale_ngff._builder_init import builder

# Import custom zarr store types
from stack_to_multiscale_ngff.h5_shard_store import H5_Shard_Store
from stack_to_multiscale_ngff.archived_nested_store import Archived_Nested_Store
from stack_to_multiscale_ngff.h5_nested_store import H5_Nested_Store

# Import local functions
from stack_to_multiscale_ngff.arg_parser import parser
# from Z:\cbiPythonTools\bil_api\converters\H5_zarr_store3 import H5Store

# Note that attempts to determine the amount of free mem does not work for SLURM allocation
# This parameter must be set manually when submitting jobs to reduce the risk of overrunning
# RAM allocation




if __name__ == '__main__':
    
    try:
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
                # zarr_store_type=NestedDirectoryStore,
                # zarr_store_type=Archived_Nested_Store,
                zarr_store_type=H5_Nested_Store,
                verify_zarr_write=verify_zarr_write, skip=skip)
        
    
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
                
                # Need to take the min/max data collected during res1 creation and edit zattrs
        if mr.zarr_store_type == Archived_Nested_Store or mr.zarr_store_type == H5_Nested_Store:
            for r in reversed(list(range(len(mr.pyramidMap)))):
                mr.get_store(r).consolidate()
            
    finally:
        #Cleanup
        countKeyboardInterrupt = 0
        countException = 0
        while True:
            print('Cleaning up tmp dir and orphaned lock files')
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
                    raise
                pass
            
    
        stop = time.time()
        print((stop - start)/60/60)
        
        sys.exit(0)
    
## https://download.brainimagelibrary.org/2b/da/2bdaf9e66a246844/mouseID_405429-182725/
## /bil/data/2b/da/2bdaf9e66a246844/mouseID_405429-182725/

    