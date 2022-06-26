from time import sleep

from config.vision_config import *

from picamera2 import Picamera2, Preview

from time import sleep


# picam2 = Picamera2()
# picam2.start_preview(Preview.QTGL)
#
# preview_config = picam2.preview_configuration(raw={"size": picam2.sensor_resolution})
# print(preview_config)
# picam2.configure(preview_config)
#
# picam2.start()
# time.sleep(2)
#
# raw = picam2.capture_array("raw")
# print(raw.shape)
# print(picam2.stream_configuration("raw"))

# todo: check if anything needs changing to use picamera2 https://github.com/raspberrypi/picamera2/blob/main/examples/opencv_face_detect.py


class CameraControl:
    def __init__(self):
        """
        Initialise the camera
        """
        self.camera_resolution = (resolution_x, resolution_y)

        self.camera = Picamera2()
        print(self.camera.sensor_resolution)

        preview_config = self.camera.preview_configuration(raw={"size": self.camera_resolution})
        print(preview_config)
        self.camera.configure(preview_config)

        print(self.camera.camera_configuration)

        self.camera.start()
        sleep(2)

        self.raw = self.camera.capture_array("raw")
        print(self.raw.shape)
        print(self.camera.stream_configuration("raw"))

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
