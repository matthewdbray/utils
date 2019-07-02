#!/usr/bin/env python

import argparse
import numpy as np
import sys

def main():

    #filename = sys.argv[1]
    #outfile = sys.argv[2]

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mesh', action='store', required=True, 
            dest='filename', help='The 2dm mesh you want to turn into a poly')
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
            header = split[0]
            if header == "ND":
                nodes.append((float(split[1]), float(split[2]),
                    float(split[3]), float(split[4])))
            elif header == "E3T":
                facets.append((int(split[1]), int(split[2]), int(split[3]),
                    int(split[4])))

    with open(outfile, 'w') as ofile:
        line = '%d 3 0 0\n' % len(nodes)
        ofile.write(line)
        print "Writing nodes"
        for n in nodes:
            line = '%d %f %f %f\n' % (n[0], n[1]+x_off, n[2]+y_off, n[3]+z_off)
            ofile.write(line)
        line = '%d 0\n' % len(facets)
        ofile.write(line)
        print "Writing facets"
        for f in facets:
            ofile.write('1\n')
            line = '3 %d %d %d\n' % (f[1], f[2], f[3])
            ofile.write(line)
        ofile.write('0\n') # holes
        ofile.write('0') # Attributes



if __name__ == '__main__':
    sys.exit(main())
