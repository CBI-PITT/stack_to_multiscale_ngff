# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 17:11:50 2022

@author: awatson
"""


import math
import numpy as np

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
    
    '''
    Grows chunks shape by axis y and x by the origional chunk shape until a 
    defined size in GB is reached
    
    return tuple of new chunk shape
    '''
    
    current_chunks = origional_chunks
    current_size = get_size_GB(current_chunks,dtype)
    
    print(current_chunks)
    print(current_size)
    
    if current_size > chunk_limit_GB:
        return current_size
    
    idx = 0
    chunk_bigger_than_y = True if current_chunks[1] >= image_shape[1] else False
    chunk_bigger_than_x = True if current_chunks[2] >= image_shape[2] else False
    
    while current_size <= chunk_limit_GB:
        
        # last_size = get_size_GB(current_chunks,dtype)
        last_shape = current_chunks
        
        chunk_iter_idx = idx%2
        if chunk_iter_idx == 0 and chunk_bigger_than_y == False:
            current_chunks = (origional_chunks[0],current_chunks[1]+origional_chunks[1],current_chunks[2])
        elif chunk_iter_idx == 1 and chunk_bigger_than_x == False:
            current_chunks = (origional_chunks[0],current_chunks[1],current_chunks[2]+origional_chunks[2])
            
        current_size = get_size_GB(current_chunks,dtype)
        
        print(current_chunks)
        print(current_size)
        print('next step chunk limit {}'.format(current_size))
        
        
        if current_size > chunk_limit_GB:
            return last_shape
        
        if  current_chunks[1] > image_shape[1]:
            chunk_bigger_than_y = True
        
        if  current_chunks[2] > image_shape[2]:
            chunk_bigger_than_x = True
        
        if all([chunk_bigger_than_y,chunk_bigger_than_x]):
            return last_shape
        
        idx += 1






