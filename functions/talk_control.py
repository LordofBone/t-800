from soran.integrate_stt import run_stt_inference

from Bot_Engine.functions import core_systems

from hardware.pi_operations import *

logger = logging.getLogger("talk-control")

BotControl = core_systems.CoreInterface.integrate()


class TalkController:
    def __init__(self):
        """
        This is the main class that runs the STT and bot interaction.
        """
        self.bot_control = BotControl

        self.inference_output = None

        self.bot_response = None

        self.interrupt = False

    def activate_interrupt(self):
        """
        This function is used to interrupt the STT and bot interaction.
        :return:
        """
        self.interrupt = True

    def talk_loop(self):
        """
        This is the main loop that runs the STT and bot interaction.
        :return:
        """
        while True:
            self.inference_output = run_stt_inference()

            logger.debug(self.inference_output)

            self.bot_response = (BotControl.input_get_response(self.inference_output))

            logger.debug(self.bot_response)

            self.command_checker()

    def command_checker(self):
        """
        This function checks if the bot response is a command.
        :return:
        """

        if self.bot_response == "shut down":
            shutdown()
