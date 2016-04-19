#!/usr/bin/env python

def enhancecolors(new_folder):
   
   import sys
   import os 
   import Image
   import ImageEnhance
   import glob
   import numpy as np 
   import shutil

   #getting to the right directory
   cwd = os.getcwd() 
   os.chdir(cwd)
  
   #grabbing all the jpg files
   files = glob.glob("*.jpg")
   print "%d number of files to be converted" % len(files)
   #creating a folder for adjusted images
   try:
      os.mkdir(new_folder) 
   except OSError:
      shutil.rmtree(new_folder)
      os.mkdir(new_folder)

   cnt = 0
   #iterating through the files
   for file in files: 
      new_filename = file.split('.jpg')
      new_filename = str(new_filename[0]) + '_adj.jpg'
      img = Image.open(file)

      #getting histogram of colors for ratio (black band)
      hist, bins = np.histogram(img.histogram(), bins = 255) 

      #some ratio I got from doing it manually on one time step
      ratio = 13.0/725

      #Image manipulation
      bright = ImageEnhance.Brightness(img)
      img = bright.enhance(hist[0]*ratio)
      color = ImageEnhance.Color(img)
      img = color.enhance(0.8)

      #Saving file
      cnt += 1 
      img.save(new_folder + '/' + new_filename, "JPEG")
      print "Processed " + file + " number",cnt


if __name__ == '__main__':
   import sys
   
   if len(sys.argv) != 2:
      print 'Please provide new folder in which to put adjust images in.'
      exit()
   else:
      new_folder = sys.argv[1]

   enhancecolors(new_folder)
   
