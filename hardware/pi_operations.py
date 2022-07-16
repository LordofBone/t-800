from events.event_queue import EventQueueAccess
from events.event_types import SHUTDOWN, REBOOT, HARDWARE_PI

from subprocess import call

import logging

import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
ledPin = 8
GPIO.setup(ledPin, GPIO.OUT)

logger = logging.getLogger("pi-operations")


class PiOperations:
    def __init__(self):
        # todo: add extra raspberry pi operations here, temp checks etc.
        self.shutdown_wait_seconds = 5

    def shutdown(self):
        """
        Shutdown the Pi
        :return:
        """
        logger.debug(f"Switching Off in {self.shutdown_wait_seconds} seconds")
        sleep(self.shutdown_wait_seconds)
        call('sudo shutdown now', shell=True)

    def reboot(self):
        """
        Restart the Pi
        :return:
        """
        logger.debug(f"Restarting in {self.shutdown_wait_seconds} seconds")
        sleep(self.shutdown_wait_seconds)
        call('sudo reboot now', shell=True)

    def queue_checker(self):
        """
        Check the event queue for events
        :return:
        """
        while True:
            event = EventQueueAccess.get_latest_event([HARDWARE_PI])
            if event:
                if event[1] == SHUTDOWN:
                    self.shutdown()
                elif event[1] == REBOOT:
                    self.reboot()
            else:
                sleep(1)


PiOperationsAccess = PiOperations()

if __name__ == "__main__":
    """
    Run the PiOperations class to test LED function
    """
    PiOperationsAccess.shutdown()
