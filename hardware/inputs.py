import time
import board
from digitalio import DigitalInOut, Direction, Pull

BUTTON_PIN = board.D17
JOYDOWN_PIN = board.D27
JOYLEFT_PIN = board.D22
JOYUP_PIN = board.D23
JOYRIGHT_PIN = board.D24
JOYSELECT_PIN = board.D16

buttons = [BUTTON_PIN, JOYUP_PIN, JOYDOWN_PIN,
           JOYLEFT_PIN, JOYRIGHT_PIN, JOYSELECT_PIN]
for i, pin in enumerate(buttons):
    buttons[i] = DigitalInOut(pin)
    buttons[i].direction = Direction.INPUT
    buttons[i].pull = Pull.UP
button, joyup, joydown, joyleft, joyright, joyselect = buttons

while True:
    if not button.value:
        print("Button pressed")
    if not joyup.value:
        print("Joystick up")
    if not joydown.value:
        print("Joystick down")
    if not joyleft.value:
        print("Joystick left")
    if not joyright.value:
        print("Joystick right")
    if not joyselect.value:
        print("Joystick select")

    time.sleep(0.01)
