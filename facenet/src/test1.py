from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

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


def Face_load_data(face_list, do_random_crop, do_random_flip, image_size, do_prewhiten=True):
    nrof_samples = len(face_list)
    images = np.zeros((nrof_samples, image_size, image_size, 3))
    for i in range(nrof_samples):
        img = face_list[i]
        if img.ndim == 2:
            img = to_rgb(img)
        if do_prewhiten:
            img = prewhiten(img)
        img = crop(img, do_random_crop, image_size)
        img = flip(img, do_random_flip)
        images[i, :, :, :] = img
    return images


def prewhiten(x):
    mean = np.mean(x)
    std = np.std(x)
    std_adj = np.maximum(std, 1.0 / np.sqrt(x.size))
    y = np.multiply(np.subtract(x, mean), 1 / std_adj)
    return y


def crop(image, random_crop, image_size):
    if image.shape[1] > image_size:
        sz1 = int(image.shape[1] // 2)
        sz2 = int(image_size // 2)
        if random_crop:
            diff = sz1 - sz2
            (h, v) = (np.random.randint(-diff, diff + 1), np.random.randint(-diff, diff + 1))
        else:
            (h, v) = (0, 0)
        image = image[(sz1 - sz2 + v):(sz1 + sz2 + v), (sz1 - sz2 + h):(sz1 + sz2 + h), :]
    return image


def flip(image, random_flip):
    if random_flip and np.random.choice([True, False]):
        image = np.fliplr(image)
    return image


def to_rgb(img):
    w, h = img.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 0] = ret[:, :, 1] = ret[:, :, 2] = img
    return ret


print('Creating networks and loading parameters')
with tf.Graph().as_default():
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.9)
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
        detect_multiple_faces = True

        print('Loading feature extraction model')
        modeldir = '/home/snow/Desktop/Face-Tag/models/20180402-114759.pb'
        facenet.load_model(modeldir)

        # Classify images
        print('Testing classifier')
        classifier_filename_exp = os.path.expanduser(
            '/home/snow/Desktop/Face-Tag/models/ft_v1__classifier.pkl')
        with open(classifier_filename_exp, 'rb') as infile:
            (model, class_names) = pickle.load(infile)

        # Get input and output tensors
        images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
        embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
        embedding_size = embeddings.get_shape()[1]

        start = time.time()
        image_path = '/home/snow/Desktop/Face-Tag/DSC_4354.JPG'
        try:
            img = misc.imread(image_path)

        except (IOError, ValueError, IndexError) as e:
            errorMessage = '{}: {}'.format(image_path, e)
            print(errorMessage)
        else:
            if img.ndim < 2:
                print('Unable to align "%s"' % image_path)
            if img.ndim == 2:
                img = facenet.to_rgb(img)
            img = img[:, :, 0:3]

            bounding_boxes, box_cord = detect_face.detect_face(
                img, minsize, pnet, rnet, onet, threshold, factor)

            nrof_faces = bounding_boxes.shape[0]
            face_list = []
            if nrof_faces > 0:
                det = bounding_boxes[:, 0:4]
                det_arr = []
                img_size = np.asarray(img.shape)[0:2]
                if nrof_faces > 1:
                    if detect_multiple_faces:
                        for i in range(nrof_faces):
                            det_arr.append(np.squeeze(det[i]))
                    else:
                        bounding_box_size = (det[:, 2]-det[:, 0])*(det[:, 3]-det[:, 1])
                        img_center = img_size / 2
                        offsets = np.vstack([(det[:, 0]+det[:, 2])/2-img_center[1],
                                             (det[:, 1]+det[:, 3])/2-img_center[0]])
                        offset_dist_squared = np.sum(np.power(offsets, 2.0), 0)
                        index = np.argmax(bounding_box_size-offset_dist_squared *
                                          2.0)  # some extra weight on the centering
                        det_arr.append(det[index, :])
                else:
                    det_arr.append(np.squeeze(det))

                for i, det in enumerate(det_arr):
                    det = np.squeeze(det)
                    bb = np.zeros(4, dtype=np.int32)
                    bb[0] = np.maximum(det[0]-margin/2, 0)
                    bb[1] = np.maximum(det[1]-margin/2, 0)
                    bb[2] = np.minimum(det[2]+margin/2, img_size[1])
                    bb[3] = np.minimum(det[3]+margin/2, img_size[0])
                    cropped = img[bb[1]:bb[3], bb[0]:bb[2], :]
                    scaled = misc.imresize(
                        cropped, (image_size, image_size), interp='bilinear')
                    face_list.append(scaled)
            else:
                print('Unable to align "%s"' % image_path)

            # Run forward pass to calculate embeddings
            print('Calculating features for images')

            nrof_images = nrof_faces
            nrof_batches_per_epoch = int(math.ceil(1.0 * nrof_images / batch_size))
            emb_array = np.zeros((nrof_images, embedding_size))
            for i in range(nrof_batches_per_epoch):
                # start_index = i * args.batch_size - Hardcoded Batch Size
                start_index = i * batch_size
                #end_index = min((i + 1) * args.batch_size, nrof_images)
                end_index = min((i + 1) * batch_size, nrof_images)

                images = Face_load_data(face_list, False, False, 160)

                feed_dict = {images_placeholder: images, phase_train_placeholder: False}
                emb_array[start_index:end_index, :] = sess.run(embeddings, feed_dict=feed_dict)

            predictions = model.predict_proba(emb_array)
            best_class_indices = np.argmax(predictions, axis=1)
            print(best_class_indices)
            best_class_probabilities = predictions[np.arange(
                len(best_class_indices)), best_class_indices]

            # Print Face recognization result for each Face in the Frame

            for i in range(len(best_class_indices)):

                print('%4d  %s: %.3f' %
                      (i, class_names[best_class_indices[i]], best_class_probabilities[i]))
        print('Took Time:', time.time()-start)
