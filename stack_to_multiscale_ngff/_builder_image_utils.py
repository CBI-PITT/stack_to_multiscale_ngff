# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 21:11:13 2022

@author: awatson
"""

import zarr
import os
import numpy as np
import tifffile
import skimage
import io
import math
import glob
import shutil
# import imagecodecs
from copy import deepcopy


# file = r'C:\code\testData\191817_05308_CH1.tif'
# file = r'H:\globus\pitt\bil\fMOST RAW\CH1\182725_03717_CH1.tif'


class _builder_image_utils:
    '''
    A mix-in class for builder.py
    '''
    
    def nifti_unpacker(self,file):
        
        import nibabel as nib
        from skimage import io, img_as_uint, img_as_float32
        import numpy as np

        # file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_rawdata.nii"
        # file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_avg_dwi.nii"

        # #Background? Bone?
        # file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_a0.nii"
        # file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_M0_rigid.nii"

        # #Invert of background, bone?
        # file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_fa.nii"

        # #Nothing interesting?
        # file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_adc.nii"
        # file = r"H:\globus\pitt\bil\yongsoo\MRI\P4_JN0167_MTR_rigid.nii"


        fileObj = nib.load(file)

        data = fileObj.get_fdata()

        data = data.astype('uint16')

        if len(data.shape) == 4:
            # Create a mean image accross the last axis
            data = img_as_float32(data)
            data = img_as_uint(np.mean(data,axis=-1))
        
        data = data[::-1,::-1,::-1]
        tmp_img_dir = os.path.join(self.tmp_dir,'img')
        os.makedirs(tmp_img_dir,exist_ok=True)
        
        #Remove any existing files
        filelist = glob.glob(os.path.join(tmp_img_dir, "**/**"))
        for f in filelist:
            try:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)
            except Exception:
                pass
        
        for idx,ii in enumerate(data):
            idx = str(idx).zfill(4)
            fname = 'nii_layer_{}.tif'.format(idx)
            fname = os.path.join(tmp_img_dir,fname)
            print('Writing file {}'.format(fname))
            io.imsave(fname,ii)
        
        return sorted(glob.glob(os.path.join(tmp_img_dir, "*")))



    def jp2_unpacker(self, fileList):
        print(fileList)
        from skimage import io
        from natsort import natsorted
        from dask.delayed import delayed
        import dask
        useGlymur = False
        try:
            # Error if glymur is not installed
            # conda install -c conda-forge glymur
            import glymur
            # present = importlib.util.find_spec("glymur")
            # print(present)
            # if present is None: assert(False)

            jp2file = fileList[0]
            jp2 = glymur.Jp2k(jp2file)
            # glymur.set_option('lib.num_threads', self.cpu_cores)
            glymur.set_option('lib.num_threads', 8)
            # Assume shape is 2D or 3D (y,x) or (y,x,color)
            # Error when trying to access data if openJp2 dependencies are not correct
            lowestRes = jp2[::-1,::-1]
            # If no error assume glymur and current dependencies are installed
            useGlymur = True
            shape = jp2.shape
            dtype = jp2.dtype

        except (Exception,AssertionError):
            ## Fix to deal with fussy PIL and very large jp2 files
            from skimage import io, img_as_uint, img_as_float32
            from PIL import Image, ImageFile
            Image.MAX_IMAGE_PIXELS = 2000000000
            ImageFile.LOAD_TRUNCATED_IMAGES = False # Probably keep this False, but True may solve for partly formed files

            #Load test image
            jp2file = fileList[0]
            jp2 = io.imread(jp2file) # An error may occur here if files are shaped (y,x,color), if so, properly setup glymur to solve the problem
            shape = jp2.shape
            dtype = jp2.dtype

        if useGlymur:
            imread = glymur.Jp2k
        else:
            imread = io.imread

        def write_3_colors_from_jp2(reader, readFile, fileNamePattern, outDirectory, zlayer):
            print(f'Reading File: {readFile}')
            canvas = reader(readFile)[:]
            # canvas = reader(readFile)[::-1,::-1]
            for color in range(3):
                out_base = os.path.join(outDirectory,str(color))
                os.makedirs(out_base, exist_ok=True)
                outFile = fileNamePattern.format(str(color).zfill(2), str(zlayer).zfill(4))
                outFile = os.path.join(out_base, outFile)
                print(f'Writing file: {outFile}')
                tifffile.imwrite(outFile, canvas[:, :, color], bigtiff=True, tile=(1024, 1024))

        # filesList = []
        # files = natsorted(glob.glob(os.path.join(self.in_location, '*.{}'.format(self.fileType))))
        if len(shape) == 2:
            flist = []
            for ii in self.in_location:
                flist.append(natsorted(glob.glob(os.path.join(ii,'*.{}'.format(self.fileType)))))
            return flist

        elif len(shape) == 3 and 3 in shape:

            # Remove any existing files in temp location
            filelist = glob.glob(os.path.join(self.tmp_dir, "**/**"))
            for f in filelist:
                try:
                    if os.path.isfile(f):
                        os.remove(f)
                    elif os.path.isdir(f):
                        shutil.rmtree(f)
                except Exception:
                    pass

            canvas = np.zeros(shape=shape,dtype=dtype)
            tmp_img_dir = os.path.join(self.tmp_dir, 'img')
            os.makedirs(tmp_img_dir, exist_ok=True)
            fname = 'jp2img_c{}_z{}.tif'

            to_compute = []
            for z_layer, file in enumerate(fileList):
                a = delayed(write_3_colors_from_jp2)(imread, file, fname,tmp_img_dir,z_layer)
                to_compute.append(a)
            dask.compute(to_compute,num_workers=self.cpu_cores//4)

            # reader, readFile, fileNamePattern, outDirectory, zlayer

            # for z_layer, file in enumerate(fileList):
            #     print(f'Reading file: {file}')
            #     canvas[:] = imread(file)[:]
            #     for color in range(3):
            #         saveName = os.path.join(tmp_img_dir,fname.format(str(color).zfill(2),str(z_layer).zfill(4)))
            #         print(f'Writing file: {saveName}')
            #         tifffile.imwrite(saveName, canvas[:,:,color], bigtiff=True, tile=(1024,1024))

            flist = []
            for ii in natsorted(glob.glob(os.path.join(tmp_img_dir,'*'))):
                flist.append(natsorted(glob.glob(os.path.join(ii,'*.{}'.format('tif')))))
            print(flist)

            return flist


        #
        # for idx, ii in enumerate(data):
        #     idx = str(idx).zfill(4)
        #     fname = 'nii_layer_{}.tif'.format(idx)
        #     fname = os.path.join(tmp_img_dir, fname)
        #     print('Writing file {}'.format(fname))
        #     io.imsave(fname, ii)
        #
        # return sorted(glob.glob(os.path.join(tmp_img_dir, "*")))

'''
Tiff managers can take a tiff file (tiff_manager) or list of files (tiff_manager_3d)
and present them as sliceable arrays.  

'desired_chunk_depth parameters' allow non-chunked tiff files to appear to be 
chunked by a desireable number of lines for interacting with downstream libraries
like dask array.

Files are only opened during __init__ and when data is requested via slicing

Cloning options are available to maintain the properties of a previously instantiated
manager but with a different file.  This allows for rapid creation of 1000s of 
managers without having to access the file system during __init__ to integrigate
each file.
'''
class tiff_manager:
    def __init__(self,file,desired_chunk_depth=64):
        self.file = file
        
        self.ext = os.path.splitext(file)[-1]
        if self.ext == '.tiff' or self.ext == '.tif':
            img = self._get_tiff_zarr_array()
            self.shape = img.shape
            self.nbytes = img.nbytes
            self.ndim = img.ndim
            self.chunks = img.chunks
            self.dtype = img.dtype
        
        elif self.ext == '.jp2':
            img = self._read_jp2(slice(None))
            self.shape = img.shape
            self.nbytes = img.nbytes
            self.ndim = img.ndim
            self.chunks = (1,self.shape[1])
            self.dtype = img.dtype
        del img
        
        self._desired_chunk_depth = desired_chunk_depth
        self._adjust_chunk_depth()
        
    def __getitem__(self,key):
        # if key == (np.s_[0:0],)*self.ndim:
        if key == (slice(0,0,None),)*self.ndim:
            #Hack to speed up dask array conversions
            return np.asarray([],dtype=self.dtype)
        return self._read_img(key)
    
    # def _read_tiff(self,key):
    #     with tifffile.imread(self.file,aszarr=True) as store:
    #         return zarr.open(store)[key]
        
    def _change_file(self,file):
        self.file = file
    
    def _read_img(self,key):
        if self.ext == '.tiff' or self.ext == '.tif':
            return self._read_tiff(key)
        elif self.ext == '.jp2':
            return self._read_jp2(key)
    
    def _get_tiff_zarr_array(self):
        with tifffile.imread(self.file,aszarr=True) as store:
            return zarr.open(store)
        
    def _read_tiff(self,key):
        print('Read {}'.format(self.file))
        return self._get_tiff_zarr_array()[key]
    
    def _read_jp2(self,key):
        print('Read {}'.format(self.file))
        with open(self.file, 'rb') as f:
            img = io.BytesIO(f.read())
        return skimage.io.imread(img)[key]
    
    def clone_manager_new_file(self,file):
        '''
        Changes only the file associated with the class
        Assumes that the new file shares all other properties
        No attempt is made to verify this
        
        This method is designed for speed.
        It is to be used when 1000s of tiff files must be referenced and 
        it avoids opening each file to inspect metadata
        
        Returns: a new instance of the class with a different filename
        '''
        new = deepcopy(self)
        new._change_file(file)
        return new
        
    def _adjust_chunk_depth(self):
        if self._desired_chunk_depth >= self.shape[0]:
            self.chunks = (self.shape[0],*self.chunks[1:])
        elif self._desired_chunk_depth % self.chunks[0] == 0:
                self.chunks = (self._desired_chunk_depth,*self.chunks[1:])
    


# Simple 3d tiff_manager without any chunk_depth options
class tiff_manager_3d:
    def __init__(self,fileList):
        assert isinstance(fileList,(list,tuple))
        self.fileList = fileList
        self.ext = os.path.splitext(fileList[0])[-1]
        
        if self.ext == '.tiff' or self.ext == '.tif':
            img = self._get_tiff_zarr_array(0)
            self.shape = img.shape
            self.nbytes = img.nbytes
            self.ndim = img.ndim
            self.chunks = img.chunks
            self.dtype = img.dtype
        
        elif self.ext == '.jp2':
            img = self._read_jp2(slice(None),0)
            self.shape = img.shape
            self.nbytes = img.nbytes
            self.ndim = img.ndim
            self.chunks = (1,self.shape[1])
            self.dtype = img.dtype
        del img
        
        self._conv_3d()
        
    def _conv_3d(self):
        z_depth = len(self.fileList)
        self.shape = (z_depth,*self.shape)
        self.nbytes = int(self.nbytes*z_depth)
        self.ndim = 3
        self.chunks = (z_depth,*self.chunks)
    
    
    def __getitem__(self,key):
        #Hack to speed up dask array conversions
        if key == (slice(0,0,None),)*self.ndim:
            return np.asarray([],dtype=self.dtype)
        
        return self._get_3d(key)
    
    @staticmethod
    def _format_slice(key):
        # print('In Slice {}'.format(key))
        if isinstance(key,slice):
            return (key,)
        
        if isinstance(key,int):
            return (slice(key,key+1,None),)
        
        if isinstance(key,tuple):
            out_slice = []
            for ii in key:
                if isinstance(ii,slice):
                    out_slice.append(ii)
                elif isinstance(ii,int):
                    out_slice.append(slice(ii,ii+1,None))
                else:
                    out_slice.append(ii)
                    
        # print('Out Slice {}'.format(out_slice))
        return tuple(out_slice)
        
    def _slice_out_shape(self,key):
        key = self._format_slice(key)
        key = list(key)
        if isinstance(key,int):
            key = [slice(key,None,None)]
            # print(key)
        out_shape = []
        for idx,_ in enumerate(self.shape):
            if idx < len(key):
                if isinstance(key[idx],int):
                    key[idx] = slice(key[idx],None,None)
                # print(key)
                test_array = np.asarray((1,)*self.shape[idx],dtype=bool)
                # print(test_array)
                # print(key[idx])
                test_array = test_array[key[idx]].shape[0]
                # print(test_array)
                out_shape.append(
                        test_array
                    )
            else:
                out_shape.append(self.shape[idx])
        out_shape = tuple(out_shape)
        # print(out_shape)
        return out_shape
        
    
    def _read_img(self,key,idx):
        if self.ext == '.tiff' or self.ext == '.tif':
            return self._read_tiff(key,idx)
        elif self.ext == '.jp2':
            return self._read_jp2(key,idx)
    
    def _get_tiff_zarr_array(self,idx):
        with tifffile.imread(self.fileList[idx],aszarr=True) as store:
            return zarr.open(store)
        
    def _read_tiff(self,key,idx):
        print('Read {}'.format(self.fileList[idx]))
        return self._get_tiff_zarr_array(idx)[key]
    
    def _read_jp2(self,key,idx):
        print('Read {}'.format(self.fileList[idx]))
        with open(self.fileList[idx], 'rb') as f:
            img = io.BytesIO(f.read())
        return skimage.io.imread(img)[key]
        # return skimage.io.imread(self.fileList[idx])[key]
    
    
    def _get_3d(self,key):
        key = self._format_slice(key)
        shape_of_output = self._slice_out_shape(key)
        canvas = np.zeros(shape_of_output,dtype=self.dtype)
        # print(canvas.shape)
        
        # if len(key) == 1:
        #     key = key[slice(None)]
        
        for idx in range(canvas.shape[0]):
            two_d = key[1:]
            # print(two_d)
            if len(two_d) == 1:
                two_d = two_d[0]
            # print(two_d)
            canvas[idx] = self._read_img(two_d,idx)
        return canvas
    
    def _change_file_list(self,fileList):
        old_zdepth = self.shape[0]
        
        self.fileList = fileList
        
        new_zdepth = len(self.fileList)
        self.shape = (new_zdepth,*self.shape[1:])
        self.nbytes = int(self.nbytes / old_zdepth * new_zdepth)
        self.chunks = (new_zdepth,*self.chunks[1:])
        
    
    def clone_manager_new_file_list(self,fileList):
        '''
        Changes only the file associated with the class
        Assumes that the new file shares all other properties
        No attempt is made to verify this
        
        This method is designed for speed.
        It is to be used when 1000s of tiff files must be referenced and 
        it avoids opening each file to inspect metadata
        
        Returns: a new instance of the class with a different filename
        '''
        new = deepcopy(self)
        new._change_file_list(fileList)
        return new
    
    
def get_size_GB(shape,dtype):
    
    current_size = math.prod(shape)/1024**3
    if dtype == np.dtype('uint8'):
        pass
    elif dtype == np.dtype('uint16'):
        current_size *=2
    elif dtype == np.dtype('float32'):
        current_size *=4
    elif dtype == float:
        current_size *=8
    
    return current_size
    
def optimize_chunk_shape_3d(image_shape,origional_chunks,dtype,chunk_limit_GB):
    
    current_chunks = origional_chunks
    current_size = get_size_GB(current_chunks,dtype)
    
    print(current_chunks)
    print(current_size)
    
    if current_size > chunk_limit_GB:
        return current_size
    
    idx = 0
    while current_size <= chunk_limit_GB:
        
        last_size = get_size_GB(current_chunks,dtype)
        last_shape = current_chunks
        
        chunk_iter_idx = idx%2
        if chunk_iter_idx == 0:
            current_chunks = (origional_chunks[0],current_chunks[1]+origional_chunks[1],current_chunks[2])
        elif chunk_iter_idx == 1:
            current_chunks = (origional_chunks[0],current_chunks[1],current_chunks[2]+origional_chunks[2])
            
        current_size = get_size_GB(current_chunks,dtype)
        
        print(current_chunks)
        print(current_size)
        print('next step chunk limit {}'.format(current_size))
        
        
        if current_size > chunk_limit_GB:
            return last_shape
        if any([x>y for x,y in zip(current_chunks,image_shape)]):
            return last_shape
        
        idx += 1









