import ssl
import asyncio
import websockets
import cv2
import numpy as np
import base64
import mediapipe as mp
import json

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)



width = 1920
height = 1080
focal_length = 1 * width
cam_matrix = np.array([[focal_length, 0, height/2],
                            [0, focal_length, width/2],
                            [0, 0, 1]])
cam_matrix = np.array(cam_matrix)
dist_matrix = np.zeros((4, 1), dtype=np.float64)


image = cv2.imread('./samples/test_image.jpg')



image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
image.flags.writeable = False
results = face_mesh.process(image)
image.flags.writeable = True




send_dict = []

if results.multi_face_landmarks:
    detected_faces = results.multi_face_landmarks
    detected_nums = len(detected_faces)
    # for face_landmarks in results.multi_face_landmarks:
    for face_idx in range(detected_nums):
        face_2d = []
        face_3d = []
        output = []
        print(face_idx)
        for idx, lm in enumerate(detected_faces[face_idx].landmark):
            if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                if idx == 1:
                    center_x = int(lm.x * width)
                    center_y = int(lm.y * height)
                x = int(lm.x * width)
                y = int(lm.y * height)


                face_2d.append([x,y])
                face_3d.append([x, y, lm.z])


        face_2d = np.array(face_2d, dtype=np.float64)
        face_3d = np.array(face_3d, dtype=np.float64)

        success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

        rmat, jac = cv2.Rodrigues(rot_vec)

        angle, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)


            # print(angle)
        center_x = str(center_x) + ','
        center_y = str(center_y) + ','
        # center_x = str(960) + ','
        # center_y = str(400) + ','
        x_rot = str(angle[0] ) + ','
        y_rot = str(round(angle[1], 3)) + ','
        z_rot = str(angle[2]) + ','

        output = {'center_x' : center_x,
                    'center_y' : center_y,
                    'x_rot' : x_rot,
                    'y_rot' : y_rot,
                    'z_rot' : z_rot}

        send_dict.append(output)
        
    print(json.dumps(send_dict).encode('UTF-8'))
            
