# !/user/bin/env python3
# Available commands to write to the low-level systems:
# Does a test run where the HK will move around a bit to test motors and avoidance routines:
# "run_test"

# Measures distance from all the ultrasonics and returns the results:
# "measure_dist"

# Moves the HK forward
# "move_forward"

# Moves the HK backward
# "move_backward"

# Turns the HK right
# "turn_right"

# Turns the HK left
# "turn_left"

# Turns on patrol mode, where the bot will move around in a patrol pattern for a time:
# "patrol_mode"

# Switches movement override on (the HK can not be moved without ultrasonics being clear)
# "move_override_on"

# Switches movement override of (the HK can be moved ignoring all ultrasonics)
# "move_override_off"

# Fires purple plasma
# "plasma_purple"

# Fires red plasma
# "plasma_red"

import threading
from dataclasses import dataclass, field
from time import sleep

import serial

from events.event_processor import EventFactoryAccess

from config.serial_config import *

import logging

logger = logging.getLogger("serial-interfacing")


# todo: determine whether this needs to be a dataclass
@dataclass
class SerialController:
    serial_on: bool = False

    serial_list: list = field(default_factory=list)

    def __post_init__(self):
        """
        This is the post init function for the serial controller, it will set up the serial connection and start the
        threads :return:
        """
        self.s1 = serial.Serial()
        self.s1.baudrate = speed
        self.s1.port = port

        # Attempt to open the serial port with the above configuration
        self.open_serial()

    def get_serial_list(self):
        """
        This will return the serial list, this is used to get the serial output from the Arduino
        :return:
        """
        try:
            # Pop 0 index so that it's FIFO rather than LIFO like the event handling as these want to be processed
            # in-order rather than latest first
            event_popped = self.serial_list.pop(0).strip()
        except IndexError:
            event_popped = ""
        return event_popped

    def open_serial(self):
        """
        This will try and open the serial port and will set the serial_on boolean as appropriate
        :return:
        """
        try:
            self.s1.open()
            self.serial_on = True
            logger.debug("Serial Connection SUCCESS")
        except serial.serialutil.SerialException:
            self.s1.close()
            self.serial_on = False
            logger.debug("Serial Connection FAILURE")

    # This grabs the serial writes from the event factory and will write them to the Arduino
    # todo: upon a write
    #  failure this will simply move onto the next serial writes until a connection is found, may need to add in
    #  re-attempts? This is setup to grab from the event factory list, so that the event queue handles them one at a
    #  time, to prevent multiple conflicting writes, if you want to write something to serial a "SERIAL_WRITE" event
    #  is needed, along with the serial instruction to be sent
    def write_serial_processor(self):
        """
        This will grab the serial writes from the event factory and will write them to the Arduino
        :return:
        """
        while True:
            s_write = EventFactoryAccess.get_serial_list_to_write()
            if not s_write == "":
                self.write_serial(s_write)
            else:
                sleep(1)

    def write_serial(self, to_write):
        """
        This is where all serial writes to the Arduino are handled, it will also check if the serial fails and set a
        retry of the serial open and wait if so (wait time configurable in serial_config.py)
        :param to_write:
        :return:
        """
        if self.s1.is_open:
            final_write = to_write + "\n"
            try:
                self.s1.write(final_write.encode())
            except serial.serialutil.SerialException:
                self.open_serial()
                sleep(YAMLAccess.S_WAIT)
        else:
            logger.debug("No Serial on WRITE - Retrying Connection")
            self.open_serial()
            sleep(YAMLAccess.S_WAIT)

    # This is called and threaded to read the serial outputs from the Arduino and will append them to the read serial
    # list - this will also try the serial connection and if it fails it will attempt to re-open the connection and
    # wait if so (wait time configurable in serial_config.py)
    def read_serial(self):
        """
        This is called and threaded to read the serial outputs from the Arduino and will append them to the read serial
        list - this will also try the serial connection and if it fails it will attempt to re-open the connection and
        wait if so (wait time configurable in serial_config.py)
        :return:
        """
        while True:
            if self.s1.is_open:
                logger.debug("Reading Serial")
                try:
                    current_serial = self.s1.readline().decode()
                except serial.serialutil.SerialException:
                    current_serial = ""
                    self.open_serial()
                    sleep(YAMLAccess.S_WAIT)
                if not current_serial == "":
                    logger.debug(current_serial)
                    self.serial_list.append(current_serial)
            else:
                logger.debug("No Serial on READ - Retrying Connection")
                self.open_serial()
                sleep(YAMLAccess.S_WAIT)


# Instantiate the class so serial interface can be accessed from other modules
SerialAccess = SerialController()

if __name__ == "__main__":
    # Run a test on serial reads and writes
    logger.debug("Testing Serial Read:")
    threading.Thread(target=SerialAccess.read_serial, daemon=False).start()
    sleep(2)

    logger.debug("Testing Serial Write:")
    # Using direct access to the write function here for testing purposes - in real world modules should use the
    # queue with event type SERIAL_WRITE" to prevent two modules from trying to write to the serial at the same time
    SerialAccess.write_serial('test_serial')

    sleep(1)

    # Test getting distance details from the Arduino
    SerialAccess.write_serial('measure_dist')

    sleep(3)

    # Print out all the serial outputs from the Arduino
    logger.debug("Testing Serial List Processing:")

    while True:
        serial_out = SerialAccess.get_serial_list()
        if serial_out == "":
            break
        else:
            logger.debug(serial_out + "\n")
        sleep(1)

    logger.debug("Serial List Test Complete")
