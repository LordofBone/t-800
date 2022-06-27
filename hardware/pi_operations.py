# !/user/bin/env python3

# This module is for operating system level operations on the Pi, such as shutdowns, reboots etc.

from events.event_queue import EventQueueAccess

from time import sleep

import subprocess

import logging

logger = logging.getLogger("pi-operations")


class PiOperations:
    def __init__(self):
        # todo: add extra raspberry pi operations here, temp checks etc.
        pass

    def shutdown(self):
        """
        Shutdown the Pi
        :return:
        """
        logger.debug("Switching Off")
        subprocess.call('sudo shutdown now', shell=True)

    def reboot(self):
        """
        Restart the Pi
        :return:
        """
        logger.debug("Restarting")
        subprocess.call('sudo reboot now', shell=True)

    def queue_checker(self):
        while True:
            event = EventQueueAccess.get_latest_event(["HARDWARE_PI"])
            if event:
                if event[1] == "SHUTDOWN":
                    self.shutdown()
                elif event[1] == "REBOOT":
                    self.reboot()
            else:
                sleep(1)


PiOperationsAccess = PiOperations()

if __name__ == "__main__":
    # Test the OS calls work with a reboot
    PiOperationsAccess.reboot()
