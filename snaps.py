import time
import os
import subprocess

def takePic():
	process = subprocess.Popen(['bash', 'image_cap.sh'], stdout=open(os.devnull, 'wb'))
	process.communicate()

def takePics(num, name):
	nameFolder = ("./images/train/" + name)
	for i in range(num):
		process = subprocess.Popen(['bash', 'image_cap_norename.sh', nameFolder], stdout=open(os.devnull, 'wb'))
		process.communicate()
		#time.sleep(3)
		
#if called direct then run the function
if __name__ == '__main__':
	takePic()