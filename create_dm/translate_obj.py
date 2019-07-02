#!/usr/bin/env python

import sys

def translate_obj(obj, nobj, xoff, yoff, zoff):
    with open(nobj, 'w') as ofile: 
        with open(obj) as ifile: 
            for line in ifile.readlines(): 
                if line.split()[0] == "v": 
                    v,x,y,z = line.split()
                    nx = float(x) + float(xoff)
                    ny = float(y) + float(yoff) 
                    nz = float(z) + float(zoff)
                    nline = 'v %f %f %f\n' % (nx, ny, nz)
                    ofile.write(nline)
                else: 
                    ofile.write(line)

if __name__ == '__main__': 
    obj = sys.argv[1]
    nobj = sys.argv[2]
    x = sys.argv[3]
    y = sys.argv[4]
    z = sys.argv[5]
    translate_obj(obj, nobj, x, y, z)
