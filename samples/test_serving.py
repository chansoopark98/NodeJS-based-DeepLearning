import json
import requests
from PIL import Image
import numpy as np
import tensorflow as tf 
import cv2
# pixels = np.zeros((1, 224, 224, 3))


img = cv2.imread('./demo_files/demo_imgs/20220607_153233.jpg')
img = cv2.resize(img, (180, 320))
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img = np.expand_dims(img, axis=0)


address = 'http://localhost:8501/v1/models/test_model:predict'
data = json.dumps({'instances':img[0:3].tolist()})

result = requests.post(address, data=data)

predictions = json.loads(str(result.content, 'utf-8'))['predictions']

for prediction in predictions:
    prediction = np.array(prediction)
    reshape_img = np.reshape(prediction, (320, 180, 2))
    output = np.argmax(reshape_img, axis=-1)
    output = output * 127
    
    cv2.imshow('test', output.astype(np.uint8))
    cv2.waitKey(0)