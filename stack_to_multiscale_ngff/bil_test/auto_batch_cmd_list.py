#/bil/data/df/75/df75626840c76c15/mouseID_210254-15257/Green/Origin /bil/data/df/75/df75626840c76c15/mouseID_210254-15257/Red/Origin /bil/users/awatson/conv/mouseID_210254-15257 -mem 2900 -cpu 80 -tmp /local --clevel 8
#-s 1 1 50 1 1 -oc 1 1 1 1024 1024 -fc 1 1 64 64 64


import os, glob

# outFileName = 

bilPath = '/bil/data'
basePath = '56/fb/56fb1b25ca6b5fae'
scale = '1 1 50 1 1' #tczyx

outPath = '/bil/users/awatson/conv'

mem = 2900
cpu = 80
tmp = '/local'
clevel = 8
file_type = 'tif'

start_chunks = '1 1 1 1024 1024'
stop_chunks =  '1 1 64 64 64'



levels = 3

search = '/*' * (levels-1)

groups = glob.glob(os.path.join(bilPath,basePath) + search)


toProcess = {}
for group in groups:
    
    toProcess[group] = sorted(glob.glob(group + '/*'))
    

len(toProcess)
lines = []
for idx,group in enumerate(toProcess):
    
    line = ''
    
    #Inputs
    for inDir in toProcess[group]:
        line = line + inDir + ' '
    
    outDir = group.replace(bilPath,outPath)
    line = line + inDir + ' '
    line = line + outDir + '/' + os.path.split(outDir)[-1] + '.omezarr '
    line = line + '-mem ' + str(mem) + ' '
    line = line + '-cpu ' + str(cpu) + ' '
    line = line + '-tmp ' + tmp + ' '
    line = line + '-s ' + scale + ' '
    line = line + '-oc ' + start_chunks + ' '
    line = line + '-fc ' + stop_chunks + ' '
    line = line + '--clevel ' + str(clevel) + ' '
    line = line + '-ft ' + file_type
    
    if idx < len(toProcess)-1:
        line = line + '\n'
    
    lines.append(line)


outFileName = os.path.join(outPath,'lines_to_process.txt')

with open(outFileName,'w') as f:
    f.writelines(lines)