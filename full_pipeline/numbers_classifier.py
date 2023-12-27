from libs import cv2 , io , os
from sklearn.neighbors import KNeighborsClassifier
from skimage.feature import hog
from sklearn import metrics
import matplotlib.pyplot as plt
import cv2
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from preprocessing import gray_image , HistogramEqualization
from scipy.io import loadmat
from skimage import filters

import pickle






class H3T_Numbers_Classifier():
    digits = []
    training_dataset = []
    training_dataset_labels = []

    #Classifiers
    classifier = None

    trained_model_file_path = "second_trained_model.pk1"
    
    def __init__(self):
        self.digits = [ '0' , '1' , '2' , '3' , '4' , '5' , '6' , '7', '8' , '9']
    
    def prepare_training_data(self,training_directory):
        digit_feature_vector = {digit : [] for digit in self.digits}
        for digit in self.digits:
            digit_folder = f'{training_directory}/{digit}/'
            for digit_img in os.listdir(digit_folder):
                image = io.imread(os.path.join(digit_folder, digit_img))
                resized_img = cv2.resize(image, (16, 32))
                threshold = filters.threshold_otsu(resized_img)
                print(threshold)
                thresholded_image = np.zeros(resized_img.shape)
                thresholded_image[resized_img  > threshold] = 1
                
                
                
                feature_vector = hog(resized_img , pixels_per_cell=(2, 4), cells_per_block=(2, 4))
                digit_feature_vector[digit].append(feature_vector)
                self.training_dataset_labels.append(digit)
            print(f'digit {digit} done')
        self.training_dataset = [feature for digit_list in digit_feature_vector.values() for feature in digit_list]
        print(len(self.training_dataset) , len(self.training_dataset_labels))



    # def prepare_test_data(self,test_directory):
    #     for digit in self.digits:
    #         digit_folder = f'{test_directory}/digit_{digit}/'
    #         for digit_img in os.listdir(digit_folder):
                
    #             image = io.imread(os.path.join(digit_folder, digit_img))
    #             resized_img = cv2.resize(image, (128, 128))
    #             gray = gray_image(resized_img)
    #             feature_vector , _ = hog(gray,pixels_per_cell=(4 , 4) , transform_sqrt=True)
    #             self.test_features.append(feature_vector)
    #             self.test_labels.append(digit)
    
    def load_dataset(self):
        mnist = loadmat("./dataset/new_numbers/mnist-original.mat")
        mnist_data = mnist["data"].T
        mnist_label = mnist["label"][0]
        self.training_dataset_labels = []
        self.training_dataset = []

        for i in range(len(mnist_data)):
            # resized_img = cv2.resize(image, (32, 32))
            image = mnist_data[i].reshape(28, 28)
            feature_vector = hog(image , pixels_per_cell=(4 , 4), cells_per_block=(4, 4))
            self.training_dataset_labels.append(mnist_label[i])
            self.training_dataset.append(feature_vector)


    def train(self , mode : str):
        if (mode == "knn"):
            self.classifier = KNeighborsClassifier(n_neighbors = 5000)
        elif (mode == "svm"):
            self.classifier = SVC(kernel = 'rbf')
        elif (mode == "rf"):
            self.classifier = RandomForestClassifier(n_estimators = 100 , criterion = 'entropy' , random_state = 0)
            
        self.classifier.fit(self.training_dataset , self.training_dataset_labels)
    
    # def test(self):
    #     self.classifier.predict(self.test_features)
    #     accuracy = self.classifier.score(self.test_features , self.test_labels)
    #     print(accuracy)

    def save_trained_model(self):
        #delete file contents in trained_model.pk1
        open(self.trained_model_file_path , 'w').close()
        
        # save the model to disk
        with open(self.trained_model_file_path , 'wb') as file:
            pickle.dump(self.classifier , file)
    
    def load_trained_model(self):
        # load the model from disk
        with open(self.trained_model_file_path , 'rb') as file:
            self.classifier = pickle.load(file)


    def predict(self, img_to_predict):
        feature_vector= hog(img_to_predict, pixels_per_cell=(2, 4), cells_per_block=(2 , 4))
        return self.classifier.predict([feature_vector])
