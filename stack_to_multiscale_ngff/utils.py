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
    
def axis_reorganizer(array=None,input_orientation='tczyx'):
    '''
    Return a tuple which transposes an array to 'tczyx' orientation given the known orientation
    Currently assumes that dims 0,1 are always tc

    input_orientation = string designating 3-axis 'x','y','z' orientation
    Examples: 'tczyx','tcxyz','tcyzx','tczxy'
    '''

    assert isinstance(input_orientation,str)
    assert len(input_orientation) == 5
    assert 't' in input_orientation and input_orientation[0] == 't'
    assert 'c' in input_orientation and input_orientation[1] == 'c'
    assert 'z' in input_orientation
    assert 'y' in input_orientation
    assert 'x' in input_orientation

    if array is not None:
        assert len(array.shape) == 5

    orientations = {
        'tczyx': (0,1,2,3,4),
        'tczxy': (0,1,2,4,3),
        'tcxzy': (0,1,3,4,2),
        'tcxyz': (0,1,4,3,2),
        'tcyzx': (0,1,3,2,4),
        'tcyxz': (0,1,4,2,3)
    }
    if array is None:
        return orientations[input_orientation]
    if array is not None:
        return array.transpose(orientations[input_orientation])

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



# def optimize_chunk_shape_3d_2(image_shape,origional_chunks,output_chunks,dtype,chunk_limit_GB):
#
#     '''
#     Grows chunks shape by axis y and x by the origional chunk shape until a
#     defined size in GB is reached
#
#     return tuple of new chunk shape
#     '''
#     y = origional_chunks[1] if origional_chunks[1] > output_chunks[1] else output_chunks[1]
#     x = origional_chunks[2] if origional_chunks[2] > output_chunks[2] else output_chunks[2]
#
#     origional_chunks = (origional_chunks[0],y,x)
#
#     current_chunks = origional_chunks
#     current_size = get_size_GB(current_chunks,dtype)
#
#     print(current_chunks)
#     print(current_size)
#
#     if current_size > chunk_limit_GB:
#         return current_size
#
#     idx = 0
#     chunk_bigger_than_y = True if current_chunks[1] >= image_shape[1] else False
#     chunk_bigger_than_x = True if current_chunks[2] >= image_shape[2] else False
#
#     while current_size <= chunk_limit_GB:
#
#         # last_size = get_size_GB(current_chunks,dtype)
#         last_shape = current_chunks
#
#         chunk_iter_idx = idx%2
#         if chunk_iter_idx == 0 and chunk_bigger_than_y == False:
#             current_chunks = (origional_chunks[0],current_chunks[1]+output_chunks[1],current_chunks[2])
#         elif chunk_iter_idx == 1 and chunk_bigger_than_x == False:
#             current_chunks = (origional_chunks[0],current_chunks[1],current_chunks[2]+output_chunks[2])
#
#         # # Iterate over y first then x
#         # if chunk_bigger_than_y == False:
#         #     current_chunks = (origional_chunks[0],current_chunks[1]+output_chunks[1],current_chunks[2])
#         # elif chunk_bigger_than_x == False:
#         #     current_chunks = (origional_chunks[0],current_chunks[1],current_chunks[2]+output_chunks[2])
#
#         current_size = get_size_GB(current_chunks,dtype)
#
#         print(current_chunks)
#         print(current_size)
#         print('next step chunk limit {}'.format(current_size))
#
#
#         if current_size > chunk_limit_GB:
#             return last_shape
#
#         if  current_chunks[1] > image_shape[1]:
#             chunk_bigger_than_y = True
#
#         if  current_chunks[2] > image_shape[2]:
#             chunk_bigger_than_x = True
#
#         if all([chunk_bigger_than_y,chunk_bigger_than_x]):
#             return last_shape
#
#         idx += 1


def optimize_chunk_shape_3d_2(image_shape, origional_chunks, output_chunks, dtype, chunk_limit_GB):
    '''
    Grows chunks shape by axis y and x by the origional chunk shape until a
    defined size in GB is reached

    return tuple of new chunk shape
    '''
    y = origional_chunks[1] if origional_chunks[1] > output_chunks[1] else output_chunks[1]
    x = origional_chunks[2] if origional_chunks[2] > output_chunks[2] else output_chunks[2]

    origional_chunks = (origional_chunks[0], y, x)

    current_chunks = origional_chunks
    current_size = get_size_GB(current_chunks, dtype)

    print(current_chunks)
    print(current_size)

    if current_size > chunk_limit_GB:
        return current_chunks

    idx = 0
    chunk_bigger_than_z = True if current_chunks[0] >= image_shape[0] else False
    chunk_bigger_than_y = True if current_chunks[1] >= image_shape[1] else False
    chunk_bigger_than_x = True if current_chunks[2] >= image_shape[2] else False

    while current_size <= chunk_limit_GB:

        # last_size = get_size_GB(current_chunks,dtype)
        last_shape = current_chunks

        # chunk_iter_idx = idx % 2
        # if chunk_iter_idx == 0 and chunk_bigger_than_y == False:
        #     current_chunks = (origional_chunks[0], current_chunks[1] + output_chunks[1], current_chunks[2])
        # elif chunk_iter_idx == 1 and chunk_bigger_than_x == False:
        #     current_chunks = (origional_chunks[0], current_chunks[1], current_chunks[2] + output_chunks[2])

        # Iterate over y first then x
        if chunk_bigger_than_y == False:
            current_chunks = (origional_chunks[0],current_chunks[1]+output_chunks[1],current_chunks[2])
        elif chunk_bigger_than_x == False:
            current_chunks = (origional_chunks[0],current_chunks[1],current_chunks[2]+output_chunks[2])
        elif chunk_bigger_than_z == False:
            current_chunks = (origional_chunks[0] + output_chunks[0], current_chunks[1], current_chunks[2])

        current_size = get_size_GB(current_chunks, dtype)

        print(current_chunks)
        print(current_size)
        print('next step chunk limit {}'.format(current_size))

        if current_size > chunk_limit_GB:
            return last_shape

        if current_chunks[0] > image_shape[0]:
            chunk_bigger_than_z = True

        if current_chunks[1] > image_shape[1]:
            chunk_bigger_than_y = True

        if current_chunks[2] > image_shape[2]:
            chunk_bigger_than_x = True

        if all([chunk_bigger_than_z, chunk_bigger_than_y, chunk_bigger_than_x]):
            return last_shape

        idx += 1

