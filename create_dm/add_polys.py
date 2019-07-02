#!/usr/bin/env python

import sys

if __name__ == '__main__': 
    
    nodes = []
    elements = []
    mat_num = 10 
    nelements = 0
    node_offset = 0

    for i in range(len(sys.argv)-1):
        infile = sys.argv[i+1]
        line_num = 1
        has_mat = False
        print "Reading %s" % infile
        with open(infile) as ifile: 
            print "Node offset is now:", node_offset
            with open('combined.poly','w') as ofile:
                header = ifile.readline() 
                nnodes = int(header.split()[0])
                print "Number of nodes", nnodes
                for line in ifile.readlines(): 
                    if line_num <= nnodes:
                        line = line.split()[1:]
                        line = ' '.join(line)
                        nodes.append(line)
                    elif line_num == nnodes+1:
                        ele_header = line.split()
                        nelements += int(ele_header[0])
                        if int(ele_header[1]) == 1:
                            has_mat = True
                    else:
                        if line.split()[0] != '1' and line.split()[0] != '0':
                            if has_mat:
                                line = line.rstrip('\n')
                                ele = line.split()[1:-1]
                                try:
                                    ele = [int(e) + node_offset for e in ele]
                                except:
                                    continue
                                ele.append(mat_num)
                                ele = [str(e) for e in ele]
                                ele = line.split()[0] + ' ' + ' '.join(ele) 
                                elements.append(ele)
                            else:
                                ele = line.rstrip('\n')
                                ele = ele.split()[1:]
                                try:
                                    ele = [int(e) + node_offset for e in ele]
                                except:
                                    continue
                                #ele.append(mat_num)
                                ele = [str(e) for e in ele]
                                ele = line.split()[0] + ' ' + ' '.join(ele)
                                elements.append(ele)
                    line_num += 1 
            node_offset += nnodes
            mat_num += 10

        with open('combined.poly', 'w') as ofile: 
            ofile.write('%d 3 0 0\n' % len(nodes))
            for i,n in enumerate(nodes): 
                line = '%d %s\n' % (i+1, n)
                ofile.write(line)
            ofile.write('%d 0\n' % len(elements))
            for e in elements:
                ofile.write('1\n')
                ofile.write('%s\n' % e)

                


                        

                





