#!/usr/bin/env python

import argparse

if __name__ == '__main__': 

    parser = argparse.ArgumentParser()

    parser.add_argument('--2dm', '-m', action='store', required=True, 
            dest='two_dm', help='This is the 2dm file you want converted.')

    parser.add_argument('--obj', '-o', action='store', required=True, 
            dest='obj', help='This is the name of the obj file.')

    results = parser.parse_args()
    two_dm = results.two_dm
    obj = results.obj

    facets = []
    nodes = []

    print("Reading in 2dm file")
    with open(two_dm) as ifile:
        for line in ifile.readlines(): 
            header = line.split()[0]
            if header == 'E3T': 
                facets.append(line.split()[2:5])
            elif header == 'ND': 
                nodes.append(line.split()[2:5])
            else: 
                continue
    
    print ("Writing to obj file")
    with open(obj, 'w') as ofile: 
        for node in nodes: 
            nline = 'v ' + ' '.join(node) + '\n'
            ofile.write(nline)
        for face in facets: 
            nline = 'f ' + ' '.join(face) + '\n'
            ofile.write(nline)


