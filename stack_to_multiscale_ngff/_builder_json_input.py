# -*- coding: utf-8 -*-
"""
Created on Mon Aug  23 15:08:13 2023

@author: awatson
"""
from datetime import datetime
from typing import Tuple, List, Union, Optional
import os
import warnings
  

from pydantic import BaseModel, StrictStr, StrictInt, ValidationError, field_validator, Field, conlist
# https://docs.pydantic.dev/latest/usage/validators/#field-validators

supportedFileInputs = ('.tif','.tiff','.jp2','.nifti') #First value is default
supportedZarrOutputs = ('.ome.zarr','omehans') #First value is default
supportedCompression = {
                    'zlib':{'clevel':{'default':5, 'min':1, 'max':9},'shuffle':{'default':1,'min':0,'max':1}},
                    'jpegxl':{'clevel':{'default':101,'min':50, 'max':101},'lossy':{'default':False,'min_clevel':101}} #101 lossless

                    } #First key is default

chunkDefaults = {'origional':(1,1,1,1024,1024),'final':(1,1,64,64,64)}

class json_input(BaseModel):

    # Required paths for conversion
    input: Union[str, List[str], Tuple[str]]
    output: str
    
    # Option to switch input file type
    inputFileType: Optional[str] = supportedFileInputs[0]
    
    # Define scale
    scale: Optional[Tuple[float,...]] = Field(default = (1,1,1,1,1), min_items=3, max_items=5)
    
    # Define compressor
    compressor: Optional[str] = tuple(supportedCompression.keys())[0]
    clevel: Optional[int]  =  Field(default = None, validate_default=True)
    shuffle: Optional[int]  =  Field(default = None, validate_default=True)
    lossy: Optional[bool] = Field(default = None, validate_default=True)
    
    # Define temp directory
    tmpDir: Optional[str] = Field(default = os.getcwd(), validate_default=True)
    
    # Option to define origional and final chunks
    origionalChunks: Optional[Tuple[StrictInt,...]] = Field(default = chunkDefaults['origional'], min_items=1, max_items=5)
    finalChunks: Optional[Tuple[StrictInt,...]] = Field(default = chunkDefaults['final'], min_items=1, max_items=5)
    
    # OMERO Metedata
    #colors
    #channelLabels
    #windowLabels
    defaultZ: Optional[int] = None
    
    
    @field_validator('input','output','tmpDir')
    @classmethod
    def normalize_path(cls, v, values, **kwargs):
        if v is None:
            return
        if isinstance(v,str):
            out = [v]
        else:
            out = v
        out = [x.replace('\\','/') for x in out]
        out = [x.replace('//','/') for x in out]
        out = [x[:-1] if x[-1] == '/' else x for x in out]
        return out if len(out) > 1 else out[0]
    
    @field_validator('output')
    @classmethod
    def output_extension_supported(cls, v, values, **kwargs):
        
        if not any([v.endswith(x) for x in supportedZarrOutputs]):
            raise ValueError(f'File type not supported as output: Must use {supportedZarrOutputs}')
        return v.lower()
    
    @field_validator('inputFileType')
    @classmethod
    def file_inputs_ok(cls, v, values, **kwargs):
        if v.lower() not in supportedFileInputs:
            raise ValueError(f'File type not supported as input: Must use {supportedFileInputs}')
        return v.lower()
       
    @field_validator('compressor')
    @classmethod
    def compressor_builder(cls, v, values, **kwargs):
        if v is None:
            return v
        if v.lower() not in supportedCompression:
            raise ValueError(f'Compressor is not supported: Choose from {supportedCompression}')
        return v.lower()
    
    @field_validator('clevel')
    @classmethod
    def clevel_val(cls, v, values, **kwargs):
        print(values)
        if v is None:
            return supportedCompression.get(values.data['compressor'],{}).get('clevel',{}).get('default')
        c_min = supportedCompression.get(values.data['compressor'],{}).get('clevel',{}).get('min')
        c_max = supportedCompression.get(values.data['compressor'],{}).get('clevel',{}).get('max')
        if c_min is not None:
            assert v >= c_min, f'clevel must be >= {c_min}'
        if c_max is not None:
            assert v <= c_max, f'clevel must be <= {c_max}'
        return v
    
    @field_validator('shuffle')
    @classmethod
    def shuffle_val(cls, v, values, **kwargs):
        if v is None:
            return supportedCompression.get(values.data['compressor'],{}).get('shuffle',{}).get('default')
        c_min = supportedCompression.get(values.data['compressor'],{}).get('shuffle',{}).get('min')
        c_max = supportedCompression.get(values.data['compressor'],{}).get('shuffle',{}).get('max')
        if c_min is not None:
            assert v >= c_min, f'shuffle must be >= {c_min}'
        if c_max is not None:
            assert v <= c_max, f'shuffle must be <= {c_max}'
        return v
    
    @field_validator('lossy')
    @classmethod
    def lossy_val(cls, v, values, **kwargs):
        if v is None:
            warnings.warn('Lossy flag is set to False, disabling lossy compression.  Since lossy compression results in loss of information, the user must explictly declare lossy=True to enable this type of compression')
            return False
        clevel = values.data['clevel']
        print(clevel)
        min_clevel = supportedCompression.get(values.data['compressor'],{}).get('lossy',{}).get('min_clevel')
        print(min_clevel)
        if clevel is None or clevel<min_clevel:
            return False
        return True if v == True else False
        
    @field_validator('scale')
    @classmethod
    def scale_val(cls, v, values, **kwargs):
        while len(v) < 5:
            v = (1,*v)
        if v[0] != 1 or v[1] != 1:
            raise ValueError(f'For scale of dimensions (t,c,z,y,x); (t,c) must always be 1. If only 3 dimensions are provided, they are assumed to be (z,y,x)')
        return v
    
    @field_validator('origionalChunks','finalChunks')
    @classmethod
    def chunks_val(cls, v, values, **kwargs):
        while len(v) < 5:
            v = (1,*v)
        return v
    
    #@field_validator('shuffle', always=True)
    #def shuffle_val(cls, v, values, **kwargs):
    #    if v is None:
    #        return supportedCompression[values['compressor']]['shuffle']['default']
    #    c_min = supportedCompression[values['compressor']]['shuffle']['min']
    #    c_max = supportedCompression[values['compressor']]['shuffle']['max']
    #    assert v >= c_min and v <= c_max, f'shuffle must be between {c_min} and {c_max}'
    #    return v


m = json_input(input=['/this//is\\a/fake//path//','/another/\\aweful\\dir/'],output='/another//output.ome.zarr',compressor='jpegxl',clevel=50)
print(m)