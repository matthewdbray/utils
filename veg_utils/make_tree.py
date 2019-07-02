__author__ = 'matthewbray'


#Read in csv file
filename = 'eljunque.csv'
f1 = open('/Users/matthewbray/Desktop/Geosites/ElJunque/' + filename, 'r')
n_filename = filename.split('.')
n_filename = n_filename[0] + '_wtrees.csv'
f2 = open(n_filename, 'w')
lst = []
veg_list = []
for line in f1.readlines():
    lst.append(line)

tmplist = []
for line in lst:
    tmplist = line.split(',')
    veg_list.append(tmplist)

veg_list = [ [ x.rstrip('\n').lower() for x in item] for item in veg_list]

tree_models = ['trumpetwood', 'sierrapalm','didimoponax']

for i in range(0, len(veg_list)):
    if veg_list[i][0] in tree_models:
        leaves_line = veg_list[i][:]
        bark_line = veg_list[i][:]
        leaves_line[0] = leaves_line[0] + '_leaves'
        bark_line[0] = bark_line[0] + '_bark'
        veg_list.append(leaves_line)
        veg_list.append(bark_line)

for line in veg_list:
    for item in tree_models:
        if line[0] == item:
            del line[:]
            break


veg_list = filter(None, veg_list)

for line in veg_list:
    line = ','.join(line)
    f2.write(line)
    f2.write('\n')