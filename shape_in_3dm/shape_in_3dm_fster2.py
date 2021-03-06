#!/usr/bin/env python

"""
Author: Matthew Bray
Date: Mar 27, 2015

The purpose of this program is to read in 3dm files and change the materials
in different polygons that we are feeding it.  This could be as simple as a
parallelepiped (box) or something that looks like a mortar shell.

More shapes will be added as needed.
"""

import argparse
import numpy as np
from scipy.spatial import ConvexHull
import sys

class Node(object):
    """ Defines the relevant parts of a node struct """

    def __init__(self, x, y, z, nnum):
        self.x = x
        self.y = y
        self.z = z
        self.nnum = nnum

class Tet(object):
    """ Defines the relevant parts of a tet struct """

    def __init__(self, n1, n2, n3, n4, tnum, mat):
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.n4 = n4
        self.tnum = tnum
        self.mat = mat

    def __str__(self):
        return 'Node 1: {}\nNode 2: {}\nNode 3: {}\nNode 4: {}\n'\
                'Tet number: {}\nTet material: {}\nTet Centroid: {}'\
                .format(self.n1, self.n2, self.n3, self.n4, self.tnum,
                        self.mat, self.centroid)


def points_from_mesh(shapefile):
    """ Getting points from a 2dm or 3dm mesh """

    with open(shapefile) as ofile:
        points=[]
        for line in ofile.readlines():
            if line is not None:
                split = line.split()
                if split[0] == "ND":
                    pnt=[split[2], split[3], split[4]]
                    points.append(pnt)
    points = np.array(points, dtype=float)

    return points

def bounding_box_points(shapefile, x, y, z, points=None):
    """
    Loads the shapefile into a numpy array and returns a ccw bounding box
    """

    if not points.any():  # Not read in already from a 2dm
        points = np.loadtxt(shapefile, dtype=float)

    # Translate the points to where they will be in the mesh
    to_add = np.array((x,y,z),dtype=float)
    points += to_add

    # Bounding box
    # %timeit shows that .min is a lot faster than min(points[:,0])
    min_x = points[:,0].min()
    max_x = points[:,0].max()
    min_y = points[:,1].min()
    max_y = points[:,1].max()
    min_z = points[:,2].min()
    max_z = points[:,2].max()

    # Adding the adjustment percentage that you want to increase bbox
#    min_x -= min_x * adj
#    max_x += max_x * adj
#    min_y -= min_y * adj
#    max_y += max_y * adj
#    min_z -= min_z * adj
#    max_z += max_z * adj

    ## Returning counter clockwise bottom first bounding box (cube)
    #return ((min_x, min_y, min_z), (max_x, min_y, min_z), (max_x, max_y, min_z),
    #        (min_x, max_y, min_z), (min_x, min_y, max_z), (max_x, min_y, max_z),
    #        (max_x, max_y, max_z), (min_z, max_y, max_z))

    # Returning min and max for x,y,z
    min_max_arr = np.array(((min_x, min_y, min_z), (max_x, max_y, max_z)))
    print "Bounding box:"
    print min_max_arr

    return points, min_max_arr

def point_in_3d_poly(node, poly):
    """
    Seeing if a point is inside a polygon in three dimensions.
    node is a Node class that has an x,y, and z.
    Poly is a numpy array of points that make up the poly


    This makes a 3D convex hull with the regular points, then adds the new
    point to the list and makes a new convex hull.  Assumedly if this list
    doesn't change then the centroid is inside the convex hull
    """
    hull = ConvexHull(poly)
    new_pt = np.array([[node.x, node.y, node.z]])
    new_pts = np.append(poly, new_pt, axis=0)
    new_hull = ConvexHull(new_pts)
    if list(hull.vertices) == list(new_hull.vertices):
        return True
    else:
        return False

def build_nodes(mesh, bbox):
    """
    Does a first pass through the file and reads in the nodes and the num of
    tets and highest material number in 3dm file.
    """
    nnodes = 0
    nnodes_in_bbox = 0
    ntets = 0
    highest_mat_num = 1
    nodes = []
    nodes_in_bbox = []

    # Getting bounding box
    min_x, min_y, min_z = bbox[0]
    max_x, max_y, max_z = bbox[1]

    print "Reading in nodes...."

    with open(mesh) as infile:
        for line in infile.readlines():
            if line is not None:
                split = line.split()
                marker = split[0] # Node or facet
            if marker == "ND":
                split = [float(x) for x in split if x != "ND"]
                node = (split[1], split[2], split[3], split[0])
                # Checking to see if node is in bounding box
                if min_x <= node[0] <= max_x:
                    if min_y <= node[1] <= max_y:
                        if min_z <= node[2] <= max_z:
                            nodes_in_bbox.append(split[0])
                            nnodes_in_bbox += 1
                nodes.append(node)
                nnodes += 1
            elif marker  == "E4T":
                ntets += 1
                if int(split[-1]) > highest_mat_num:
                    highest_mat_num = int(split[-1])

    print "There are\n\t{} nodes\n\t{} tets\n\thighest material number is "\
            "{}".format(nnodes, ntets, highest_mat_num)
    print "There are \n\t{} nodes in the bounding box".format(nnodes_in_bbox)
    if nnodes_in_bbox <= 0:
        print "No nodes in bounding box - something went wrong"
        sys.exit()

    return nodes, nodes_in_bbox, highest_mat_num

