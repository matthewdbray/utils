#!/usr/bin/env python

#==============================================================================
# This was just a code creating out of being sick of turning triangle and
# tetgen codes into 2dm and 3dm's.  This is just a quick and dirty way of doing
# that
#==============================================================================

import argparse
import numpy as np
import sys

def create_2dm(nfile, ffile, outfile):
    nodes = np.loadtxt(nfile, skiprows=1, dtype=float)
    facets = np.loadtxt(ffile, skiprows=1, dtype=int)
    with open(outfile, 'w') as ofile:
        ofile.write('MESH2D\n')
        print "Writing nodes"
        for n in nodes:
            line = 'ND %d %f %f %f\n' % (n[0], n[1], n[2], n[3])
            ofile.write(line)
        print "Writing facets"
        for f in facets:
            line = 'E3T %d %d %d %d\n' % (f[0], f[1], f[2], f[3])
            ofile.write(line)
        ofile.write('END')
        print "--DONE--"

def create_3dm(nfile, efile, outfile):
    print "Reading nodes..."
    nodes = []
    with open(nfile) as nf:
        nf.readline()
        for line in nf.readlines(): 
            node = line.split()
            nodes.append(node)
        nodes = nodes[:-1]
    print "Reading elements..."
    elements = []
    with open(efile) as ef:
        ef.readline()
        for line in ef.readlines():
            element = line.split()
            elements.append(element)
        elements = elements[:-1]

    with open(outfile, 'w') as ofile:
        ofile.write('MESH3D\n')
        print "Writing nodes"
        for n in nodes:
            line = 'ND %s %s %s %s\n' % (n[0], n[1], n[2], n[3])
            ofile.write(line)
        print "Writing elements"
        for e in elements:
            try:
                line = 'E4T %s %s %s %s %s %s\n' % (e[0], e[1], e[2], e[3], e[4], e[5])
            except:
                line = 'E4T %s %s %s %s %s 1\n' % (e[0], e[1], e[2], e[3],
                        e[4])
            ofile.write(line)
        ofile.write('END')
        print "--DONE--"

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('--node', '-n', action='store', required=True,
            dest='node_file',
            help='The node file produced by tetgen or triangle')
    parser.add_argument('--ele', '-e', action='store', dest='ele_file',
            required=True, help='The elements produced by tetgen')
    parser.add_argument('--2dm', '-2', action='store_true', dest='two_dim',
            required=False, default=False,
            help='Use if you are creating a 2dm')
    parser.add_argument('--3dm', '-3', action='store_true', dest='three_dim',
            required=False, default=False,  help='Use if you creating a 3dm')
    parser.add_argument('--out', '-o', action='store', dest='outfile',
            required=True, help='Name of the out file')

    results = parser.parse_args()
    node_file = results.node_file
    ele_file = results.ele_file
    two_dim = results.two_dim
    three_dim = results.three_dim
    outfile = results.outfile

    if two_dim and three_dim:
        print "You must select either two or three dimensions"
        sys.exit()
    elif two_dim:
        create_2dm(node_file, ele_file, outfile)
    elif three_dim:
        create_3dm(node_file, ele_file, outfile)
    else:
        print "You must select either two or three dimensions"
        sys.exit()

if __name__ == "__main__":
    main()
