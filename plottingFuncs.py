import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle as Rec

# plot "histogram"
def densityHist(proj, pers = []):
    plt.plot(proj)
    ny = proj.shape[0]
    for pe in pers:
        p = np.percentile(proj, pe)
        plt.plot([0,ny], [p, p])
        plt.text(x=ny, y=p, s=str(pe))
    plt.show()

# plot boxes around words (or just linebreaks)
def plotBoxes(img, lb, wb = [], cb = [], cmap = None):
    if len(lb) == 0:
        lb = [0, img.shape[0]]
    plt.imshow(img, cmap=cmap)
    plt.plot([0,img.shape[1]], [lb, lb], 'b')
    if len(wb) > 0:
        for i in range(len(lb)-1):
            plt.plot([wb[i], wb[i]], [lb[i], lb[i+1]], 'b')
            if len(cb) > 0:
                for j in range(len(wb[i])-1):
                    plt.plot([np.add(wb[i][j], cb[i][j]), np.add(wb[i][j],cb[i][j])],
                             [lb[i], lb[i+1]], 'r')
    plt.show()