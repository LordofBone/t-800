#!/user/bin/env python

#imports
import time
import os
import sys
import subprocess
import vision_analysis
import chatbot
import speech_out
import speech_in
import log_new_face
import face_trainer
import face_infer
import snaps
import led_on
from colors import *

#switch on the eye led
led_on.ledON()

#setup face inference
class_names, device, model_trained = face_infer.loadAndSetup()

#number of times to loop conversation routine per photo analysis
convo_loop_times = (10)

#clear initial input variable
inputWords = ("")

#function for getting all names from the training folders
def get_immediate_subdirectories(a_dir):
	return [name for name in os.listdir(a_dir)
			if os.path.isdir(os.path.join(a_dir, name))]

#put all human names in training into a list (currently not being used)			
#human_names = get_immediate_subdirectories('./images/train/')

def conversation(inputWords, humanid):
	#send off input and human id to chatbot
	reply = chatbot.conversation(inputWords, humanid)
	
	#print reply for debugging/logging
	sys.stdout.write(BLUE)
	print (reply)
	sys.stdout.write(RESET)
	
	#use tts for saying reply
	speech_out.tts(reply)
	
	return reply
			
while True:
	#set print colour for outputs
	sys.stdout.write(RED)
	
	#clear variables for loop start
	topPrediction = ()
	topPredictionConfidence = ()
	humanid = ("noone")
	
	#flash led and take a pic
	led_on.ledFlash(6)
	snaps.takePic()
	led_on.ledFlash(2)
	
	#output for logging
	print("Processing objects and looking for faces")
	
	#get predictions from vision analysis module
	topPrediction, topPredictionConfidence, humanid, confidence = vision_analysis.imageAnalyse(class_names, device, model_trained)
	
	#print outputs of object inference for logging/debug
	print(topPrediction)
	print(topPredictionConfidence)
	
	#send outputs of object inference to chatbot
	chatbot.dbWordsUpdate(topPrediction)
	
	#if human id none - say out loud the results from object inference
	if humanid == "noone":
		speech_out.tts(topPrediction)
		continue
	else:
		#if human id unknown grab photos of them and log to training folder - then run the training module
		if humanid == "unknown":
			print("No face identified")
			speech_out.tts("Please identify yourself")
			humanid = speech_in.listen()
			sys.stdout.write(RED)
			print(humanid)
			sys.stdout.write(RESET)
			log_new_face.log_face(humanid)
			speech_out.tts("Say cheese")
			led_on.ledFlash(6)
			snaps.takePics(9, humanid)
			led_on.ledFlash(2)
			speech_out.tts("Training neural net with new face, please wait")
			face_trainer.face_train()
			speech_out.tts("Training complete")
			#reload model and classes containing names into face inference module
			class_names, device, model_trained = face_infer.loadAndSetup()
		else:
			#if human identified log out to 
			print("Face identified: " + humanid)
		
		#run conversation loop
		for i in range(convo_loop_times):
			#bot gives initial greeting
			conversation(inputWords, humanid)
			#human response is taken and printed - then loops around putting the input back into the conversation module
			inputWords = speech_in.listen()
			sys.stdout.write(BLUE)
			print(inputWords)
			sys.stdout.write(RESET)