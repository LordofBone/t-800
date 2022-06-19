# !/user/bin/env python3

# This checks inputs against missions and gets objectives, refreshes mission parameters and gets standing orders and
# processes objectives and passes them on to be actioned

from time import sleep

from functions.draw_vision import VisionAccess
from events.event_processor import EventFactoryAccess
from events.event_queue import EventQueueAccess
from utils.yaml_importer import YAMLAccess, dict_search

import logging

logger = logging.getLogger("mission-parameteriser")

# Function for checking whether an input matches against missions set in the mission_parameters.yaml
def mission_check(input_check):
    # Search through primary, secondary and tertiary objectives and return true if any of them are found, along with
    # the objectives
    # todo: need to work on a way to process multiple of the same detections (if needed?) at the
    #  moment if two 'person' items are in the mission parameters only the last objective found in the search will be
    #  returned
    primary_found, objective_p = dict_search(YAMLAccess.primary.values(), input_check)
    secondary_found, objective_s = dict_search(YAMLAccess.secondary.values(), input_check)
    tertiary_found, objective_t = dict_search(YAMLAccess.tertiary.values(), input_check)

    # Put mission detection booleans and objectives into tuples
    mission_confirms = (primary_found, secondary_found, tertiary_found)
    mission_objectives = (objective_p, objective_s, objective_t)

    # If missions are found pass them into the event queue with appropriate priority depending on mission,
    # along with the objective and name of confirmed mission target
    if primary_found:
        EventQueueAccess.queue_addition('PRI_MSN:{}'.format(input_check), objective_p, 1)
    if secondary_found:
        EventQueueAccess.queue_addition('SEC_MSN:{}'.format(input_check), objective_s, 2)
    if tertiary_found:
        EventQueueAccess.queue_addition('TER_MSN:{}'.format(input_check), objective_t, 3)

    # Return tuples so that when this is called from another module the details can be used elsewhere (for instance
    # in object detection these are used to draw the info onto the screen)
    return mission_confirms, mission_objectives


# Grabs the latest mission parameters from the mission_parameter.yaml
# todo: add a switcher in here so that within the YAML purple or red plasma can be selected
def get_params(test_mode=False):
    while True:
        # Add the mission parameters to be displayed
        VisionAccess.add_mission_params(YAMLAccess.primary, YAMLAccess.secondary,
                                        YAMLAccess.tertiary)

        # Print them for debug/testing
        logger.debug(VisionAccess.text_list_params_primary)

        logger.debug(VisionAccess.text_list_params_secondary)

        logger.debug(VisionAccess.text_list_params_tertiary)

        # Run a check for standing orders
        (primary_found, secondary_found, tertiary_found), (objective_p, objective_s, objective_t) = \
            mission_check("STAND_ORD")

        # If standing orders are detected push them into the event queue with the appropriate priority
        if primary_found:
            logger.debug('Standing Order: "{}" found'.format(objective_p))
            EventQueueAccess.queue_addition("PRI_MSN:STAND_ORD", objective_p, 1)
        if secondary_found:
            logger.debug('Standing Order: "{}" found'.format(objective_s))
            EventQueueAccess.queue_addition("SEC_MSN:STAND_ORD", objective_s, 2)
        if tertiary_found:
            logger.debug('Standing Order: "{}" found'.format(objective_t))
            EventQueueAccess.queue_addition("TER_MSN:STAND_ORD", objective_t, 3)
        # If test mode is activated then break the loop
        if test_mode:
            break

        # Sleep for period of time as defined in mission_parameters.yaml
        sleep(YAMLAccess.PARAM_REFRESH)
        # Refresh the yaml parameters to get new missions/objectives
        YAMLAccess.refresh_params()


# This function processes objectives from the event factory and pushes them into actions This is put here outside of
# the event factory so that it can be threaded seperately, so the event factory won't stop while it is waiting for
# actions to complete
def objective_processor():
    while True:
        # Grab the latest objective from the factory list
        objective = EventFactoryAccess.get_mission_objective_list()
        # If an objective is present from the list then process it and console print
        if not objective == "":
            logger.debug(objective)

            # Depending on the objective, call the relevant action - unknown objectives are dropped
            if objective == "terminate":
                EventQueueAccess.queue_addition("ACTION:EXECUTE", "TERMINATE", 1)
            elif objective == "patrol":
                EventQueueAccess.queue_addition("ACTION:MOVEMENT", "PATROL", 3)
            else:
                logger.debug("unknown objective")

        # Wait for a period of time as defined in mission_parameters.yaml before processing next objective
        sleep(YAMLAccess.OBJ_PROCESS)


if __name__ == "__main__":
    # Perform a test on getting the mission parameters from the mission_parameters.yaml and display them
    get_params(True)
