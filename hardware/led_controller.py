import time
from subprocess import call


def led_on():
    """
    Turn the LED on
    :return:
    """
    call('echo "79" > /sys/class/gpio/export', shell=True)
    call('echo "out" > /sys/class/gpio/gpio79/direction', shell=True)
    call('echo "1" > /sys/class/gpio/gpio79/value', shell=True)


def led_off():
    """
    Turn the LED off
    :return:
    """
    call('echo "79" > /sys/class/gpio/export', shell=True)
    call('echo "out" > /sys/class/gpio/gpio79/direction', shell=True)
    call('echo "0" > /sys/class/gpio/gpio79/value', shell=True)


def led_flash(times_to_flash):
    """
    Flash the LED a number of times
    :param times_to_flash:
    :return:
    """
    for i in range(times_to_flash):
        call('echo "0" > /sys/class/gpio/gpio79/value', shell=True)
        time.sleep(0.1)
        call('echo "1" > /sys/class/gpio/gpio79/value', shell=True)
        time.sleep(0.1)


# if called direct then run the function
if __name__ == '__main__':
    led_on()
