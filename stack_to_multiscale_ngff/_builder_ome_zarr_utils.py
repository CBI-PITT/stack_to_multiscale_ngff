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
        r = zarr.open(store)
        print(r)
        
        multiscales = {}
        multiscales["version"] = "0.5-dev"
        multiscales["name"] = self.omero_dict['name'] if self.omero_dict['name'] is not None else ""
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

        multiscales["type"] = self.downSampType

        # Define down sampling methods for inclusion in zattrs
        description = ''
        details = ''
        if multiscales['type'] == 'mean':
            description = '2x downsample of in up to 3 dimensions calculated using the local mean'
            details = 'stack_to_multiscale_ngff._builder_img_processing.local_mean_downsample'
        elif multiscales['type'] == 'max':
            description = '2x downsample of in up to 3 dimensions calculated using the local max'
            details = 'stack_to_multiscale_ngff._builder_img_processing.local_max_downsample'


        multiscales["metadata"] = {
                        "description": description,
                        "details": details
                    }

        
        r.attrs['multiscales'] = [multiscales]

        omero = {}
        omero['id'] = 1
        omero['name'] = self.omero_dict['name'] if self.omero_dict['name'] is not None else ""
        omero['version'] = "0.5-dev"

        colors = self.omero_dict['channels']['color']
        # If the colors dict is not present, then make it with a rotating color palette
        if colors is None:
            colors_palette = [
                'FF0000', #red
                '00FF00', #green
                'FF00FF', #purple
                'FF00FF'  #blue
                ]
            colors = {}
            for idx in range(self.Channels):
                colors[idx] = colors_palette[idx%len(colors_palette)]

        labels = self.omero_dict['channels']['label']
        channels = []
        for chn in range(self.Channels):
            new = {}
            new["active"] = True
            new["coefficient"] = 1
            new["color"] = colors[chn]
            new["family"] = "linear"
            new['inverted'] = False
            new['label'] = labels[chn] if labels is not None else f"Channel{chn}"
            
            if self.dtype==np.dtype('uint8'):
                end = mx = 255
            elif self.dtype==np.dtype('uint16'):
                end = mx = 65535
            elif self.dtype==float:
                end = mx = 1


            new['window'] = {
                "end": self.omero_dict['channels']['window'][chn]['end'] if self.omero_dict['channels']['window'] is not None else end,
                "max": self.omero_dict['channels']['window'][chn]['max'] if self.omero_dict['channels']['window'] is not None else mx,
                "min": self.omero_dict['channels']['window'][chn]['min'] if self.omero_dict['channels']['window'] is not None else 0,
                "start": self.omero_dict['channels']['window'][chn]['start'] if self.omero_dict['channels']['window'] is not None else 0
                }
            
            channels.append(new)
            
        omero['channels'] = channels
        
        omero['rdefs'] = {
            "defaultT": 0,                    # First timepoint to show the user
            "defaultZ": self.omero_dict['rdefs']['defaultZ'] if self.omero_dict['rdefs']['defaultZ'] is not None else self.shape[2]//2, # Default Z section to show the user
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
        


