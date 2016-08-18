#!/usr/bin/env python
"""keysight_convert.py v0.1 (written in python 2.7)

convert csv files to keysight/agilent 81150A binary waveforms
x values have to be floats between 0 and 1 (first point should start with x=0)
y values have to be floats between -1 and +1

csv format:

<xval1>,<yval1>
<xval2>,<yval2>
<xval3>,<yval3>
...

example:

./keysight_convert.py -i example.csv

2016 by Michael Wiebusch
http://mwiebusch.de
"""
import numpy as np
from matplotlib import pyplot as plt
import argparse
import re


#small helper fuction for little endian/big endian conversion stuff
def flip(num):
  return bytearray([num & 0xFF,(num & 0xFF00)>>8])


def main():

  # Parse command-line arguments
  parser = argparse.ArgumentParser(usage=__doc__)
  parser.add_argument("-i","--input", help="input file (csv)")
  parser.add_argument("-o","--output", help="output binary file, otherwise input filename + .wfm extension will be used")
  args = parser.parse_args()

  #remove file extension, add wfm
  infile_base = re.split('\.[^\.]+$',args.input)[0]
  outfile=infile_base+".wfm"
  if args.output:
    outfile=args.output

  a = np.loadtxt(open(args.input,"rb"),delimiter=",",skiprows=1)

  #print a

  x=a[:,0]
  y=a[:,1]

  #plt.plot(x,y)
  #plt.show()

  no_points = x.size
  
  print "converting "+str(no_points)+" data points"
  
  #the file skeleton (with stuff in it that I don't understand
  template = "42FEAF4201000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000400000FF000000D80E05000000000000409F4000000000000000000000008040D594407DBFBE2AFFFFF73F0100000000000000"
  #with open('template.bin', 'rb') as f:
      #data = f.read()
      
  b = bytearray(template.decode("hex"))

  ##debug output
  #print ''.join('{:02X}'.format(x) for x in b)

  #insert number of points
  b[0x50] = no_points & 0xFF
  b[0x51] = (no_points & 0xFF00)>>8
  
  #insert file name (first 8 characters)
  for i in range(0,8):
    if(i < len(infile_base)):
      b[0x08+2*i] = infile_base[i]

  #append data points
  for i in range(0,no_points):
    b=b+flip(min(0x3FFF,int(0x4000*x[i])))
    b=b+flip(0)
    b=b+flip(int(0x1FFF*y[i]))
    b=b+flip(0)

  #first point has to start at zero. or the function generator will crash. enforce it
  b[0x80] = 0
  b[0x81] = 0

  #write out finished binary
  print "done."
  print "writing output file: "+outfile
  with open(outfile, 'wb') as f:
    f.write(b);
  print "done."
    
   
if __name__ == "__main__":
  main()
