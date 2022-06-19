# !/user/bin/env python3

# This module is for operating system level operations on the Pi, such as shutdowns, reboots etc.

import subprocess


def shutdown():
    # Switch off the Pi
    ConsoleAccess.console_print_bool("Switching Off")
    subprocess.call('sudo shutdown now', shell=True)


def restart():
    # Restart the Pi
    ConsoleAccess.console_print_bool("Restarting")
    subprocess.call('sudo reboot now', shell=True)


if __name__ == "__main__":
    # Test the OS calls work with a reboot
    ConsoleAccess.console_print_enable = True
    restart()
