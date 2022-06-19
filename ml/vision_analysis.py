import os
import subprocess
import time
import sys
import numpy as np
from colors import *
import dlib
import dlib.cuda as cuda
import glob
import csv
from skimage import io
import face_infer
import object_infer
from colors import *

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
num_landmarks = 68

accuracyThreshold = float(0.9)

print("Using CUDA:")
print(dlib.DLIB_USE_CUDA)


def image_analyse(class_names, device, model_trained):
    # load image and run face detection
    for f in glob.glob('image_cam.jpg'):
        img = io.imread(f)
        dets = detector(img, 1)  # face detection

        # ignore all the files with no or more than one faces detected.
        if len(dets) == 1:
            humanid, confidence = face_infer.infer_face(class_names, device, model_trained)
            # if confidence on prediction is below threshold then class as unknown
            if confidence < accuracyThreshold:
                humanid = "unknown"
        else:
            # with no face detected mark as no one there
            humanid = "noone"
            confidence = float(0.0)

    # run object inference
    top_prediction, top_prediction_confidence = object_infer.infer_object()

    # return values
    return top_prediction, top_prediction_confidence, humanid, confidence


# if called direct then run the function
if __name__ == '__main__':
    class_names, device, model_trained = face_infer.loadAndSetup()
    print(image_analyse(class_names, device, model_trained))
