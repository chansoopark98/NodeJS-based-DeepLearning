from tensorflow.python.saved_model import tag_constants
import tensorflow as tf
import numpy as np
import open3d as o3d
import cv2
import math

def classifier(x, num_classes=19, upper=4, name=None):
    x = tf.keras.layers.Conv2D(num_classes,
                               kernel_size=1,
                               strides=1,
                               kernel_initializer=tf.keras.initializers.VarianceScaling(
                                   scale=1.0, mode="fan_out", distribution="truncated_normal")
                               )(x)
    x = tf.keras.layers.UpSampling2D(size=(upper, upper),
                                     interpolation='bilinear',
                                     name=name)(x)
    return x

class SemanticModel():
    def __init__(self):
        self.image_size = (320, 240)
        # tf.config.set_soft_device_placement(True)
        self.load_model()
        self.warm_up()
    
    def load_model(self):
        converted_model_path = '/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path_trt/1/'
    
        print('load_model')
        seg_model = tf.saved_model.load(converted_model_path, tags=[tag_constants.SERVING])
    
        print('infer')
        self.infer = seg_model.signatures['serving_default']


    def warm_up(self):
        dummy_data = tf.zeros((1, self.image_size[0], self.image_size[1],3))
    
        with tf.device('/device:GPU:0'):
            pred_seg = self.infer(dummy_data)
            _ = pred_seg['output']
            print('gpu 0 warm up')
        with tf.device('/device:GPU:1'):
            pred_seg = self.infer(dummy_data)
            _ = pred_seg['output']
            print('gpu 1 warm up')
    
    
    def model_predict(self, image, gpu_name):
        # with tf.device(gpu_name):
        shape = image.shape
            
        image = tf.image.resize(image, size=(self.image_size[0], self.image_size[1]),
            method=tf.image.ResizeMethod.BILINEAR)
        
        image = tf.cast(image, tf.float32)
        image = tf.expand_dims(image, axis=0)
        image /= 255.

        preds = self.infer(image)
        pred_output = preds['output']
        output = tf.argmax(pred_output, axis=-1)
        output = output[0]
        output = tf.expand_dims(output, axis=-1)
        
        
        
        output = tf.image.resize(output, size=(shape[0], shape[1]), method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
        
        
        return output[:, :, 0].numpy().astype(np.uint8) * 127


    def euler_from_matrix(self, rot, degree=False ):
        
        sy = math.sqrt( rot[2, 1]*rot[2, 1]+rot[2, 2]*rot[2, 2] )
        singular = sy < 1e-6

        roll = math.atan2( rot[2, 1], rot[2, 2] )
        pitch = math.atan2(-rot[2, 0], math.sqrt( rot[2, 1]*rot[2, 1]+rot[2, 2]*rot[2, 2] ) )
        yaw = math.atan2( rot[1, 0], rot[0, 0] )
        
        if degree:
            return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)
        else:
            return roll, pitch, yaw

    def calc_pca(self, img, mask):
        img_h = img.shape[0]
        img_w = img.shape[1]

        # Get display area
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        display_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        # tmp = 0
        # display_contours = []
        # for contour in contours:
        #     area = cv2.contourArea(contour)
        #     if area > tmp: 
        #         tmp = area
        #         display_contours.append(contour)
                
        x,y,w,h = cv2.boundingRect(display_contours[0])
        area = cv2.contourArea(display_contours[0])

        print(area)

        depth_map = np.ones((img.shape[0], img.shape[1], 1), np.float32)
        depth_map[y:y+h, x:x+w] *= 300.

        open3d_rgb = o3d.geometry.Image(img)
        pred_depth = o3d.geometry.Image(depth_map)

        rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
            open3d_rgb, pred_depth)

        pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
            rgbd_image,
            o3d.camera.PinholeCameraIntrinsic(
                o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault))

        xyz_load = np.asarray(pcd.points)
 
        pc = np.zeros((img_h, img_w, 3))
        xyz_load = np.reshape(xyz_load, (img_h, img_w, 3))
        pc[:,:,0] = xyz_load[:, :, 0]
        pc[:,:,1] = xyz_load[:, :, 1]
        pc[:,:,2] = xyz_load[:, :, 2]

        center_x = x + (w//2)
        center_y = y + (h//2)
        
        choose_pc = pc[center_y-1:center_y+1, center_x-1:center_x+1]

        pointCloud_area = np.zeros((img_h, img_w), dtype=np.uint8)
        pointCloud_area = cv2.line(pointCloud_area, (center_x-1, center_y-1), (center_x+1, center_y+1), 255, 10, cv2.LINE_AA)
        choose_pc = pc[np.where(pointCloud_area[:, :]==255)]
                    
        choose_pc = choose_pc[~np.isnan(choose_pc[:,2])]

        meanarr, comparr, _ = cv2.PCACompute2(choose_pc, mean=None)

        comparr = -comparr
        if comparr[2, 2] < 0:
            comparr[2, :3] = -comparr[2, :3]
                    
        # Target Pose 생성
        target_pose = np.identity(4)
        target_pose[:3,:3] = comparr.T # rotation
        target_pose[:3,3] = meanarr # transration

        roll, pitch, yaw = self.euler_from_matrix(rot=target_pose[:3,:3], degree=False)

        return center_x, center_y, roll, pitch, yaw, area, w, h

