from time import sleep

from config.vision_config import *

from picamera2 import Picamera2, Preview

from time import sleep


class CameraControl:
    def __init__(self):
        """
        Initialise the camera
        """
        self.camera_resolution = (resolution_x, resolution_y)

        self.camera = Picamera2()
        print(self.camera.sensor_resolution)

        preview_config = self.camera.preview_configuration(main={"size": self.camera_resolution})

        self.camera.configure(preview_config)

        print(self.camera.camera_configuration)

        self.camera.start()
        sleep(2)

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
