#!/bin/python
# BoxScaler: finds optimal box size ratios for scaling data
# Max Wilkinson, MRC LMB, October 2018



import numpy as np

################

startbox = input("What is the smallest box size allowed? ")
finishbox = input("What is the largest box size allowed? ")
startApix = input("What is your starting pixel size? ")
endApix = input("What is the desired final pixel size? ")
ntimes = input("and how many answers do you want? ")

# if provided box size is odd
if startbox % 2 != 0:
    startbox += 1

# get desired ratio
apixRatio=startApix/endApix

# produce range of possible box sizes and compute a division matrix between them all
boxArray = np.arange(startbox,finishbox,2,dtype=float)
ratioArray = np.divide.outer(boxArray,boxArray)
i = 1
while i <= ntimes:
    # find index of closest box size ratio to the desired angpix ratio
    idxMin = np.abs(ratioArray - apixRatio).argmin()
    indxMin2D = np.unravel_index(idxMin,ratioArray.shape)  #unravel_index converts a 1D index into a 2D index based on the dimensions given by .shape

    # use x and y of this index to find the starting and ending box sizes
    startscale=boxArray[indxMin2D[1]]
    endscale=boxArray[indxMin2D[0]]

    # print output
    print('Starting with a {:.0f} pixel box, scale to a {:.0f} pixel box'.format(startscale, endscale))
    print('This will give a scaling factor of {:.5f}, compared to a desired pixel size ratio of {:.5f}, giving a {:.3f} percent error.\n'.format(endscale/startscale, apixRatio, (endscale/startscale-apixRatio)/apixRatio*100))
    # remove this answer from ratioarray by setting it to a very large number
    ratioArray.flat[idxMin] = 999.
    i += 1

