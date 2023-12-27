from flask import Flask, request, jsonify,send_file
import os
from service import getSpeed
from io import BytesIO
import base64
from PIL import Image
import numpy as np
import cv2
from numbers_classifier import H3T_Numbers_Classifier

def init_number_classifier():
    print("initializing")
    numbers_classifier = H3T_Numbers_Classifier()
    numbers_classifier.load_trained_model()
    print("model loaded")
    return numbers_classifier

app = Flask(__name__)

classifier = init_number_classifier()

@app.route('/members')
def members():
    return {'members': ['John', 'Alex', 'Kate']}


@app.route('/upload', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo provided'}), 400
    
    photo = request.files['photo']
    speed = getSpeed(photo,classifier)

    return jsonify({'speed':speed})

if __name__ == '__main__':
    app.run(debug=True)

