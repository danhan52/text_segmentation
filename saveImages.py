import csv
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle as Rec
import numpy as np
import random

# save all segments to a folder
def saveSegments(img, fname, lb, wb, cb = [], folder = "./",
                 ftype = ".png"):
    prefix = folder + fname
    with open(prefix+"_manifest.csv", "w") as f:
        writeit = csv.writer(f)
        writeit.writerow(["origImg", "imgLoc"])
        for i in range(len(lb)-1):
            if lb[i+1] - lb[i] < 5:
                continue
            for j in range(len(wb[i])-1):
                if wb[i][j+1] - wb[i][j] < 5:
                    continue
                # write manifest entry
                colrow = str(int(lb[i])) + "_" + str(int(wb[i][j]))
                nm = prefix + "_" + colrow + ftype
                writeit.writerow([fname, fname+"_" + colrow + ftype])
                
                # save chunk
                fInd = max(i-1, 0)
                sInd = min(i+2, len(lb))
                chunk = img[lb[fInd]:lb[sInd],]
                fit, ax = plt.subplots(1)
                ax.imshow(chunk)
                # draw segmentation lines
                if len(cb) > 0:
                    for k in range(len(cb[i][j])):
                        llx = np.add(wb[i][j], cb[i][j][k])
                        lly = lb[i]-lb[i-1]
                        rect = Rec([llx, lly], 0, lb[i+1]-lb[i], linewidth=1,
                                edgecolor="b", facecolor="none")
                        ax.add_patch(rect)
                # make bounding box
                llx = wb[i][j]
                lly = lb[i]-lb[i-1]
                wid = wb[i][j+1]-wb[i][j]
                hei = lb[i+1]-lb[i]
                rect = Rec([llx, lly], wid, hei, linewidth=3,
                           edgecolor="r", facecolor="none")
                ax.add_patch(rect)

                plt.gca().set_axis_off()
                plt.subplots_adjust(top=1,bottom=0,right=1,left=0,
                                    hspace=0,wspace=0)
                plt.margins(0,0)
                plt.gca().xaxis.set_major_locator(mpl.ticker.NullLocator())
                plt.gca().yaxis.set_major_locator(mpl.ticker.NullLocator())
                plt.savefig(nm, bbox_inches="tight",
                           pad_inches=0)
                plt.close()
    return True

# save just sections of the lines
def saveLines(img, fname, lb, folder = "./", ftype = ".png"):
    prefix = folder + fname
    with open(prefix+"_manifest.csv", "w") as f:
        writeit = csv.writer(f)
        writeit.writerow(["origImg", "imgLoc"])
        for i in range(len(lb)-1):
            if i > 9: break
            if lb[i+1] - lb[i] < 5:
                continue
            # write manifest entry
            colrow = str(int(lb[i]))
            nm = prefix + "_" + colrow + ftype
            writeit.writerow([fname, fname+"_" + colrow + ftype])

            # save chunk
            fInd = max(i-1, 0)
            sInd = min(i+2, len(lb)-1)
            chunk = img[lb[fInd]:lb[sInd],]
            fit, ax = plt.subplots(1)
            ax.imshow(chunk)

            plt.gca().set_axis_off()
            plt.subplots_adjust(top=1,bottom=0,right=1,left=0,
                                hspace=0,wspace=0)
            plt.margins(0,0)
            plt.gca().xaxis.set_major_locator(mpl.ticker.NullLocator())
            plt.gca().yaxis.set_major_locator(mpl.ticker.NullLocator())
            plt.savefig(nm, bbox_inches="tight",
                       pad_inches=0)
            plt.close()
    return True


# save just sections of the lines
def saveLinesdc(img, lb, rw, folder, manifest1, manifest2, prefix,
              ftype = ".jpg", lines = 3):
    with open(manifest1, "a") as f1, open(manifest2, "a") as f2:
        writeit = csv.writer(f1)
        write2it = csv.writer(f2)
        # randomly pick 3 rows to use
        random.seed(50)
        lbi = list(range(len(lb)-1))
        random.shuffle(lbi)
        count = 0
        ind = 0
        while count < lines:
            i = lbi[ind]
            if i < 2 or i > len(lb) - 3 or lb[i+1]-lb[i] < 5:
                ind += 1
                continue
            
            # get chunk
            fInd = max(i-2, 0)
            sInd = min(i+3, len(lb)-1)
            if lb[sInd] - lb[fInd] < 50:
                ind += 1
                continue
            chunk = img[lb[fInd]:lb[sInd],]
            
            # save location
            colrow = str(int(lb[i]))
            nm1 = prefix + "_" + colrow + ftype
            nm2 = folder + prefix + "_" + colrow + ftype
            # write manifest entry
            rwcp = [x for x in list(rw)]
            rwcp.append(colrow)
            rwcp.append(nm1)
            writeit.writerow(rwcp)
            rwcp2 = [rw["subject_id"], rw["hdl_id"], rw["meta_json"]["origin"],
                    rw["meta_json"].get("#telegrams", "na"), colrow, nm1]
            write2it.writerow(rwcp2)
            
            # save chunk
            fit, ax = plt.subplots(1)
            ax.imshow(chunk)

            plt.gca().set_axis_off()
            plt.subplots_adjust(top=1,bottom=0,right=1,left=0,
                                hspace=0,wspace=0)
            plt.margins(0,0)
            plt.gca().xaxis.set_major_locator(mpl.ticker.NullLocator())
            plt.gca().yaxis.set_major_locator(mpl.ticker.NullLocator())
            plt.savefig(nm2, bbox_inches="tight", pad_inches=0)
            plt.close()
            
            count += 1
            ind += 1
    return True


# save just sections of the lines
def saveLinesbp(img, lb, rw, folder, manifest1, manifest2, prefix,
              ftype = ".jpg", lines = 3):
    with open(manifest1, "a") as f1, open(manifest2, "a") as f2:
        writeit = csv.writer(f1)
        write2it = csv.writer(f2)
        # randomly pick 3 rows to use
        random.seed(50)
        lbi = list(range(len(lb)-1))
        random.shuffle(lbi)
        count = 0
        ind = 0
        while count < lines:
            i = lbi[ind]
            if i < 2 or i > len(lb) - 3 or lb[i+1]-lb[i] < 5:
                ind += 1
                continue
            
            # get chunk
            fInd = max(i-2, 0)
            sInd = min(i+3, len(lb)-1)
            if lb[sInd] - lb[fInd] < 50:
                ind += 1
                continue
            
            # save location
            colrow = str(int(lb[i]))
            nm1 = prefix + "_" + colrow + ftype
            nm2 = folder + prefix + "_" + colrow + ftype
            # write manifest entry
            rwcp = [x for x in list(rw)]
            rwcp.append(colrow)
            rwcp.append(nm1)
            writeit.writerow(rwcp)
            rwcp2 = [rw["subject_id"], rw["meta_json"].get("creator", "na"),
                    colrow, nm1]
            write2it.writerow(rwcp2)
            
            # save chunk
            chunk = img[lb[fInd]:lb[sInd],]
            fit, ax = plt.subplots(1)
            ax.imshow(chunk)

            plt.gca().set_axis_off()
            plt.subplots_adjust(top=1,bottom=0,right=1,left=0,
                                hspace=0,wspace=0)
            plt.margins(0,0)
            plt.gca().xaxis.set_major_locator(mpl.ticker.NullLocator())
            plt.gca().yaxis.set_major_locator(mpl.ticker.NullLocator())
            plt.savefig(nm2, bbox_inches="tight", pad_inches=0)
            plt.close()
            
            count += 1
            ind += 1
    return True