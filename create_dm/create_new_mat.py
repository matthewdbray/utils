#!/usr/bin/env python

import numpy as np 
import sys

def bounding_box(pts, min_x=-np.inf, max_x=np.inf, min_y=-np.inf,
        max_y=np.inf, min_z=-np.inf, max_z=np.inf):

    bound_x = np.logical_and(pts[:, 0] > min_x, pts[:, 0] < max_x)
    bound_y = np.logical_and(pts[:, 1] > min_y, pts[:, 1] < max_y)
    bound_z = np.logical_and(pts[:, 2] > min_z, pts[:, 2] < max_z)

    bb_filter_xy = np.logical_and(bound_x, bound_y)
    bb_filter = np.logical_and(bb_filter_xy, bound_z)

    return bb_filter

if __name__ == '__main__': 

    mesh = sys.argv[1]

    rectangle = np.array([[0.2, 0.2, 0.2],
                         [0.4, 0.4, 0.4]])

    min_x = rectangle[:,0].min()
    max_x = rectangle[:,0].max()
    min_y = rectangle[:,1].min()
    max_y = rectangle[:,1].max()
    min_z = rectangle[:,2].min()
    max_z = rectangle[:,2].max()

    inside_box = bounding_box(pts, min_x=min_x, max_x=max_x, min_y=min_y, 
            max_y=max_y, min_z=min_z, max_z=max_z)

    points_inside_box = pts[inside_box]

    print len(points_inside_box)
