
import tensorflow as tf


class TrtMOdel():
    def __init__(self):
        converted_model_path = '/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path_trt/1/'
        model = tf.saved_model.load(converted_model_path)