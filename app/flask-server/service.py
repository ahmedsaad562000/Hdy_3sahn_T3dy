import cv2
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt
from skimage.color import rgb2gray, rgba2rgb
from skimage.filters import gaussian
from skimage.util.shape import view_as_windows
import os
from skimage import io
import pandas as pd
import threading
import preprocessing as pp
from skimage import filters
from sklearn import metrics
from skimage.feature import hog
from sklearn.svm import SVC
import detection as detect
import roi as roi
from flask import jsonify

sign_imgs_corr = detect.get_corrleation_matrices("./dataset/corr_signs")



def process_image(photo,numbers_classifier):
    predictedSignValue = 0;
    try:
        photo = np.fromstring(photo.read(), np.uint8)
        photo = cv2.imdecode(photo, cv2.IMREAD_COLOR)
        cv2.imwrite('original.jpg', photo)

        resized_img = cv2.resize(photo, (1280, 720))        
        cropped_img = cv2.hconcat([resized_img[:, :(resized_img.shape[1] // 3)]  , resized_img[:, 2 * (resized_img.shape[1] // 3):]])
        gray_image = pp.gray_image(resized_img)
        equalized_image = pp.HistogramEqualization(gray_image)
        edge_image = pp.LoGEdgeDetection(equalized_image)
        rois = roi.extract_roi(edge_image , resized_img)

        # save all rois
        for i in range(len(rois)):
            cv2.imwrite(f'roi{i}.jpg', rois[i])

        if (len(rois)  == 0):
            print("no rois")
        else:
            print(f'number of rois is {len(rois)}')
            detected_image_index = detect.detect_sign(rois, sign_imgs_corr)
            print(detected_image_index) 
            if detected_image_index != -1:
                new_image = pp.gray_image(rois[detected_image_index])

                kernel = np.ones((2,2), np.uint8)
                new_image = cv2.erode(new_image, kernel, iterations=2)
                new_image = cv2.dilate(new_image, kernel, iterations=1)
                
                cropped_img = new_image[ 30:100 , 25:61 ]
                resized_img = cv2.resize(cropped_img, (16, 32))

                threshold = filters.threshold_otsu(resized_img)
                thresholded_image = np.zeros(resized_img.shape)
                thresholded_image[resized_img  > threshold] = 1
                blurred_threshold_image = filters.gaussian(thresholded_image , sigma=0.7)

                predictedSign = numbers_classifier.predict(blurred_threshold_image)[0]
                print(f'prediction is {predictedSign}')
                predictedSignValue = int(predictedSign) * 10
                
                print(f'predictedSignValue is {predictedSignValue}')

            else:
                print("no sign detected")

        return predictedSignValue
    except Exception as e:
        print(f"Error processing image: {e}")
        return None