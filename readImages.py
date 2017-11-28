from skimage import io as skimio
from skimage import color as skimcolor
import matplotlib.pyplot as plt

# read in an image
def readImg(filename, plotIt = False):
    # read in image file
    let = skimio.imread(filename)
    grey = skimcolor.rgb2gray(let)

    if plotIt:        
        plt.imshow(let)
        plt.show()
        plt.imshow(grey, cmap = "gray")
        plt.show()
    return let, grey

# save an image locally from online source
def readAndSave(filename, toFolder, newFn, imType = ".jpg"):
    # read in image file
    let = skimio.imread(filename)
    to = toFolder + str(newFn) + imType
    skimio.imsave(to, let)
    return to