def compute_centroids_find_in_poly(mesh, nodes, nodes_in_bbox, highest_mat_num,
        poly, outfile):
    """
    Computes the centroid for each tet, and also figures out whether it is in
    the bounding box of the pts that you're wanting to change if a bbox is
    given as np.array(((min_x,min_y,min_z),(max_x,max_y,max_z)))
    """

    print "Computing centroids of tets ... "

    tets_bbox = []
    tets = []
    ofile = open(outfile, 'w')

    with open(mesh) as infile:
        for line in infile.readlines():
            # Set up boolean
            inPoly = False
            inBbox = False
            ntets = 0

            # Iterate through file
            if line is not None:
                split = line.split()
                marker = split[0]
            if marker == "E4T":
                # Parsing line and turning them into integers
                split = [int(x) for x in split if x != "E4T"]
                n1 = split[1]
                n2 = split[2]
                n3 = split[3]
                n4 = split[4]
                tnum = split[0]
                mat = split[5]

                if any(x in [n1,n2,n3,n4] for x in nodes_in_bbox):
                    nmat = highest_mat_num + 1
                    line = 'E4T %5d %5d %5d %5d %5d %d\n' % (tnum, n1, n2,
                            n3, n4, nmat)
                    ofile.write(line)
                else:
                    ofile.write(line)  # Nothing to change
            elif marker == "ND":
                ofile.write(line)
            else:
                ofile.write(line)






                    # Computing centroids
#                    cx = np.sum((n1.x, n2.x, n3.x, n4.x), dtype=float)/4.0
#                    cy = np.sum((n1.y, n2.y, n3.y, n4.y), dtype=float)/4.0
#                    cz = np.sum((n1.z, n2.z, n3.z, n4.z), dtype=float)/4.0

                    #if point_in_3d_poly(Node(cx,cy,cz,-1), poly):
                        #inPoly=True
                        #nmat = highest_mat_num+1
                        #tets.append(Tet(n1.nnum ,n2.nnum, n3.nnum, n4.nnum ,tnum, nmat))

        # delete nodes for RAM space
        del(nodes)
        return tets

def write_new_3dm(mesh, outfile, tets):
    """
    Writes the nodes and tets to a 3dm file - reiterates through the first
    file to save RAM space
    """

    print "Writing to new 3dm...."
    tnum = 1 # Tet numbers start at 1

    with open(mesh) as infile:
        with open(outfile,'w') as ofile:
            ofile.write('MESH3D\n')
            for line in infile.readlines():
                tetFound = False
                split = line.split()
                if split[0] == "E4T":
                    split = [int(x) for x in split if x != 'E4T']
                    for tet in tets:
                        if tet.tnum == tnum:
                            tetFound = True
                            line = 'E4T %03d %05d %05d %05d %05d %d\n' %\
                            (tet.tnum, tet.n1, tet.n2, tet.n3, tet.n4, tet.mat)
                            ofile.write(line)
                    if not tetFound:
                        ofile.write(line)
                else:
                    ofile.write(line)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '--mesh', action='store', required=True,
            dest='mesh',
            help='This is the mesh file you are wanting to change')
    parser.add_argument('-s', '--shape', action='store', required=True,
            dest='shapefile',
            help='This is the file that contains the x,y,z coordinates of '\
                    'the shape that you are wanting to enter into the mesh')
    parser.add_argument('-x', action='store', required=True, dest='x',
            help='This is the x location of the object being placed.')
    parser.add_argument('-y', action='store', required=True, dest='y',
            help='This is the y location of the object being placed.')
    parser.add_argument('-z', action='store', required=True, dest='z',
            help='This is the z location of the object being placed.')
    parser.add_argument('-o', '--out', action='store', required=False,
            dest='outfile', default='outfile.3dm',
            help='This is the new 3dm file with planted object')

    results = parser.parse_args()

    mesh = results.mesh
    shapefile = results.shapefile
    x = results.x
    y = results.y
    z = results.z
    outfile = results.outfile

    ext = shapefile.split('.')[-1]
    from pycallgraph import PyCallGraph, Config
    from pycallgraph.output import GraphvizOutput

    config = Config(max_depth=4)
    with PyCallGraph(output=GraphvizOutput(), config=config):
        if ext == "2dm" or ext == "3dm":
            points = points_from_mesh(shapefile)
            points, bbox = bounding_box_points(shapefile, x, y, z, points=points)
        else:
            points, bbox = bounding_box_points(shapefile, x,y,z)

        nodes, nodes_in_bbox, highest_mat_num = build_nodes(mesh, bbox)
        tets = compute_centroids_find_in_poly(
                mesh,
                nodes,
                nodes_in_bbox,
                highest_mat_num,
                points,
                outfile)

#     write_new_3dm(mesh, outfile, tets)











