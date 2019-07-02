#!/usr/bin/env python

__author__ = 'matthewbray'

def getData(filename):
    ''' Gets the data from a csv veg file that you're looking to process
    '''
    f = open(filename)

    data = []

    for line in f.readlines():
        data.append(line)

    data = [d.rstrip('\n') for d in data]
    data = filter(None, data)
    return data

def findGroups(data):
    ''' This goes through the input file and finds if any of them are doubles, triples, etc
         Make sure that when you use this you do for ex: creosote_3_group_2  for a double
    '''
    from random import uniform
    new_data = []
    for d in data:
        isGroup = False
        dsn = d.split(',')[0].split('_')
        ds = d.split(',')
        for p in dsn:
            if p == 'group':
                isGroup = True
                new_name = ''.join(d.split(',')[0].split('_')[:1])
                ds[0] = new_name
                new_data.append(','.join(ds))
                num = int(dsn[-1])
                for i in range(num-1):
                    rand_x = round(uniform(-0.3,0.3),3)
                    rand_y = round(uniform(-0.3,0.3),3)
                    rand_s = round(uniform(-0.3,0.3),3)
                    ds[1] = float(ds[1]) + rand_s
                    ds[2] = float(ds[2]) + rand_x
                    ds[3] = float(ds[3]) + rand_y
                    ds = [str(x) for x in ds]
                    new_data.append(','.join(ds))
            else:
                 pass
        if isGroup is False:
           new_data.append(d)

    return new_data

def findCircles(data):
    ''' This will find circles if you are giving it the diameter as the size field
        These will have an extra field right after the obj name to tell the width (diameter) of the circle
        For ex: creosote_circle_7
    '''
    from random import uniform
    from math import pi
    from math import sin
    from math import cos
#    import matplotlib.pyplot as plt
    new_data = []
    for d in data:
        isCircle = False
        dsn = d.split(',')[0].split('_')
        ds = d.split(',')
        num = 0
        x_offset = float(ds[2])
        y_offset = float(ds[3])
#        x = []
#        y = []
        for p in dsn:
            #  Find out if it includes circle in the name
            if p == "circle":
                isCircle = True
                # find out how many plants are in the circle
                num = int(dsn[-1])
                diameter = float(ds[1])
                r = diameter/2.0
                new_name = ''.join(d.split(',')[0].split('_')[:1])
                ds[0] = new_name
                for i in range(num):
                    # Create random points along the circumference with random x and y jiggle and random size
                    # The size in the input file is the diameter of the circle
                    theta = round(uniform(0,360),3)
                    rsize = round(uniform(0.3, 1.2), 3)
                    ds[1] = rsize
                    rjiggle = uniform(-0.4,0)
                    ds[2] = round((r+ rjiggle) * cos(theta) + x_offset,3)
                    ds[3] = round((r + rjiggle) * sin(theta) + y_offset,3)
#                    x.append(ds[2])
#                    y.append(ds[3])
                    ds =  [ str(item) for item in ds ]
                    new_data.append(','.join(ds))
            else:
                pass
        if isCircle is False:
            new_data.append(d)
#   plt.scatter(x,y)
#   plt.show()
    return new_data

def randomizeVeg(data, model, numModels):
    ''' This is used to randomize which models go where in your veg csv
        The veg model needs to be an exact match and will then add _1, _2, _3 depending on how many models you have
    '''
    from random import randrange
    new_data = []
    for d in data:
        ds = d.split(',')
        if ds[0] == model:
            num = randrange(0,numModels)
            if num is 0:
                new_data.append(d)
            if num is not 0:
                ds[0] = ds[0] + '_' + str(num)
                new_data.append(','.join(ds))
        else:
            new_data.append(d)
    new_data = [x.rstrip('\r') for x in new_data]
    return new_data

def scanForFlowersOrLeaves(data):
    ''' Handle leaves and flowers by the fourth and fifth column
        1 means they will have leaves or flowers and _bark and _leaves/_flowers will be added
        Also adds in random orientation so the bark/leaves/flowers match one another.
    '''
    from random import randrange
    new_data = []
    for d in data:
        d = d.split(',')
        if d[-2].lstrip() == '1' and d[-1].lstrip() == '1':
            bark = d[0] + '_bark'
            leaves = d[0] + '_leaves'
            flowers = d[0] + '_flowers'
            d = d[1:]
            coords = ',' + ','.join(d)
            rand_ori = str(randrange(0,360))
            coords = coords + ',' + rand_ori
            bark_veg = bark + coords
            leaves_veg = leaves + coords
            flowers_veg = flowers + coords
            new_data.append(bark_veg)
            new_data.append(leaves_veg)
            new_data.append(flowers_veg)
        elif d[-2].lstrip()  == '1' and d[-1].lstrip() == '0':
            bark = d[0] + '_bark'
            leaves = d[0] + '_leaves'
            d = d[1:4] 
            coords = ',' + ','.join(d)
            rand_ori = str(randrange(0,360))
            coords = coords + ',' + rand_ori
            bark_veg = bark + coords
            leaves_veg = leaves + coords
            new_data.append(bark_veg)
            new_data.append(leaves_veg)
        elif d[-2].lstrip() == '0' and d[-1].lstrip() == '1':
            #  This must be a flower
            leaves = d[0] + '_leaves'
            flowers = d[0] + '_flowers'
            d = d[1:]
            coords = ',' + ','.join(d)
            rand_ori = str(randrange(0,360))
            coords = coords + ',' + rand_ori 
            leaves_veg = leaves + coords
            flowers_veg = flowers + coords
            new_data.append(leaves_veg)
            new_data.append(flowers_veg)
        elif d[-2].lstrip() == '0' and d[-1].lstrip() == '0':
            rand_ori = str(randrange(0,360))
            d = d[:-2]
            rand_ori = str(randrange(0,360)) 
            d.append(rand_ori)
            new_data.append(','.join(d))
    return new_data

def writeVegList(filename, data):
    info = filename.split('/')
    file = info[-1].split('.')[0]
    path = '/'.join(info[:-1]) + '/'
    outfile = open(path + file + '_forinput.csv', 'w')
    for d in data:
        outfile.write(','.join(d.split(',')))
        outfile.write('\n')


if __name__ == '__main__':
    filename = '/Users/matthewbray/Dropbox/flash.csv'
    d = getData(filename)
    models = {'creosote':2, 'green_bush':2, 'fuzzball':5}
    for key, value in models.iteritems():
       d = randomizeVeg(d, model = key, numModels = value)
    d = findGroups(d)
    d = findCircles(d)
    d = scanForFlowersOrLeaves(d)
    writeVegList(filename, d)

