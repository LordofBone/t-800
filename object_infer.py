import os
import subprocess
import time
import sys
import numpy as np
from colors import *

def infer_object():

	#commdand for passing the photo into imagenet
	process = subprocess.Popen(['./my-recognition', 'image_cam.jpg'], stdout=subprocess.PIPE)

	#execute the command and get output
	out, err = process.communicate()

	#get the top predictions and score and strip out any newlines
	topPredictionSplit = str(out.split("recognized as ")[1])
	topPrediction = str(topPredictionSplit.split(" (class")[0])
	topPredictionConfidence = str(topPredictionSplit.split("with ")[1])
	topPrediction = topPrediction.replace("'", "")
	topPredictionConfidence = topPredictionConfidence.replace(" confidence", "")
	topPredictionConfidence = topPredictionConfidence.strip('\n')

	#print results
	sys.stdout.write(BLUE)
	print(topPrediction)
	print(topPredictionConfidence)
	sys.stdout.write(RESET)
	
	#return the prediction and confidence
	return topPrediction, topPredictionConfidence

#if called direct then run the function	
if __name__ == '__main__':
	print(infer_object())