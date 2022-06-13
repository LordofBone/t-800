import time
import os
from subprocess import call

def ledON():
	call('echo "79" > /sys/class/gpio/export', shell=True)
	call('echo "out" > /sys/class/gpio/gpio79/direction', shell=True)
	call('echo "1" > /sys/class/gpio/gpio79/value', shell=True)
	
def ledOFF():
        call('echo "79" > /sys/class/gpio/export', shell=True)
        call('echo "out" > /sys/class/gpio/gpio79/direction', shell=True)
        call('echo "0" > /sys/class/gpio/gpio79/value', shell=True)

def ledFlash(timesToFlash):
		for i in range(timesToFlash):
			call('echo "0" > /sys/class/gpio/gpio79/value', shell=True)
			time.sleep(0.1)
			call('echo "1" > /sys/class/gpio/gpio79/value', shell=True)
			time.sleep(0.1)


#if called direct then run the function
if __name__ == '__main__':
	ledON()
