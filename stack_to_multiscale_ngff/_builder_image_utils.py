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

