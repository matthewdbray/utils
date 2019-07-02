__author__ = 'matthewbray'

import sys
import os
import math
from random import randrange

#Takes in a csv file in order of TreeType, diameter, height, y-axis, x-axis
#Will fill in height from diameter equation if known

def createHeader(outfile):
    f2.write('<Scene Version="2.0">')
    f2.write('\n')
    f2.write('  <Units Value="Unknown"></Units>')

def typeDefinitions(outfile, models):
    outfile.write('  <TypeDefinitions>\n')
    outfile.write('    <Type Name ="Scene"></Type>\n')
    outfile.write('    <Type Name ="Vegetation"\n')
    outfile.write('          Parent="Scene"></Type>\n')
    for items in models:
        outfile.write('    <Type Name="'+items+'"\n')
        outfile.write('          Parent="Vegetation"></Type>\n')
    outfile.write('  </TypeDefinitions>\n')

def objectFileDirectory(outfile, models):
    fileEntry = {}
    entry = 0
    outfile.write('  <ObjectFileDirectory>\n')
    for i in range(0,len(models)):
        if models[i] == '5x5':
            outfile.write('    <File Name="/Users/matthewbray/Desktop/Geosites/ElJunque/vegtest/'+models[i]+'.obj"></File>\n')
            fileEntry[models[i]] = entry
            entry += 1
        else:
            outfile.write('    <File Name="/Users/matthewbray/Desktop/Geosites/Fraser/vegtest/'+models[i]+'_leaves.obj"></File>\n')
            outfile.write('    <File Name="/Users/matthewbray/Desktop/Geosites/Fraser/vegtest/'+models[i]+'_bark.obj"></File>\n')
            outfile.write('    <File Name="/Users/matthewbray/Desktop/Geosites/Fraser/vegtest/'+models[i]+'_tall_leaves.obj"></File>\n')
            outfile.write('    <File Name="/Users/matthewbray/Desktop/Geosites/Fraser/vegtest/'+models[i]+'_tall_bark.obj"></File>\n')
            fileEntry[models[i]+'_leaves'] = entry
            fileEntry[models[i]+'_bark'] = entry+1
            fileEntry[models[i]+'_tall_leaves'] = entry+2
            fileEntry[models[i]+'_tall_bark'] = entry+3
            entry += 4
    outfile.write('  </ObjectFileDirectory>\n')
    outfile.write('  <TextureFileDirectory></TextureFileDirectory>\n')
    return fileEntry
def objectDefinitions(outfile, veglist, fileEntry):
    z_value = str(-2.2)
    outfile.write('  <ObjectDefinitions>\n')
    types = ['leaves', 'bark']
    for item in veglist:
        spin = str(randrange(360))
        if item[0] == '5x5':
            outfile.write('    <Object Name="'+item[0]+'"\n')
            outfile.write('            NodeType="'+item[0]+'"\n')
            outfile.write('            ObjectType="Faceted"\n')
            outfile.write('            UserDefinedType="-Other"\n')
            outfile.write('            SurfaceType="Other"\n')
            for key in fileEntry:
                arg = key
                arg2 = item[0]
                if arg == arg2:
                    outfile.write('            FileEntry="'+str(fileEntry[key])+'">\n')
            outfile.write('      <Units Value="Unknown"></Units>\n')
            outfile.write('      <Color Value="0.741176 0.741176 0.556863 1"></Color>\n')
            outfile.write('      <Position Value="'+item[4]+' '+item[3]+' '+z_value+'"></Position>\n')
            outfile.write('      <Orientation Value="0 0 ' + spin + '"></Orientation>\n')
            outfile.write('      <Scale Value="1 1 1"></Scale>\n')
            outfile.write('      <Origin Value="0 0 0"></Origin>\n')
            outfile.write('      <Constraints></Constraints>\n')
            outfile.write('    </Object>\n')
        elif float(item[2]) > 0:
            for type in types:
                outfile.write('    <Object Name="'+item[0]+'_tall_'+type+'"\n')
                outfile.write('            NodeType="'+item[0]+'"\n')
                outfile.write('            ObjectType="Faceted"\n')
                outfile.write('            UserDefinedType="-Other"\n')
                outfile.write('            SurfaceType="Other"\n')
                for key in fileEntry:
                    arg = key
                    arg2 = item[0] + '_tall_' + type
                    if arg == arg2:
                        outfile.write('            FileEntry="'+str(fileEntry[key])+'">\n')
                outfile.write('      <Units Value="Unknown"></Units>\n')
                if type is 'leaves':
                    if item[0] == 'spruce':
                        outfile.write('      <Color Value="0.00392157 0.282353 0.0470588 1"></Color>\n')
                    else:
                        outfile.write('      <Color Value="0.191287 0.392859 0.101305 1"></Color>\n')
                else:
                    outfile.write('      <Color Value="0.741176 0.741176 0.556863 1"></Color>\n')
                outfile.write('      <Position Value="'+item[4]+' '+item[3]+' '+z_value+'"></Position>\n')
                outfile.write('      <Orientation Value="0 0 0"></Orientation>\n')
                outfile.write('      <Scale Value="' + str((float(item[2])*0.4925+0.1234)) + ' ' + str((float(item[2])*0.4925+0.1234)) + ' ' + str(item[2]) + '"></Scale>\n')
                outfile.write('      <Origin Value="0 0 0"></Origin>\n')
                outfile.write('      <Constraints></Constraints>\n')
                outfile.write('    </Object>\n')
        else:
            for type in types:
                outfile.write('    <Object Name="'+item[0]+'_'+type+'"\n')
                outfile.write('            NodeType="'+item[0]+'"\n')
                outfile.write('            ObjectType="Faceted"\n')
                outfile.write('            UserDefinedType="-Other"\n')
                outfile.write('            SurfaceType="Other"\n')
                for key in fileEntry:
                    arg = key
                    arg2 = item[0] + '_' + type
                    if arg == arg2:
                        outfile.write('            FileEntry="'+str(fileEntry[key])+'">\n')
                outfile.write('      <Units Value="Unknown"></Units>\n')
                if type is 'leaves':
                    if item[0] == 'spruce':
                        outfile.write('      <Color Value="0.00392157 0.282353 0.0470588 1"></Color>\n')
                    else:
                        outfile.write('      <Color Value="0.191287 0.392859 0.101305 1"></Color>\n')
                else:
                    outfile.write('      <Color Value="0.741176 0.741176 0.556863 1"></Color>\n')
                outfile.write('      <Position Value="'+item[4]+' '+item[3]+' '+z_value+'"></Position>\n')
                outfile.write('      <Orientation Value="0 0 ' + spin + '"></Orientation>\n')
                outfile.write('      <Scale Value="' + str((float(item[2])*0.4925+0.1234)) + ' ' + str((float(item[2])*0.4925+0.1234)) + ' ' + str(item[2]) + '"></Scale>\n')
                outfile.write('      <Origin Value="0 0 0"></Origin>\n')
                outfile.write('      <Constraints></Constraints>\n')
                outfile.write('    </Object>\n')

