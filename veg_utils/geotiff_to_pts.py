__author__ = 'matthewbray'

## Give the filename
## Converts geotiff to lidar pts

import sys
import os
import gdal
import numpy

work_dir = os.getcwd() + '/'
filename = sys.argv[1]

ds = gdal.Open( filename, gdal.GA_ReadOnly )

filename_pts = filename + '.pts'

pts = open(filename_pts, 'w')

x_ori, dx, rot, y_ori, dy, rot = ds.GetGeoTransform()
Nx = ds.RasterXSize
Ny = ds.RasterYSize

z_array = ds.GetRasterBand(1).ReadAsArray()
z_array = numpy.flipud(z_array)


tot_pixels = str(Nx*Ny)
pts.write(tot_pixels+'\n')

for i in range(0, -Ny, -1):
    for j in range(0, Nx):
        x = str(x_ori + j)
        y = str(y_ori + i)
        z = str(z_array[i][j])
        junk = '100 125 125 125\n'
        line = '%s %s %s %s' % (x,y,z,junk)
        pts.write(line)

