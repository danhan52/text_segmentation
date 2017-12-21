import numpy as np
import pandas as pd
import json

################################################################################

# read classifications from my slope workflow
# I'll change this later to download straight for online if file is too old
def readSlopeClassification(clFile):
    clExp = pd.read_csv(clFile)
     # get most recent workflow
    clExp = clExp.loc[clExp['workflow_version'] == 16.28]
    # convert subject data to json
    clExp['subj_json'] = [json.loads(q) for q in clExp['subject_data']]
    # get hdl_id from json
    clExp['hdl_id'] = [q.get(list(q.keys())[0]).get('hdl_id', '')
                       for q in clExp['subj_json']]
    clExp = clExp.loc[clExp['hdl_id'] != '']
    return clExp


# read in the subject file that contains information for all uploaded files
def readSubjFile(subjFile):
    # subject file
    subj = pd.read_csv(subjFile)
    # get only the workflow from the live project
    subj = subj.loc[subj['workflow_id'] == 1874]

    # get metadata in dictionary format
    subj['meta_json'] = [json.loads(q) for q in subj['metadata']]
    # get hdl_id from metadata
    subj['hdl_id'] = [q.get('hdl_id', 'mssF') for q in subj['meta_json']]
    # get image url
    subj['url'] = [json.loads(q).get('0') for q in subj['locations']]

    # remove images without ids
    subj = subj[subj['hdl_id'] != 'mssF']
    # remove codebook images (mssEC_36-67)
    filt = subj['hdl_id'].str.contains('mssEC_3[6-9]|[4-6][0-9]')
    subj = subj[~filt]
    # remove ledgers that seemed weird (only easy stuff for now)
    filt = subj['hdl_id'].str.contains('mssEC_3[0-3]|2[6-9]')
    subj = subj[~filt]
    # remove the first few pages because they tended to be blank
    filt = subj['hdl_id'].str.contains('mssEC_\d\d_00[1-6]')
    subj = subj[~filt]
    
    return subj

# read consensus files from local file
def readConsensusFile(consensusFile):
    cons = pd.read_csv(consensusFile, sep='@@', engine='python')
    cons = cons.drop_duplicates()
    return cons

# merge the subject file with the consensus file and remove things not in the
# slope classification export if it's provided
def mergeSubjAndCons(subj, cons, clExp=None):
    # combine the two and sift out unneeded columns
    allTelegramInfo = pd.merge(cons, subj, on="hdl_id", suffixes=["_cons", "_subj"])
    idAndUrl = allTelegramInfo.loc[:,["hdl_id", "url_cons"]].drop_duplicates()
    telegrams = allTelegramInfo.loc[:,["hdl_id", "bestLineIndex", "consensus_text", 
                                           "y_loc", "len_wordlist"]]

    if clExp is not None: # use only the data that has slant information
        idAndUrl = idAndUrl.loc[idAndUrl['hdl_id'].isin(clExp['hdl_id'])]
        telegrams = telegrams.loc[telegrams['hdl_id'].isin(clExp['hdl_id'])]
    
    return idAndUrl, telegrams

# get the slope information from the classification export
def meanSlope(clExp, hdl_id):
    curClExp = clExp.loc[clExp['hdl_id'] == hdl_id, 'annotations']
    curClExp = [json.loads(i) for i in curClExp]
    slopes = []
    for item in curClExp:
        if item[0]['value'] == 'No':
            continue
        for val in item[1]['value']:
            x1 = val['x1']
            x2 = val['x2']
            y1 = val['y1']
            y2 = val['y2']
            if x1 > x2:
                x1, x2 = x2, x1
                y1, y2 = y2, y1
            slope = 1.0 * (y2 - y1)/(x2 - x1)
            slopes.append(slope)

    # only keep slopes that aren't too different
    mn = np.mean(slopes)
    sd = np.std(slopes)
    slopes = [x for x in slopes if x > mn-sd and x < mn+sd]
    return np.mean(slopes)
