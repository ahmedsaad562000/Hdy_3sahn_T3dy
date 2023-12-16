from libs import np , cv2 , io , os , sys
from sklearn.neighbors import KNeighborsClassifier
from skimage.feature import hog
from sklearn import metrics
import matplotlib.pyplot as plt
import cv2
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier






class H3T_Classifier():
    speeds = []
    
    training_dataset = []
    training_dataset_labels = []
    
    test_features = []
    test_labels = []

    #Classifiers
    classifier = None
    
    def __init__(self):
        self.speeds = ['30' , '50' , '60' , '70' , '80' , '100' , '120']
    
    def prepare_training_data(self,training_directory):
        speed_feature_vector = {speed : [] for speed in self.speeds}
        for speed in self.speeds:
            speed_folder = f'{training_directory}/speed_{speed}/'
            for speed_img in os.listdir(speed_folder):
                image = io.imread(os.path.join(speed_folder, speed_img))
                resized_img = cv2.resize(image, (128, 128))
                feature_vector, _ = hog(resized_img, visualize=True, channel_axis=2)
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
                feature_vector, _ = hog(resized_img, visualize=True, channel_axis=2)
                self.test_features.append(feature_vector)
                self.test_labels.append(speed)

    def train(self , mode : str):
        if (mode == "knn"):
            self.classifier = KNeighborsClassifier(n_neighbors = 20)
        elif (mode == "svm"):
            self.classifier = SVC(kernel = "linear" , random_state = 0)
        elif (mode == "rf"):
            self.classifier = RandomForestClassifier(n_estimators = 100 , criterion = 'entropy' , random_state = 0)
            
        self.classifier.fit(self.training_dataset , self.training_dataset_labels)
    
    def test(self):
        self.classifier.predict(self.test_features)
        accuracy = self.classifier.score(self.test_features , self.test_labels)
        print(accuracy)

    def predict(self, img_to_predict):
        feature_vector , _ = hog(img_to_predict , visualize = True , channel_axis = 2)
        return self.classifier.predict([feature_vector])
