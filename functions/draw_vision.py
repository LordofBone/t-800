# !/user/bin/env python3

# This module is for drawing text and other details onto a frame passed into it and then displaying it to the user if
# vision is enabled
import logging
from dataclasses import dataclass, field

import cv2
import numpy as np

from hardware.serial_interfacing import SerialAccess

from functions.talk_control import TalkControllerAccess

from events.event_queue import DrawListQueueAccess
from events.event_types import SERIAL_DRAW, OVERLAY_DRAW, ANY, HUMAN, PRIMARY, SECONDARY, TERTIARY, IDENT_POSITIVE, \
    LISTENING, INFERENCING_SPEECH

from config.vision_config import *

logger = logging.getLogger("vision-control")


def get_list_item(ind, list_in):
    """
    Get an item from a list/dictionary and catch index/key errors if there is no such item
    :param ind:
    :param list_in:
    :return:
    """
    try:
        return list_in[ind]
    except IndexError:
        return ""
    except KeyError:
        return ""


# todo: determine whether this needs to be a dataclass
@dataclass
class HKVision:
    """
    This is the main function for drawing the vision onto the frame
    """
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
    text_list_current_process: list = field(default_factory=list)
    text_list_params_primary: list = field(default_factory=dict)
    text_list_params_secondary: list = field(default_factory=dict)
    text_list_params_tertiary: list = field(default_factory=dict)
    frame_rate_calc: float = 1
    text_max_events: int = 24
    text_max_serial: int = 8
    text_max_current_process: int = 3
    overlay_time: int = 5
    overlay_count: int = 0
    show_smaller_img: bool = False
    smaller_image_scale: int = 4
    ANY_NO_SERIAL_DRAW = ANY
    ANY_NO_SERIAL_DRAW.remove(SERIAL_DRAW)
    ANY_NO_SERIAL_DRAW.remove(OVERLAY_DRAW)

    def add_frame(self, frame, frame_rate_calc):
        """
        This is where the latest frame to be worked on is passed in, along with the FPS number to be drawn
        :param frame:
        :param frame_rate_calc:
        :return:
        """
        self.frame = frame
        self.frame_rate_calc = frame_rate_calc

    def add_sub_image(self, image, image_x, image_y):
        """
        This is where a cropped image is added to the frame for overlaying
        :param image:
        :param image_x:
        :param image_y:
        :return:
        """
        self.cropped_image = image
        self.smaller_img_x = image_x
        self.smaller_img_y = image_y

    def overlay_frame(self, overlay_text, overlay_text_2, overlay_text_3, time):
        """
        This is where the overlay image is drawn onto the frame
        :param overlay_text:
        :param overlay_text_2:
        :param overlay_text_3:
        :param time:
        :return:
        """
        if not self.show_smaller_img:
            self.overlay_text = overlay_text.upper()
            self.overlay_text_2 = 'TARGET: {}'.format(overlay_text_2.upper())
            self.overlay_text_3 = overlay_text_3.upper()
            self.overlay_time = time
            self.show_smaller_img = True

            # Resize image down
            self.resized_image = cv2.resize(self.cropped_image, (
                int(self.smaller_img_y / self.smaller_image_scale), int(self.smaller_img_x / self.smaller_image_scale)))

            # Draw text into the smaller resized image
            self.draw_text_resized(1, self.overlay_text, 5, 15)
            self.draw_text_resized(1, self.overlay_text_2, 5, 35)
            self.draw_text_resized(1, self.overlay_text_3, 5, 55)

    def add_text_list_event(self):
        """
        This is where the latest events from the event processor are added in to be drawn
        :return:
        """
        # todo: figure out why the event type is drawing to screen not the content of the event
        event = DrawListQueueAccess.get_latest_event(self.ANY_NO_SERIAL_DRAW)
        if event:
            self.text_list_event.insert(0, event[2])
            if len(self.text_list_event) == self.text_max_events:
                self.text_list_event.pop(self.text_max_events - 1)

    def add_text_list_serial(self):
        """
        This is where the latest serial data from the serial interface is added in to be drawn
        :return:
        """
        event = DrawListQueueAccess.get_latest_event([SERIAL_DRAW])
        if event:
            self.text_list_serial.insert(0, event[2])
            if len(self.text_list_serial) == self.text_max_serial:
                self.text_list_serial.pop(self.text_max_serial - 1)

    def add_text_list_current_process(self, current_process):
        """
        This is where the latest current process from the serial interface is added in to be drawn
        :return:
        """
        self.text_list_current_process.insert(0, current_process)
        if len(self.text_list_current_process) == self.text_max_current_process:
            self.text_list_current_process.pop(self.text_max_current_process - 1)

    def picture_in_picture(self):
        """
        This is where the smaller image is drawn onto the frame
        :return:
        """
        # Get height/width of resized image
        h1, w1 = self.resized_image.shape[:2]

        # Set position of resized image
        pip_h = 400
        pip_w = 450

        # Overlay resized image onto the main frame
        self.frame[pip_h:pip_h + h1, pip_w:pip_w + w1] = self.resized_image

    def add_mission_params(self, primary, secondary, tertiary):
        """
        This is where the mission parameters are added in to be drawn
        :param primary:
        :param secondary:
        :param tertiary:
        :return:
        """
        self.text_list_params_primary = primary
        self.text_list_params_secondary = secondary
        self.text_list_params_tertiary = tertiary

    def draw_text(self, font_size, text_d="no_fps_data", text_x=15, text_y=30, text_r=255, text_g=255,
                  text_b=255):
        """
        This is where the text is drawn onto the frame
        :param font_size:
        :param text_d:
        :param text_x:
        :param text_y:
        :param text_r:
        :param text_g:
        :param text_b:
        :return:
        """
        self.cv2.putText(self.frame, text_d, (text_x, text_y), self.font, font_size, (text_b, text_g, text_r),
                         self.font_thickness,
                         self.cv2.LINE_AA)

    def draw_text_resized(self, font_size, text_d="no_fps_data", text_x=15, text_y=30, text_r=255, text_g=255,
                          text_b=255):
        """
        This is where the text is drawn onto a cropped frame
        :param self:
        :param font_size:
        :param text_d:
        :param text_x:
        :param text_y:
        :param text_r:
        :param text_g:
        :param text_b:
        :return:
        """
        self.cv2.putText(self.resized_image, text_d, (text_x, text_y), self.font, font_size, (text_b, text_g, text_r),
                         self.font_thickness,
                         self.cv2.LINE_AA)

    def draw_list(self, in_list, x_start=30, y_start=65, y_move=25):
        """
        This is where the list of events/serial data is drawn onto the frame
        :param y_move:
        :param in_list:
        :param x_start:
        :param y_start:
        :return:
        """
        for i in range(0, self.text_max_events, 1):
            self.draw_text(self.font_size, get_list_item(i, in_list), x_start, y_start)
            y_start += y_move

    def draw_vision(self):
        """
        This is where the vision data is drawn onto the frame
        :return:
        """
        event = DrawListQueueAccess.get_latest_event([OVERLAY_DRAW])

        if event:
            split_event_details = event[2].split("|")

            if split_event_details[0] == PRIMARY:
                self.overlay_frame(IDENT_POSITIVE, split_event_details[1], split_event_details[2], 20)
            elif split_event_details[0] == SECONDARY:
                self.overlay_frame(IDENT_POSITIVE, split_event_details[1], split_event_details[2], 20)
            elif split_event_details[0] == TERTIARY:
                self.overlay_frame(IDENT_POSITIVE, split_event_details[1], split_event_details[2], 20)

        if TalkControllerAccess.STT_handler.listening:
            self.add_text_list_current_process(LISTENING)
        else:
            try:
                self.text_list_current_process.remove(LISTENING)
            except ValueError:
                logger.debug("No listening text found")

        if TalkControllerAccess.STT_handler.inferencing:
            self.add_text_list_current_process(INFERENCING_SPEECH)
        else:
            try:
                self.text_list_current_process.remove(INFERENCING_SPEECH)
            except ValueError:
                logger.debug("No inferencing text found")

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
        self.draw_text(self.font_size, "FPS={0:.2f}".format(self.frame_rate_calc),
                       self.frame_x - int(self.frame_x * .98),
                       self.frame_y - int(self.frame_y * .98))

        # Draw resolution of camera
        self.draw_text(self.font_size,
                       "RES_X={} RES_Y={}".format(resolution_x, resolution_y),
                       self.frame_x - int(self.frame_x * .60))

        # Draw confidence threshold
        self.draw_text(self.font_size, "CONF_THRESH={}".format(CONF_THRESHOLD),
                       self.frame_x - int(self.frame_x * .88))

        # If serial access is on (Arduino plugged-in and ON) then draw latest serial outputs
        # If serial is OFF then display this
        if SerialAccess.serial_on:
            self.draw_text(self.font_size, "SERIAL_READS:",
                           self.frame_x - int(self.frame_x * .22))
        else:
            self.draw_text(self.font_size, "NO_SERIAL_DEVICE",
                           self.frame_x - int(self.frame_x * .22))

        # Draw events to screen
        self.draw_list(self.text_list_event, self.frame_x - int(self.frame_x * .95))
        # Draw serial outputs to screen
        self.draw_list(self.text_list_serial, self.frame_x - int(self.frame_x * .20))

        self.draw_list(self.text_list_current_process, int(self.frame_x / 2 - 50), int(self.frame_y / 2 - 50), 30)

        # Draw mission parameters
        self.draw_text(self.font_size, "MISSION_PARAMS:", self.frame_x - int(self.frame_x * .22),
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

    def wipe_frames(self):
        """
        This is where the frames are wiped clean to try and save on RAM
        :return:
        """
        del self.frame
        # del self.smaller_img
        # del self.resized_image

    def clear_vision(self):
        """
        This is where all the cv2 windows are cleared
        :return:
        """
        self.cv2.destroyAllWindows()


# Instantiate the main class so that all modules can access the vision functions
VisionAccess = HKVision(resolution_x, resolution_y)
