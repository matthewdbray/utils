#!/usr/bin/env python

import argparse

if __name__ == '__main__': 

    parser = argparse.ArgumentParser()

    parser.add_argument('--2dm', '-m', action='store', required=True, 
            dest='two_dm', help='This is the 2dm file you want converted.')

    parser.add_argument('--obj', '-o', action='store', required=True, 
            dest='obj', help='This is the name of the obj file.')
    parser.add_argument('--mat', action='store_true', required=False,
            dest='mat', help='This is if you want material.')


    results = parser.parse_args()

    two_dm = results.two_dm
    obj = results.obj
    if results.mat:
        mat = results.mat
        mats = {}

    facets = []
    nodes = []

    print("Reading in 2dm file")
    with open(two_dm) as ifile:
        for line in ifile.readlines(): 
            header = line.split()[0]
            if header == 'E3T': 
                if mat:
                    facets.append(line.split()[2:6])
                    mats[str(line.split()[-1])] = True
                else:
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
            if mat:
#                print(mats['1'])
                if mats[str(face[-1])] != False:
                    mat_line = 'usemtl Mat_%s\n' % str(face[-1]) 
                    ofile.write(mat_line)
                    mats[str(face[-1])] = False
                    nline = 'f ' + ' '.join(face[:-1]) + '\n'
                    ofile.write(nline)
                else:
                    nline = 'f ' + ' '.join(face[:-1]) + '\n'
                    ofile.write(nline)
            else:
                nline = 'f ' + ' '.join(face) + '\n'
                ofile.write(nline)


