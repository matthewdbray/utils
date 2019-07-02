#!/usr/bin/env python

import sys

filename = sys.argv[1]
nfile = filename.split('.')[0] + '_swapped.2dm'

with open(nfile, 'w') as ofile: 
    with open(filename) as ifile: 
        for line in ifile.readlines(): 
            if line.split()[0] == "ND": 
                h, n, x, y, z = line.split()
                nline = ' '.join([h,n,x,z,y])+'\n'
                ofile.write(nline)
            else: 
                ofile.write(line)

