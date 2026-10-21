# stack_to_multiscale_ngff



## A tool for converting multi-terabyte stacks of images into a multiscale OME-NGFF Zarr



#### Get involved:

If you identify a bug or have a suggestion please open an [issue](https://github.com/CBI-PITT/stack_to_multiscale_ngff/issues).

If you wish to submit a pull request, do so [here](https://github.com/CBI-PITT/stack_to_multiscale_ngff/pulls).

If this conversion tool has been useful to you, please [let us know](mailto:alan.watson@pitt.edu).



Install:

```bash
# Clone the repo
git clone https://github.com/CBI-PITT/stack_to_multiscale_ngff.git
# cd to the clone
cd stack_to_multiscale_ngff

# Create a virtual environment
conda create -n stack_to_multiscale_ngff python=3.12 -y
# Activate the virtual environment
conda activate stack_to_multiscale_ngff

# Install stack_to_multiscale_ngff
pip install -e .

```



#### *The NGFF version of the output is selected with --zarrFormat (default 0.6).  

###### 1)	'--zarrFormat 0.6' (default) writes a sharded [zarr v3](https://zarr-specs.readthedocs.io/en/latest/v3/core/v3.0.html) output with [OME-NGFF 0.6](https://ngff.openmicroscopy.org/specifications/0.6/index.html) metadata.  Sharding greatly reduces the number of files created: each shard is one physical storage object containing many inner chunks.

###### 2)	'--zarrFormat 0.5' writes a sharded [zarr v3](https://zarr-specs.readthedocs.io/en/latest/v3/core/v3.0.html) output with [OME-NGFF 0.5](https://ngff.openmicroscopy.org/specifications/0.5/index.html) metadata.

###### 3)	'--zarrFormat 0.4' writes a chunked [zarr v2](https://zarr-specs.readthedocs.io/en/latest/v2/v2.0.html) output with [OME-NGFF 0.4](https://ngff.openmicroscopy.org/specifications/0.4/index.html) metadata for maximum compatibility with older readers.



Example:

```bash
python ~/stack_to_multiscale_ngff/stack_to_multiscale_ngff/builder.py '/path/to/tiff/stack/channel1' '/path/to/tiff/stack/channel2' '/path/to/tiff/stack/channel3' '/path/to/output/multiscale.ome.zarr' --scale 1 1 0.280 0.114 0.114 --origionalChunkSize 1 1 1 1024 1024 --finalChunkSize 1 1 64 64 64 --fileType tif
```



<u>Let's break down how to use the converter:</u>

```bash
python ~/stack_to_multiscale_ngff/stack_to_multiscale_ngff/builder.py
```

Above, we specify that we want to run the 'builder.py' script which manages the conversion.



```bash
'/path/to/tiff/stack/channel1' '/path/to/tiff/stack/channel2' '/path/to/tiff/stack/channel3'
```

Next we pass the paths(s) to directories where a TIFF z-series is stored.  Each directory must contain file for only 1 channel.  If the directory specified contains subdirectories, each subdirectory is assumed to contain a z-series for each channel.  In the above examples, we will convert a 3 channel z-series. 



```bash
'/path/to/output/multiscale.ome.zarr'
```

Next we pass the output path.  The OME-Zarr will be stored in this path.  By default the output is a sharded zarr v3 store with OME-NGFF 0.6 metadata (see --zarrFormat).  For compatibility purposes, we recommend appending the extension  '.ome.zarr' which signals to down-stream applications how to understand the data.  Use '--zarrFormat 0.4' to write a chunked zarr v2 output with OME-NGFF 0.4 metadata instead (or '--zarrFormat 0.5' for sharded zarr v3 with OME-NGFF 0.5 metadata).  Writing is massively parallel and shard-safe: one dask task writes exactly one complete shard (or chunk for v2), so different workers always write different shards simultaneously and no locking is required.



```bash
--scale 1 1 0.280 0.114 0.114
```

Here we specify the scale in microns of the original data. Scale is always represented as 5-axis with axis t and c always being 1 and axes z, y, and x being indicated in microns. The scale of our example in microns is (0.280 0.114 0.114):(z,y,x). time and channel are always specified as 1 (1,1):(t,c).  Thus scale for this example scale is specified as:   --scale 1 1 0.280 0.114 0.114



```bash
--origionalChunkSize 1 1 1 1024 1024 --finalChunkSize 1 1 64 64 64
```

Here we specify the chunk size to be used for storing the data. This can be a very important consideration depending on your down stream use case. --origionalChunkSize specifies the starting chunk size for the highest resolution information and with each scale, the application will converge towards --finalChunkSize as it approaches the lowest resolution information. By default --origionalChunkSize are (1,1,1,1024,1024) and --finalChunkSize are (1,1,64,64,64). Chunks must always be represented as 5-axis (t,c,z,y,x)

-- In the the author's opinion, the default chunks sizes represent a good trade off between disk access and file transfer size over the internet. The anisotropic nature of chunks at high-resolution before converging on isotropic chunks at low resolution offers a compromise between efficient 3D rendering at low resolutions and focused access to the highest-resolution for computation.  *Users should optimize chunk sizes individual use case.*



```bash
--fileType tif
# options: tif, tiff, jp2 (default: tif)
# some nifti are supported, but it is experimental
```

Here we specify the file extension for the images files that will be converted to ome-zarr.



**Usage:**

```
python ~/stack_to_multiscale_ngff/stack_to_multiscale_ngff/builder.py --help

usage: builder.py [-h] [-oc O O O O O] [-fc F F F F F] [-sh SH SH SH SH SH]
                  [-zf ZF] [-cpu C] [-mem M] [-tmp TMP] [-ft FT]
                  [-s S S S S S] [-cmp CMP] [-cl CMP] [-cmpms CMP] [-clms CMP]
                  [-ch [CH ...]] [-clr [CLR ...]] [-win [WIN ...]] [-n NAM]
                  [-z dfZ] [-dst DSM] [-v] [-sk] [-st] [-df] [-bt] [-los]
                  [-losms]
                  input [input ...] output

Form a multiresolution chunked zarr-NGFF from a TIFF series.

positional arguments:
  input                 One or multiple input directores which contain tiff
                        files to be converted.
  output                Output directory for multiresolution series.

options:
  -h, --help            show this help message and exit
  -oc O O O O O, --origionalChunkSize O O O O O
                        The chunk size for the higest resolution scale0. Must
                        be 5 integers for axes (TCZYX).
  -fc F F F F F, --finalChunkSize F F F F F
                        The chunk size for the lowest resolution scaleX. Must
                        be 5 integers for axes (TCZYX).
  -sh SH SH SH SH SH, --shardShape SH SH SH SH SH
                        Shard size for sharded zarr v3 output. Must be 5
                        integers for axes (TCZYX). Each spatial dim must be a
                        multiple of the largest chunk size for that axis.
                        Default: 4x the largest chunk size along z, largest
                        chunk along y/x.
  -zf ZF, --zarrFormat ZF
                        NGFF version of the output: 0.6 (default, sharded
                        zarr v3), 0.5 (sharded zarr v3), or 0.4 (chunked,
                        zarr v2).
  -cpu C                Number of cpus which are available
  -mem M                Available RAM in GB: default is 0.8x of free RAM
  -tmp TMP, --tmpLocation TMP
                        Location for temp files --> high-speed local storage
                        is suggested
  -ft FT, --fileType FT
                        File type for input --> Currently tif,tiff,jp2 and
                        some nifti are supported
  -s S S S S S, --scale S S S S S
                        5-dim scale of the datasets (tczyx) in MICRONS
  -cmp CMP, --compression CMP
                        Compression method (zstd,jpegxl)
  -cl CMP, --clevel CMP
                        Compression level : Integer 0-9 zstd (default 5), 50-100 jpegxl
  -ch [CH ...], --channelLabels [CH ...]
                        A label for each channel
  -clr [CLR ...], --colors [CLR ...]
                        Color for each channel: by default colors are repeatedly assigned as [green, red, purple, blue,...]
  -win [WIN ...], --windowLabels [WIN ...]
                        START END MIN MAX defining the LUT representation of each channel
  -n NAM, --name NAM    Name of the dataset
  -z dfZ, --defaultZ dfZ
                        Default Z-Layer to be displayed during visualization
  -dst DSM, --downSampleType DSM
                        Down sample method. Options are mean and max (default: mean
  -v, --verbose         Verbose output : additive more v = greater level of verbosity
  -sk, --skip           skip resolution level if it already exist
  -st, --stopBuild      Immediately stop building multiscale NGFF after initializing builder class- only used for development purposes
  -df, --directToFinalChunks
                        Use final chunks for all multiscales except full resolution
  -los, --lossy         Use lossy compression, this only matters if using jpegxl and it MUST be selected for lossy compression to be enabled
```



**OMERO Metadata:**

The OME metadata associated with OME-zarr allows users to specify Name of Dataset, Channel labels, Colors, Lookup Table (LUT) window settings and default Z.  These values are used by some, visualization tools to customize the default view upon opening. stack_to_multiscale_ngff will attempt to determine the LUT settings window automatically based on the full resolution data.  The default Z will be the middle z-layer.  However, the channel labels and colors will receive default values.  

The user can specify this information manually using the following options:

1) Name of Dataset:

```bash
--name "My Favorite Experiment"
```

2. Channel Labels:

```bash
--channelLabels "my favorite gene" my_second_favorite gfp 
```

3. [Colors](https://github.com/CBI-PITT/stack_to_multiscale_ngff/blob/892c69a811c44a4e49071ce5335bd803e78f06a5/stack_to_multiscale_ngff/_builder_colors.py#L602): 

```bash
--colors green red purple
# Specify common names of colors for each channel
```

4. LUT Windows: START END MIN MAX

<img src="https://raw.githubusercontent.com/CBI-PITT/stack_to_multiscale_ngff/main/stack_to_multiscale_ngff/images/LUT.png" alt="LUT" width="200"/>

```bash
 --windowLabels 1771 8085 1111 11944 500 20000 0 65534 0 65534 0 65534
 # must specify 4 integers for each channel
```

5. Default Z:

```bash
--defaultZ 525
# Integer defines the z-layer that is displayed by default
```



**Advanced Usage:**

Down sample method:

The method used to calculate multiscale images can be specified using the --downSampleType switch.  Options are mean or max.  Default is mean. The method uses a 3D local mean/max filter to calculate the lower resolution data.

```bash
--downSampleType max
# default mean.  Options: [mean, max]
```



Compression:

The compression method and level can be chosen.  For sharded zarr v3 output (default), only [Blosc zstd](https://numcodecs.readthedocs.io/en/stable/blosc.html) is supported (JPEG XL is not available as a zarr v3 codec).  For zarr v2 output ('--zarrFormat 0.4'), [Blosc zstd](https://numcodecs.readthedocs.io/en/stable/blosc.html) and [jpegxl](https://github.com/cgohlke/imagecodecs/blob/master/imagecodecs/_jpegxl.pyx) are supported.

Default (lossless): zstd, compression level 5, BITSHUFFLE filter

```bash
--compression 'zstd' --clevel 5 # (Default, options 0-9)
--compression 'jpegxl' # (lossless jpegxl, zarr v2 output only)

--compression # (No compression)

--compression 'jpegxl' --clevel 95 --lossy # (lossy jpegxl, 95 quality, zarr v2 output only)
# lossy compression MUST specify --lossy otherwise clevel is ignored and it defaults to lossless jpegxl)
```





SLURM:

stack_to_multiscale_ngff attempts to determine the number of CPU cores available and the amount of RAM that can be used for conversion.  The application attempts to use every CPU and maximize the amount of RAM to accelerate the conversion process.  However, this fails to work properly when running the application on a SLURM allocation. *The user must manually specify the number of cores and the amount of RAM using the switches -cpu, -mem*

For an allocation with 32 cores and 512GB of RAM

```bash
--cpu 32 --mem 512
```



