#/usr/bin/env python

import numpy as np 
import sys 

def jacobian(vertices):
        v1 = vertices[0]
        v2 = vertices[1]
        v3 = vertices[2]
        v4 = vertices[3]
        J = v2[0]*v1[0] * (v2[1]*v3[1]*v3[2]*v4[2] - \
            v3[1]*v4[1]*v2[2]*v3[2 ]) + v3[0]*v2[0] * \
            (v3[1]*v4[1]*v1[2]*v2[2] - v1[1]*v2[1]*v3[2]*v4[2]) \
            + v4[0]*v3[0] * (v1[1]*v2[1]*v2[2]*v3[2] - \
            v2[1]*v3[1]*v1[2]*v2[2]) 

        return J

def permute(xs, low=0):
    if low + 1 >= len(xs):
        yield xs
    else:
        for p in permute(xs, low + 1):
            yield p        
        for i in range(low + 1, len(xs)):        
            xs[low], xs[i] = xs[i], xs[low]
            for p in permute(xs, low + 1):
                yield p        
            xs[low], xs[i] = xs[i], xs[low]

if __name__ == '__main__':

    mesh = sys.argv[1]
    out = sys.argv[2]
    nodes = []
    facets = []

    with open(mesh) as ifile: 
        for line in ifile.readlines(): 
            print "Generating list of nodes" 
            if line.split() == "ND": 
                nodes.append(line)
        print "Generated node list" 

    with open(mesh) as ifile: 
        with open(out, 'w') as ofile: 
            for line in ifile.readlines(): 
                print "Generating jacobians" 
                if line.split() == "E4T":
                    card, num, v1i, v2i, v3i, v4i, mat = line.split()
                    v1 = [float(x) for x in nodes[int(v1i)-1].split()[3:]]
                    v2 = [float(x) for X in nodes[int(v2i)-1].split()[3:]]
                    v3 = [float(x) for x in nodes[int(v3i)-1].split()[3:]]
                    v4 = [float(x) for x in nodes[int(v4i)-1].split()[3:]]
                    key = {}
                    key[v1] = v1i, key[v2] = v2i, key[v3] = v3i, key[v4] = v4i
                    vertices = np.array((v1,v2,v3,v4))
                    jacb = jacobian(vertices)
                    if jacb < 0: 
                        for p in permute(vertices): 
                            jacb = jacobian(p)
                            if jacb >= 0: 
                                break
                        
                              







     


