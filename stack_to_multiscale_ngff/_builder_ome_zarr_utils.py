# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 12:46:17 2023

@author: awatson
"""

'''
Store mix-in classes for utilities

These classes are designed to be inherited by the builder class (builder.py)
'''

import zarr
import numpy as np

class _builder_ome_zarr_utils:
    
    def build_zattrs(self):
        
        store = self.get_store_from_path(self.out_location)
        # if self.zarr_store_type == H5_Shard_Store:
        #     store = self.zarr_store_type(self.out_location,verbose=1)
        # else:
        #     store = self.zarr_store_type(self.out_location)
        r = zarr.open(store)
        print(r)
        
        multiscales = {}
        multiscales["version"] = "0.5-dev"
        multiscales["name"] = "a dataset"
        multiscales["axes"] = [
            {"name": "t", "type": "time", "unit": "millisecond"},
            {"name": "c", "type": "channel"},
            {"name": "z", "type": "space", "unit": "micrometer"},
            {"name": "y", "type": "space", "unit": "micrometer"},
            {"name": "x", "type": "space", "unit": "micrometer"}
            ]


        # datasets = [] 
        # for res in self.pyramidMap:
        #     scale = {}
        #     scale["path"] = 'scale{}'.format(res)
        #     scale["coordinateTransformations"] = [{
        #         "type": "scale",
        #         "scale": [
        #             1, 1,
        #             round(self.geometry[2]*(res+1)**2,3),
        #             round(self.geometry[3]*(res+1)**2,3),
        #             round(self.geometry[4]*(res+1)**2,3)
        #             ]
        #         }]
            
        #     datasets.append(scale)
            
        datasets = [] 
        for res in self.pyramidMap:
            scale = {}
            scale["path"] = 'scale{}'.format(res)

            z,y,x = self.pyramidMap[res]['resolution']
                
            scale["coordinateTransformations"] = [{
                "type": "scale",
                "scale": [
                    1, 1,
                    round(z,3),
                    round(y,3),
                    round(x,3)
                    ]
                }]
            
            datasets.append(scale)

        multiscales["datasets"] = datasets

        # coordinateTransformations = [{
        #                 # the time unit (0.1 milliseconds), which is the same for each scale level
        #                 "type": "scale",
        #                 "scale": [
        #                     1.0, 1.0, 
        #                     round(self.geometry[0],3),
        #                     round(self.geometry[1],3),
        #                     round(self.geometry[2],3)
        #                     ]
        #             }]

        # multiscales["coordinateTransformations"] = coordinateTransformations

        multiscales["type"] = 'mean'

        multiscales["metadata"] = {
                        "description": "local mean",
                        "any": "other",
                        "details": "here"
                    }

        
        r.attrs['multiscales'] = [multiscales]

        omero = {}
        omero['id'] = 1
        omero['name'] = "a dataset"
        omero['version'] = "0.5-dev"

        colors = [
            'FF0000', #red
            '00FF00', #green
            'FF00FF', #purple
            'FF00FF'  #blue
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
            
            if self.dtype==np.dtype('uint8'):
                end = mx = 255
            elif self.dtype==np.dtype('uint16'):
                end = mx = 65535
            elif self.dtype==float:
                end = mx = 1
            
            new['window'] = {
                "end": end, #Get max value of a low resolution series
                "max": mx, #base on dtype
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
        
        return
    
    def edit_omero_channels(self,channel_num,attr_name,new_value):
        # store = self.zarr_store_type(self.out_location,verbose=1)
        store = self.get_store_from_path(self.out_location)
        r = zarr.open(store)
        
        omero = r.attrs['omero']
        
        channels = omero['channels']
        
        channels[channel_num][attr_name] = new_value
        
        omero['channels'] = channels
        
        r.attrs['omero'] = omero
        
    
    def get_omero_attr(self,attr_name):
        store = self.get_store_from_path(self.out_location)
        # if self.zarr_store_type == H5_Shard_Store:
        #     store = self.zarr_store_type(self.out_location,verbose=1)
        # else:
        #     store = self.zarr_store_type(self.out_location)
        r = zarr.open(store)
        
        omero = r.attrs['omero']
        
        return omero[attr_name]
        
    # def edit_omero_channels(channel_num,attr_name,new_value):
    #     store = zarr.DirectoryStore(r'Z:\toTest\testZarr')
    #     r = zarr.open(store)
        
    #     omero = r.attrs['omero']
        
    #     channels = omero['channels']
        
    #     channels[channel_num][attr_name] = new_value
        
        
    #     r.attrs['omero'] = channels
    
    
    def set_omero_window(self):
        
        channels = self.get_omero_attr('channels')
        print(channels)
        for ch in range(self.Channels):
            #set in write_resolution()
            print(ch)
            channel_dict = channels[ch]
            print(channel_dict)
            window = channel_dict['window']
            print(window)
            window['start'] = self.min[ch]
            window['end'] = self.max[ch]
            print(window)
            self.edit_omero_channels(channel_num=ch,attr_name='window',new_value=window)
        


