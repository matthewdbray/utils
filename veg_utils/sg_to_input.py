#!/usr/bin/env python 

import sys

#from veg_tools import file_naming
#filename = '/Users/matthewbray/PyCharmProjects/veg_input/4-30-12.sg'
def file_naming(fname):
    f = fname.split('/')[-1]
    f2 = f.split('.')[0]
    return f2+'.dat'

#filename = '/Users/rdgslmdb/Dropbox/xfrog/1_Meter/building_scene.sg'
filename = sys.argv[1]
f1 = open(filename, 'r')
new_filename = file_naming(filename)
print new_filename
f2 = open(new_filename, 'w')

raw_data = []
tmp_list = []
split_data = []

for line in f1.readlines():
    tmp_list = line.split()
    split_data.append(tmp_list)
    raw_data.append(line)

#Get list of models
models = []
isDirectory = False
for line in split_data:
    if line[0] == '</ObjectFileDirectory>':
        isDirectory = False
    if isDirectory is True:
        line = line[1].split('"')
        line = line[1].split('/')
        line = line[-1]
        checkext = line.split('.')
        if checkext[-1] == 'obj':
            models.append(line)
        elif checkext[-1] == '2dm': 
            models.append(line)
    if line[0] == '<ObjectFileDirectory>':
        isDirectory = True

#Create mod_num dict
mod_num = {}
cnt = 0
for model in models:
    key = 'mod' + str(cnt)
    mod_num[key] = model
    cnt += 1

#Create file_entry dict
file_entry = {}
for i in range(0, len(models)):
    key = str(i)
    value = 'mod' + str(i)
    file_entry[key] = value
print file_entry
#Get instances and create instance line list
inst_line = []
isObj = False
tmp_inst_line = []
for line in raw_data:
    line = line.lstrip()
    if line == '</Object>\n':
        isObj = False
        tmp_inst_line.append(scale)
        tmp_inst_line.append(ori)
        tmp_inst_line.append(x)
        tmp_inst_line.append(y)
        tmp_inst_line.append(z)
        inst_line.append(tmp_inst_line)
        tmp_inst_line = []
    if isObj is True:
        line_split = line.split('"')
        if line_split[0] == 'FileEntry=':
            file_ent = line_split[1]
            for key in file_entry:
                if key == file_ent:
                    value = file_entry[key]
                    tmp_inst_line.append(value)
        if line_split[0] == '<Position Value=':
            coords = line_split[1].split()
            x,y,z = coords[:]
        if line_split[0] == '<Orientation Value=':
            ori = line_split[1].split()
            ori = ori[2]
        if line_split[0] == '<Scale Value=':
            scale = line_split[1].split()
            scale = scale[2]
    checkobj = line.split()
    if checkobj[0] == '<Object':
        isObj = True


#Start Creating the .dat file
f2.write('MODELS ')
len_mod = str(len(models))
f2.write(len_mod)
f2.write('\n')
for key in mod_num:
    line = key + ' veg/' + mod_num[key]
    f2.write(line)
    f2.write('\n')
f2.write('\n')

line = 'LEAFSIZE ' + str(len(models)) + '\n'
f2.write(line)

for key in mod_num:
    line = key + ' 0.01\n'
    f2.write(line)
f2.write('\n')

line = 'MATERIALCODE ' + str(len(models)) + '\n'
f2.write(line)

for key in mod_num:
    line = key + ' 100\n'
    f2.write(line)

f2.write('NODEFILE veg/veg_Temp\n')
f2.write('START_SIM_TIME ###&&&&\n')
f2.write('END_SIM_TIME ###&&&&\n')
f2.write('MET_WIND_HEIGHT 2.5\n')
f2.write('OUTPUT_MESH PreQC/veg.2dm\n')
f2.write('INPUT_FLUX_FILE 500\n')
f2.write('MET_FILE soil/EJ30.met\n')
f2.write('\n')

line = 'INSTANCE ' + str(len(inst_line)) + '\n'
f2.write(line)

for line in inst_line:
    line = ' '.join(line) + '\n'
    f2.write(line)







