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
    predictedSign = 0;
    try:
        img = cv2.imdecode(np.fromstring(photo.read(), np.uint8), cv2.IMREAD_COLOR)
        # resized_img = cv2.resize(img,  (1280, 720))
        # cropped_img = cv2.hconcat([resized_img[:, :(resized_img.shape[1] // 3)]  , resized_img[:, 2 * (resized_img.shape[1] // 3):]])
        gray_image_result = pp.gray_image(img)
        equalized_image = pp.HistogramEqualization(gray_image_result)
        edge_image = pp.LoGEdgeDetection(equalized_image)
        rois = roi.extract_roi(edge_image , img)

        if (len(rois)  == 0):
            print("no rois")
        else:
            detected_image_index = detect.detect_sign(rois, sign_imgs_corr)
            print(detected_image_index) 
            if detected_image_index != -1:
                
                # feature_vector , transformed_hog = hog(rois[detected_image_index] , visualize = True , channel_axis=2  , pixels_per_cell=(16, 16) , transform_sqrt=True)
                # pp.show_images([rois[detected_image_index], transformed_hog])

                # red_channel = colored_image[:, :, 0]
                # green_channel = colored_image[:, :, 1]
                # blue_channel = colored_image[:, :, 2]

                # new_image = red_channel.copy()

                # for i in range(new_image.shape[0]):
                #     for j in range(new_image.shape[1]):
                #         if (red_channel[i][j]  < 200 and green_channel[i][j] < 200 and blue_channel[i][j] < 200):
                #             new_image[i][j] = 255
                #         else:
                #             new_image[i][j] = 0

                new_image = pp.gray_image(rois[detected_image_index])

                

                
                new_image = new_image[ 30:100 , 25:61 ]

                #perform closing
                kernel = np.ones((2,2), np.uint8)
                new_image = cv2.dilate(new_image, kernel, iterations=3)
                new_image = cv2.erode(new_image, kernel, iterations=1)
                
                thrsholded_image = np.zeros_like(new_image)
                threshold = filters.threshold_otsu(new_image)
                thrsholded_image[new_image <= threshold] = 1
                thrsholded_image = cv2.resize(thrsholded_image , (12, 24)).astype(np.uint8)
                
                new_black_image = np.zeros((28, 28))
                new_black_image[2:2+thrsholded_image.shape[0] , 8:8+thrsholded_image.shape[1]] = thrsholded_image
                # new_black_image = filters.gaussian(new_black_image , sigma=1)

                # # apply dilation
                # kernel = np.ones((2, 2), np.uint8)
                # new_black_image = cv2.dilate(new_black_image, kernel, iterations=1)

                
                # pp.show_images([new_image , thrsholded_image , new_black_image])




                # gray_roi = pp.gray_image(rois[detected_image_index])
                
                # gray_roi = pp.HistogramEqualization(gray_roi)

                # new_image = gray_roi[ 20:100 , 15:110 ]

                # first_digit = new_image[: , 0:new_image.shape[0]//2]

                # pp.show_images([gray_roi , new_image , first_digit], ["sign_detected" , "new_image" , "first digit"]) 
                
                # print(gray_roi.shape)
                serializable_array = numbers_classifier.predict(new_black_image).tolist()
                print(f'prediction is {serializable_array[0]*10}')
                predictedSign = serializable_array[0]*10
            else:
                print("no sign detected")

        return predictedSign
    except Exception as e:
        print(f"Error processing image: {e}")
        return None