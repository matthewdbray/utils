#!/usr/bin/env python                                                              

import commands
import glob
import os 
import sys

def createmovie(full_name):                                                        
                                                                                   
                                                                                   
   cwd = os.getcwd()                                                               
   os.chdir(cwd)                     

   files = glob.glob('*')
   jpgFiles = False
   tifFiles = False
   for f in files:
       ext = f.split('.')[-1]
       if ext == 'jpg':
           print "Found jpg file: %s" % f
           jpgFiles = True
           tifFiles = False
           print "Already converted to jpg files"
           break
       elif ext == 'tif':
           tifFiles = True
   if tifFiles:
       print "Converting from tif to jpg"
       convertTiff()

   print "Creating mp4"                                                            
   cmd = 'ffmpeg -framerate 10 -pattern_type glob -i "*.jpg" -c:v libx264 %s.mp4' % full_name 
   failure, output = commands.getstatusoutput(cmd)                                 
   print failure, output 
                                                                                   
   print "Creating wmv"                                                            
   cmd = 'ffmpeg -i %s.mp4 -c:v wmv2 -b:v 20M -s 720x720 -c:a wmav2 -b:a 192k %s.wmv' % (full_name, full_name) 
   failure, output = commands.getstatusoutput(cmd)                                 
                                                                                   
   print "--DONE--"                                                                
                                                                                   

def convertTiff():

    files = glob.glob("*.tif")
    for f in files: 
        basename = f.split('.tif')[0] 
        cmd = 'convert -quality 100 -resize 30% '
        cmd += '%s %s.jpg' % (f, basename) 
        failure, output = commands.getstatusoutput(cmd)
        print "Coverted file %s" % f 


if __name__ == '__main__':                                                         
                                                                                   
   if len(sys.argv) != 2:                                                          
      print 'Usage: you need to give the name of the movie in the command line.'
      exit()                                                                       
   else:                                                                           
      full_name = sys.argv[1]                                                      
                                                                                   
   createmovie(full_name)    
