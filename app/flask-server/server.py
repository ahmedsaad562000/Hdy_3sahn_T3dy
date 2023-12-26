from flask import Flask, request, jsonify,send_file
import os
from service import process_image
from io import BytesIO
import base64
from PIL import Image
import numpy as np
import cv2
from numbers_classifier import H3T_Numbers_Classifier

app = Flask(__name__)

# run a function once the server is up
print("initializing")
numbers_classifier = H3T_Numbers_Classifier()
numbers_classifier.load_trained_model()
print("model loaded")


@app.route('/members')
def members():
    return {'members': ['John', 'Alex', 'Kate']}


@app.route('/upload', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo provided'}), 400

    photo = request.files['photo']

    lengthROIs = process_image(photo,numbers_classifier)

    # # Convert NumPy array to binary data
    # _, buffer = cv2.imencode('.jpg', processed_image)
    # binary_data = buffer.tobytes()

    # # Convert binary data to base64-encoded string
    # base64_encoded = base64.b64encode(binary_data).decode('utf-8')

    return jsonify({'result':lengthROIs})


if __name__ == '__main__':
    app.run(debug=True)
