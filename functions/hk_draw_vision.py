# !/user/bin/env python3

# This module is for drawing text and other details onto a frame passed into it and then displaying it to the user if
# vision is enabled

from dataclasses import dataclass, field

import cv2
import numpy as np

from hk_event_processor import EventFactoryAccess
from hk_serial_interfacing import SerialAccess
from hk_yaml_importer import YAMLAccess


# Function for getting items from a list/dictionary and catching index/key errors if there is no such item
def get_list_item(ind, list_in):
    try:
        return list_in[ind]
    except IndexError:
        return ""
    except KeyError:
        return ""


# todo: determine whether this needs to be a dataclass
@dataclass
class HKVision:
    frame_x: int
    frame_y: int
    cv2 = cv2
    frame: np.ndarray = np.zeros(shape=16)
    smaller_img: np.ndarray = np.zeros(shape=16)
    freq = cv2.getTickFrequency()
    font = cv2.FONT_HERSHEY_PLAIN
    font_size = 1
    font_thickness = 1
    x_offset: int = .48
    y_offset: int = .15
    text_list_event: list = field(default_factory=list)
    text_list_serial: list = field(default_factory=list)
    text_list_params_primary: list = field(default_factory=dict)
    text_list_params_secondary: list = field(default_factory=dict)
    text_list_params_tertiary: list = field(default_factory=dict)
    frame_rate_calc: float = 1
    text_max_events: int = 24
    text_max_serial: int = 8
    overlay_time: int = 5
    overlay_count: int = 0
    show_smaller_img: bool = False
    smaller_image_scale: int = 4

    # This is where the latest frame to be worked on is passed in, along with the FPS number to be drawn
    def add_frame(self, frame, frame_rate_calc):
        self.frame = frame
        self.frame_rate_calc = frame_rate_calc

    # This is for overlay frames onto the main frame
    def overlay_frame(self, image, image_x, image_y, overlay_text, overlay_text_2, overlay_text_3, time):
        if not self.show_smaller_img:
            self.smaller_img = image
            self.smaller_img_x = image_x
            self.smaller_img_y = image_y
            self.overlay_text = overlay_text.upper()
            self.overlay_text_2 = 'TARGET: {}'.format(overlay_text_2.upper())
            self.overlay_text_3 = overlay_text_3.upper()
            self.overlay_time = time
            self.show_smaller_img = True

            # Resize image down
            self.resized_image = cv2.resize(self.smaller_img, (
                int(self.smaller_img_y / self.smaller_image_scale), int(self.smaller_img_x / self.smaller_image_scale)))

            # Draw text into the smaller resized image
            self.draw_text(self.resized_image, 1, self.overlay_text, 5, 15)
            self.draw_text(self.resized_image, 1, self.overlay_text_2, 5, 35)
            self.draw_text(self.resized_image, 1, self.overlay_text_3, 5, 55)

    # This is where the latest events from the event factory are added in to be drawn
    def add_text_list_event(self):
        event_insert = EventFactoryAccess.get_event_list_to_draw()
        if not event_insert == "":
            self.text_list_event.insert(0, event_insert)
            if len(self.text_list_event) == self.text_max_events:
                self.text_list_event.pop(self.text_max_events - 1)

    # This is where the latest events from the serial outputs are added in to be drawn
    def add_text_list_serial(self):
        get_serial = EventFactoryAccess.get_serial_list_to_draw()
        self.text_list_serial.insert(0, get_serial)
        if len(self.text_list_serial) == self.text_max_serial:
            self.text_list_serial.pop(self.text_max_serial - 1)

    # This draws in the overlay picture set from the overlay function
    def picture_in_picture(self):
        # Get height/width of resized image
        h1, w1 = self.resized_image.shape[:2]

        # Set position of resized image
        pip_h = 400
        pip_w = 450

        # Overlay resized image onto the main frame
        self.frame[pip_h:pip_h + h1, pip_w:pip_w + w1] = self.resized_image

    # This grabs the mission parameters to be drawn
    def add_mission_params(self, primary, secondary, tertiary):
        self.text_list_params_primary = primary
        self.text_list_params_secondary = secondary
        self.text_list_params_tertiary = tertiary

    # Function for drawing text
    def draw_text(self, frame_in, font_size, text_d="no_fps_data", text_x=15, text_y=30, text_r=255, text_g=255,
                  text_b=255):
        self.cv2.putText(frame_in, text_d, (text_x, text_y), self.font, font_size, (text_b, text_g, text_r),
                         self.font_thickness,
                         self.cv2.LINE_AA)

    # Function for going through lists and drawing them on screen as a moving set of items
    def draw_list(self, in_list, x_start=30, y_start=65):
        for i in range(0, self.text_max_events, 1):
            self.draw_text(self.frame, self.font_size, get_list_item(i, in_list), x_start, y_start)
            y_start += 25

    # Main function that draws everything to the frame and displays it
    def draw_vision(self):
        # Get latest events
        self.add_text_list_event()

        # Get latest serial outputs
        self.add_text_list_serial()

        # Display a picture of the acquired target within the main vision
        if self.show_smaller_img:
            if self.overlay_count < self.overlay_time:
                self.picture_in_picture()
                self.overlay_count += 1
            else:
                self.overlay_count = 0
                self.show_smaller_img = False

        # Draw FPS
        self.draw_text(self.frame, self.font_size, "FPS={0:.2f}".format(self.frame_rate_calc),
                       self.frame_x - int(self.frame_x * .98),
                       self.frame_y - int(self.frame_y * .98))

        # Draw resolution of camera
        self.draw_text(self.frame, self.font_size,
                       "RES_X={} RES_Y={}".format(YAMLAccess.IM_WIDTH, YAMLAccess.IM_HEIGHT),
                       self.frame_x - int(self.frame_x * .60))

        # Draw confidence threshold
        self.draw_text(self.frame, self.font_size, "CONF_THRESH={}".format(YAMLAccess.CONF_THRESHOLD),
                       self.frame_x - int(self.frame_x * .88))

        # If serial access is on (Arduino plugged-in and ON) then draw latest serial outputs
        # If serial is OFF then display this
        if SerialAccess.serial_on:
            self.draw_text(self.frame, self.font_size, "SERIAL_READS:",
                           self.frame_x - int(self.frame_x * .22))
        else:
            self.draw_text(self.frame, self.font_size, "NO_SERIAL_DEVICE",
                           self.frame_x - int(self.frame_x * .22))

        # Draw events to screen
        self.draw_list(self.text_list_event, self.frame_x - int(self.frame_x * .95))

        # Draw serial outputs to screen
        self.draw_list(self.text_list_serial, self.frame_x - int(self.frame_x * .20))

        # Draw mission parameters
        self.draw_text(self.frame, self.font_size, "MISSION_PARAMS:", self.frame_x - int(self.frame_x * .22),
                       self.frame_y - int(self.frame_y * .47))

        self.draw_list(self.text_list_params_primary, self.frame_x - int(self.frame_x * .20),
                       self.frame_y - int(self.frame_y * .45))

        self.draw_list(self.text_list_params_secondary, self.frame_x - int(self.frame_x * .20),
                       self.frame_y - int(self.frame_y * .30))

        self.draw_list(self.text_list_params_tertiary, self.frame_x - int(self.frame_x * .20),
                       self.frame_y - int(self.frame_y * .15))

        # All the results have been drawn on the frame, so it's time to display it.
        self.cv2.imshow('Live Vision', self.frame)

        # Press 'q' to quit
        if self.cv2.waitKey(1) == ord('q'):
            self.clear_vision()

    # Function for clearing all cv2 windows
    def clear_vision(self):
        self.cv2.destroyAllWindows()


# Instantiate the main class so that all modules can access the vision functions
VisionAccess = HKVision(YAMLAccess.IM_WIDTH, YAMLAccess.IM_HEIGHT)
