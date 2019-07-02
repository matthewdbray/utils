#!/usr/bin/env python

__author__ = 'matthewbray'

from veg_tools import *

#Veg_input.dat file to convert
veg_input = 'flash.dat'
#f1 = open('/Users/matthewbray/PycharmProjects/veg_input/%s' % veg_input, 'r')
f2 = open('/Users/matthewbray/Desktop/sg_from_input.sg', 'w')
f1 = open('/Users/matthewbray/PycharmProjects/veg_input/%s' % veg_input, 'r')
full_dat = []

# Read in entire .dat file
for line in f1.readlines():
    full_dat.append(line)
tmpmodels=[]
models = []
mod_dict = {}
ismodel = False
for line in full_dat:
    if line[0:6] == 'MODELS':
        ismodel = True
    if line == '\n':
        ismodel = False
    if ismodel is True and line[0:6] != 'MODELS':
        tmpmodels.append(line)

for line in tmpmodels:
    line = line.split(' veg/')
    mod = line[1]
    mod = mod.rstrip('\n')
    models.append(mod)
    mod_dict[line[0]] = mod

# Get instances
instances = []
isInstance = False

for line in full_dat:
    if line[0:8] == 'INSTANCE':
        isInstance = True
    if isInstance is True and line[0:8] != 'INSTANCE':
        line = line.split()
        instances.append(line)

createHeader(f2)
typeDefinitions(f2, models)
fileEntry = objectFileDirectory(f2, models)
objectDefinitions(f2, mod_dict, instances, fileEntry)
addFooter(f2)

print "--DONE--"
