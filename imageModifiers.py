import numpy as np
import matplotlib.pyplot as plt

from skimage import filters as skimfilt

# project the image onto a specific direction
def project(img, direction):
    if direction == "x":
        proj = np.sum(img, 0)
    elif direction == "y":
        proj = np.sum(img, 1)
    else:
        print("Direction must be one of 'x' or 'y'")
        proj = []
    return proj

# binarize an image
def binarizeImg(img, threshFn = None, biThresh = None, greater = True, plotIt = False):
    if threshFn is not None:
        biThresh = threshFn(img)
    elif biThresh is None:
        biThresh = 0
    if greater:
        imgCp = img > biThresh
    else:
        imgCp = img < biThresh
    
    if plotIt:
        plt.imshow(imgCp, cmap = "gray")
        plt.show()
    return imgCp, biThresh

# smooth an image
def smoothImg(img, sigma, plotIt = False):
    imgCp = skimfilt.gaussian(img, sigma=sigma, multichannel=False)
    if plotIt:
        plt.imshow(imgCp, cmap = "gray")
        plt.show()
    return imgCp

# remove the edges from an image
def removeEdges(grey, let, pageBlur, plotit = False):
    level1Mask = binarizeImg(grey, skimfilt.threshold_triangle, greater=False)[0]
    blurredLevel1Mask = smoothImg(level1Mask, sigma=pageBlur)

    level2TrimLevels = ['hard', 'soft']
    level2ThreshFn = {'hard' : skimfilt.threshold_yen,
                       'soft' : skimfilt.threshold_mean}
    level2Mask = { label : binarizeImg(blurredLevel1Mask, fn, greater=False)[0]
                  for label, fn in level2ThreshFn.items() }
    xProjectedL2Mask = { label : project(mask, 'y')
                        for label, mask in level2Mask.items() }
    yProjectedL2Mask = { label : project(mask, 'x')
                        for label, mask in level2Mask.items() }
    level2TrimMask = {label : np.outer(xProjectedL2Mask[label], 
                                       yProjectedL2Mask[label]) > 0
                      for label in level2Mask.keys() }
    level2TrimOffsets = {label : (np.nonzero(xProjectedL2Mask[label])[0][0],
                                  np.nonzero(yProjectedL2Mask[label])[0][0])
                         for label in level2Mask.keys() }
    
    greyTrimmed = {label : grey[mask].reshape(np.count_nonzero(xProjectedL2Mask[label]),
                                               np.count_nonzero(yProjectedL2Mask[label]))
                    for label, mask in level2TrimMask.items() }
    letTrimmed = {label : let[mask].reshape(np.count_nonzero(xProjectedL2Mask[label]),
                                            np.count_nonzero(yProjectedL2Mask[label]),
                                            3)
                  for label, mask in level2TrimMask.items() }
    
    otherInfo = {'level1Mask': level1Mask,
                 'blurredLevel1Mask': blurredLevel1Mask, 
                 'level2TrimLevels': level2TrimLevels,
                 'level2Mask': level2Mask,
                 'xProjectedL2Mask': xProjectedL2Mask, 
                 'yProjectedL2Mask': yProjectedL2Mask,
                 'level2TrimMask': level2TrimMask,
                 'level2TrimOffsets': level2TrimOffsets}
    
    if plotit:
        # plot level 1
        subjectFigure, subjectAxes = plt.subplots(figsize=(90, 60),
                                                      ncols=2, nrows=1)
        subjectAxes.flatten()[0].imshow(level1Mask, cmap = 'gray')
        subjectAxes.flatten()[1].imshow(blurredLevel1Mask, cmap = 'gray')
        plt.show()

        # plot level 2
        subjectFigure, subjectAxes = plt.subplots(figsize=(30, 20), ncols=3, nrows=2)
        # soft
        subjectAxes.flatten()[0].imshow(level2Mask['soft'], cmap = 'gray')
        subjectAxes.flatten()[1].imshow(level2TrimMask['soft'], cmap = 'gray')
        subjectAxes.flatten()[2].imshow(greyTrimmed['soft'], cmap = 'gray')
        # hard
        subjectAxes.flatten()[3].imshow(level2Mask['hard'], cmap = 'gray')
        subjectAxes.flatten()[4].imshow(level2TrimMask['hard'], cmap = 'gray')
        subjectAxes.flatten()[5].imshow(greyTrimmed['hard'], cmap = 'gray')
        plt.show()
        
    return greyTrimmed, letTrimmed, otherInfo
