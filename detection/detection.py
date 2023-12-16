
import numpy as np
import cv2
import pandas as pd

def detect_signs(rois : list , sign_imgs_corr : list):
    rois_corr = []
    for i in range(len(rois)):
        image = cv2.resize(rois[i], (64, 64)) #resize image
        
        df_r = pd.DataFrame(image[: , : , 0]) #red channel dataframe
        
        df_g = pd.DataFrame(image[: , : , 1]) #green channel dataframe
        
        df_b = pd.DataFrame(image[: , : , 2]) #blue channel dataframe
        
        corr= pd.concat([df_r, df_g, df_b], axis=1).corr() #correlation matrix
        
        rois_corr.append(corr)

    votes = [0 for i in range(len(rois))] #number of votes for each ROI

    for i in range(len(sign_imgs_corr)):
        scores_list = [ np.sum(np.sum(np.abs(rois_corr[j] - sign_imgs_corr[i])))/(64*64*3*3) for j in range(len(rois))]
        most_correlated_index = np.argmin(scores_list)
        print(scores_list[most_correlated_index])
        if (scores_list[most_correlated_index] < 0.4):
            votes[most_correlated_index] += 1

    print(votes)
    
    if (max(votes) >= len(sign_imgs_corr) // 2 ):
        return votes.index(max(votes))
