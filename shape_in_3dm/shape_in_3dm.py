#!/usr/bin/env python

"""
Author: Matthew Bray
Date: Mar 27, 2015

The purpose of this program is to read in 3dm files and change the materials
in different polygons that we are feeding it.  This could be as simple as a
parallelepiped (box) or something that looks like a mortar shell.

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

def bounding_box_points(shapefile, depth, x, y, z, points=None):
    """
    Loads the shapefile into a numpy array and returns a ccw bounding box
    """

    if not points.any():  # Not read in already from a 2dm
        points = np.loadtxt(shapefile, dtype=float)

    # Get the top most part of the 2dm at the 0 point and
    # then accounting for depth
    to_zero = np.array((0,0,points[:,2].max()+float(depth)), 
            dtype=float)
    points -= to_zero

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

    # Returning min and max for x,y,z
    bbox = np.array(((min_x, min_y, min_z), (max_x, max_y, max_z)))
    print 'Bounding box - ' 
    print bbox
    return points, np.array(((min_x, min_y, min_z), (max_x, max_y, max_z)))

def point_in_3d_poly(x,y,z, poly):
    """
    Seeing if a point is inside a polygon in three dimensions.
    node is a Node class that has an x,y, and z.
    Poly is a numpy array of points that make up the poly


    This makes a 3D convex hull with the regular points, then adds the new
    point to the list and makes a new convex hull.  Assumedly if this list
    doesn't change then the centroid is inside the convex hull
    """
    hull = ConvexHull(poly)
    new_pt = np.array([[x, y, z]], dtype=float)
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
                node = (split[1], split[2], split[3])
                nodes.append(node)
                nnodes += 1
            elif split[0] == "E4T":
                ntets += 1
                if int(split[-1]) > highest_mat_num:
                    highest_mat_num = int(split[-1])

    print "There are\n\t{} nodes\n\t{} tets\n\thighest material number is "\
            "{}".format(nnodes, ntets, highest_mat_num)

    return nodes, highest_mat_num

def compute_centroids(mesh, nodes, bbox, highest_mat_num, poly, outfile):
    """
    Computes the centroid for each tet, and also figures out whether it is in
    the bounding box of the pts that you're wanting to change if a bbox is
    given as np.array(((min_x,min_y,min_z),(max_x,max_y,max_z)))
    """
    print "Computing node values and centroids ... "

    # Opening the outfile for writing
    ofile = open(outfile, 'w')

    tets_bbox = []

    min_x, min_y, min_z = bbox[0]
    max_x, max_y, max_z = bbox[1]

    # Reopening file for another iteration
    with open(mesh) as infile:
        for line in infile: 

            foundTet = False

            if line is not None: 
                split = line.split()
                marker = split[0]
            if marker == "ND": 
                ofile.write(line) 
            elif marker == "E4T": 
                tetline = [int(x) for x in split if x != "E4T"]
                tnum, n1, n2, n3, n4, mat = tetline
                n1x, n1y, n1z = nodes[n1-1]
                n2x, n2y, n2z = nodes[n2-1]
                n3x, n3y, n3z = nodes[n3-1]
                n4x, n4y, n4z = nodes[n4-1]

                # Computing averages
                cx = np.sum((n1x, n2x, n3x, n4x), dtype=float) * 0.25
                cy = np.sum((n1y, n2y, n3y, n4y), dtype=float) * 0.25
                cz = np.sum((n1z, n2z, n3z, n4z), dtype=float) * 0.25

                if min_x <= cx <= max_x: 
                    if min_y <= cy <= max_y: 
                        if min_z <= cz <= max_z:
                            if point_in_3d_poly(cx, cy, cz, poly):
                                print "Found a tet to change: %d" % tnum
                                foundTet = True
                                outline = "E4T %5d %5d %5d %5d %5d %d\n" %\
                                        (tnum, n1, n2, n3, n4, highest_mat_num+1)
                                ofile.write(outline)
                if foundTet is False: 
                    ofile.write(line)
            else:
                ofile.write(line)

    print "--DONE--"

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
    parser.add_argument('-d', '--depth', action='store', required=True, 
            dest='depth', help='This is the depth you want to bury the obj')
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
    depth = results.depth
    x = results.x
    y = results.y
    z = results.z
    outfile = results.outfile

    ext = shapefile.split('.')[-1]
    if ext == "2dm" or ext == "3dm":
        points = points_from_mesh(shapefile)
        points, bbox = bounding_box_points(shapefile, depth, x, y, z, 
                points=points)
    else:
        points, bbox = bounding_box_points(shapefile, depth, x,y,z)
    nodes, highest_mat_num = build_geometry(mesh)
    compute_centroids(mesh, nodes, bbox, highest_mat_num, points, outfile)
#    tets = change_materials(tets, tets_bbox, points, highest_mat_num)
#    write_new_3dm(outfile, nodes, tets)











