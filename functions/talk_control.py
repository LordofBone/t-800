from soran.integrate_stt import SpeechtoTextHandler

from Bot_Engine.functions import core_systems

from events.event_queue import EventQueueAccess, CurrentProcessQueueAccess
from Bot_Engine.functions.voice_controller import VoiceControllerAccess

from events.event_types import LISTEN_STT, TALK_SYSTEMS, SPEAK_TTS, REPEAT_INPUT_TTS, REPEAT_LAST, LISTENING, \
    INFERENCING_SPEECH, PROCESSING_RESPONSES, AUDIO_SYSTEM, ML_SYSTEM, RESPONSE_FOUND

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

    def speak_tts(self):
        """
        This function is used to speak the bot response.
        :return:
        """
        VoiceControllerAccess.tts(self.bot_response)

    def listen_stt(self):
        """
        This is the main function that runs the STT and bot interaction.
        :return:
        """
        # todo: use TalkControllerAccess.STT_handler.listening
        CurrentProcessQueueAccess.queue_addition(AUDIO_SYSTEM, LISTENING, 1)

        self.STT_handler.initiate_recording()

        CurrentProcessQueueAccess.queue_addition(ML_SYSTEM, INFERENCING_SPEECH, 1)

        self.inference_output = self.STT_handler.run_inference()

        CurrentProcessQueueAccess.queue_addition(ML_SYSTEM, f"Heard: {self.inference_output[0]}", 1)

        logger.debug(self.inference_output)

    def get_bot_engine_response(self):
        """
        This function returns the bot response.
        :return:
        """
        CurrentProcessQueueAccess.queue_addition(ML_SYSTEM, PROCESSING_RESPONSES, 1)

        self.bot_response = (BotControl.input_get_response(self.inference_output))

        CurrentProcessQueueAccess.queue_addition(RESPONSE_FOUND, f"REPLY: {self.bot_response}", 1)

        logger.debug(self.bot_response)

    def command_checker(self):
        """
        This function checks if the bot response is a command.
        :return:
        """
        if self.inference_output == "command shut down":
            EventQueueAccess().add_event(HARDWARE_PI, SHUTDOWN, 5)
        elif self.inference_output == "command recite":
            EventQueueAccess().add_event(TALK_SYSTEMS, REPEAT_INPUT_TTS, 3)
        elif self.inference_output == "command repeat":
            EventQueueAccess().add_event(TALK_SYSTEMS, REPEAT_LAST, 3)

    def queue_checker(self):
        """
        Check the event queue for events
        :return:
        """
        while True:
            event = EventQueueAccess.get_latest_event([TALK_SYSTEMS])

            if event:
                split_event_details = event[2].split("|")
                if split_event_details[0] == LISTEN_STT:
                    self.listen_stt()
                    self.command_checker()
                    self.get_bot_engine_response()
                elif split_event_details[0] == REPEAT_INPUT_TTS:
                    self.listen_stt()
                    self.bot_response = self.inference_output
                    self.speak_tts()
                elif split_event_details[0] == REPEAT_LAST:
                    self.speak_tts()
            else:
                sleep(1)


TalkControllerAccess = TalkController()
