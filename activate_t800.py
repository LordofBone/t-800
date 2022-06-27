# !/user/bin/env python3

# Main module where all of the subsystems for the HK are called and activated, also allows for commandline arguments
# for debugging, showing vision and storing detections to file

import threading
from time import sleep

import functions.mission_parameteriser
import ml.ml_systems
from events.event_queue import EventQueueAccess
from hardware.serial_interfacing import SerialAccess
from hardware.serial_to_events import serial_getter
from functions.talk_control import TalkController
from hardware.pi_operations import PiOperationsAccess

import logging

logger = logging.getLogger("t800-activation-system")


def start_systems():
    """
    Start the event queue as a thread
    Start the mission parameteriser parameter getter as a thread
    Start the serial access reader as a thread
    Start the serial write processor as a thread
    Start the serial getter function as a thread
    Start the mission parameteriser objective processor as a thread
    Start the ML systems, passing in the commandline arguments for showing vision and storing detections to file
    :return:
    """

    # Start pi hardware operations as a thread
    threading.Thread(target=PiOperationsAccess.queue_checker, daemon=False).start()

    # Start the mission parameteriser parameter getter as a thread
    threading.Thread(target=functions.mission_parameteriser.get_params, daemon=False).start()

    logger.info("Started Mission Parameteriser")

    # Start the serial access reader as a thread
    threading.Thread(target=SerialAccess.read_serial, daemon=False).start()

    logger.info("Started Serial Access")

    sleep(2)

    # Start the serial write processor as a thread
    threading.Thread(target=SerialAccess.write_serial_processor, daemon=False).start()

    logger.info("Started Serial Write Processor")

    sleep(2)

    # Start the serial getter function as a thread
    threading.Thread(target=serial_getter, daemon=False).start()

    logger.info("Started Serial Getter")

    sleep(2)

    # Start the mission parameteriser objective processor as a thread
    threading.Thread(target=functions.mission_parameteriser.objective_processor, daemon=False).start()

    logger.info("Started Mission Parameteriser Objective Processor")

    sleep(2)

    threading.Thread(target=functions.talk_control.TalkController, daemon=False).start()

    logger.info("Started Talk Controller")

    # Start the ML systems, passing in the commandline arguments for showing vision and storing detections to file
    ml.ml_systems.start_machine_vision()

    logger.info("Started Machine Vision")

    # serial write test
    # todo: probably needs removing
    sleep(30)

    EventQueueAccess.queue_addition("SERIAL_WRITE", "test_serial", 1)


if __name__ == "__main__":
    start_systems()
