import cv2
import numpy as np
import preprocessing as pp
from skimage import filters
import detection as detect
import roi as roi

sign_imgs_corr = detect.get_corrleation_matrices("./dataset/corr_signs")

def getSpeed(photo,numbers_classifier):
    predicted_sign_value = 0;
    try:
        photo = convert_image_to_nparray(photo)
        resized_img = resize_image(photo)        
        cropped_img = crop_image(resized_img)
        gray_image = pp.gray_image(resized_img)
        equalized_image = pp.HistogramEqualization(gray_image)
        edge_image = pp.LoGEdgeDetection(equalized_image)
        ROIs = roi.extract_roi(edge_image , resized_img)

        if (len(ROIs)  == 0):
            print("no rois")
        else:
            print(f'number of rois is {len(ROIs)}')
            detected_image_index = detect.detect_sign(ROIs, sign_imgs_corr)
            print(detected_image_index) 
            if detected_image_index != -1:
                new_image = pp.gray_image(ROIs[detected_image_index])

                kernel = np.ones((2,2), np.uint8)
                new_image = cv2.erode(new_image, kernel, iterations=2)
                new_image = cv2.dilate(new_image, kernel, iterations=1)
                
                cropped_img = new_image[ 30:100 , 25:61 ]
                resized_img = cv2.resize(cropped_img, (16, 32))

                threshold = filters.threshold_otsu(resized_img)
                thresholded_image = np.zeros(resized_img.shape)
                thresholded_image[resized_img  > threshold] = 1

                blurred_threshold_image = filters.gaussian(thresholded_image , sigma=0.7)

                predicted_sign = numbers_classifier.predict(blurred_threshold_image)[0]
                predicted_sign_value = int(predicted_sign) * 10
                print(f'predictedSignValue is {predicted_sign_value}')
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