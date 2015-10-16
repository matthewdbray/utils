#!/usr/bin/env python 

import sys,os 


if len(sys.argv) < 6: 
   print "This will set up a bash file to run extract_hot_ser.py for a certain # of days"
   print "Usage <Simulation Name> <Hour to start> <Hour to finish> <# of nodes> <# of facets>" 

# Change to current working directory
cwd = os.getcwd()
os.chdir(cwd)

outfile = open("extract_hours.sh", "w") 

sim_name = sys.argv[1]
start_day = int(sys.argv[2])
end_day = int(sys.argv[3])
num_nodes = sys.argv[4]
num_facets = sys.argv[5]

for i in range(start_day, end_day+1):
   line = 'echo "Extracting day: ' + str(i) + '"\n'
   outfile.write(line) 
   line = 'extract_hot_ser.py ' + sim_name + ' ' + str(i) + ' ' + num_nodes + ' ' + num_facets + '\n' 
   outfile.write(line)

outfile.flush()
outfile.close()
