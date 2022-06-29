# !/user/bin/env python3

# This module is for operating system level operations on the Pi, such as shutdowns, reboots etc.

from events.event_queue import EventQueueAccess
from events.event_types import SHUTDOWN, REBOOT, LED_ON, LED_OFF, LED_FLASH, HARDWARE_PI

from time import sleep
from subprocess import call

import logging

logger = logging.getLogger("pi-operations")


class PiOperations:
    def __init__(self):
        # todo: add extra raspberry pi operations here, temp checks etc.
        self.led_flash_default = 3

    def shutdown(self):
        """
        Shutdown the Pi
        :return:
        """
        logger.debug("Switching Off")
        call('sudo shutdown now', shell=True)

    def reboot(self):
        """
        Restart the Pi
        :return:
        """
        logger.debug("Restarting")
        call('sudo reboot now', shell=True)

    def led_on(self):
        """
        Turn the LED on
        :return:
        """
        logger.debug("Turning LED on")
        call('echo "79" > /sys/class/gpio/export', shell=True)
        call('echo "out" > /sys/class/gpio/gpio79/direction', shell=True)
        call('echo "1" > /sys/class/gpio/gpio79/value', shell=True)

    def led_off(self):
        """
        Turn the LED off
        :return:
        """
        logger.debug("Turning LED off")
        call('echo "79" > /sys/class/gpio/export', shell=True)
        call('echo "out" > /sys/class/gpio/gpio79/direction', shell=True)
        call('echo "0" > /sys/class/gpio/gpio79/value', shell=True)

    def led_flash(self, times_to_flash):
        """
        Flash the LED a number of times
        :param times_to_flash:
        :return:
        """
        logger.debug("Flashing LED")
        for i in range(times_to_flash):
            call('echo "0" > /sys/class/gpio/gpio79/value', shell=True)
            sleep(0.1)
            call('echo "1" > /sys/class/gpio/gpio79/value', shell=True)
            sleep(0.1)

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
                elif event[1] == LED_ON:
                    self.led_on()
                elif event[1] == LED_OFF:
                    self.led_off()
                elif event[1] == LED_FLASH:
                    self.led_flash(self.led_flash_default)
            else:
                sleep(1)


PiOperationsAccess = PiOperations()

if __name__ == "__main__":
    """
    Run the PiOperations class to test LED function
    """
    PiOperationsAccess.led_flash(3)
