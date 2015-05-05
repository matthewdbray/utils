#!/usr/bin/env python

import sys

def main():

    filename = sys.argv[1]
    outfile = sys.argv[2]
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
            line = '%d %f %f %f\n' % (n[0], n[1], n[2], n[3])
            ofile.write(line)
        line = '%d 0' % len(facets)
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
