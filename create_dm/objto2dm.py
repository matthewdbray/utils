#!/usr/bin/env python

import sys

objfile = sys.argv[1]
mat_num = sys.argv[2]

name = objfile.split('.')[0]
newfile = name + '.2dm'
usemtl = False
mats = {}

with open(newfile, 'w') as ofile: 
    with open(objfile) as ifile:
        vn = 1
        en = 1
        ofile.write('MESH2D\n')
        for line in ifile.readlines(): 
            try:
                head = line.split()[0]
            except:
                continue
            if head == "usemtl": 
                usemtl = True
                # Find material
                new_mat = line.split()[-1]
                # Add material to dictionary
                if new_mat not in mats: 
                    mat_num = int(mat_num) + 10 
                    mats[new_mat] = mat_num
                
            if head == "v": 
                v, x, y, z = line.split()
                nline = ' '.join(['ND', str(vn), x, y, z])+'\n'
                ofile.write(nline)
                vn += 1 
            if head == "f": 
                f, v1, v2, v3 = line.split()
                if not usemtl:
                    nline = ' '.join(['E3T', str(en), v1, v2, v3, mat_num])+'\n'
                if usemtl: 
                    mat_num = str(max(mats.values())) 
                    nline = ' '.join(['E3T', str(en), v1, v2, v3, mat_num])+'\n'
                
                ofile.write(nline)
                en += 1 
            
