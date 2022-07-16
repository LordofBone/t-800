from events.event_queue import EventQueueAccess
from events.event_types import LED_ON, LED_OFF, LED_FLASH, LED_ACCESS

from time import sleep

import logging

import RPi.GPIO as GPIO
import time

logger = logging.getLogger("led-controller")


class LEDController:
    def __init__(self):
        self.led_flash_default = 3
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.ledPin = 14
        GPIO.setup(self.ledPin, GPIO.OUT)

    def led_on(self):
        """
        Turn the LED on
        :return:
        """
        logger.debug("Turning LED on")
        logger.debug("Eye LED turning on")
        GPIO.output(self.ledPin, GPIO.HIGH)

    def led_off(self):
        """
        Turn the LED off
        :return:
        """
        logger.debug("Turning LED off")
        logger.debug("Eye LED turning off")
        GPIO.output(self.ledPin, GPIO.LOW)

    def led_flash(self, times_to_flash):
        """
        Flash the LED a number of times
        :param times_to_flash:
        :return:
        """
        logger.debug("Flashing LED")
        for i in range(times_to_flash):
            self.led_on()
            time.sleep(0.5)
            logger.debug("Eye LED turning off")
            self.led_off()
            time.sleep(0.5)

    def queue_checker(self):
        """
        Check the event queue for events
        :return:
        """
        while True:
            event = EventQueueAccess.get_latest_event([LED_ACCESS])
            if event:
                if event[1] == LED_ON:
                    self.led_on()
                elif event[1] == LED_OFF:
                    self.led_off()
                elif event[1] == LED_FLASH:
                    self.led_flash(self.led_flash_default)
            else:
                sleep(1)


LEDControllerAccess = LEDController()

if __name__ == "__main__":
    """
    Run the LEDControllerAccess class to test LED function
    """
    LEDControllerAccess.led_flash(3)
    GPIO.cleanup()
