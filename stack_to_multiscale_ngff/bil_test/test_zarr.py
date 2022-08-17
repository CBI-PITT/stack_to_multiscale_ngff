# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 20:57:49 2022

@author: alpha
"""

import zarr
import numpy as np
import sys
import os

path = r'C:\code\stack_to_multiscale_ngff\stack_to_multiscale_ngff'
if path not in sys.path:
    sys.path.append(path)
    
from stack_to_multiscale_ngff.h5_shard_store import H5_Shard_Store as h5s


root = 'c:/code/testZarr'

# root = r'Z:\testData\test_zarr'

store = h5s(root,verbose=1)
r = zarr.open(store)

class self:
    pass

self = self()

self.in_location = root
self.pyramidMap = {
    0:[(2,2,2),(3,3,3)],
    1:[(2,2,2),(3,3,3)],
    2:[(2,2,2),(3,3,3)],
    3:[(2,2,2),(3,3,3)],
    4:[(2,2,2),(3,3,3)]
    }
self.geometry = (0.35,0.35,1)
self.Channels = 2
self.shape = (1,1,550,23523,56234)

multiscales = {}
multiscales["version"] = "0.5-dev"
multiscales["name"] = os.path.split(self.in_location)[1]
multiscales["axes"] = [
    {"name": "t", "type": "time", "unit": "millisecond"},
    {"name": "c", "type": "channel"},
    {"name": "z", "type": "space", "unit": "micrometer"},
    {"name": "y", "type": "space", "unit": "micrometer"},
    {"name": "x", "type": "space", "unit": "micrometer"}
    ]


datasets = [] 
for res in self.pyramidMap:
    scale = {}
    scale["path"] = 'scale{}'.format(res)
    scale["coordinateTransformations"] = [{
        "type": "scale",
        "scale": [
            1.0, 1.0,
            round(self.geometry[0]*(res+1)**2,3),
            round(self.geometry[1]*(res+1)**2,3),
            round(self.geometry[2]*(res+1)**2,3)
            ]
        }]
    
    datasets.append(scale)

multiscales["datasets"] = datasets

coordinateTransformations = [{
                # the time unit (0.1 milliseconds), which is the same for each scale level
                "type": "scale",
                "scale": [
                    1.0, 1.0, 
                    round(self.geometry[0],3),
                    round(self.geometry[1],3),
                    round(self.geometry[2],3)
                    ]
            }]

multiscales["coordinateTransformations"] = coordinateTransformations

multiscales["type"] = 'mean'

multiscales["metadata"] = {
                "description": "local mean",
                "any": "other",
                "details": "here"
            }

r.attrs['multiscales'] = [multiscales]

omero = {}
omero['id'] = 1
omero['name'] = os.path.split(self.in_location)[1]
omero['version'] = "0.5-dev"

colors = [
    'FF0000',
    '00FF00',
    'FF0000',
    'FF00FF'
    ]
colors = colors*self.Channels
colors = colors[:self.Channels]

channels = []
for chn,clr in zip(range(self.Channels),colors):
    new = {}
    new["active"] = True
    new["coefficient"] = 1
    new["color"] = clr
    new["family"] = "linear"
    new['inverted'] = False
    new['label'] = "Channel{}".format(chn)
    new['window'] = {
        "end": 65535, #Get max value of a low resolution series
        "max": 65535, #base on dtype
        "min": 0, #base on dtype
        "start": 0 #Get min value of a low resolution series
        }
    
    channels.append(new)

omero['channels'] = channels

omero['rdefs'] = {
    "defaultT": 0,                    # First timepoint to show the user
    "defaultZ": self.shape[2]//2,     # First Z section to show the user
    "model": "color"                  # "color" or "greyscale"
    }

r.attrs['omero'] = omero




