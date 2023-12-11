#import numpy as np
from skimage import io , data , filters
from matplotlib import pyplot as plt
import cv2
import numpy as np


def read_images(filepath):

    # # read images
    for i in range(16,17):

        img = io.imread(filepath + "/{}.png".format(i))
        # resize image
        img =cv2.resize(img, dsize=(70, 70), interpolation=cv2.INTER_CUBIC)
        # convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # gaussian filter
        img01 = filters.gaussian(gray, sigma=0.1)
        img02 = filters.gaussian(gray, sigma=0.2)
        img03 = filters.gaussian(gray, sigma=0.3)
        img05 = filters.gaussian(gray, sigma=0.5)
        img2 = filters.gaussian(gray, sigma=2)
        
        
        

        # show before and after gaussian filter

        images = [gray, img01, img02, img03, img05]
        titles = ['gray', 'sigma=0.1', 'sigma=0.2', 'sigma=0.3', 'sigma=0.5']
        # plt.figure()
        # plt.subplot(2, 3, 1)
        # plt.title('original')
        # plt.imshow(img, cmap='gray')
        
        # for i in range(len(images)):
        #     thresh = filters.threshold_otsu(images[i])
        #     plt.subplot(2, 3, i + 2)
        #     plt.title(titles[i])
        #     plt.imshow(images[i]>thresh , cmap='gray')
            
        # plt.show()

        # get bounding boxes for each image
        threshold = filters.threshold_otsu(gray)
        gray[gray < threshold] = 0
        gray[gray >= threshold] = 1

        
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[2:]
        

        cutted = []

# Iterate through the contours and draw bounding boxes
        plt.figure()
        plt.subplot(3, 3, 1)
        plt.imshow(gray, cmap='gray')
        
        for contour in contours:
            # Get the bounding rect
            x, y, w, h = cv2.boundingRect(contour)
            if (w < 30 or h < 30) or (w>65 or h>65):
                continue
            cutted.append(gray[y:y+h, x:x+(w//2)])
            cutted.append(gray[y:y+h, x+(w//2):x+w])
            print("found")
            # Draw the bounding rect

        for i in range(len(cutted)):
            plt.subplot(3, 3, i+2)
            plt.imshow(cutted[i], cmap='gray')
        plt.show()

        


    return 0

    
        


if __name__ == "__main__":
    read_images("dataset/beforeknn")