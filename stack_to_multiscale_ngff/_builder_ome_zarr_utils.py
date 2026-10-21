# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 12:46:17 2023

@author: awatson
"""

'''
Store mix-in classes for utilities

These classes are designed to be inherited by the builder class (builder.py)

OME-Zarr metadata:
- zarr v3 output (default) follows NGFF 0.6: attributes.ome =
  {"version": "0.6", "multiscales": [...], "omero": {...}} stored in zarr.json.
- zarr v2 output follows NGFF 0.4: attributes.multiscales = [{"version": "0.4", ...}]
  stored in .zattrs.
The 'omero' display metadata is written both nested (attributes.ome.omero, 0.6)
and at the top level (attributes.omero) so that current and legacy readers can
find it. Metadata is published only after all resolution levels finish writing,
so aborted output is not advertised as a complete image.
'''

import zarr
import numpy as np

class _builder_ome_zarr_utils:

    def get_root_group(self, mode='r+'):
        return zarr.open_group(self.out_location, mode=mode, zarr_format=self.zarr_format)

    def _ngff_axes(self, discrete_channel=False):
        axes = [
            {"name": "t", "type": "time", "unit": "millisecond"},
            {"name": "c", "type": "channel"},
            {"name": "z", "type": "space", "unit": "micrometer"},
            {"name": "y", "type": "space", "unit": "micrometer"},
            {"name": "x", "type": "space", "unit": "micrometer"},
        ]
        if discrete_channel:
            axes[1]["discrete"] = True
        return axes

    def _build_omero(self):
        omero = {}
        omero['id'] = 1
        omero['name'] = self.omero_dict['name'] if self.omero_dict['name'] is not None else ""

        colors = self.omero_dict['channels']['color']
        # If the colors dict is not present, then make it with a rotating color palette
        if colors is None:
            colors_palette = [
                'FF0000', #red
                '00FF00', #green
                'FF00FF', #purple
                '0000FF'  #blue
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
            new['label'] = labels[chn] if labels is not None else "Channel{}".format(chn)

            if self.dtype==np.dtype('uint8'):
                mx = 255
            elif self.dtype==np.dtype('uint16'):
                mx = 65535
            elif self.dtype==np.dtype('float32') or self.dtype==float:
                mx = 1

            windows = self.omero_dict['channels']['window']
            new['window'] = {
                "end": windows[chn]['end'] if windows is not None else mx,
                "max": windows[chn]['max'] if windows is not None else mx,
                "min": windows[chn]['min'] if windows is not None else 0,
                "start": windows[chn]['start'] if windows is not None else 0
                }

            channels.append(new)

        omero['channels'] = channels

        omero['rdefs'] = {
            "defaultT": 0,                    # First timepoint to show the user
            "defaultZ": self.omero_dict['rdefs']['defaultZ'] if self.omero_dict['rdefs']['defaultZ'] is not None else self.shape[2]//2, # Default Z section to show the user
            "model": "color"                  # "color" or "greyscale"
            }

        return omero

    def _build_downsample_metadata(self):
        '''
        Metadata about the downscaling method (NGFF multiscales.metadata).
        '''
        meta = {"boundary": "edge"}
        if self.downSampType == 'mean':
            meta["description"] = 'downsample calculated using the local mean'
            meta["method"] = 'dask.array.coarsen(np.mean)'
            if self.dtype.kind in 'ui':
                meta["rounding"] = 'nearest_even_for_integer'
        elif self.downSampType == 'max':
            meta["description"] = 'downsample calculated using the local max'
            meta["method"] = 'dask.array.coarsen(np.max)'
        return meta


    def _build_datasets_transforms(self, include_input_output=True):
        '''
        Per-dataset coordinateTransformations mapping each level's array
        coordinates to physical coordinates.

        scale = voxel size at each resolution level in physical units.
        translation = (pixel-size-at-resolution-N - pixel-size-at-resolution-0) / 2
        per spatial axis (voxel-center alignment for binning downsampling).

        include_input_output: NGFF 0.6 style with explicit input/output
        coordinate system references (and scale+translation wrapped in a
        sequence). NGFF 0.5 style (include_input_output=False) emits plain
        scale and translation transforms, translation listed after scale.
        '''
        base_resolution = self.pyramidMap[0]['resolution']
        datasets = []
        cumulative = [1, 1, 1]
        for res in sorted(self.pyramidMap):
            path = 'scale{}'.format(res)
            if res > 0:
                cumulative = [c * d for c, d in zip(cumulative, self.pyramidMap[res]['downsamp'])]
            scale = [1, 1] + [round(float(r), 3) for r in self.pyramidMap[res]['resolution']]
            translation = [0, 0] + [round(float(b) * (c - 1) / 2.0, 6) for b, c in zip(base_resolution, cumulative)]
            if include_input_output:
                if any(t != 0 for t in translation):
                    transformation = {
                        "type": "sequence",
                        "input": {"path": path},
                        "output": {"name": "intrinsic"},
                        "transformations": [
                            {"type": "scale", "scale": scale},
                            {"type": "translation", "translation": translation},
                        ],
                    }
                else:
                    transformation = {
                        "type": "scale",
                        "scale": scale,
                        "input": {"path": path},
                        "output": {"name": "intrinsic"},
                    }
                datasets.append({"path": path, "coordinateTransformations": [transformation]})
            else:
                transformations = [{"type": "scale", "scale": scale}]
                if any(t != 0 for t in translation):
                    transformations.append({"type": "translation", "translation": translation})
                datasets.append({"path": path, "coordinateTransformations": transformations})
        return datasets

    def _build_multiscales_0_6(self):
        multiscales = {
            "name": self.omero_dict['name'] if self.omero_dict['name'] is not None else "",
            "type": self.downSampType,
            "metadata": self._build_downsample_metadata(),
            "coordinateSystems": [{"name": "intrinsic", "axes": self._ngff_axes(discrete_channel=True)}],
            "datasets": self._build_datasets_transforms(),
        }
        return multiscales

    def _build_multiscales_0_5(self):
        '''
        NGFF 0.5: like 0.6 but without coordinateSystems, without input/output
        coordinate system references in the per-dataset transforms, and
        without the 0.6-only 'discrete' axis field.
        '''
        multiscales = {
            "name": self.omero_dict['name'] if self.omero_dict['name'] is not None else "",
            "type": self.downSampType,
            "metadata": self._build_downsample_metadata(),
            "axes": self._ngff_axes(),
            "datasets": self._build_datasets_transforms(include_input_output=False),
        }
        return multiscales

    def _build_multiscales_0_4(self):
        datasets = []
        for res in sorted(self.pyramidMap):
            scale = {
                "path": 'scale{}'.format(res),
                "coordinateTransformations": [{
                    "type": "scale",
                    "scale": [1, 1] + [round(float(r), 3) for r in self.pyramidMap[res]['resolution']],
                }],
            }
            datasets.append(scale)

        multiscales = {
            "version": "0.4",
            "name": self.omero_dict['name'] if self.omero_dict['name'] is not None else "",
            "axes": self._ngff_axes(),
            "datasets": datasets,
            "type": self.downSampType,
            "metadata": self._build_downsample_metadata(),
        }
        return multiscales

    def publish_metadata(self):
        '''
        Publish OME-Zarr metadata. Must be called only after all resolution
        levels finish writing so aborted output is not advertised as a
        complete OME-NGFF multiscale image.
        '''
        r = self.get_root_group()
        omero = self._build_omero()
        if self.ngff_version == 0.6:
            ome = {
                "version": "0.6",
                "multiscales": [self._build_multiscales_0_6()],
                "omero": omero,
            }
            r.attrs["ome"] = ome
            # Also write omero at the top level (0.4 convention) for legacy readers
            r.attrs["omero"] = omero
        elif self.ngff_version == 0.5:
            ome = {
                "version": "0.5",
                "multiscales": [self._build_multiscales_0_5()],
                "omero": omero,
            }
            r.attrs["ome"] = ome
            # Also write omero at the top level (0.4 convention) for legacy readers
            r.attrs["omero"] = omero
        else:
            r.attrs["multiscales"] = [self._build_multiscales_0_4()]
            r.attrs["omero"] = omero
        print('Published OME-Zarr metadata')

    def set_omero_window(self):
        '''
        Store per channel min/max (calculated during downsampling) as the
        default display window. Consumed later by publish_metadata().
        '''
        windows = self.omero_dict['channels']['window']
        if windows is None:
            windows = {}
            self.omero_dict['channels']['window'] = windows

        if self.dtype==np.dtype('uint8'):
            mx = 255
        elif self.dtype==np.dtype('uint16'):
            mx = 65535
        elif self.dtype==np.dtype('float32') or self.dtype==float:
            mx = 1

        for ch in range(self.Channels):
            windows[ch] = {
                "start": self.min[ch],
                "end": self.max[ch],
                "min": 0,
                "max": mx,
            }
