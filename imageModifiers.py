import numpy as np
from scipy import ndimage
from scipy import misc
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from skimage import filters

from PIL import Image
import requests
from io import BytesIO

# read in an image
def readImg(filename, plotIt = False):
    # read in image file
    if "https://" in filename:
        response = requests.get(filename)
        let = Image.open(BytesIO(response.content))
        grey = np.array(let.convert("LA"))[:,:,0]
        let = np.array(let)
    else:
        let = misc.imread(filename)
        grey = misc.imread(filename, flatten=True)

    if plotIt:        
        plt.imshow(let)
        plt.show()
        plt.imshow(grey, cmap = "gray")
        plt.show()
    return let, grey

# save an image locally from online source
def readAndSave(filename, toFolder, newFn, imType = ".jpg"):
    # read in image file
    if "https://" in filename:
        filename = cStringIO.StringIO(urllib.urlopen(filename).read())
    let = Image.open(filename)
    to = toFolder + str(newFn) + imType
    let.save(to)

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
def binarizeImg(img, biThresh, plotIt = False):
    imgCp = img.copy()
    if biThresh == "otsu":
        biThresh = filters.threshold_otsu(imgCp)
    inds = imgCp > biThresh
    imgCp[inds] = 1
    imgCp[np.logical_not(inds)] = 0
    if plotIt:
        plt.imshow(imgCp, cmap = "gray")
        plt.show()
    return imgCp

# smooth an image
def smoothImg(img, smoothSigma, plotIt = False):
    imgCp = ndimage.filters.gaussian_filter(input=img, sigma=smoothSigma)
    if plotIt:
        plt.imshow(imgCp, cmap = "gray")
        plt.show()
    return imgCp


# functions for removing/whitening the edges of the image
# remove all rows that are entirely black
def removeEdges(imgCol, imgGr, rmThresh = 0):
    imgGrCp = imgGr.copy()
    imgColCp = imgCol.copy()
    
    imgY = project(imgGrCp, "y")
    imgGrCp = imgGrCp[imgY > rmThresh]
    imgColCp = imgColCp[imgY > rmThresh]
    
    imgX = project(imgGrCp, "x")
    imgGrCp = imgGrCp[:,imgX > rmThresh]
    imgColCp = imgColCp[:,imgX > rmThresh]
    return imgColCp, imgGrCp

# whiten based on projection
def whitenEdgesProject(grey):
    grey2 = smoothImg(grey, smoothSigma=1.0)
    brX = argrelextrema(project(grey2, "x"), np.greater_equal)[0]
    brX = [brX[0], brX[-1]]
    brY = argrelextrema(project(grey2, "y"), np.greater_equal)[0]
    brY = [brY[0], brY[-1]]
    greyCp = grey.copy()
    greyCp[:,:brX[0]] = 255
    greyCp[:,brX[1]:] = 255
    greyCp[:brY[0]] = 255
    greyCp[brY[1]:] = 255
    return greyCp

# use an edge filter
def whitenEdgesFilter(grey):
    grey2 = smoothImg(grey, smoothSigma=3.0)
    grey2 = 1 - binarizeImg(grey2, "otsu")
    labels, nrObj = ndimage.label(grey2)
    nr, nc = grey.shape
    wlabs = [labels[0, 0], labels[0, nc-1], labels[nr-1, 0],
             labels[nr-1, nc-1]]
    wlabs = np.unique(wlabs)
    greyCp = grey.copy()
    for la in wlabs:
        greyCp[labels == la] = 255
    return greyCp