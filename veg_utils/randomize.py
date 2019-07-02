#!/usr/bin/env python
from random import uniform 
import sys

infile = sys.argv[1]
mod_num = sys.argv[2]
small = float(sys.argv[3])
large = float(sys.argv[4])

with open(infile) as ifile: 
    new_lines = []
    for line in ifile.readlines():
        inst = line.split()[0]
        if inst == mod_num:  
            line = line.split()
            line[1] = round(uniform(small, large), 3) 
            line[2] = round(uniform(0, 360), 3)
            line = [str(i) for i in line] 
            new_inst = ' '.join(line) 
            new_lines.append(new_inst)

        else:
            line = line.rstrip('\n')
            new_lines.append(line)

with open('new_build_scene.dat', 'w') as ofile: 
    for line in new_lines: 
        ofile.write(line+'\n')

