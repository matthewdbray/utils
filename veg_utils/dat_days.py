#!/usr/bin/env python

# Use this inside a folder of a day of veg_Temp_#.dat files
# This will put the appropriate hours in the files



import sys 

start_hr = int(sys.argv[1])


for i in range(24):
    outfile = 'veg_Temp_' + str(start_hr) + '.dat'
    infile = 'veg_Temp_' + str(i) + '.dat'
    with open(outfile, 'w') as ofile: 
        with open(infile) as ifile: 
            lines = []
            nlines = []
            for line in ifile.readlines(): 
                if line.split()[0] == "TS": 
                    h, o, t = line.split()
                    t = str(start_hr)
                    nline = ' '.join([h,o,t]) + '\n'
                    ofile.write(nline)
                else: 
                    ofile.write(line)
    start_hr += 1 



