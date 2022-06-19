# !/user/bin/env python3

# Code modified from https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi/
# /Object_detection_picamera.py

# This is where object detection is performed by Tensorflow and further information is passed into the vision module
# and onto mission parameters, depending on configuration when called it will also draw to the screen - so that a
# remote user can see what the HK is doing/seeing

import calendar
import os
import sys
import time
from dataclasses import dataclass

import cv2
import numpy as np
import tensorflow as tf
from picamera import PiCamera
from picamera.array import PiRGBArray
from six.moves import range

from hk_console_logger import ConsoleAccess
from hk_draw_vision import VisionAccess
from hk_event_queue import EventQueueAccess
from hk_yaml_importer import YAMLAccess
from hk_mission_parameteriser import mission_check

# Doing this inside the class seemed problematic, so moved outside the class:
# This is needed since the working directory is the object_detection folder.
sys.path.append(YAMLAccess.OBJ_DETECT_PATH)

# Import utilites
from utils import label_map_util as label_map_util
from utils import visualization_utils as vis_util


# todo: determine whether this needs to be a dataclass
@dataclass
class ObjectDetector(object):
    # Switch to show whether the vision of the HK is shown
    disp_vision: bool
    store_detects: bool

    # Set up camera constants
    IM_WIDTH: int
    IM_HEIGHT: int

    # Number of classes the object detector can identify
    NUM_CLASSES: int

    # Object detection code path
    OBJ_DETECT_PATH: str

    # Name of the directory containing the object detection module we're using
    MODEL_NAME: str

    objects_frame = {}

    cv2 = cv2

    t1: int = 1
    t2: int = 1

    time1: int = 1
    frame_rate_calc: float = 1

    track_ids: bool = None
    agnostic_mode: bool = False
    skip_scores: bool = False
    skip_labels: bool = False
    skip_track_ids: bool = False

    def __post_init__(self):
        # Grab path to current working directory
        self.CWD_PATH = self.OBJ_DETECT_PATH

        # Path to frozen detection graph .pb file, which contains the model that is used
        # for object detection.
        self.PATH_TO_CKPT = os.path.join(self.CWD_PATH, self.MODEL_NAME, 'frozen_inference_graph.pb')

        # Path to label map file
        self.PATH_TO_LABELS = os.path.join(self.CWD_PATH, 'data', 'mscoco_label_map.pbtxt')

        # Load the label map.
        # Label maps map indices to category names, so that when the convolution
        # network predicts `5`, we know that this corresponds to `airplane`.
        # Here we use internal utility functions, but anything that returns a
        # dictionary mapping integers to appropriate string labels would be fine
        self.label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        self.categories = label_map_util.convert_label_map_to_categories(self.label_map,
                                                                         max_num_classes=self.NUM_CLASSES,
                                                                         use_display_name=True)
        self.category_index = label_map_util.create_category_index(self.categories)

        # Load the Tensorflow model into memory.
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            self.od_graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(self.PATH_TO_CKPT, 'rb') as fid:
                self.serialized_graph = fid.read()
                self.od_graph_def.ParseFromString(self.serialized_graph)
                tf.import_graph_def(self.od_graph_def, name='')

            self.sess = tf.compat.v1.Session(graph=self.detection_graph)

        # Define input and output tensors (i.e. data) for the object detection classifier

        # Input tensor is the image
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')

        # Output tensors are the detection boxes, scores, and classes
        # Each box represents a part of the image where a particular object was detected
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')

        # Each score represents level of confidence for each of the objects.
        # The score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')

        # Number of objects detected
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

        # Initialize frame rate calculation
        self.frame_rate_calc = 1
        self.freq = self.cv2.getTickFrequency()

        # Initialize Picamera and grab reference to the raw capture
        self.camera = PiCamera()
        self.camera.resolution = (self.IM_WIDTH, self.IM_HEIGHT)
        self.camera.framerate = YAMLAccess.IM_FPS
        self.rawCapture = PiRGBArray(self.camera, size=(self.IM_WIDTH, self.IM_HEIGHT))
        self.rawCapture.truncate(0)

    def run_analysis_stream(self):
        for self.frame1 in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=False):
            self.objects_frame = {}

            self.t1 = self.cv2.getTickCount()

            # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
            # i.e. a single-column array, where each item in the column has the pixel RGB value
            self.frame = np.copy(self.frame1.array)
            self.frame.setflags(write=True)
            self.frame_rgb = self.cv2.cvtColor(self.frame, self.cv2.COLOR_BGR2RGB)
            self.frame_expanded = np.expand_dims(self.frame_rgb, axis=0)

            # Perform the actual detection by running the model with the image as input
            (self.boxes, self.scores, self.classes, self.num) = self.sess.run(
                [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
                feed_dict={self.image_tensor: self.frame_expanded})

            # Check through all detections
            for i in range(np.squeeze(self.boxes).shape[0]):

                # Only perform actions if the objects detected are above the threshold (int configurable in the
                # mission_parameters.yaml)
                if np.squeeze(self.scores) is None or np.squeeze(self.scores)[i] > YAMLAccess.CONF_THRESHOLD:
                    # Set display_str to the name of the class detected, alongside the confidence score
                    class_name = self.category_index[np.squeeze(self.classes).astype(np.int32)[i]]['name']
                    display_str = str(class_name)
                    self.objects_frame[display_str] = str(round(100 * np.squeeze(self.scores)[i]))
                    display_str_out = '{}: {}%'.format(display_str, round(100 * np.squeeze(self.scores)[i]))

                    ConsoleAccess.console_printer(display_str_out)

                    # Grab positions of the detections (x, y)
                    y_min, x_min, y_max, x_max = np.squeeze(self.boxes)[i]
                    # Have added this in here as without it, it seems to report 0,0,0,0 boxes of nothing for some reason
                    # Then convert to left, right, top, bottom for image cropping
                    if y_min > 0.00 and x_min > 0.00 and y_max > 0.00 and x_max > 0.00:
                        (left, right, top, bottom) = (x_min * YAMLAccess.IM_WIDTH, x_max * YAMLAccess.IM_WIDTH,
                                                      y_min * YAMLAccess.IM_HEIGHT, y_max * YAMLAccess.IM_HEIGHT)

                        # Crop detection from the main frame
                        crop_img = self.frame[int(top):int(bottom), int(left):int(right)]

                        # Grab current datetime
                        ts = calendar.timegm(time.gmtime())

                        # If store detections is enabled write a jpg of the cropped detection along with details in
                        # the filename
                        if self.store_detects:
                            filename = 'Captured/{}_{}_.jpg'.format(str(ts), display_str_out)
                            cv2.imwrite(filename, crop_img)

                        # Split the detection string to get the name of the detection
                        name_split = display_str_out.split(":")[0]

                        # Run the detection name into the mission parameters to check for mission objectives based on
                        # said detection and return booleans for primary, secondary and tertiary detections - along
                        # with their objectives for the detections
                        (primary_found, secondary_found, tertiary_found), (objective_p, objective_s, objective_t) = \
                            mission_check(name_split)

                        ConsoleAccess.console_printer((primary_found, secondary_found, tertiary_found))
                        ConsoleAccess.console_printer((objective_p, objective_s, objective_t))

                        # If mission objectives are found for the detection then display the cropped image of the
                        # detection along with the mame and objective.

                        # todo: look into making this a little more
                        #  advanced as at the moment it will just overlay the most recent mission detection and if
                        #  multiple levels of missions are found; for instance primary and secondary, only the most
                        #  recent will be over-layed (although both should be executed into the queue and processed)
                        if primary_found:
                            VisionAccess.overlay_frame(crop_img, right, bottom, "IDENT POSITIVE", name_split,
                                                       objective_p, 20)
                        if secondary_found:
                            VisionAccess.overlay_frame(crop_img, right, bottom, "IDENT POSITIVE", name_split,
                                                       objective_s, 20)
                        if tertiary_found:
                            VisionAccess.overlay_frame(crop_img, right, bottom, "IDENT POSITIVE", name_split,
                                                       objective_t, 20)
                        # If no mission-specific detections are found process other detections for 'person',
                        # ID as human and pass into event queue, for anything else pass in 'object' and the name of
                        # the detection
                        elif name_split == "person":
                            EventQueueAccess.queue_addition("HUMAN: " + display_str_out, "crop_img", 4)
                        else:
                            EventQueueAccess.queue_addition("OBJECT: " + display_str_out, "crop_img", 5)
                        # Delete the cropped image to save memory
                        del crop_img

            # Draw the results of the detection
            vis_util.visualize_boxes_and_labels_on_image_array(
                self.frame,
                np.squeeze(self.boxes),
                np.squeeze(self.classes).astype(np.int32),
                np.squeeze(self.scores),
                self.category_index,
                use_normalized_coordinates=True,
                line_thickness=8,
                min_score_thresh=YAMLAccess.CONF_THRESHOLD)

            # Get tick-count, this is for getting the frames-per-second (FPS)
            self.t2 = self.cv2.getTickCount()

            ConsoleAccess.console_printer("FPS: " + str(self.frame_rate_calc))

            # If vision-mode is activated then pass the frame with all the details into the vision access module
            if self.disp_vision:
                VisionAccess.add_frame(self.frame, self.frame_rate_calc)
                VisionAccess.draw_vision()

            # Perform calculations on frame-time to get FPS
            self.time1 = (self.t2 - self.t1) / self.freq
            self.frame_rate_calc = 1 / self.time1

            # Truncate the latest capture and delete the frame to save memory
            self.rawCapture.truncate(0)
            del self.frame

    # Function for closing camera, clearing vision and clearing all cv2 windows
    def clear_analysis_stream(self):
        self.camera.close()

        VisionAccess.clear_vision()

        self.cv2.destroyAllWindows()


if __name__ == "__main__":
    # Perform a test on the object detection module
    ConsoleAccess.console_print_enable = True
    ConsoleAccess.console_printer("Testing Object Detection")
    TestObjectDetect = ObjectDetector(True, False, YAMLAccess.IM_WIDTH, YAMLAccess.IM_HEIGHT, YAMLAccess.NUM_CLASSES,
                                      YAMLAccess.OBJ_DETECT_PATH, YAMLAccess.MODEL_NAME)

    TestObjectDetect.run_analysis_stream()
