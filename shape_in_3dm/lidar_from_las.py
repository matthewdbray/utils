#!/usr/bin/env python

import liblas
import glob
import sys

#File Name
fname = sys.argv[1]

#Offsets
x_off = 25 # -25 to 25 
y_off = 25 # -25 to 25 

#Center Data
x_cent = float(sys.argv[2])
y_cent = float(sys.argv[3])

#Min and Max 
x_min = x_cent - x_off
x_max = x_cent + x_off
y_min = y_cent - y_off
y_max = y_cent + y_off

#Find las files 
files = glob.glob('*.las')

pts = []
for f in files: 
    print "Reading %s\n" % f
    las = liblas.file.File(f, mode='r')
    h = las.header
    #print "x_min >= h.min[0]", x_min, h.min[0], x_min >= h.min[0]
    #print "x_max <= h.max[0]", x_max, h.max[0], x_max <= h.max[0]
    #print "y_min >= h.min[1]", y_min, h.min[1], y_min >= h.min[1]
    #print "y_max <= h.max[1]", y_max, h.max[1], y_max <= h.max[1]
    if x_min >= h.min[0] or x_max <= h.max[0] or y_min >= h.min[1] or y_max <= h.max[1]:
            for p in las: 
            #    if x_min <= p.x <= x_max: 
            #        if y_min <= p.y <= y_max: 

            #    print x_min, h.min[0]
            #    print x_max, h.max[0]
            #    print y_min, h.min[1]
            #    print y_max, h.max[1]
            #    print "" 
                if p.x >= x_min and p.x <= x_max: 
                    if p.y >= y_min and p.y <= y_max: 
                        pts.append((p.x,p.y,p.z))

                    #print "X,Y,Z: ", p.x, p.y, p.z
    las.close()

with open(fname, 'w') as ofile: 
    ofile.write(str(len(pts)) + '\n')
    for p in pts: 
        p = [str(x) for x in p]
        line = ' '.join(p) + '\n'
        ofile.write(line)





    
