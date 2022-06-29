# !/user/bin/env python3

# This parses through all yamls and puts them into a dataclass so that other modules can import and use the config
# easily, it will also refresh the data from the yamls - so you can drop extra information into the files in
# real-time and the HK will pick it up (for instance adding in new missions and objectives)

from dataclasses import dataclass, field

import yaml

import logging

from config.parameter_config import *

logger = logging.getLogger("yaml-importer")


def dict_search(values, search_for):
    """
    This is a search function for looking through dictionaries (mainly for searching through mission objectives for confirmations
    and returning objectives)
    :param values:
    :param search_for:
    :return:
    """
    for k in values:
        if search_for in k:
            return True, k.split("|")
    return False, "NO_MSN"


@dataclass
class YAMLData:
    primary: dict = field(default_factory=dict)
    secondary: dict = field(default_factory=dict)
    tertiary: dict = field(default_factory=dict)

    # Confidence threshold for visual detection - will only run process on detected objects that are at or above this
    # percentage
    CONF_THRESHOLD: int = 0.75

    # How many seconds per refresh of mission parameters
    PARAM_REFRESH: int = 60

    # How many seconds to process each objective
    OBJ_PROCESS: int = 1

    def __post_init__(self):
        """
        This is the post-init function for the YAMLData class, it will refresh the parameters from the yaml files
        :return:
        """

        self.refresh_params()

    def refresh_params(self):
        """
        This function will refresh the parameters from the yaml files it can be threaded to enable the parameters to be updated
        in real time
        :return:
        """
        self.primary = {}
        self.secondary = {}
        self.tertiary = {}
        # Get mission parameters from yaml config file
        with open(mission_parameters_file) as file:
            documents = yaml.full_load(file)

            # Extract sub-dicts
            self.primary = documents['missions']['primary']
            self.secondary = documents['missions']['secondary']
            self.tertiary = documents['missions']['tertiary']

            # Get confidence threshold from the YAML file
            self.CONF_THRESHOLD = documents['analysis_config']['confidence_threshold']

            # Get parameter refresh time from the YAML file
            self.PARAM_REFRESH = documents['parameter_config']['parameters_refresh_time']

            # Get objective process time from the YAML file
            self.OBJ_PROCESS = documents['parameter_config']['objective_process_time']


# Instantiates the yaml dataclass so that other modules can import it and use the latest yaml data
YAMLAccess = YAMLData()

if __name__ == "__main__":
    # Perform a test by parsing all yaml files and printing their data
    YAMLAccess.refresh_params()
    logger.debug(YAMLAccess)

    # Search and return test missions/objectives
    primary_found, objective_p = dict_search(YAMLAccess.primary.values(), "test_primary")
    secondary_found, objective_s = dict_search(YAMLAccess.secondary.values(), "test_secondary")
    tertiary_found, objective_t = dict_search(YAMLAccess.tertiary.values(), "test_tertiary")

    # Print the test missions/objectives
    if primary_found:
        logger.debug("PRIMARY SUCCESS")
        logger.debug(objective_p)
    if secondary_found:
        logger.debug("SECONDARY SUCCESS")
        logger.debug(objective_s)
    if tertiary_found:
        logger.debug("TERTIARY SUCCESS")
        logger.debug(objective_t)
