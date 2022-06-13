#!/user/bin/env python

#imports
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

#load face detection algorithms
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
num_landmarks = 68

#set accuracy threshold needed to be reached in order to determine human id
accuracyThreshold = float(0.9)

#check cuda is being used
sys.stdout.write(CYAN)
print("Using CUDA:")
print(dlib.DLIB_USE_CUDA)
sys.stdout.write(RESET)

def imageAnalyse(class_names, device, model_trained):
	#load image and run face detection
	for f in glob.glob('image_cam.jpg'):
		img = io.imread(f)
		dets = detector(img, 1)  # face detection

		# ignore all the files with no or more than one faces detected.
		if len(dets) == 1:
			humanid, confidence = face_infer.infer_face(class_names, device, model_trained)
			#if confidence on prediction is below threshold then class as unknown
			if confidence < accuracyThreshold:
				humanid = ("unknown")
		else:
			#with no face detected mark as no one there
			humanid = ("noone")
			confidence = float(0.0)
			
	#run object inference
	topPrediction, topPredictionConfidence = object_infer.infer_object()
	
	#return values
	return topPrediction, topPredictionConfidence, humanid, confidence

#if called direct then run the function
if __name__ == '__main__':
	class_names, device, model_trained = face_infer.loadAndSetup()
	sys.stdout.write(RED)
	print(imageAnalyse(class_names, device, model_trained))
	sys.stdout.write(RESET)
