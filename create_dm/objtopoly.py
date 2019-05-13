#!/usr/bin/env python

import argparse
import numpy as np
import sys

def main():

    #filename = sys.argv[1]
    #outfile = sys.argv[2]

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mesh', action='store', required=True, 
            dest='filename', help='The obj mesh you want to turn into a poly')
    parser.add_argument('-x', action='store', required=False, default=0, 
            dest='x_off', help='The x offset')
    parser.add_argument('-y', action='store', required=False, default=0, 
            dest='y_off', help='The y offset')
    parser.add_argument('-z', action='store', required=False, default=0, 
            dest='z_off', help='The z offset')
    parser.add_argument('-o', '--outfile', action='store', required=True, 
            dest='outfile', help='The outfile name')

    results = parser.parse_args()
    filename = results.filename
    x_off = float(results.x_off)
    y_off = float(results.y_off)
    z_off = float(results.z_off)
    outfile = results.outfile

    nodes = []
    facets = []

    with open(filename) as infile:
        for line in infile.readlines():
            split = line.split()
            try:
                header = split[0]
            except:
                continue
            if header == "v":
                nodes.append((float(split[1]), float(split[2]),
                    float(split[3])))
            elif header == "f":
                if '/' not in line:
                    f = split[1:]
                    facet = [int(x) for x in f]
                    facets.append(facet)
                elif '/' in line:  
                    f = split[1:]
                    facet = [int(x.split('/')[0]) for x in f]
                    facets.append(facet)
                else:
                    print "Unknown format" 


    with open(outfile, 'w') as ofile:
        line = '%d 3 0 0\n' % len(nodes)
        ofile.write(line)
        print "Writing nodes"
        count = 1 
        for n in nodes:
            line = '%d %f %f %f\n' % (count, n[0]+x_off, n[1]+y_off, n[2]+z_off)
            ofile.write(line)
            count += 1 
        line = '%d 0\n' % len(facets)
        ofile.write(line)
        print "Writing facets"
        for f in facets:
            ofile.write('1\n')
            num_f = len(f)
            string = "%i " % num_f 
            for i in range(num_f):
                string += '%i ' % f[i]
            string += '\n'
            #line = '3 %d %d %d\n' % (f[1], f[2], f[3])
            ofile.write(string)
        ofile.write('0\n') # holes
        ofile.write('0') # Attributes



if __name__ == '__main__':
    sys.exit(main())
