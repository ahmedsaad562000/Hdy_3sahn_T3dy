from libs import np , cv2 , threading
import preprocessing as pp
from skimage import filters , measure
import detection as detect
import roi as roi

sign_imgs_corr = detect.get_corrleation_matrices("./dataset/corr_signs")

def getSpeed(photo,numbers_classifier):
    predicted_sign_value = 0;
    try:
        photo = convert_image_to_nparray(photo)
        resized_img = resize_image(photo)        
        gray_image = pp.gray_image(resized_img)
        equalized_image = pp.HistogramEqualization(gray_image)
        edge_image = pp.LoGEdgeDetection(equalized_image)
        ROIs = roi.extract_roi(edge_image , resized_img)

        if (len(ROIs)  == 0):
            print("no rois")
        else:
            detected_image_index = detect.detect_sign(ROIs, sign_imgs_corr)
            if detected_image_index != -1:
                result = segement_numbers(ROIs[detected_image_index],numbers_classifier)
                if (result != None):
                    predicted_sign_value = get_fixed_speed(result)
                else: 
                    print("no sign detected")
            else:
                print("no sign detected")
        return predicted_sign_value
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def crop_image(resized_img):
    return cv2.hconcat([resized_img[:, :(resized_img.shape[1] // 3)]  , resized_img[:, 2 * (resized_img.shape[1] // 3):]])

def resize_image(photo):
    resized_img = cv2.resize(photo, (1280, 720))
    return resized_img

def convert_image_to_nparray(photo):
    photo = np.fromstring(photo.read(), np.uint8)
    photo = cv2.imdecode(photo, cv2.IMREAD_COLOR)
    return photo

def get_fixed_speed(speed):
    hundreds = speed // 100
    tens = (speed // 10) % 10
    ones = speed % 10

    if ones != 0:
        ones = 0

    if hundreds > 1:
        hundreds = 1

    modified_speed = hundreds * 100 + tens * 10 + ones
    return modified_speed

def segement_numbers(image , numbers_classifier):
    V = cv2.cvtColor(image , cv2.COLOR_BGR2HSV)[: ,: , 2]
    T = filters.threshold_local(V, 27, offset=5, method="gaussian")
    thresh = (V > T).astype("uint8") * 255
    thresh = cv2.bitwise_not(thresh)
    inverted_thresh = cv2.bitwise_not(thresh)
    # pp.show_images([image , thresh])
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
        print("wrong sign detected with length = " , len(charCandidates))
        return None
    
    for i in range(charCandidateslen):
        new_image = inverted_thresh[charCandidates[i][1]:charCandidates[i][1]+charCandidates[i][3] , charCandidates[i][0]:charCandidates[i][0]+charCandidates[i][2]]
        new_image = cv2.resize(new_image, (16, 32))
        # pp.show_images([new_image], [f"new_image {i}"])
        prediction = numbers_classifier.predict(new_image)
        imagess.append((charCandidates[i][0] , prediction[0].astype(int)))
    
    #sort by the x coordinate
    imagess.sort(key=lambda x: -x[0])
    
    result = np.sum([imagess[i][1]*(10**i) for i in range(len(imagess))])
        
    return result

