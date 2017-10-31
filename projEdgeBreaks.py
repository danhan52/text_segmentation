from scipy.signal import argrelextrema
from skimage.feature import canny
from operator import itemgetter
from itertools import groupby
import numpy as np


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

# get breaks based on projection
def projBreaks(img, direction, thresh = 0):
    proj = project(img, direction)
    breaks = argrelextrema(proj, np.greater_equal)[0]
    breaks = breaks[breaks > thresh-1]
    # append 0 and image size to ends of vector
    if not breaks[0] == 0:
        breaks = np.insert(breaks, 0, 0)
    if not breaks[-1] == proj.shape[0]:
        breaks = np.append(breaks, proj.shape[0]) 
    return breaks.astype("int")

# get the breaks based on canny edge detection
def edgeBreaks(img, direction, thresh = 0, cpar = [5, 1, 25]):
    edges = canny(img, cpar[0], cpar[1], cpar[2])
    eproj = project(edges, direction)
    br = np.sort(np.where(eproj <= thresh)[0])
    # get middle (mean) of continuous sequences
    breaks = []
    for k, g in groupby(enumerate(br), lambda ix:ix[0]-ix[1]):
        group = list(map(itemgetter(1), g))
        breaks.append(np.mean(group))
    # append 0 and image size to ends of vector
    if not breaks[0] == 0:
        breaks = np.insert(breaks, 0, 0)
    if not breaks[-1] == eproj.shape[0]:
        breaks = np.append(breaks, eproj.shape[0]) 
    return breaks.astype("int")

