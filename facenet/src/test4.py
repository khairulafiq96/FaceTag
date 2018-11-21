from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import configparser

import tensorflow as tf
from scipy import misc
import cv2
import matplotlib.pyplot as plt
import numpy as np
import argparse
import facenet
from align import detect_face
import os
from os.path import join as pjoin
import sys
import time
import copy
import math
import pickle
from sklearn.svm import SVC
from sklearn.externals import joblib

import csv
import datetime

import mysql.connector
from mysql.connector import Error
import datetime

config = configparser.ConfigParser()
config.read("myConfig.ini")
var_a = config.get("myVars", "globalFilepath")

img_path = var_a

print('Creating networks and loading parameters')
with tf.Graph().as_default():
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.6)
    sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
    with sess.as_default():
        pnet, rnet, onet = detect_face.create_mtcnn(sess, None)

        minsize = 20  # minimum size of face
        threshold = [0.6, 0.7, 0.7]  # three steps's threshold
        factor = 0.709  # scale factor
        margin = 44
        frame_interval = 3
        batch_size = 1000
        image_size = 182
        input_image_size = 160

        print('Loading feature extraction model')
        modeldir = '/home/afiq/Desktop/facetag/Face-Tag/models/20180402-114759.pb'
        facenet.load_model(modeldir)

        images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
        embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
        embedding_size = embeddings.get_shape()[1]

        classifier_filename = '/home/afiq/Desktop/facetag/Face-Tag/models/ft_v2__classifier.pkl'
        classifier_filename_exp = os.path.expanduser(classifier_filename)
        with open(classifier_filename_exp, 'rb') as infile:
            (model, class_names) = pickle.load(infile) #encoding='latin1'
            print('load classifier file-> %s' % classifier_filename_exp)

        c = 0

        print('Start Recognition!')
        print ("IMG PATH : "+ img_path)
        prevTime = 0
        frame = cv2.imread(img_path, 0)

        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)  # resize frame (optional)

        curTime = time.time()+1    # calc fps
        timeF = frame_interval

        if (c % timeF == 0):
            find_results = []

            if frame.ndim == 2:
                frame = facenet.to_rgb(frame)
            frame = frame[:, :, 0:3]
            bounding_boxes, _ = detect_face.detect_face(
                frame, minsize, pnet, rnet, onet, threshold, factor)
            nrof_faces = bounding_boxes.shape[0]
            print('Face Detected: %d' % nrof_faces)

            if nrof_faces > 0:
                det = bounding_boxes[:, 0:4]
                img_size = np.asarray(frame.shape)[0:2]

                cropped = []
                scaled = []
                scaled_reshape = [] #to an window just select "General Appearance > Icon File". Problematic here is that Glade only shows image files locate
                bb = np.zeros((nrof_faces, 4), dtype=np.int32)

                for i in range(nrof_faces):
                    emb_array = np.zeros((1, embedding_size))

                    bb[i][0] = det[i][0]
                    bb[i][1] = det[i][1]
                    bb[i][2] = det[i][2]
                    bb[i][3] = det[i][3]

                    # inner exception
                    if bb[i][0] <= 0 or bb[i][1] <= 0 or bb[i][2] >= len(frame[0]) or bb[i][3] >= len(frame):
                        print('face is too close')
                        continue

                    cropped.append(frame[bb[i][1]:bb[i][3], bb[i][0]:bb[i][2], :])
                    cropped[i] = facenet.flip(cropped[i], False)
                    scaled.append(misc.imresize(
                        cropped[i], (image_size, image_size), interp='bilinear'))
                    scaled[i] = cv2.resize(scaled[i], (input_image_size, input_image_size),
                                           interpolation=cv2.INTER_CUBIC)
                    scaled[i] = facenet.prewhiten(scaled[i])
                    scaled_reshape.append(
                        scaled[i].reshape(-1, input_image_size, input_image_size, 3))
                    feed_dict = {
                        images_placeholder: scaled_reshape[i], phase_train_placeholder: False}
                    emb_array[0, :] = sess.run(embeddings, feed_dict=feed_dict)
                    predictions = model.predict_proba(emb_array)
                    # print(predictions)
                    best_class_indices = np.argmax(predictions, axis=1)
                    print(best_class_indices)
                    best_class_probabilities = predictions[np.arange(
                        len(best_class_indices)), best_class_indices]
                    print(best_class_probabilities)

                    if best_class_probabilities[0] > 0.3136:

                        cv2.rectangle(frame, (bb[i][0], bb[i][1]), (bb[i][2],
                                                                    bb[i][3]), (0, 255, 0), 2)  # boxing face

                        # plot result idx under box DETECTED FACES
                        text_x = bb[i][0]
                        text_y = bb[i][3] + 20
                        result_names = class_names[best_class_indices[0]]
                        print(result_names)
                        cv2.putText(frame, result_names, (text_x, text_y),
                                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255),
                                    thickness=1, lineType=2)

                        #insert datastamp into file
                        out_file = open("writeTime.csv", "a")
                        writer = csv.writer(out_file)

                        try:
                           connection = mysql.connector.connect(host='localhost',
                                                     database='facetagDatabase',
                                                     user='root',
                                                     password='')



                           username = result_names
                           date_in = datetime.datetime.now().strftime("%d/%m/%y") #input
                           time_in = datetime.datetime.now().strftime("%H:%M")
                           time_out = datetime.datetime.now().strftime("%H:%M")

                           print(date_in)

                           sql_select_query = "SELECT * FROM userData WHERE username = %s AND date = %s"
                           val = (username,date_in)
                           cursor = connection.cursor()
                           cursor.execute(sql_select_query, val)
                           records = cursor.fetchall()

                           print("Total number of rows ", cursor.rowcount)

                           if cursor.rowcount == 0:
                               sql_insert_query = "INSERT INTO userData (username, date, time_in) VALUES (%s,%s,%s)"
                               val = (username,date_in,time_in)
                               cursor = connection.cursor()
                               result  = cursor.execute(sql_insert_query,val)
                               connection.commit()
                               print ("Record inserted successfully into User table")
                           else:
                                for row in records:
                                    if row[0] == username and row[1] == date_in:
                                         sql_update_query = "UPDATE userData SET time_out = %s WHERE username = %s AND date = %s"
                                         val = (time_out,username,date_in)
                                         cursor = connection.cursor()
                                         result  = cursor.execute(sql_update_query,val)
                                         connection.commit()
                           cursor.close()

                        except Error as e :
                            print ("Error while connecting to MySQL", e)
                        finally:
                            #closing database connection.
                            if(connection.is_connected()):
                                connection.close()
                                print("connection is closed")


                    elif best_class_probabilities[0] > 0.01:

                        cv2.rectangle(frame, (bb[i][0], bb[i][1]), (bb[i][2],
                                                                    bb[i][3]), (0, 255, 0), 2)  # boxing face

                        # plot result idx under box UNKNOWN
                        text_x = bb[i][0]
                        text_y = bb[i][3] + 20
                        cv2.putText(frame, "Unknown", (text_x, text_y),
                                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255),
                                    thickness=1, lineType=2)
            else:
                print('Unable to align')


            frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            cv2.imshow('Image', frame)

        if cv2.waitKey(1000000) & 0xFF == ord('q'):
            sys.exit("Thanks")
        cv2.destroyAllWindows()
