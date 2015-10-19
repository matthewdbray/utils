#!/usr/bin/env python

from collections import OrderedDict
import h5py 
import glob
import numpy as np 
import sys

if len(sys.argv) != 3: 
    print "Usage: extract_node_temporal.py <sim_name> <node_to_extract>" 

sim_name = sys.argv[1]
node = int(sys.argv[2])

# Grab all the h5 files except surface
files = glob.glob(sim_name+"_p[0-9]*.h5")

# Set boolean for when you find the original node number in a chunk 
found_orig_node = False

# Finding the h5 chunk that has the node number we're looking for
while not found_orig_node: 
    for fname in files: 
        print "Reading %s ... " % fname
        f1 = h5py.File(fname, 'r')
        geo = f1['Geometry']
        n_ = geo['orig_node_number']
        nodes = n_['0']
        nds = np.array(nodes)
        # Find index of node if it exists
        idx = np.where(nds == node)
        # See if idx actually contains an index.  It the previous np.where
        # fails you are left with an empty tuple
        if len(idx[0]) != 0:
            found_orig_node = True
            idx = idx[0][0]
            file_to_loop = fname
            print "Found %d in file %s" % (node, fname)
            break

f1 = h5py.File(file_to_loop, 'r')
data = f1['Data']
temp = data['Temperature']
times = temp['Times']

# Temperature is a dictionary which is unsorted.  You can't use just a regular
# sort on it because temp['Times'] is an array of floats, but with even numbers
# the key in temp is an int - so this is just an annoying thing you have to do
temp_ord = OrderedDict()

for time in times: 
    if time.is_integer(): 
        temp_ord[str(time)] = temp[str(int(time))]
    elif time == 'Times': 
        continue
    else: 
        temp_ord[str(time)] = temp[str(time)]

# New file for the temperatures and then printing out to the file
f2 = open('%s_%d.txt' % (sim_name, node), 'w')

for tmp in temp_ord.iterkeys():
    f2.write('%s\n' % temp_ord[tmp][idx])

f1.close()
f2.close()
    


