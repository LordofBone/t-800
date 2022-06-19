# !/user/bin/env python3

# This module is for operating system level operations on the Pi, such as shutdowns, reboots etc.

import subprocess

import logging

logger = logging.getLogger("pi-operations")

def shutdown():
    # Switch off the Pi
    logger.debug("Switching Off")
    subprocess.call('sudo shutdown now', shell=True)


def restart():
    # Restart the Pi
    logger.debug("Restarting")
    subprocess.call('sudo reboot now', shell=True)


if __name__ == "__main__":
    # Test the OS calls work with a reboot
    restart()
