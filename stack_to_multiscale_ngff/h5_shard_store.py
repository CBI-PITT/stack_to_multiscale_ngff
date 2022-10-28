# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 10:29:42 2022

@author: awatson
"""

'''
A Zarr store that uses HDF5 as a containiner to shard chunks accross a single
axis.  The store is implemented similar to a directory store 
but on axis[-3] HDF5 files are written which contain
chunks cooresponding to the remainining axes.  If the shape of the 
the array are less than 3 axdes, the shards will be accross axis0

Example:
    array.shape = (1,1,200,10000,10000)
    /root/of/array/.zarray
    #Sharded h5 container at axis[-3]
    /root/of/array/0/0/4.hf
    
    4.hf contents:
        key:value
        0.0:bit-string
        0.1:bit-string
        4.6:bit-string
        ...
        ...
'''


import os
import h5py
import shutil
import time
import numpy as np
import random
import uuid
import glob
import threading
import datetime

from zarr.errors import (
    MetadataError,
    BadCompressorError,
    ContainsArrayError,
    ContainsGroupError,
    FSPathExistNotDir,
    ReadOnlyError,
)

from numcodecs.abc import Codec
from numcodecs.compat import (
    ensure_bytes,
    ensure_text,
    ensure_contiguous_ndarray
)
# from numcodecs.registry import codec_registry

from threading import Lock, RLock
# from filelock import Timeout, FileLock, SoftFileLock

from zarr.util import (buffer_size, json_loads, nolock, normalize_chunks,
                       normalize_dimension_separator,
                       normalize_dtype, normalize_fill_value, normalize_order,
                       normalize_shape, normalize_storage_path, retry_call)

from zarr._storage.absstore import ABSStore  # noqa: F401

from zarr._storage.store import Store

class H5_Shard_Store(Store):
    """
    Storage class the uses HDF5 files to shard chunks accross axis [-3]
    
    Currently, the number of axes in the zarr array must be len(zarr_array) >= 4
    """

    def __init__(self, path, normalize_keys=True,swmr=True,
                 verbose=False,verify_write=True,
                 alternative_lock_file_path=None):

        # guard conditions
        path = os.path.abspath(path)
        if os.path.exists(path) and not os.path.isdir(path):
            raise FSPathExistNotDir(path)

        self.path = path if path[-1] != '/' else path[-1]
        self.normalize_keys = normalize_keys
        self._mutex = RLock()
        self.swmr=swmr
        self.verbose = verbose #bool or int >= 1
        self.verify_write = verify_write
        self._files = ['.zarray','.zgroup','.zattrs','.zmetadata']
        self.uuid = str(uuid.uuid1())
        if alternative_lock_file_path is None:
            self.alternative_lock_file_path = alternative_lock_file_path
        else:
            self.alternative_lock_file_path = alternative_lock_file_path if alternative_lock_file_path[-1] != '/' else alternative_lock_file_path[-1]
        

    def __getstate__(self):
        return (self.path, self.normalize_keys, self.swmr, self.verbose,
                self.verify_write, self._files, self.alternative_lock_file_path)
    
    def __setstate__(self, state):
        (self.path, self.normalize_keys, self.swmr, self.verbose,
         self.verify_write, self._files, self.alternative_lock_file_path) = state
        self._mutex = RLock()   
        self.uuid = str(uuid.uuid1())





    def _normalize_key(self, key):
        return key.lower() if self.normalize_keys else key
    
    # def _dset_from_dirStoreFilePath(self,filepath):
    #     base, dset = os.path.split(filepath)
    #     h5_file = os.path.join(base,self._h5_name)
    #     return h5_file,dset

    def _fromfile(self,file,dset):
        """ Read data from a file
        Parameters
        ----------
        fn : str
            Filepath to open and read from.
        Notes
        -----
        Subclasses should overload this method to specify any custom
        file reading logic.
        """
        # Extract Bytes from h5py
        trys = 0
        blockedTrys = 0
        while True:
            try:
                with h5py.File(file,'r',libver='latest', swmr=self.swmr,locking=True) as f:
                    if dset in f:
                        # return f[dset][()]
                        return f[dset][()].tobytes()
                    else:
                        raise KeyError(dset)
                break
            except KeyError:
                raise
            except BlockingIOError:
                wait = 0.5
                blockedTrys += 1
                print('IO Blocked during open for key {}, try #{} : Pausing {} sec'.format(dset, blockedTrys, wait))
                time.sleep(wait)
            except:
                wait = 0.5
                trys += 1
                print('READ Failed for key {}, try #{} : Pausing {} sec'.format(dset, trys, wait))
                if self.verbose == 2:
                    print('READ Failed for key {}, try #{} : Pausing {} sec'.format(dset, trys, wait))
                time.sleep(wait)
                if trys == 500:
                    raise

    
    class LockFileError(Exception):
        pass

    
    # def getLockFile(self,file):
    #     if isinstance(self.alternative_lock_file_path,str):
    #         file = file.replace(self.path,self.alternative_lock_file_path)
    #         # print('New Lockfile Location: {}'.format(file))
    #     try:
    #         ident = threading.get_ident()
    #         return file+'___'+self.uuid + '_' + str(ident) + '.lock'
    #     except:
    #         return file+'___'+self.uuid + '.lock'
    
    def getLockFile(self,file):
        if isinstance(self.alternative_lock_file_path,str):
            file = file.replace(self.path,self.alternative_lock_file_path)
            dirPath = os.path.split(file)[0]
            if not os.path.exists(dirPath):
                os.makedirs(dirPath,exist_ok=True)
        
        return '{}.lock'.format(file)
    
    def isFileLockedByAnotherProcess(self,file):
        present = glob.glob(file+'___*.lock')
        if present == []:
            return False
        # if any([self.uuid not in x for x in present]):
        lockName = self.getLockFile(file)
        if any([lockName not in x for x in present]):
            return True
        else:
            return False
            
        
    def _tofile(self,key, data, file):
        """ Write data to a file
        Parameters
        ----------
        a : array-like
            Data to write into the file.
        fn : str
            Filepath to open and write to.
        Notes
        -----
        Subclasses should overload this method to specify any custom
        file writing logic.
        """
        # Form lock file class
        # lockfile = self.getLockFile(file)
        lockfile = self.getLockFile(file)
        
        trys = 0
        lock_attempts = 0
        is_open=False
        complete = False
        while True:
            try:
                if os.path.exists(lockfile):
                    raise self.LockFileError('Lock file already exists')
                try:
                    # Attempt to take the lock file
                    with open(lockfile,'x') as f:
                        is_open=True
                        pass
                except:
                    raise self.LockFileError('Lock file could not be created')
                
                
                with h5py.File(file,'a',libver='latest',locking=True) as f:
                    f.swmr_mode = self.swmr
                    if key in f:
                        if self.verbose == 2:
                            print('Deleting existing dataset before writing new data : {}'.format(key))
                        del f[key]
                    f.create_dataset(key, data=data)
                
                if is_open and os.path.exists(lockfile):
                    os.remove(lockfile)
                    is_open=False
                    
                if self.verify_write:
                    from_file = self._fromfile(file,key)
                    # print(from_file)
                    # print(data)
                    if from_file == data.tobytes():
                    # if from_file == data:
                        # print('True')
                        pass
                    else:
                        print('errored')
                        raise KeyError(key)
                complete = True
            
            except self.LockFileError:
                lock_attempts += 1
                # tt = random.randrange(1,5)/10
                tt = 0.1
                print('Lock File Not Acquired Trying again in {} seconds : trys {}'.format(tt,lock_attempts))
                time.sleep(tt)
                
                # Look for stuck lockfile and delete if older than 5 minutes
                if not lock_attempts%20:
                    a = datetime.datetime.today() - datetime.datetime.fromtimestamp(os.path.getmtime(lockfile))
                    # 5 minutes lockfile tollerance before deleting
                    try:
                        if a.seconds >= 300:
                            print('{} file is older than 5 minutes: deleting'.format(lockfile))
                            os.remove(lockfile)
                    except:
                        pass
            
            except:
                trys += 1
                # tt = random.randrange(1,10)
                tt = 1
                if self.verbose == 2:
                    print('WRITE Failed for key {}, try #{} : Pausing {} sec'.format(key, trys,tt))
                time.sleep(tt)
                if trys == 36000:
                    raise
            
            finally:
                try:
                    if is_open and os.path.exists(lockfile):
                        os.remove(lockfile)
                    if complete:
                        break
                except:
                    pass
                is_open=False
    
    def _dset_from_dirStoreFilePath(self,key):
        '''
        filepath will include self.path + key ('0.1.2.3.4')
        Chunks will be sharded along the axis[-3] if the length is >= 3
        Otherwise chunks are sharded along axis 0.
        Key stored in the h5 file is the full key for each chunk ('0.1.2.3.4')
        '''
        
        dirs, key = os.path.split(key)
        dirs = os.path.split(dirs)
        
        key = self._normalize_key(key)
        # dirs = tuple([self._normalize_key(x) for x in dirs])
        if key in self._files:
            return os.path.join(self.path,*dirs,key), None
        
        
        try:
            splitKey = key.split('.')
            # if axes are > 3 then the h5 file should be on the 3rd axis
            # else on axis 0
            if len(splitKey) > 3:
                dirs = dirs + tuple(splitKey[:-3])
                fname = splitKey[-3]
            else:
                fname = splitKey[0]
            
            h5_file = os.path.join(self.path,*dirs,fname + '.h5')
            
            # print(h5_file)
            return h5_file, key
        except:
            return os.path.join(self.path,*dirs,key), None
    
    
    def __getitem__(self, key):
        
        if self.verbose:
            print('GET : {}'.format(key))
        
        # #Special case for .zarray file which should be in file system
        # if key == '.zarray' or key == '.zgroup' or key == '.zattrs':
        #     fn = os.path.join(self.path,key)
        #     with open(fn, mode='rb') as f:
        #         return f.read()
        
        file, dset = self._dset_from_dirStoreFilePath(key)
        # print(file)
        # print(dset)
        
        if dset is None:
            # print('Im HEre1')
            try:
                with open(file, mode='rb') as f:
                    # print('Im HEre2')
                    return f.read()
            except:
                # print('Im HEre3')
                if os.path.exists(os.path.join(os.path.split(file)[0],'.zgroup')) and \
                    os.path.exists(os.path.join(os.path.split(file)[0],'.zattrs')):
                        try:
                            # print('Im HEre4')
                            with open(os.path.join(os.path.split(file)[0],'.zattrs'), mode='rb') as f:
                                return f.read()
                        except:
                            pass
                raise KeyError(key)
        
        
        if os.path.exists(file):
            return self._fromfile(file,dset)
        
        # Must raise KeyError when key does not exist for zarr to load defult 'fill' values
        else:
            raise KeyError(key)
                
        raise KeyError(key)

    def __setitem__(self, key, value):
        
        # key = self._normalize_key(key)
        
        if self.verbose:
            print('SET : {}'.format(key))
            # print('SET VALUE : {}'.format(value))
        
        # #Special case for .zarray file which should be in file system
        # if key == '.zarray' or key == '.zgroup' or key == '.zattrs':
        #     if not os.path.exists(self.path):
        #         os.makedirs(self.path)
        #     fn = os.path.join(self.path,key)
        #     with open(fn, mode='wb') as f:
        #         f.write(value)
        #     return
        
        file, dset = self._dset_from_dirStoreFilePath(key)
        # print(file)
        
        if dset is None:
            basePath = os.path.split(file)[0]
            if not os.path.exists(basePath):
                os.makedirs(basePath)
            with open(file, mode='wb') as f:
                f.write(value)
            return
        
        # coerce to flat, contiguous array (ideally without copying)
        value = ensure_contiguous_ndarray(value)
        
        # result = None
        try:
            # destination path for key
            # print(h5_file)
            # print(dset)
            # print(h5_file,dset)
    
            # ensure there is no directory in the way
            if os.path.isdir(file):
                shutil.rmtree(file)
    
            # ensure containing directory exists
            dir_path, _ = os.path.split(file)
            if os.path.isfile(dir_path):
                raise KeyError(key)
                
            os.makedirs(dir_path,exist_ok=True)
    
            #Write to h5 file
            try:
                self._tofile(dset, value, file)
                # result = self._tofile(dset, value, file)
            except:
                pass
        except:
            # basePath = os.path.join(self.path,os.path.split(key)[0])
            # if not os.path.exists(basePath):
            #     os.makedirs(basePath)
            # fullPath = os.path.join(self.path,key)
            # with open(fullPath, mode='wb') as f:
            #     f.write(value)
            return

    def __delitem__(self, key):
        
        '''
        Does not yet handle situation where directorystore path is provided
        as the key.
        '''
        
        
        if self.verbose == 2:
            print('__delitem__')
            print('DEL : {}'.format(key))
        
        file, dset = self._dset_from_dirStoreFilePath(key)
        
        if os.path.exists(key):
            os.remove(key)
        elif dset is None:
            if os.path.exists(file):
                os.remove(file)
        # elif '.h5' in file:
        #     with h5py.File(file,'a',libver='latest', swmr=self.swmr) as f:
        #         del f[dset]
        else:
            with h5py.File(file,'a',libver='latest', swmr=self.swmr,locking=True) as f:
                f.swmr_mode = self.swmr
                del f[dset]

    def __contains__(self, key):
        
        if self.verbose == 2:
            print('__contains__')
            print('CON : {}'.format(key))
        
        file, dset = self._dset_from_dirStoreFilePath(key)
        
        # print(file)
        
        if os.path.exists(file):
            # print('HERE')
            return True
        try:
            if os.path.exists(file):
                with h5py.File(file,'r',libver='latest', swmr=self.swmr,locking=True) as f:
                    return dset in f
        except:
            pass
                
        if self.verbose == 2:
            print('Store does not contain {}'.format(key))
        return False
    
    def __enter__(self):
        return self



    def __eq__(self, other):
        if self.verbose == 2:
            print('eq')
        return (
            isinstance(other, H5Store) and
            self.path == other.path
        )

    def keys(self):
        if self.verbose == 2:
            print('keys')
        if os.path.exists(self.path):
            yield from self._keys_fast(self.path)


    def _keys_fast(self,path, walker=os.walk):
        '''
        This will inspect each h5 file and yield keys in the form of paths.
        
        The paths must be translated into h5_file, key using the function:
            self._dset_from_dirStoreFilePath
        
        Only returns relative paths to store
        '''
        if self.verbose == 2:
            print('_keys_fast')
        for dirpath, _, filenames in walker(path):
            relpath = os.path.relpath(dirpath, path)
            relpath = relpath.replace("\\", "/")
            # print(dirpath)
            for f in filenames:
                # print(f)
                if '.h5' in f:
                    h5_file = os.path.join(dirpath,f)
                    # print(h5_file)
                    # h5_file = os.path.join(dirpath,file_path)
                    with h5py.File(h5_file,'r',libver='latest', swmr=self.swmr,locking=True) as f:
                        dset_list =  list(f.keys())
                    
                else:
                    dset_list = [f]
                
                if relpath == os.curdir:
                    # relpath = relpath.replace("\\", "/")
                    dset_list = [os.path.join(relpath,x) for x in dset_list]
                else:
                    # relpath = relpath.replace("\\", "/")
                    dset_list = ["/".join((relpath, x)) for x in dset_list]
                    # dset_list = [os.path.join(dirpath,x) for x in dset_list]
                dset_list = [x.replace("\\", "/") for x in dset_list]
                dset_list = [x[2:] if x[0:2] == './' else x for x in dset_list]
                dset_list = [x[3:] if x[0:3] == '../' else x for x in dset_list]
                yield from dset_list
                    # yield os.path.join(dirpath,f)

    def _keys_num_estimate(self,walker=os.walk):
        '''
        For only the first h5 file, count number of keys and extrapolate to all h5 files
        -a form of cheating to stop every h5 file from being inspected.  
        This can improve performance by many fold for very large datasets.
        
        Estimates could be off if all keys are not written.  Perhaps a method
        to estimate total keys based on shape + chunks would be better.
        '''
        if self.verbose == 2:
            print('_keys_num_estimate')
        idx = True
        for dirpath, _, filenames in walker(self.path):
            # dirpath = os.path.relpath(dirpath, path)
            # print(dirpath)
            for f in filenames:
                # print(f)
                if idx and '.h5' in f:
                    h5_file = os.path.join(dirpath,f)
                    # print(h5_file)
                    # h5_file = os.path.join(dirpath,file_path)
                    with h5py.File(h5_file,'r',libver='latest', swmr=self.swmr,locking=True) as f:
                        dset_list =  list(f.keys())
                    h5_key_num = len(dset_list)
                    # print('len == {}'.format(h5_key_num))
                    idx = False
                    
                if 'h5_key_num' in locals() and '.h5' in f:
                    yield from range(h5_key_num)
                else:
                    yield 1

    def __iter__(self):
        if self.verbose == 2:
            print('__iter__')
        return self.keys()

    def __len__(self):
        if self.verbose == 2:
            print('__len__')
        return sum((1 for _ in self._keys_num_estimate()))

