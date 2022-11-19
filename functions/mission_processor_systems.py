# !/user/bin/env python3

# This checks inputs against missions and gets objectives, refreshes mission parameters and gets standing orders and
# processes objectives and passes them on to be actioned

import time
from time import sleep

from functions.draw_vision import VisionAccess
from events.event_queue import EventQueueAccess, DrawListQueueAccess, queue_adder
from events.event_types import ANY, LISTEN_STT, TERMINATE, PATROL, TALK_SYSTEMS, ACTION_EXECUTE, ACTION_MOVEMENT, \
    PRI_MSN_STAND_ORD, SEC_MSN_STAND_ORD, TER_MSN_STAND_ORD, TALK, HUMAN, PRIMARY, SECONDARY, TERTIARY, OVERLAY_DRAW, \
    STAND_ORD, OBJECT
from utils.yaml_importer import YAMLAccess, dict_search

import logging

logger = logging.getLogger("mission-parameteriser")


class MissionProcessor:
    def __init__(self):
        self.primary_objectives = ""
        self.secondary_objectives = ""
        self.tertiary_objectives = ""
        # todo: add this to a config somewhere
        self.duplicate_event_backoff = 10

        self.duplicate_event_backoff_time = time.time() - self.duplicate_event_backoff

        self.set_standing_orders()

    def mission_check(self, input_check):
        """
        This function checks whether an input matches against missions set in the mission_parameters.yaml
        :param input_check:
        :return:
        """
        # Search through primary, secondary and tertiary objectives and return true if any of them are found, along with
        # the objectives
        primary_found, objective_p = dict_search(YAMLAccess.primary.values(), input_check)
        secondary_found, objective_s = dict_search(YAMLAccess.secondary.values(), input_check)
        tertiary_found, objective_t = dict_search(YAMLAccess.tertiary.values(), input_check)

        # Put mission detection booleans and objectives into tuples
        mission_confirms = (primary_found, secondary_found, tertiary_found)
        mission_objectives = (objective_p, objective_s, objective_t)

        # Return tuples so that when this is called from another module the details can be used elsewhere (for instance
        # in object detection these are used to draw the info onto the screen)
        return mission_confirms, mission_objectives

    def standing_order_refresher(self):
        """
        This function refreshes the standing orders every so often
        :return:
        """
        while True:
            self.set_standing_orders()
            sleep(YAMLAccess.PARAM_REFRESH)

    def set_standing_orders(self):
        """
        This function gets the latest mission parameters from the YAML file and returns them as a dictionary
        :return:
        """
        # Refresh the yaml parameters to get new missions/objectives
        YAMLAccess.refresh_params()

        # todo: make this an addition to the queue rather than a direct call, so this entire function can be run
        #  standalone
        # Add the mission parameters to be displayed
        VisionAccess.add_mission_params(YAMLAccess.primary, YAMLAccess.secondary,
                                        YAMLAccess.tertiary)

        self.primary_objectives = YAMLAccess.primary
        self.secondary_objectives = YAMLAccess.secondary
        self.tertiary_objectives = YAMLAccess.tertiary

        # Print them for debug/testing
        logger.debug(VisionAccess.text_list_params_primary)

        logger.debug(VisionAccess.text_list_params_secondary)

        logger.debug(VisionAccess.text_list_params_tertiary)

        # Run a check for standing orders
        (primary_found, secondary_found, tertiary_found), (objective_p, objective_s, objective_t) = \
            self.mission_check(STAND_ORD)
        # todo: figure out why everything is being pushed as primary
        # If standing orders are detected push them into the event queue with the appropriate priority
        if primary_found:
            logger.debug(f'Standing Order: "{objective_p}" found')
            EventQueueAccess.queue_addition(PRI_MSN_STAND_ORD, objective_p, 1)
        if secondary_found:
            logger.debug(f'Standing Order: "{objective_s}" found')
            EventQueueAccess.queue_addition(SEC_MSN_STAND_ORD, objective_s, 2)
        if tertiary_found:
            logger.debug(f'Standing Order: "{objective_t}" found')
            EventQueueAccess.queue_addition(TER_MSN_STAND_ORD, objective_t, 3)

    def objective_processor(self):
        """
        This function processes objectives from the event factory and pushes them into actions
        :return:
        """
        previous_event = ""

        # todo: move human detection to another specific function
        while True:
            # Get the next event from the event queue
            event = EventQueueAccess.get_latest_event(
                [HUMAN, OBJECT, PRI_MSN_STAND_ORD, SEC_MSN_STAND_ORD, TER_MSN_STAND_ORD])

            if not event:
                continue

            if event[1] == previous_event and time.time() < self.duplicate_event_backoff_time + self.duplicate_event_backoff:
                continue

            (primary_found, secondary_found, tertiary_found), (objective_p, objective_s, objective_t) = \
                self.mission_check(event[1])

            if primary_found:
                queue_adder(objective_p[1], objective_p[2], 1)
                DrawListQueueAccess.queue_addition(OVERLAY_DRAW, f"{PRIMARY}|{event[1]}|{objective_p[2]}", 1)
            elif secondary_found:
                queue_adder(objective_s[1], objective_s[2], 2)
                DrawListQueueAccess.queue_addition(OVERLAY_DRAW, f"{SECONDARY}|{event[1]}|{objective_s[2]}", 2)
            elif tertiary_found:
                queue_adder(objective_t[1], objective_t[2], 3)
                DrawListQueueAccess.queue_addition(OVERLAY_DRAW, f"{TERTIARY}|{event[1]}|{tertiary_found[2]}", 3)

            previous_event = event[1]

            # Wait for a period of time as defined in mission_parameters.yaml before processing next objective
            sleep(YAMLAccess.OBJ_PROCESS)


MissionProcessorAccess = MissionProcessor()

if __name__ == "__main__":
    # Perform a test.txt on getting the mission parameters from the mission_parameters.yaml and display them
    MissionProcessorAccess.set_standing_orders()
    MissionProcessorAccess.objective_processor()
