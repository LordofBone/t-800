import time
from subprocess import call


def led_on():
    call('echo "79" > /sys/class/gpio/export', shell=True)
    call('echo "out" > /sys/class/gpio/gpio79/direction', shell=True)
    call('echo "1" > /sys/class/gpio/gpio79/value', shell=True)


def led_off():
    call('echo "79" > /sys/class/gpio/export', shell=True)
    call('echo "out" > /sys/class/gpio/gpio79/direction', shell=True)
    call('echo "0" > /sys/class/gpio/gpio79/value', shell=True)


def led_flash(times_to_flash):
    for i in range(times_to_flash):
        call('echo "0" > /sys/class/gpio/gpio79/value', shell=True)
        time.sleep(0.1)
        call('echo "1" > /sys/class/gpio/gpio79/value', shell=True)
        time.sleep(0.1)


# if called direct then run the function
if __name__ == '__main__':
    led_on()