def addFooter(outfile):
    outfile.write('  </ObjectDefinitions>\n')
    outfile.write('  <UserDefinedTypeDefinitions>\n')
    outfile.write('    <UserType Name="-Other"></UserType>\n')
    outfile.write('  </UserDefinedTypeDefinitions>\n')
    outfile.write('</Scene>\n')

def takeOutUnderNum(veglist):
    count = 0
    tot_veg = len(veglist)
    num = 5
    new_veglist = []
    for i in range(0, len(veglist)):
         if float(veglist[i][2]) > num:
             new_veglist.append(veglist[i])
             count += 1
    print 'Removed', tot_veg-count, 'trees under', num, 'meters'
    return new_veglist

def rotatePoints(veglist):
    rotated_veg = []
    for item in veglist:
        degrees = 0
        radians = math.pi * degrees / 180
        x = float(item[4])
        y = float(item[3])
        x_rot = x*math.cos(radians) - y*math.sin(radians)
        y_rot = x*math.sin(radians) + y*math.cos(radians)
        item[3] = str(round(y_rot, 3))
        item[4] = str(round(x_rot, 3))
        rotated_veg.append(item)
    return rotated_veg

def translatePoints(veglist):
    translated_veg = []
    for item in veglist:
        move_x = 0
        move_y = 0
        item[3] = str(float(item[3]) + move_y)
        item[4] = str(float(item[4]) + move_x)
        translated_veg.append(item)
    return translated_veg

filename = '/Users/matthewbray/Desktop/Geosites/Fraser/a.csv'
outfile = '/Users/matthewbray/Desktop/Geosites/Fraser/new.sg'

f1 = open(filename, 'r')
f2 = open(outfile, 'w')

lst = []

#Read in the file
for line in f1.readlines():
    lst.append(line)



#Break up lines into their component pieces and get rid of \n
tmplist = []
veglist = []
for line in lst:
    tmplist = line.split(',')
    veglist.append(tmplist)

veglist = [ [ x.rstrip('\n').lower() for x in item ] for item in veglist ]
#veglist.pop(-1)  #Removes last line which is empty

#Rotate the veg if necessary
#veglist = rotatePoints(veglist)

#Translate the vegs to fit the 5x5 if necessary
#veglist = translatePoints(veglist)

#Begin creating XML file
createHeader(f2)

#Get list of trees
vegmodels = []
vegmodels.append(str(veglist[0][0]))
j = 0
for i in range(0, len(veglist)):
    if str(veglist[i][0]).lower() not in vegmodels:
        vegmodels.append(str(veglist[i][0]))
        j += 1
print 'There are', len(vegmodels), 'different veg models being placed.\n'

#Found ratio of diameter to height using excel

vegCount = {'spruce' : lambda x: 1.4287*x+3.7747, 'pine' : lambda x: 1.3518*x + 2.7664, 'fir' : lambda x: x*1.1216+5.716 }

#Fill out empty values using equations in dictionary
for i in range(0,len(veglist)):
    if veglist[i][2] == '':
        for keys in vegCount:
            if veglist[i][0] == keys:
                veglist[i][2] = vegCount[keys](float(veglist[i][1]))

#If you want trees under 5 meters comment this part out
#veglist = takeOutUnderNum(veglist)

#Finish up the XML file
typeDefinitions(f2, vegmodels)

fileEntry = objectFileDirectory(f2, vegmodels)

objectDefinitions(f2, veglist, fileEntry)

addFooter(f2)

#x = []; y = []
#
#for item in veglist:
#    x.append(item[4])
#    y.append(item[3])
#
#plot(x,y)