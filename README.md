# stack_to_multiscale_ngff



## A tool for converting multi-terabyte stacks of images into a multiscale OME-NGFF Zarr



#### By default, the zarr store used is a custom h5_shard_store designed to limit the number of files produced by mimicking a directory store axis[:-3] and sharding chunks across axis[-3] for volumetric data.  For datasets with less than 3 axes, or axis0 is used for sharding.