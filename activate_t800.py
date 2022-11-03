import threading
from time import sleep

import os
import sys

# todo: put these under config
bot_engine_dir = os.path.join(os.path.dirname(__file__), 'Bot_Engine')
chatbot_dir = os.path.join(os.path.dirname(__file__), bot_engine_dir, 'Chatbot_8')
soran_dir = os.path.join(os.path.dirname(__file__), 'soran')

sys.path.append(bot_engine_dir)
sys.path.append(chatbot_dir)
sys.path.append(soran_dir)

from functions.mission_processor_systems import MissionProcessorAccess
import ml.ml_systems
from events.event_queue import queue_adder
from events.event_types import LED_ACCESS, LED_ON
from hardware.serial_interfacing import SerialAccess
from hardware.serial_to_events import serial_getter
from functions.talk_control import TalkControllerAccess
from hardware.pi_operations import PiOperationsAccess
from hardware.inputs import InputSystemsAccess
from hardware.led_controller import LEDControllerAccess

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
    # Start input checking as a thread
    threading.Thread(target=InputSystemsAccess.check_inputs, daemon=False).start()

    logger.info("Started Input Checking")

    # Start pi hardware operations as a thread
    threading.Thread(target=PiOperationsAccess.queue_checker, daemon=False).start()

    logger.info("Started Pi Operations")

    # Start LED controller as a thread
    threading.Thread(target=LEDControllerAccess.queue_checker, daemon=False).start()

    logger.info("Started LED Controller")

    # Start the mission parameteriser parameter getter as a thread
    threading.Thread(target=MissionProcessorAccess.objective_processor, daemon=False).start()

    threading.Thread(target=MissionProcessorAccess.standing_order_refresher, daemon=False).start()

    logger.info("Started Mission Processor")

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

    # Start talk control as a thread
    threading.Thread(target=TalkControllerAccess.queue_checker, daemon=False).start()

    logger.info("Started Talk Controller")

    # Start the ML systems, passing in the commandline arguments for showing vision and storing detections to file
    ml.ml_systems.start_machine_vision()

    logger.info("Started Machine Vision")

    # turn on the LED eye
    queue_adder(LED_ACCESS, LED_ON, 1)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    start_systems()
