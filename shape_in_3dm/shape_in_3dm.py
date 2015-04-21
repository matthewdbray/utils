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

    def __init__(self, n1, n2, n3, n4, tnum, mat, centroid=-1):
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.n4 = n4
        self.tnum = tnum
        self.mat = mat
        self.centroid = centroid

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

def bounding_box_points(shapefile, x, y, z, points=None, adj=None):
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
    min_x -= min_x * adj
    max_x += max_x * adj
    min_y -= min_y * adj
    max_y += max_y * adj
    min_z -= min_z * adj
    max_z += max_z * adj


    # Returning min and max for x,y,z
    return points, np.array(((min_x, min_y, min_z), (max_x, max_y, max_z)))

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

def build_geometry(mesh):
    """
    Reads the geometry of the mesh and returns the number of nodes, the number
    of facets, and the highest material number currently in the mesh.

    If there is a bounding box included it also pulls those nodes
    """
    nnodes = 0
    ntets = 0
    highest_mat_num = 1
    tets = []
    nodes = []

    print "Reading geometry...."

    with open(mesh) as infile:
        for line in infile.readlines():
            if line is not None:
                split = line.split()
            if split[0] == "ND":
                split = [float(x) for x in split if x != "ND"]
                node = Node(split[1], split[2], split[3], split[0])
                nodes.append(node)
                nnodes += 1
            elif split[0] == "E4T":
                ntets += 1
                split = [int(x) for x in split if x != "E4T"]
                tet = Tet(split[1], split[2], split[3], split[4], split[0],
                        split[5]) # n1, n2, n3, n4, nnum, matnum
                tets.append(tet)

                if int(split[-1]) > highest_mat_num:
                    highest_mat_num = int(split[-1])

    print "There are\n\t{} nodes\n\t{} tets\n\thighest material number is "\
            "{}".format(nnodes, ntets, highest_mat_num)

    return np.array(nodes), np.array(tets),  highest_mat_num

def compute_centroids(nodes, tets, bbox):
    """
    Computes the centroid for each tet, and also figures out whether it is in
    the bounding box of the pts that you're wanting to change if a bbox is
    given as np.array(((min_x,min_y,min_z),(max_x,max_y,max_z)))
    """
    print "Computing node values and centroids ... "

    tets_bbox = []

    min_x, min_y, min_z = bbox[0]
    max_x, max_y, max_z = bbox[1]

    for tet in tets:
        tet.n1 = nodes[tet.n1-1]
        tet.n2 = nodes[tet.n2-1]
        tet.n3 = nodes[tet.n3-1]
        tet.n4 = nodes[tet.n4-1]
        # Computing averages
        cx = np.sum((tet.n1.x, tet.n2.x, tet.n3.x, tet.n4.x), dtype=float) * 0.25
        cy = np.sum((tet.n1.y, tet.n2.y, tet.n3.y, tet.n4.y), dtype=float) * 0.25
        cz = np.sum((tet.n1.z, tet.n2.z, tet.n3.z, tet.n4.z), dtype=float) * 0.25
        cnode = Node(cx, cy, cz, -1)
        tet.centroid = cnode


        if min_x <= tet.centroid.x <= max_x:
            if min_y <= tet.centroid.y <= max_y:
                if min_z <= tet.centroid.z <= max_z:
                    tets_bbox.append(tet)

        if len(tets_bbox) == 0:
            print "There are no tets in the bounding box - error"
            sys.exit()

    return nodes, tets, np.array(tets_bbox)

def change_materials(tets, tets_bbox, points, highest_mat_num):
    """
    Looks at the tets and the convex hull of the points.  If a point is added
    to the points list and the convex hull does not change, it means that this
    point is inside the object and the material is changed.

    A bounding box can be given for a quicker analysis with large meshes - this
    will keep you from having to compare every centroid.
    """

    if len(tets_bbox) > 0:
        for tet in tets_bbox:
            if point_in_3d_poly(tet.centroid, points):
                tets[tet.tnum-1].mat = highest_mat_num+1
    return tets

def write_new_3dm(outfile, nodes, tets):
    with open(outfile, 'w') as ofile:
        ofile.write('MESH3D\n')
        for tet in tets:
            line = 'E4T %03d %05d %05d %05d %05d %d\n' % (tet.tnum,
                    tet.n1.nnum, tet.n2.nnum, tet.n3.nnum, tet.n4.nnum,
                    tet.mat)
            ofile.write(line)
        for node in nodes:
            line = 'ND %03d %5.3f %5.3f %5.3f\n' % (node.nnum, node.x, node.y,
                    node.z)
            ofile.write(line)
        ofile.write('ENDDS')



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
    if ext == "2dm" or ext == "3dm":
        points = points_from_mesh(shapefile)
        points, bbox = bounding_box_points(shapefile, x, y, z, points=points,
                adj=0.05)
    else:
        points, bbox = bounding_box_points(shapefile, x,y,z)
    nodes, tets, highest_mat_num = build_geometry(mesh)
    nodes, tets, tets_bbox = compute_centroids(nodes, tets, bbox)
    tets = change_materials(tets, tets_bbox, points, highest_mat_num)
    write_new_3dm(outfile, nodes, tets)











