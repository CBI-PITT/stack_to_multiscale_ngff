#/bil/data/df/75/df75626840c76c15/mouseID_210254-15257/Green/Origin /bil/data/df/75/df75626840c76c15/mouseID_210254-15257/Red/Origin /bil/users/awatson/conv/mouseID_210254-15257 -mem 2900 -cpu 80 -tmp /local --clevel 8
#-s 1 1 50 1 1 -oc 1 1 1 1024 1024 -fc 1 1 64 64 64


import os

''' Output path will be output_base + UUID + next_path'''

output_base = '/bil/users/awatson/fmost_conv'

output_zarr_ext = '.omehans'

mem = 2900
cpu = 80
tmp = '/scratch/fmost_conv'
compression = 'zstd'
clevel = 9
compression_multiscales = 'jpegxl'
clevel_multiscales = 100

file_type = 'tif'
downSampleType = 'mean'

start_chunks = '1 1 1 1024 1024'
stop_chunks =  '1 1 64 64 64'


# http = 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_362188-191815/CH2'
#
# key ='mouseID_362188-191815'
# value =datasets.get('mouseID_362188-191815')


def http_to_path(http):
    return http.replace('https://download.brainimagelibrary.org','/bil/data')

def get_uuid_and_next_path(http):
    out = http_to_path(http)
    out = out.split('/')
    idx = 0
    uuid = ''
    datasetID = ''
    for slot in out:

        if uuid != '':
            datasetID = slot

            return uuid,datasetID

        # Determine the uuid
        if idx == 2:
            if len(slot) == 16:
                uuid = slot

        # Find the first 2 directories
        if len(slot) == 2:
            idx += 1
        else:
            idx = 0


def get_output_path(http, output_base):
    uuid, datasetID = get_uuid_and_next_path(http)
    path = f'{output_base}/{uuid[:2]}/{uuid[2:4]}/{uuid}/{datasetID}'
    return path

lines = []
for key,value in datasets.items():
    
    line = ''

    # Inputs
    idx = 1
    while True:
        l = value.get('channel').get(idx)
        if l is not None:
                line = f'{line}{http_to_path(l)} '
                idx += 1
        else:
            break

    # Output path
    ch_path =value.get('channel').get(1)
    output = get_output_path(ch_path, output_base)
    line = f'{line}{output}{output_zarr_ext} '


    # Scale
    if value.get('scale') is not None:
        scale = value.get('scale')
        s = ' '.join([str(x) for x in (1, 1, *scale)])
        line = f'{line} -s {s} '


    # Colors
    colors = ['green','red','purple','blue']
    line = f'{line} --colors '
    for idx,_ in enumerate(value.get('channel')):
        line = f'{line} {colors[idx]} '

    # Channel Labels
    line = f'{line} --channelLabels '
    for idx,_ in enumerate(value.get('channel')):
        label = value.get('label').get(idx+1)
        if label is not None:
            line = f'{line} {label} '
        else:
            line = f'{line} Channel{idx+1} '

    # Name of dataset
    line = f'{line} --name {key} '

    # Write options
    line = f'{line} -oc {start_chunks} '
    line = f'{line} -fc {stop_chunks} '
    line = f'{line} -ft {file_type} '
    line = f'{line} --compression {compression} '
    line = f'{line} --clevel {clevel} '
    line = f'{line} --downSampleType {downSampleType} '
    # line = f'{line} --verify_zarr_write '

    # helper options
    line = f'{line} -mem {mem} '
    line = f'{line} -cpu {cpu} '
    line = f'{line} -tmp {tmp}/{key} '

    line = f'{line} --buildTmpCopyDestination '

    # Setup alternative compression for multiscales, if selected
    if compression_multiscales is not None:
        line = f'{line} --compressionms {compression_multiscales} '
        line = f'{line} --clevelms {clevel_multiscales} '
        if compression_multiscales == 'jepgxl' and clevel_multiscales <= 100:
            line = f'{line} --lossyms '


    
    lines.append(line)


