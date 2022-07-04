import tensorflow as tf
import tensorflow.keras.models as models
from .model_zoo.UNet import unet
from .model_zoo.DeepLabV3plus import DeeplabV3_plus
from .model_zoo.modify_DeepLabV3plus import deepLabV3Plus
from .model_zoo.EfficientNetV2 import EfficientNetV2S
from .model_zoo.DDRNet_23_slim import ddrnet_23_slim
from .model_zoo.mobileNetV3 import MobileNetV3_Small
from tensorflow.keras.applications.imagenet_utils import preprocess_input
from tensorflow.python.saved_model import tag_constants
import numpy as np

def classifier(x, num_classes=19, upper=4, name=None):
    x = tf.keras.layers.Conv2D(num_classes, 1, strides=1,
                      kernel_initializer=tf.keras.initializers.VarianceScaling(scale=1.0, mode="fan_out", distribution="truncated_normal"))(x)
    x = tf.keras.layers.UpSampling2D(size=(upper, upper), interpolation='bilinear', name=name)(x)
    return x

def segmentation_model(image_size):
    # model_input, model_output = unet(input_shape=(image_size[0], image_size[1], 3), use_logits=False)
    # return tf.keras.Model(model_input, model_output)
    return ddrnet_23_slim(input_shape=(image_size[0], image_size[1], 3), num_classes=1)

    

def semantic_model(image_size, model='MobileNetV3S'):
    if model=='MobileNetV3S':
        base = MobileNetV3_Small(shape=(image_size[0], image_size[1], 3), n_class=1000, alpha=1, include_top=False).build()
        # 224 1
        # 112 2
        # 56 4 -> add
        # 28 8
        # 14 16 -> add_5
        # get output stride 
            # 1/4 : re_lu_1
            # 1/16
        c5 = base.get_layer('add_5').output  # 16x32 256 or get_layer('post_swish') => 확장된 채널 1280
        c2 = base.get_layer('add').output  # 128x256 48
    else:
        base = EfficientNetV2S(input_shape=(image_size[0], image_size[1], 3), pretrained="imagenet")
        c5 = base.get_layer('add_34').output
        c2 = base.get_layer('add_4').output 




    """
    for EfficientNetV2S (input resolution: 512x1024)
    32x64 = 'add_34'
    64x128 = 'add_7'
    128x256 = 'add_4'
    """
    features = [c2, c5]

    model_input = base.input
    model_output = deepLabV3Plus(features=features, activation='swish')

    semantic_output = classifier(model_output, num_classes=2, upper=4, name='output')

    model = models.Model(inputs=[model_input], outputs=[semantic_output])
    
    return model


class SemanticModel():
    def __init__(self):
        self.image_size = (224, 224)
        self.weights = './dl_model/test_weights.h5'
        self.export_path = './dl_model/saved_model/'
        # tf.config.set_soft_device_placement(True)
        self.load_model()
        self.warm_up()
    
    def load_model(self):

        converted_model_path = '/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path_trt/1/'
        # self.model = tf.saved_model.load(converted_model_path)
        print('load_model')
        try:
            self.model = tf.saved_model.load(converted_model_path, tags=[tag_constants.SERVING])
        except Exception as e:
            print('load_model error')
            # print('Log : {0}'.format(e))
        # signature_keys = list(self.model.signatures.keys())
        # print(signature_keys)

        print('infer')
        self.infer = self.model.signatures['serving_default']
        # print(self.infer.structured_outputs)

    def warm_up(self):
        dummy_data = tf.zeros((1, self.image_size[0], self.image_size[1],3))
        
        print(dummy_data.shape)
        with tf.device('/device:GPU:0'):
            _ = self.infer(dummy_data)
            print('gpu 0 warm up')
        with tf.device('/device:GPU:1'):
            _ = self.infer(dummy_data)
            print('gpu 1 warm up')
    

    
    def model_predict(self, image, gpu_name):
        # '/device:GPU:0'
        
            # image = tf.expand_dims(image, axis=0)
            
        image = tf.image.resize(image, size=(self.image_size[0], self.image_size[1]),
            method=tf.image.ResizeMethod.BILINEAR)
        
        image = tf.cast(image, tf.float32)
        image = tf.expand_dims(image, axis=0)
        image = (image / 127.5) - 1.
        labeling = self.infer(image)
        preds = labeling['output']

        # output = self.model.predict_on_batch(image)
        output = tf.argmax(preds, axis=-1)
        output = output[0]
        return output.numpy().astype(np.uint8)