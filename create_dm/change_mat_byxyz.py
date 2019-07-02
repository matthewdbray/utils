#!/usr/bin/env python
import sys

## Look at function main() for things to change

def compute_centroid(facet, nodes):
    """ You only need the y centroid """
    tot_z = 0
    for f in facet[:-1]:
        try:
           node = nodes[f-1]
        except: 
            print f
            sys.exit()
        tot_z += node[2]

    return tot_z/4.0



def change_materials(mat_num, new_mat, min_z, max_z, facets, nodes):
    
    new_facets = []
    for f in facets:
        if f[-1] == mat_num:
            centroid = compute_centroid(f, nodes)
            if min_z <= centroid <= max_z:
                f[-1] = new_mat
                new_facets.append(f)
            else:
                new_facets.append(f)
        else:
            new_facets.append(f)
    return new_facets


            


def main():
    #####
    # Stuff you might want to change
    #####
    
    mat_num = 20 # Mat number to change
    new_mat = 30 # What to change it to
    
    min_z = -10
    max_z = 0

    mesh = '/Users/matthewbray/git/utils/create_dm/conexBox_1layer.3dm'
    out = '/Users/matthewbray/git/utils/create_dm/conexBox_3mats.3dm'

    facets = []
    nodes = []

    with open(mesh) as f: 
        for line in f.readlines():
            tag = line.split()[0]  # Check if node or facet
            if tag == "E4T": 
                ele = line.split()[2:]
                ele = [int(e) for e in ele]
                facets.append(ele)
            elif tag == "ND": 
                node = line.split()[2:]
                node = [float(n) for n in node]
                nodes.append(node)
            else:
                continue

    print "Changing materials"
    new_facets = change_materials(mat_num, new_mat, min_z, max_z, facets, nodes)

    with open(out, 'w') as of:
        of.write('MESH3D\n')
        for i, f in enumerate(new_facets):
            line = 'E4T %i %i %i %i %i %i\n' % (i+1,f[0],f[1],f[2],f[3],f[4])
            of.write(line)
        for i, n in enumerate(nodes):
            line = 'ND %i %f %f %f\n' % (i+1,n[0],n[1],n[2])
            of.write(line)
        of.write('END')

            




if __name__ == '__main__': 
    main()
