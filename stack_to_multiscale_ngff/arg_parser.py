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
    
    (['-oc','--origionalChunkSize'],int,5,'O',(1,1,1,1024,1024),'store','The chunk size for the higest resolution scale0. Must be 5 integers for axes (TCZYX).'),
    (['-fc','--finalChunkSize'],int,5,'F',(1,1,16,256,256),'store','The chunk size for the lowest resolution scaleX. Must be 5 integers for axes (TCZYX).'),
    (['-cpu'],int,1,'C',[os.cpu_count()],'store','Number of cpus which are available'),
    (['-mem'],int,1,'M',[int(psutil.virtual_memory().free/1024/1024/1024*0.8)],'store','Available RAM in GB: default is 0.8x of free RAM'),
    (['-tmp','--tmpLocation'],str,1,'TMP',['/CBI_FastStore/tmp_dask'],'store','Location for temp files --> high-speed local storage is suggested'),
    (['-ft','--fileType'],str,1,'FT',['tif'],'store','File type for input --> Currently tif,tiff,jp2 and some nifti are supported'),
    (['-s','--scale'],float,5,'S',(1,1,1,1,1),'store','5-dim scale of the datasets (tczyx) in MICRONS'),
    (['-cl','--clevel'],int,1,'CMP',[5],'store','Compression level : Integer 0-9 where 0 is no compression and 9 is the most compression'),
    #Optional arguyments for OME-ZARR OMERO metadata
    (['-ch','--channelLabels'],str,'*','CH',[],'store','A label for each channel'),
    (['-clr','--colors'],str,'*','CLR',[],'store','Color for each channel: by default colors are repeatedly assigned as [green, red, purple, blue,...]'),
    (['-win','--windowLabels'],int,'*','WIN',[],'store','START STOP MIN MAX defining the LUT representation of each channel'),
    (['-n','--name'],str,1,'NAM',[],'store','Name of the dataset'),
    (['-z','--defaultZ'],int,1,'dfZ',[],'store','Default Z-Layer to be displayed during visualization')

    ]

switch = [
    (['-v', '--verbose'], 0,'count','Verbose output : additive more v = greater level of verbosity'),
    (['-vzw', '--verify_zarr_write'], False,'store_true','Immediately verify each chunk written to disk.  Currently only works with H5_Shard_Store'),
    (['-sk', '--skip'], False,'store_true','skip resolution level if it already exist'),
    (['-st','--stopBuild'], True,'store_false','Immediately stop building multiscale NGFF after initializing builder class- only used for development purposes'),
    ]

for var,v_type,nargs,v_help in positional:
    parser.add_argument(var, type=v_type, nargs=nargs,help=v_help)

for var,v_type,nargs,metavar,default,action,v_help in optional:
    parser.add_argument(*var,type=v_type,nargs=nargs,metavar=metavar,default=default,action=action,help=v_help)

for var,default,action,v_help in switch:
    parser.add_argument(*var,default=default,action=action,help=v_help)


# args = parser.parse_args()
# print(args)
# print(args.input)
# print(args.output)
# print(args.mem)
# print(args.cpu)
# print(args.finalChunkSize)
# print(args.origionalChunkSize)
