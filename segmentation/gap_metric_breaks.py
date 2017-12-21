import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage

import skimage.filters as skimfilt
from skimage.morphology import convex_hull_object
from skimage.morphology import convex_hull_image
from skimage.measure import find_contours

from sklearn.mixture import GaussianMixture

from scipy.ndimage.measurements import center_of_mass
from shapely.geometry import LineString

from segmentation.imageModifiers import binarizeImg

def getGapDistances(chunk, edgeThresh=0.1, sizeThresh=10, plotIt=False):
    chunkBi, _ = binarizeImg(chunk, threshFn=skimfilt.threshold_otsu, 
                             greater=False, plotIt=plotIt)
    
    # get convex hulls of connected components
    chunk_hull = convex_hull_object(chunkBi, neighbors=4)
    nrow, ncol = chunk.shape
    
    # Label convex hulls
    chunk_hull_labels, nrObj = ndimage.label(chunk_hull)


    # Remove all objects touching the top and bottom that have a 
    # center of mass also close to the top or bottom.
    centers = center_of_mass(chunk_hull, chunk_hull_labels, range(1, nrObj+1))
    thresh_top = nrow*edgeThresh
    thresh_bot = nrow - nrow*edgeThresh

    # top edge
    for j in range(ncol):
        if chunk_hull_labels[0, j] != 0:
            lab = chunk_hull_labels[0, j]
            if centers[lab-1][0] < thresh_top:
                chunk_hull_labels[chunk_hull_labels == lab] = 0
                
    # bottom edge
    for j in range(ncol):
        if chunk_hull_labels[nrow-1, j] != 0:
            lab = chunk_hull_labels[nrow-1, j]
            if centers[lab-1][0] > thresh_bot:
                chunk_hull_labels[chunk_hull_labels == lab] = 0

    
    # Remove all objects that are just absolutely tiny
    labs = np.unique(chunk_hull_labels)
    for lab in labs:
        size = np.sum(chunk_hull_labels == lab)
        if size < sizeThresh:
            chunk_hull_labels[chunk_hull_labels == lab] = 0

    
    # Relabel convex hulls after previous removal
    chunk_hull = chunk_hull_labels > 0
    chunk_hull_labels, nrObj = ndimage.label(chunk_hull)

    
    # Sort labels by means x values
    osli = ndimage.find_objects(chunk_hull_labels)
    mean_x = [np.mean(x[1].indices(10**10)[:2]) for x in osli]

    order = np.argsort(mean_x)
    for j in range(len(order)):
        chunk_hull_labels[chunk_hull_labels == order[j]+1] = -(j+1)
    chunk_hull_labels *= -1

    
    # Get centers of mass for convex hulls
    centers = center_of_mass(chunk_hull, chunk_hull_labels, range(1, nrObj+1))

    
    # Find contours of objects and use these with lines between
    # centers of mass to get distance between objects
    contours = find_contours(chunk_hull, 0.5)
    contours = [contours[o] for o in order]

    distances = []
    break_centers = []
    for j in range(len(contours)-1):
        obj1 = LineString(contours[j])
        obj2 = LineString(contours[j+1])
        center_dist = LineString([centers[j], centers[j+1]])

        edge1 = obj1.intersection(center_dist)
        edge2 = obj2.intersection(center_dist)
        distances.append(edge1.distance(edge2))
        
        try:
            break_centers.append(LineString([edge1, edge2]).centroid.coords[0][1])
        except:
            break_centers.append(0)
    distances = np.array(distances, ndmin=2).T

    
    if plotIt:
        plt.imshow(chunk_hull, cmap="gray")
        plt.show()
        plt.imshow(chunk_hull_labels, cmap="nipy_spectral")
        plt.plot([x[1] for x in centers], [y[0] for y in centers], "ro")
        plt.show()

    return distances, chunk_hull_labels, break_centers

def gapBreaks(chunk):
    g_dist, chhul, brc = getGapDistances(chunk)
    
    # create a gaussian mixture model to split data into
    # inter and intra-word splits
    gmm = GaussianMixture(n_components=2)
    gmm.fit(g_dist)

    # get groups
    cl = gmm.predict(g_dist).astype("bool")
    if np.mean(g_dist[cl,]) < np.mean(g_dist[np.logical_not(cl)]):
        cl = np.logical_not(cl)

    br = [brc[i] for i in range(len(cl)) if cl[i]]
    return br