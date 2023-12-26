
from libs import np , pd , cv2 , os , io , threading

def get_corrleation_matrices(folder_path):


    

    # Get a list of all files in the folder
    file_names = os.listdir(folder_path)

    # Filter the file names to include only image files
    image_files = [file for file in file_names if file.endswith((".jpg", ".jpeg", ".png"))]

    sign_imgs_corr = []
    for file in image_files:
        
        image_path = os.path.join(folder_path, file)
        image = io.imread(image_path)
        image = cv2.resize(image, (128, 128))
        df_r = pd.DataFrame(image[: , : , 0])
        df_g = pd.DataFrame(image[: , : , 1])
        df_b = pd.DataFrame(image[: , : , 2])

        corr= pd.concat([df_r, df_g, df_b], axis=1).corr()
        sign_imgs_corr.append(corr)
    
    return sign_imgs_corr 



def detect_sign(rois : list , sign_imgs_corr : list):


    rois_corr = [0 for i in range(len(rois))]
    votes = [0 for i in range(len(rois))] #number of votes for each ROI

    def add_corr_matrix(index):

        df_r = pd.DataFrame(rois[index][: , : , 0]) #red channel dataframe
        
        df_g = pd.DataFrame(rois[index][: , : , 1]) #green channel dataframe
        
        df_b = pd.DataFrame(rois[index][: , : , 2]) #blue channel dataframe
        
        corr= pd.concat([df_r, df_g, df_b], axis=1).corr() #correlation matrix
        
        rois_corr[index] = corr

    def add_vote(index):
        scores_list = [ np.sum(np.sum(np.abs(rois_corr[j] - sign_imgs_corr[index])))/(128*128*3*3) for j in range(len(rois))]
        most_correlated_index = np.argmin(scores_list)
        print(scores_list[most_correlated_index])
        if (scores_list[most_correlated_index] < 0.45):
            votes[most_correlated_index] += 1
    
    
    threads = [0 for i in range(len(rois))]

    for i in range(len(rois)):
        t = threading.Thread(target=add_corr_matrix, args=(i,))
        t.start()
        threads[i] = t
    
    for t in threads:
        t.join()


    threads = [0 for i in range(len(sign_imgs_corr))]
    
    
    for i in range(len(sign_imgs_corr)):
        t = threading.Thread(target=add_vote, args=(i,))
        t.start()
        threads[i] = t
    
    for t in threads:
        t.join()

    print(votes)
    
    if (max(votes) >= len(sign_imgs_corr) // 2 ):
        return votes.index(max(votes))
    else:
        return -1

