from picamera import PiCamera
from picamera.array import PiRGBArray

from time import sleep

from config.vision_config import *


class CameraControl:
    def __init__(self):
        """
        Initialise the camera
        """
        self.camera = PiCamera()
        self.camera.resolution = (resolution_x, resolution_y)
        self.camera.framerate = framerate

        # Grab reference to the raw capture
        self.rawCapture = PiRGBArray(CameraControlAccess.camera, size=(resolution_x, resolution_y))
        self.rawCapture.truncate(0)

    def take_pic(self, name):
        """
        Take a picture and save it to the specified directory
        :param name:
        :return:
        """
        self.camera.start_preview()
        sleep(5)
        self.camera.capture(f'{object_detect_images_dir}/{name}.jpg')
        self.camera.stop_preview()

    def take_pics(self, num, name):
        """
        Take a number of pictures and save them to the specified directory
        :param num:
        :param name:
        :return:
        """
        for i in range(num):
            self.camera.start_preview()
            sleep(5)
            self.camera.capture(f'{object_detect_images_dir}/{name}_{num}.jpg')
            self.camera.stop_preview()


CameraControlAccess = CameraControl()

if __name__ == '__main__':
    CameraControlAccess.take_pic('test')