outFileName = os.path.join(outPath,'lines_to_process.txt')

with open(outFileName,'w') as f:
    f.writelines(lines)


#test
/bil/users/awatson/miniconda3/envs/stack_to_multiscale_ngff/bin/python /bil/users/awatson/stack_to_multiscale_ngff/stack_to_multiscale_ngff/builder.py /bil/data/2b/da/2bdaf9e66a246844/mouseID_404421-182720/CH1 /bil/data/2b/da/2bdaf9e66a246844/mouseID_404421-182720/CH2 /bil/users/awatson/fmost_conv/2b/da/2bdaf9e66a246844/mouseID_404421-182720.omehans  -s 1 1 1 0.23 0.23  --colors  green  red  --channelLabels  GFP  PI  --name mouseID_404421-182720  -oc 1 1 1 1024 1024  -fc 1 1 64 64 64  -ft tif  --compression zstd  --clevel 9  --downSampleType mean  --verify_zarr_write  -mem 2900  -cpu 80  -tmp /local/mouseID_404421-182720


/bil/users/awatson/miniconda3/envs/stack_to_multiscale_ngff/bin/python /bil/users/awatson/stack_to_multiscale_ngff/stack_to_multiscale_ngff/builder.py /bil/data/2b/da/2bdaf9e66a246844/mouseID_404421-182720/CH1 /bil/data/2b/da/2bdaf9e66a246844/mouseID_404421-182720/CH2 /local/fmost_conv/2b/da/2bdaf9e66a246844/mouseID_404421-182720.omehans  -s 1 1 1 0.23 0.23  --colors  green  red  --channelLabels  GFP  PI  --name mouseID_404421-182720  -oc 1 1 1 1024 1024  -fc 1 1 64 64 64  -ft tif  --compression zstd  --clevel 9  --downSampleType mean  --verify_zarr_write  -mem 2900  -cpu 80  -tmp /local/mouseID_404421-182720 --buildTmpCopyDestination


/bil/users/awatson/miniconda3/envs/stack_to_multiscale_ngff/bin/python /bil/users/awatson/stack_to_multiscale_ngff/stack_to_multiscale_ngff/builder.py /bil/data/2b/da/2bdaf9e66a246844/mouseID_404421-182720/CH1 /bil/data/2b/da/2bdaf9e66a246844/mouseID_404421-182720/CH2 /bil/users/awatson/TEST_CONV_TEMP/build_tmp_c5/mouseID_404421-182720.omehans  -s 1 1 1 0.23 0.23  --colors  green  red  --channelLabels  GFP  PI  --name mouseID_404421-182720  -oc 1 1 1 1024 1024  -fc 1 1 64 64 64  -ft tif  --compression zstd  --clevel 5  --downSampleType mean  --verify_zarr_write  -mem 2900  -cpu 80  -tmp /local/mouseID_404421-182720 --buildTmpCopyDestination

##
/bil/users/awatson/miniconda3/envs/stack_to_multiscale_ngff/bin/python -i /bil/users/awatson/stack_to_multiscale_ngff/stack_to_multiscale_ngff/builder.py

## CBI_Test
~/anaconda3/envs/multiscale_develop/bin/python -i /CBI_FastStore/cbiPythonTools/stack_to_multiscale_ngff/stack_to_multiscale_ngff/builder.py /CBI_Hive/globus/pitt/bil/game_science/BILSample/0 /CBI_Hive/globus/pitt/bil/game_science/TEST_OUT.omehans  -s 1 1 0.28 0.114 0.114  --colors  green  --channelLabels  c1  --name test_alt_ms_compressor -oc 1 1 1 1024 1024  -fc 1 1 64 64 64  -ft tif  --compression zstd  --clevel 5  --downSampleType mean  -tmp /CBI_FastStore/TEST_OME_ZARR_CONVERT/TEST_TEST --buildTmpCopyDestination --compressionms jpegxl  --clevelms 100 --lossyms
