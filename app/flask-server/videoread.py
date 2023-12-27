from libs import cv2 , os ,np , threading


####################

import preprocessing as pp
import detection as detect
import roi as roi
from skimage import filters , measure


from numbers_classifier import H3T_Numbers_Classifier
import ctypes # An included library with Python install.



def Mbox(title, text, style):
  return ctypes.windll.user32.MessageBoxW(0, text, title, style)


def extract_frames(video_path, output_folder, fps=30):
    """
    Extract frames from a video at a given frame rate.

    Parameters:
    - video_path (str): Path to the input video.
    - output_folder (str): Path to the folder where frames will be saved.
    - fps (int): Frames per second to extract.

    Returns:
    - None
    """

    # filename 
    filename = os.path.splitext(os.path.basename(video_path))[0]
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Couldn't open the video file.")
        return

    frame_count = 0
    frames = []
    while True:
        ret, frame = cap.read()

        # Break the loop if no more frames available
        if not ret:
            break

        # Check if the current frame count is divisible by the desired FPS
        if frame_count % fps == 0:
            frame_path = f"{output_folder}/{filename} {frame_count}.jpg"
            cv2.imwrite(frame_path, frame)
            print(f"Frame {frame_count} saved to {frame_path}")
            frames.append(frame)

        frame_count += 1

    cap.release()
    
    return frames


def clear_folder(folder_path):
    """
    Clear all files from a folder.

    Parameters:
    - folder_path (str): Path to the folder.

    Returns:
    - None
    """
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")    


def process_video(video_path, numbers_classifier  ,fps=30):
    sign_imgs_corr = detect.get_corrleation_matrices("../../dataset/corr_signs")

    # filename 
    #filename = os.path.splitext(os.path.basename(video_path))[0]
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    cv2.namedWindow("videsso", cv2.WINDOW_AUTOSIZE)
    
    if not cap.isOpened():
        print("Error: Couldn't open the video file.")
        return
    
    frame_count = 0
    threads = []
    while True:
        ret, frame = cap.read()

        # Break the loop if no more frames available
        if not ret:
            break
        
        cv2.imshow("vidsseo", frame)
        cv2.waitKey(20) & 0xFF == ord('0')
        if (frame_count % fps == 0):
           threads.append(threading.Thread(target=process_frame , args=(frame , numbers_classifier , sign_imgs_corr)).start())
        frame_count+=1
    for thread in threads:
        if (thread is not None):
            thread.join()
    

    cap.release()





def segement_numbers(image , numbers_classifier):
    V = cv2.cvtColor(image , cv2.COLOR_BGR2HSV)[: ,: , 2]
    T = filters.threshold_local(V, 27, offset=5, method="gaussian")
    thresh = (V > T).astype("uint8") * 255
    thresh = cv2.bitwise_not(thresh)
    inverted_thresh = cv2.bitwise_not(thresh)
    #pp.show_images([image , thresh])
    # perform a connected components analysis and initialize the mask to store the locations
    # of the character candidates
    charCandidates = []
    labels = measure.label(thresh, background=0)
    threads = []
    for label in np.unique(labels):
        thread = threading.Thread(target=detect.process_label, args=(labels , label, thresh , charCandidates))
        thread.start()
        threads.append(thread)
     
    # Wait for all threads to finish
    for thread in threads:
        thread.join()
            
    imagess = []

    charCandidateslen = len(charCandidates)
    if (charCandidateslen < 2 or charCandidateslen > 3):
        #print("wrong sign detected with length = " , len(charCandidates))
        return None
    
    for i in range(charCandidateslen):
        new_image = inverted_thresh[charCandidates[i][1]:charCandidates[i][1]+charCandidates[i][3] , charCandidates[i][0]:charCandidates[i][0]+charCandidates[i][2]]
        new_image = cv2.resize(new_image, (16, 32))
        #pp.show_images([new_image], [f"new_image {i}"])
        prediction = numbers_classifier.predict(new_image)
        imagess.append((charCandidates[i][0] , prediction[0].astype(int)))
    
    #sort by the x coordinate
    imagess.sort(key=lambda x: -x[0])
    
    result = np.sum([imagess[i][1]*(10**i) for i in range(len(imagess))])
        
    return result



    
def process_frame(frame , numbers_classifier , sign_imgs_corr):
    resized_img = cv2.resize(frame, (1280, 720))

    # pp.show_images([resized_img], ["resized_img Image"])

    #cropped_img = cv2.hconcat([resized_img[:, :(resized_img.shape[1] // 3)]  , resized_img[:, 2 * (resized_img.shape[1] // 3):]])

    # Convert the image to grayscale
    gray_image = pp.gray_image(resized_img)
    # pp.show_images([gray_image], ["Gray Image"])

    equalized_image = pp.HistogramEqualization(gray_image)

    # Apply edge detection
    edge_image = pp.LoGEdgeDetection(equalized_image)

    # Extract ROIs
    rois = roi.extract_roi(edge_image , resized_img)

    #pp.show_images(rois)

    ## detect sign
    if (len(rois)  == 0):
        #print("no rois")
        return
    else:
        detected_image_index = detect.detect_sign(rois, sign_imgs_corr)
        #print(detected_image_index) 
        if detected_image_index != -1:





            # new_image = pp.gray_image(rois[detected_image_index])

            # # #perform opening
            # kernel = np.ones((2,2), np.uint8)
            # new_image = cv2.erode(new_image, kernel, iterations=2)
            # new_image = cv2.dilate(new_image, kernel, iterations=1)
            
            # cropped_img = new_image[ 30:100 , 25:61 ]
            # resized_img = cv2.resize(cropped_img, (16, 32))

            # threshold = filters.threshold_otsu(resized_img)
            # thresholded_image = np.zeros(resized_img.shape)
            # thresholded_image[resized_img  > threshold] = 1
            # blurred_threshold_image = filters.gaussian(thresholded_image , sigma=0.7)

            # # show everything
            # pp.show_images([new_image , thresholded_image , blurred_threshold_image])

        

            result = segement_numbers(rois[detected_image_index] , numbers_classifier)
            if (result != None and result != 0):
                print(f'result = {result}')
                #show a warning message
                Mbox('Hady 3shan T3dy', f'Speed Limit = {result}', 1)
                

if __name__ == "__main__":
    videos_folder = '../../dataset/videos'
    video_frames_folder = '../../dataset/video_frames'

    numbers_classifier = H3T_Numbers_Classifier()
    numbers_classifier.load_trained_model()

    for video_path in os.listdir(videos_folder):
        process_video(os.path.join(videos_folder , video_path) , numbers_classifier=numbers_classifier , fps = 20)
        cv2.waitKey(0)
