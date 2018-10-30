#!/bin/python
# BoxScaler: finds optimal box size ratios for scaling data
# Max Wilkinson, MRC LMB, October 2018



import numpy as np

################
# Take inputs
#startbox=408
#finishbox=408
boxrange=300    # edit this to search a bigger range of box sizes
#startApix=1.025
#endApix=1.055

startbox = input("What is the smallest box size allowed? ")
startApix = input("What is your starting pixel size? ")
endApix = input("What is the desired final pixel size? ")
ntimes = input("and how many answers do you want? ")



# get desired ratio
apixRatio=startApix/endApix

# produce range of possible box sizes and compute a division matrix between them all
boxArray = np.arange(startbox,startbox+boxrange,2,dtype=float)
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
    print 'Start with box size', startscale, 'scale to box size', endscale
    print 'This will give a scaling factor of', endscale/startscale, 'compared to desired apix ratio of', apixRatio, 'giving a', (endscale/startscale-apixRatio)/apixRatio*100, 'percent error'
    print ''
    # remove this answer from ratioarray by setting it to a very large number
    ratioArray.flat[idxMin] = 999.
    i += 1

