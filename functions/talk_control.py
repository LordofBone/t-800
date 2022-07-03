from soran.integrate_stt import SpeechtoTextHandler

from Bot_Engine.functions import core_systems

from events.event_queue import EventQueueAccess, DrawListQueueAccess

from events.event_types import LISTEN_STT, TALK_SYSTEMS, OVERLAY_DRAW, LISTENING, INFERENCING_SPEECH

from hardware.pi_operations import *

logger = logging.getLogger("talk-control")

BotControl = core_systems.CoreInterface.integrate()


class TalkController:
    def __init__(self):
        """
        This is the main class that runs the STT and bot interaction.
        """
        self.bot_control = BotControl

        self.STT_handler = SpeechtoTextHandler()

        self.inference_output = None

        self.bot_response = None

        self.interrupt = False

    def activate_interrupt(self):
        """
        This function is used to interrupt the STT and bot interaction.
        :return:
        """
        self.interrupt = True

    def listen_stt(self):
        """
        This is the main function that runs the STT and bot interaction.
        :return:
        """
        self.STT_handler.initiate_recording()

        self.inference_output = self.STT_handler.run_inference()

        logger.debug(self.inference_output)

        self.bot_response = (BotControl.input_get_response(self.inference_output))

        logger.debug(self.bot_response)

        # todo: ensure this works properly, should be checking inputs for commands not bot responses
        self.command_checker()

    def command_checker(self):
        """
        This function checks if the bot response is a command.
        :return:
        """
        pass
        # if self.bot_response == "shut down":
        #     EventQueueAccess().add_event(SHUTDOWN)

    def queue_checker(self):
        """
        Check the event queue for events
        :return:
        """
        while True:
            event = EventQueueAccess.get_latest_event([TALK_SYSTEMS])
            if event:
                if event[2] == LISTEN_STT:
                    self.listen_stt()
                # elif event[1] == REBOOT:
                #     self.reboot()
                # elif event[1] == LED_ON:
                #     self.led_on()
                # elif event[1] == LED_OFF:
                #     self.led_off()
                # elif event[1] == LED_FLASH:
                #     self.led_flash(self.led_flash_default)
            else:
                sleep(1)


TalkControllerAccess = TalkController()
