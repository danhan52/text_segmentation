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
            sInd = min(i+2, len(lb))
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