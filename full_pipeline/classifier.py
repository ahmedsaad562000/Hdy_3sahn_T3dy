from libs import cv2 , io , os
from sklearn.neighbors import KNeighborsClassifier
from skimage.feature import hog
from sklearn import metrics
import matplotlib.pyplot as plt
import cv2
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from preprocessing import gray_image , HistogramEqualization

import pickle






class H3T_Classifier():
    speeds = []
    
    training_dataset = []
    training_dataset_labels = []
    
    test_features = []
    test_labels = []

    #Classifiers
    classifier = None

    trained_model_file_path = "trained_model.pk1"
    
    def __init__(self):
        self.speeds = ['30' , '50' , '60' , '70' , '80' , '100' , '120']
    
    def prepare_training_data(self,training_directory):
        speed_feature_vector = {speed : [] for speed in self.speeds}
        for speed in self.speeds:
            speed_folder = f'{training_directory}/speed_{speed}/'
            for speed_img in os.listdir(speed_folder):
                image = io.imread(os.path.join(speed_folder, speed_img))
                resized_img = cv2.resize(image, (128, 128))
                # gray = gray_image(resized_img)
                feature_vector = hog(resized_img, channel_axis=2 , pixels_per_cell=(8 , 8), cells_per_block=(4, 4) , transform_sqrt=True)
                speed_feature_vector[speed].append(feature_vector)
                self.training_dataset_labels.append(speed)
        self.training_dataset = [feature for speed_list in speed_feature_vector.values() for feature in speed_list]
        print(len(self.training_dataset) , len(self.training_dataset_labels))



    def prepare_test_data(self,test_directory):
        for speed in self.speeds:
            speed_folder = f'{test_directory}/speed_{speed}/'
            for speed_img in os.listdir(speed_folder):
                
                image = io.imread(os.path.join(speed_folder, speed_img))
                resized_img = cv2.resize(image, (128, 128))
                gray = gray_image(resized_img)
                feature_vector , _ = hog(gray,pixels_per_cell=(4 , 4) , transform_sqrt=True)
                self.test_features.append(feature_vector)
                self.test_labels.append(speed)

    def train(self , mode : str):
        if (mode == "knn"):
            self.classifier = KNeighborsClassifier(n_neighbors = 20)
        elif (mode == "svm"):
            self.classifier = SVC(kernel = 'rbf')
        elif (mode == "rf"):
            self.classifier = RandomForestClassifier(n_estimators = 100 , criterion = 'entropy' , random_state = 0)
            
        self.classifier.fit(self.training_dataset , self.training_dataset_labels)
    
    def test(self):
        self.classifier.predict(self.test_features)
        accuracy = self.classifier.score(self.test_features , self.test_labels)
        print(accuracy)

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
        feature_vector= hog(img_to_predict, channel_axis=2 , pixels_per_cell=(8 , 8), cells_per_block=(4 , 4) , transform_sqrt=True)
        return self.classifier.predict([feature_vector])
