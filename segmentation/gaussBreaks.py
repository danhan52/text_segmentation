import numpy as np
from scipy import ndimage
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import transform as tf
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle as Rec
from skimage import filters as skimfilt
from segmentation.imageModifiers import *


def gaussBreaks(chunk, nu=3.5, biThresh=2, shear=0.6, fix=15, order=0, plotIt=False,
               threshFn = skimfilt.threshold_otsu):
    # get smoothing factors
    sigYs = np.arange(1, 8, 0.3)
    sigXs = sigYs * nu
    # shear the image
    oldrg = (np.max(chunk) - np.min(chunk))
    newrg = 2
    ch2 = (((chunk - np.min(chunk)) * newrg) / oldrg) - 1
    mytf = tf.AffineTransform(shear=shear)
    chunk = tf.warp(ch2, inverse_map=mytf)
    
    # choose which smoothing factor to use based on minimizing
    # the white space
    extents = []
    count = 0
    for j in range(len(sigYs)):
        filt = gf(input=chunk, sigma=(sigYs[j],sigXs[j]), order=order)
        if count < biThresh:
            binfilt, th = binarizeImg(filt, threshFn)
            count += 1
        else:
            binfilt, _ = binarizeImg(filt, biThresh=th)
        extents.append(np.sum(binfilt))
    j = np.argmin(extents)
    
    filt = gf(input=chunk, sigma=(sigYs[j],sigXs[j]))
    binfilt, _ = binarizeImg(filt, biThresh=th)
    binfilt = 1 - binfilt
    
    # find connect components
    labels, nrObj = ndimage.label(binfilt)
    osli = ndimage.find_objects(labels)
    
    # find the word boxes
    rec = []
    bounds = []
    sh = np.max(labels.shape)
    for sl in osli:
        sl0 = sl[0].indices(sh)
        sl1 = sl[1].indices(sh)
        
        xLeng = sl1[1]-sl1[0]
        yLeng = sl0[1]-sl0[0]
        if xLeng*yLeng > 100:
            bounds.append([sl1[0], sl1[1]])
            rec.append([[sl1[0], sl0[0]], xLeng, yLeng])
    # combine those that are surrounded by others
    bounds = sorted(bounds)
    newbounds = []
    skipnext = False
    if len(bounds) <= 0:
        return [0, chunk.shape[1]]
    bPrev = bounds[0]
    for i in range(1, len(bounds)):
        bCur = bounds[i]
        if bPrev[1] > bCur[0]:
            bPrev = [bPrev[0], max(bCur[1], bPrev[1])]
        else:
            newbounds.append(bPrev)
            bPrev = [x for x in bCur]
    newbounds.append(bPrev)
    try:
        wbLine = [newbounds[0][0]]
    except:
        wbLine = [0]
    for i in range(1, len(newbounds)):
        b1 = newbounds[i-1]
        b2 = newbounds[i]
        wbLine.append(np.mean([b1[1], b2[0]])-fix)
    try:
        wbLine.append(b2[1])
    except:
        wbLine.append(chunk.shape[1])
#         pass
    
    # plot connected components
    if plotIt:
        fit,ax = plt.subplots(1)
        ax.imshow(labels, cmap='nipy_spectral')
        for i in range(len(rec)):
            rect = mpl.patches.Rectangle(rec[i][0], rec[i][1], rec[i][2], linewidth=1, edgecolor="r", facecolor="none")
            ax.add_patch(rect)
        plt.show()
    
    return np.array(wbLine).astype("int")