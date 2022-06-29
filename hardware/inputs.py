import time
import board
from digitalio import DigitalInOut, Direction, Pull

from events.event_queue import EventQueueAccess
from events.event_types import SHUTDOWN, HARDWARE_PI


class InputSystems:
    def __init__(self):
        self.BUTTON_PIN = board.D17
        self.JOYDOWN_PIN = board.D27
        self.JOYLEFT_PIN = board.D22
        self.JOYUP_PIN = board.D23
        self.JOYRIGHT_PIN = board.D24
        self.JOYSELECT_PIN = board.D16

        self.buttons = [self.BUTTON_PIN, self.JOYUP_PIN, self.JOYDOWN_PIN,
                        self.JOYLEFT_PIN, self.JOYRIGHT_PIN, self.JOYSELECT_PIN]
        for i, pin in enumerate(self.buttons):
            self.buttons[i] = DigitalInOut(pin)
            self.buttons[i].direction = Direction.INPUT
            self.buttons[i].pull = Pull.UP
        self.button, self.joyup, self.joydown, self.joyleft, self.joyright, self.joyselect = self.buttons

    def check_inputs(self):

        while True:
            if not self.button.value:
                EventQueueAccess.queue_addition(HARDWARE_PI, SHUTDOWN, 6)
            if not self.joyup.value:
                print("Joystick up")
            if not self.joydown.value:
                print("Joystick down")
            if not self.joyleft.value:
                print("Joystick left")
            if not self.joyright.value:
                print("Joystick right")
            if not self.joyselect.value:
                print("Joystick select")

            time.sleep(0.01)


InputSystemsAccess = InputSystems()
