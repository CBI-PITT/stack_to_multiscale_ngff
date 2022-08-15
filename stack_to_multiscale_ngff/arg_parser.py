# -*- coding: utf-8 -*-
"""
Created on Sat Aug 13 18:43:51 2022

@author: alpha
"""

import argparse
import os
import psutil
psutil.virtual_memory()

# parser = argparse.ArgumentParser(description='Process some integers.')
# parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                     help='an integer for the accumulator')
# parser.add_argument('--sum', dest='accumulate', action='store_const',
#                     const=sum, default=max,
#                     help='sum the integers (default: find the max)')

# args = parser.parse_args()
# print(args.accumulate(args.integers))

parser = argparse.ArgumentParser(description='''
                                 Form a multiresolution chunked
                                 zarr-NGFF from a TIFF series.
                                 ''')

positional = [
    ('input',str,'+','One or multiple input directores which contain tiff files to be converted.'),
    ('output', str, 1, 'Output directory for multiresolution series.')
    ]

optional = [
    
    (['-oc','--origionalChunkSize'],int,5,'O',(1,1,4,1024,1024),'store','The chunk size for the higest resolution scale0. Must be 5 integers for axes (TCZYX).'),
    (['-fc','--finalChunkSize'],int,5,'F',(1,1,128,128,128),'store','The chunk size for the lowest resolution scaleX. Must be 5 integers for axes (TCZYX).'),
    (['-cpu'],int,1,'C',os.cpu_count(),'store','Number of cpus which are available'),
    (['-mem'],int,1,'M',int(psutil.virtual_memory().free/1024/1024/1024*.8),'store','Available RAM in GB: default is 0.8x of free RAM')
    
    ]

switch = [
    (['-v', '--verbose'], 0,'count','Verbose output : additive more v = greater level of verbosity')
    ]

for var,v_type,nargs,v_help in positional:
    parser.add_argument(var, type=v_type, nargs=nargs,help=v_help)

for var,v_type,nargs,metavar,default,action,v_help in optional:
    parser.add_argument(*var,type=v_type,nargs=nargs,metavar=metavar,default=default,action=action,help=v_help)

for var,default,action,v_help in switch:
    parser.add_argument(*var,default=default,action=action,help=v_help)


args = parser.parse_args()
print(args)
print(args.input)
print(args.output)