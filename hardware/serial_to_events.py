# !/user/bin/env python3

# This gets the latest serial outputs from the serial interfacing module and puts them into the draw queue as well as
# processing different serial event types to relay into the event queue for processing into actions on the Pi

from time import sleep

from events.event_queue import DrawListQueueAccess, queue_adder
from events.event_types import SERIAL_DRAW, SERIAL_WRITE, SERIAL_TEST, CHECK_DISTANCE
from hardware.serial_interfacing import SerialAccess
from config.serial_config import *

import logging

logger = logging.getLogger("serial-events")


def serial_getter():
    """
    This function is called from the serial_interfacing module to get the latest serial output from the serial interface
    :return:
    """
    while True:
        serial_in = SerialAccess.get_serial_list()
        # If serial output is present then process it, otherwise skip
        if serial_in != "":
            logger.debug(serial_in)

            # Sent the serial outputs into the event factory's serial receiver list for processing
            DrawListQueueAccess.queue_addition(event_type=SERIAL_DRAW, event_content=serial_in, priority=3)

            # This is where the outputs are processed for commands to be sent to the event queue
            # todo: add in more
            #  actions here from Arduino outputs, such as movement locks while the Arduino is moving motors etc.
            if serial_in == "SUCCESS!":
                queue_adder("TEST_EVENT", "SERIAL_TEST", 1)
            # todo: need to review whether the below is really needed, it was made to lock movements to prevent
            #  multiple movements at once, but it just seemed to spam the serial writing to the point where other
            #  things like firing plasma would not work, seems to work fine without this so far

            # if "moving" or "turning" in serial_in:
            #     EventQueueAccess.queue_addition("ACTION:MOVEMENT", "LOCK", 1)
            # if "stopping" in serial_in:
            #     EventQueueAccess.queue_addition("ACTION:MOVEMENT", "UNLOCK", 2)
        # else:
        #     sleep(1)


if __name__ == "__main__":
    # Run a test by writing some commands and checking that the responses are processed by the event queue/event factory
    import threading

    threading.Thread(target=SerialAccess.read_serial, daemon=False).start()
    sleep(2)

    threading.Thread(target=serial_getter, daemon=False).start()

    sleep(2)

    # In actual real-world use the queue is used to ensure prevention of two modules trying to write to the Serial at
    # the same time, this tests that this will work correctly
    queue_adder(SERIAL_WRITE, SERIAL_TEST, 1)

    sleep(2)

    queue_adder(SERIAL_WRITE, CHECK_DISTANCE, 1)
