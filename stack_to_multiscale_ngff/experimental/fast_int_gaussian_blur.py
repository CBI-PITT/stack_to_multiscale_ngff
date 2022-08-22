# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 14:37:49 2022

@author: awatson
"""

import numpy as np
import math
from itertools import product

## Approximate a gaussian blur and 2x downsample

'''
Assume the following distribution for gaussian

1 2 1
2 4 2
1 2 1

'''

'''

1 1 1 1 1 1
1 1 1 1 1 1
1 1 1 1 1 1
1 1 1 1 1 1
1 1 1 1 1 1

'''

'''
2x downsample version, but may not properly approximate a gaussian
'''
# shape = (1024,1024,1024)

# array = np.arange(math.prod(shape),dtype='uint32').reshape(shape)

# # out = np.zeros(array.shape,dtype=array.dtype)

# out = np.zeros((array.shape[0]//2,array.shape[2]//2,array.shape[2]//2),dtype=array.dtype)

# idx = 0
# div = 0
# for z,y,x in product(range(2),range(2),range(2)):
    
#     if sum([x==1 for x in (z,y,x)]) == 0:
#         out += array[z::2,y::2,x::2] * 4
#         div += 4
#         print(4)
#     if sum([x==1 for x in (z,y,x)]) == 1:
#         out += array[z::2,y::2,x::2] * 2
#         div += 2
#         print(2)
#     if sum([x==1 for x in (z,y,x)]) == 2:
#         out += array[z::2,y::2,x::2]
#         div += 1
#         print(1)
#     if sum([x==1 for x in (z,y,x)]) == 3:
#         out += array[z::2,y::2,x::2]
#         div += 1
#         print(1)
    
#     idx += 1
#     # print(idx)
#     # print(div)

# out //= div




shape = (1024,1024,1024)

array = np.zeros(shape,dtype='uint16')
array += 65535

# out = np.zeros(array.shape,dtype=array.dtype)

# pad array with 1 value on all sides
out = np.zeros((array.shape[0]+2,array.shape[2]+2,array.shape[2]+2),dtype='uint32')

idx = 0
div = 0
for z,y,x in product(range(3),range(3),range(3)):
    
    factor = 1
    
    if all((x,y,z)):
        factor = 4
    elif sum([x==1 for x in (z,y,x)]) == 2:
        factor = 2
        
    div += factor
    
    print(div)
        
    for _ in range(factor):
        out[z:-(2-z) if z!=2 else None,
            y:-(2-y) if y!=2 else None,
            x:-(2-x) if x!=2 else None] += array
    
    
print(div)
out //= div
out = out[1:-1,1:-1,1:-1]
out = out[::2,::2,::2]



